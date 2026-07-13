#!/usr/bin/env python3
"""
clam.py — HyperClam v0.1.0. Local, layered, over-zealous PII scrubbing.

Stages: deterministic patterns (never skipped) -> optional local LLM layer
-> optional adversarial verification pass. See CLAM.md for the contract.

Usage:
    python clam.py scrub <input.txt> [--triggers triggers.yaml]
                   [--llm http://localhost:11434/v1 --model <name>]
                   [--max-passes 3] [--irreversible] [--link-entities]
                   [--i-accept-remote-risk]
    python clam.py selftest

Dependencies: Python 3.9+, pyyaml (only when --triggers is used).
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
import unicodedata
import urllib.request
import urllib.error
from pathlib import Path


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

# --------------------------------------------------------------- validators

def luhn_ok(digits: str) -> bool:
    total, alt = 0, False
    for ch in reversed(digits):
        d = int(ch)
        if alt:
            d *= 2
            if d > 9:
                d -= 9
        total += d
        alt = not alt
    return total % 10 == 0


def iban_ok(s: str) -> bool:
    s = s.replace(" ", "").upper()
    if not (15 <= len(s) <= 34):
        return False
    rearranged = s[4:] + s[:4]
    digits = "".join(str(ord(c) - 55) if c.isalpha() else c for c in rearranged)
    try:
        return int(digits) % 97 == 1
    except ValueError:
        return False


def ipv4_ok(s: str) -> bool:
    parts = s.split(".")
    return len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)


# --------------------------------------------------------------- patterns
# (category, compiled regex, validator-or-None). US-centric in v0.1.0 — see CLAM.md.

PATTERNS = [
    ("EMAIL", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), None),
    ("SSN", re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), None),
    ("CARD", re.compile(r"\b\d(?:[ -]?\d){12,18}\b"),
     lambda m: luhn_ok(re.sub(r"[ -]", "", m)) and 13 <= len(re.sub(r"[ -]", "", m)) <= 19),
    ("IBAN", re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b"), iban_ok),
    ("IP", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), ipv4_ok),
    ("PHONE", re.compile(
        r"(?<![\d.])(?:\+?1[ \-.]?)?(?:\(\d{3}\)[ \-.]?|\d{3}[ \-.])\d{3}[ \-.]\d{4}(?!\d)"), None),
    ("ADDRESS", re.compile(
        r"\b\d{1,5}\s+[A-Z][A-Za-z]*(?:\s[A-Z][A-Za-z]*){0,3}\s"
        r"(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard|Lane|Ln|Drive|Dr|Court|Ct|Way|Place|Pl)\b"), None),
]

DOB_DATE = re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b")
DOB_CUE = re.compile(r"\b(?:born|DOB|birth)\b", re.IGNORECASE)
DOB_WINDOW = 40

LOCAL_HOSTS = ("localhost", "127.0.0.1", "[::1]", "0.0.0.0")


# --------------------------------------------------------------- triggers

def load_triggers(path):
    if not path:
        return {"always_scrub": [], "context_escalators": [], "allowlist": []}
    try:
        import yaml
    except ImportError:
        sys.exit("--triggers needs pyyaml: pip install pyyaml")
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    data.setdefault("always_scrub", [])
    data.setdefault("context_escalators", [])
    data.setdefault("allowlist", [])
    return data


def trigger_regex(entry: str):
    if entry.startswith("re:"):
        return re.compile(entry[3:], re.IGNORECASE)
    return re.compile(re.escape(entry), re.IGNORECASE)


# --------------------------------------------------------------- span engine

def find_spans(text: str, triggers: dict) -> list:
    """Return [(start, end, category, matched_text)] from the deterministic layer."""
    spans = []
    for cat, rx, validator in PATTERNS:
        for m in rx.finditer(text):
            if validator and not validator(m.group(0)):
                continue
            spans.append((m.start(), m.end(), cat, m.group(0)))
    # DOB: date within window of a cue word (context escalator, built-in)
    cues = [m.start() for m in DOB_CUE.finditer(text)]
    for m in DOB_DATE.finditer(text):
        if any(abs(m.start() - c) <= DOB_WINDOW for c in cues):
            spans.append((m.start(), m.end(), "DOB", m.group(0)))
    # operator triggers
    for entry in triggers["always_scrub"]:
        for m in trigger_regex(entry).finditer(text):
            spans.append((m.start(), m.end(), "TRIGGER", m.group(0)))
    for esc in triggers["context_escalators"]:
        cue_rx = re.compile(esc["cue"], re.IGNORECASE)
        pat_rx = trigger_regex(esc["pattern"]) if isinstance(esc["pattern"], str) \
            else esc["pattern"]
        cues = [m.start() for m in cue_rx.finditer(text)]
        for m in pat_rx.finditer(text):
            if any(abs(m.start() - c) <= int(esc.get("window", 40)) for c in cues):
                spans.append((m.start(), m.end(), esc.get("category", "TRIGGER"),
                              m.group(0)))
    # allowlist filter
    allow = {a.lower() for a in triggers["allowlist"]}
    spans = [s for s in spans if s[3].lower() not in allow]
    # overlap resolution: longest span wins, then earliest
    spans.sort(key=lambda s: (s[0], -(s[1] - s[0])))
    resolved, last_end = [], -1
    for s in spans:
        if s[0] >= last_end:
            resolved.append(s)
            last_end = s[1]
    return resolved


class Scrubber:
    """Applies spans to text with per-document, per-category placeholder numbering.
    Same original value -> same placeholder within this document. Placeholders
    carry no derived information (CLAM.md §Threat Model)."""

    def __init__(self):
        self.mapping = {}          # placeholder -> original
        self._by_value = {}        # (category, value) -> placeholder
        self._counters = {}        # category -> next ordinal
        self.audit = {}            # category -> count

    def placeholder_for(self, category: str, value: str) -> str:
        key = (category, value)
        if key not in self._by_value:
            self._counters[category] = self._counters.get(category, 0) + 1
            ph = f"[{category}_{self._counters[category]}]"
            self._by_value[key] = ph
            self.mapping[ph] = value
        return self._by_value[key]

    def apply(self, text: str, spans: list) -> str:
        out, cursor = [], 0
        for start, end, cat, value in spans:
            out.append(text[cursor:start])
            out.append(self.placeholder_for(cat, value))
            self.audit[cat] = self.audit.get(cat, 0) + 1
            cursor = end
        out.append(text[cursor:])
        return "".join(out)

    def scrub_values(self, text: str, findings: list) -> str:
        """Replace exact-match LLM findings ({text, category}) everywhere."""
        for f in findings:
            value = f.get("text", "")
            if not value or value not in text:
                continue
            ph = self.placeholder_for(f.get("category", "PII").upper(), value)
            n = text.count(value)
            text = text.replace(value, ph)
            self.audit[f.get("category", "PII").upper()] = \
                self.audit.get(f.get("category", "PII").upper(), 0) + n
        return text


# --------------------------------------------------------------- LLM stages

SCRUB_PROMPT = (
    "You are a PII detector. List every span of personally identifying "
    "information in the document below: person names, organizations that "
    "identify a person, job titles + locations that narrow to a person, "
    "usernames, account numbers, and any other identifier. Be over-zealous: "
    "if unsure, include it. Respond with ONLY a JSON array of objects "
    '{"text": "<exact span copied verbatim>", "category": "<LABEL>"}. '
    "No commentary.\n\n--- DOCUMENT ---\n")

ADVERSARY_PROMPT = (
    "You are an adversarial privacy auditor. The document below was scrubbed; "
    "placeholders like [NAME_1] are intentional. Find any REMAINING personally "
    "identifying information the scrub missed, including indirect identifiers "
    "(unique role + place, rare event + date). Respond with ONLY a JSON array "
    'of {"text": "<exact span>", "category": "<LABEL>"} — empty array if '
    "nothing remains.\n\n--- DOCUMENT ---\n")


def assert_local(base_url: str, override: bool):
    host = re.sub(r"^https?://", "", base_url).split("/")[0].split(":")[0]
    if host not in LOCAL_HOSTS and not override:
        sys.exit(f"REFUSED: endpoint host '{host}' is not local. A PII scrubber "
                 "that sends raw text to a remote API defeats its purpose. "
                 "If you accept that risk, re-run with --i-accept-remote-risk.")
    if host not in LOCAL_HOSTS and override:
        print(f"WARNING: sending text to REMOTE endpoint {base_url}", file=sys.stderr)


def llm_findings(base_url: str, model: str, prompt: str, text: str,
                 timeout: int = 180) -> list:
    body = {"model": model, "temperature": 0.0,
            "messages": [{"role": "user", "content": prompt + text}]}
    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                content = json.loads(resp.read().decode("utf-8")
                                     )["choices"][0]["message"]["content"]
            m = re.search(r"\[.*\]", content, re.DOTALL)
            return json.loads(m.group(0)) if m else []
        except (urllib.error.URLError, TimeoutError, KeyError,
                json.JSONDecodeError) as e:
            if attempt == 2:
                sys.exit(f"LLM stage failed twice; refusing to continue silently: {e}")
    return []


# --------------------------------------------------------------- commands

def cmd_scrub(args):
    src = Path(args.input)
    raw = src.read_bytes()
    pre_hash = hashlib.sha256(raw).hexdigest()   # Stage -1: integrity baseline
    text = unicodedata.normalize("NFC",
                                 raw.decode("utf-8")).replace("\r\n", "\n")
    triggers = load_triggers(args.triggers)
    scrubber = Scrubber()
    passes_used = 1

    # Stage 1 — deterministic (never skipped)
    text = scrubber.apply(text, find_spans(text, triggers))

    # Stage 2 + 3 — LLM scrub, then adversarial verify loop
    if args.llm:
        assert_local(args.llm, args.i_accept_remote_risk)
        text = scrubber.scrub_values(
            text, llm_findings(args.llm, args.model, SCRUB_PROMPT, text))
        for _ in range(max(0, args.max_passes - 1)):
            residual = llm_findings(args.llm, args.model, ADVERSARY_PROMPT, text)
            residual = [f for f in residual if f.get("text", "") in text]
            if not residual:
                break
            passes_used += 1
            text = scrubber.scrub_values(text, residual)
        else:
            residual = llm_findings(args.llm, args.model, ADVERSARY_PROMPT, text)
            if residual:
                print(f"RESIDUAL FINDINGS after {args.max_passes} passes "
                      f"(NOT silently accepted): {json.dumps(residual)}",
                      file=sys.stderr)

    out_path = src.with_suffix(src.suffix + ".scrubbed.txt") \
        if src.suffix != ".txt" else src.with_name(src.stem + ".scrubbed.txt")
    out_path.write_text(text, encoding="utf-8")

    post_hash = sha256_file(src)                 # Stage -1 close: prove read-only
    report = {"input": str(src), "output": str(out_path),
              "source_sha256": pre_hash,
              "source_unaltered": post_hash == pre_hash,
              "found_per_category": scrubber.audit, "passes": passes_used,
              "llm_layer": bool(args.llm), "irreversible": args.irreversible}
    if post_hash != pre_hash:
        print("INTEGRITY FAIL: source file changed during processing — "
              "output is untrustworthy; investigate before using it.",
              file=sys.stderr)
        print(json.dumps(report, indent=2))
        sys.exit(3)
    if not args.irreversible:
        map_path = out_path.with_suffix(".mapping.json")
        map_path.write_text(json.dumps(scrubber.mapping, indent=2,
                                       ensure_ascii=False), encoding="utf-8")
        try:
            os.chmod(map_path, 0o600)
        except OSError:
            pass
        report["mapping"] = str(map_path)
    print(json.dumps(report, indent=2))


def cmd_manifest(args):
    """Snapshot (or verify) SHA-256 of every file under a directory.
    Run before processing real data; run --check after to prove 'originals
    not altered' as a fact rather than a promise."""
    root = Path(args.dir)
    files = sorted(p for p in root.rglob("*") if p.is_file()
                   and not p.name.endswith(".manifest.json"))
    current = {str(p.relative_to(root)): sha256_file(p) for p in files}
    if args.check:
        recorded = json.loads(Path(args.check).read_text(encoding="utf-8"))["files"]
        altered = sorted(k for k in recorded if k in current and current[k] != recorded[k])
        missing = sorted(k for k in recorded if k not in current)
        new = sorted(k for k in current if k not in recorded)
        ok = not altered and not missing
        print(json.dumps({"manifest": args.check, "files_recorded": len(recorded),
                          "altered": altered, "missing": missing, "new_files": new,
                          "result": "PASS" if ok else "FAIL"}, indent=2))
        return 0 if ok else 1
    out = Path(args.out) if args.out else root / (root.name + ".manifest.json")
    out.write_text(json.dumps(
        {"root": str(root), "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
         "algorithm": "sha256", "files": current},
        indent=2, ensure_ascii=False), encoding="utf-8")
    try:
        os.chmod(out, 0o600)
    except OSError:
        pass
    print(json.dumps({"manifest": str(out), "files_hashed": len(current)}, indent=2))
    return 0


# --------------------------------------------------------------- selftest

FIXTURE = """Ticket #4412 from Dana Whitfield <dana.whitfield@example-corp.com>.
Callback number: (555) 214-8890. Alt: 555-214-8891.
Customer paid with card 4111 1111 1111 1111 and gave SSN 219-09-9999.
Server logs show logins from 203.0.113.42 for account holder
born 04/12/1988, residing at 1742 Willow Creek Drive.
Wire refund to IBAN DE89370400440532013000 per request.
Contact support@yourcompany.com for escalation. Meeting on 06/02/2026
discussed roadmap (no cue words nearby, so this date must NOT be flagged
as DOB — dates are only PII in birth context)."""

GOLD = [
    ("EMAIL", "dana.whitfield@example-corp.com"),
    ("PHONE", "(555) 214-8890"),
    ("PHONE", "555-214-8891"),
    ("CARD", "4111 1111 1111 1111"),
    ("SSN", "219-09-9999"),
    ("IP", "203.0.113.42"),
    ("DOB", "04/12/1988"),
    ("ADDRESS", "1742 Willow Creek Drive"),
    ("IBAN", "DE89370400440532013000"),
]


def cmd_selftest(_args):
    triggers = {"always_scrub": [], "context_escalators": [],
                "allowlist": ["support@yourcompany.com"]}
    spans = find_spans(FIXTURE, triggers)
    found = {(cat, val) for (_s, _e, cat, val) in spans}
    hits = [g for g in GOLD if g in found]
    misses = [g for g in GOLD if g not in found]
    extras = sorted(found - set(GOLD))
    recall = len(hits) / len(GOLD)
    scrubbed = Scrubber().apply(FIXTURE, spans)
    leak = [g for g in GOLD if g[1] in scrubbed]
    allow_ok = "support@yourcompany.com" in scrubbed
    second_date_ok = scrubbed.count("[DOB_") == 1  # far date must not be DOB

    print(f"HyperClam selftest — deterministic layer")
    print(f"  gold spans:     {len(GOLD)}")
    print(f"  recall:         {recall:.3f}  ({len(hits)}/{len(GOLD)})")
    print(f"  misses:         {misses or 'none'}")
    print(f"  extra findings: {extras or 'none'}  (over-zealous is acceptable; "
          f"silent misses are not)")
    print(f"  allowlist honored: {allow_ok}")
    print(f"  context-gated DOB (far date not flagged): {second_date_ok}")
    print(f"  post-scrub leak check: {'LEAK: ' + str(leak) if leak else 'clean'}")
    ok = recall == 1.0 and not leak and allow_ok and second_date_ok
    print(f"  result: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(prog="clam", description="HyperClam PII scrubber")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sc = sub.add_parser("scrub", help="scrub a text file")
    sc.add_argument("input")
    sc.add_argument("--triggers", default=None, help="triggers.yaml path")
    sc.add_argument("--llm", default=None, help="OpenAI-compatible base URL (local)")
    sc.add_argument("--model", default=None, help="model name for --llm")
    sc.add_argument("--max-passes", type=int, default=3)
    sc.add_argument("--irreversible", action="store_true",
                    help="write no mapping file")
    sc.add_argument("--link-entities", action="store_true",
                    help="(reserved) cross-document consistent pseudonyms")
    sc.add_argument("--i-accept-remote-risk", action="store_true")
    sc.set_defaults(func=cmd_scrub)
    st = sub.add_parser("selftest", help="measured check of the deterministic layer")
    st.set_defaults(func=cmd_selftest)
    mf = sub.add_parser("manifest",
                        help="hash every file in a dir (or --check a prior manifest)")
    mf.add_argument("dir")
    mf.add_argument("--out", default=None, help="manifest output path")
    mf.add_argument("--check", default=None, help="verify against this manifest")
    mf.set_defaults(func=cmd_manifest)
    args = ap.parse_args()
    if args.cmd == "scrub" and args.llm and not args.model:
        ap.error("--llm requires --model")
    rc = args.func(args)
    sys.exit(rc or 0)


if __name__ == "__main__":
    main()
