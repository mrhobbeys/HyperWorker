#!/usr/bin/env python3
"""
test_cycle_lifecycle.py — regression test for the v6.0.0 cycle-lifecycle checks
in tools/hw-verify.py (core/VERIFICATION.md §Layer 1 check 17,
core/SUBSTRATE.md §Lifecycle events / §`hw cycle`, core/LOCK.md §Ongoing Projects).

v5.3 specified four cycle failures and shipped none of them:

  - `cycle.close` with no matching open        -> cycle_close_without_open
  - a second `cycle.open` with no close between -> cycle_open_without_close
  - either kind on a `lifecycle: terminal` project -> cycle_on_terminal_lifecycle
  - `project.archive` (hw wrap) with a cycle open  -> wrap_with_open_cycle

Covers those, plus: matching is by cycle_id when both events carry one; a
mispaired close is one failure rather than a cascade; parking with an open cycle
is legal (an ongoing project parks and resumes like any other); lifecycle is read
from PROJECT.md with an unsubstituted template placeholder treated as unknown;
and the required-payload-field entries the two kinds gained.

Stdlib only; no pytest dependency, mirroring tools/test_checked_claims.py's
harness pattern (importlib-loads hw-verify.py).

Usage:  python tools/test_cycle_lifecycle.py
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

check_cycle_lifecycle = hw_verify.check_cycle_lifecycle
find_project_lifecycle = hw_verify.find_project_lifecycle

PROJECT = "weekly-sweep"

_next_id = [0]


def reset_ids():
    _next_id[0] = 0


def ev(kind: str, payload: dict | None = None, project: str = PROJECT) -> dict:
    _next_id[0] += 1
    return {"id": f"EV-{_next_id[0]:04d}", "actor": "planner", "project": project,
            "kind": kind, "payload": dict(payload or {})}


def cycle_open(cycle_id: str = "C-001", project: str = PROJECT) -> dict:
    return ev("cycle.open", {"project_id": project, "cycle_id": cycle_id,
                             "opened_at": "2026-08-01T00:00:00Z",
                             "cadence": "weekly", "cadence_days": 7}, project)


def cycle_close(cycle_id: str = "C-001", project: str = PROJECT) -> dict:
    return ev("cycle.close", {"project_id": project, "cycle_id": cycle_id,
                              "closed_at": "2026-08-08T00:00:00Z",
                              "summary": "swept", "next_due": "2026-08-15"}, project)


def write_project_md(tmp: Path, lifecycle: str | None, project: str = PROJECT):
    """Write a PROJECT.md. `lifecycle=None` omits the section entirely."""
    proj_dir = tmp / "projects" / project
    proj_dir.mkdir(parents=True, exist_ok=True)
    text = f"# PROJECT - {project}\n\n## Status\n\nactive\n"
    if lifecycle is not None:
        text += f"\n## Lifecycle\n\n{lifecycle}\n\n**Cadence:** weekly\n"
    text += "\n## Objective\n\nSweep the segments every week.\n"
    (proj_dir / "PROJECT.md").write_text(text, encoding="utf-8")


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
# Legal cycle sequences
# ---------------------------------------------------------------------------

@case("open -> close -> open -> close on an ongoing project -> no failures")
def _(tmp):
    reset_ids()
    write_project_md(tmp, "ongoing")
    events = [cycle_open("C-001"), cycle_close("C-001"),
              cycle_open("C-002"), cycle_close("C-002")]
    return expect_clean(check_cycle_lifecycle(tmp, events))


@case("an open cycle at the end of the chain is legal (work in flight)")
def _(tmp):
    reset_ids()
    write_project_md(tmp, "ongoing")
    events = [cycle_open("C-001"), cycle_close("C-001"), cycle_open("C-002")]
    return expect_clean(check_cycle_lifecycle(tmp, events))


@case("parking with an open cycle is legal (ongoing projects park and resume)")
def _(tmp):
    reset_ids()
    write_project_md(tmp, "ongoing")
    events = [cycle_open("C-001"),
              ev("project.park", {"project_id": PROJECT, "reason": "operator away"})]
    return expect_clean(check_cycle_lifecycle(tmp, events))


@case("archive after the cycle is closed -> no failures")
def _(tmp):
    reset_ids()
    write_project_md(tmp, "ongoing")
    events = [cycle_open("C-001"), cycle_close("C-001"),
              ev("project.archive", {"project_id": PROJECT, "summary": "need ended"})]
    return expect_clean(check_cycle_lifecycle(tmp, events))


@case("no cycle events at all -> no failures (and PROJECT.md is never read)")
def _(tmp):
    reset_ids()
    # No PROJECT.md written: a terminal project with no cycles must not trip.
    events = [ev("task.create", {"task_id": "T-001"}),
              ev("project.archive", {"project_id": PROJECT, "summary": "done"})]
    return expect_clean(check_cycle_lifecycle(tmp, events))


@case("cycles on one project do not leak into another project's pairing")
def _(tmp):
    reset_ids()
    write_project_md(tmp, "ongoing", "alpha")
    write_project_md(tmp, "ongoing", "beta")
    events = [
        cycle_open("C-001", "alpha"),
        cycle_open("C-001", "beta"),      # different project: not a double open
        cycle_close("C-001", "alpha"),
        cycle_close("C-001", "beta"),
    ]
    return expect_clean(check_cycle_lifecycle(tmp, events))


# ---------------------------------------------------------------------------
# Pairing failures
# ---------------------------------------------------------------------------

@case("close with no open at all -> cycle_close_without_open")
def _(tmp):
    reset_ids()
    write_project_md(tmp, "ongoing")
    return expect_failures(check_cycle_lifecycle(tmp, [cycle_close("C-001")]), 1,
                           ["cycle_close_without_open", "C-001", "EV-0001"])


@case("close after the cycle was already closed -> cycle_close_without_open")
def _(tmp):
    reset_ids()
    write_project_md(tmp, "ongoing")
    events = [cycle_open("C-001"), cycle_close("C-001"), cycle_close("C-001")]
    return expect_failures(check_cycle_lifecycle(tmp, events), 1,
                           ["cycle_close_without_open"])


@case("close naming a different cycle than the open one -> cycle_close_without_open")
def _(tmp):
    reset_ids()
    write_project_md(tmp, "ongoing")
    events = [cycle_open("C-003"), cycle_close("C-002")]
    return expect_failures(check_cycle_lifecycle(tmp, events), 1,
                           ["cycle_close_without_open", "C-002", "C-003"])


@case("two opens with no close between -> cycle_open_without_close")
def _(tmp):
    reset_ids()
    write_project_md(tmp, "ongoing")
    events = [cycle_open("C-001"), cycle_open("C-002")]
    return expect_failures(check_cycle_lifecycle(tmp, events), 1,
                           ["cycle_open_without_close", "C-001", "C-002"])


@case("three opens with no closes -> two failures, not a cascade")
def _(tmp):
    reset_ids()
    write_project_md(tmp, "ongoing")
    events = [cycle_open("C-001"), cycle_open("C-002"), cycle_open("C-003")]
    return expect_failures(check_cycle_lifecycle(tmp, events), 2,
                           ["cycle_open_without_close"])


@case("a mispaired close still closes the cycle -> one failure, not two")
def _(tmp):
    reset_ids()
    write_project_md(tmp, "ongoing")
    events = [cycle_open("C-001"), cycle_close("C-002"), cycle_open("C-003")]
    return expect_failures(check_cycle_lifecycle(tmp, events), 1,
                           ["cycle_close_without_open"])


# ---------------------------------------------------------------------------
# Terminal lifecycle
# ---------------------------------------------------------------------------

@case("cycle.open on an explicitly terminal project -> cycle_on_terminal_lifecycle")
def _(tmp):
    reset_ids()
    write_project_md(tmp, "terminal")
    return expect_failures(check_cycle_lifecycle(tmp, [cycle_open("C-001")]), 1,
                           ["cycle_on_terminal_lifecycle", "EV-0001"])


@case("cycle.open + cycle.close on a terminal project -> two failures")
def _(tmp):
    reset_ids()
    write_project_md(tmp, "terminal")
    events = [cycle_open("C-001"), cycle_close("C-001")]
    return expect_failures(check_cycle_lifecycle(tmp, events), 2,
                           ["cycle_on_terminal_lifecycle"])


@case("PROJECT.md with no Lifecycle section defaults to terminal -> FAIL")
def _(tmp):
    reset_ids()
    write_project_md(tmp, None)
    return expect_failures(check_cycle_lifecycle(tmp, [cycle_open("C-001")]), 1,
                           ["cycle_on_terminal_lifecycle"])


@case("no PROJECT.md at all -> lifecycle unknown, terminal check stands down")
def _(tmp):
    reset_ids()
    events = [cycle_open("C-001"), cycle_close("C-001")]
    return expect_clean(check_cycle_lifecycle(tmp, events))


@case("unsubstituted {{ lifecycle }} placeholder -> unknown, check stands down")
def _(tmp):
    reset_ids()
    write_project_md(tmp, "{{ lifecycle }}")
    return expect_clean(check_cycle_lifecycle(tmp, [cycle_open("C-001")]))


@case("find_project_lifecycle reads section, inline form, default and unknown")
def _(tmp):
    checks = []
    write_project_md(tmp, "ongoing", "p-ongoing")
    checks.append((find_project_lifecycle(tmp, "p-ongoing") == "ongoing", "section ongoing"))
    write_project_md(tmp, "terminal", "p-terminal")
    checks.append((find_project_lifecycle(tmp, "p-terminal") == "terminal", "section terminal"))
    write_project_md(tmp, None, "p-default")
    checks.append((find_project_lifecycle(tmp, "p-default") == "terminal", "default terminal"))
    checks.append((find_project_lifecycle(tmp, "p-missing") is None, "no PROJECT.md"))

    proj = tmp / "projects" / "p-inline"
    proj.mkdir(parents=True, exist_ok=True)
    (proj / "PROJECT.md").write_text(
        "# PROJECT - p-inline\n\nfrontmatter says lifecycle: ongoing here\n",
        encoding="utf-8")
    checks.append((find_project_lifecycle(tmp, "p-inline") == "ongoing", "inline form"))

    bad = [label for ok, label in checks if not ok]
    return (not bad, f"find_project_lifecycle mismatched on {bad}")


# ---------------------------------------------------------------------------
# Wrap with an open cycle
# ---------------------------------------------------------------------------

@case("project.archive with an open cycle -> wrap_with_open_cycle")
def _(tmp):
    reset_ids()
    write_project_md(tmp, "ongoing")
    events = [cycle_open("C-004"),
              ev("project.archive", {"project_id": PROJECT, "summary": "done"})]
    return expect_failures(check_cycle_lifecycle(tmp, events), 1,
                           ["wrap_with_open_cycle", "C-004", "EV-0002"])


@case("project.wrap alias with an open cycle -> wrap_with_open_cycle")
def _(tmp):
    reset_ids()
    write_project_md(tmp, "ongoing")
    events = [cycle_open("C-004"),
              ev("project.wrap", {"project_id": PROJECT, "summary": "done"})]
    return expect_failures(check_cycle_lifecycle(tmp, events), 1,
                           ["wrap_with_open_cycle"])


@case("archive with an open cycle reports once, then the slot is clear")
def _(tmp):
    reset_ids()
    write_project_md(tmp, "ongoing")
    events = [cycle_open("C-004"),
              ev("project.archive", {"project_id": PROJECT, "summary": "done"}),
              cycle_open("C-005")]   # legal after the archive cleared the slot
    return expect_failures(check_cycle_lifecycle(tmp, events), 1,
                           ["wrap_with_open_cycle"])


# ---------------------------------------------------------------------------
# Event-kind registration
# ---------------------------------------------------------------------------

@case("cycle.open / cycle.close are known kinds with required payload fields")
def _(tmp):
    known = hw_verify.KNOWN_EVENT_KINDS
    required = hw_verify.REQUIRED_PAYLOAD_FIELDS
    checks = [
        ("cycle.open" in known, "cycle.open known"),
        ("cycle.close" in known, "cycle.close known"),
        ("next_due" in required.get("cycle.close", ()), "next_due required on close"),
        ("cadence" in required.get("cycle.open", ()), "cadence required on open"),
        ("cycle_id" in required.get("cycle.open", ()), "cycle_id required on open"),
    ]
    bad = [label for ok, label in checks if not ok]
    return (not bad, f"event-kind registration mismatched on {bad}")


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
