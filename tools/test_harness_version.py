#!/usr/bin/env python3
"""
test_harness_version.py — regression test for the v6.0.0 harness_version gate in
tools/hw-verify.py (core/VERIFICATION.md §Layer 1 check 16, CONTRIBUTING.md §5).

CONTRIBUTING.md §5 has said since v5.1.1 that "the harness MUST refuse to run a
schema whose `harness_version` exceeds the harness's own version." No such check
existed anywhere in the reference verifier. That is how the repo reached a state
where the harness identified as 5.2.1 while the `program` schema declared 5.3.0
and nothing noticed the newest schema was, by the repo's own rule, unrunnable.

Covers:
  - schema newer than the harness -> FAIL with a refusal message
  - schema equal to the harness -> clean
  - schema older than the harness -> note only, never a failure
  - the gate follows the ACTIVE project's schema (parked/archived ones are out)
  - graceful degrade: no active project, no PROJECT.md, no schema dir, no
    schema.yaml, no harness_version key, unparseable version
  - semver comparison across major/minor/patch, short forms, and pre-release tags
  - end-to-end: verify() FAILs and prints the refusal

Stdlib only; no pytest dependency, mirroring tools/test_checked_claims.py's
harness pattern (importlib-loads hw-verify.py).

Usage:  python tools/test_harness_version.py
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

check_harness_version = hw_verify.check_harness_version
compare_semver = hw_verify.compare_semver
parse_semver = hw_verify.parse_semver
parse_schema_harness_version = hw_verify.parse_schema_harness_version
HARNESS_VERSION = hw_verify.HARNESS_VERSION

# One patch level above whatever the harness currently declares. Derived rather
# than written down: this case exists to prove the gate refuses on a patch-level
# difference, and a hardcoded literal silently becomes an "equal" case the first
# time the harness itself ships that patch (it did, at 6.0.1).
_MAJOR, _MINOR, _PATCH = parse_semver(HARNESS_VERSION)
NEXT_PATCH_VERSION = f"{_MAJOR}.{_MINOR}.{_PATCH + 1}"

PROJECT = "demo-project"
SCHEMA = "demo-schema"

_next_id = [0]


def reset_ids():
    _next_id[0] = 0


def ev(kind: str, project: str = PROJECT, payload: dict | None = None) -> dict:
    _next_id[0] += 1
    body = dict(payload or {})
    body.setdefault("project_id", project)
    return {"id": f"EV-{_next_id[0]:04d}", "actor": "planner", "project": project,
            "kind": kind, "payload": body}


def write_project_md(tmp: Path, project: str = PROJECT, schema: str = SCHEMA):
    proj_dir = tmp / "projects" / project
    proj_dir.mkdir(parents=True, exist_ok=True)
    (proj_dir / "PROJECT.md").write_text(
        f"# PROJECT - {project}\n\nBootstrapped from `schemas/projects/{schema}/`.\n",
        encoding="utf-8",
    )


def write_schema_yaml(tmp: Path, harness_version, schema: str = SCHEMA):
    """Write a minimal schema.yaml. `harness_version=None` omits the key."""
    schema_dir = tmp / "schemas" / "projects" / schema
    schema_dir.mkdir(parents=True, exist_ok=True)
    text = f"schema_id: {schema}\nschema_version: 1.0\n"
    if harness_version is not None:
        text += f'harness_version: "{harness_version}"\n'
    text += "description: |\n  A fixture schema.\n"
    (schema_dir / "schema.yaml").write_text(text, encoding="utf-8")


CASES = []


def case(name):
    def register(fn):
        CASES.append((name, fn))
        return fn
    return register


# ---------------------------------------------------------------------------
# The gate
# ---------------------------------------------------------------------------

@case("schema newer than the harness -> FAIL with a refusal message")
def _(tmp):
    reset_ids()
    write_project_md(tmp)
    write_schema_yaml(tmp, "7.0.0")
    failures, notes = check_harness_version(tmp, [ev("project.activate")])
    if len(failures) != 1:
        return (False, f"expected exactly one failure, got {failures}")
    text = failures[0]
    needed = ["harness_version_too_new", "7.0.0", HARNESS_VERSION, "Refusing",
              "CONTRIBUTING.md"]
    missing = [n for n in needed if n not in text]
    return (not missing, f"refusal missing {missing}: {text}")


@case("schema newer by a patch level only -> FAIL")
def _(tmp):
    reset_ids()
    write_project_md(tmp)
    write_schema_yaml(tmp, NEXT_PATCH_VERSION)
    failures, _notes = check_harness_version(tmp, [ev("project.activate")])
    return (len(failures) == 1, f"expected one failure, got {failures}")


@case("schema equal to the harness -> no failures, no notes")
def _(tmp):
    reset_ids()
    write_project_md(tmp)
    write_schema_yaml(tmp, HARNESS_VERSION)
    failures, notes = check_harness_version(tmp, [ev("project.activate")])
    return (failures == [] and notes == [], f"got failures={failures} notes={notes}")


@case("schema older than the harness -> note only, never a failure")
def _(tmp):
    reset_ids()
    write_project_md(tmp)
    write_schema_yaml(tmp, "5.1.1")
    failures, notes = check_harness_version(tmp, [ev("project.activate")])
    ok = failures == [] and len(notes) == 1 and "harness_version_older" in notes[0]
    return (ok, f"expected one note and no failures, got failures={failures} notes={notes}")


# ---------------------------------------------------------------------------
# Scoping: the ACTIVE project's schema
# ---------------------------------------------------------------------------

@case("gate follows the active project, not an archived one")
def _(tmp):
    reset_ids()
    write_project_md(tmp, "old-project", "old-schema")
    write_schema_yaml(tmp, "9.9.9", "old-schema")   # would fail if consulted
    write_project_md(tmp, "new-project", "new-schema")
    write_schema_yaml(tmp, HARNESS_VERSION, "new-schema")
    events = [
        ev("project.activate", "old-project"),
        ev("project.archive", "old-project", {"summary": "done"}),
        ev("project.activate", "new-project"),
    ]
    failures, _notes = check_harness_version(tmp, events)
    return (failures == [], f"expected the archived schema to be out of scope, got {failures}")


@case("gate fires for a parked-then-resumed project that is active again")
def _(tmp):
    reset_ids()
    write_project_md(tmp)
    write_schema_yaml(tmp, "6.1.0")
    events = [
        ev("project.activate"),
        ev("project.park", PROJECT, {"reason": "pause"}),
        ev("project.activate"),
    ]
    failures, _notes = check_harness_version(tmp, events)
    return (len(failures) == 1, f"expected one failure, got {failures}")


@case("no active project (all parked) -> gate does not run")
def _(tmp):
    reset_ids()
    write_project_md(tmp)
    write_schema_yaml(tmp, "9.9.9")
    events = [ev("project.activate"), ev("project.park", PROJECT, {"reason": "x"})]
    failures, notes = check_harness_version(tmp, events)
    return (failures == [] and notes == [], f"got failures={failures} notes={notes}")


@case("no project.activate anywhere -> gate does not run")
def _(tmp):
    reset_ids()
    write_project_md(tmp)
    write_schema_yaml(tmp, "9.9.9")
    failures, notes = check_harness_version(tmp, [ev("task.create")])
    return (failures == [] and notes == [], f"got failures={failures} notes={notes}")


# ---------------------------------------------------------------------------
# Graceful degrade
# ---------------------------------------------------------------------------

@case("no PROJECT.md -> gate does not run (schema unknown)")
def _(tmp):
    reset_ids()
    write_schema_yaml(tmp, "9.9.9")
    failures, notes = check_harness_version(tmp, [ev("project.activate")])
    return (failures == [] and notes == [], f"got failures={failures} notes={notes}")


@case("no schema directory -> gate does not run")
def _(tmp):
    reset_ids()
    write_project_md(tmp)
    failures, notes = check_harness_version(tmp, [ev("project.activate")])
    return (failures == [] and notes == [], f"got failures={failures} notes={notes}")


@case("schema.yaml with no harness_version -> note, not a refusal")
def _(tmp):
    reset_ids()
    write_project_md(tmp)
    write_schema_yaml(tmp, None)
    failures, notes = check_harness_version(tmp, [ev("project.activate")])
    ok = failures == [] and len(notes) == 1 and "harness_version_undeclared" in notes[0]
    return (ok, f"expected one undeclared note, got failures={failures} notes={notes}")


@case("unparseable harness_version -> note, not a refusal")
def _(tmp):
    reset_ids()
    write_project_md(tmp)
    write_schema_yaml(tmp, "next-gen")
    failures, notes = check_harness_version(tmp, [ev("project.activate")])
    ok = failures == [] and len(notes) == 1 and "harness_version_unparseable" in notes[0]
    return (ok, f"expected one unparseable note, got failures={failures} notes={notes}")


@case("schema pack sitting beside the workspace is found too")
def _(tmp):
    reset_ids()
    workspace = tmp / "instance"
    (workspace / "projects").mkdir(parents=True, exist_ok=True)
    write_project_md(workspace)
    write_schema_yaml(tmp, "8.0.0")   # schemas/ one level up from the workspace
    failures, _notes = check_harness_version(workspace, [ev("project.activate")])
    return (len(failures) == 1, f"expected one failure from the sibling pack, got {failures}")


# ---------------------------------------------------------------------------
# Version parsing / comparison
# ---------------------------------------------------------------------------

@case("semver comparison orders major, minor and patch correctly")
def _(tmp):
    checks = [
        (compare_semver("6.0.0", "6.0.0") == 0, "equal"),
        (compare_semver("5.3.0", "6.0.0") < 0, "older major"),
        (compare_semver("6.1.0", "6.0.0") > 0, "newer minor"),
        (compare_semver("6.0.1", "6.0.0") > 0, "newer patch"),
        (compare_semver("10.0.0", "9.0.0") > 0, "double-digit major"),
        (compare_semver("6.0", "6.0.0") == 0, "short form"),
        (compare_semver("6", "6.0.0") == 0, "major only"),
        (compare_semver("6.0.0-rc1", "6.0.0") == 0, "pre-release tag ignored"),
        (compare_semver("v6.1.0", "6.0.0") > 0, "leading v"),
        (compare_semver("next", "6.0.0") is None, "unparseable"),
        (compare_semver(None, "6.0.0") is None, "None"),
        (parse_semver("5.2.1") == (5, 2, 1), "parse tuple"),
    ]
    bad = [label for ok, label in checks if not ok]
    return (not bad, f"semver comparison mismatched on {bad}")


@case("harness_version parsed from quoted, bare and commented declarations")
def _(tmp):
    schema_dir = tmp / "schemas" / "projects" / SCHEMA
    schema_dir.mkdir(parents=True, exist_ok=True)
    path = schema_dir / "schema.yaml"
    cases = [
        ('harness_version: "6.0.0"\n', "6.0.0"),
        ("harness_version: 6.0.0\n", "6.0.0"),
        ("harness_version: '5.2.0'\n", "5.2.0"),
        ("harness_version: 5.3.0   # bumped for checked claims\n", "5.3.0"),
        ("schema_id: x\n", None),
    ]
    bad = []
    for text, expected in cases:
        path.write_text(text, encoding="utf-8")
        got = parse_schema_harness_version(path)
        if got != expected:
            bad.append(f"{text.strip()!r} -> {got!r} (expected {expected!r})")
    return (not bad, f"parse mismatches: {bad}")


@case("the shipped program schema pins to this harness version")
def _(tmp):
    repo_root = HERE.parent
    declared = parse_schema_harness_version(
        repo_root / "schemas" / "projects" / "program" / "schema.yaml")
    ok = declared is not None and compare_semver(declared, HARNESS_VERSION) <= 0
    return (ok, f"program schema declares {declared!r}, harness is {HARNESS_VERSION}")


# ---------------------------------------------------------------------------
# End to end
# ---------------------------------------------------------------------------

@case("verify() FAILs a workspace whose active schema is too new")
def _(tmp):
    reset_ids()
    write_project_md(tmp)
    write_schema_yaml(tmp, "7.0.0")
    hw_dir = tmp / ".hyperworker"
    hw_dir.mkdir(parents=True, exist_ok=True)
    event = {"id": "EV-0001", "ts": "2026-08-14T00:00:00Z", "kind": "project.activate",
             "actor": "planner", "project": PROJECT,
             "payload": {"project_id": PROJECT, "name": PROJECT, "schema": SCHEMA,
                          "started_at": "2026-08-14T00:00:00Z"},
             "prev_hash": hw_verify.ZERO_HASH}
    event["hash"] = hw_verify.event_hash(event)
    (hw_dir / "events.jsonl").write_text(
        json.dumps(event, sort_keys=True, separators=(",", ":"),
                   ensure_ascii=False) + "\n", encoding="utf-8")

    result = hw_verify.verify(tmp, None)
    rendered = hw_verify.render(result)
    ok = (result["result"] == "FAIL"
          and len(result["harness_version_failures"]) == 1
          and "harness_version_too_new" in rendered)
    return (ok, f"expected FAIL on harness_version, got {result}")


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
