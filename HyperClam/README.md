![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-blue.svg)

# HyperClam

**Local PII scrubbing that clams up before your data leaves the house.**

You want to process real data — tickets, emails, documents, exports — with an LLM. Some of that data should never reach a cloud API: names, emails, phone numbers, account numbers, addresses, the sentence that identifies your client without naming them. HyperClam is the cleaning station: a local, layered scrubber that runs *before* anything leaves your machine, replaces PII with consistent pseudonyms, and hands you a scrubbed document plus a locally-kept mapping to reverse it.

A clam doesn't talk. That's the product.

## Posture: over-zealous by design

Scrubbing has asymmetric failure costs. A false positive costs a little utility (something got masked that didn't need to be). A false negative is a **leak** — and at 100 documents a day, a 95%-recall scrubber is not 95% of a product, it is a leak machine. HyperClam therefore defaults aggressive: when unsure, scrub. Utility is tunable back up; a leak is not tunable back.

Recall is the product. Which means recall must be **measured, never asserted** — see §Testing. HyperClam ships with no marketing number; it ships with the instrument that produces your number, on your data, on your machine.

## Architecture: hard-coded first, LLM second, adversary third

1. **Deterministic layer.** Validated patterns — emails, phone numbers, SSNs, credit cards (Luhn-checked), IBANs (mod-97-checked), IP addresses, street addresses, dates-of-birth in context. Regex doesn't get tired, doesn't get creative, and *guarantees* its categories. This layer is the floor, never skipped.
2. **Local LLM layer.** Catches what patterns cannot: names in prose, employers, indirect identifiers ("my sister runs the Springfield DMV branch"). Local endpoint only — a scrubber that ships your raw text to a cloud API to find PII is a parody of itself. Non-localhost endpoints require an explicit, loudly-named override flag.
3. **Adversarial pass.** A second model (or second prompt) reads the *scrubbed* output with one job: find any PII that survived. Detection is easier than scrubbing, so verification is cheaper than generation. Loop until clean or max passes; residual findings are reported, never silently accepted.

Plus **triggers** (`triggers.yaml`): your always-scrub denylist (client names, project codenames, internal hostnames), context escalators (dates near "born/DOB" are DOBs), and an explicit allowlist for terms that look like PII but aren't (your own public support email).

## The de-anonymization trap (read this)

Anonymizers have been broken not by missing PII but by **predictable replacement patterns** — once an attacker learns the pattern, the masking reverses. HyperClam's placeholder rules are designed against that class of attack:

- Placeholders carry **zero derived information**: no preserved initials, no length hints, no phonetic echoes, no hash-of-the-original (hashes are rainbow-table-reversible).
- Pseudonym numbering is **per-document**: `[PERSON_2]` in one document has no relationship to `[PERSON_2]` in another. Cross-document linkage is opt-in and warned, never default.
- The mapping table is a **separate local artifact** (never embedded in output, written with owner-only permissions), or not produced at all in `--irreversible` mode.
- Format-preserving substitution (keeping a phone-number *shape* for downstream parsing) is available but explicitly flagged as a utility/safety trade.

See `CLAM.md` §Threat Model for the full analysis and the falsifier we hold ourselves to.

## Quick start

```bash
pip install pyyaml

# scrub a file with the deterministic layer only (no LLM needed)
python clam.py scrub input.txt

# with the local LLM layer + adversarial pass (any OpenAI-compatible local server)
python clam.py scrub input.txt --llm http://localhost:11434/v1 --model llama3.1:8b

# measure yourself before trusting yourself
python clam.py selftest
```

Outputs: `input.scrubbed.txt`, `input.mapping.json` (local, 0600), and an audit report of what was found per category and per layer.

## Testing (HyperFinch integration)

HyperClam's recall is established by **injection testing**: take real-shaped documents, inject known synthetic PII, and measure exactly what the scrubber catches — gold labels for free, zero real-PII risk, infinitely repeatable. The sibling project [HyperFinch](../HyperFinch/) runs these as flight plans across models, prompts, and configurations; `clam.py selftest` is the built-in miniature of the same method. A configuration is shippable when its measured recall on the injection corpus meets your bar — not before.

## What HyperClam does NOT claim

- **Not "HIPAA/GDPR compliant."** Compliance is a property of your process, not of a tool. HyperClam gives you measured recall on declared categories; your compliance posture is yours.
- **Not perfect.** No scrubber is. The adversarial pass and the audit report exist because the honest design assumes misses and hunts them.
- **Not a cloud service.** Local-only by design and by default. That is the entire point.

## Relationship to the Hyper family

Standalone product; own repo lifecycle. Built and dogfooded under [HyperWorker](https://github.com/mrhobbeys/hyperworker) (the harness), measured by HyperFinch (the instrument). HyperClam is stage zero of every data pipeline the family runs: nothing flows to a frontier model until it has passed the cleaning station.

## License

MIT — see [LICENSE](LICENSE).

---

*Built by [@mrhobbeys](https://x.com/mrhobbeys).*
