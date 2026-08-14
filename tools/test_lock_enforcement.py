#!/usr/bin/env python3
"""
test_lock_enforcement.py — regression test for the v6.0.0 Lock enforcement check
in tools/hw-verify.py (core/VERIFICATION.md §Layer 1 check 15,
core/LOCK.md §The Switch Protocol).

The field incident this pins: `project.activate` was appended for a second
project with no preceding `project.park` / `project.archive` of the active one.
LOCK.md promises the harness refuses exactly this ("<old-project> is still
active. Run `hw park` or `hw wrap` first") but the promise was prose, so nothing
refused and two projects were structurally active at once.

Covers:
  - bootstrap (first activate in a chain) is legal
  - activate -> park -> activate and activate -> archive -> activate are legal
  - activate -> activate (different project) FAILs, naming both projects
  - re-activating the already-active project is legal (`hw bootstrap --resume`)
  - park/archive of a NON-active project does not release the Lock
  - `_harness`-scoped meta events never move the Lock
  - payload.project_id wins over the event's `project` field
  - one missing park is one failure, not a cascade
  - `project.wrap` accepted as an alias for the release `hw wrap` performs
  - active_project() reports the Lock holder at the end of the chain

Stdlib only; no pytest dependency, mirroring tools/test_checked_claims.py's
harness pattern (importlib-loads hw-verify.py; each case returns ok + detail).

Usage:  python tools/test_lock_enforcement.py
Exits 0 if all cases pass, 1 otherwise.
"""

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HW_VERIFY_PATH = HERE / "hw-verify.py"

spec = importlib.util.spec_from_file_location("hw_verify", HW_VERIFY_PATH)
hw_verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hw_verify)

check_lock_enforcement = hw_verify.check_lock_enforcement
active_project = hw_verify.active_project
lock_target = hw_verify.lock_target

_next_id = [0]


def reset_ids():
    _next_id[0] = 0


def ev(kind: str, project: str, payload: dict | None = None,
       project_id: str | None = "same") -> dict:
    """Minimal synthetic event.

    `project_id` defaults to mirroring `project` in the payload (what a real
    Lock event carries); pass None to omit it, or an explicit string to make the
    payload and the event scope disagree.
    """
    _next_id[0] += 1
    body = dict(payload or {})
    if project_id == "same":
        body.setdefault("project_id", project)
    elif project_id is not None:
        body["project_id"] = project_id
    return {
        "id": f"EV-{_next_id[0]:04d}",
        "actor": "planner",
        "project": project,
        "kind": kind,
        "payload": body,
    }


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
# Legal sequences
# ---------------------------------------------------------------------------

@case("bootstrap: first activate with nothing active -> no failures")
def _():
    reset_ids()
    return expect_clean(check_lock_enforcement([ev("project.activate", "alpha")]))


@case("activate -> park -> activate (the switch protocol) -> no failures")
def _():
    reset_ids()
    events = [
        ev("project.activate", "alpha"),
        ev("project.park", "alpha", {"reason": "operator stepped away"}),
        ev("project.activate", "beta"),
    ]
    return expect_clean(check_lock_enforcement(events))


@case("activate -> archive -> activate (hw wrap then bootstrap) -> no failures")
def _():
    reset_ids()
    events = [
        ev("project.activate", "alpha"),
        ev("project.archive", "alpha", {"summary": "done"}),
        ev("project.activate", "beta"),
    ]
    return expect_clean(check_lock_enforcement(events))


@case("re-activating the already-active project (hw bootstrap --resume) -> no failures")
def _():
    reset_ids()
    events = [
        ev("project.activate", "alpha"),
        ev("task.status", "alpha"),
        ev("project.activate", "alpha"),
    ]
    return expect_clean(check_lock_enforcement(events))


@case("park -> resume across four projects in sequence -> no failures")
def _():
    reset_ids()
    events = []
    for name in ("alpha", "beta", "gamma", "delta"):
        events.append(ev("project.activate", name))
        events.append(ev("project.park", name, {"reason": "rotating"}))
    return expect_clean(check_lock_enforcement(events))


@case("project.wrap accepted as a release alias -> no failures")
def _():
    reset_ids()
    events = [
        ev("project.activate", "alpha"),
        ev("project.wrap", "alpha", {"summary": "done"}),
        ev("project.activate", "beta"),
    ]
    return expect_clean(check_lock_enforcement(events))


@case("_harness meta events between activates do not move the Lock -> no failures")
def _():
    reset_ids()
    events = [
        ev("project.activate", "alpha"),
        ev("toolchain.anchor", "_harness", {"source": "shipped"}, project_id=None),
        ev("friction.log", "_harness", {"severity": "non-blocking"}, project_id=None),
        ev("project.park", "alpha", {"reason": "pause"}),
        ev("project.activate", "beta"),
    ]
    return expect_clean(check_lock_enforcement(events))


@case("_harness-scoped activate naming no project is skipped, not treated as a lock")
def _():
    reset_ids()
    events = [
        ev("project.activate", "_harness", project_id=None),
        ev("project.activate", "alpha"),
    ]
    return expect_clean(check_lock_enforcement(events))


@case("no Lock events at all -> no failures")
def _():
    reset_ids()
    events = [ev("task.create", "alpha", {"task_id": "T-001"}),
              ev("finding.add", "alpha", {"artifact_id": "F-001"})]
    return expect_clean(check_lock_enforcement(events))


# ---------------------------------------------------------------------------
# Violations
# ---------------------------------------------------------------------------

@case("the field incident: activate beta while alpha is active -> FAIL")
def _():
    reset_ids()
    events = [
        ev("project.activate", "alpha"),
        ev("task.create", "alpha", {"task_id": "T-001"}),
        ev("project.activate", "beta"),
    ]
    return expect_failures(
        check_lock_enforcement(events), 1,
        ["lock_activate_without_release", "'alpha'", "'beta'", "EV-0003", "EV-0001"],
    )


@case("archive of a DIFFERENT project does not release the Lock -> FAIL")
def _():
    reset_ids()
    events = [
        ev("project.activate", "alpha"),
        ev("project.archive", "stale-other", {"summary": "cleanup"}),
        ev("project.activate", "beta"),
    ]
    return expect_failures(check_lock_enforcement(events), 1,
                           ["lock_activate_without_release"])


@case("park arriving AFTER the second activate does not excuse it -> FAIL")
def _():
    reset_ids()
    events = [
        ev("project.activate", "alpha"),
        ev("project.activate", "beta"),
        ev("project.park", "alpha", {"reason": "noticed late"}),
    ]
    return expect_failures(check_lock_enforcement(events), 1,
                           ["lock_activate_without_release"])


@case("payload.project_id wins over the event scope -> FAIL")
def _():
    reset_ids()
    events = [
        ev("project.activate", "_harness", project_id="alpha"),
        ev("project.activate", "_harness", project_id="beta"),
    ]
    return expect_failures(check_lock_enforcement(events), 1, ["'alpha'", "'beta'"])


@case("one missing park is one failure, not a cascade")
def _():
    reset_ids()
    events = [
        ev("project.activate", "alpha"),
        ev("project.activate", "beta"),   # the violation
        ev("project.park", "beta", {"reason": "pause"}),
        ev("project.activate", "gamma"),  # legal: beta was released
    ]
    return expect_failures(check_lock_enforcement(events), 1, ["'beta'"])


@case("three concurrent activates -> two failures")
def _():
    reset_ids()
    events = [
        ev("project.activate", "alpha"),
        ev("project.activate", "beta"),
        ev("project.activate", "gamma"),
    ]
    return expect_failures(check_lock_enforcement(events), 2,
                           ["'alpha'", "'beta'", "'gamma'"])


# ---------------------------------------------------------------------------
# active_project() helper
# ---------------------------------------------------------------------------

@case("active_project(): reports the Lock holder at the end of the chain")
def _():
    reset_ids()
    checks = [
        (active_project([]) is None, "empty chain"),
        (active_project([ev("project.activate", "alpha")]) == "alpha", "one activate"),
        (active_project([ev("project.activate", "alpha"),
                         ev("project.park", "alpha", {"reason": "x"})]) is None,
         "activate then park"),
        (active_project([ev("project.activate", "alpha"),
                         ev("project.archive", "alpha", {"summary": "x"}),
                         ev("project.activate", "beta")]) == "beta",
         "archive then activate"),
        (active_project([ev("project.activate", "alpha"),
                         ev("project.park", "other", {"reason": "x"})]) == "alpha",
         "park of a non-active project"),
        (lock_target(ev("toolchain.anchor", "_harness", project_id=None)) is None,
         "harness meta event"),
    ]
    bad = [label for ok, label in checks if not ok]
    return (not bad, f"active_project mismatched on {bad}")


def main() -> int:
    failures = 0
    for name, fn in CASES:
        try:
            ok, detail = fn()
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
