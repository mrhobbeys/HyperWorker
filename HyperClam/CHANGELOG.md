# Changelog — HyperClam

## v0.1.0 (2026-06-09) — Initial spec + working core

Standalone product. Built and dogfooded under HyperWorker; measured by HyperFinch; not bound by the harness's no-shipped-code posture.

- `CLAM.md` design spec: hypotheses H-C1–H-C4 with falsifiers, threat model (including the pattern-re-identification attack class — placeholders carry zero derived information, per-document numbering, separate 0600 mapping file, `--irreversible` mode), pipeline contract, measurement method (injection testing; recall is measured, never asserted), declared v0.1.0 gaps (US-centric phone/address, no IPv6, no NER stage).
- `clam.py` working core: deterministic layer with validated patterns (Luhn for cards, mod-97 for IBANs, octet-validated IPv4, context-gated DOB), `triggers.yaml` support (always_scrub / context_escalators / allowlist), per-document placeholder engine, optional local-LLM scrub stage + adversarial verify loop (localhost-enforced; remote requires `--i-accept-remote-risk`), audit report, `selftest` with gold-labeled fixture — deterministic-layer recall must be 1.000 or the build fails.
- `triggers.example.yaml` — shareable shape of the operator trigger file, with the keep-it-local warning.
- Stage -1 integrity (operator-requested as a launch guarantee): every scrub records the source's SHA-256 before processing and re-hashes after — `source_unaltered` in every report, exit 3 on mismatch; `clam.py manifest <dir>` / `--check` pin and verify whole corpora. "Originals not altered" is verified per run, never asserted.
- §Office Formats Without Office added to CLAM.md: full-package scanning requirement (tracked changes, core.xml author fields, hidden sheets), read-only-source rule, hardened stdlib-only extraction mode on the roadmap; motivated by the 2026-06-10 blind scan of a 118-file real corpus (PII concentration finding, filename-PII finding, xlsx-as-hottest-format finding).
