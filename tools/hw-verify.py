#!/usr/bin/env python3
"""
hw-verify.py — Reference implementation of the `hw verify` agent protocol.

Replays the event log, recomputes hashes, validates the chain, and checks every
projection hash and citation. Implements the algorithm specified in
core/SUBSTRATE.md §`hw verify`.

Usage:
    python tools/hw-verify.py --workspace <path>
    python tools/hw-verify.py --workspace <path> --since EV-0042

Exits 0 on PASS, 1 on FAIL. Untracked-projection and stale-citation findings
are reported as warnings; they do not change the exit code.

This is a reference implementation. Agents may reimplement the algorithm in
their environment, but the canonical serialization and citation rules in
core/SUBSTRATE.md are authoritative — divergence from those rules is a bug.

v5.2.1: KNOWN_EVENT_KINDS synced with the substrate (adds operator_soul_anchor,
toolchain.anchor) and REQUIRED_PAYLOAD_FIELDS entries added for both.
"""

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

CITATION_RE = re.compile(r"\[([A-Z]+)-(\d{3,})#([0-9a-f]{12})\]")
ARTIFACT_DIRS = ("decisions", "findings", "anti-patterns", "operating-reality",
                 "sources", "claims", "contradictions")
ZERO_HASH = "0" * 64
ZERO_HASH_PREFIXED = "sha256:" + ZERO_HASH

DEFAULT_ALLOWED_TERMINAL_STATES = (
    "complete", "deferred", "excluded-after-discovery", "escalated",
)

# v5.1 event kinds. The validator confirms each event's `kind` is in the closed
# set the harness recognizes. Unknown kinds are reported as untracked but do not
# block PASS — schemas may extend the set legitimately (e.g., `claim.add`).
KNOWN_EVENT_KINDS = {
    "project.activate", "project.archive", "project.park",
    "backlog.add", "backlog.remove",
    "decision.add", "decision.supersede", "decision.promote",
    "finding.add", "finding.supersede", "finding.promote",
    "anti-pattern.add", "anti-pattern.supersede",
    "operating-reality.add", "operating-reality.supersede",
    "task.create", "task.status", "task.recite", "task.scan", "task.complete",
    "branch.open", "branch.event", "branch.fold",
    "verify.layer1.pass", "verify.layer1.fail",
    "verify.layer2.pass", "verify.layer2.fail",
    "council.invoke", "council.report",
    "council.converged", "council.escalated",
    "capability.gap",
    "friction.log", "friction.log.prompt",
    "session.handoff",
    "scope.complete",
    "external_state.read_back",
    "bootstrap.inventory_diff", "bootstrap.scope_locked", "bootstrap.probe_skipped",
    "operator_soul_anchor",   # v5.2.0; missing from this set until v5.2.1
    "toolchain.anchor",       # v5.2.1
}

# Required payload fields per v5.1 event kind. None means no per-kind structural
# check beyond schema validation (which is out of scope for hw verify; it lives
# in the schema-validation step at hw add time).
REQUIRED_PAYLOAD_FIELDS = {
    "friction.log": ("type", "description", "surfaced_by", "severity"),
    "friction.log.prompt": ("trigger", "signal_summary"),
    "session.handoff": ("project_id", "closing_actor", "recommended_first_action"),
    "scope.complete": ("scope_items",),
    "external_state.read_back": ("task_id", "artifact_url", "equality_method",
                                  "divergence_detected"),
    "bootstrap.inventory_diff": ("schema", "probe_method", "declared", "found"),
    "bootstrap.scope_locked": ("project_id",),
    "bootstrap.probe_skipped": ("schema", "reason"),
    # fire_id is recommended but not required; projection generator falls back to
    # the matching council.invoke event.id when missing. v5.0.1 council events
    # pre-date the field; relaxing to optional preserves backward-compat.
    "council.invoke": ("trigger",),
    # fire_id is recommended but not required; projection generator falls back to
    # the matching council.invoke event.id when missing.
    "council.report": ("member", "role", "convergence_vote"),
    # fire_id is recommended but not required; projection generator falls back to
    # the matching council.invoke event.id when missing.
    "council.converged": (),
    "council.escalated": (),
    "operator_soul_anchor": ("soul_path", "soul_hash", "fired_at"),
    "toolchain.anchor": ("tools", "source", "fired_at"),
}


def canonical_serialize(obj) -> bytes:
    """Canonical JSON serialization for hashing. See SUBSTRATE.md §Canonical Serialization."""
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def event_hash(event: dict) -> str:
    """Recompute an event's hash from its content (excluding the hash field)."""
    canonical = {k: v for k, v in event.items() if k != "hash"}
    return sha256_hex(canonical_serialize(canonical))


def short_hash(full_hex: str) -> str:
    return full_hex[:12]


def normalize_recorded_hash(recorded: str) -> str:
    """Strip optional `sha256:` prefix to get bare hex."""
    if recorded.startswith("sha256:"):
        return recorded[len("sha256:"):]
    return recorded


def projection_short_hash(path: Path) -> str:
    return short_hash(sha256_hex(path.read_bytes()))


def collect_citations(payload) -> list:
    """Extract all citations from a payload (recursively walks dicts/lists/strings)."""
    found = []

    def walk(obj):
        if isinstance(obj, str):
            for match in CITATION_RE.finditer(obj):
                found.append((f"{match.group(1)}-{match.group(2)}", match.group(3)))
        elif isinstance(obj, dict):
            for value in obj.values():
                walk(value)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(payload)
    return found


def parse_scope_items_from_project_md(project_md_path: Path) -> list:
    """Parse PROJECT.md §Scope > ### Included bullets.

    Only the Included subsection counts for scope-completeness coverage; items
    listed under "### Explicitly Excluded" are excluded by definition and need
    not appear in the scope.complete snapshot. Empty placeholders like
    "<deliverable / system / artifact>" and parenthesized "none"/"n/a" are
    skipped.
    """
    if not project_md_path.exists():
        return []
    text = project_md_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    items = []
    in_scope = False
    in_included = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            heading = stripped[3:].strip().lower()
            in_scope = heading == "scope"
            in_included = False
            continue
        if not in_scope:
            continue
        if stripped.startswith("### "):
            sub = stripped[4:].strip().lower()
            in_included = sub == "included"
            continue
        if stripped.startswith("# "):
            in_scope = False
            in_included = False
            continue
        if not in_included:
            continue
        if not stripped.startswith("- "):
            continue
        body = stripped[2:].strip()
        if not body:
            continue
        if body.startswith("<") and body.endswith(">"):
            continue
        if re.fullmatch(r"\(?\s*(none|n/a|tbd|-)\s*\)?", body, re.IGNORECASE):
            continue
        item_id = None
        id_match = re.search(r"\b(T-\d{3,})\b", body)
        if id_match:
            item_id = id_match.group(1)
        items.append({"id": item_id, "name": body})
    return items


def parse_capability_gates_yaml(path: Path) -> dict:
    """Minimal YAML reader for capability-gates.yaml. We look only for the
    `scope_completeness:` block to extract `allowed_terminal_states` and the
    `external_state_readback:` block to extract `required_for`. Anything more
    elaborate would need PyYAML; we keep this dependency-free.
    """
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    out = {}

    def extract_block(block_name: str) -> dict | None:
        m = re.search(rf"^{re.escape(block_name)}:\s*$", text, re.MULTILINE)
        if not m:
            return None
        block_start = m.end()
        rest = text[block_start:]
        block_lines = []
        for line in rest.splitlines():
            if line.strip() == "":
                block_lines.append(line)
                continue
            if not line.startswith(" ") and not line.startswith("\t"):
                break
            block_lines.append(line)
        return {"raw": "\n".join(block_lines)}

    sc = extract_block("scope_completeness")
    if sc is not None:
        states_match = re.search(
            r"allowed_terminal_states:\s*\[([^\]]*)\]",
            sc["raw"],
        )
        if states_match:
            states = [s.strip().strip('"').strip("'")
                      for s in states_match.group(1).split(",")
                      if s.strip()]
            out["scope_completeness"] = {"allowed_terminal_states": states}
        else:
            out["scope_completeness"] = {"allowed_terminal_states":
                                          list(DEFAULT_ALLOWED_TERMINAL_STATES)}

    esrb = extract_block("external_state_readback")
    if esrb is not None:
        patterns = re.findall(r"^\s*-\s*\"([^\"]+)\"", esrb["raw"], re.MULTILINE)
        out["external_state_readback"] = {"required_for": patterns}

    return out


def find_schema_for_project(workspace: Path, project_id: str) -> str | None:
    """Read PROJECT.md §Schema line to get schema name. Falls back to scanning
    the file for the canonical 'bootstrapped from `schemas/projects/<name>/`'
    sentence.
    """
    project_md = workspace / "projects" / project_id / "PROJECT.md"
    if not project_md.exists():
        return None
    text = project_md.read_text(encoding="utf-8")
    m = re.search(r"schemas/projects/([a-z0-9-]+)/", text)
    if m:
        return m.group(1)
    return None


def check_scope_completeness(workspace: Path, events: list) -> list:
    """Run Layer 1 scope-completeness check across all projects with session.handoff."""
    failures = []
    by_project = defaultdict(list)
    for ev in events:
        by_project[ev.get("project")].append(ev)

    for project_id, project_events in by_project.items():
        if not project_id or project_id == "_harness":
            continue
        handoff_indices = [i for i, ev in enumerate(project_events)
                           if ev.get("kind") == "session.handoff"]
        if not handoff_indices:
            continue
        last_handoff_idx = handoff_indices[-1]

        scope_complete_idx = None
        for i in range(last_handoff_idx - 1, -1, -1):
            if project_events[i].get("kind") == "scope.complete":
                scope_complete_idx = i
                break

        if scope_complete_idx is None:
            # No scope.complete precedes the last handoff. That's not
            # automatically a FAIL: a retroactive fix-run may append a
            # scope.complete *after* the handoff to close out the same
            # boundary it should have covered originally. As long as no
            # further session.handoff has fired since (this is still the
            # last one), a trailing scope.complete satisfies the obligation.
            # Multiple trailing events can occur (repeated fix-runs); take the
            # most recent one.
            for i in range(len(project_events) - 1, last_handoff_idx, -1):
                if project_events[i].get("kind") == "scope.complete":
                    scope_complete_idx = i
                    break

        if scope_complete_idx is None:
            failures.append(
                f"{project_id}: scope_completeness_missing "
                f"(no scope.complete precedes or retroactively follows "
                f"{project_events[last_handoff_idx]['id']})"
            )
            continue

        sc_event = project_events[scope_complete_idx]
        scope_items = sc_event.get("payload", {}).get("scope_items", [])

        schema = find_schema_for_project(workspace, project_id)
        allowed = list(DEFAULT_ALLOWED_TERMINAL_STATES)
        if schema:
            cap_gates_path = (workspace.parent / "schemas" / "projects"
                              / schema / "capability-gates.yaml")
            if not cap_gates_path.exists():
                cap_gates_path = (workspace / "schemas" / "projects"
                                  / schema / "capability-gates.yaml")
            cap_gates = parse_capability_gates_yaml(cap_gates_path)
            sc_cfg = cap_gates.get("scope_completeness")
            if sc_cfg and sc_cfg.get("allowed_terminal_states"):
                allowed = sc_cfg["allowed_terminal_states"]

        for entry in scope_items:
            ts = entry.get("terminal_state")
            if ts not in allowed:
                failures.append(
                    f"{project_id}: scope_completeness_terminal_state_disallowed "
                    f"(item {entry.get('id') or entry.get('name')!r} -> "
                    f"{ts!r}; allowed {allowed})"
                )

        declared_items = parse_scope_items_from_project_md(
            workspace / "projects" / project_id / "PROJECT.md"
        )
        snapshot_ids = {entry.get("id") for entry in scope_items if entry.get("id")}
        snapshot_names = {entry.get("name") for entry in scope_items if entry.get("name")}
        for declared in declared_items:
            if declared["id"] and declared["id"] in snapshot_ids:
                continue
            if declared["name"] in snapshot_names:
                continue
            failures.append(
                f"{project_id}: scope_completeness_unrepresented_item "
                f"({declared['id'] or declared['name']!r} declared in PROJECT.md "
                f"§Scope but not in scope.complete snapshot)"
            )

    return failures


def task_matches_readback_pattern(task_meta: dict, pattern: str) -> bool:
    """Match a task's frontmatter against a v5.1.1 external_state_readback pattern.

    Patterns are human-readable strings declared in capability-gates.yaml. v5.1.1
    recognizes two: a critical-risk match and a live-edit delivery-mode match.
    The matcher is intentionally narrow; new patterns extend this function.
    """
    p = pattern.lower()
    if "critical" in p and "risk" in p:
        return str(task_meta.get("risk_level", "")).lower() == "critical"
    if "live-edit" in p:
        return str(task_meta.get("delivery_mode", "")).lower() == "live-edit"
    return False


def check_external_state_readback(workspace: Path, events: list) -> tuple:
    """Run Layer 1 external_state.read_back check.

    Returns (failures, warnings).
    """
    failures = []
    warnings = []

    by_project = defaultdict(list)
    for ev in events:
        by_project[ev.get("project")].append(ev)

    for project_id, project_events in by_project.items():
        if not project_id or project_id == "_harness":
            continue

        schema = find_schema_for_project(workspace, project_id)
        if not schema:
            continue

        cap_gates_path = (workspace / "schemas" / "projects" / schema
                          / "capability-gates.yaml")
        if not cap_gates_path.exists():
            cap_gates_path = (workspace.parent / "schemas" / "projects"
                              / schema / "capability-gates.yaml")
        cap_gates = parse_capability_gates_yaml(cap_gates_path)
        esrb = cap_gates.get("external_state_readback")
        if not esrb or not esrb.get("required_for"):
            continue
        patterns = esrb["required_for"]

        task_meta = {}
        for ev in project_events:
            if ev.get("kind") == "task.create":
                payload = ev.get("payload", {}) or {}
                tid = payload.get("task_id")
                fm = payload.get("frontmatter") or {}
                if tid:
                    task_meta[tid] = fm

        for idx, ev in enumerate(project_events):
            if ev.get("kind") != "task.complete":
                continue
            tid = (ev.get("payload") or {}).get("task_id")
            if not tid:
                continue
            meta = task_meta.get(tid, {})
            if not any(task_matches_readback_pattern(meta, p) for p in patterns):
                continue

            window = project_events[idx + 1: idx + 6]
            paired = None
            for follow in window:
                if follow.get("kind") != "external_state.read_back":
                    continue
                payload = follow.get("payload") or {}
                if payload.get("task_id") == tid:
                    paired = follow
                    break

            if paired is None:
                failures.append(
                    f"{project_id}: external_state_readback_missing "
                    f"(task {tid} matched required_for; no paired "
                    f"external_state.read_back within 5 events of {ev['id']})"
                )
                continue

            payload = paired.get("payload") or {}
            if payload.get("divergence_detected"):
                follow_idx = project_events.index(paired)
                trailing = project_events[follow_idx + 1: follow_idx + 6]
                friction_followup = any(
                    f.get("kind") == "friction.log"
                    for f in trailing
                )
                msg = (f"{project_id}: external_state_readback_divergence "
                       f"(task {tid}, read_back {paired['id']})")
                if not friction_followup:
                    msg += " — no follow-up friction.log within 5 events"
                warnings.append(msg)

    return failures, warnings


def check_bootstrap_probe(events: list) -> list:
    """Run Layer 1 bootstrap-probe check.

    Every project (with a project.activate event) must have either
    (bootstrap.inventory_diff with operator_reconciliation populated, followed
    by bootstrap.scope_locked) OR a bootstrap.probe_skipped event.
    """
    failures = []
    by_project = defaultdict(list)
    for ev in events:
        by_project[ev.get("project")].append(ev)

    for project_id, project_events in by_project.items():
        if not project_id or project_id == "_harness":
            continue

        has_activate = any(ev.get("kind") == "project.activate"
                           for ev in project_events)
        if not has_activate:
            continue

        skipped = any(ev.get("kind") == "bootstrap.probe_skipped"
                      for ev in project_events)
        if skipped:
            continue

        diffs = [ev for ev in project_events
                 if ev.get("kind") == "bootstrap.inventory_diff"]
        locks = [ev for ev in project_events
                 if ev.get("kind") == "bootstrap.scope_locked"]

        if not diffs and not locks:
            failures.append(
                f"{project_id}: bootstrap_probe_missing "
                f"(no bootstrap.inventory_diff, bootstrap.scope_locked, "
                f"or bootstrap.probe_skipped after project.activate)"
            )
            continue

        reconciled = False
        for diff in diffs:
            payload = diff.get("payload") or {}
            if payload.get("operator_reconciliation") is not None:
                reconciled = True
                break

        if diffs and not reconciled and not locks:
            failures.append(
                f"{project_id}: bootstrap_probe_missing "
                f"(bootstrap.inventory_diff without operator_reconciliation "
                f"and no bootstrap.scope_locked)"
            )
            continue

        if not locks and diffs and not reconciled:
            failures.append(
                f"{project_id}: bootstrap_probe_missing "
                f"(bootstrap.inventory_diff present but no bootstrap.scope_locked)"
            )

    return failures


def find_projection_path(workspace: Path, artifact_id: str, hashes_index: dict) -> Path | None:
    """Locate a projection file for an artifact ID. Prefer hashes.json, else search."""
    for projection_path in hashes_index:
        if Path(projection_path).stem == artifact_id:
            candidate = workspace / projection_path
            if candidate.exists():
                return candidate
    for projects_dir in (workspace / "projects").glob("*/"):
        for sub in ARTIFACT_DIRS:
            candidate = projects_dir / sub / f"{artifact_id}.md"
            if candidate.exists():
                return candidate
    return None


def verify(workspace: Path, since: str | None) -> dict:
    events_path = workspace / ".hyperworker" / "events.jsonl"
    hashes_path = workspace / ".hyperworker" / "hashes.json"

    result = {
        "events_scanned": 0,
        "tamper": [],
        "chain_breaks": [],
        "projection_drift": [],
        "missing_projections": [],
        "untracked_projections": [],
        "broken_citations": [],
        "stale_citations": [],
        "unknown_event_kinds": [],
        "malformed_payloads": [],
        "scope_completeness_failures": [],
        "external_state_readback_failures": [],
        "external_state_readback_warnings": [],
        "bootstrap_probe_failures": [],
        "result": "PASS",
    }

    if not events_path.exists():
        result["result"] = "FAIL"
        result["error"] = f"events.jsonl not found at {events_path}"
        return result

    events = []
    with events_path.open(encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            events.append(json.loads(line))
    result["events_scanned"] = len(events)

    skip_until = since
    skipping = skip_until is not None
    prev_recorded_hash = ZERO_HASH

    for idx, event in enumerate(events):
        if skipping:
            prev_recorded_hash = normalize_recorded_hash(event["hash"])
            if event["id"] == skip_until:
                skipping = False
            continue

        recomputed = event_hash(event)
        recorded = normalize_recorded_hash(event["hash"])
        if recomputed != recorded:
            result["tamper"].append(event["id"])

        recorded_prev = normalize_recorded_hash(event["prev_hash"])
        if idx == 0 and since is None:
            if recorded_prev != ZERO_HASH:
                result["chain_breaks"].append(event["id"])
        else:
            if recorded_prev != prev_recorded_hash:
                result["chain_breaks"].append(event["id"])

        prev_recorded_hash = recorded

        kind = event.get("kind")
        if kind not in KNOWN_EVENT_KINDS:
            result["unknown_event_kinds"].append(f"{event['id']}:{kind}")
        else:
            required = REQUIRED_PAYLOAD_FIELDS.get(kind)
            if required:
                payload = event.get("payload") or {}
                missing = [f for f in required if f not in payload]
                if missing:
                    result["malformed_payloads"].append(
                        f"{event['id']}:{kind} missing {missing}"
                    )

    hashes_index = {}
    if hashes_path.exists():
        try:
            hashes_index = json.loads(hashes_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            result["result"] = "FAIL"
            result["error"] = f"hashes.json is not valid JSON at {hashes_path}"
            return result

    for projection_path, recorded_short in hashes_index.items():
        full_path = workspace / projection_path
        if not full_path.exists():
            result["missing_projections"].append(projection_path)
            continue
        actual_short = projection_short_hash(full_path)
        recorded_short_bare = normalize_recorded_hash(recorded_short)
        if actual_short != recorded_short_bare:
            result["projection_drift"].append(projection_path)

    tracked_paths = {workspace / p for p in hashes_index}
    projects_root = workspace / "projects"
    if projects_root.exists():
        for project_dir in projects_root.iterdir():
            if not project_dir.is_dir():
                continue
            for sub in ARTIFACT_DIRS:
                sub_dir = project_dir / sub
                if not sub_dir.exists():
                    continue
                for projection in sub_dir.glob("*.md"):
                    if projection not in tracked_paths:
                        result["untracked_projections"].append(
                            str(projection.relative_to(workspace)).replace("\\", "/")
                        )

    artifact_short_hashes = {}
    for projection_path in hashes_index:
        artifact_id = Path(projection_path).stem
        artifact_short_hashes[artifact_id] = normalize_recorded_hash(hashes_index[projection_path])

    for event in events:
        for artifact_id, cited_short in collect_citations(event.get("payload", {})):
            current = artifact_short_hashes.get(artifact_id)
            if current is None:
                projection = find_projection_path(workspace, artifact_id, hashes_index)
                if projection is None:
                    result["broken_citations"].append(
                        f"[{artifact_id}#{cited_short}] @ {event['id']}"
                    )
                    continue
                current = projection_short_hash(projection)
            if cited_short != current:
                result["stale_citations"].append(
                    f"[{artifact_id}#{cited_short}] @ {event['id']} (current: {current})"
                )

    result["scope_completeness_failures"] = check_scope_completeness(workspace, events)
    esrb_failures, esrb_warnings = check_external_state_readback(workspace, events)
    result["external_state_readback_failures"] = esrb_failures
    result["external_state_readback_warnings"] = esrb_warnings
    result["bootstrap_probe_failures"] = check_bootstrap_probe(events)

    blocking = (
        result["tamper"]
        or result["chain_breaks"]
        or result["projection_drift"]
        or result["missing_projections"]
        or result["broken_citations"]
        or result["malformed_payloads"]
        or result["scope_completeness_failures"]
        or result["external_state_readback_failures"]
        or result["bootstrap_probe_failures"]
    )
    result["result"] = "FAIL" if blocking else "PASS"
    return result


def render(result: dict) -> str:
    lines = [
        "hw verify",
        f"  events_scanned:        {result['events_scanned']}",
        f"  tamper:                {len(result['tamper'])} {result['tamper']}",
        f"  chain_breaks:          {len(result['chain_breaks'])} {result['chain_breaks']}",
        f"  projection_drift:      {len(result['projection_drift'])} {result['projection_drift']}",
        f"  missing_projections:   {len(result['missing_projections'])} {result['missing_projections']}",
        f"  untracked_projections: {len(result['untracked_projections'])} {result['untracked_projections']}",
        f"  broken_citations:      {len(result['broken_citations'])} {result['broken_citations']}",
        f"  stale_citations:       {len(result['stale_citations'])} {result['stale_citations']}",
        f"  unknown_event_kinds:   {len(result['unknown_event_kinds'])} {result['unknown_event_kinds']}",
        f"  malformed_payloads:    {len(result['malformed_payloads'])} {result['malformed_payloads']}",
        f"  scope_completeness:    {len(result['scope_completeness_failures'])} {result['scope_completeness_failures']}",
        f"  ext_state_readback:    {len(result['external_state_readback_failures'])} {result['external_state_readback_failures']}",
        f"  ext_state_warnings:    {len(result['external_state_readback_warnings'])} {result['external_state_readback_warnings']}",
        f"  bootstrap_probe:       {len(result['bootstrap_probe_failures'])} {result['bootstrap_probe_failures']}",
        f"  result:                {result['result']}",
    ]
    if "error" in result:
        lines.append(f"  error:                 {result['error']}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Reference implementation of `hw verify`.")
    parser.add_argument("--workspace", required=True, type=Path,
                        help="Workspace root containing .hyperworker/")
    parser.add_argument("--since", default=None,
                        help="Skip the chain re-walk for events before this EV-NNNN ID")
    args = parser.parse_args()

    workspace = args.workspace.resolve()
    if not workspace.is_dir():
        print(f"Workspace path is not a directory: {workspace}", file=sys.stderr)
        return 2

    result = verify(workspace, args.since)
    print(render(result))
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
