# HyperClam — Design Spec (v0.1.0)

> Local, layered, over-zealous PII scrubbing with measured recall and anti-reversibility placeholder rules. Read `README.md` for the pitch; this file is the contract.

---

## Hypotheses

| ID | Claim | Falsifier |
|---|---|---|
| H-C1 | A deterministic pattern layer + local LLM layer catches materially more PII than either alone; the deterministic floor guarantees its categories at 100% on well-formed instances. | Injection testing shows the LLM layer adds no recall over patterns alone, OR a well-formed instance of a deterministic category survives scrubbing. |
| H-C2 | An adversarial second pass (detector reading scrubbed output) catches residual PII cheaper than improving the scrub prompt. | Across sweeps, the adversarial pass finds nothing the scrub pass missed (dead weight) OR misses what a human grader then finds at material rates (false floor). |
| H-C3 | The placeholder rules in §Threat Model prevent pattern-based re-identification. | Anyone — including us — demonstrates recovery of original values from scrubbed output alone (no mapping file), using placeholder structure, ordering, or format. Standing invitation. |
| H-C4 | Over-zealous defaults preserve enough utility for downstream LLM tasks. | Graded downstream-task quality on scrubbed vs. raw input degrades beyond the operator's declared tolerance. |

---

## Threat Model

| Threat | Vector | Countermeasure |
|---|---|---|
| Direct leak | PII survives scrubbing and reaches a cloud API | Layered scrub + adversarial pass + measured recall before trust (injection testing) |
| Pattern re-identification | Placeholders encode derived info (initials, length, phonetics, stable hashes) — the documented failure of a prior anonymizing product: once the pattern was learned, the data reversed | Placeholders carry zero derived content: category + per-document ordinal only (`[PERSON_3]`); no hashing of originals; no preserved fragments |
| Cross-document linkage | Same pseudonym for same entity across a corpus lets an attacker join documents and triangulate identity | Per-document mapping; per-run random salt; cross-doc consistency is opt-in (`--link-entities`) with a printed warning |
| Mapping exposure | The reversal table leaks alongside the scrubbed text | Mapping is a separate file, owner-only permissions (0600), never embedded in output; `--irreversible` produces no mapping at all |
| Self-defeating scrub | The scrubber sends raw text to a remote API to "find PII" | Endpoint must be localhost/127.0.0.1/[::1]; anything else requires `--i-accept-remote-risk` and prints what it is about to do |
| Source alteration | Any stage (or any other process) modifies the originals during a run — corrupting evidence and trust | Stage -1 integrity: per-file pre/post SHA-256 in every scrub report (`source_unaltered`); corpus-level `manifest` / `manifest --check` commands; mismatch fails loud (exit 3) |
| Trigger-list leak | The operator's `always_scrub` list (client names, codenames) is itself sensitive | `triggers.yaml` lives operator-side, gitignored by convention; docs say so explicitly |
| Format-preserving inference | Keeping value *shapes* (a 10-digit "phone") narrows the search space for reversal | Off by default; `--format-preserving` prints the trade it is making |

**Residual risks named honestly:** free-prose indirect identification ("the only female firefighter in Greenfield") is detectable only by the LLM layer and only sometimes — this is exactly what injection testing must probe with hard cases; placeholder *count* leaks how many distinct entities a document mentions (accepted; negligible vs. utility cost of padding); a compromised local machine defeats everything (out of scope — HyperClam is not endpoint security).

---

## Pipeline

```
input ──► Stage -1: integrity baseline
              SHA-256 the source bytes BEFORE anything reads them;
              re-hash after outputs are written; mismatch = exit 3, loud.
              Corpus-level: `clam.py manifest <dir>` before a run,
              `--check` after — "originals not altered" as a verified
              fact, not a promise. Chain of custody for auditors.
      ──► Stage 0: normalize (unicode NFC, line endings)
      ──► Stage 1: DETERMINISTIC  (never skipped)
              validated patterns + triggers.yaml always_scrub
      ──► Stage 2: LOCAL LLM      (optional; --llm)
              contextual PII the patterns cannot see
      ──► Stage 3: ADVERSARIAL    (optional; runs when --llm is on)
              detector reads SCRUBBED text: "find surviving PII"
              findings → re-scrub → repeat (max_passes, default 3)
      ──► outputs: scrubbed text + local mapping + audit report
```

Every stage records what it found and at which pass; the audit report is the per-document evidence trail (counts per category per layer, residual findings, passes used). Trust the report, not the absence of visible PII.

## Deterministic layer — v0.1.0 categories

| Category | Validation | Notes |
|---|---|---|
| `EMAIL` | RFC-lite pattern | |
| `PHONE` | NANP-shaped patterns | **US-centric in v0.1.0** — international formats are a declared gap, roadmap v0.2 |
| `SSN` | format | |
| `CARD` | 13–19 digits + **Luhn check** | Luhn cuts false positives on long IDs |
| `IBAN` | format + **mod-97 check** | |
| `IP` | IPv4 octet-validated | IPv6 roadmap |
| `ADDRESS` | number + street-suffix heuristic | US-centric, intentionally loose (over-zealous) |
| `DOB` | date pattern **within a context window** of born/DOB/birth | The context-escalator pattern: a date is not PII; a date next to "born" is |
| `TRIGGER` | operator literals/regex from `triggers.yaml` | client names, codenames, hostnames |

The deterministic layer's promise is narrow and absolute: well-formed instances of these categories do not pass. `clam.py selftest` enforces it — recall on the deterministic fixture must be 1.0 or the build is broken.

## triggers.yaml

```yaml
always_scrub:            # literal or regex; matched case-insensitively; category TRIGGER
  - "Acme Holdings"
  - "project kingfisher"
  - 're:\bACC-\d{6}\b'   # prefix `re:` for regex
context_escalators:      # pattern becomes PII when near a cue word (chars window)
  - cue: "born|DOB|birth"
    pattern: 're:\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
    window: 40
    category: DOB
allowlist:               # never scrub, even if a pattern matches (your own public email)
  - "support@yourcompany.com"
```

The triggers file is the operator's knowledge encoded — the things no general scrubber could know are sensitive *here*. It is also itself sensitive: keep it local, gitignore it.

## Placeholders and mapping

- Form: `[CATEGORY_n]`, `n` assigned by order of first appearance **within the document**. Same value → same placeholder within a document (consistency keeps the text usable downstream).
- No global registry. A fresh run is a fresh mapping. `--link-entities` opts into cross-document consistency for corpus jobs, with the linkage risk printed at run time.
- Mapping file: `{placeholder: original}` JSON, written 0600, alongside the output. `--irreversible` skips it entirely.

## LLM layer contract

Request: scrub-instruction + document; response: JSON array of `{"text": "<exact span>", "category": "<label>"}`. Exact-match spans are replaced through the same placeholder machinery as Stage 1 (one mapping, one audit trail). Malformed JSON → retry once → fail loud (never "best effort" silently). The adversarial pass uses the same contract with a detector instruction and, ideally, a *different* model or at minimum a different prompt frame — correlated blind spots are the failure mode, and HyperFinch sweeps measure whether your detector pair actually decorrelates (H-C2).

## Office Formats Without Office (v0.2 requirement)

HyperClam targets machines that do not and should not have Office installed — Linux servers, domain controllers, hardened hosts. This is a feature, not a limitation, and it sets three rules:

1. **Parse the raw package.** docx/xlsx/pptx are ZIP + XML. The visible body text is one part among many; the same package carries `core.xml` author/last-modified-by fields, comments, **tracked changes** (deleted text still present in the file), hidden rows and "very hidden" sheets, and custom properties. The scrubber scans the *full package*, not just the rendered text — the metadata surfaces are exactly where competing tools leak. Any text-extraction count that covers only visible body text is a floor on the document's true PII, never a ceiling.
2. **Read-only on source, always.** Scrubbed output and audit artifacts land in a separate directory. The original file's bytes are never modified — no metadata churn, no Office-tool re-save side effects, no contaminated evidence.
3. **Minimal dependency surface.** Extraction uses pure-Python libraries (no COM, no LibreOffice). For a privacy tool, every dependency is supply-chain attack surface; the roadmap holds a hardened stdlib-only extraction mode (zipfile + xml.etree) for deployments where third-party packages are themselves a policy problem.

Output contract for this product stage: file in → scrubbed text/JSONL out, fit for LLM consumption, plus the audit report. Re-emitting format-preserving scrubbed .docx/.xlsx is a separate, later problem (v0.4+) — useful, but not required for the preprocessing-gateway use case.

**Corpus finding that motivated this section (2026-06-10 blind scan, 118 real files):** PII concentrates — median file had zero deterministic spans while nine files carried 50+ each (contact-list spreadsheets at 700–860 emails apiece), so triage reporting ("these files are radioactive, these are clean") is first-class output; the deterministic layer found zero PII in *filenames* while an LLM spotted person/client names in them immediately (H-C1 demonstrated — filenames become a scrub surface in v0.2); and field-level xlsx scrubbing moves from roadmap to core requirement, since the hottest files are spreadsheets whose utility depends on structure surviving the scrub.

## Measurement (the only honest recall number is yours)

1. **Freeze a corpus** of real-shaped documents from your own domain (tickets, emails, reports). Pull once, replay forever.
2. **Inject** synthetic PII at known offsets — gold labels for free. Include hard cases: names that are common words, indirect identifiers, PII split across line breaks.
3. **Sweep** with HyperFinch: models × prompts × `max_passes` × trigger configs. Metrics per cell: **span recall** (primary), span precision, utility retention (graded downstream task on scrubbed output), tokens, latency.
4. **Grade the misses.** Every false negative becomes a fixture in the regression corpus. The corpus only grows.

Ship gate: a configuration is usable on real data when measured recall on the current injection corpus meets the operator's declared bar. v0.1.0 declares no number — it declares the method.

## Roadmap

- v0.2 — international phone/address patterns; IPv6; NER stage between regex and LLM; HyperFinch flight-plan templates for the injection sweep.
- v0.3 — structured-format awareness (CSV/JSON field-level scrubbing — Spencer's existing research spreadsheets are the use case); reversible re-identification workflow (scrubbed answer comes back from the frontier model → mapping re-inflates it locally).
- Each addition states a hypothesis and a falsifier, house style.
