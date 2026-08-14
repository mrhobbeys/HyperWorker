#!/usr/bin/env python3
"""
test_one_line_events.py — regression test for the v6.0.0 one-line event kinds in
tools/hw-verify.py: the slimmed `friction.log` (core/SUBSTRATE.md §Friction Log
Event Kind, HARNESS.md §Friction Logs).

Field evidence: four `friction.log` entries in 130 events across ten weeks. The
mechanism existed and the operator wanted it; six required fields "felt heavier
than the value" and the engagement's best lessons went uncaptured. The payload is
now `{note}` required, `{category, severity, task_id}` optional -- and the pre-v6
rich form still verifies, so no chain has to migrate.

Covers: slim acceptance, rich back-compat, the neither-shape failure, and
end-to-end dispatch through verify() (the reports land in malformed_payloads,
which is the same class of defect as a missing required field).

Stdlib only; no pytest dependency, mirroring tools/test_checked_claims.py's
harness pattern (importlib-loads hw-verify.py).

Usage:  python tools/test_one_line_events.py
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

check_note_payloads = hw_verify.check_note_payloads

PROJECT = "recovery"

_next_id = [0]


def reset_ids():
    _next_id[0] = 0


def ev(kind: str, payload: dict | None = None, project: str = PROJECT) -> dict:
    _next_id[0] += 1
    return {"id": f"EV-{_next_id[0]:04d}", "actor": "executor:T-004",
            "project": project, "kind": kind, "payload": dict(payload or {})}


def rich_friction(**overrides) -> dict:
    payload = {
        "type": "OPERATOR-CONFUSION",
        "patch_id": None,
        "description": "The recitation band rejected three honest paraphrases.",
        "surfaced_by": "operator",
        "severity": "non-blocking",
        "suggested_target": "unclear",
    }
    payload.update(overrides)
    return ev("friction.log", payload)


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
# friction.log -- the slim form
# ---------------------------------------------------------------------------

@case("a bare note is a complete friction.log payload")
def _(tmp):
    reset_ids()
    events = [ev("friction.log", {"note": "The recitation band rejected three honest paraphrases."})]
    return expect_clean(check_note_payloads(events))


@case("note plus the optional fields -> no failures")
def _(tmp):
    reset_ids()
    events = [ev("friction.log", {"note": "hashes.json drifted after a manual edit",
                                  "category": "REGRESSION", "severity": "blocking",
                                  "task_id": "T-004"})]
    return expect_clean(check_note_payloads(events))


@case("a free-text category is accepted (no enum to get right)")
def _(tmp):
    reset_ids()
    events = [ev("friction.log", {"note": "the probe doc assumed a CMS",
                                  "category": "whatever this is"})]
    return expect_clean(check_note_payloads(events))


@case("several slim entries in one chain -> no failures")
def _(tmp):
    reset_ids()
    events = [ev("friction.log", {"note": f"note {n}"}) for n in range(5)]
    return expect_clean(check_note_payloads(events))


@case("a chain with no friction events at all -> no failures")
def _(tmp):
    reset_ids()
    return expect_clean(check_note_payloads([ev("task.create", {"task_id": "T-001"})]))


# ---------------------------------------------------------------------------
# friction.log -- pre-v6 rich back-compat
# ---------------------------------------------------------------------------

@case("the pre-v6 rich form still verifies with no note")
def _(tmp):
    reset_ids()
    return expect_clean(check_note_payloads([rich_friction()]))


@case("rich and slim entries coexist in one chain")
def _(tmp):
    reset_ids()
    events = [rich_friction(), ev("friction.log", {"note": "one line"})]
    return expect_clean(check_note_payloads(events))


@case("a note rescues a payload that is missing rich fields")
def _(tmp):
    reset_ids()
    events = [ev("friction.log", {"type": "REGRESSION", "note": "one line"})]
    return expect_clean(check_note_payloads(events))


# ---------------------------------------------------------------------------
# Neither shape
# ---------------------------------------------------------------------------

@case("a payload that is neither shape -> reported, naming note first")
def _(tmp):
    reset_ids()
    events = [ev("friction.log", {"type": "REGRESSION", "severity": "blocking"})]
    return expect_failures(check_note_payloads(events), 1,
                           ["friction.log", "note", "EV-0001"])


@case("an empty payload -> reported")
def _(tmp):
    reset_ids()
    return expect_failures(check_note_payloads([ev("friction.log", {})]), 1, ["note"])


@case("an empty note is not a note")
def _(tmp):
    reset_ids()
    return expect_failures(check_note_payloads([ev("friction.log", {"note": "   "})]), 1,
                           ["note is empty"])


@case("a non-string note is not a note")
def _(tmp):
    reset_ids()
    return expect_failures(check_note_payloads([ev("friction.log", {"note": 42})]), 1,
                           ["note is empty"])


@case("two bad payloads -> two failures, one per event")
def _(tmp):
    reset_ids()
    events = [ev("friction.log", {}), ev("friction.log", {"note": ""})]
    return expect_failures(check_note_payloads(events), 2, ["EV-0001", "EV-0002"])


# ---------------------------------------------------------------------------
# Registration and end-to-end dispatch
# ---------------------------------------------------------------------------

@case("friction.log carries no flat required-field list any more")
def _(tmp):
    checks = [
        ("friction.log" in hw_verify.KNOWN_EVENT_KINDS, "kind known"),
        ("friction.log" not in hw_verify.REQUIRED_PAYLOAD_FIELDS,
         "no flat required list (the either/or lives in check_note_payloads)"),
        (hw_verify.FRICTION_RICH_FIELDS == ("type", "description", "surfaced_by", "severity"),
         "rich field set preserved"),
    ]
    bad = [label for ok, label in checks if not ok]
    return (not bad, f"registration mismatched on {bad}")


@case("end to end: verify() PASSes a workspace of one-line friction notes")
def _(tmp):
    reset_ids()
    write_chain(tmp, [ev("friction.log", {"note": "the band rejected an honest paraphrase"}),
                      rich_friction()])
    result = hw_verify.verify(tmp, None)
    return (result["result"] == "PASS" and result["malformed_payloads"] == [],
            f"expected PASS, got {result['result']} {result['malformed_payloads']}")


@case("end to end: verify() FAILs a friction payload that is neither shape")
def _(tmp):
    reset_ids()
    write_chain(tmp, [ev("friction.log", {"description": "half a rich entry"})])
    result = hw_verify.verify(tmp, None)
    if result["result"] != "FAIL":
        return (False, f"expected FAIL, got {result['result']}")
    return expect_failures(result["malformed_payloads"], 1, ["friction.log", "note"])


@case("the docs state the one-step protocol and the four-in-130 evidence")
def _(tmp):
    harness = (HERE.parent / "HARNESS.md").read_text(encoding="utf-8")
    substrate = (HERE.parent / "core" / "SUBSTRATE.md").read_text(encoding="utf-8")
    checks = [
        ("The protocol (one step)" in harness, "HARNESS.md one-step heading"),
        ("130 events" in harness, "HARNESS.md field evidence"),
        ("130 events" in substrate, "SUBSTRATE.md field evidence"),
        ("later, optional" in harness and "later, optional" in substrate,
         "promotion is later and optional"),
    ]
    bad = [label for ok, label in checks if not ok]
    return (not bad, f"docs missing {bad}")


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
