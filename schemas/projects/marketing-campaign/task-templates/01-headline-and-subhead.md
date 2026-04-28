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
4. Pick the one closest to the brand-voice anchors in `OR-001.brand_voice_anchor`. Write it under `## Headline`. **Multi-source voice composition** (v5.1): `brand_voice_anchor` may be a single string (v5.0.1 form) or a list of strings (v5.1 form). Treat a single-string value as a single-element list — there is nothing to compose, so just use it. For a list, compose the anchors in operator-declared priority order: the first listed anchor dominates on conflict; later anchors narrow or extend the first without overriding it. If a later anchor and the first contradict (e.g., a brand guide says "formal" and a competitor-tone analysis says "casual"), follow the first and note the conflict in the discoveries section of the completion report. If `brand_voice_anchor` is null, default to the rules-template Tier 4 STYLE.
5. Generate one subhead ≤ 25 words that names the offer outcome without claiming a specific revenue or earnings result.
6. Run banned-token scan against the rules table; reject any candidate containing a banned token.

## Completion Report

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [F-001#…], [DEC-001#…]
- **SCAN markers answered:** <count>
- **Outputs produced:** outputs/landing-page-copy.md (Headline, Subhead sections)
- **Discoveries:** <items>
- **Recommended follow-up artifacts:** "none" or "Write F-XXX capturing audience-language preference observed during candidate generation"

## Live-edit adaptation (v5.1.1)

This template is `delivery_mode: constrained` (draft to a file). If forked to `delivery_mode: live-edit` to mutate an existing landing-page headline/subhead in a CMS, replace step 2 with the v5.1.1 enumeration:

> Capture the pre-edit state (existing headline, subhead). Enumerate `edit_candidates` (the existing headline + subhead with proposed replacements), `create_candidates` (any net-new variant copy the rebrand mission implies — e.g., a new section heading), and `delete_candidates` (any obsolete copy the rebrand should remove). Do not pre-prune candidates based on perceived effort. The proposal phase enumerates; the council phase decides via `scope-shrink-watcher`.

See `core/TYPED-ARTIFACTS.md` §Live-Edit Proposal Artifacts for the per-candidate field shape and `schemas/projects/marketing-campaign/council.yaml` `scope-shrink-watcher` for the convergence contract.
