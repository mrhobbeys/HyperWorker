#!/usr/bin/env python3
"""
test_checked_claims.py — regression test for the v5.3 checked-claims primitive
in tools/hw-verify.py (core/SUBSTRATE.md §Checked Claims, core/VERIFICATION.md
§Layer 1 check 13 and §Claim Replay).

Covers:
  - structural validation of `claim:` blocks (well-formed vs malformed predicate)
  - schema-required-claim enforcement via verification.yaml `checked_claims.required_for`
    (missing claim fails; present + passing does not; risk-level-scoped patterns)
  - `--claims` replay: file_exists (true/false), file_sha256 (match/mismatch),
    cmd_exit skip behavior without --allow-cmd

Stdlib + PyYAML only (PyYAML used only to sanity-check the fixture YAML this
script hand-writes is itself valid YAML; hw-verify.py's own parser stays
dependency-free, matched separately). No pytest dependency, mirroring
tools/test_scope_completeness.py's harness pattern (importlib-loads hw-verify.py).

Usage:  python tools/test_checked_claims.py
Exits 0 if all cases pass, 1 otherwise.
"""

import importlib.util
import sys
import tempfile
from pathlib import Path

try:
    import yaml  # noqa: F401  (sanity-check only; see module docstring)
    _HAVE_YAML = True
except ImportError:  # pragma: no cover - environment without pyyaml
    _HAVE_YAML = False

HERE = Path(__file__).resolve().parent
HW_VERIFY_PATH = HERE / "hw-verify.py"

spec = importlib.util.spec_from_file_location("hw_verify", HW_VERIFY_PATH)
hw_verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hw_verify)

check_claims_structural = hw_verify.check_claims_structural
check_claims_required = hw_verify.check_claims_required
replay_claims = hw_verify.replay_claims
validate_claim_block = hw_verify.validate_claim_block

PROJECT = "demo-project"
SCHEMA = "demo-schema"

_next_id = [0]


def reset_ids():
    _next_id[0] = 0


def ev(kind: str, payload: dict, project: str = PROJECT) -> dict:
    _next_id[0] += 1
    return {
        "id": f"EV-{_next_id[0]:04d}",
        "project": project,
        "kind": kind,
        "payload": payload,
    }


def good_claim(predicate: dict, passed: bool = True) -> dict:
    return {
        "predicate": predicate,
        "checked_at": "2026-07-13T00:00:00Z",
        "passed": passed,
    }


def write_verification_yaml(tmp: Path, required_for_lines: str, schema: str = SCHEMA):
    """Write a minimal verification.yaml declaring checked_claims.required_for,
    using the same indented-block-list convention shipped verification.yaml /
    capability-gates.yaml files already use for `required_for:` (see
    schemas/projects/marketing-campaign/capability-gates.yaml external_state_readback).
    """
    schema_dir = tmp / "schemas" / "projects" / schema
    schema_dir.mkdir(parents=True, exist_ok=True)
    text = "checked_claims:\n  required_for:\n" + required_for_lines
    (schema_dir / "verification.yaml").write_text(text, encoding="utf-8")
    if _HAVE_YAML:
        # Sanity-check the fixture is valid YAML (independent of hw-verify.py's
        # own dependency-free parser, which is what's actually under test).
        parsed = yaml.safe_load(text)
        assert "checked_claims" in parsed and "required_for" in parsed["checked_claims"]


def write_project_md(tmp: Path, project: str = PROJECT, schema: str = SCHEMA):
    proj_dir = tmp / "projects" / project
    proj_dir.mkdir(parents=True, exist_ok=True)
    (proj_dir / "PROJECT.md").write_text(
        f"# PROJECT — {project}\n\nBootstrapped from `schemas/projects/{schema}/`.\n",
        encoding="utf-8",
    )


CASES = []


def case(name):
    def register(fn):
        CASES.append((name, fn))
        return fn
    return register


# ---------------------------------------------------------------------------
# Structural validation (check_claims_structural)
# ---------------------------------------------------------------------------

@case("well-formed claim (file_exists) passes structural check")
def _(tmp):
    reset_ids()
    claim = good_claim({"file_exists": "output/report.md"})
    events = [ev("finding.add", {"id": "F-001", "claim": claim})]
    result = check_claims_structural(events)
    return (result == [], f"expected [], got {result}")


@case("well-formed claim (file_sha256) passes structural check")
def _(tmp):
    reset_ids()
    claim = good_claim({"file_sha256": {"path": "out.bin", "hash": "a" * 64}})
    events = [ev("task.complete", {"task_id": "T-001", "claim": claim})]
    result = check_claims_structural(events)
    return (result == [], f"expected [], got {result}")


@case("malformed predicate kind fails structural check")
def _(tmp):
    reset_ids()
    claim = good_claim({"not_a_real_kind": "x"})
    events = [ev("finding.add", {"id": "F-001", "claim": claim})]
    result = check_claims_structural(events)
    return (len(result) == 1, f"expected 1 failure, got {result}")


@case("predicate with two keys fails structural check")
def _(tmp):
    reset_ids()
    claim = good_claim({"file_exists": "a.txt", "file_absent": "b.txt"})
    events = [ev("finding.add", {"id": "F-001", "claim": claim})]
    result = check_claims_structural(events)
    return (len(result) == 1, f"expected 1 failure, got {result}")


@case("absolute path in file_exists fails structural check")
def _(tmp):
    reset_ids()
    claim = good_claim({"file_exists": "/etc/passwd"})
    events = [ev("finding.add", {"id": "F-001", "claim": claim})]
    result = check_claims_structural(events)
    return (len(result) == 1, f"expected 1 failure, got {result}")


@case("claim missing checked_at fails structural check")
def _(tmp):
    reset_ids()
    claim = {"predicate": {"file_exists": "a.txt"}, "passed": True}
    events = [ev("finding.add", {"id": "F-001", "claim": claim})]
    result = check_claims_structural(events)
    return (len(result) == 1, f"expected 1 failure, got {result}")


@case("claim missing passed fails structural check")
def _(tmp):
    reset_ids()
    claim = {"predicate": {"file_exists": "a.txt"}, "checked_at": "2026-07-13T00:00:00Z"}
    events = [ev("finding.add", {"id": "F-001", "claim": claim})]
    result = check_claims_structural(events)
    return (len(result) == 1, f"expected 1 failure, got {result}")


@case("no claim block at all -> no structural failures (never required by default)")
def _(tmp):
    reset_ids()
    events = [ev("finding.add", {"id": "F-001"}), ev("task.complete", {"task_id": "T-001"})]
    result = check_claims_structural(events)
    return (result == [], f"expected [], got {result}")


@case("well-formed claim on a scope.complete scope_items[] entry passes")
def _(tmp):
    reset_ids()
    claim = good_claim({"file_absent": "old/deprecated.txt"})
    events = [ev("scope.complete", {"scope_items": [
        {"id": "T-001", "name": "thing", "terminal_state": "complete", "claim": claim},
    ]})]
    result = check_claims_structural(events)
    return (result == [], f"expected [], got {result}")


@case("malformed claim on a scope.complete scope_items[] entry fails")
def _(tmp):
    reset_ids()
    claim = {"predicate": {"file_absent": "x"}, "checked_at": "2026-07-13T00:00:00Z",
              "passed": "yes"}  # not a bool
    events = [ev("scope.complete", {"scope_items": [
        {"id": "T-001", "name": "thing", "terminal_state": "complete", "claim": claim},
    ]})]
    result = check_claims_structural(events)
    return (len(result) == 1, f"expected 1 failure, got {result}")


# ---------------------------------------------------------------------------
# Schema-required enforcement (check_claims_required)
# ---------------------------------------------------------------------------

@case("schema-required claim missing -> checked_claims_missing")
def _(tmp):
    reset_ids()
    write_project_md(tmp)
    write_verification_yaml(tmp, "    - finding.add\n")
    events = [ev("finding.add", {"id": "F-001"})]
    result = check_claims_required(tmp, events)
    ok = len(result) == 1 and "checked_claims_missing" in result[0]
    return (ok, f"expected one checked_claims_missing failure, got {result}")


@case("schema-required claim present and passing -> no failures")
def _(tmp):
    reset_ids()
    write_project_md(tmp)
    write_verification_yaml(tmp, "    - finding.add\n")
    claim = good_claim({"file_exists": "out.txt"}, passed=True)
    events = [ev("finding.add", {"id": "F-001", "claim": claim})]
    result = check_claims_required(tmp, events)
    return (result == [], f"expected [], got {result}")


@case("schema-required claim present but passed: false -> checked_claims_predicate_failed")
def _(tmp):
    reset_ids()
    write_project_md(tmp)
    write_verification_yaml(tmp, "    - finding.add\n")
    claim = good_claim({"file_exists": "out.txt"}, passed=False)
    events = [ev("finding.add", {"id": "F-001", "claim": claim})]
    result = check_claims_required(tmp, events)
    ok = len(result) == 1 and "checked_claims_predicate_failed" in result[0]
    return (ok, f"expected one checked_claims_predicate_failed failure, got {result}")


@case("no verification.yaml -> requirement off, no failures (graceful degrade)")
def _(tmp):
    reset_ids()
    write_project_md(tmp)
    # No verification.yaml written at all.
    events = [ev("finding.add", {"id": "F-001"})]
    result = check_claims_required(tmp, events)
    return (result == [], f"expected [], got {result}")


@case("event kind not named in required_for -> not enforced")
def _(tmp):
    reset_ids()
    write_project_md(tmp)
    write_verification_yaml(tmp, "    - external_state.read_back\n")
    events = [ev("finding.add", {"id": "F-001"})]  # finding.add not required
    result = check_claims_required(tmp, events)
    return (result == [], f"expected [], got {result}")


@case("risk-level-scoped pattern task.complete:critical enforces only critical tasks")
def _(tmp):
    reset_ids()
    write_project_md(tmp)
    write_verification_yaml(tmp, "    - task.complete:critical\n")
    events = [
        ev("task.create", {"task_id": "T-001", "title": "std",
                            "frontmatter": {"risk_level": "standard"}}),
        ev("task.create", {"task_id": "T-002", "title": "crit",
                            "frontmatter": {"risk_level": "critical"}}),
        ev("task.complete", {"task_id": "T-001"}),          # standard: no claim needed
        ev("task.complete", {"task_id": "T-002"}),          # critical: claim required, missing
    ]
    result = check_claims_required(tmp, events)
    crit_event_id = events[3]["id"]
    ok = len(result) == 1 and crit_event_id in result[0]
    return (ok, f"expected exactly one failure referencing {crit_event_id}, got {result}")


@case("scope.complete required_for enforces every scope_items[] entry")
def _(tmp):
    reset_ids()
    write_project_md(tmp)
    write_verification_yaml(tmp, "    - scope.complete\n")
    passing = good_claim({"file_exists": "a.txt"})
    events = [ev("scope.complete", {"scope_items": [
        {"id": "T-001", "name": "one", "terminal_state": "complete", "claim": passing},
        {"id": "T-002", "name": "two", "terminal_state": "complete"},  # missing claim
    ]})]
    result = check_claims_required(tmp, events)
    ok = len(result) == 1 and "T-002" in result[0]
    return (ok, f"expected one failure referencing T-002, got {result}")


# ---------------------------------------------------------------------------
# --claims replay (replay_claims)
# ---------------------------------------------------------------------------

@case("--claims replay: file_exists true -> pass")
def _(tmp):
    reset_ids()
    (tmp / "present.txt").write_text("hi", encoding="utf-8")
    claim = good_claim({"file_exists": "present.txt"})
    events = [ev("finding.add", {"id": "F-001", "claim": claim})]
    summary = replay_claims(tmp, events, allow_cmd=False)
    ok = summary["result"] == "PASS" and summary["pass"] == 1 and not summary["fail"]
    return (ok, f"expected PASS/1 pass, got {summary}")


@case("--claims replay: file_exists false -> fail")
def _(tmp):
    reset_ids()
    claim = good_claim({"file_exists": "does-not-exist.txt"})
    events = [ev("finding.add", {"id": "F-001", "claim": claim})]
    summary = replay_claims(tmp, events, allow_cmd=False)
    ok = summary["result"] == "FAIL" and len(summary["fail"]) == 1
    return (ok, f"expected FAIL/1 fail, got {summary}")


@case("--claims replay: file_sha256 match -> pass")
def _(tmp):
    reset_ids()
    import hashlib
    data = b"checked-claims fixture bytes"
    (tmp / "artifact.bin").write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    claim = good_claim({"file_sha256": {"path": "artifact.bin", "hash": digest}})
    events = [ev("task.complete", {"task_id": "T-001", "claim": claim})]
    summary = replay_claims(tmp, events, allow_cmd=False)
    ok = summary["result"] == "PASS" and summary["pass"] == 1
    return (ok, f"expected PASS/1 pass, got {summary}")


@case("--claims replay: file_sha256 mismatch -> fail")
def _(tmp):
    reset_ids()
    (tmp / "artifact.bin").write_bytes(b"actual bytes on disk")
    claim = good_claim({"file_sha256": {"path": "artifact.bin", "hash": "b" * 64}})
    events = [ev("task.complete", {"task_id": "T-001", "claim": claim})]
    summary = replay_claims(tmp, events, allow_cmd=False)
    ok = summary["result"] == "FAIL" and len(summary["fail"]) == 1
    return (ok, f"expected FAIL/1 fail, got {summary}")


@case("--claims replay: cmd_exit skipped without --allow-cmd")
def _(tmp):
    reset_ids()
    claim = good_claim({"cmd_exit": {"cmd": "exit 0", "expect_code": 0}})
    events = [ev("task.complete", {"task_id": "T-001", "claim": claim})]
    summary = replay_claims(tmp, events, allow_cmd=False)
    ok = (summary["result"] == "PASS"  # skipped is not a fail
          and summary["pass"] == 0
          and not summary["fail"]
          and len(summary["skipped"]) == 1
          and "shell predicates disabled" in summary["skipped"][0])
    return (ok, f"expected 1 skipped ('shell predicates disabled'), got {summary}")


@case("--claims replay: cmd_exit with --allow-cmd but no schema capability -> still skipped")
def _(tmp):
    reset_ids()
    write_project_md(tmp)  # schema referenced, but no capability-gates.yaml at all
    claim = good_claim({"cmd_exit": {"cmd": "exit 0", "expect_code": 0}})
    events = [ev("task.complete", {"task_id": "T-001", "claim": claim})]
    summary = replay_claims(tmp, events, allow_cmd=True)
    ok = (len(summary["skipped"]) == 1
          and "capability declarations" in summary["skipped"][0])
    return (ok, f"expected 1 skipped ('...capability declarations...'), got {summary}")


@case("--claims replay: malformed claim reported as error, not replayed")
def _(tmp):
    reset_ids()
    claim = {"predicate": {"file_exists": "x"}}  # missing checked_at / passed
    events = [ev("finding.add", {"id": "F-001", "claim": claim})]
    summary = replay_claims(tmp, events, allow_cmd=False)
    ok = len(summary["error"]) == 1 and "malformed" in summary["error"][0]
    return (ok, f"expected 1 error mentioning 'malformed', got {summary}")


@case("--claims replay: no claims recorded anywhere -> N/A")
def _(tmp):
    reset_ids()
    events = [ev("finding.add", {"id": "F-001"}), ev("task.complete", {"task_id": "T-001"})]
    summary = replay_claims(tmp, events, allow_cmd=False)
    return (summary["result"] == "N/A", f"expected N/A, got {summary}")


def main() -> int:
    failures = 0
    for name, fn in CASES:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp = Path(raw_tmp)
            try:
                ok, detail = fn(tmp)
            except Exception as e:  # noqa: BLE001 - surface as a case failure, not a crash
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
