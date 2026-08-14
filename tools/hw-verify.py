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

v6.0.0: verifier hardening. Five checks that the docs promised and no code
performed (core/VERIFICATION.md §Layer 1 checks 14-18):

  14 ID integrity        duplicate or non-increasing event IDs (the field
                         incident where EV-0116..EV-0120 exist twice with
                         correct prev_hash links and `hw verify` said PASS)
  15 Lock enforcement    project.activate while another project is active
  16 harness_version     refuse a schema pinned above HARNESS_VERSION
  17 Cycle lifecycle     the v5.3 cycle.open/cycle.close FAILs, unimplemented
  18 Schema-declared     custom Layer 1 checks a schema's capability-gates.yaml
                         declares (the program pack's three)

Each ships with a test suite: tools/test_id_integrity.py,
test_lock_enforcement.py, test_harness_version.py, test_cycle_lifecycle.py,
test_program_checks.py.

v6.0.0 field evidence: three more checks and two relaxations, each from a
documented failure of the same ten-week production deployment
(core/VERIFICATION.md §Layer 1 checks 19-21):

  19 Exclusion discipline  a hypothesis is `excluded` only with a test_ref
                           naming a dynamic test (AP-008: a static read struck
                           the true root cause off the list; ~19 attempts burned)
  20 Evidence capture      evidence.capture well-formedness and ED-id uniqueness
                           (raw output survived only when hand-copied by a human)
  21 Open loops            loop.open/loop.close pairing, and a session.handoff
                           that omits a loop open at that point (a fully gated
                           action sat unconsumed for five weeks)

v6.0.0 protocol features, same deployment (core/VERIFICATION.md §Layer 1
check 22 and core/SUBSTRATE.md §Secrets Gate):

  22 Secrets gate         payload content that looks like a credential
                          (a sync digest copied a DSRM password verbatim into
                          an append-only log; only real-world rotation
                          remediates). A WARNING by default -- history must
                          keep verifying -- and a FAIL under --strict-secrets.
                          scan_for_secrets() is the reference scanner `hw add`
                          runs BEFORE appending, where the refusal is free.
                          Suite: tools/test_secrets_gate.py.

`profile: single-executor` (core/SUBSTRATE.md §Execution Profile) is read the
same way `lifecycle` is -- schema.yaml wins, then PROJECT.md, unknown reads as
the `multi-actor` default. Under it, a missing `actor` is not a malformed
payload (it defaults to `executor`) and citation handles may drop the `#hash`
suffix; every other check is unchanged, because the hashes are still in the
artifacts. Suite: tools/test_execution_profile.py.

Relaxed, not tightened: friction.log now needs only a one-line `note` (four
entries in 130 events -- the six-field form went unused), with the pre-v6 rich
form still accepted; operator.correction is well-formedness only. Both live in
check_note_payloads. Suites: test_exclusion_discipline.py, test_evidence_capture.py,
test_open_loops.py, test_one_line_events.py.
"""

import argparse
import hashlib
import json
import math
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
                 "sources", "claims", "contradictions",
                 "evidence")   # v6.0.0 evidence.capture projections
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
    "evidence.capture",            # v6.0.0 field-evidence primitives
    "operator.correction",         # v6.0.0; the invisible channel, made visible
    "loop.open", "loop.close",     # v6.0.0 open-loop tracking
}

# Required payload fields per v5.1 event kind. None means no per-kind structural
# check beyond schema validation (which is out of scope for hw verify; it lives
# in the schema-validation step at hw add time).
# The pre-v6.0.0 rich friction.log form. Still accepted; no longer the price of
# admission. See check_note_payloads and core/SUBSTRATE.md §Friction Log Event Kind.
FRICTION_RICH_FIELDS = ("type", "description", "surfaced_by", "severity")

REQUIRED_PAYLOAD_FIELDS = {
    # friction.log is validated by check_note_payloads, which accepts either the
    # v6.0.0 slim form (note) or the pre-v6 rich form -- an either/or a flat
    # required-field list cannot express.
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
    # v6.0.0 field-evidence kinds. The content-form rules for
    # evidence.capture live in check_evidence_capture (one of content /
    # content_path, which a flat required-field list cannot express).
    "evidence.capture": ("id", "producing_command", "captured_at", "summary"),
    "loop.open": ("loop_id", "description", "blocking_on", "opened_at"),
    "loop.close": ("loop_id", "closed_at", "resolution"),
    # session.handoff.open_loops is required from v6.0.0 but deliberately
    # NOT listed here: a missing field on a pre-v6 chain is a note from
    # check_open_loops, not a blocking malformed-payload FAIL.
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


# ---------------------------------------------------------------------------
# v6.0.0 field-evidence checks (Layer 1 checks 19+). Each one comes from a
# documented failure of a ten-week production deployment; see core/SUBSTRATE.md
# for the section that states the protocol and the field evidence behind it.
# ---------------------------------------------------------------------------

EVIDENCE_ID_RE = re.compile(r"^ED-\d{3,}$")
EVIDENCE_ID_CITE_RE = re.compile(r"\bED-\d{3,}\b")
HYPOTHESIS_STATUSES = ("open", "suspect", "excluded")


# The v6.0.0 one-line kinds. Both exist because a heavier form went unused in
# the field: friction.log got 4 entries in 130 events, and operator corrections
# were never captured at all.
ONE_LINE_KINDS = ("friction.log", "operator.correction")


def check_open_loops(events: list) -> tuple:
    """Layer 1 check 21: gated actions stay countable.

    core/SUBSTRATE.md §Open Loops. Field evidence: a message cleared every
    technical gate for a server rejoin and said the only remaining gate was the
    operator's word. Nothing tracked it. The divergence between believed and
    actual state surfaced FIVE WEEKS later, through an unrelated symptom, in
    production. Nothing was wrong with the work -- "waiting on X" was a sentence
    in a document rather than a row anything could count.

      - `loop.close` with no matching open      -> loop_close_without_open
      - a `loop_id` opened twice in one project -> duplicate_loop_open
      - a handoff omitting a loop open then     -> handoff_missing_open_loops

    Loops are never reopened: a recurrence is a new L id, so a second open of the
    same `loop_id` is a duplicate whether or not the first was closed.

    Staleness is deliberately NOT checked here. It is date-dependent -- a chain
    that verifies today would fail tomorrow with no event appended -- so it lives
    in `hw status`, which leads with OVERDUE OPEN LOOPS.

    Returns (failures, notes). A `session.handoff` with no `open_loops` field at
    all is a note: the field is required from v6.0.0, and pre-v6 chains keep
    verifying.
    """
    failures = []
    notes = []
    by_project = defaultdict(list)
    for event in events:
        by_project[event.get("project")].append(event)

    for project_id, project_events in by_project.items():
        if not project_id or project_id == "_harness":
            continue

        opened = {}   # loop_id -> event id of the open
        open_now = set()

        for event in project_events:
            kind = event.get("kind")
            payload = event.get("payload") or {}
            if not isinstance(payload, dict):
                payload = {}
            loop_id = payload.get("loop_id")

            if kind == "loop.open":
                if loop_id in opened:
                    failures.append(
                        f"{project_id}: duplicate_loop_open "
                        f"({event.get('id')} opens {loop_id}, already opened by "
                        f"{opened[loop_id]}; loops are not reopened - a "
                        f"recurrence is a new L id)"
                    )
                else:
                    opened[loop_id] = event.get("id")
                open_now.add(loop_id)

            elif kind == "loop.close":
                if loop_id not in open_now:
                    detail = ("no loop is open under that id"
                              if loop_id not in opened
                              else f"{loop_id} was already closed")
                    failures.append(
                        f"{project_id}: loop_close_without_open "
                        f"({event.get('id')} closes "
                        f"{loop_id or '<no loop_id>'}; {detail})"
                    )
                else:
                    open_now.discard(loop_id)

            elif kind == "session.handoff":
                declared = payload.get("open_loops")
                if declared is None:
                    notes.append(
                        f"{project_id}: handoff_open_loops_absent "
                        f"({event.get('id')} predates the v6.0.0 open_loops "
                        f"field; open now: "
                        f"{sorted(open_now) if open_now else 'none'})"
                    )
                    continue
                if not isinstance(declared, list):
                    failures.append(
                        f"{project_id}: handoff_missing_open_loops "
                        f"({event.get('id')} open_loops is {type(declared).__name__}, "
                        f"expected a list of L ids (use [] for none))"
                    )
                    continue
                missing = sorted(loop for loop in open_now if loop not in declared)
                if missing:
                    failures.append(
                        f"{project_id}: handoff_missing_open_loops "
                        f"({event.get('id')} omits {', '.join(missing)}; a loop the "
                        f"next session cannot count is a loop nobody is holding)"
                    )

    return failures, notes


def check_note_payloads(events: list) -> list:
    """Well-formedness for the v6.0.0 one-line event kinds.

    `friction.log` (core/SUBSTRATE.md §Friction Log Event Kind): four entries in
    130 events across ten weeks. The mechanism existed and the operator wanted
    it; six fields "felt heavier than the value" and the run's best lessons went
    uncaptured. Well-formed now means a non-empty `note`, OR the full pre-v6 rich
    set -- both verify, so no chain has to migrate.

    `operator.correction` (§Operator Correction): well-formedness only. `note`
    present and non-empty; `context` and `should_have_lived` are optional and
    unchecked. Whether a correction was promoted into its should_have_lived home
    is a judgment the verifier cannot make, and a check that guessed would only
    teach agents to write nominal values.

    Returns strings for result["malformed_payloads"]: a payload that is neither
    shape is the same class of defect as a missing required field.
    """
    failures = []
    for event in events:
        kind = event.get("kind")
        if kind not in ONE_LINE_KINDS:
            continue
        payload = event.get("payload")
        if not isinstance(payload, dict):
            payload = {}

        note = payload.get("note")
        if isinstance(note, str) and note.strip():
            continue

        missing_rich = None
        if kind == "friction.log":
            missing_rich = [f for f in FRICTION_RICH_FIELDS if f not in payload]
            if not missing_rich:
                continue

        if "note" in payload:
            failures.append(
                f"{event.get('id')}:{kind} note is empty "
                f"(one line is the whole obligation)"
            )
        elif missing_rich is not None:
            failures.append(
                f"{event.get('id')}:{kind} missing ['note'] "
                f"(or the pre-v6 rich set, which is missing {missing_rich})"
            )
        else:
            failures.append(f"{event.get('id')}:{kind} missing ['note']")
    return failures


def check_evidence_capture(events: list) -> list:
    """Layer 1 check 20: `evidence.capture` well-formedness and ED-id uniqueness.

    core/SUBSTRATE.md §Evidence Capture. The payload carries the raw output a
    conclusion rested on, either inline (`content`) or by path (`content_path` +
    `content_sha256`) so a large log does not enter the hash chain. Exactly one
    form: two authorities for the same capture is the state the primitive exists
    to prevent.

    ED ids are unique across the whole log, not per project, because `test_ref`
    and finding evidence cite them bare (`ED-014`, no project qualifier).
    """
    failures = []
    seen = {}  # ED id -> event id

    for event in events:
        if event.get("kind") != "evidence.capture":
            continue
        payload = event.get("payload") or {}
        if not isinstance(payload, dict):
            payload = {}
        event_id = event.get("id")
        evidence_id = payload.get("id")

        if not isinstance(evidence_id, str) or not EVIDENCE_ID_RE.match(evidence_id):
            failures.append(
                f"{event_id}: evidence_id_malformed "
                f"(id {evidence_id!r}; expected ED-NNN, zero-padded to at least 3 digits)"
            )
        elif evidence_id in seen:
            failures.append(
                f"{event_id}: duplicate_evidence_id "
                f"({evidence_id} was already captured by {seen[evidence_id]}; "
                f"ED ids are unique across the whole log because citations carry "
                f"no project qualifier)"
            )
        else:
            seen[evidence_id] = event_id

        label = evidence_id if isinstance(evidence_id, str) else event_id
        has_inline = isinstance(payload.get("content"), str)
        has_path = isinstance(payload.get("content_path"), str) and payload["content_path"]

        if has_inline and has_path:
            failures.append(
                f"{label}: evidence_capture_content_ambiguous "
                f"({event_id} carries both inline content and content_path; "
                f"a capture has exactly one authority)"
            )
        elif not has_inline and not has_path:
            failures.append(
                f"{label}: evidence_capture_no_content "
                f"({event_id} carries neither content nor content_path; "
                f"a capture with no output captures nothing)"
            )
        elif has_path and not payload.get("content_sha256"):
            failures.append(
                f"{label}: evidence_capture_path_without_hash "
                f"({event_id} points at {payload['content_path']} with no "
                f"content_sha256; the path form still has to pin what was captured)"
            )

    return failures


def captured_evidence_ids(events: list) -> set:
    """Every well-formed ED id an `evidence.capture` event put in the chain."""
    ids = set()
    for event in events:
        if event.get("kind") != "evidence.capture":
            continue
        payload = event.get("payload") or {}
        evidence_id = payload.get("id") if isinstance(payload, dict) else None
        if isinstance(evidence_id, str) and EVIDENCE_ID_RE.match(evidence_id):
            ids.add(evidence_id)
    return ids


def hypothesis_entries(events: list) -> list:
    """(event, fields) pairs for every event carrying hypothesis state.

    Scoped to `finding.add` (where core/SUBSTRATE.md §Exclusion Discipline puts
    `status` / `test_ref`) plus any other `<kind>.add` that carries an explicit
    `test_ref` — schema-declared hypothesis kinds opt in by using the field.
    Deliberately NOT every payload with a `status` key: the program pack's
    `workstream.add` uses `status` for something else entirely.
    """
    entries = []
    for event in events:
        kind = event.get("kind") or ""
        if not kind.endswith(".add"):
            continue
        payload = event.get("payload")
        if not isinstance(payload, dict):
            continue
        fields = artifact_fields(payload)
        if kind != "finding.add" and "test_ref" not in fields:
            continue
        if "status" not in fields and "test_ref" not in fields:
            continue
        entries.append((event, fields))
    return entries


def check_exclusion_discipline(events: list) -> list:
    """Layer 1 check 19: nothing is excluded without a dynamic test.

    core/SUBSTRATE.md §Exclusion Discipline. From AP-008: the true root cause was
    struck off the hypothesis list on the strength of a well-argued STATIC read,
    and ~19 attempts were burned before anyone went back to it. The verifier
    cannot see how a conclusion was reached, so it enforces the one thing it can
    see -- whether anything was actually run.

    A `test_ref` resolves if it names an `evidence.capture` id present in the
    chain, or if the same event carries a well-formed `claim:` block (the
    predicate was run at authoring time). Presence anywhere in the chain is
    enough; requiring the capture to precede the exclusion would fail legitimate
    convergence-writer ordering (core/SUBSTRATE.md §Single-Writer Rule).
    """
    failures = []
    captured = captured_evidence_ids(events)

    for event, fields in hypothesis_entries(events):
        status = fields.get("status")
        if status is None:
            continue
        label = fields.get("id") or fields.get("artifact_id") or event.get("id")

        if not isinstance(status, str) or status not in HYPOTHESIS_STATUSES:
            failures.append(
                f"{label}: invalid_hypothesis_status "
                f"({event.get('id')} declares status {status!r}; expected one of "
                f"{'|'.join(HYPOTHESIS_STATUSES)})"
            )
            continue

        if status != "excluded":
            continue

        test_ref = fields.get("test_ref")
        if not isinstance(test_ref, str) or not test_ref.strip():
            failures.append(
                f"{label}: excluded_without_test_ref "
                f"({event.get('id')} marks the hypothesis excluded with no "
                f"test_ref; a static read marks it suspect, not excluded)"
            )
            continue

        cited = EVIDENCE_ID_CITE_RE.findall(test_ref)
        if cited:
            missing = [c for c in cited if c not in captured]
            if missing:
                failures.append(
                    f"{label}: excluded_test_ref_unresolved "
                    f"({event.get('id')} cites {', '.join(missing)}; no "
                    f"evidence.capture in the chain produced "
                    f"{'those ids' if len(missing) > 1 else 'that id'})"
                )
            continue

        payload = event.get("payload") or {}
        claim = payload.get("claim") if isinstance(payload, dict) else None
        if claim is not None and validate_claim_block(claim) is None:
            continue

        failures.append(
            f"{label}: excluded_without_test_ref "
            f"({event.get('id')} test_ref {test_ref!r} names neither an "
            f"evidence.capture id (ED-NNN) nor a claim: predicate on this event; "
            f"prose reasoning is not a test)"
        )

    return failures


# ---------------------------------------------------------------------------
# Execution profile (H-S12). core/SUBSTRATE.md §Execution Profile.
#
# Field evidence, measured on a one-agent engagement: `actor` was always the
# same value; the `event` vs `add` kind distinction was "mostly ceremony";
# `cite:[F-0xx#hash]` handles were "basically never consumed"; the sync-digest
# bridge was write-only and never read back for recovery. Ceremony that returns
# nothing on a one-agent run is ceremony an agent learns to fill in nominally.
#
# `profile: single-executor` drops the ceremony and nothing else. Hashes stay in
# the artifacts, the chain stays hash-linked, every Layer 1 check still runs.
# ---------------------------------------------------------------------------

PROFILES = ("multi-actor", "single-executor")
DEFAULT_PROFILE = "multi-actor"
SINGLE_EXECUTOR_DEFAULT_ACTOR = "executor"

PROFILE_VALUE_RE = re.compile(
    r"profile:\s*[\"'`]?(single-executor|multi-actor)\b", re.IGNORECASE)


def parse_schema_profile(path: Path) -> str | None:
    """Read `profile:` from a schema.yaml. The schema wins over PROJECT.md."""
    if not path.exists():
        return None
    m = PROFILE_VALUE_RE.search(path.read_text(encoding="utf-8"))
    return m.group(1).lower() if m else None


def find_project_profile(workspace: Path, project_id: str | None) -> str:
    """Resolve a project's execution profile, the way lifecycle is resolved.

    Precedence: the active schema's `schema.yaml` `profile:`, then PROJECT.md
    (a `## Profile` section's first content line, or an inline `profile:`
    declaration anywhere in the file), then the documented default
    `multi-actor`. Unknown reads as the default: a project that declares nothing
    behaves exactly as it did before v6.0.0.
    """
    if not project_id or project_id == "_harness":
        return DEFAULT_PROFILE

    schema = find_schema_for_project(workspace, project_id)
    if schema:
        schema_dir = find_schema_dir(workspace, schema)
        if schema_dir is not None:
            declared = parse_schema_profile(schema_dir / "schema.yaml")
            if declared:
                return declared

    project_md = workspace / "projects" / project_id / "PROJECT.md"
    if not project_md.exists():
        return DEFAULT_PROFILE
    text = project_md.read_text(encoding="utf-8")

    lines = text.splitlines()
    for idx, line in enumerate(lines):
        if line.strip().lower() not in ("## profile", "# profile"):
            continue
        for body in lines[idx + 1:]:
            stripped = body.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                break
            # An unsubstituted placeholder -- `{{ profile }}`, or the
            # `<multi-actor | single-executor ...>` line the shipped
            # project-template carries -- declares nothing. Reading a choice out
            # of a menu of choices is how a template becomes a decision nobody
            # made.
            if "{{" in stripped or stripped.startswith("<"):
                return DEFAULT_PROFILE
            lowered = stripped.lower()
            if "single-executor" in lowered:
                return "single-executor"
            if "multi-actor" in lowered:
                return "multi-actor"
            break
        break

    m = PROFILE_VALUE_RE.search(text)
    if m:
        return m.group(1).lower()
    return DEFAULT_PROFILE


def check_actor_requirement(workspace: Path, events: list) -> tuple:
    """`actor` is required under multi-actor and optional under single-executor.

    core/SUBSTRATE.md §Execution Profile. On the engagement that motivated this,
    `actor` carried one value for ten weeks -- a field whose every value is the
    same is a field that answers no question. Under `profile: single-executor` a
    missing `actor` reads as `executor` and is not a defect; under `multi-actor`
    (the default, so every existing project) behavior is unchanged: `actor` is
    who wrote this, and on a chain with two writers it is load-bearing.

    Returns (failures, notes). Failures join result["malformed_payloads"] --
    a missing required top-level field is the same class of defect as a missing
    payload field. The note records, once per project, that the relaxation is in
    force, so an operator reading a report can see which rules are off.
    """
    failures = []
    notes = []
    profiles = {}

    for event in events:
        project = event.get("project")
        if project not in profiles:
            profiles[project] = find_project_profile(workspace, project)
        actor = event.get("actor")
        if isinstance(actor, str) and actor.strip():
            continue
        if profiles[project] == "single-executor":
            continue
        failures.append(
            f"{event.get('id')}:{event.get('kind')} missing ['actor'] "
            f"(project {project!r} runs profile: {DEFAULT_PROFILE}; a project "
            f"with one agent may declare profile: single-executor, which "
            f"defaults actor to {SINGLE_EXECUTOR_DEFAULT_ACTOR!r})"
        )

    for project in sorted(p for p in profiles if p):
        if profiles[project] == "single-executor":
            notes.append(
                f"{project}: profile_single_executor "
                f"(actor optional, defaults to {SINGLE_EXECUTOR_DEFAULT_ACTOR}; "
                f"digest-bridge steps N/A; citations may use bare ids)"
            )
    return failures, notes


# ---------------------------------------------------------------------------
# Secrets gate (Layer 1 check 22, H-S10). core/SUBSTRATE.md §Secrets Gate.
#
# Field evidence: a sync digest copied a DSRM password and a local-admin password
# verbatim into a mailbox. The log is append-only, so the credential is now
# PERMANENT -- the only remediation was rotating it in the real world. The fix
# attempted at the time was a redaction BLOCKLIST file, which was itself a
# cleartext file aggregating live credentials: one forgotten entry from the next
# leak.
#
# The scanner is deliberately a WARNING by default. Historical chains contain
# leaked secrets and must keep verifying -- refusing to verify a chain does not
# unleak anything, and a verifier that FAILs forever on immutable history is a
# verifier operators stop running. `--strict-secrets` promotes it to FAIL for
# new-chain hygiene, where the refusal is still cheap: the event has not landed.
# ---------------------------------------------------------------------------

REDACTION_MARKER = "[REDACTED-SECRET]"

# Entropy backstop for UNLABELED blobs. Labeled secrets are the pattern rules'
# job; this catches the pasted token nobody named. Tuned against false
# positives, since a noisy warning is one operators learn to scroll past.
SECRET_ENTROPY_BITS = 4.0
SECRET_TOKEN_MIN_LEN = 20

# Values that name a secret without being one. `[REDACTED-SECRET]` is the
# protocol's own store-by-reference marker and must never trip the gate that
# asks for it.
SECRET_PLACEHOLDER_RE = re.compile(
    r"""^(?:
        \[REDACTED[^\]]*\] | <[^>]*> | \{\{.*\}\} | \$\{?[A-Za-z_][A-Za-z0-9_]*\}? |
        %[A-Za-z_][A-Za-z0-9_]*% | \*+ | x{3,} | \.{3,} | -+ |
        null | none | nil | "" | '' | changeme | redacted | omitted |
        vault:.* | keyring:.* | ref:.* | see\b.*
    )$""",
    re.IGNORECASE | re.VERBOSE,
)

SECRET_ASSIGNMENT_RE = re.compile(
    r"""(?ix)
    \b(
        dsrm[_\- ]?password | password | passwd | pwd | passphrase |
        client[_\-]?secret | secret[_\-]?key | secret |
        api[_\-]?key | apikey | access[_\-]?key | private[_\-]?key |
        auth[_\-]?token | access[_\-]?token | refresh[_\-]?token | token |
        credential | creds
    )
    \s*[:=]\s*
    (?:"([^"]*)"|'([^']*)'|(<[^>]*>)|([^\s;,"']+))
    """
)

SECRET_PEM_RE = re.compile(
    r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY(?: BLOCK)?-----"
    r"|-----BEGIN OPENSSH PRIVATE KEY-----"
    r"|PuTTY-User-Key-File-\d"
)

# scheme://user:password@host, plus the ADO.NET / ODBC keyword form.
SECRET_CONNSTR_RE = re.compile(
    r"\b[a-z][a-z0-9+.\-]*://[^\s:/@]+:[^\s:/@]+@[^\s/]+"
    r"|\b(?:server|data source|host|initial catalog|database)\s*=[^;]{1,120};"
    r"[^\n]{0,200}?\b(?:password|pwd)\s*=",
    re.IGNORECASE,
)

SECRET_BEARER_RE = re.compile(
    r"\bbearer\s+[A-Za-z0-9._\-+/=]{12,}"
    r"|\bauthorization\s*[:=]\s*[A-Za-z0-9._\-+/= ]{12,}"
    r"|\bAKIA[0-9A-Z]{16}\b"
    r"|\bgh[pousr]_[A-Za-z0-9]{16,}"
    r"|\bxox[abprs]-[A-Za-z0-9-]{10,}"
    r"|\bsk-[A-Za-z0-9]{20,}"
    r"|\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{4,}",
    re.IGNORECASE,
)

# Masked before the entropy pass: these are hashes the harness itself requires.
# Every one of them is high-entropy by construction, and every one of them is
# supposed to be there.
SECRET_HASH_MASK_RES = (
    re.compile(r"\[[A-Z]+-\d{3,}#[0-9a-f]{12}\]"),                 # citations
    re.compile(r"(?i)\bsha256:[0-9a-f]{12,64}\b"),                 # prefixed hashes
    re.compile(
        r"""(?ix)\b(?:prev_hash|content_sha256|soul_hash|sha256|hash|
            test_ref|checksum|digest|fingerprint|thumbprint|commit)
            \s*[:=]\s*"?[0-9a-f]{12,64}"?"""
    ),
)

# `/` is deliberately NOT in the token alphabet: it splits paths
# (`projects/<id>/tasks/T-001/consumed-inputs.md`) into segments too short to
# score, which is the single biggest source of entropy false positives in a
# harness whose payloads are mostly paths and ids.
SECRET_TOKEN_RE = re.compile(r"[A-Za-z0-9+=_-]{%d,}" % SECRET_TOKEN_MIN_LEN)
HEX_ONLY_RE = re.compile(r"^[0-9a-fA-F]+$")


def shannon_entropy(text: str) -> float:
    """Bits per character. Pure hex tops out at 4.0, which is why the threshold
    sits there: no hash the harness requires can reach it."""
    if not text:
        return 0.0
    counts = defaultdict(int)
    for ch in text:
        counts[ch] += 1
    total = len(text)
    bits = 0.0
    for count in counts.values():
        p = count / total
        bits -= p * math.log2(p)
    return bits


def _has_rule(hits: list, rule: str) -> bool:
    return any(hit.startswith(rule) for hit in hits)


def _is_placeholder(value: str) -> bool:
    value = (value or "").strip().strip(",;")
    if not value:
        return True
    return bool(SECRET_PLACEHOLDER_RE.match(value))


def scan_for_secrets(text) -> list:
    """Return one line per secret-shaped hit in `text`; empty list means clean.

    Five detectors, in order of how sure they are:

      1. assignment        password= / api_key: / token= with a real value
      2. private_key       PEM and OpenSSH private-key blocks
      3. connection_string scheme://user:pass@host, and Server=...;Password=
      4. bearer_token      Bearer/Authorization headers and vendor key shapes
      5. high_entropy      an unlabeled blob nobody named

    **The returned lines never contain the secret.** A verifier that echoed what
    it found would copy the credential into the report, the terminal scrollback,
    and whatever event records the run -- which is the original failure with more
    steps. Hits name the rule, the key, and a length; never the value.

    False-positive guards, in the order they matter:

      - `[REDACTED-SECRET]` and other placeholders (`<vault-ref>`, `${VAR}`,
        `null`, `see the vault`) are values that name a secret without being one.
      - Harness hashes are masked before the entropy pass: citations, `sha256:`
        prefixes, and 12-64 hex chars assigned to `hash` / `prev_hash` /
        `sha256` / `content_sha256` / `soul_hash` / `test_ref`.
      - Pure-hex tokens are skipped outright at any length, and the entropy
        threshold is 4.0 bits/char -- the ceiling for a 16-symbol alphabet, so
        no hex string can reach it even in principle.
      - An entropy candidate must mix letters with digits or base64 padding.
        `SessionHandoffTemplateProjection` scores 4.04 and is not a secret.
    """
    if not isinstance(text, str) or not text.strip():
        return []

    hits = []
    # Everything a named rule already reported is blanked out before the
    # entropy pass, so one secret produces one hit rather than two. The entropy
    # rule's job is the blob nobody labeled.
    masked = text

    def blank(match):
        nonlocal masked
        start, end = match.span()
        masked = masked[:start] + " " * (end - start) + masked[end:]

    for match in SECRET_ASSIGNMENT_RE.finditer(text):
        key = match.group(1)
        value = next((g for g in match.groups()[1:] if g is not None), "")
        if _is_placeholder(value):
            continue
        blank(match)
        hits.append(
            f"assignment ({key.lower()}= with a {len(value.strip())}-char value; "
            f"store by reference and write {REDACTION_MARKER})"
        )

    for match in SECRET_PEM_RE.finditer(text):
        blank(match)
        if not _has_rule(hits, "private_key"):
            hits.append("private_key (a PEM / OpenSSH private-key block)")

    for match in SECRET_CONNSTR_RE.finditer(text):
        blank(match)
        if not _has_rule(hits, "connection_string"):
            hits.append(
                "connection_string (credentials embedded in a connection string)")

    for match in SECRET_BEARER_RE.finditer(text):
        blank(match)
        if not _has_rule(hits, "bearer_token"):
            hits.append(
                "bearer_token (a bearer/authorization header or vendor key shape)")

    for pattern in SECRET_HASH_MASK_RES:
        masked = pattern.sub(" ", masked)

    for token in SECRET_TOKEN_RE.findall(masked):
        if HEX_ONLY_RE.match(token):
            continue
        has_alpha = any(c.isalpha() for c in token)
        has_digit = any(c.isdigit() for c in token)
        has_b64 = any(c in "+=" for c in token)
        if not (has_alpha and (has_digit or has_b64)):
            continue
        entropy = shannon_entropy(token)
        if entropy < SECRET_ENTROPY_BITS:
            continue
        hits.append(
            f"high_entropy ({len(token)} chars at {entropy:.2f} bits/char; "
            f"unlabeled high-entropy token)"
        )

    return hits


def _walk_payload_strings(obj, path="") -> list:
    """(json-ish path, string) for every string anywhere in a payload."""
    out = []
    if isinstance(obj, str):
        out.append((path or "payload", obj))
    elif isinstance(obj, dict):
        for key, value in obj.items():
            out.extend(_walk_payload_strings(value, f"{path}.{key}" if path else str(key)))
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            out.extend(_walk_payload_strings(item, f"{path}[{idx}]"))
    return out


def check_secrets(events: list) -> list:
    """Layer 1 check 22: `possible_secret_in_event`.

    core/SUBSTRATE.md §Secrets Gate. Scans every string in every payload. A hit
    is a WARNING by default and a FAIL under `--strict-secrets`; see the module
    header on why history must keep verifying.

    The real enforcement point is `hw add`, which runs the same scan BEFORE the
    append and refuses. This check is the after-the-fact half: it tells an
    operator which events to rotate against, on a chain where deletion is not
    available.
    """
    warnings = []
    for event in events:
        payload = event.get("payload")
        if payload is None:
            continue
        for field_path, text in _walk_payload_strings(payload):
            for hit in scan_for_secrets(text):
                warnings.append(
                    f"{event.get('id')}:{event.get('kind')} possible_secret_in_event "
                    f"(payload.{field_path}: {hit})"
                )
    return warnings


# Legal `workstream.status` transitions, from the program schema's
# artifact-extensions.yaml. A status that does not change (X -> X) is also legal:
# the schema's own T-004 refreshes `last_rollup_citation` by re-adding the
# workstream artifact, which is a metadata write, not a status change.
LEGAL_WORKSTREAM_TRANSITIONS = {
    ("active", "parked"), ("parked", "active"),
    ("active", "promoted"), ("active", "retired"), ("active", "done"),
    ("parked", "retired"), ("promoted", "retired"),
}


def iter_top_level_yaml_blocks(text: str):
    """Yield (block_name, block_body) for each top-level key in a YAML file.

    Comment lines are dropped so a commented-out declaration is not read as a
    live one. Dependency-free by design, matching parse_capability_gates_yaml.
    """
    name = None
    body = []
    for line in text.splitlines():
        if line.strip().startswith("#"):
            continue
        header = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if header and not line.startswith((" ", "\t")):
            if name is not None:
                yield name, "\n".join(body)
            name, body = header.group(1), []
            continue
        if name is not None:
            body.append(line)
    if name is not None:
        yield name, "\n".join(body)


def parse_capability_gates_declared_checks(path: Path) -> set:
    """Layer 1 check names a schema's capability-gates.yaml declares and enforces.

    The convention the `program` pack established: a block declaring a custom
    Layer 1 check carries `layer1_check_name: <name>` and `enforce: true` (e.g.
    `spawn_pause:`, `registry_consistency:`, `rollup_citation:`). Reading the
    declaration rather than hardcoding a schema name keeps the machinery
    schema-agnostic per CONTRIBUTING.md §4: any schema that declares one of the
    implemented checks gets it.
    """
    if not path.exists():
        return set()
    declared = set()
    for _name, body in iter_top_level_yaml_blocks(path.read_text(encoding="utf-8")):
        check = re.search(r"^\s+layer1_check_name:\s*([A-Za-z0-9_.-]+)\s*$",
                          body, re.MULTILINE)
        if not check:
            continue
        enforce = re.search(r"^\s+enforce:\s*(\S+)\s*$", body, re.MULTILINE)
        if enforce and enforce.group(1).strip('"').strip("'").lower() in (
                "false", "no", "off"):
            continue
        declared.add(check.group(1))
    return declared


def artifact_fields(payload: dict) -> dict:
    """Flatten a typed-artifact `.add` payload to its field map.

    The documented shape is flat (`{artifact_id, fields...}`, core/SUBSTRATE.md
    §Typed-artifact events); a `frontmatter:` / `fields:` nesting is tolerated
    because task.create already uses `frontmatter`. Top-level keys win.
    """
    fields = {}
    for key in ("frontmatter", "fields", "artifact"):
        nested = payload.get(key)
        if isinstance(nested, dict):
            fields.update(nested)
    for key, value in payload.items():
        if key in ("frontmatter", "fields", "artifact"):
            continue
        fields[key] = value
    return fields


def reverses_list(value) -> list:
    """`reverses:` accepts a single ID or a list (v5.3). Normalize to a list."""
    if not value:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [v for v in value if isinstance(v, str) and v]
    return []


def collect_workstream_artifacts(project_events: list) -> tuple:
    """Fold `workstream.add` events into per-artifact state.

    One artifact may be written more than once: a status change is a NEW
    artifact carrying `reverses:`, but a `last_rollup_citation` refresh re-adds
    the SAME artifact id with `reverses:` unset (program schema T-004 step 5).
    So state is merged forward per id, and every add is kept in order so the
    roll-up check can tell the current citation from a prior cycle's.

    Returns (artifacts, superseded, issues) where artifacts maps
    ws_id -> {fields, adds, order} and superseded is the set of ws_ids some
    other artifact reverses (or that declare their own `superseded_by`).
    """
    artifacts = {}
    issues = []
    order = 0
    for event in project_events:
        if event.get("kind") != "workstream.add":
            continue
        fields = artifact_fields(event.get("payload") or {})
        ws_id = fields.get("artifact_id") or fields.get("id")
        if not ws_id:
            issues.append(
                f"{event.get('id')} workstream.add carries no artifact_id"
            )
            continue
        entry = artifacts.get(ws_id)
        if entry is None:
            artifacts[ws_id] = {"fields": dict(fields), "adds": [(event, fields)],
                                 "order": order}
            order += 1
        else:
            entry["fields"].update(fields)
            entry["adds"].append((event, fields))

    superseded = set()
    for ws_id, entry in artifacts.items():
        for old_id in reverses_list(entry["fields"].get("reverses")):
            superseded.add(old_id)
        if entry["fields"].get("superseded_by"):
            superseded.add(ws_id)

    return artifacts, superseded, issues


def check_spawn_pause(project_id: str, project_events: list) -> list:
    """Program Layer 1 check `spawn_pause_skipped`.

    From schemas/projects/program/capability-gates.yaml: a workstream artifact
    with `origin: spawned` must be preceded, in order, by
    `workstream.spawn_proposed` and a `workstream.spawn_decided` with
    `decision: approved` and `operator_confirmed: true`. A declined proposal must
    never be followed by a registration. `origin: existing-registered`
    workstreams are exempt - they describe instances that predate the program.

    Only the event that FIRST registers a workstream is gated: a later add for
    the same id (citation refresh) or an add carrying `reverses:` (a status
    supersede of an already-approved workstream) is not a new spawn.

    Ambiguity resolved: the workstream artifact schema has no `proposal_id`
    field, so the YAML's "matching proposal_id" cannot always be read off the
    registration. When the add carries one, it is matched exactly. When it does
    not, the check consumes the earliest approved-and-confirmed proposal that
    precedes the registration and is not already spoken for - one pause per
    spawned workstream, which is the property the gate exists to enforce.
    """
    failures = []

    proposals = {}
    decisions = {}
    for idx, event in enumerate(project_events):
        kind = event.get("kind")
        payload = event.get("payload") or {}
        proposal_id = payload.get("proposal_id")
        if not proposal_id:
            continue
        if kind == "workstream.spawn_proposed":
            proposals.setdefault(proposal_id, (idx, event))
        elif kind == "workstream.spawn_decided":
            decisions[proposal_id] = (idx, event)

    declined = {pid for pid, (_i, ev) in decisions.items()
                if (ev.get("payload") or {}).get("decision") == "declined"}

    approved = sorted(
        (idx, pid)
        for pid, (idx, ev) in decisions.items()
        if (ev.get("payload") or {}).get("decision") == "approved"
        and (ev.get("payload") or {}).get("operator_confirmed") is True
        and pid in proposals and proposals[pid][0] < idx
    )

    consumed = set()
    seen_artifacts = set()

    for idx, event in enumerate(project_events):
        if event.get("kind") != "workstream.add":
            continue
        fields = artifact_fields(event.get("payload") or {})
        ws_id = fields.get("artifact_id") or fields.get("id")
        proposal_id = fields.get("proposal_id")

        if proposal_id and proposal_id in declined:
            failures.append(
                f"{project_id}: spawn_pause_skipped "
                f"({event.get('id')} registers {ws_id or '<no id>'} for "
                f"proposal {proposal_id}, which the operator DECLINED at "
                f"{decisions[proposal_id][1].get('id')})"
            )
            continue

        first_registration = bool(ws_id) and ws_id not in seen_artifacts
        if ws_id:
            seen_artifacts.add(ws_id)
        if reverses_list(fields.get("reverses")) or not first_registration:
            continue
        if str(fields.get("origin") or "").strip().lower() != "spawned":
            continue

        if proposal_id:
            proposal = proposals.get(proposal_id)
            decision = decisions.get(proposal_id)
            if proposal is None or proposal[0] >= idx:
                failures.append(
                    f"{project_id}: spawn_pause_skipped "
                    f"({event.get('id')} registers spawned workstream "
                    f"{ws_id} for proposal {proposal_id}; no preceding "
                    f"workstream.spawn_proposed for that proposal_id)"
                )
                continue
            if decision is None or decision[0] >= idx:
                failures.append(
                    f"{project_id}: spawn_pause_skipped "
                    f"({event.get('id')} registers spawned workstream "
                    f"{ws_id} for proposal {proposal_id}; no preceding "
                    f"workstream.spawn_decided - the agent did not wait for the "
                    f"operator)"
                )
                continue
            decision_payload = decision[1].get("payload") or {}
            if (decision_payload.get("decision") != "approved"
                    or decision_payload.get("operator_confirmed") is not True):
                failures.append(
                    f"{project_id}: spawn_pause_skipped "
                    f"({event.get('id')} registers spawned workstream {ws_id}; "
                    f"{decision[1].get('id')} is decision="
                    f"{decision_payload.get('decision')!r} operator_confirmed="
                    f"{decision_payload.get('operator_confirmed')!r} - approval "
                    f"must be both)"
                )
                continue
            consumed.add(proposal_id)
            continue

        match = next((pid for pos, pid in approved
                      if pos < idx and pid not in consumed), None)
        if match is None:
            failures.append(
                f"{project_id}: spawn_pause_skipped "
                f"({event.get('id')} registers spawned workstream "
                f"{ws_id}; no unconsumed workstream.spawn_proposed + "
                f"workstream.spawn_decided(approved, operator_confirmed: true) "
                f"pair precedes it)"
            )
            continue
        consumed.add(match)

    return failures


def check_registry_supersede_chain(project_id: str, project_events: list) -> list:
    """Program Layer 1 check `registry_status_vs_supersede_chain`.

    From schemas/projects/program/capability-gates.yaml: for every
    `child_project_id`, exactly one workstream artifact - the one with no
    `superseded_by` - is current, and its status must be reachable from its
    direct predecessor's status by a legal transition.

    Ambiguity resolved: the schema's own T-004 refreshes `last_rollup_citation`
    by re-adding a workstream artifact without changing its status, so an
    unchanged status (X -> X) is treated as legal. Reading the transition table
    strictly would FAIL every roll-up cycle the schema itself prescribes.
    """
    artifacts, superseded, issues = collect_workstream_artifacts(project_events)
    failures = [f"{project_id}: registry_status_vs_supersede_chain ({issue})"
                for issue in issues]

    for ws_id, entry in sorted(artifacts.items(), key=lambda kv: kv[1]["order"]):
        for old_id in reverses_list(entry["fields"].get("reverses")):
            predecessor = artifacts.get(old_id)
            if predecessor is None:
                failures.append(
                    f"{project_id}: registry_status_vs_supersede_chain "
                    f"({ws_id} reverses {old_id}, which has no workstream.add "
                    f"event in this chain)"
                )
                continue
            was = str(predecessor["fields"].get("status") or "").strip().lower()
            now = str(entry["fields"].get("status") or "").strip().lower()
            if not was or not now or was == now:
                continue
            if (was, now) not in LEGAL_WORKSTREAM_TRANSITIONS:
                failures.append(
                    f"{project_id}: registry_status_vs_supersede_chain "
                    f"({ws_id} supersedes {old_id} with status {was} -> {now}; "
                    f"not a legal workstream.status transition)"
                )

    by_child = defaultdict(list)
    for ws_id, entry in artifacts.items():
        child = entry["fields"].get("child_project_id")
        if not child or ws_id in superseded:
            continue
        by_child[child].append(ws_id)

    for child, ws_ids in sorted(by_child.items()):
        if len(ws_ids) > 1:
            failures.append(
                f"{project_id}: registry_status_vs_supersede_chain "
                f"(child_project_id {child!r} has {len(ws_ids)} current "
                f"workstream artifacts {sorted(ws_ids)}; exactly one artifact "
                f"with no superseded_by is current, and its status is the "
                f"registry's answer)"
            )

    return failures


def check_rollup_citations(workspace: Path, project_id: str,
                            project_events: list) -> tuple:
    """Program Layer 1 check `rollup_citation_stale_or_broken`.

    The YAML declares two severities and this check honors both. At write time
    the cited path must resolve and its recorded sha256 must match the file's
    actual bytes - a hard FAIL, since the program agent had just read the file.
    At each subsequent roll-up cycle the prior cycle's citation is re-checked
    non-blocking: a path that no longer resolves is a WARNING (the sibling
    instance moved), a differing hash is expected and informational (the sibling
    moved on, which is what "staleness checkable" means), and a hash that still
    matches means the workstream has written nothing since - noted as an
    overdue_workstreams candidate when that workstream is itself
    `lifecycle: ongoing`.

    Ambiguity resolved: a verifier runs after the fact and cannot observe write
    time directly. The write-time citation is taken to be the one on the latest
    add of a current (non-superseded) artifact - the citation this chain is
    asserting right now. Every earlier citation is a prior cycle's.

    Returns (failures, warnings).
    """
    failures = []
    warnings = []
    artifacts, superseded, _issues = collect_workstream_artifacts(project_events)

    for ws_id, entry in sorted(artifacts.items(), key=lambda kv: kv[1]["order"]):
        adds = entry["adds"]
        is_current = ws_id not in superseded
        lifecycle = str(entry["fields"].get("lifecycle") or "").strip().lower()

        for position, (event, fields) in enumerate(adds):
            citation = fields.get("last_rollup_citation")
            if not isinstance(citation, dict):
                continue
            path = citation.get("path")
            recorded = citation.get("sha256")
            if not path or not recorded:
                continue
            write_time = is_current and position == len(adds) - 1
            cycle_id = citation.get("cycle_id") or "<no cycle_id>"
            target = workspace / str(path)

            if not target.is_file():
                if write_time:
                    failures.append(
                        f"{project_id}: rollup_citation_stale_or_broken "
                        f"({ws_id} at {event.get('id')} cites {path!r}, which "
                        f"does not resolve from the workspace root)"
                    )
                else:
                    warnings.append(
                        f"{project_id}: rollup_citation_broken "
                        f"({ws_id} cycle {cycle_id} cited {path!r}, which no "
                        f"longer resolves; the sibling instance's projection "
                        f"moved or its instance path changed - non-blocking)"
                    )
                continue

            recorded_bare = normalize_recorded_hash(str(recorded)).strip().lower()
            if len(recorded_bare) < 12:
                if write_time:
                    failures.append(
                        f"{project_id}: rollup_citation_stale_or_broken "
                        f"({ws_id} at {event.get('id')} cites {path!r} with "
                        f"sha256 {recorded!r}; expected at least the 12-hex "
                        f"short form)"
                    )
                continue

            actual = sha256_hex(target.read_bytes())
            matches = actual.startswith(recorded_bare)

            if write_time and not matches:
                failures.append(
                    f"{project_id}: rollup_citation_stale_or_broken "
                    f"({ws_id} at {event.get('id')} cites {path!r} at sha256 "
                    f"{recorded_bare[:12]}; the file now hashes to "
                    f"{actual[:12]})"
                )
            elif not write_time and matches and lifecycle == "ongoing":
                warnings.append(
                    f"{project_id}: rollup_citation_unchanged "
                    f"({ws_id} cycle {cycle_id} cited {path!r} and it still "
                    f"hashes to {actual[:12]}; the workstream has written no "
                    f"new projection since - overdue_workstreams candidate)"
                )

    return failures, warnings


def check_schema_declared_layer1(workspace: Path, events: list) -> tuple:
    """Run the custom Layer 1 checks a project's schema declares and enforces.

    The `program` schema declared three checks in capability-gates.yaml prose
    and shipped none of them as code. They run here for any project whose active
    schema declares them, keyed on the declaration rather than on the schema
    name (CONTRIBUTING.md §4: core machinery, schema-configured trigger).

    Returns (failures, warnings).
    """
    failures = []
    warnings = []

    by_project = defaultdict(list)
    for event in events:
        by_project[event.get("project")].append(event)

    for project_id, project_events in by_project.items():
        if not project_id or project_id == "_harness":
            continue
        schema = find_schema_for_project(workspace, project_id)
        if not schema:
            continue
        schema_dir = find_schema_dir(workspace, schema)
        if schema_dir is None:
            continue
        declared = parse_capability_gates_declared_checks(
            schema_dir / "capability-gates.yaml")
        if not declared:
            continue

        if "spawn_pause_skipped" in declared:
            failures.extend(check_spawn_pause(project_id, project_events))
        if "registry_status_vs_supersede_chain" in declared:
            failures.extend(
                check_registry_supersede_chain(project_id, project_events))
        if "rollup_citation_stale_or_broken" in declared:
            rollup_failures, rollup_warnings = check_rollup_citations(
                workspace, project_id, project_events)
            failures.extend(rollup_failures)
            warnings.extend(rollup_warnings)

    return failures, warnings


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


def verify(workspace: Path, since: str | None, strict_secrets: bool = False) -> dict:
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
        "schema_check_failures": [],
        "schema_check_warnings": [],
        "scope_completeness_failures": [],
        "external_state_readback_failures": [],
        "external_state_readback_warnings": [],
        "bootstrap_probe_failures": [],
        "checked_claims_malformed": [],
        "checked_claims_required_failures": [],
        "exclusion_failures": [],
        "evidence_capture_failures": [],
        "open_loop_failures": [],
        "open_loop_notes": [],
        "secret_warnings": [],
        "strict_secrets": strict_secrets,
        "profile_notes": [],
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
    schema_failures, schema_warnings = check_schema_declared_layer1(workspace, events)
    result["schema_check_failures"] = schema_failures
    result["schema_check_warnings"] = schema_warnings
    result["scope_completeness_failures"] = check_scope_completeness(workspace, events)
    esrb_failures, esrb_warnings = check_external_state_readback(workspace, events)
    result["external_state_readback_failures"] = esrb_failures
    result["external_state_readback_warnings"] = esrb_warnings
    result["bootstrap_probe_failures"] = check_bootstrap_probe(events)
    result["checked_claims_malformed"] = check_claims_structural(events)
    result["checked_claims_required_failures"] = check_claims_required(workspace, events)
    result["exclusion_failures"] = check_exclusion_discipline(events)
    result["evidence_capture_failures"] = check_evidence_capture(events)
    result["malformed_payloads"].extend(check_note_payloads(events))
    loop_failures, loop_notes = check_open_loops(events)
    result["open_loop_failures"] = loop_failures
    result["open_loop_notes"] = loop_notes
    result["secret_warnings"] = check_secrets(events)
    actor_failures, profile_notes = check_actor_requirement(workspace, events)
    result["malformed_payloads"].extend(actor_failures)
    result["profile_notes"] = profile_notes

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
        or result["schema_check_failures"]
        or result["scope_completeness_failures"]
        or result["external_state_readback_failures"]
        or result["bootstrap_probe_failures"]
        or result["checked_claims_malformed"]
        or result["checked_claims_required_failures"]
        or result["exclusion_failures"]
        or result["evidence_capture_failures"]
        or result["open_loop_failures"]
        # Check 22 is a WARNING by default: a historical chain that leaked a
        # credential must still verify, because refusing to verify it unleaks
        # nothing. --strict-secrets promotes it for new-chain hygiene.
        or (strict_secrets and result["secret_warnings"])
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
        f"  schema_checks:         {len(result['schema_check_failures'])} {result['schema_check_failures']}",
        f"  schema_check_warnings: {len(result['schema_check_warnings'])} {result['schema_check_warnings']}",
        f"  scope_completeness:    {len(result['scope_completeness_failures'])} {result['scope_completeness_failures']}",
        f"  ext_state_readback:    {len(result['external_state_readback_failures'])} {result['external_state_readback_failures']}",
        f"  ext_state_warnings:    {len(result['external_state_readback_warnings'])} {result['external_state_readback_warnings']}",
        f"  bootstrap_probe:       {len(result['bootstrap_probe_failures'])} {result['bootstrap_probe_failures']}",
        f"  checked_claims:        {len(result['checked_claims_malformed'])} {result['checked_claims_malformed']}",
        f"  checked_claims_req:    {len(result['checked_claims_required_failures'])} {result['checked_claims_required_failures']}",
        f"  exclusion_discipline:  {len(result['exclusion_failures'])} {result['exclusion_failures']}",
        f"  evidence_capture:      {len(result['evidence_capture_failures'])} {result['evidence_capture_failures']}",
        f"  open_loops:            {len(result['open_loop_failures'])} {result['open_loop_failures']}",
        f"  open_loop_notes:       {len(result['open_loop_notes'])} {result['open_loop_notes']}",
        f"  profile_notes:         {len(result['profile_notes'])} {result['profile_notes']}",
        f"  possible_secrets:      {len(result['secret_warnings'])}"
        f"{' (FAIL: --strict-secrets)' if result.get('strict_secrets') and result['secret_warnings'] else ''}"
        f" {result['secret_warnings']}",
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
    parser.add_argument("--strict-secrets", action="store_true",
                        help="Promote Layer 1 check 22 (possible_secret_in_event) from "
                             "WARNING to FAIL. Off by default so historical chains that "
                             "already carry a leaked credential keep verifying; on for "
                             "new-chain hygiene (core/SUBSTRATE.md §Secrets Gate).")
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

    result = verify(workspace, args.since, strict_secrets=args.strict_secrets)
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
