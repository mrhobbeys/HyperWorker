#!/usr/bin/env python3
"""
test_exclusion_discipline.py — regression test for the v6.0.0 exclusion-discipline
check in tools/hw-verify.py (core/VERIFICATION.md §Layer 1 check 19,
core/SUBSTRATE.md §Exclusion Discipline).

Field evidence: AP-008, the most expensive failure of a ten-week deployment. The
true root cause was struck off the hypothesis list on the strength of a
well-argued STATIC read, and ~19 attempts were burned before anyone revisited it.
The rule that follows: a hypothesis may be marked `excluded` only with a
`test_ref` naming a dynamic test that exercised the actual code path -- an
evidence.capture id or a checked-claim predicate. Static reads mark `suspect`.

Covers: the three failure codes (`excluded_without_test_ref`,
`excluded_test_ref_unresolved`, `invalid_hypothesis_status`); both resolution
routes for a test_ref; the scoping rule that keeps the program pack's
`workstream.add` `status` field out of this check; and end-to-end dispatch.

Stdlib only; no pytest dependency, mirroring tools/test_checked_claims.py's
harness pattern (importlib-loads hw-verify.py).

Usage:  python tools/test_exclusion_discipline.py
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

check_exclusion_discipline = hw_verify.check_exclusion_discipline
hypothesis_entries = hw_verify.hypothesis_entries

PROJECT = "recovery"

_next_id = [0]


class _Omit:
    pass


_OMIT = _Omit()


def reset_ids():
    _next_id[0] = 0


def ev(kind: str, payload: dict | None = None, project: str = PROJECT) -> dict:
    _next_id[0] += 1
    return {"id": f"EV-{_next_id[0]:04d}", "actor": "executor:T-004",
            "project": project, "kind": kind, "payload": dict(payload or {})}


def hypothesis(artifact_id: str = "F-012", status: str = "open",
               test_ref=_OMIT, kind: str = "finding.add", **extra) -> dict:
    payload = {
        "id": artifact_id,
        "created_at": "2026-08-01T12:00:00Z",
        "title": "the retry wrapper swallows the timeout",
        "evidence": "Ran the path; the handler was reached and returned 200.",
        "applies_to": "app/retry.py",
        "confidence": "provisional",
        "tags": [],
        "status": status,
    }
    if test_ref is not _OMIT:
        payload["test_ref"] = test_ref
    if status is _OMIT:
        del payload["status"]
    payload.update(extra)
    return ev(kind, payload)


def capture(evidence_id: str = "ED-001") -> dict:
    return ev("evidence.capture", {
        "id": evidence_id,
        "producing_command": "curl -sS http://localhost:8080/health",
        "captured_at": "2026-08-01T11:30:00Z",
        "content": "HTTP/1.1 200 OK\n",
        "summary": "the handler was reached on the live path",
    })


def claim_block(passed: bool = True) -> dict:
    return {"predicate": {"file_exists": "app/retry.py"},
            "checked_at": "2026-08-01T12:00:00Z", "passed": passed}


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
# Legal hypothesis states
# ---------------------------------------------------------------------------

@case("status open with no test_ref -> no failures")
def _(tmp):
    reset_ids()
    return expect_clean(check_exclusion_discipline([hypothesis("F-012", "open")]))


@case("status suspect with no test_ref -> no failures (where a static read lands)")
def _(tmp):
    reset_ids()
    return expect_clean(check_exclusion_discipline([hypothesis("F-013", "suspect")]))


@case("suspect with a prose note in test_ref -> no failures (only excluded is gated)")
def _(tmp):
    reset_ids()
    events = [hypothesis("F-013", "suspect", test_ref="read the wrapper, looks wrong")]
    return expect_clean(check_exclusion_discipline(events))


@case("excluded citing an evidence.capture in the chain -> no failures")
def _(tmp):
    reset_ids()
    events = [capture("ED-001"), hypothesis("F-012", "excluded", test_ref="ED-001")]
    return expect_clean(check_exclusion_discipline(events))


@case("excluded citing a capture with a prose note around the id -> no failures")
def _(tmp):
    reset_ids()
    events = [capture("ED-014"),
              hypothesis("F-012", "excluded",
                         test_ref="ED-014 - ran the import against the live path")]
    return expect_clean(check_exclusion_discipline(events))


@case("excluded citing two captures, both present -> no failures")
def _(tmp):
    reset_ids()
    events = [capture("ED-001"), capture("ED-002"),
              hypothesis("F-012", "excluded", test_ref="ED-001 and ED-002")]
    return expect_clean(check_exclusion_discipline(events))


@case("excluded on a claim: predicate recorded on the same event -> no failures")
def _(tmp):
    reset_ids()
    events = [hypothesis("F-012", "excluded",
                         test_ref="claim: file_exists app/retry.py",
                         claim=claim_block())]
    return expect_clean(check_exclusion_discipline(events))


@case("a capture appended after the exclusion still resolves (convergence-writer order)")
def _(tmp):
    reset_ids()
    events = [hypothesis("F-012", "excluded", test_ref="ED-001"), capture("ED-001")]
    return expect_clean(check_exclusion_discipline(events))


@case("a finding with no status at all -> not a hypothesis, no failures")
def _(tmp):
    reset_ids()
    return expect_clean(check_exclusion_discipline([hypothesis("F-020", _OMIT)]))


@case("an empty chain -> no failures")
def _(tmp):
    reset_ids()
    return expect_clean(check_exclusion_discipline([]))


# ---------------------------------------------------------------------------
# excluded_without_test_ref -- the AP-008 failure itself
# ---------------------------------------------------------------------------

@case("excluded with no test_ref at all -> excluded_without_test_ref")
def _(tmp):
    reset_ids()
    return expect_failures(check_exclusion_discipline([hypothesis("F-012", "excluded")]),
                           1, ["excluded_without_test_ref", "F-012", "EV-0001"])


@case("excluded with test_ref: null -> excluded_without_test_ref")
def _(tmp):
    reset_ids()
    events = [hypothesis("F-012", "excluded", test_ref=None)]
    return expect_failures(check_exclusion_discipline(events), 1,
                           ["excluded_without_test_ref"])


@case("excluded with a whitespace test_ref -> excluded_without_test_ref")
def _(tmp):
    reset_ids()
    events = [hypothesis("F-012", "excluded", test_ref="   ")]
    return expect_failures(check_exclusion_discipline(events), 1,
                           ["excluded_without_test_ref"])


@case("excluded on a well-argued static read -> excluded_without_test_ref")
def _(tmp):
    reset_ids()
    events = [hypothesis("F-012", "excluded",
                         test_ref="read the whole call path; it cannot reach here")]
    return expect_failures(check_exclusion_discipline(events), 1,
                           ["excluded_without_test_ref", "prose reasoning is not a test"])


@case("excluded with a malformed claim: block and no ED id -> excluded_without_test_ref")
def _(tmp):
    reset_ids()
    events = [hypothesis("F-012", "excluded", test_ref="checked it",
                         claim={"predicate": {}, "passed": True})]
    return expect_failures(check_exclusion_discipline(events), 1,
                           ["excluded_without_test_ref"])


@case("a claim: block that ran and failed still counts as a dynamic test")
def _(tmp):
    reset_ids()
    events = [hypothesis("F-012", "excluded", test_ref="claim predicate",
                         claim=claim_block(passed=False))]
    return expect_clean(check_exclusion_discipline(events))


@case("two untested exclusions -> two failures, one per hypothesis")
def _(tmp):
    reset_ids()
    events = [hypothesis("F-012", "excluded"), hypothesis("F-013", "excluded")]
    return expect_failures(check_exclusion_discipline(events), 2,
                           ["F-012", "F-013"])


# ---------------------------------------------------------------------------
# excluded_test_ref_unresolved
# ---------------------------------------------------------------------------

@case("excluded citing an ED id no capture produced -> excluded_test_ref_unresolved")
def _(tmp):
    reset_ids()
    events = [hypothesis("F-012", "excluded", test_ref="ED-014")]
    return expect_failures(check_exclusion_discipline(events), 1,
                           ["excluded_test_ref_unresolved", "ED-014"])


@case("excluded citing one present and one absent capture -> names only the absent one")
def _(tmp):
    reset_ids()
    events = [capture("ED-001"),
              hypothesis("F-012", "excluded", test_ref="ED-001 and ED-099")]
    ok, detail = expect_failures(check_exclusion_discipline(events), 1,
                                 ["excluded_test_ref_unresolved", "ED-099"])
    if not ok:
        return (ok, detail)
    return ("ED-001" not in check_exclusion_discipline(events)[0].split("cites")[1],
            "the resolved capture should not be reported as missing")


@case("a malformed capture id does not resolve a citation -> unresolved")
def _(tmp):
    reset_ids()
    events = [ev("evidence.capture", {"id": "ED-1", "producing_command": "x",
                                      "captured_at": "2026-08-01T00:00:00Z",
                                      "content": "", "summary": "s"}),
              hypothesis("F-012", "excluded", test_ref="ED-001")]
    return expect_failures(check_exclusion_discipline(events), 1,
                           ["excluded_test_ref_unresolved", "ED-001"])


@case("a test_ref shaped like ED-1 is not a capture citation -> without_test_ref")
def _(tmp):
    reset_ids()
    events = [hypothesis("F-012", "excluded", test_ref="ED-1")]
    return expect_failures(check_exclusion_discipline(events), 1,
                           ["excluded_without_test_ref"])


# ---------------------------------------------------------------------------
# invalid_hypothesis_status
# ---------------------------------------------------------------------------

@case("a status outside the enum -> invalid_hypothesis_status")
def _(tmp):
    reset_ids()
    return expect_failures(check_exclusion_discipline([hypothesis("F-012", "ruled-out")]),
                           1, ["invalid_hypothesis_status", "ruled-out"])


@case("a non-string status -> invalid_hypothesis_status")
def _(tmp):
    reset_ids()
    return expect_failures(check_exclusion_discipline([hypothesis("F-012", True)]),
                           1, ["invalid_hypothesis_status"])


@case("an invalid status is reported once, not also as a missing test_ref")
def _(tmp):
    reset_ids()
    return expect_failures(check_exclusion_discipline([hypothesis("F-012", "EXCLUDED")]),
                           1, ["invalid_hypothesis_status"])


# ---------------------------------------------------------------------------
# Scoping -- what the check must NOT read as a hypothesis
# ---------------------------------------------------------------------------

@case("workstream.add status: active is not a hypothesis status")
def _(tmp):
    reset_ids()
    events = [ev("workstream.add", {"id": "WS-001", "status": "active"})]
    return expect_clean(check_exclusion_discipline(events))


@case("a non-finding .add that opts in with test_ref IS checked")
def _(tmp):
    reset_ids()
    events = [hypothesis("HYP-003", "excluded", kind="hypothesis.add", test_ref="")]
    return expect_failures(check_exclusion_discipline(events), 1,
                           ["excluded_without_test_ref", "HYP-003"])


@case("hypothesis state nested under frontmatter: is read")
def _(tmp):
    reset_ids()
    events = [ev("finding.add", {"artifact_id": "F-030",
                                 "frontmatter": {"id": "F-030", "status": "excluded"}})]
    return expect_failures(check_exclusion_discipline(events), 1,
                           ["excluded_without_test_ref", "F-030"])


@case("non-.add kinds are never read as hypotheses")
def _(tmp):
    reset_ids()
    events = [ev("task.status", {"task_id": "T-001", "status": "excluded"})]
    return expect_clean(check_exclusion_discipline(events))


@case("hypothesis_entries picks up finding.add and test_ref opt-ins only")
def _(tmp):
    reset_ids()
    events = [hypothesis("F-012", "suspect"),
              ev("workstream.add", {"id": "WS-001", "status": "active"}),
              ev("decision.add", {"id": "DEC-001", "test_ref": "ED-001"}),
              ev("task.create", {"task_id": "T-001", "status": "open"})]
    got = [fields.get("id") for _, fields in hypothesis_entries(events)]
    return (got == ["F-012", "DEC-001"], f"expected [F-012, DEC-001], got {got}")


# ---------------------------------------------------------------------------
# Schema and end-to-end dispatch
# ---------------------------------------------------------------------------

@case("finding.yaml declares status, test_ref and the exclusion rule")
def _(tmp):
    text = (HERE.parent / "schemas" / "artifacts" / "finding.yaml").read_text(encoding="utf-8")
    checks = [
        ("name: status" in text, "status field"),
        ("name: test_ref" in text, "test_ref field"),
        ("[open, suspect, excluded]" in text, "status enum"),
        ("exclusion_rule:" in text, "exclusion_rule block"),
        ("- status\n  - test_ref" in text, "render_order carries both"),
    ]
    bad = [label for ok, label in checks if not ok]
    return (not bad, f"finding.yaml missing {bad}")


@case("templates/ELIMINATION.md ships with a frontier line and the matrix columns")
def _(tmp):
    text = (HERE.parent / "templates" / "ELIMINATION.md").read_text(encoding="utf-8")
    checks = [
        ("**Frontier:**" in text, "frontier line"),
        ("| Hypothesis | Status | How tested (test_ref) | Result |" in text, "matrix header"),
        ("Rendering protocol" in text, "rendering protocol"),
        ("excluded_without_test_ref" in text, "names the failure code"),
    ]
    bad = [label for ok, label in checks if not ok]
    return (not bad, f"ELIMINATION.md missing {bad}")


@case("end to end: verify() FAILs a workspace with an untested exclusion")
def _(tmp):
    reset_ids()
    write_chain(tmp, [hypothesis("F-012", "excluded")])
    result = hw_verify.verify(tmp, None)
    if result["result"] != "FAIL":
        return (False, f"expected FAIL, got {result['result']}")
    return expect_failures(result["exclusion_failures"], 1, ["excluded_without_test_ref"])


@case("end to end: verify() PASSes an exclusion backed by a capture")
def _(tmp):
    reset_ids()
    write_chain(tmp, [capture("ED-001"),
                      hypothesis("F-012", "excluded", test_ref="ED-001")])
    result = hw_verify.verify(tmp, None)
    return (result["result"] == "PASS" and result["exclusion_failures"] == [],
            f"expected PASS with no exclusion failures, got {result['result']} "
            f"{result['exclusion_failures']}")


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
