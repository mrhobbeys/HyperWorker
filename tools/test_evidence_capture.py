#!/usr/bin/env python3
"""
test_evidence_capture.py — regression test for the v6.0.0 `evidence.capture`
checks in tools/hw-verify.py (core/VERIFICATION.md §Layer 1 check 20,
core/SUBSTRATE.md §Evidence Capture).

Field evidence: across a ten-week deployment the raw command outputs and error
codes that conclusions rested on survived only where a human hand-copied them
into a side ledger. `evidence.capture` keeps the bytes on the log.

Covers: ED-id well-formedness and uniqueness across the whole log (not per
project, because citations carry no project qualifier); the exactly-one-content-
form rule (inline `content` XOR `content_path` + `content_sha256`); the required
payload fields; event-kind registration; and end-to-end dispatch through
verify().

Stdlib only; no pytest dependency, mirroring tools/test_checked_claims.py's
harness pattern (importlib-loads hw-verify.py).

Usage:  python tools/test_evidence_capture.py
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

check_evidence_capture = hw_verify.check_evidence_capture
captured_evidence_ids = hw_verify.captured_evidence_ids

PROJECT = "recovery"

_next_id = [0]


def reset_ids():
    _next_id[0] = 0


def ev(kind: str, payload: dict | None = None, project: str = PROJECT) -> dict:
    _next_id[0] += 1
    return {"id": f"EV-{_next_id[0]:04d}", "actor": "executor:T-004",
            "project": project, "kind": kind, "payload": dict(payload or {})}


def capture(evidence_id: str = "ED-001", project: str = PROJECT, **overrides) -> dict:
    payload = {
        "id": evidence_id,
        "producing_command": "python -c 'import app.loader'",
        "captured_at": "2026-08-01T12:00:00Z",
        "content": "Traceback (most recent call last):\n  ImportError: no module named x\n",
        "summary": "the loader import fails before the handler is reached",
    }
    payload.update(overrides)
    for key in [k for k, v in payload.items() if v is _OMIT]:
        del payload[key]
    return ev("evidence.capture", payload, project)


class _Omit:
    pass


_OMIT = _Omit()


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
# Well-formed captures
# ---------------------------------------------------------------------------

@case("inline-content capture -> no failures")
def _(tmp):
    reset_ids()
    return expect_clean(check_evidence_capture([capture("ED-001")]))


@case("path-form capture with a sha256 -> no failures")
def _(tmp):
    reset_ids()
    events = [capture("ED-002", content=_OMIT,
                      content_path="projects/recovery/evidence/raw/ED-002.log",
                      content_sha256="a" * 64)]
    return expect_clean(check_evidence_capture(events))


@case("empty inline content is still content (an empty output is a result)")
def _(tmp):
    reset_ids()
    return expect_clean(check_evidence_capture([capture("ED-003", content="")]))


@case("several distinct captures across two projects -> no failures")
def _(tmp):
    reset_ids()
    events = [capture("ED-001", "alpha"), capture("ED-002", "beta"),
              capture("ED-003", "alpha")]
    return expect_clean(check_evidence_capture(events))


@case("a chain with no evidence.capture events at all -> no failures")
def _(tmp):
    reset_ids()
    events = [ev("task.create", {"task_id": "T-001"}), ev("task.status", {})]
    return expect_clean(check_evidence_capture(events))


@case("four-digit ED ids are legal (ids grow past 999)")
def _(tmp):
    reset_ids()
    return expect_clean(check_evidence_capture([capture("ED-1042")]))


# ---------------------------------------------------------------------------
# ID well-formedness and uniqueness
# ---------------------------------------------------------------------------

@case("id missing entirely -> evidence_id_malformed")
def _(tmp):
    reset_ids()
    return expect_failures(check_evidence_capture([capture(_OMIT)]), 1,
                           ["evidence_id_malformed", "EV-0001"])


@case("id in the wrong shape -> evidence_id_malformed")
def _(tmp):
    reset_ids()
    return expect_failures(check_evidence_capture([capture("EV-0007")]), 1,
                           ["evidence_id_malformed"])


@case("id with too few digits -> evidence_id_malformed")
def _(tmp):
    reset_ids()
    return expect_failures(check_evidence_capture([capture("ED-7")]), 1,
                           ["evidence_id_malformed"])


@case("same ED id twice -> duplicate_evidence_id naming both events")
def _(tmp):
    reset_ids()
    events = [capture("ED-005"), capture("ED-005")]
    return expect_failures(check_evidence_capture(events), 1,
                           ["duplicate_evidence_id", "ED-005", "EV-0001", "EV-0002"])


@case("ED ids are unique across the log, not per project")
def _(tmp):
    reset_ids()
    events = [capture("ED-005", "alpha"), capture("ED-005", "beta")]
    return expect_failures(check_evidence_capture(events), 1,
                           ["duplicate_evidence_id"])


@case("three captures under one id -> two duplicate failures, not a cascade")
def _(tmp):
    reset_ids()
    events = [capture("ED-005"), capture("ED-005"), capture("ED-005")]
    return expect_failures(check_evidence_capture(events), 2,
                           ["duplicate_evidence_id"])


# ---------------------------------------------------------------------------
# Content form
# ---------------------------------------------------------------------------

@case("neither content nor content_path -> evidence_capture_no_content")
def _(tmp):
    reset_ids()
    return expect_failures(check_evidence_capture([capture("ED-006", content=_OMIT)]), 1,
                           ["evidence_capture_no_content", "ED-006"])


@case("both inline content and content_path -> evidence_capture_content_ambiguous")
def _(tmp):
    reset_ids()
    events = [capture("ED-007", content_path="evidence/raw/ED-007.log",
                      content_sha256="b" * 64)]
    return expect_failures(check_evidence_capture(events), 1,
                           ["evidence_capture_content_ambiguous", "ED-007"])


@case("content_path with no content_sha256 -> evidence_capture_path_without_hash")
def _(tmp):
    reset_ids()
    events = [capture("ED-008", content=_OMIT,
                      content_path="evidence/raw/ED-008.log")]
    return expect_failures(check_evidence_capture(events), 1,
                           ["evidence_capture_path_without_hash", "ED-008"])


@case("empty content_path is not a path -> evidence_capture_no_content")
def _(tmp):
    reset_ids()
    events = [capture("ED-009", content=_OMIT, content_path="")]
    return expect_failures(check_evidence_capture(events), 1,
                           ["evidence_capture_no_content"])


@case("a malformed id and a missing content report both problems")
def _(tmp):
    reset_ids()
    return expect_failures(check_evidence_capture([capture("nope", content=_OMIT)]), 2,
                           ["evidence_id_malformed", "evidence_capture_no_content"])


# ---------------------------------------------------------------------------
# captured_evidence_ids (the set exclusion discipline resolves test_ref against)
# ---------------------------------------------------------------------------

@case("captured_evidence_ids collects well-formed ids and drops malformed ones")
def _(tmp):
    reset_ids()
    events = [capture("ED-001"), capture("ED-002"), capture("nope"),
              ev("task.complete", {"task_id": "T-001"})]
    got = captured_evidence_ids(events)
    return (got == {"ED-001", "ED-002"}, f"expected ED-001/ED-002, got {sorted(got)}")


# ---------------------------------------------------------------------------
# Event-kind registration and end-to-end dispatch
# ---------------------------------------------------------------------------

@case("evidence.capture is a known kind with its required payload fields")
def _(tmp):
    required = hw_verify.REQUIRED_PAYLOAD_FIELDS.get("evidence.capture", ())
    checks = [
        ("evidence.capture" in hw_verify.KNOWN_EVENT_KINDS, "kind known"),
        ("id" in required, "id required"),
        ("producing_command" in required, "producing_command required"),
        ("captured_at" in required, "captured_at required"),
        ("summary" in required, "summary required"),
        ("evidence" in hw_verify.ARTIFACT_DIRS, "evidence/ scanned as a projection dir"),
    ]
    bad = [label for ok, label in checks if not ok]
    return (not bad, f"registration mismatched on {bad}")


@case("end to end: verify() FAILs a workspace with a duplicate ED id")
def _(tmp):
    reset_ids()
    events = [capture("ED-001"), capture("ED-001")]
    write_chain(tmp, events)
    result = hw_verify.verify(tmp, None)
    if result["result"] != "FAIL":
        return (False, f"expected FAIL, got {result['result']}")
    return expect_failures(result["evidence_capture_failures"], 1,
                           ["duplicate_evidence_id"])


@case("end to end: verify() PASSes a workspace of clean captures")
def _(tmp):
    reset_ids()
    write_chain(tmp, [capture("ED-001"), capture("ED-002")])
    result = hw_verify.verify(tmp, None)
    return (result["result"] == "PASS" and result["evidence_capture_failures"] == [],
            f"expected PASS with no evidence failures, got {result['result']} "
            f"{result['evidence_capture_failures']}")


@case("end to end: a capture missing summary is reported as a malformed payload")
def _(tmp):
    reset_ids()
    write_chain(tmp, [capture("ED-001", summary=_OMIT)])
    result = hw_verify.verify(tmp, None)
    blob = " | ".join(result["malformed_payloads"])
    return ("summary" in blob and "evidence.capture" in blob,
            f"expected a malformed-payload report naming summary, got {blob!r}")


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
