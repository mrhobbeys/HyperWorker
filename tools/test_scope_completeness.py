#!/usr/bin/env python3
"""
test_scope_completeness.py — regression test for check_scope_completeness()
in tools/hw-verify.py.

Covers the FL-024 field bug: the check anchored on `handoff_indices[-1]` and
only ever looked *backward* from the last `session.handoff` for a preceding
`scope.complete`. A legitimate retroactive fix-run that appends a
`scope.complete` event *after* a prior `session.handoff` (with no newer
handoff following it yet) produced a structural false-positive FAIL, even
though the scope-completeness obligation was satisfied.

This script builds minimal synthetic event sequences (in a throwaway temp
workspace) exercising every ordering called out in the bug report and asserts
the check's pass/fail verdict for each. Stdlib only; no pytest dependency.

Usage:  python tools/test_scope_completeness.py
Exits 0 if all cases pass, 1 otherwise.
"""

import importlib.util
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
HW_VERIFY_PATH = HERE / "hw-verify.py"

spec = importlib.util.spec_from_file_location("hw_verify", HW_VERIFY_PATH)
hw_verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hw_verify)

check_scope_completeness = hw_verify.check_scope_completeness

PROJECT = "demo-project"

_next_id = [0]


def reset_ids():
    _next_id[0] = 0


def ev(kind: str, project: str = PROJECT, scope_items=None) -> dict:
    """Build a minimal synthetic event. Only the fields check_scope_completeness
    (and the helpers it calls) touch are populated."""
    _next_id[0] += 1
    event = {
        "id": f"EV-{_next_id[0]:04d}",
        "project": project,
        "kind": kind,
        "payload": {},
    }
    if kind == "scope.complete":
        event["payload"]["scope_items"] = scope_items if scope_items is not None else []
    return event


CASES = []


def case(name):
    def register(fn):
        CASES.append((name, fn))
        return fn
    return register


@case("no handoffs at all -> no failures")
def _(workspace):
    reset_ids()
    events = [
        ev("task.create"),
        ev("task.complete"),
    ]
    return check_scope_completeness(workspace, events)


@case("handoff with no scope.complete anywhere -> FAIL")
def _(workspace):
    reset_ids()
    events = [
        ev("task.create"),
        ev("session.handoff"),
    ]
    return check_scope_completeness(workspace, events)


@case("scope.complete precedes handoff (classic ordering) -> no failures")
def _(workspace):
    reset_ids()
    events = [
        ev("task.create"),
        ev("scope.complete"),
        ev("session.handoff"),
    ]
    return check_scope_completeness(workspace, events)


@case("multiple handoff/scope.complete pairs, each preceded -> no failures")
def _(workspace):
    reset_ids()
    events = [
        ev("scope.complete"),
        ev("session.handoff"),
        ev("task.create"),
        ev("scope.complete"),
        ev("session.handoff"),
    ]
    return check_scope_completeness(workspace, events)


@case("FL-024: trailing scope.complete after last handoff, no prior -> no failures")
def _(workspace):
    reset_ids()
    events = [
        ev("task.create"),
        ev("session.handoff"),
        ev("scope.complete"),  # retroactive fix-run, no subsequent handoff
    ]
    return check_scope_completeness(workspace, events)


@case("multiple trailing scope.completes after last handoff -> no failures")
def _(workspace):
    reset_ids()
    events = [
        ev("task.create"),
        ev("session.handoff"),
        ev("scope.complete"),  # first fix attempt
        ev("scope.complete"),  # second, corrected fix attempt (most recent wins)
    ]
    return check_scope_completeness(workspace, events)


@case("any scope.complete preceding the last handoff satisfies it (pre-existing, unchanged) -> no failures")
def _(workspace):
    # Not part of the FL-024 fix: the check has never required the preceding
    # scope.complete to be "fresh" relative to an intervening handoff — it
    # only requires that *some* scope.complete precede the last handoff. This
    # case pins that pre-existing behavior so the trailing-anchor fix above
    # doesn't accidentally tighten (or loosen) it.
    reset_ids()
    events = [
        ev("session.handoff"),
        ev("scope.complete"),   # retroactive fix for the first handoff
        ev("session.handoff"),  # a second handoff; a scope.complete still precedes it
    ]
    return check_scope_completeness(workspace, events)


def main() -> int:
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        workspace = Path(tmp)
        for name, fn in CASES:
            result = fn(workspace)
            expect_fail = name.rstrip().endswith("FAIL")
            got_fail = len(result) > 0
            status = "ok" if got_fail == expect_fail else "MISMATCH"
            if status == "MISMATCH":
                failures += 1
            print(f"[{status}] {name}")
            print(f"         -> failures={result}")

    print()
    if failures:
        print(f"{failures} case(s) FAILED")
        return 1
    print(f"All {len(CASES)} case(s) passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
