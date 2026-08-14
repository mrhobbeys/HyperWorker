#!/usr/bin/env python3
"""
test_execution_profile.py — regression test for `profile: single-executor`
(v6.0.0, H-S12) in tools/hw-verify.py (core/SUBSTRATE.md §Execution Profile,
core/VERIFICATION.md §Layer 1 profile note).

Covers:
  - find_project_profile precedence: schema.yaml wins over PROJECT.md,
    PROJECT.md's `## Profile` section and inline form, unknown -> multi-actor
  - check_actor_requirement: `actor` required under multi-actor, optional
    (defaults to `executor`) under single-executor
  - bare citation ids (`F-012`, no `#hash`) are legal and do not read as broken
    citations, while hashed citations keep verifying exactly as before
  - end to end: verify() FAILs a multi-actor chain missing `actor` and PASSes
    the same chain once the project declares single-executor

Stdlib only, no pytest, importlib-loads hw-verify.py — same harness pattern as
tools/test_checked_claims.py.

Usage:  python tools/test_execution_profile.py
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

find_project_profile = hw_verify.find_project_profile
check_actor_requirement = hw_verify.check_actor_requirement

PROJECT = "demo-project"
SCHEMA = "demo-schema"
_OMIT = object()

_next_id = [0]


def reset_ids():
    _next_id[0] = 0


def ev(kind: str, payload: dict, actor=_OMIT, project: str = PROJECT) -> dict:
    _next_id[0] += 1
    event = {
        "id": f"EV-{_next_id[0]:04d}",
        "project": project,
        "kind": kind,
        "payload": payload,
    }
    if actor is not _OMIT:
        event["actor"] = actor
    return event


def write_project_md(tmp: Path, body: str = "", project: str = PROJECT,
                     schema: str = SCHEMA):
    proj_dir = tmp / "projects" / project
    proj_dir.mkdir(parents=True, exist_ok=True)
    (proj_dir / "PROJECT.md").write_text(
        f"# PROJECT - {project}\n\n## Schema\n\n"
        f"Bootstrapped from `schemas/projects/{schema}/`.\n\n{body}",
        encoding="utf-8",
    )


def write_schema_yaml(tmp: Path, body: str, schema: str = SCHEMA):
    schema_dir = tmp / "schemas" / "projects" / schema
    schema_dir.mkdir(parents=True, exist_ok=True)
    (schema_dir / "schema.yaml").write_text(body, encoding="utf-8")


def write_chain(tmp: Path, events: list):
    """Write a hash-chained events.jsonl so verify() sees an intact chain.

    Unlike the other suites' helpers this one carries `actor` only when the
    event has one — the whole point of the profile is that it may be absent.
    """
    hw_dir = tmp / ".hyperworker"
    hw_dir.mkdir(parents=True, exist_ok=True)
    lines = []
    prev = "sha256:" + hw_verify.ZERO_HASH
    for event in events:
        full = {"id": event["id"], "ts": "2026-08-01T12:00:00Z", "kind": event["kind"],
                "project": event["project"], "payload": event["payload"],
                "prev_hash": prev}
        if "actor" in event:
            full["actor"] = event["actor"]
        full["hash"] = "sha256:" + hw_verify.event_hash(full)
        prev = full["hash"]
        lines.append(json.dumps(full, sort_keys=True, separators=(",", ":"),
                                ensure_ascii=False))
    (hw_dir / "events.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (hw_dir / "hashes.json").write_text("{}", encoding="utf-8")


CASES = []


def case(name):
    def register(fn):
        CASES.append((name, fn))
        return fn
    return register


# ---------------------------------------------------------------------------
# find_project_profile — where the declaration lives, and who wins
# ---------------------------------------------------------------------------

@case("no declaration anywhere -> multi-actor (the documented default)")
def _(tmp):
    write_project_md(tmp)
    got = find_project_profile(tmp, PROJECT)
    return (got == "multi-actor", f"expected multi-actor, got {got!r}")


@case("no PROJECT.md at all -> multi-actor")
def _(tmp):
    got = find_project_profile(tmp, PROJECT)
    return (got == "multi-actor", f"expected multi-actor, got {got!r}")


@case("PROJECT.md ## Profile section is read")
def _(tmp):
    write_project_md(tmp, "## Profile\n\nsingle-executor\n")
    got = find_project_profile(tmp, PROJECT)
    return (got == "single-executor", f"expected single-executor, got {got!r}")


@case("PROJECT.md inline `profile:` declaration is read")
def _(tmp):
    write_project_md(tmp, "This project runs profile: single-executor throughout.\n")
    got = find_project_profile(tmp, PROJECT)
    return (got == "single-executor", f"expected single-executor, got {got!r}")


@case("PROJECT.md may declare multi-actor explicitly")
def _(tmp):
    write_project_md(tmp, "## Profile\n\nmulti-actor\n")
    got = find_project_profile(tmp, PROJECT)
    return (got == "multi-actor", f"expected multi-actor, got {got!r}")


@case("an unsubstituted {{ profile }} placeholder reads as the default")
def _(tmp):
    write_project_md(tmp, "## Profile\n\n{{ profile }}\n")
    got = find_project_profile(tmp, PROJECT)
    return (got == "multi-actor", f"expected multi-actor, got {got!r}")


@case("an unsubstituted <choice | menu> placeholder reads as the default")
def _(tmp):
    write_project_md(tmp, "## Profile\n\n<multi-actor | single-executor - default "
                          "`multi-actor`. See core/SUBSTRATE.md.>\n")
    got = find_project_profile(tmp, PROJECT)
    return (got == "multi-actor", f"expected multi-actor, got {got!r}")


@case("the shipped project-template, uncustomized, reads as the default")
def _(tmp):
    template = (HERE.parent / "templates" / "project-template.md").read_text(encoding="utf-8")
    proj_dir = tmp / "projects" / PROJECT
    proj_dir.mkdir(parents=True, exist_ok=True)
    (proj_dir / "PROJECT.md").write_text(template, encoding="utf-8")
    got = find_project_profile(tmp, PROJECT)
    return (got == "multi-actor", f"expected multi-actor, got {got!r}")


@case("schema.yaml profile is read")
def _(tmp):
    write_project_md(tmp)
    write_schema_yaml(tmp, 'name: demo-schema\nprofile: "single-executor"\n')
    got = find_project_profile(tmp, PROJECT)
    return (got == "single-executor", f"expected single-executor, got {got!r}")


@case("schema.yaml WINS over PROJECT.md")
def _(tmp):
    write_project_md(tmp, "## Profile\n\nsingle-executor\n")
    write_schema_yaml(tmp, "name: demo-schema\nprofile: multi-actor\n")
    got = find_project_profile(tmp, PROJECT)
    return (got == "multi-actor", f"expected schema to win with multi-actor, got {got!r}")


@case("schema.yaml with no profile key falls through to PROJECT.md")
def _(tmp):
    write_project_md(tmp, "## Profile\n\nsingle-executor\n")
    write_schema_yaml(tmp, 'name: demo-schema\nharness_version: "6.0.0"\n')
    got = find_project_profile(tmp, PROJECT)
    return (got == "single-executor", f"expected single-executor, got {got!r}")


@case("_harness-scoped events resolve to the default profile")
def _(tmp):
    got = find_project_profile(tmp, "_harness")
    return (got == "multi-actor", f"expected multi-actor, got {got!r}")


@case("the profile vocabulary is exactly two values")
def _(tmp):
    return (set(hw_verify.PROFILES) == {"multi-actor", "single-executor"}
            and hw_verify.DEFAULT_PROFILE == "multi-actor",
            f"unexpected vocabulary {hw_verify.PROFILES} / {hw_verify.DEFAULT_PROFILE}")


# ---------------------------------------------------------------------------
# check_actor_requirement — the one relaxation
# ---------------------------------------------------------------------------

@case("multi-actor: a missing actor is a defect")
def _(tmp):
    reset_ids()
    write_project_md(tmp)
    failures, notes = check_actor_requirement(tmp, [ev("task.complete", {"task_id": "T-001"})])
    ok = len(failures) == 1 and "missing ['actor']" in failures[0] and notes == []
    return (ok, f"expected one actor failure and no notes, got {failures} / {notes}")


@case("multi-actor: an empty actor string is a defect")
def _(tmp):
    reset_ids()
    write_project_md(tmp)
    failures, _ = check_actor_requirement(tmp, [ev("task.complete", {"task_id": "T-001"}, actor="  ")])
    return (len(failures) == 1, f"expected one actor failure, got {failures}")


@case("multi-actor: actors present -> no failures")
def _(tmp):
    reset_ids()
    write_project_md(tmp)
    events = [ev("task.complete", {"task_id": "T-001"}, actor="executor:T-001"),
              ev("decision.add", {"artifact_id": "DEC-001"}, actor="operator")]
    failures, notes = check_actor_requirement(tmp, events)
    return (failures == [] and notes == [], f"expected clean, got {failures} / {notes}")


@case("single-executor: a missing actor is NOT a defect")
def _(tmp):
    reset_ids()
    write_project_md(tmp, "## Profile\n\nsingle-executor\n")
    failures, _ = check_actor_requirement(tmp, [ev("task.complete", {"task_id": "T-001"})])
    return (failures == [], f"expected no failures, got {failures}")


@case("single-executor: the relaxation is reported once per project, as a note")
def _(tmp):
    reset_ids()
    write_project_md(tmp, "## Profile\n\nsingle-executor\n")
    events = [ev("task.complete", {"task_id": "T-001"}),
              ev("task.complete", {"task_id": "T-002"}),
              ev("finding.add", {"id": "F-001"})]
    failures, notes = check_actor_requirement(tmp, events)
    ok = (failures == [] and len(notes) == 1
          and "profile_single_executor" in notes[0] and PROJECT in notes[0])
    return (ok, f"expected one note and no failures, got {failures} / {notes}")


@case("single-executor: an explicit actor is still allowed")
def _(tmp):
    reset_ids()
    write_project_md(tmp, "## Profile\n\nsingle-executor\n")
    failures, _ = check_actor_requirement(
        tmp, [ev("task.complete", {"task_id": "T-001"}, actor="executor:T-001")])
    return (failures == [], f"expected no failures, got {failures}")


@case("profiles are per project: one relaxed, one not")
def _(tmp):
    reset_ids()
    write_project_md(tmp, "## Profile\n\nsingle-executor\n", project="solo",
                     schema="solo-schema")
    write_project_md(tmp, project="crew", schema="crew-schema")
    events = [ev("task.complete", {"task_id": "T-001"}, project="solo"),
              ev("task.complete", {"task_id": "T-002"}, project="crew")]
    failures, notes = check_actor_requirement(tmp, events)
    ok = (len(failures) == 1 and "crew" in failures[0]
          and len(notes) == 1 and "solo" in notes[0])
    return (ok, f"expected crew to fail and solo to note, got {failures} / {notes}")


@case("single-executor declared by the schema relaxes the same way")
def _(tmp):
    reset_ids()
    write_project_md(tmp)
    write_schema_yaml(tmp, "name: demo-schema\nprofile: single-executor\n")
    failures, notes = check_actor_requirement(tmp, [ev("task.complete", {"task_id": "T-001"})])
    return (failures == [] and len(notes) == 1,
            f"expected no failures and one note, got {failures} / {notes}")


# ---------------------------------------------------------------------------
# Citation ceremony — bare ids under single-executor, hashes unchanged
# ---------------------------------------------------------------------------

@case("a bare citation id (F-012, no #hash) is not read as a citation at all")
def _(tmp):
    found = hw_verify.collect_citations({"body": "consumed F-012 and DEC-007"})
    return (found == [], f"expected no citations parsed, got {found}")


@case("end to end: bare ids under single-executor produce no broken citations")
def _(tmp):
    reset_ids()
    write_project_md(tmp, "## Profile\n\nsingle-executor\n")
    write_chain(tmp, [ev("finding.add", {"id": "F-013", "evidence": "supersedes F-012; see DEC-007"})])
    result = hw_verify.verify(tmp, None)
    ok = (result["result"] == "PASS" and result["broken_citations"] == []
          and result["stale_citations"] == [])
    return (ok, f"expected a clean PASS, got {result['result']} "
                f"{result['broken_citations']} {result['stale_citations']}")


@case("end to end: a hashed citation to a missing artifact still breaks")
def _(tmp):
    reset_ids()
    write_project_md(tmp, "## Profile\n\nsingle-executor\n")
    write_chain(tmp, [ev("finding.add", {"id": "F-013", "evidence": "see [F-012#b8d4e1779a02]"})])
    result = hw_verify.verify(tmp, None)
    ok = result["result"] == "FAIL" and len(result["broken_citations"]) == 1
    return (ok, f"expected one broken citation, got {result['result']} "
                f"{result['broken_citations']}")


# ---------------------------------------------------------------------------
# End to end
# ---------------------------------------------------------------------------

@case("end to end: multi-actor chain missing actor FAILs as a malformed payload")
def _(tmp):
    reset_ids()
    write_project_md(tmp)
    write_chain(tmp, [ev("task.complete", {"task_id": "T-001"})])
    result = hw_verify.verify(tmp, None)
    blob = " | ".join(result["malformed_payloads"])
    return (result["result"] == "FAIL" and "actor" in blob,
            f"expected FAIL naming actor, got {result['result']} {blob!r}")


@case("end to end: the same chain PASSes once the project declares single-executor")
def _(tmp):
    reset_ids()
    write_project_md(tmp, "## Profile\n\nsingle-executor\n")
    write_chain(tmp, [ev("task.complete", {"task_id": "T-001"}),
                      ev("finding.add", {"id": "F-001"})])
    result = hw_verify.verify(tmp, None)
    ok = (result["result"] == "PASS" and result["malformed_payloads"] == []
          and len(result["profile_notes"]) == 1)
    return (ok, f"expected PASS with one profile note, got {result['result']} "
                f"{result['malformed_payloads']} {result['profile_notes']}")


@case("end to end: a multi-actor chain that carries actors is unaffected")
def _(tmp):
    reset_ids()
    write_project_md(tmp)
    write_chain(tmp, [ev("task.complete", {"task_id": "T-001"}, actor="executor:T-001")])
    result = hw_verify.verify(tmp, None)
    ok = (result["result"] == "PASS" and result["malformed_payloads"] == []
          and result["profile_notes"] == [])
    return (ok, f"expected an unchanged PASS, got {result['result']} "
                f"{result['malformed_payloads']} {result['profile_notes']}")


@case("end to end: single-executor does not disable any other Layer 1 check")
def _(tmp):
    reset_ids()
    write_project_md(tmp, "## Profile\n\nsingle-executor\n")
    # A loop closed with no matching open: check 21 must still FAIL.
    write_chain(tmp, [ev("loop.close", {"loop_id": "L-001", "closed_at": "2026-08-01",
                                         "resolution": "done"})])
    result = hw_verify.verify(tmp, None)
    ok = result["result"] == "FAIL" and len(result["open_loop_failures"]) == 1
    return (ok, f"expected the open-loop FAIL to survive, got {result['result']} "
                f"{result['open_loop_failures']}")


@case("render() carries a profile_notes row")
def _(tmp):
    reset_ids()
    write_project_md(tmp, "## Profile\n\nsingle-executor\n")
    write_chain(tmp, [ev("task.complete", {"task_id": "T-001"})])
    text = hw_verify.render(hw_verify.verify(tmp, None))
    return ("profile_notes:" in text and "profile_single_executor" in text,
            f"expected a profile_notes row, got:\n{text}")


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
