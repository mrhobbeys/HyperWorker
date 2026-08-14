#!/usr/bin/env python3
"""
test_program_checks.py — regression test for the v6.0.0 schema-declared Layer 1
checks in tools/hw-verify.py (core/VERIFICATION.md §Layer 1 check 18,
schemas/projects/program/capability-gates.yaml).

The `program` schema declares three custom Layer 1 checks - `spawn_pause_skipped`,
`registry_status_vs_supersede_chain`, `rollup_citation_stale_or_broken` - each
with a `rule: |` paragraph and `enforce: true`. All three existed only as YAML
prose. capability-gates.yaml even says it: "A capability gate that does not
produce a structural failure when violated is documentation, not enforcement"
(CONTRIBUTING.md §6.7).

Covers:
  - the declaration gate: checks run only for a schema that declares them
  - spawn_pause_skipped: approved pause, missing proposal, missing decision,
    unapproved / unconfirmed decision, declined-then-registered, ordering,
    existing-registered exemption, status supersedes and citation refreshes not
    re-gated, and the no-proposal_id fallback pairing
  - registry_status_vs_supersede_chain: legal and illegal transitions, unchanged
    status on a citation refresh, two current artifacts for one child_project_id,
    a reverses pointing at nothing, adds with no artifact id
  - rollup_citation_stale_or_broken: write-time hard FAIL on broken path and on
    hash mismatch, prior-cycle broken path as WARNING, prior-cycle hash drift as
    neither, prior-cycle unchanged hash as an overdue candidate for ongoing
    workstreams, short and full hex forms

Stdlib only; no pytest dependency, mirroring tools/test_checked_claims.py's
harness pattern (importlib-loads hw-verify.py).

Usage:  python tools/test_program_checks.py
Exits 0 if all cases pass, 1 otherwise.
"""

import hashlib
import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
HW_VERIFY_PATH = HERE / "hw-verify.py"

spec = importlib.util.spec_from_file_location("hw_verify", HW_VERIFY_PATH)
hw_verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hw_verify)

check_spawn_pause = hw_verify.check_spawn_pause
check_registry_supersede_chain = hw_verify.check_registry_supersede_chain
check_rollup_citations = hw_verify.check_rollup_citations
check_schema_declared_layer1 = hw_verify.check_schema_declared_layer1
parse_capability_gates_declared_checks = hw_verify.parse_capability_gates_declared_checks

PROJECT = "demo-program"
SCHEMA = "program"

_next_id = [0]


def reset_ids():
    _next_id[0] = 0


def ev(kind: str, payload: dict | None = None, project: str = PROJECT) -> dict:
    _next_id[0] += 1
    return {"id": f"EV-{_next_id[0]:04d}", "actor": "planner", "project": project,
            "kind": kind, "payload": dict(payload or {})}


def proposed(proposal_id: str = "P-1", trigger: str = "spawn") -> dict:
    return ev("workstream.spawn_proposed",
              {"proposal_id": proposal_id, "trigger": trigger, "slug": "slug",
               "premise": "a premise", "schema_choice": "site-seo",
               "promoted_from": None, "proposed_by": "planner"})


def decided(proposal_id: str = "P-1", decision: str = "approved",
            operator_confirmed: bool = True) -> dict:
    return ev("workstream.spawn_decided",
              {"proposal_id": proposal_id, "decision": decision,
               "decision_artifact": "[DEC-001#abcdefabcdef]",
               "operator_confirmed": operator_confirmed})


def workstream(ws_id: str, child: str = "child-a", origin: str = "spawned",
               status: str = "active", reverses=None, proposal_id=None,
               lifecycle: str = "terminal", citation=None) -> dict:
    payload = {
        "artifact_id": ws_id,
        "child_project_id": child,
        "name": f"workstream {ws_id}",
        "origin": origin,
        "instance_path": f"../{child}",
        "bootstrapped_from_schema": "site-seo",
        "lifecycle": lifecycle,
        "status": status,
        "reverses": reverses,
        "last_rollup_citation": citation,
    }
    if proposal_id is not None:
        payload["proposal_id"] = proposal_id
    return ev("workstream.add", payload)


def citation(path: str, digest: str, cycle_id: str = "C-001") -> dict:
    return {"path": path, "sha256": digest, "cycle_id": cycle_id,
            "checked_at": "2026-08-01T00:00:00Z"}


def write_sibling_projection(tmp: Path, relative: str, body: str) -> str:
    """Write a sibling-instance projection and return its full sha256 hex."""
    target = tmp / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    data = body.encode("utf-8")
    target.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def write_program_schema(tmp: Path, schema: str = SCHEMA, enforce: bool = True,
                          project: str = PROJECT):
    """Write the PROJECT.md + capability-gates.yaml pair the gate reads."""
    proj_dir = tmp / "projects" / project
    proj_dir.mkdir(parents=True, exist_ok=True)
    (proj_dir / "PROJECT.md").write_text(
        f"# PROJECT - {project}\n\nBootstrapped from `schemas/projects/{schema}/`.\n",
        encoding="utf-8")
    schema_dir = tmp / "schemas" / "projects" / schema
    schema_dir.mkdir(parents=True, exist_ok=True)
    flag = "true" if enforce else "false"
    (schema_dir / "capability-gates.yaml").write_text(
        "# fixture capability gates\n"
        "not_required:\n  - shell_exec\n\n"
        "spawn_pause:\n"
        f"  enforce: {flag}\n"
        "  layer1_check_name: spawn_pause_skipped\n"
        "  rule: |\n    prose\n\n"
        "registry_consistency:\n"
        f"  enforce: {flag}\n"
        "  layer1_check_name: registry_status_vs_supersede_chain\n"
        "  rule: |\n    prose\n\n"
        "rollup_citation:\n"
        f"  enforce: {flag}\n"
        "  layer1_check_name: rollup_citation_stale_or_broken\n"
        "  rule: |\n    prose\n",
        encoding="utf-8")


def expect_clean(failures) -> tuple:
    return (failures == [], f"expected no failures, got {failures}")


def expect_failures(failures, count: int, tokens=()) -> tuple:
    if len(failures) != count:
        return (False, f"expected {count} failure(s), got {failures}")
    blob = " | ".join(failures)
    missing = [t for t in tokens if t not in blob]
    if missing:
        return (False, f"report missing {missing}: {blob}")
    return (True, "")


CASES = []


def case(name):
    def register(fn):
        CASES.append((name, fn))
        return fn
    return register


# ---------------------------------------------------------------------------
# The declaration gate
# ---------------------------------------------------------------------------

@case("declared checks are read from capability-gates.yaml, enforce respected")
def _(tmp):
    write_program_schema(tmp, enforce=True)
    on = parse_capability_gates_declared_checks(
        tmp / "schemas" / "projects" / SCHEMA / "capability-gates.yaml")
    write_program_schema(tmp, schema="off-schema", enforce=False)
    off = parse_capability_gates_declared_checks(
        tmp / "schemas" / "projects" / "off-schema" / "capability-gates.yaml")
    expected = {"spawn_pause_skipped", "registry_status_vs_supersede_chain",
                "rollup_citation_stale_or_broken"}
    return (on == expected and off == set(),
            f"enforced={on} unenforced={off}")


@case("the shipped program pack declares all three checks")
def _(tmp):
    repo_root = HERE.parent
    declared = parse_capability_gates_declared_checks(
        repo_root / "schemas" / "projects" / "program" / "capability-gates.yaml")
    expected = {"spawn_pause_skipped", "registry_status_vs_supersede_chain",
                "rollup_citation_stale_or_broken"}
    return (declared == expected, f"program pack declares {declared}")


@case("a schema that declares nothing runs no schema checks")
def _(tmp):
    reset_ids()
    proj_dir = tmp / "projects" / PROJECT
    proj_dir.mkdir(parents=True, exist_ok=True)
    (proj_dir / "PROJECT.md").write_text(
        "# PROJECT\n\nBootstrapped from `schemas/projects/report-synthesis/`.\n",
        encoding="utf-8")
    schema_dir = tmp / "schemas" / "projects" / "report-synthesis"
    schema_dir.mkdir(parents=True, exist_ok=True)
    (schema_dir / "capability-gates.yaml").write_text(
        "not_required:\n  - shell_exec\n", encoding="utf-8")
    # A spawned workstream with no pause at all: would FAIL under the program pack.
    failures, warnings = check_schema_declared_layer1(tmp, [workstream("WS-001")])
    return (failures == [] and warnings == [],
            f"expected the undeclared schema to opt out, got {failures} {warnings}")


@case("a schema that declares the checks runs them end to end")
def _(tmp):
    reset_ids()
    write_program_schema(tmp)
    failures, _warnings = check_schema_declared_layer1(tmp, [workstream("WS-001")])
    return expect_failures(failures, 1, ["spawn_pause_skipped"])


@case("enforce: false disables the declared checks")
def _(tmp):
    reset_ids()
    write_program_schema(tmp, enforce=False)
    failures, warnings = check_schema_declared_layer1(tmp, [workstream("WS-001")])
    return (failures == [] and warnings == [],
            f"expected enforce: false to opt out, got {failures} {warnings}")


# ---------------------------------------------------------------------------
# spawn_pause_skipped
# ---------------------------------------------------------------------------

@case("proposed -> decided(approved, confirmed) -> registered -> no failures")
def _(tmp):
    reset_ids()
    events = [proposed("P-1"), decided("P-1"), workstream("WS-001", proposal_id="P-1")]
    return expect_clean(check_spawn_pause(PROJECT, events))


@case("registration with no proposal and no decision -> spawn_pause_skipped")
def _(tmp):
    reset_ids()
    return expect_failures(check_spawn_pause(PROJECT, [workstream("WS-001")]), 1,
                           ["spawn_pause_skipped", "WS-001"])


@case("proposed but never decided -> spawn_pause_skipped (the agent did not wait)")
def _(tmp):
    reset_ids()
    events = [proposed("P-1"), workstream("WS-001", proposal_id="P-1")]
    return expect_failures(check_spawn_pause(PROJECT, events), 1,
                           ["spawn_pause_skipped", "did not wait"])


@case("decided without a preceding proposal -> spawn_pause_skipped")
def _(tmp):
    reset_ids()
    events = [decided("P-1"), workstream("WS-001", proposal_id="P-1")]
    return expect_failures(check_spawn_pause(PROJECT, events), 1,
                           ["spawn_pause_skipped", "spawn_proposed"])


@case("decision with operator_confirmed: false -> spawn_pause_skipped")
def _(tmp):
    reset_ids()
    events = [proposed("P-1"), decided("P-1", operator_confirmed=False),
              workstream("WS-001", proposal_id="P-1")]
    return expect_failures(check_spawn_pause(PROJECT, events), 1,
                           ["spawn_pause_skipped", "operator_confirmed"])


@case("declined proposal followed by a registration -> spawn_pause_skipped")
def _(tmp):
    reset_ids()
    events = [proposed("P-1"), decided("P-1", decision="declined"),
              workstream("WS-001", proposal_id="P-1")]
    return expect_failures(check_spawn_pause(PROJECT, events), 1,
                           ["spawn_pause_skipped", "DECLINED"])


@case("declined proposal registered as existing-registered is still caught")
def _(tmp):
    reset_ids()
    events = [proposed("P-1"), decided("P-1", decision="declined"),
              workstream("WS-001", origin="existing-registered", proposal_id="P-1")]
    return expect_failures(check_spawn_pause(PROJECT, events), 1, ["DECLINED"])


@case("pause events arriving AFTER the registration do not excuse it")
def _(tmp):
    reset_ids()
    events = [workstream("WS-001", proposal_id="P-1"), proposed("P-1"), decided("P-1")]
    return expect_failures(check_spawn_pause(PROJECT, events), 1,
                           ["spawn_pause_skipped"])


@case("origin: existing-registered is exempt (the instance predates the program)")
def _(tmp):
    reset_ids()
    events = [workstream("WS-001", origin="existing-registered"),
              workstream("WS-002", child="child-b", origin="existing-registered")]
    return expect_clean(check_spawn_pause(PROJECT, events))


@case("a status supersede of an approved workstream is not re-gated")
def _(tmp):
    reset_ids()
    events = [
        proposed("P-1"), decided("P-1"),
        workstream("WS-001", proposal_id="P-1"),
        workstream("WS-002", status="parked", reverses="WS-001"),
    ]
    return expect_clean(check_spawn_pause(PROJECT, events))


@case("a citation refresh (same WS id re-added) is not re-gated")
def _(tmp):
    reset_ids()
    events = [
        proposed("P-1"), decided("P-1"),
        workstream("WS-001", proposal_id="P-1"),
        workstream("WS-001", proposal_id="P-1",
                    citation=citation("../child-a/SESSION-HANDOFF.md", "a" * 64)),
    ]
    return expect_clean(check_spawn_pause(PROJECT, events))


@case("no proposal_id on the registration: an unconsumed approved pair satisfies it")
def _(tmp):
    reset_ids()
    events = [proposed("P-1"), decided("P-1"), workstream("WS-001")]
    return expect_clean(check_spawn_pause(PROJECT, events))


@case("no proposal_id: one approved pair cannot cover two spawned workstreams")
def _(tmp):
    reset_ids()
    events = [proposed("P-1"), decided("P-1"),
              workstream("WS-001", child="child-a"),
              workstream("WS-002", child="child-b")]
    return expect_failures(check_spawn_pause(PROJECT, events), 1,
                           ["spawn_pause_skipped", "WS-002"])


@case("two proposals, two approvals, two spawned workstreams -> no failures")
def _(tmp):
    reset_ids()
    events = [proposed("P-1"), decided("P-1"), proposed("P-2"), decided("P-2"),
              workstream("WS-001", child="child-a"),
              workstream("WS-002", child="child-b")]
    return expect_clean(check_spawn_pause(PROJECT, events))


@case("promote-flavored spawn follows the identical protocol -> no failures")
def _(tmp):
    reset_ids()
    events = [proposed("P-9", trigger="promote"), decided("P-9"),
              workstream("WS-003", child="hot-item", proposal_id="P-9")]
    return expect_clean(check_spawn_pause(PROJECT, events))


# ---------------------------------------------------------------------------
# registry_status_vs_supersede_chain
# ---------------------------------------------------------------------------

@case("one current artifact per child_project_id -> no failures")
def _(tmp):
    reset_ids()
    events = [workstream("WS-001", child="child-a"),
              workstream("WS-002", child="child-b")]
    return expect_clean(check_registry_supersede_chain(PROJECT, events))


@case("legal transitions active->parked->active->retired -> no failures")
def _(tmp):
    reset_ids()
    events = [
        workstream("WS-001", status="active"),
        workstream("WS-002", status="parked", reverses="WS-001"),
        workstream("WS-003", status="active", reverses="WS-002"),
        workstream("WS-004", status="retired", reverses="WS-003"),
    ]
    return expect_clean(check_registry_supersede_chain(PROJECT, events))


@case("illegal transition retired->active -> registry_status_vs_supersede_chain")
def _(tmp):
    reset_ids()
    events = [workstream("WS-001", status="retired"),
              workstream("WS-002", status="active", reverses="WS-001")]
    return expect_failures(check_registry_supersede_chain(PROJECT, events), 1,
                           ["registry_status_vs_supersede_chain", "retired -> active"])


@case("illegal transition done->parked -> registry_status_vs_supersede_chain")
def _(tmp):
    reset_ids()
    events = [workstream("WS-001", status="done"),
              workstream("WS-002", status="parked", reverses="WS-001")]
    return expect_failures(check_registry_supersede_chain(PROJECT, events), 1,
                           ["done -> parked"])


@case("unchanged status on a metadata supersede is legal (T-004 citation refresh)")
def _(tmp):
    reset_ids()
    events = [workstream("WS-001", status="active"),
              workstream("WS-002", status="active", reverses="WS-001")]
    return expect_clean(check_registry_supersede_chain(PROJECT, events))


@case("two current artifacts for one child_project_id -> FAIL")
def _(tmp):
    reset_ids()
    events = [workstream("WS-001", child="child-a"),
              workstream("WS-002", child="child-a")]   # neither supersedes the other
    return expect_failures(check_registry_supersede_chain(PROJECT, events), 1,
                           ["registry_status_vs_supersede_chain", "child-a",
                            "WS-001", "WS-002"])


@case("explicit superseded_by on the old artifact resolves the current one")
def _(tmp):
    reset_ids()
    old = workstream("WS-001", child="child-a")
    old["payload"]["superseded_by"] = "[WS-002#abcdefabcdef]"
    events = [old, workstream("WS-002", child="child-a")]
    return expect_clean(check_registry_supersede_chain(PROJECT, events))


@case("reverses pointing at an unregistered workstream -> FAIL")
def _(tmp):
    reset_ids()
    events = [workstream("WS-007", status="parked", reverses="WS-006")]
    return expect_failures(check_registry_supersede_chain(PROJECT, events), 1,
                           ["WS-007 reverses WS-006"])


@case("reverses accepts a list (v5.3) and checks every predecessor")
def _(tmp):
    reset_ids()
    events = [
        workstream("WS-001", child="child-a", status="active"),
        workstream("WS-002", child="child-b", status="done"),
        workstream("WS-003", child="child-a", status="retired",
                    reverses=["WS-001", "WS-002"]),
    ]
    # WS-001 active->retired is legal; WS-002 done->retired is not.
    return expect_failures(check_registry_supersede_chain(PROJECT, events), 1,
                           ["done -> retired"])


@case("workstream.add with no artifact id -> FAIL")
def _(tmp):
    reset_ids()
    events = [ev("workstream.add", {"child_project_id": "child-a", "status": "active"})]
    return expect_failures(check_registry_supersede_chain(PROJECT, events), 1,
                           ["no artifact_id"])


@case("no workstream events at all -> no failures")
def _(tmp):
    reset_ids()
    return expect_clean(check_registry_supersede_chain(
        PROJECT, [ev("task.create", {"task_id": "T-000"})]))


# ---------------------------------------------------------------------------
# rollup_citation_stale_or_broken
# ---------------------------------------------------------------------------

@case("write-time citation that resolves and matches -> no findings")
def _(tmp):
    reset_ids()
    digest = write_sibling_projection(tmp, "child-a/SESSION-HANDOFF.md", "handoff v1")
    events = [workstream("WS-001", citation=citation("child-a/SESSION-HANDOFF.md", digest))]
    failures, warnings = check_rollup_citations(tmp, PROJECT, events)
    return (failures == [] and warnings == [], f"got {failures} {warnings}")


@case("write-time citation in 12-hex short form is accepted")
def _(tmp):
    reset_ids()
    digest = write_sibling_projection(tmp, "child-a/CYCLES.md", "cycles v1")
    events = [workstream("WS-001",
                          citation=citation("child-a/CYCLES.md", "sha256:" + digest[:12]))]
    failures, warnings = check_rollup_citations(tmp, PROJECT, events)
    return (failures == [] and warnings == [], f"got {failures} {warnings}")


@case("write-time citation whose path does not resolve -> hard FAIL")
def _(tmp):
    reset_ids()
    events = [workstream("WS-001", citation=citation("child-a/GONE.md", "a" * 64))]
    failures, warnings = check_rollup_citations(tmp, PROJECT, events)
    ok, detail = expect_failures(failures, 1,
                                 ["rollup_citation_stale_or_broken", "does not resolve"])
    return (ok and warnings == [], detail or f"unexpected warnings {warnings}")


@case("write-time citation whose hash does not match the file -> hard FAIL")
def _(tmp):
    reset_ids()
    write_sibling_projection(tmp, "child-a/SESSION-HANDOFF.md", "handoff v2")
    events = [workstream("WS-001",
                          citation=citation("child-a/SESSION-HANDOFF.md", "b" * 64))]
    failures, _warnings = check_rollup_citations(tmp, PROJECT, events)
    return expect_failures(failures, 1, ["rollup_citation_stale_or_broken", "now hashes"])


@case("write-time citation with a truncated sha256 -> hard FAIL")
def _(tmp):
    reset_ids()
    write_sibling_projection(tmp, "child-a/SESSION-HANDOFF.md", "handoff v2")
    events = [workstream("WS-001",
                          citation=citation("child-a/SESSION-HANDOFF.md", "abc"))]
    failures, _warnings = check_rollup_citations(tmp, PROJECT, events)
    return expect_failures(failures, 1, ["12-hex short form"])


@case("prior cycle's citation whose path vanished -> WARNING, not FAIL")
def _(tmp):
    reset_ids()
    digest = write_sibling_projection(tmp, "child-a/SESSION-HANDOFF.md", "handoff v3")
    events = [
        workstream("WS-001", citation=citation("child-a/MOVED.md", "a" * 64, "C-001")),
        workstream("WS-001", citation=citation("child-a/SESSION-HANDOFF.md",
                                                digest, "C-002")),
    ]
    failures, warnings = check_rollup_citations(tmp, PROJECT, events)
    ok = failures == [] and len(warnings) == 1 and "rollup_citation_broken" in warnings[0]
    return (ok, f"expected one non-blocking warning, got {failures} {warnings}")


@case("prior cycle's hash drifting is expected and reported as neither")
def _(tmp):
    reset_ids()
    digest_v2 = write_sibling_projection(tmp, "child-a/SESSION-HANDOFF.md", "handoff v2")
    events = [
        # C-001 recorded the file's older bytes; the sibling has since moved on.
        workstream("WS-001", citation=citation("child-a/SESSION-HANDOFF.md",
                                                "c" * 64, "C-001")),
        workstream("WS-001", citation=citation("child-a/SESSION-HANDOFF.md",
                                                digest_v2, "C-002")),
    ]
    failures, warnings = check_rollup_citations(tmp, PROJECT, events)
    return (failures == [] and warnings == [],
            f"expected staleness to be informational, got {failures} {warnings}")


@case("prior cycle unchanged on an ongoing workstream -> overdue candidate WARNING")
def _(tmp):
    reset_ids()
    digest = write_sibling_projection(tmp, "child-a/CYCLES.md", "cycles v1")
    events = [
        workstream("WS-001", lifecycle="ongoing",
                    citation=citation("child-a/CYCLES.md", digest, "C-001")),
        workstream("WS-001", lifecycle="ongoing",
                    citation=citation("child-a/CYCLES.md", digest, "C-002")),
    ]
    failures, warnings = check_rollup_citations(tmp, PROJECT, events)
    ok = (failures == [] and len(warnings) == 1
          and "rollup_citation_unchanged" in warnings[0]
          and "overdue_workstreams" in warnings[0])
    return (ok, f"expected one overdue-candidate warning, got {failures} {warnings}")


@case("prior cycle unchanged on a terminal workstream -> no finding")
def _(tmp):
    reset_ids()
    digest = write_sibling_projection(tmp, "child-a/SESSION-HANDOFF.md", "handoff")
    events = [
        workstream("WS-001", lifecycle="terminal",
                    citation=citation("child-a/SESSION-HANDOFF.md", digest, "C-001")),
        workstream("WS-001", lifecycle="terminal",
                    citation=citation("child-a/SESSION-HANDOFF.md", digest, "C-002")),
    ]
    failures, warnings = check_rollup_citations(tmp, PROJECT, events)
    return (failures == [] and warnings == [], f"got {failures} {warnings}")


@case("a superseded artifact's citation is never write-time checked")
def _(tmp):
    reset_ids()
    digest = write_sibling_projection(tmp, "child-a/SESSION-HANDOFF.md", "handoff")
    events = [
        workstream("WS-001", citation=citation("child-a/GONE.md", "a" * 64, "C-001")),
        workstream("WS-002", reverses="WS-001",
                    citation=citation("child-a/SESSION-HANDOFF.md", digest, "C-002")),
    ]
    failures, warnings = check_rollup_citations(tmp, PROJECT, events)
    ok = failures == [] and len(warnings) == 1
    return (ok, f"expected the superseded citation to be non-blocking, got "
                f"{failures} {warnings}")


@case("null last_rollup_citation (never rolled up) -> no findings")
def _(tmp):
    reset_ids()
    events = [workstream("WS-001", citation=None)]
    failures, warnings = check_rollup_citations(tmp, PROJECT, events)
    return (failures == [] and warnings == [], f"got {failures} {warnings}")


@case("end to end: verify()-level dispatch reports failures and warnings apart")
def _(tmp):
    reset_ids()
    write_program_schema(tmp)
    digest = write_sibling_projection(tmp, "child-a/CYCLES.md", "cycles v1")
    events = [
        proposed("P-1"), decided("P-1"),
        workstream("WS-001", proposal_id="P-1", lifecycle="ongoing",
                    citation=citation("child-a/CYCLES.md", digest, "C-001")),
        workstream("WS-001", proposal_id="P-1", lifecycle="ongoing",
                    citation=citation("child-a/CYCLES.md", digest, "C-002")),
        workstream("WS-002", child="child-b"),   # spawned, no pause: one FAIL
    ]
    failures, warnings = check_schema_declared_layer1(tmp, events)
    ok = (len(failures) == 1 and "spawn_pause_skipped" in failures[0]
          and len(warnings) == 1 and "rollup_citation_unchanged" in warnings[0])
    return (ok, f"expected 1 failure + 1 warning, got {failures} {warnings}")


def main() -> int:
    failures = 0
    for name, fn in CASES:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp = Path(raw_tmp)
            try:
                ok, detail = fn(tmp)
            except Exception as e:  # noqa: BLE001 - surface as a case failure
                ok, detail = False, f"raised {type(e).__name__}: {e}"
            status = "ok" if ok else "MISMATCH"
            if not ok:
                failures += 1
            print(f"[{status}] {name}")
            if not ok:
                print(f"         -> {detail}")

    print()
    if failures:
        print(f"{failures} case(s) FAILED")
        return 1
    print(f"All {len(CASES)} case(s) passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
