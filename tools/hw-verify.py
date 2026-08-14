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

v5.3: adds checked-claims support (core/SUBSTRATE.md §Checked Claims,
core/VERIFICATION.md §Layer 1 check 13 and §Claim Replay). Default mode gains
two structural checks: `claim:` blocks (wherever present) must be well-formed,
and event kinds a schema's verification.yaml marks `checked_claims.required_for`
must carry a passing one. `--claims` is a new, separate replay mode that
re-evaluates recorded predicates against the current world and reports
claim-level pass/fail/error/skipped, independent of chain integrity.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path, PurePosixPath, PureWindowsPath

# The substrate version this verifier implements. A schema declaring a
# harness_version above this is refused (CONTRIBUTING.md §5,
# core/VERIFICATION.md §Layer 1 check 16).
HARNESS_VERSION = "6.0.0"

CITATION_RE = re.compile(r"\[([A-Z]+)-(\d{3,})#([0-9a-f]{12})\]")
ARTIFACT_DIRS = ("decisions", "findings", "anti-patterns", "operating-reality",
                 "sources", "claims", "contradictions")
ZERO_HASH = "0" * 64
ZERO_HASH_PREFIXED = "sha256:" + ZERO_HASH

DEFAULT_ALLOWED_TERMINAL_STATES = (
    "complete", "deferred", "excluded-after-discovery", "escalated",
)

# v5.3 checked-claims. See core/SUBSTRATE.md §Checked Claims.
CLAIM_PREDICATE_KINDS = {
    "file_exists", "file_absent", "file_sha256", "cmd_exit", "url_status",
}
# Event kinds (plus scope.complete's scope_items[] granularity, handled
# separately) whose payload may carry a top-level `claim:` block.
CLAIM_BEARING_KINDS = {
    "task.complete", "finding.add", "external_state.read_back",
    "decision.add", "anti-pattern.add", "operating-reality.add",
}

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
    "cycle.open", "cycle.close",   # v5.3 lifecycle; missing from this set until v6.0.0
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
    # v5.3 lifecycle events (core/SUBSTRATE.md §Lifecycle events). `next_due` is
    # required on close: "when is the next sweep due" is substrate state, not
    # prose in a handoff, and the whole OVERDUE mechanism reads it.
    "cycle.open": ("project_id", "cycle_id", "opened_at", "cadence"),
    "cycle.close": ("project_id", "cycle_id", "closed_at", "summary", "next_due"),
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


# ---------------------------------------------------------------------------
# v6.0.0 verifier hardening. Checks below implement core/VERIFICATION.md
# §Layer 1 rows 14-18, each derived from a field incident where the promised
# refusal existed only as prose.
# ---------------------------------------------------------------------------

EVENT_ID_RE = re.compile(r"^EV-(\d+)$")


def parse_event_id(event_id) -> int | None:
    """Numeric suffix of an `EV-<n>` id, or None if the id is not that shape.

    Schema-extended IDs that do not match are skipped by the monotonicity check
    rather than reported: the closed-set discipline for IDs lives at `hw add`
    time, and an unrecognized shape is not evidence of a collision.
    """
    if not isinstance(event_id, str):
        return None
    m = EVENT_ID_RE.match(event_id.strip())
    return int(m.group(1)) if m else None


def _event_origin(event: dict, line_no: int) -> str:
    """Human-adjudicable location of an event: which line, written by whom, for
    which project. Duplicate IDs are resolved by a human reading two events with
    the same name; this is the information that read needs.
    """
    return (f"line {line_no} (actor={event.get('actor')!r}, "
            f"project={event.get('project')!r})")


def check_id_integrity(events: list, line_numbers: list | None = None) -> tuple:
    """Layer 1 check 14: event IDs are unique and strictly increasing.

    The field incident this implements (2026-07, ten-week deployment): two agents
    appended to one chain; the resuming agent derived its next ID from the last
    event *of its own project* instead of from the chain tail, so EV-0116..EV-0120
    exist twice with different content. Both runs linked `prev_hash` correctly, so
    hash-chain verification passed and `hw verify` returned PASS on a log with ten
    events and five names. See core/SUBSTRATE.md §Deriving the Next Event ID.

    Returns (duplicates, non_monotonic). A duplicated ID is reported only as a
    duplicate; re-reporting it as non-monotonic would double-count one defect.
    """
    if line_numbers is None:
        line_numbers = list(range(1, len(events) + 1))

    positions = defaultdict(list)
    for idx, event in enumerate(events):
        positions[event.get("id")].append(idx)

    duplicates = []
    for event_id, indices in positions.items():
        if len(indices) < 2:
            continue
        where = "; ".join(_event_origin(events[i], line_numbers[i]) for i in indices)
        duplicates.append(
            f"duplicate_event_id: {event_id} appears {len(indices)} times - {where}"
        )
    duplicates.sort()
    duplicated_ids = {eid for eid, idx in positions.items() if len(idx) > 1}

    non_monotonic = []
    highest = None  # (numeric_id, index)
    for idx, event in enumerate(events):
        numeric = parse_event_id(event.get("id"))
        if numeric is None:
            continue
        if highest is not None and numeric <= highest[0]:
            if event.get("id") not in duplicated_ids:
                prev_idx = highest[1]
                non_monotonic.append(
                    f"non_monotonic_event_id: {event.get('id')} at "
                    f"{_event_origin(event, line_numbers[idx])} does not exceed "
                    f"{events[prev_idx].get('id')} at "
                    f"{_event_origin(events[prev_idx], line_numbers[prev_idx])}"
                )
        if highest is None or numeric > highest[0]:
            highest = (numeric, idx)

    return duplicates, non_monotonic


# Kinds that release the Lock's single active slot. `project.archive` is what
# `hw wrap` actually appends (core/SUBSTRATE.md §`hw wrap` step 3); `project.wrap`
# is accepted as an alias so a chain written against the command name rather than
# the event name is read as a release, not as a missing one.
PROJECT_RELEASE_KINDS = ("project.park", "project.archive", "project.wrap")


def lock_target(event: dict) -> str | None:
    """Which project a Lock-affecting event acts on.

    `payload.project_id` is authoritative (core/SUBSTRATE.md §Project events);
    the event's `project` field is the fallback for chains that omit it. Returns
    None for `_harness`-scoped meta events that name no project — those are
    harness-level bookkeeping (toolchain anchors, friction, soul anchors) and
    never move the Lock.
    """
    payload = event.get("payload") or {}
    target = payload.get("project_id") or event.get("project")
    if not target or target == "_harness":
        return None
    return target


def check_lock_enforcement(events: list) -> list:
    """Layer 1 check 15: the Lock's switch protocol is enforced, not promised.

    core/LOCK.md §The Switch Protocol: switching projects is two events, never
    one — `project.park` or `project.archive` on the current project, then
    `project.activate` on the new one. A field deployment appended
    `project.activate` with no preceding release and nothing refused it: the
    refusal existed only as prose in LOCK.md, so two projects were structurally
    active at once and the projection that "refuses to point at two paths" was
    simply written twice.

    Bootstrap (the first activate in a chain) is legal. Re-activating the project
    that is already active is legal — that is `hw bootstrap --resume` on a project
    that was never released, not a second concurrent project. After reporting a
    violation the offending activate is taken as the new active project, so one
    missing park is one failure rather than a failure on every activate after it.
    """
    failures = []
    active = None
    active_since = None

    for event in events:
        kind = event.get("kind")
        if kind == "project.activate":
            target = lock_target(event)
            if target is None:
                continue
            if active is not None and active != target:
                failures.append(
                    f"{target}: lock_activate_without_release "
                    f"({event.get('id')} activates {target!r} while {active!r} is "
                    f"still active (activated at {active_since}); no "
                    f"project.park / project.archive for {active!r} in between - "
                    f"see core/LOCK.md, The Switch Protocol)"
                )
            active, active_since = target, event.get("id")
        elif kind in PROJECT_RELEASE_KINDS:
            target = lock_target(event)
            if target is not None and target == active:
                active, active_since = None, None

    return failures


def active_project(events: list) -> str | None:
    """The project holding the Lock at the end of the chain, or None.

    Same walk as check_lock_enforcement, without the reporting: last activated,
    not since parked or archived (core/LOCK.md §Substrate).
    """
    active = None
    for event in events:
        kind = event.get("kind")
        target = lock_target(event)
        if target is None:
            continue
        if kind == "project.activate":
            active = target
        elif kind in PROJECT_RELEASE_KINDS and target == active:
            active = None
    return active


def find_schema_dir(workspace: Path, schema: str) -> Path | None:
    """Locate `schemas/projects/<schema>/`, in the workspace or beside it.

    A harness instance may hold its own copy of the schema pack, or run out of a
    checkout whose `schemas/` sits one level up from the workspace; the shipped
    checks already probe both, and this centralizes that probe.
    """
    for root in (workspace, workspace.parent):
        candidate = root / "schemas" / "projects" / schema
        if candidate.is_dir():
            return candidate
    return None


def parse_semver(version) -> tuple | None:
    """Parse `X.Y.Z` (with optional trailing pre-release/build text) into a
    comparable tuple. Missing minor/patch read as 0, so `6.0` == `6.0.0`. Returns
    None if there is no leading numeric release to compare.
    """
    if not isinstance(version, str):
        return None
    m = re.match(r"^\s*v?(\d+)(?:\.(\d+))?(?:\.(\d+))?", version.strip())
    if not m:
        return None
    return tuple(int(part) if part else 0 for part in m.groups())


def compare_semver(left, right) -> int | None:
    """-1 / 0 / 1 for left <=> right; None if either side is unparseable."""
    a, b = parse_semver(left), parse_semver(right)
    if a is None or b is None:
        return None
    return (a > b) - (a < b)


def parse_schema_harness_version(path: Path) -> str | None:
    """Read the top-level `harness_version:` a schema.yaml declares."""
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^harness_version:\s*(.+?)\s*$", text, re.MULTILINE)
    if not m:
        return None
    value = re.sub(r"\s+#.*$", "", m.group(1)).strip().strip('"').strip("'")
    return value or None


def check_harness_version(workspace: Path, events: list) -> tuple:
    """Layer 1 check 16: refuse a schema built against a newer substrate.

    CONTRIBUTING.md §5 has stated since v5.1.1 that the harness MUST refuse to
    run a schema whose `harness_version` exceeds the harness's own. No such check
    existed anywhere — which is how the repo reached a state where the harness
    identified as 5.2.1 while the `program` schema declared 5.3.0, and nothing
    noticed that the newest schema was, by the repo's own rule, unrunnable.

    Scoped to the active project's schema (core/LOCK.md: one project holds the
    instance at a time, and its schema is the one in force). A schema older than
    the harness is fine and reported as a note; an unparseable or undeclared
    version is a note, not a refusal, since a missing declaration is missing
    information rather than evidence of incompatibility.

    Returns (failures, notes).
    """
    failures = []
    notes = []

    project_id = active_project(events)
    if not project_id:
        return failures, notes

    schema = find_schema_for_project(workspace, project_id)
    if not schema:
        return failures, notes

    schema_dir = find_schema_dir(workspace, schema)
    if schema_dir is None:
        return failures, notes

    declared = parse_schema_harness_version(schema_dir / "schema.yaml")
    if declared is None:
        notes.append(
            f"{project_id}: harness_version_undeclared "
            f"(schema {schema!r} declares no harness_version; harness is "
            f"{HARNESS_VERSION})"
        )
        return failures, notes

    order = compare_semver(declared, HARNESS_VERSION)
    if order is None:
        notes.append(
            f"{project_id}: harness_version_unparseable "
            f"(schema {schema!r} declares harness_version {declared!r}; "
            f"cannot compare against {HARNESS_VERSION})"
        )
    elif order > 0:
        failures.append(
            f"{project_id}: harness_version_too_new "
            f"(schema {schema!r} declares harness_version {declared}; this "
            f"harness is {HARNESS_VERSION}. Refusing to run a schema built "
            f"against a newer substrate - it may rely on primitives this "
            f"harness does not implement. Upgrade the harness, or pin the "
            f"schema to {HARNESS_VERSION}. See CONTRIBUTING.md section 5.)"
        )
    elif order < 0:
        notes.append(
            f"{project_id}: harness_version_older "
            f"(schema {schema!r} declares harness_version {declared}; harness is "
            f"{HARNESS_VERSION} - older is fine, the schema simply predates this "
            f"substrate)"
        )

    return failures, notes


def find_project_lifecycle(workspace: Path, project_id: str) -> str | None:
    """Read a project's declared lifecycle from PROJECT.md.

    `lifecycle` is Mutable Surface, not event-sourced (core/SUBSTRATE.md
    §Boundary Rule), so PROJECT.md is where it lives. Prefer a `## Lifecycle`
    section's first content line; fall back to an inline `lifecycle: <value>`
    declaration anywhere in the file. `terminal` is the documented default
    (core/LOCK.md §Ongoing Projects), so a PROJECT.md that declares nothing reads
    as terminal.

    Returns "ongoing", "terminal", or None when the answer is genuinely unknown:
    no PROJECT.md at all, or a scaffolded one whose `{{ lifecycle }}` placeholder
    was never substituted. Unknown means the terminal-lifecycle check stands down
    rather than guessing.
    """
    project_md = workspace / "projects" / project_id / "PROJECT.md"
    if not project_md.exists():
        return None
    text = project_md.read_text(encoding="utf-8")

    lines = text.splitlines()
    for idx, line in enumerate(lines):
        if line.strip().lower() not in ("## lifecycle", "# lifecycle"):
            continue
        for body in lines[idx + 1:]:
            stripped = body.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                break
            if "{{" in stripped:
                return None
            lowered = stripped.lower()
            if "ongoing" in lowered:
                return "ongoing"
            if "terminal" in lowered:
                return "terminal"
            break
        break

    m = re.search(r"lifecycle:\s*[\"'`]?(ongoing|terminal)\b", text, re.IGNORECASE)
    if m:
        return m.group(1).lower()
    return "terminal"


def check_cycle_lifecycle(workspace: Path, events: list) -> list:
    """Layer 1 check 17: the v5.3 cycle lifecycle, specified but never implemented.

    core/SUBSTRATE.md §Lifecycle events and §`hw cycle`, plus core/LOCK.md
    §Ongoing Projects, declare four failures that no code enforced:

      - `cycle.close` with no matching open        -> cycle_close_without_open
      - a second `cycle.open` with no close between -> cycle_open_without_close
      - either kind on a `lifecycle: terminal` project -> cycle_on_terminal_lifecycle
      - `project.archive` (hw wrap) with a cycle open  -> wrap_with_open_cycle

    "Matching" is by `cycle_id` when both events carry one: closing C-002 while
    C-003 is the open cycle is a close without a matching open, not a close of
    whatever happens to be open. A close is treated as closing the open cycle
    either way, so one mispaired close is one failure rather than a cascade.
    """
    failures = []
    by_project = defaultdict(list)
    for event in events:
        by_project[event.get("project")].append(event)

    for project_id, project_events in by_project.items():
        if not project_id or project_id == "_harness":
            continue

        kinds = {ev.get("kind") for ev in project_events}
        has_cycles = bool(kinds & {"cycle.open", "cycle.close"})
        lifecycle = find_project_lifecycle(workspace, project_id) if has_cycles else None

        open_cycle = None  # (cycle_id, event_id)
        for event in project_events:
            kind = event.get("kind")
            payload = event.get("payload") or {}
            cycle_id = payload.get("cycle_id")

            if kind in ("cycle.open", "cycle.close") and lifecycle == "terminal":
                failures.append(
                    f"{project_id}: cycle_on_terminal_lifecycle "
                    f"({event.get('id')} {kind} on a project whose PROJECT.md "
                    f"declares lifecycle: terminal; cycles are valid only on "
                    f"lifecycle: ongoing - see core/LOCK.md, Ongoing Projects)"
                )

            if kind == "cycle.open":
                if open_cycle is not None:
                    failures.append(
                        f"{project_id}: cycle_open_without_close "
                        f"({event.get('id')} opens {cycle_id or '<no cycle_id>'} "
                        f"while {open_cycle[0] or '<no cycle_id>'} (opened at "
                        f"{open_cycle[1]}) is still open; close the current cycle "
                        f"with hw cycle close first)"
                    )
                open_cycle = (cycle_id, event.get("id"))

            elif kind == "cycle.close":
                if open_cycle is None:
                    failures.append(
                        f"{project_id}: cycle_close_without_open "
                        f"({event.get('id')} closes "
                        f"{cycle_id or '<no cycle_id>'}; no cycle is open)"
                    )
                elif cycle_id and open_cycle[0] and cycle_id != open_cycle[0]:
                    failures.append(
                        f"{project_id}: cycle_close_without_open "
                        f"({event.get('id')} closes {cycle_id}; the open cycle is "
                        f"{open_cycle[0]}, opened at {open_cycle[1]})"
                    )
                open_cycle = None

            elif kind in ("project.archive", "project.wrap"):
                if open_cycle is not None:
                    failures.append(
                        f"{project_id}: wrap_with_open_cycle "
                        f"({event.get('id')} {kind} while "
                        f"{open_cycle[0] or '<no cycle_id>'} (opened at "
                        f"{open_cycle[1]}) is still open; run hw cycle close "
                        f"before wrapping an ongoing project)"
                    )
                    open_cycle = None

    return failures


def parse_verification_yaml_checked_claims(path: Path) -> list:
    """Minimal YAML reader for verification.yaml's `checked_claims.required_for`
    list. Mirrors the block-list convention already used by
    `external_state_readback.required_for` in shipped capability-gates.yaml
    files (quoted or bare items, one per `- ` line, indented under the key).
    Also accepts an inline `required_for: [a, b]` form. Dependency-free by
    design, matching parse_capability_gates_yaml above.
    """
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^checked_claims:\s*$", text, re.MULTILINE)
    if not m:
        return []
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
    block = "\n".join(block_lines)

    inline = re.search(r"required_for:\s*\[([^\]]*)\]", block)
    if inline:
        return [s.strip().strip('"').strip("'")
                for s in inline.group(1).split(",") if s.strip()]

    rf = re.search(r"required_for:\s*$", block, re.MULTILINE)
    if not rf:
        return []
    patterns = []
    for line in block[rf.end():].splitlines():
        stripped = line.strip()
        if stripped == "":
            continue
        item_m = re.match(r"-\s*(.+)$", stripped)
        if not item_m:
            break
        item = re.sub(r"\s+#.*$", "", item_m.group(1)).strip()
        patterns.append(item.strip('"').strip("'"))
    return patterns


def capability_gates_allows_shell(path: Path) -> bool:
    """True if the schema's capability-gates.yaml declares `shell_exec` as an
    available tool: it appears in some task's `required_tools` list and is not
    listed under `not_required`. No file, or no declaration either way,
    defaults to False (closed) — see core/SUBSTRATE.md §Checked Claims,
    the shell-capability gate for cmd_exit predicates.
    """
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")

    not_required = set()
    inline = re.search(r"^not_required:\s*\[([^\]]*)\]", text, re.MULTILINE)
    if inline:
        not_required = {s.strip().strip('"').strip("'")
                         for s in inline.group(1).split(",") if s.strip()}
    else:
        block_m = re.search(r"^not_required:\s*$", text, re.MULTILINE)
        if block_m:
            for line in text[block_m.end():].splitlines():
                if line.strip() == "":
                    continue
                if not line.startswith(" ") and not line.startswith("\t"):
                    break
                item_m = re.match(r"\s*-\s*([^\s#]+)", line)
                if item_m:
                    not_required.add(item_m.group(1).strip('"').strip("'"))

    if "shell_exec" in not_required:
        return False

    for required_tools in re.findall(r"required_tools:\s*\[([^\]]*)\]", text):
        items = {s.strip().strip('"').strip("'")
                  for s in required_tools.split(",") if s.strip()}
        if "shell_exec" in items:
            return True
    return False


def validate_claim_predicate(predicate) -> str | None:
    """Return an error string if `predicate` is malformed, else None."""
    if not isinstance(predicate, dict) or len(predicate) != 1:
        return "predicate must be an object with exactly one key"
    ((pkind, pval),) = predicate.items()
    if pkind not in CLAIM_PREDICATE_KINDS:
        return f"unknown predicate kind {pkind!r}"

    if pkind in ("file_exists", "file_absent"):
        if not isinstance(pval, str) or not pval:
            return f"{pkind} value must be a non-empty path string"
        if PureWindowsPath(pval).is_absolute() or PurePosixPath(pval).is_absolute():
            return f"{pkind} path must be workspace-relative, not absolute: {pval!r}"
    elif pkind == "file_sha256":
        if not isinstance(pval, dict) or "path" not in pval or "hash" not in pval:
            return "file_sha256 requires {path, hash}"
        if not re.fullmatch(r"[0-9a-fA-F]{64}", str(pval.get("hash", ""))):
            return "file_sha256 hash must be full 64-character hex"
    elif pkind == "cmd_exit":
        if not isinstance(pval, dict) or "cmd" not in pval or not pval.get("cmd"):
            return "cmd_exit requires at least {cmd}"
    elif pkind == "url_status":
        if not isinstance(pval, dict) or "url" not in pval or "expect_code" not in pval:
            return "url_status requires {url, expect_code}"
    return None


def validate_claim_block(claim) -> str | None:
    """Return an error string if `claim` is a malformed claim: block, else None."""
    if not isinstance(claim, dict):
        return "claim must be an object"
    if "predicate" not in claim:
        return "missing predicate"
    reason = validate_claim_predicate(claim["predicate"])
    if reason:
        return reason
    if "checked_at" not in claim or not isinstance(claim["checked_at"], str):
        return "missing/invalid checked_at"
    if "passed" not in claim or not isinstance(claim["passed"], bool):
        return "missing/invalid passed"
    return None


def collect_claim_entries(events: list) -> list:
    """Return (event, label, claim) for every location a claim: block may
    appear, per core/SUBSTRATE.md §Checked Claims: top-level `claim` on
    world-state-asserting `.add`/`.complete`/`.read_back` payloads, and
    per-item `claim` on scope.complete's scope_items[].
    """
    entries = []
    for ev in events:
        kind = ev.get("kind")
        payload = ev.get("payload") or {}
        if kind in CLAIM_BEARING_KINDS:
            claim = payload.get("claim")
            if claim is not None:
                entries.append((ev, kind, claim))
        elif kind == "scope.complete":
            for item in payload.get("scope_items", []) or []:
                if not isinstance(item, dict):
                    continue
                claim = item.get("claim")
                if claim is not None:
                    label = f"scope_items[{item.get('id') or item.get('name') or '?'}]"
                    entries.append((ev, label, claim))
    return entries


def check_claims_structural(events: list) -> list:
    """Layer 1 check 13, part 1: every claim: block present, anywhere, is
    well-formed — regardless of whether the schema requires it.
    """
    malformed = []
    for ev, label, claim in collect_claim_entries(events):
        reason = validate_claim_block(claim)
        if reason:
            malformed.append(f"{ev['id']} {label}: {reason}")
    return malformed


def _claim_pattern_matches(event_kind: str, risk_level, pattern: str) -> bool:
    """Match one checked_claims.required_for pattern against an event.
    Pattern is `<event_kind>` or `<event_kind>:<risk_level>` — the risk-level
    suffix is only meaningful for task.complete (see core/SUBSTRATE.md
    §Checked Claims).
    """
    if ":" in pattern:
        p_kind, p_risk = pattern.split(":", 1)
    else:
        p_kind, p_risk = pattern, None
    if event_kind != p_kind:
        return False
    if p_risk is None:
        return True
    return (risk_level or "").lower() == p_risk.strip().lower()


def check_claims_required(workspace: Path, events: list) -> list:
    """Layer 1 check 13, part 2: schema-required claims are present and passing.

    Reads each project's schema's verification.yaml `checked_claims.required_for`.
    No schema, no verification.yaml, or no checked_claims key: the requirement
    is off for that project (graceful degrade — never required by default).
    """
    failures = []
    by_project = defaultdict(list)
    for ev in events:
        by_project[ev.get("project")].append(ev)

    for project_id, project_events in by_project.items():
        if not project_id or project_id == "_harness":
            continue

        schema = find_schema_for_project(workspace, project_id)
        if not schema:
            continue

        verification_path = (workspace / "schemas" / "projects" / schema
                              / "verification.yaml")
        if not verification_path.exists():
            verification_path = (workspace.parent / "schemas" / "projects"
                                  / schema / "verification.yaml")
        required_for = parse_verification_yaml_checked_claims(verification_path)
        if not required_for:
            continue

        task_meta = {}
        for ev in project_events:
            if ev.get("kind") == "task.create":
                payload = ev.get("payload", {}) or {}
                tid = payload.get("task_id")
                fm = payload.get("frontmatter") or {}
                if tid:
                    task_meta[tid] = fm

        for ev in project_events:
            kind = ev.get("kind")
            payload = ev.get("payload") or {}

            if kind == "scope.complete":
                if not any(_claim_pattern_matches(kind, None, p) for p in required_for):
                    continue
                for item in payload.get("scope_items", []) or []:
                    if not isinstance(item, dict):
                        continue
                    label = item.get("id") or item.get("name") or "?"
                    claim = item.get("claim")
                    if claim is None:
                        failures.append(
                            f"{project_id}: checked_claims_missing "
                            f"({ev['id']} scope_items[{label}])"
                        )
                        continue
                    reason = validate_claim_block(claim)
                    if reason:
                        failures.append(
                            f"{project_id}: checked_claims_missing "
                            f"({ev['id']} scope_items[{label}]: malformed — {reason})"
                        )
                        continue
                    if not claim.get("passed"):
                        failures.append(
                            f"{project_id}: checked_claims_predicate_failed "
                            f"({ev['id']} scope_items[{label}])"
                        )
                continue

            risk_level = None
            if kind == "task.complete":
                tid = payload.get("task_id")
                risk_level = (task_meta.get(tid, {}) or {}).get("risk_level")

            if not any(_claim_pattern_matches(kind, risk_level, p) for p in required_for):
                continue

            claim = payload.get("claim")
            if claim is None:
                failures.append(f"{project_id}: checked_claims_missing ({ev['id']} {kind})")
                continue
            reason = validate_claim_block(claim)
            if reason:
                failures.append(
                    f"{project_id}: checked_claims_missing "
                    f"({ev['id']} {kind}: malformed — {reason})"
                )
                continue
            if not claim.get("passed"):
                failures.append(
                    f"{project_id}: checked_claims_predicate_failed ({ev['id']} {kind})"
                )

    return failures


def evaluate_claim_predicate(workspace: Path, predicate: dict, allow_cmd: bool,
                              shell_allowed_cache: dict, project_id) -> tuple:
    """Replay one predicate against the current world. Returns (status, detail)
    with status in {pass, fail, error, skipped}. See core/VERIFICATION.md
    §Claim Replay for the algorithm this implements.
    """
    ((pkind, pval),) = predicate.items()
    try:
        if pkind == "file_exists":
            exists = (workspace / pval).exists()
            return ("pass", f"{pval} exists") if exists else ("fail", f"{pval} does not exist")

        if pkind == "file_absent":
            exists = (workspace / pval).exists()
            return ("fail", f"{pval} exists") if exists else ("pass", f"{pval} absent")

        if pkind == "file_sha256":
            target = workspace / pval["path"]
            if not target.exists():
                return ("fail", f"{pval['path']} does not exist")
            actual = sha256_hex(target.read_bytes())
            expected = str(pval["hash"]).lower()
            if actual.lower() == expected:
                return ("pass", f"{pval['path']} sha256 matches")
            return ("fail", f"{pval['path']} sha256 {actual} != expected {expected}")

        if pkind == "url_status":
            req = urllib.request.Request(pval["url"], method="HEAD")
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    code = resp.status
            except urllib.error.HTTPError as e:
                code = e.code
            if code == pval["expect_code"]:
                return ("pass", f"{pval['url']} -> {code}")
            return ("fail", f"{pval['url']} -> {code}, expected {pval['expect_code']}")

        if pkind == "cmd_exit":
            if not allow_cmd:
                return ("skipped", "shell predicates disabled")
            if project_id not in shell_allowed_cache:
                allowed = False
                schema = find_schema_for_project(workspace, project_id) if project_id else None
                if schema:
                    cap_path = (workspace / "schemas" / "projects" / schema
                                / "capability-gates.yaml")
                    if not cap_path.exists():
                        cap_path = (workspace.parent / "schemas" / "projects"
                                    / schema / "capability-gates.yaml")
                    allowed = capability_gates_allows_shell(cap_path)
                shell_allowed_cache[project_id] = allowed
            if not shell_allowed_cache[project_id]:
                return ("skipped",
                        "shell_exec not permitted by workspace capability declarations")
            try:
                proc = subprocess.run(
                    pval["cmd"], shell=True, capture_output=True, text=True,
                    timeout=30, cwd=str(workspace),
                )
            except Exception as e:  # noqa: BLE001 — replay must not crash on a bad cmd
                return ("error", f"execution error: {e}")
            expect_code = pval.get("expect_code", 0)
            output = (proc.stdout or "") + (proc.stderr or "")
            if proc.returncode != expect_code:
                return ("fail", f"exit {proc.returncode}, expected {expect_code}")
            substr = pval.get("expect_substring")
            if substr and substr not in output:
                return ("fail", f"output missing expected substring {substr!r}")
            return ("pass", f"exit {proc.returncode}")
    except Exception as e:  # noqa: BLE001 — a single bad claim must not abort replay
        return ("error", str(e))

    return ("error", f"unhandled predicate kind {pkind!r}")


def replay_claims(workspace: Path, events: list, allow_cmd: bool) -> dict:
    """`hw verify --claims`: re-evaluate every recorded claim predicate against
    the current world. Independent of, and reported separately from, chain
    integrity. See core/VERIFICATION.md §Claim Replay.
    """
    entries = collect_claim_entries(events)
    details = []
    shell_cache = {}

    for ev, label, claim in entries:
        malformed = validate_claim_block(claim)
        if malformed:
            details.append({"event_id": ev["id"], "label": label, "status": "error",
                             "detail": "malformed, not replayed"})
            continue
        status, detail = evaluate_claim_predicate(
            workspace, claim["predicate"], allow_cmd, shell_cache, ev.get("project"),
        )
        details.append({"event_id": ev["id"], "label": label, "status": status,
                         "detail": detail})

    summary = {"claims_checked": len(details), "pass": 0,
               "fail": [], "error": [], "skipped": [], "details": details}
    for d in details:
        line = f"{d['event_id']}.{d['label']}: {d['detail']}"
        if d["status"] == "pass":
            summary["pass"] += 1
        elif d["status"] == "fail":
            summary["fail"].append(line)
        elif d["status"] == "error":
            summary["error"].append(line)
        elif d["status"] == "skipped":
            summary["skipped"].append(line)

    if not details:
        summary["result"] = "N/A"
    elif summary["fail"]:
        summary["result"] = "FAIL"
    else:
        summary["result"] = "PASS"
    return summary


def render_claims(summary: dict) -> str:
    lines = [
        "hw verify --claims",
        f"  claims_checked: {summary['claims_checked']}",
        f"  pass:           {summary['pass']}",
        f"  fail:           {len(summary['fail'])} {summary['fail']}",
        f"  error:          {len(summary['error'])} {summary['error']}",
        f"  skipped:        {len(summary['skipped'])} {summary['skipped']}",
        f"  result:         {summary['result']}",
    ]
    return "\n".join(lines)


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


def load_events_with_lines(events_path: Path) -> tuple:
    """Load events plus the 1-based file line each came from.

    The line numbers are not derivable from list position once blank lines are
    skipped, and duplicate-ID adjudication needs the real line to open the file
    at. See check_id_integrity.
    """
    events = []
    line_numbers = []
    with events_path.open(encoding="utf-8") as f:
        for line_no, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line:
                continue
            events.append(json.loads(line))
            line_numbers.append(line_no)
    return events, line_numbers


def load_events(events_path: Path) -> list:
    return load_events_with_lines(events_path)[0]


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
        "duplicate_event_ids": [],
        "non_monotonic_event_ids": [],
        "lock_violations": [],
        "harness_version_failures": [],
        "harness_version_notes": [],
        "cycle_lifecycle_failures": [],
        "scope_completeness_failures": [],
        "external_state_readback_failures": [],
        "external_state_readback_warnings": [],
        "bootstrap_probe_failures": [],
        "checked_claims_malformed": [],
        "checked_claims_required_failures": [],
        "result": "PASS",
    }

    if not events_path.exists():
        result["result"] = "FAIL"
        result["error"] = f"events.jsonl not found at {events_path}"
        return result

    events, line_numbers = load_events_with_lines(events_path)
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

    duplicates, non_monotonic = check_id_integrity(events, line_numbers)
    result["duplicate_event_ids"] = duplicates
    result["non_monotonic_event_ids"] = non_monotonic
    result["lock_violations"] = check_lock_enforcement(events)
    hv_failures, hv_notes = check_harness_version(workspace, events)
    result["harness_version_failures"] = hv_failures
    result["harness_version_notes"] = hv_notes
    result["cycle_lifecycle_failures"] = check_cycle_lifecycle(workspace, events)
    result["scope_completeness_failures"] = check_scope_completeness(workspace, events)
    esrb_failures, esrb_warnings = check_external_state_readback(workspace, events)
    result["external_state_readback_failures"] = esrb_failures
    result["external_state_readback_warnings"] = esrb_warnings
    result["bootstrap_probe_failures"] = check_bootstrap_probe(events)
    result["checked_claims_malformed"] = check_claims_structural(events)
    result["checked_claims_required_failures"] = check_claims_required(workspace, events)

    blocking = (
        result["tamper"]
        or result["chain_breaks"]
        or result["projection_drift"]
        or result["missing_projections"]
        or result["broken_citations"]
        or result["malformed_payloads"]
        or result["duplicate_event_ids"]
        or result["non_monotonic_event_ids"]
        or result["lock_violations"]
        or result["harness_version_failures"]
        or result["cycle_lifecycle_failures"]
        or result["scope_completeness_failures"]
        or result["external_state_readback_failures"]
        or result["bootstrap_probe_failures"]
        or result["checked_claims_malformed"]
        or result["checked_claims_required_failures"]
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
        f"  duplicate_event_ids:   {len(result['duplicate_event_ids'])} {result['duplicate_event_ids']}",
        f"  non_monotonic_ids:     {len(result['non_monotonic_event_ids'])} {result['non_monotonic_event_ids']}",
        f"  lock_violations:       {len(result['lock_violations'])} {result['lock_violations']}",
        f"  harness_version:       {len(result['harness_version_failures'])} {result['harness_version_failures']}",
        f"  harness_version_note:  {len(result['harness_version_notes'])} {result['harness_version_notes']}",
        f"  cycle_lifecycle:       {len(result['cycle_lifecycle_failures'])} {result['cycle_lifecycle_failures']}",
        f"  scope_completeness:    {len(result['scope_completeness_failures'])} {result['scope_completeness_failures']}",
        f"  ext_state_readback:    {len(result['external_state_readback_failures'])} {result['external_state_readback_failures']}",
        f"  ext_state_warnings:    {len(result['external_state_readback_warnings'])} {result['external_state_readback_warnings']}",
        f"  bootstrap_probe:       {len(result['bootstrap_probe_failures'])} {result['bootstrap_probe_failures']}",
        f"  checked_claims:        {len(result['checked_claims_malformed'])} {result['checked_claims_malformed']}",
        f"  checked_claims_req:    {len(result['checked_claims_required_failures'])} {result['checked_claims_required_failures']}",
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
    parser.add_argument("--claims", action="store_true",
                        help="Also replay recorded claim: predicates against the current "
                             "world (v5.3, core/VERIFICATION.md §Claim Replay). Reported "
                             "separately from, and never affecting, chain integrity.")
    parser.add_argument("--allow-cmd", action="store_true",
                        help="Permit cmd_exit claim predicates to execute during --claims "
                             "replay. Still gated by the workspace's shell_exec capability "
                             "declaration (core/SUBSTRATE.md §Checked Claims). Default: "
                             "cmd_exit predicates are skipped.")
    args = parser.parse_args()

    workspace = args.workspace.resolve()
    if not workspace.is_dir():
        print(f"Workspace path is not a directory: {workspace}", file=sys.stderr)
        return 2

    result = verify(workspace, args.since)
    print(render(result))
    exit_code = 0 if result["result"] == "PASS" else 1

    if args.claims:
        events_path = workspace / ".hyperworker" / "events.jsonl"
        if events_path.exists():
            claims_summary = replay_claims(workspace, load_events(events_path), args.allow_cmd)
        else:
            claims_summary = {"claims_checked": 0, "pass": 0, "fail": [], "error": [],
                               "skipped": [], "result": "N/A", "details": []}
        print()
        print(render_claims(claims_summary))
        if claims_summary["result"] == "FAIL":
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
