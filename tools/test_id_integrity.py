#!/usr/bin/env python3
"""
test_id_integrity.py — regression test for the v6.0.0 event-ID integrity check
in tools/hw-verify.py (core/VERIFICATION.md §Layer 1 check 14,
core/SUBSTRATE.md §Deriving the Next Event ID).

The field incident this pins: two agents appended to one chain over a ten-week
deployment; the resuming agent derived its next event ID from the last event of
its own project rather than from the chain tail, so EV-0116..EV-0120 exist twice
with different content. Both runs linked prev_hash correctly, so the hash chain
verified and `hw verify` returned PASS on a log with ten events and five names.

Covers:
  - duplicate IDs anywhere in the chain (adjacent, far apart, three-way, and the
    reproduced five-event field incident)
  - the duplicate report carrying both line numbers, actors and projects
  - non-monotonic IDs (backwards jump, repeat-after-gap) with the offending and
    the prior high-water event both named
  - a duplicate is reported once (as a duplicate), never twice
  - clean chains, single events, empty chains, gaps, and unparseable IDs

Stdlib only; no pytest dependency, mirroring tools/test_scope_completeness.py's
harness pattern (importlib-loads hw-verify.py).

Usage:  python tools/test_id_integrity.py
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

check_id_integrity = hw_verify.check_id_integrity
parse_event_id = hw_verify.parse_event_id
load_events_with_lines = hw_verify.load_events_with_lines

PROJECT = "demo-project"


def ev(event_id: str, actor: str = "executor:T-001", project: str = PROJECT,
       kind: str = "task.status") -> dict:
    """Minimal synthetic event. Only the fields check_id_integrity reads are set."""
    return {"id": event_id, "actor": actor, "project": project, "kind": kind,
            "payload": {}}


CASES = []


def case(name):
    def register(fn):
        CASES.append((name, fn))
        return fn
    return register


# ---------------------------------------------------------------------------
# Clean chains
# ---------------------------------------------------------------------------

@case("strictly increasing IDs -> no findings")
def _(tmp):
    events = [ev(f"EV-{n:04d}") for n in range(1, 6)]
    dupes, non_mono = check_id_integrity(events)
    return (dupes == [] and non_mono == [], f"got dupes={dupes} non_mono={non_mono}")


@case("increasing IDs with gaps -> no findings (gaps are legal)")
def _(tmp):
    events = [ev("EV-0001"), ev("EV-0007"), ev("EV-0100")]
    dupes, non_mono = check_id_integrity(events)
    return (dupes == [] and non_mono == [], f"got dupes={dupes} non_mono={non_mono}")


@case("empty chain -> no findings")
def _(tmp):
    dupes, non_mono = check_id_integrity([])
    return (dupes == [] and non_mono == [], f"got dupes={dupes} non_mono={non_mono}")


@case("single event -> no findings")
def _(tmp):
    dupes, non_mono = check_id_integrity([ev("EV-0001")])
    return (dupes == [] and non_mono == [], f"got dupes={dupes} non_mono={non_mono}")


# ---------------------------------------------------------------------------
# Duplicates
# ---------------------------------------------------------------------------

@case("adjacent duplicate ID -> one duplicate finding")
def _(tmp):
    events = [ev("EV-0001"), ev("EV-0002"), ev("EV-0002"), ev("EV-0003")]
    dupes, _non_mono = check_id_integrity(events)
    ok = len(dupes) == 1 and "EV-0002" in dupes[0] and "appears 2 times" in dupes[0]
    return (ok, f"expected one EV-0002 duplicate, got {dupes}")


@case("far-apart duplicate ID -> one duplicate finding")
def _(tmp):
    events = [ev("EV-0001"), ev("EV-0002"), ev("EV-0003"), ev("EV-0004"),
              ev("EV-0002")]
    dupes, _non_mono = check_id_integrity(events)
    ok = len(dupes) == 1 and "EV-0002" in dupes[0]
    return (ok, f"expected one EV-0002 duplicate, got {dupes}")


@case("three events sharing one ID -> one finding naming all three")
def _(tmp):
    events = [ev("EV-0009"), ev("EV-0009"), ev("EV-0009")]
    dupes, _non_mono = check_id_integrity(events)
    ok = len(dupes) == 1 and "appears 3 times" in dupes[0]
    return (ok, f"expected one 3-way duplicate finding, got {dupes}")


@case("duplicate report carries both line numbers, actors and projects")
def _(tmp):
    events = [
        ev("EV-0116", actor="executor:T-007", project="alpha"),
        ev("EV-0117", actor="executor:T-007", project="alpha"),
        ev("EV-0116", actor="executor:T-031", project="beta"),
    ]
    dupes, _non_mono = check_id_integrity(events, line_numbers=[118, 119, 224])
    if len(dupes) != 1:
        return (False, f"expected exactly one duplicate finding, got {dupes}")
    text = dupes[0]
    needed = ["line 118", "line 224", "executor:T-007", "executor:T-031",
              "alpha", "beta"]
    missing = [n for n in needed if n not in text]
    return (not missing, f"report missing {missing}: {text}")


@case("field incident: EV-0116..EV-0120 appended twice -> five duplicate findings")
def _(tmp):
    first = [ev(f"EV-{n:04d}", actor="executor:T-007", project="alpha")
             for n in range(112, 121)]
    second = [ev(f"EV-{n:04d}", actor="executor:T-031", project="beta")
              for n in range(116, 121)]
    dupes, non_mono = check_id_integrity(first + second)
    ok = len(dupes) == 5 and all("appears 2 times" in d for d in dupes)
    # The duplicated IDs must not ALSO be counted as non-monotonic.
    ok = ok and non_mono == []
    return (ok, f"expected 5 duplicates and 0 non-monotonic, got "
                f"dupes={len(dupes)} non_mono={non_mono}")


@case("duplicate findings are sorted deterministically")
def _(tmp):
    events = [ev("EV-0005"), ev("EV-0001"), ev("EV-0005"), ev("EV-0001")]
    dupes, _non_mono = check_id_integrity(events)
    ok = len(dupes) == 2 and dupes == sorted(dupes)
    return (ok, f"expected 2 sorted duplicate findings, got {dupes}")


# ---------------------------------------------------------------------------
# Monotonicity
# ---------------------------------------------------------------------------

@case("backwards ID -> one non-monotonic finding naming both events")
def _(tmp):
    events = [ev("EV-0001"), ev("EV-0009"), ev("EV-0004")]
    dupes, non_mono = check_id_integrity(events)
    ok = (dupes == [] and len(non_mono) == 1
          and "EV-0004" in non_mono[0] and "EV-0009" in non_mono[0])
    return (ok, f"expected one non-monotonic finding, got {non_mono}")


@case("two backwards IDs after one high-water mark -> two findings")
def _(tmp):
    events = [ev("EV-0010"), ev("EV-0003"), ev("EV-0004")]
    _dupes, non_mono = check_id_integrity(events)
    return (len(non_mono) == 2, f"expected 2 non-monotonic findings, got {non_mono}")


@case("high-water mark is the max seen, not the previous event")
def _(tmp):
    # EV-0004 already lost to EV-0010; EV-0011 is fine and becomes the new high.
    events = [ev("EV-0010"), ev("EV-0004"), ev("EV-0011"), ev("EV-0012")]
    _dupes, non_mono = check_id_integrity(events)
    ok = len(non_mono) == 1 and "EV-0004" in non_mono[0]
    return (ok, f"expected only EV-0004 flagged, got {non_mono}")


@case("non-monotonic report carries line numbers, actors and projects")
def _(tmp):
    events = [
        ev("EV-0009", actor="planner", project="alpha"),
        ev("EV-0004", actor="operator", project="beta"),
    ]
    _dupes, non_mono = check_id_integrity(events, line_numbers=[42, 43])
    if len(non_mono) != 1:
        return (False, f"expected one finding, got {non_mono}")
    text = non_mono[0]
    needed = ["line 42", "line 43", "planner", "operator", "alpha", "beta"]
    missing = [n for n in needed if n not in text]
    return (not missing, f"report missing {missing}: {text}")


@case("unparseable IDs are skipped by monotonicity, still checked for duplicates")
def _(tmp):
    events = [ev("EV-0001"), ev("SNAPSHOT"), ev("EV-0002"), ev("SNAPSHOT")]
    dupes, non_mono = check_id_integrity(events)
    ok = len(dupes) == 1 and "SNAPSHOT" in dupes[0] and non_mono == []
    return (ok, f"expected 1 duplicate and 0 non-monotonic, got "
                f"dupes={dupes} non_mono={non_mono}")


@case("parse_event_id handles EV-NNNN, wide IDs, and junk")
def _(tmp):
    checks = [
        (parse_event_id("EV-0001") == 1, "EV-0001"),
        (parse_event_id("EV-12345") == 12345, "EV-12345"),
        (parse_event_id("ev-0001") is None, "lowercase"),
        (parse_event_id("EV-00A1") is None, "non-numeric"),
        (parse_event_id(None) is None, "None"),
        (parse_event_id(7) is None, "int"),
    ]
    bad = [label for ok, label in checks if not ok]
    return (not bad, f"parse_event_id mismatched on {bad}")


# ---------------------------------------------------------------------------
# End-to-end through verify()
# ---------------------------------------------------------------------------

@case("verify() reports duplicates with real file line numbers and FAILs")
def _(tmp):
    hw_dir = tmp / ".hyperworker"
    hw_dir.mkdir(parents=True, exist_ok=True)
    lines = []
    prev = hw_verify.ZERO_HASH
    for event_id, actor, project in (("EV-0001", "planner", "alpha"),
                                     ("EV-0002", "executor:T-001", "alpha"),
                                     ("EV-0002", "executor:T-009", "beta")):
        event = {"id": event_id, "ts": "2026-08-14T00:00:00Z", "kind": "task.status",
                 "actor": actor, "project": project, "payload": {},
                 "prev_hash": prev}
        event["hash"] = hw_verify.event_hash(event)
        prev = event["hash"]
        lines.append(json.dumps(event, sort_keys=True, separators=(",", ":"),
                                ensure_ascii=False))
    # A blank line so list position and file line number diverge.
    (hw_dir / "events.jsonl").write_text(
        lines[0] + "\n\n" + lines[1] + "\n" + lines[2] + "\n", encoding="utf-8")

    events, line_numbers = load_events_with_lines(hw_dir / "events.jsonl")
    if line_numbers != [1, 3, 4]:
        return (False, f"expected line numbers [1, 3, 4], got {line_numbers}")

    result = hw_verify.verify(tmp, None)
    ok = (result["result"] == "FAIL"
          and len(result["duplicate_event_ids"]) == 1
          and "line 4" in result["duplicate_event_ids"][0]
          and result["tamper"] == []
          and result["chain_breaks"] == [])
    return (ok, f"expected FAIL on duplicate IDs with intact chain, got {result}")


@case("verify() PASSes an otherwise-clean chain with unique increasing IDs")
def _(tmp):
    hw_dir = tmp / ".hyperworker"
    hw_dir.mkdir(parents=True, exist_ok=True)
    lines = []
    prev = hw_verify.ZERO_HASH
    for n in (1, 2, 3):
        event = {"id": f"EV-{n:04d}", "ts": "2026-08-14T00:00:00Z",
                 "kind": "task.status", "actor": "planner", "project": "alpha",
                 "payload": {}, "prev_hash": prev}
        event["hash"] = hw_verify.event_hash(event)
        prev = event["hash"]
        lines.append(json.dumps(event, sort_keys=True, separators=(",", ":"),
                                ensure_ascii=False))
    (hw_dir / "events.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    result = hw_verify.verify(tmp, None)
    ok = (result["result"] == "PASS"
          and result["duplicate_event_ids"] == []
          and result["non_monotonic_event_ids"] == [])
    return (ok, f"expected PASS with no ID findings, got {result}")


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
