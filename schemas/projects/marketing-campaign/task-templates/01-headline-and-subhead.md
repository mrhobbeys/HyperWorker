---
id: T-001
kind: task
schema: marketing-campaign
phase: 1
risk_level: standard
required_tools: [file_write]
delivery_mode: constrained
depends_on: [T-000]
consumes:
  - "[OR-001#<short-hash>]"
  - "[F-001#<short-hash>]"            # audience description
  - "[DEC-001#<short-hash>]"          # offer statement
acceptance_criteria:
  - "Headline ≤ 12 words (Tier 3)."
  - "Subhead ≤ 25 words (Tier 3)."
  - "Headline leads with the reader's problem (Tier 4)."
  - "Zero Tier 1 banned tokens."
  - "Zero income guarantees, fabricated testimonials, or unverifiable superlatives."
---

# Task T-001: Landing Page Headline and Subhead

## Objective

Produce one landing-page headline and one subhead that mirror `DEC-001`'s offer for the audience in `F-001`. Output is appended to `outputs/landing-page-copy.md` under a `## Headline` and `## Subhead` section. Saved as draft only.

## Step-by-Step Instructions

1. Recite each consumed artifact in `consumed-inputs.md`. Confirm each paraphrase passes Layer 1 overlap.
2. Answer every `@@SCAN_n_m:` marker in `00-REFERENCE-rules.compressed.md`.
3. Generate three headline candidates that lead with the audience's pain (Tier 4 COPY-METHOD), each ≤ 12 words.
4. Pick the one closest to the brand-voice anchor in `OR-001.brand_voice_anchor`. Write it under `## Headline`.
5. Generate one subhead ≤ 25 words that names the offer outcome without claiming a specific revenue or earnings result.
6. Run banned-token scan against the rules table; reject any candidate containing a banned token.

## Completion Report

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [F-001#…], [DEC-001#…]
- **SCAN markers answered:** <count>
- **Outputs produced:** outputs/landing-page-copy.md (Headline, Subhead sections)
- **Discoveries:** <items>
- **Recommended follow-up artifacts:** "none" or "Write F-XXX capturing audience-language preference observed during candidate generation"
