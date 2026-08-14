#!/usr/bin/env python3
"""
test_open_loops.py — regression test for the v6.0.0 open-loop checks in
tools/hw-verify.py (core/VERIFICATION.md §Layer 1 check 21,
core/SUBSTRATE.md §Open Loops).

Field evidence: a message cleared every technical gate for a server rejoin and
said the only remaining gate was the operator's word. Nothing tracked it. The
divergence between believed and actual state surfaced FIVE WEEKS later, through
an unrelated symptom, in production. Nothing was wrong with the work -- "waiting
on X" was a sentence in a document rather than a row anything could count.

Covers the three failure codes:

  - `loop.close` with no matching open      -> loop_close_without_open
  - a `loop_id` opened twice in one project -> duplicate_loop_open
  - a handoff omitting a loop open then     -> handoff_missing_open_loops

plus the backward-compatibility rule (an absent `open_loops` field is a note, not
a FAIL), per-project isolation, event-kind registration, and end-to-end dispatch.

Stdlib only; no pytest dependency, mirroring tools/test_checked_claims.py's
harness pattern (importlib-loads hw-verify.py).

Usage:  python tools/test_open_loops.py
Exits 0 if all cases pass, 1 otherwise.
"""

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
HW_VERIFY_PATH = HERE / "hw-verify.py"

spec = importlib.util.spec_from_file_location("hw_verify", HW_VERIFY_PATH)
hw_verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hw_verify)

check_open_loops = hw_verify.check_open_loops

PROJECT = "recovery"

_next_id = [0]


class _Omit:
    pass


_OMIT = _Omit()


def reset_ids():
    _next_id[0] = 0


def ev(kind: str, payload: dict | None = None, project: str = PROJECT) -> dict:
    _next_id[0] += 1
    return {"id": f"EV-{_next_id[0]:04d}", "actor": "planner",
            "project": project, "kind": kind, "payload": dict(payload or {})}


def loop_open(loop_id: str = "L-001", project: str = PROJECT,
              blocking_on: str = "operator-word", **extra) -> dict:
    payload = {"loop_id": loop_id,
               "description": "rejoin the standby server; every technical gate is cleared",
               "blocking_on": blocking_on,
               "opened_at": "2026-06-28T09:00:00Z",
               "stale_after_days": 7}
    payload.update(extra)
    return ev("loop.open", payload, project)


def loop_close(loop_id: str = "L-001", project: str = PROJECT) -> dict:
    return ev("loop.close", {"loop_id": loop_id,
                             "closed_at": "2026-07-02T09:00:00Z",
                             "resolution": "operator gave the word; rejoin done"},
              project)


def handoff(open_loops=_OMIT, project: str = PROJECT) -> dict:
    payload = {"project_id": project, "closing_actor": "executor:T-004",
               "recommended_first_action": "run hw verify --since"}
    if open_loops is not _OMIT:
        payload["open_loops"] = open_loops
    return ev("session.handoff", payload, project)


def scope_complete(project: str = PROJECT) -> dict:
    """A session.handoff needs one of these ahead of it (Layer 1 check 8)."""
    return ev("scope.complete", {"scope_items": []}, project)


def expect_clean(result) -> tuple:
    failures, notes = result
    return (failures == [], f"expected no failures, got {failures}")


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
# Legal loop sequences
# ---------------------------------------------------------------------------

@case("open -> close -> open -> close -> no failures")
def _(tmp):
    reset_ids()
    events = [loop_open("L-001"), loop_close("L-001"),
              loop_open("L-002"), loop_close("L-002")]
    return expect_clean(check_open_loops(events))


@case("an open loop at the end of the chain is legal (it is still waiting)")
def _(tmp):
    reset_ids()
    return expect_clean(check_open_loops([loop_open("L-001")]))


@case("several loops open at once -> no failures")
def _(tmp):
    reset_ids()
    events = [loop_open("L-001"), loop_open("L-002", blocking_on="external"),
              loop_open("L-003", blocking_on="scheduled")]
    return expect_clean(check_open_loops(events))


@case("loops close out of order -> no failures")
def _(tmp):
    reset_ids()
    events = [loop_open("L-001"), loop_open("L-002"),
              loop_close("L-002"), loop_close("L-001")]
    return expect_clean(check_open_loops(events))


@case("the same loop id in two projects is two loops")
def _(tmp):
    reset_ids()
    events = [loop_open("L-001", "alpha"), loop_open("L-001", "beta"),
              loop_close("L-001", "alpha"), loop_close("L-001", "beta")]
    return expect_clean(check_open_loops(events))


@case("a chain with no loop events at all -> no failures")
def _(tmp):
    reset_ids()
    return expect_clean(check_open_loops([ev("task.create", {"task_id": "T-001"})]))


# ---------------------------------------------------------------------------
# loop_close_without_open
# ---------------------------------------------------------------------------

@case("close with no open at all -> loop_close_without_open")
def _(tmp):
    reset_ids()
    return expect_failures(check_open_loops([loop_close("L-001")]), 1,
                           ["loop_close_without_open", "L-001", "EV-0001"])


@case("closing an already-closed loop -> loop_close_without_open")
def _(tmp):
    reset_ids()
    events = [loop_open("L-001"), loop_close("L-001"), loop_close("L-001")]
    return expect_failures(check_open_loops(events), 1,
                           ["loop_close_without_open", "already closed"])


@case("closing a loop id that was never opened, while another is open")
def _(tmp):
    reset_ids()
    events = [loop_open("L-001"), loop_close("L-009")]
    return expect_failures(check_open_loops(events), 1,
                           ["loop_close_without_open", "L-009"])


@case("closing a loop opened in a different project -> loop_close_without_open")
def _(tmp):
    reset_ids()
    events = [loop_open("L-001", "alpha"), loop_close("L-001", "beta")]
    return expect_failures(check_open_loops(events), 1,
                           ["beta", "loop_close_without_open"])


@case("a close with no loop_id at all -> loop_close_without_open")
def _(tmp):
    reset_ids()
    events = [ev("loop.close", {"closed_at": "2026-07-02T09:00:00Z",
                                "resolution": "done"})]
    return expect_failures(check_open_loops(events), 1,
                           ["loop_close_without_open", "<no loop_id>"])


# ---------------------------------------------------------------------------
# duplicate_loop_open
# ---------------------------------------------------------------------------

@case("the same loop id opened twice while open -> duplicate_loop_open")
def _(tmp):
    reset_ids()
    events = [loop_open("L-001"), loop_open("L-001")]
    return expect_failures(check_open_loops(events), 1,
                           ["duplicate_loop_open", "L-001", "EV-0001", "EV-0002"])


@case("reopening a closed loop id -> duplicate_loop_open (a recurrence is a new L id)")
def _(tmp):
    reset_ids()
    events = [loop_open("L-001"), loop_close("L-001"), loop_open("L-001")]
    return expect_failures(check_open_loops(events), 1,
                           ["duplicate_loop_open"])


@case("three opens under one id -> two duplicate failures, not a cascade")
def _(tmp):
    reset_ids()
    events = [loop_open("L-001"), loop_open("L-001"), loop_open("L-001")]
    return expect_failures(check_open_loops(events), 2, ["duplicate_loop_open"])


# ---------------------------------------------------------------------------
# handoff_missing_open_loops -- the five-week failure itself
# ---------------------------------------------------------------------------

@case("handoff listing the open loop -> no failures")
def _(tmp):
    reset_ids()
    events = [loop_open("L-003"), handoff(["L-003"])]
    return expect_clean(check_open_loops(events))


@case("handoff with [] when nothing is open -> no failures")
def _(tmp):
    reset_ids()
    events = [loop_open("L-001"), loop_close("L-001"), handoff([])]
    return expect_clean(check_open_loops(events))


@case("handoff omitting an open loop -> handoff_missing_open_loops")
def _(tmp):
    reset_ids()
    events = [loop_open("L-003"), handoff([])]
    return expect_failures(check_open_loops(events), 1,
                           ["handoff_missing_open_loops", "L-003", "EV-0002"])


@case("handoff listing one of two open loops -> names only the omitted one")
def _(tmp):
    reset_ids()
    events = [loop_open("L-003"), loop_open("L-004"), handoff(["L-003"])]
    failures, _ = check_open_loops(events)
    if len(failures) != 1:
        return (False, f"expected 1 failure, got {failures}")
    return ("L-004" in failures[0] and "omits L-004" in failures[0],
            f"expected the report to name only L-004: {failures[0]}")


@case("a loop closed before the handoff need not be listed")
def _(tmp):
    reset_ids()
    events = [loop_open("L-003"), loop_close("L-003"), handoff([])]
    return expect_clean(check_open_loops(events))


@case("a loop opened after the handoff is not the handoff's problem")
def _(tmp):
    reset_ids()
    events = [handoff([]), loop_open("L-003")]
    return expect_clean(check_open_loops(events))


@case("two handoffs, the second still omitting the loop -> two failures")
def _(tmp):
    reset_ids()
    events = [loop_open("L-003"), handoff([]), handoff([])]
    return expect_failures(check_open_loops(events), 2,
                           ["handoff_missing_open_loops", "EV-0002", "EV-0003"])


@case("open_loops as a string instead of a list -> handoff_missing_open_loops")
def _(tmp):
    reset_ids()
    events = [loop_open("L-003"), handoff("L-003")]
    return expect_failures(check_open_loops(events), 1,
                           ["handoff_missing_open_loops", "expected a list"])


@case("another project's open loop is not this handoff's obligation")
def _(tmp):
    reset_ids()
    events = [loop_open("L-003", "alpha"), handoff([], "beta")]
    return expect_clean(check_open_loops(events))


# ---------------------------------------------------------------------------
# Backward compatibility -- absent field is a note, not a FAIL
# ---------------------------------------------------------------------------

@case("a pre-v6 handoff with no open_loops field -> note, not failure")
def _(tmp):
    reset_ids()
    events = [loop_open("L-003"), handoff()]
    failures, notes = check_open_loops(events)
    if failures:
        return (False, f"expected no failures on a pre-v6 handoff, got {failures}")
    blob = " | ".join(notes)
    return ("handoff_open_loops_absent" in blob and "L-003" in blob,
            f"expected a note naming the open loop, got {notes}")


@case("a pre-v6 handoff with nothing open -> note says none")
def _(tmp):
    reset_ids()
    failures, notes = check_open_loops([handoff()])
    return (failures == [] and len(notes) == 1 and "none" in notes[0],
            f"expected one 'none' note, got failures={failures} notes={notes}")


@case("open_loops: null is treated as absent (a note), not as an empty list")
def _(tmp):
    reset_ids()
    events = [loop_open("L-003"), handoff(None)]
    failures, notes = check_open_loops(events)
    return (failures == [] and len(notes) == 1,
            f"expected a note and no failure, got failures={failures} notes={notes}")


@case("notes never block: verify() PASSes a pre-v6 handoff with an open loop")
def _(tmp):
    reset_ids()
    write_chain(tmp, [loop_open("L-003"), scope_complete(), handoff()])
    result = hw_verify.verify(tmp, None)
    return (result["result"] == "PASS" and len(result["open_loop_notes"]) == 1,
            f"expected PASS with one note, got {result['result']} "
            f"{result['open_loop_notes']}")


# ---------------------------------------------------------------------------
# Registration, docs and end-to-end dispatch
# ---------------------------------------------------------------------------

@case("loop.open / loop.close are known kinds with required payload fields")
def _(tmp):
    known = hw_verify.KNOWN_EVENT_KINDS
    required = hw_verify.REQUIRED_PAYLOAD_FIELDS
    checks = [
        ("loop.open" in known, "loop.open known"),
        ("loop.close" in known, "loop.close known"),
        ("blocking_on" in required.get("loop.open", ()), "blocking_on required on open"),
        ("opened_at" in required.get("loop.open", ()), "opened_at required on open"),
        ("resolution" in required.get("loop.close", ()), "resolution required on close"),
        ("open_loops" not in required.get("session.handoff", ()),
         "open_loops absent from the flat required list (it is a note, not a FAIL)"),
    ]
    bad = [label for ok, label in checks if not ok]
    return (not bad, f"registration mismatched on {bad}")


@case("templates/OPEN-LOOPS.md ships with the staleness column and protocol")
def _(tmp):
    text = (HERE.parent / "templates" / "OPEN-LOOPS.md").read_text(encoding="utf-8")
    checks = [
        ("Stale after" in text, "staleness column"),
        ("OVERDUE" in text, "overdue marker"),
        ("Newest first" in text, "newest-first ordering"),
        ("Rendering protocol" in text, "rendering protocol"),
        ("loop_close_without_open" in text, "names the failure codes"),
    ]
    bad = [label for ok, label in checks if not ok]
    return (not bad, f"OPEN-LOOPS.md missing {bad}")


@case("hw status leads with OVERDUE OPEN LOOPS and the handoff template carries the list")
def _(tmp):
    substrate = (HERE.parent / "core" / "SUBSTRATE.md").read_text(encoding="utf-8")
    handoff_tpl = (HERE.parent / "templates" / "session-handoff-template.md").read_text(encoding="utf-8")
    checks = [
        ("OVERDUE OPEN LOOPS" in substrate, "hw status block documented"),
        ("stale_after_days" in substrate, "staleness field documented"),
        ("five weeks" in substrate.lower(), "field evidence recorded"),
        ("Open loops" in handoff_tpl, "handoff template section"),
        ("open_loops" in handoff_tpl, "handoff template names the payload field"),
    ]
    bad = [label for ok, label in checks if not ok]
    return (not bad, f"docs missing {bad}")


@case("end to end: verify() FAILs a handoff that omits an open loop")
def _(tmp):
    reset_ids()
    write_chain(tmp, [loop_open("L-003"), scope_complete(), handoff([])])
    result = hw_verify.verify(tmp, None)
    if result["result"] != "FAIL":
        return (False, f"expected FAIL, got {result['result']}")
    return expect_failures((result["open_loop_failures"], []), 1,
                           ["handoff_missing_open_loops", "L-003"])


@case("end to end: verify() PASSes a clean open-and-close cycle")
def _(tmp):
    reset_ids()
    write_chain(tmp, [loop_open("L-001"), scope_complete(), handoff(["L-001"]),
                      loop_close("L-001")])
    result = hw_verify.verify(tmp, None)
    return (result["result"] == "PASS" and result["open_loop_failures"] == [],
            f"expected PASS, got {result['result']} {result['open_loop_failures']}")


def write_chain(tmp: Path, events: list):
    """Write a hash-chained events.jsonl so verify() sees an intact chain."""
    hw_dir = tmp / ".hyperworker"
    hw_dir.mkdir(parents=True, exist_ok=True)
    lines = []
    prev = "sha256:" + hw_verify.ZERO_HASH
    for event in events:
        full = {"id": event["id"], "ts": "2026-08-01T12:00:00Z", "kind": event["kind"],
                "actor": event["actor"], "project": event["project"],
                "payload": event["payload"], "prev_hash": prev}
        full["hash"] = "sha256:" + hw_verify.event_hash(full)
        prev = full["hash"]
        lines.append(json.dumps(full, sort_keys=True, separators=(",", ":"),
                                ensure_ascii=False))
    (hw_dir / "events.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (hw_dir / "hashes.json").write_text("{}", encoding="utf-8")


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
