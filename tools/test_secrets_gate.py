#!/usr/bin/env python3
"""
test_secrets_gate.py — regression test for the v6.0.0 secrets gate (H-S10) in
tools/hw-verify.py (core/SUBSTRATE.md §Secrets Gate, core/VERIFICATION.md
§Layer 1 check 22).

Covers:
  - scan_for_secrets: assignment, PEM/private key, connection string,
    bearer/vendor-token and high-entropy detectors
  - the false-positive guards that matter most in this harness: the hashes the
    substrate itself requires (event hashes, citations, content_sha256,
    test_ref) and the `[REDACTED-SECRET]` marker the protocol asks for
  - the report never echoes the secret it found
  - check_secrets field-path reporting across nested payloads
  - end to end: WARNING by default (a leaked chain still verifies),
    FAIL under --strict-secrets

Stdlib only, no pytest, importlib-loads hw-verify.py — same harness pattern as
tools/test_checked_claims.py.

Usage:  python tools/test_secrets_gate.py
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

scan_for_secrets = hw_verify.scan_for_secrets
check_secrets = hw_verify.check_secrets
shannon_entropy = hw_verify.shannon_entropy

PROJECT = "demo-project"

# A synthetic credential, in the shape the field incident produced: a sync
# digest copied a DSRM password and a local-admin password verbatim into a
# mailbox, and an append-only log made it permanent.
FAKE_PASSWORD = "Wint3rRecovery2026"
FAKE_TOKEN = "xK7pQ2mZr9TvLb4WnE8sYd3FgHj5"

_next_id = [0]


def reset_ids():
    _next_id[0] = 0


def ev(kind: str, payload: dict, project: str = PROJECT) -> dict:
    _next_id[0] += 1
    return {
        "id": f"EV-{_next_id[0]:04d}",
        "actor": "executor:T-004",
        "project": project,
        "kind": kind,
        "payload": payload,
    }


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


CASES = []


def case(name):
    def register(fn):
        CASES.append((name, fn))
        return fn
    return register


def has_rule(hits, rule) -> bool:
    return any(hit.startswith(rule) for hit in hits)


# ---------------------------------------------------------------------------
# Detectors — the shapes that must trip the gate
# ---------------------------------------------------------------------------

@case("obvious password assignment is a hit")
def _(tmp):
    hits = scan_for_secrets(f'password: "{FAKE_PASSWORD}"')
    return (has_rule(hits, "assignment"), f"expected an assignment hit, got {hits}")


@case("the field-evidence shape (DSRM password in a digest) is a hit")
def _(tmp):
    text = (f"Sync digest 2026-06-02\n  DSRM password = {FAKE_PASSWORD}\n"
            f"  local admin pwd = {FAKE_PASSWORD}x\n")
    hits = scan_for_secrets(text)
    return (len(hits) >= 2, f"expected both credentials flagged, got {hits}")


@case("api_key assignment is a hit")
def _(tmp):
    hits = scan_for_secrets("api_key=abcd1234efgh5678ijkl9012")
    return (has_rule(hits, "assignment"), f"expected an assignment hit, got {hits}")


@case("client_secret assignment is a hit")
def _(tmp):
    hits = scan_for_secrets("client_secret: Q7x-Winter-Rotation-Value")
    return (has_rule(hits, "assignment"), f"expected an assignment hit, got {hits}")


@case("PEM private-key block is a hit")
def _(tmp):
    text = ("-----BEGIN RSA PRIVATE KEY-----\n"
            "MIIEowIBAAKCAQEAy8Dbv8prpJ/0kKhlGeJYozo2t60EG8L0561g13R29LvMR5hy\n"
            "-----END RSA PRIVATE KEY-----")
    hits = scan_for_secrets(text)
    return (has_rule(hits, "private_key"), f"expected a private_key hit, got {hits}")


@case("OpenSSH private-key block is a hit")
def _(tmp):
    hits = scan_for_secrets("-----BEGIN OPENSSH PRIVATE KEY-----")
    return (has_rule(hits, "private_key"), f"expected a private_key hit, got {hits}")


@case("a certificate block is NOT a private key (public material is public)")
def _(tmp):
    hits = scan_for_secrets("-----BEGIN CERTIFICATE-----")
    return (not has_rule(hits, "private_key"),
            f"expected no private_key hit on a certificate, got {hits}")


@case("URL connection string with embedded credentials is a hit")
def _(tmp):
    hits = scan_for_secrets("postgres://svc_app:s3cr3tpass@db.internal:5432/appdb")
    return (has_rule(hits, "connection_string"),
            f"expected a connection_string hit, got {hits}")


@case("keyword connection string (Server=...;Password=...) is a hit")
def _(tmp):
    hits = scan_for_secrets(
        "Server=sql01;Initial Catalog=app;User ID=sa;Password=Hunter2Winter;")
    return (bool(hits), f"expected a hit, got {hits}")


@case("bearer token is a hit")
def _(tmp):
    hits = scan_for_secrets("Authorization: Bearer abcdefgh12345678ijklmnop")
    return (has_rule(hits, "bearer_token"), f"expected a bearer_token hit, got {hits}")


@case("AWS access-key id shape is a hit")
def _(tmp):
    hits = scan_for_secrets("the runner used AKIAIOSFODNN7EXAMPLE")
    return (has_rule(hits, "bearer_token"), f"expected a bearer_token hit, got {hits}")


@case("JWT shape is a hit")
def _(tmp):
    hits = scan_for_secrets(
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0In0.dBjftJeZ4CVPmB92K")
    return (bool(hits), f"expected a hit, got {hits}")


@case("unlabeled high-entropy token is a hit")
def _(tmp):
    hits = scan_for_secrets(f"pasted from the console: {FAKE_TOKEN}")
    return (has_rule(hits, "high_entropy"), f"expected a high_entropy hit, got {hits}")


# ---------------------------------------------------------------------------
# False-positive guards — the harness's own hashes must never trip the gate
# ---------------------------------------------------------------------------

@case("a full sha256 in content_sha256 is NOT flagged")
def _(tmp):
    hits = scan_for_secrets(
        "content_sha256: 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08")
    return (hits == [], f"expected no hits, got {hits}")


@case("prev_hash / hash values are NOT flagged")
def _(tmp):
    hits = scan_for_secrets(
        "prev_hash: sha256:" + "0" * 64
        + " hash: 3f786850e387550fdab836ed7e6dc881de23001b")
    return (hits == [], f"expected no hits, got {hits}")


@case("12-hex citations are NOT flagged")
def _(tmp):
    hits = scan_for_secrets("consumed [OR-001#d2e3f4a5b6c7] and [F-014#b8d4e1779a02]")
    return (hits == [], f"expected no hits, got {hits}")


@case("a bare 64-hex digest is NOT flagged (pure hex cannot reach the threshold)")
def _(tmp):
    hits = scan_for_secrets("a" * 32 + " " + "9f86d081884c7d659a2feaa0c55ad015" * 2)
    return (hits == [], f"expected no hits, got {hits}")


@case("test_ref and evidence ids are NOT flagged")
def _(tmp):
    hits = scan_for_secrets("test_ref: ED-014 (ran the import against the live path)")
    return (hits == [], f"expected no hits, got {hits}")


@case("[REDACTED-SECRET] plus a pointer is NOT flagged")
def _(tmp):
    hits = scan_for_secrets(
        "DSRM credential: [REDACTED-SECRET] - operator vault, entry 'dc-recovery'")
    return (hits == [], f"expected no hits, got {hits}")


@case("password: [REDACTED-SECRET] is NOT flagged (the gate asks for exactly this)")
def _(tmp):
    hits = scan_for_secrets("password: [REDACTED-SECRET]")
    return (hits == [], f"expected no hits, got {hits}")


@case("an angle-bracket pointer value is NOT flagged")
def _(tmp):
    hits = scan_for_secrets("password: <see operator vault, entry dc-recovery>")
    return (hits == [], f"expected no hits, got {hits}")


@case("password: null is NOT flagged")
def _(tmp):
    hits = scan_for_secrets("password: null")
    return (hits == [], f"expected no hits, got {hits}")


@case("an environment-variable reference is NOT flagged")
def _(tmp):
    hits = scan_for_secrets("password=${DB_PASSWORD}")
    return (hits == [], f"expected no hits, got {hits}")


@case("harness paths and identifiers are NOT flagged")
def _(tmp):
    text = ("projects/demo-project/tasks/T-001/consumed-inputs.md "
            "00-REFERENCE-rules.compressed.md SessionHandoffTemplateProjection "
            "recommended_first_action equality_method: manual-attestation")
    hits = scan_for_secrets(text)
    return (hits == [], f"expected no hits, got {hits}")


@case("prose mentioning a password without assigning one is NOT flagged")
def _(tmp):
    hits = scan_for_secrets(
        "the operator reminded me the password lives in the vault, not in the log")
    return (hits == [], f"expected no hits, got {hits}")


@case("non-string and empty input scan clean")
def _(tmp):
    bad = [scan_for_secrets(None), scan_for_secrets(12), scan_for_secrets(""),
           scan_for_secrets("   ")]
    return (all(h == [] for h in bad), f"expected all empty, got {bad}")


@case("pure hex tops out at 4.0 bits/char, the entropy threshold")
def _(tmp):
    worst = shannon_entropy("0123456789abcdef" * 4)
    return (worst <= hw_verify.SECRET_ENTROPY_BITS,
            f"uniform hex scored {worst}, threshold is "
            f"{hw_verify.SECRET_ENTROPY_BITS}")


# ---------------------------------------------------------------------------
# The report must not become the second copy of the secret
# ---------------------------------------------------------------------------

@case("hit lines never echo the secret value")
def _(tmp):
    hits = scan_for_secrets(f"password={FAKE_PASSWORD} token={FAKE_TOKEN}")
    leaked = [h for h in hits if FAKE_PASSWORD in h or FAKE_TOKEN in h]
    return (hits and not leaked,
            f"expected hits with no secret echoed, got {hits}")


@case("check_secrets warnings never echo the secret value")
def _(tmp):
    reset_ids()
    events = [ev("finding.add", {"id": "F-001", "evidence": f"pwd = {FAKE_PASSWORD}"})]
    warnings = check_secrets(events)
    leaked = [w for w in warnings if FAKE_PASSWORD in w]
    return (warnings and not leaked,
            f"expected warnings with no secret echoed, got {warnings}")


# ---------------------------------------------------------------------------
# check_secrets — field paths and event attribution
# ---------------------------------------------------------------------------

@case("check_secrets names the event and the payload field")
def _(tmp):
    reset_ids()
    events = [ev("evidence.capture", {"id": "ED-001", "content": f"password={FAKE_PASSWORD}"})]
    warnings = check_secrets(events)
    ok = (len(warnings) == 1
          and "EV-0001" in warnings[0]
          and "payload.content" in warnings[0]
          and "possible_secret_in_event" in warnings[0])
    return (ok, f"expected one attributed warning, got {warnings}")


@case("check_secrets reaches nested dicts and list entries")
def _(tmp):
    reset_ids()
    events = [ev("scope.complete", {"scope_items": [
        {"id": "T-001", "name": "clean", "terminal_state": "complete"},
        {"id": "T-002", "name": "handover", "terminal_state": "complete",
         "reason": f"admin password: {FAKE_PASSWORD}"},
    ]})]
    warnings = check_secrets(events)
    ok = len(warnings) == 1 and "scope_items[1].reason" in warnings[0]
    return (ok, f"expected one warning naming scope_items[1].reason, got {warnings}")


@case("check_secrets on a clean chain returns nothing")
def _(tmp):
    reset_ids()
    events = [
        ev("finding.add", {"id": "F-001", "evidence": "the import resolved; see [OR-001#d2e3f4a5b6c7]"}),
        ev("task.complete", {"task_id": "T-001",
                             "completion_report_path": "projects/demo/tasks/T-001/report.md"}),
        ev("operator.correction", {"note": "that host is behind the bastion"}),
    ]
    warnings = check_secrets(events)
    return (warnings == [], f"expected no warnings, got {warnings}")


@case("check_secrets reports one line per hit across several events")
def _(tmp):
    reset_ids()
    events = [
        ev("finding.add", {"id": "F-001", "evidence": f"password={FAKE_PASSWORD}"}),
        ev("finding.add", {"id": "F-002", "evidence": "-----BEGIN OPENSSH PRIVATE KEY-----"}),
        ev("finding.add", {"id": "F-003", "evidence": "nothing sensitive here"}),
    ]
    warnings = check_secrets(events)
    ok = len(warnings) == 2 and "EV-0003" not in " ".join(warnings)
    return (ok, f"expected two warnings from EV-0001/EV-0002, got {warnings}")


# ---------------------------------------------------------------------------
# End to end — WARNING by default, FAIL under --strict-secrets
# ---------------------------------------------------------------------------

@case("end to end: a leaked chain still verifies (warning, not failure)")
def _(tmp):
    reset_ids()
    write_chain(tmp, [ev("finding.add", {"id": "F-001", "evidence": f"password={FAKE_PASSWORD}"})])
    result = hw_verify.verify(tmp, None)
    ok = result["result"] == "PASS" and len(result["secret_warnings"]) == 1
    return (ok, f"expected PASS with 1 warning, got {result['result']} "
                f"{result['secret_warnings']}")


@case("end to end: --strict-secrets promotes the same chain to FAIL")
def _(tmp):
    reset_ids()
    write_chain(tmp, [ev("finding.add", {"id": "F-001", "evidence": f"password={FAKE_PASSWORD}"})])
    result = hw_verify.verify(tmp, None, strict_secrets=True)
    ok = result["result"] == "FAIL" and len(result["secret_warnings"]) == 1
    return (ok, f"expected FAIL with 1 warning, got {result['result']} "
                f"{result['secret_warnings']}")


@case("end to end: --strict-secrets PASSes a clean chain")
def _(tmp):
    reset_ids()
    write_chain(tmp, [
        ev("finding.add", {"id": "F-001", "evidence": "credential: [REDACTED-SECRET] "
                                                       "(operator vault, entry dc-recovery)"}),
        ev("task.complete", {"task_id": "T-001",
                             "completion_report_path": "projects/demo/tasks/T-001/report.md"}),
    ])
    result = hw_verify.verify(tmp, None, strict_secrets=True)
    ok = result["result"] == "PASS" and result["secret_warnings"] == []
    return (ok, f"expected clean PASS, got {result['result']} {result['secret_warnings']}")


@case("end to end: default verify() records the strict flag as off")
def _(tmp):
    reset_ids()
    write_chain(tmp, [ev("task.complete", {"task_id": "T-001"})])
    result = hw_verify.verify(tmp, None)
    return (result["strict_secrets"] is False,
            f"expected strict_secrets False, got {result['strict_secrets']!r}")


@case("render() carries a possible_secrets row")
def _(tmp):
    reset_ids()
    write_chain(tmp, [ev("finding.add", {"id": "F-001", "evidence": f"password={FAKE_PASSWORD}"})])
    text = hw_verify.render(hw_verify.verify(tmp, None, strict_secrets=True))
    ok = "possible_secrets:" in text and "--strict-secrets" in text
    return (ok, f"expected a strict-marked possible_secrets row, got:\n{text}")


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
