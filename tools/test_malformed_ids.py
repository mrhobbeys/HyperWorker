#!/usr/bin/env python3
"""
test_malformed_ids.py — regression test for identifier typing in
tools/hw-verify.py (core/VERIFICATION.md §Layer 1, `malformed_payloads`).

The defect this pins: `hw verify` raised an uncaught exception on payloads whose
identifier fields carried the wrong type. A `loop.open` with no `loop_id` put
`None` into the open-loop set and the next `session.handoff` died in `sorted()`;
a `loop_id` carrying a list died as an unhashable dict key; a `project.activate`
with an integer `project_id` reached path construction and died there.

That is worse than a wrong answer. `events.jsonl` is append-only: the operator
cannot delete the offending event, so a verifier that raises turns one malformed
payload into a workspace that can never be verified again, and reports nothing
about the other events in the chain. The rule this suite enforces:

  A malformed identifier is a Layer 1 FAIL with a full report, never a traceback.

Every case asserts three things: verification completes, the result is FAIL, and
the malformed value is named in a report row. The end-to-end cases run the
script as a subprocess and assert exit code 1 and a complete 31-row report --
the same exit code every other FAIL produces.

Stdlib only; no pytest dependency, mirroring tools/test_open_loops.py's harness
pattern (importlib-loads hw-verify.py).

Usage:  python tools/test_malformed_ids.py
Exits 0 if all cases pass, 1 otherwise.
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
HW_VERIFY_PATH = HERE / "hw-verify.py"

spec = importlib.util.spec_from_file_location("hw_verify", HW_VERIFY_PATH)
hw_verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hw_verify)

check_open_loops = hw_verify.check_open_loops
check_identifier_types = hw_verify.check_identifier_types

PROJECT = "recovery"

_next_id = [0]


def reset_ids():
    _next_id[0] = 0


def ev(kind: str, payload=None, project=PROJECT, actor="planner") -> dict:
    _next_id[0] += 1
    return {"id": f"EV-{_next_id[0]:04d}", "actor": actor,
            "project": project, "kind": kind,
            "payload": payload if payload is not None else {}}


def loop_open(loop_id="L-001", project=PROJECT, omit_id=False) -> dict:
    payload = {"description": "rejoin the standby server",
               "blocking_on": "operator-word",
               "opened_at": "2026-06-28T09:00:00Z",
               "stale_after_days": 7}
    if not omit_id:
        payload["loop_id"] = loop_id
    return ev("loop.open", payload, project)


def loop_close(loop_id="L-001", project=PROJECT, omit_id=False) -> dict:
    payload = {"closed_at": "2026-07-02T09:00:00Z",
               "resolution": "operator gave the word"}
    if not omit_id:
        payload["loop_id"] = loop_id
    return ev("loop.close", payload, project)


def handoff(open_loops=None, project=PROJECT) -> dict:
    payload = {"project_id": project, "closing_actor": "executor:T-004",
               "recommended_first_action": "run hw verify --since"}
    if open_loops is not None:
        payload["open_loops"] = open_loops
    return ev("session.handoff", payload, project)


def scope_complete(project=PROJECT) -> dict:
    """A session.handoff needs one of these ahead of it (Layer 1 check 8)."""
    return ev("scope.complete", {"scope_items": []}, project)


def write_chain(tmp: Path, events: list):
    """Write a hash-chained events.jsonl so verify() sees an intact chain."""
    hw_dir = tmp / ".hyperworker"
    hw_dir.mkdir(parents=True, exist_ok=True)
    lines = []
    prev = "sha256:" + hw_verify.ZERO_HASH
    for event in events:
        full = {"id": event["id"], "ts": "2026-08-01T12:00:00Z",
                "kind": event["kind"], "actor": event["actor"],
                "project": event["project"], "payload": event["payload"],
                "prev_hash": prev}
        full["hash"] = "sha256:" + hw_verify.event_hash(full)
        prev = full["hash"]
        lines.append(json.dumps(full, sort_keys=True, separators=(",", ":"),
                                ensure_ascii=False))
    (hw_dir / "events.jsonl").write_text("\n".join(lines) + "\n",
                                         encoding="utf-8", newline="")
    (hw_dir / "hashes.json").write_text("{}", encoding="utf-8", newline="")


def run_cli(tmp: Path, *extra) -> tuple:
    """Run hw-verify.py as the operator would. Returns (exit_code, stdout)."""
    proc = subprocess.run(
        [sys.executable, str(HW_VERIFY_PATH), "--workspace", str(tmp), *extra],
        capture_output=True, text=True,
    )
    return proc.returncode, proc.stdout + proc.stderr


def expect_report_fail(tmp: Path, tokens, *extra) -> tuple:
    """The whole contract in one assertion: exit 1, a full report, no traceback,
    and the malformed value named somewhere in it.
    """
    code, out = run_cli(tmp, *extra)
    if "Traceback" in out:
        return (False, f"verification raised instead of reporting:\n{out}")
    if code != 1:
        return (False, f"expected exit 1 (the FAIL code), got {code}:\n{out}")
    if "  result:                FAIL" not in out:
        return (False, f"expected a FAIL result row, got:\n{out}")
    rows = [line for line in out.splitlines() if line.startswith("  ")]
    if len(rows) < 31:
        return (False, f"report truncated to {len(rows)} rows:\n{out}")
    missing = [t for t in tokens if t not in out]
    if missing:
        return (False, f"report never names {missing}:\n{out}")
    return (True, "")


def expect_failures(result, count: int, tokens=()) -> tuple:
    failures, _notes = result
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
# The four named field shapes, end to end through the CLI
# ---------------------------------------------------------------------------

@case("end to end: loop.open with no loop_id, then a handoff -> FAIL, not a crash")
def _(tmp):
    reset_ids()
    write_chain(tmp, [loop_open(omit_id=True), scope_complete(), handoff([])])
    return expect_report_fail(tmp, ["malformed_loop_id", "EV-0001"])


@case("end to end: loop_id as a list -> FAIL, not an unhashable-type crash")
def _(tmp):
    reset_ids()
    write_chain(tmp, [loop_open(["L-001"]), loop_close(["L-001"])])
    return expect_report_fail(tmp, ["loop_id is list", "EV-0001", "EV-0002"])


@case("end to end: loop.close with no loop_id -> FAIL, not a crash")
def _(tmp):
    reset_ids()
    write_chain(tmp, [loop_close(omit_id=True)])
    return expect_report_fail(tmp, ["loop_close_without_open", "<no loop_id>"])


@case("end to end: project.activate with an int project_id -> FAIL, not a path crash")
def _(tmp):
    reset_ids()
    write_chain(tmp, [ev("project.activate", {"project_id": 123})])
    return expect_report_fail(tmp, ["project_id is int 123", "EV-0001"])


@case("end to end: --strict-secrets reports the same malformed id, same exit code")
def _(tmp):
    reset_ids()
    write_chain(tmp, [ev("project.activate", {"project_id": 123})])
    return expect_report_fail(tmp, ["project_id is int 123"], "--strict-secrets")


@case("end to end: a malformed id does not suppress the rest of the chain's report")
def _(tmp):
    reset_ids()
    write_chain(tmp, [loop_open(omit_id=True), loop_close("L-009")])
    code, out = run_cli(tmp)
    checks = [
        ("Traceback" not in out, "no traceback"),
        (code == 1, "exit 1"),
        ("malformed_loop_id" in out, "the malformed open is reported"),
        ("loop_close_without_open" in out, "the later close is still checked"),
        ("events_scanned:        2" in out, "both events were scanned"),
    ]
    bad = [label for ok, label in checks if not ok]
    return (not bad, f"report incomplete on {bad}:\n{out}")


# ---------------------------------------------------------------------------
# check_open_loops: loop_id typing
# ---------------------------------------------------------------------------

@case("loop.open with no loop_id -> malformed_loop_id, and nothing enters the open set")
def _(tmp):
    reset_ids()
    return expect_failures(check_open_loops([loop_open(omit_id=True), handoff([])]),
                           1, ["malformed_loop_id", "absent", "EV-0001"])


@case("loop.open with a list loop_id -> malformed_loop_id naming the type")
def _(tmp):
    reset_ids()
    return expect_failures(check_open_loops([loop_open(["L-001"])]), 1,
                           ["malformed_loop_id", "list"])


@case("loop.open with an int loop_id -> malformed_loop_id naming the type")
def _(tmp):
    reset_ids()
    return expect_failures(check_open_loops([loop_open(7)]), 1,
                           ["malformed_loop_id", "int"])


@case("loop.open with a blank loop_id -> malformed_loop_id (a name of spaces is no name)")
def _(tmp):
    reset_ids()
    return expect_failures(check_open_loops([loop_open("   ")]), 1,
                           ["malformed_loop_id", "str"])


@case("a malformed open does not poison a later handoff's sorted() report")
def _(tmp):
    reset_ids()
    events = [loop_open("L-001"), loop_open(omit_id=True), handoff([])]
    failures, _notes = check_open_loops(events)
    blob = " | ".join(failures)
    checks = [
        (len(failures) == 2, f"expected 2 failures, got {failures}"),
        ("malformed_loop_id" in blob, "the malformed open is named"),
        ("handoff_missing_open_loops" in blob, "the well-formed loop is still counted"),
        ("L-001" in blob, "the well-formed loop id is named"),
    ]
    bad = [label for ok, label in checks if not ok]
    return (not bad, f"failed on {bad}: {failures}")


@case("a malformed open does not poison a pre-v6 handoff's note either")
def _(tmp):
    reset_ids()
    events = [loop_open("L-001"), loop_open(omit_id=True), handoff()]
    failures, notes = check_open_loops(events)
    return (len(notes) == 1 and "L-001" in notes[0] and len(failures) == 1,
            f"expected one note naming L-001 and one failure, "
            f"got failures={failures} notes={notes}")


@case("loop.close with a list loop_id -> loop_close_without_open, rendered <no loop_id>")
def _(tmp):
    reset_ids()
    return expect_failures(check_open_loops([loop_close(["L-001"])]), 1,
                           ["loop_close_without_open", "<no loop_id>"])


@case("a non-mapping payload on a loop event is skipped, not dereferenced")
def _(tmp):
    reset_ids()
    return expect_failures(check_open_loops([ev("loop.open", ["not-a-mapping"])]),
                           1, ["malformed_loop_id", "absent"])


@case("a non-string project groups under no project and is skipped")
def _(tmp):
    reset_ids()
    return expect_failures(check_open_loops([loop_open("L-001", project=["p"])]), 0)


# ---------------------------------------------------------------------------
# check_identifier_types: what it reports, and what it deliberately does not
# ---------------------------------------------------------------------------

@case("an absent identifier is NOT reported here (the required-field check owns it)")
def _(tmp):
    reset_ids()
    return (check_identifier_types([loop_open(omit_id=True)]) == [],
            "an absent field must be reported once, by the required-field check")


@case("a well-typed chain reports nothing")
def _(tmp):
    reset_ids()
    events = [ev("project.activate", {"project_id": "p1"}),
              loop_open("L-001"), loop_close("L-001"), handoff([])]
    return (check_identifier_types(events) == [],
            f"expected silence, got {check_identifier_types(events)}")


@case("project_id, cycle_id and loop_id are each type-checked")
def _(tmp):
    reset_ids()
    events = [
        ev("project.activate", {"project_id": 123}),
        ev("cycle.open", {"project_id": "p1", "cycle_id": ["C-001"],
                          "opened_at": "2026-01-01", "cadence": "weekly"}),
        loop_open({"loop_id": "L-001"}),
    ]
    failures = check_identifier_types(events)
    blob = " | ".join(failures)
    checks = [
        (len(failures) == 3, f"expected 3, got {failures}"),
        ("project_id is int" in blob, "project_id typed"),
        ("cycle_id is list" in blob, "cycle_id typed"),
        ("loop_id is dict" in blob, "loop_id typed"),
    ]
    bad = [label for ok, label in checks if not ok]
    return (not bad, f"failed on {bad}: {failures}")


@case("a payload that is not a mapping is reported once, and no field is read from it")
def _(tmp):
    reset_ids()
    failures = check_identifier_types([ev("loop.open", ["nope"])])
    return (len(failures) == 1 and "payload is list" in failures[0],
            f"expected one payload-shape failure, got {failures}")


@case("a non-string project is reported")
def _(tmp):
    reset_ids()
    failures = check_identifier_types([loop_open("L-001", project=["p"])])
    return (len(failures) == 1 and "project is list" in failures[0],
            f"expected one project-shape failure, got {failures}")


@case("the report names the type but never invents a value")
def _(tmp):
    reset_ids()
    failures = check_identifier_types([ev("project.activate", {"project_id": 123})])
    return (len(failures) == 1 and "int 123" in failures[0]
            and "expected an id string" in failures[0],
            f"expected a typed report, got {failures}")


@case("evidence.capture ids stay with check_evidence_capture (one defect, one report)")
def _(tmp):
    reset_ids()
    events = [ev("evidence.capture", {"id": 7, "producing_command": "x",
                                      "captured_at": "2026-01-01",
                                      "summary": "s", "content": "out"})]
    identifier_failures = check_identifier_types(events)
    evidence_failures = hw_verify.check_evidence_capture(events)
    return (identifier_failures == [] and len(evidence_failures) == 1
            and "evidence_id_malformed" in evidence_failures[0],
            f"expected the evidence check to own it, got "
            f"identifier={identifier_failures} evidence={evidence_failures}")


# ---------------------------------------------------------------------------
# The path-construction family: nothing builds a Path out of a non-string
# ---------------------------------------------------------------------------

@case("lock_target returns None for a project_id that is not a string")
def _(tmp):
    bad = [123, ["p"], {"p": 1}, "   ", True]
    got = [hw_verify.lock_target(
        {"kind": "project.activate", "project": None, "payload": {"project_id": v}})
        for v in bad]
    return (got == [None] * len(bad), f"expected all None, got {got}")


@case("lock_target still resolves a well-formed activate, and still skips _harness")
def _(tmp):
    good = hw_verify.lock_target(
        {"kind": "project.activate", "project": None, "payload": {"project_id": "p1"}})
    harness = hw_verify.lock_target(
        {"kind": "friction.log", "project": "_harness", "payload": {}})
    fallback = hw_verify.lock_target(
        {"kind": "project.activate", "project": "p2", "payload": {}})
    return (good == "p1" and harness is None and fallback == "p2",
            f"got good={good!r} harness={harness!r} fallback={fallback!r}")


@case("active_project never returns a non-string, so no path is built from one")
def _(tmp):
    reset_ids()
    events = [ev("project.activate", {"project_id": 123}, project=None)]
    return (hw_verify.active_project(events) is None,
            f"expected None, got {hw_verify.active_project(events)!r}")


@case("find_schema_for_project refuses a non-string project id instead of pathing it")
def _(tmp):
    got = [hw_verify.find_schema_for_project(tmp, v) for v in (123, ["p"], None, "")]
    return (got == [None] * 4, f"expected all None, got {got}")


@case("find_project_lifecycle refuses a non-string project id")
def _(tmp):
    got = [hw_verify.find_project_lifecycle(tmp, v) for v in (123, ["p"], None, "")]
    return (got == [None] * 4, f"expected all None, got {got}")


@case("find_project_profile falls back to the default for a non-string project id")
def _(tmp):
    got = [hw_verify.find_project_profile(tmp, v) for v in (123, ["p"], None, "")]
    return (got == [hw_verify.DEFAULT_PROFILE] * 4,
            f"expected the {hw_verify.DEFAULT_PROFILE} default, got {got}")


@case("check_harness_version completes on a chain whose only activate is malformed")
def _(tmp):
    reset_ids()
    events = [ev("project.activate", {"project_id": 123})]
    failures, notes = hw_verify.check_harness_version(tmp, events)
    return (failures == [] and notes == [],
            f"expected a quiet return, got failures={failures} notes={notes}")


@case("check_cycle_lifecycle renders a bad cycle_id as <no cycle_id>, never the value")
def _(tmp):
    reset_ids()
    events = [ev("cycle.close", {"project_id": "p1", "cycle_id": 5,
                                 "closed_at": "x", "summary": "s", "next_due": "y"})]
    failures = hw_verify.check_cycle_lifecycle(tmp, events)
    blob = " | ".join(failures)
    return (len(failures) == 1 and "cycle_close_without_open" in blob
            and "<no cycle_id>" in blob,
            f"expected one close-without-open naming <no cycle_id>, got {failures}")


@case("check_cycle_lifecycle completes with a payload that is not a mapping")
def _(tmp):
    reset_ids()
    events = [ev("cycle.open", ["nope"]), ev("cycle.open", ["nope-again"])]
    failures = hw_verify.check_cycle_lifecycle(tmp, events)
    blob = " | ".join(failures)
    return (len(failures) == 1 and "cycle_open_without_close" in blob
            and "<no cycle_id>" in blob,
            f"expected one open-without-close naming <no cycle_id>, got {failures}")


@case("check_actor_requirement completes with a non-string project")
def _(tmp):
    reset_ids()
    events = [ev("loop.open", {"loop_id": "L-001"}, project=["p"], actor=None)]
    failures, notes = hw_verify.check_actor_requirement(tmp, events)
    return (len(failures) == 1 and notes == [],
            f"expected one actor failure and no note, "
            f"got failures={failures} notes={notes}")


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

@case("check_identifier_types feeds malformed_payloads, which blocks PASS")
def _(tmp):
    reset_ids()
    write_chain(tmp, [ev("project.activate", {"project_id": 123})])
    result = hw_verify.verify(tmp, None)
    return (result["result"] == "FAIL"
            and any("project_id is int" in f for f in result["malformed_payloads"]),
            f"expected a blocking malformed_payloads row, got {result['result']} "
            f"{result['malformed_payloads']}")


@case("every identifier field in the table names a known event kind")
def _(tmp):
    unknown = [k for k in hw_verify.IDENTIFIER_PAYLOAD_FIELDS
               if k not in hw_verify.KNOWN_EVENT_KINDS and k != "project.wrap"]
    return (not unknown, f"table names unknown kinds: {unknown}")


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
