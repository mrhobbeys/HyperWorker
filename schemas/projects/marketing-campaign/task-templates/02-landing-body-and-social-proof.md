---
id: T-002
kind: task
schema: marketing-campaign
phase: 1
risk_level: standard
required_tools: [file_write]
delivery_mode: constrained
depends_on: [T-001]
consumes:
  - "[OR-001#<short-hash>]"
  - "[F-001#<short-hash>]"
  - "[DEC-001#<short-hash>]"
  - "[DEC-002#<short-hash>]"          # tone-of-voice schema, written during T-001 if needed
acceptance_criteria:
  - "Body copy contains a problem section, an outcome section, and a CTA section."
  - "Single CTA — no split attention."
  - "Social proof section cites only verifiable client results from operator's safe-claims list."
  - "Reading level Flesch-Kincaid ≤ 8."
  - "Zero Tier 1 banned tokens."
---

# Task T-002: Landing Page Body and Social Proof

## Objective

Extend `outputs/landing-page-copy.md` with a body section and a social-proof section. The headline and subhead from T-001 are the visual top; this task fills the rest of the page. One CTA only.

## Step-by-Step Instructions

1. Recite consumed artifacts.
2. Answer SCAN markers.
3. Draft the body in three blocks (problem → outcome → CTA), each 1–3 short paragraphs.
4. Draft the social-proof section using only entries from the safe-claims list in `00-REFERENCE-rules.md`. If a candidate claim is not on the safe list and not anchored to a finding, drop it.
5. Banned-token scan and reading-level check against acceptance criteria.

## Completion Report

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [F-001#…], [DEC-001#…], [DEC-002#…]
- **SCAN markers answered:** <count>
- **Outputs produced:** outputs/landing-page-copy.md (Body, Social Proof sections)
- **Discoveries:** <items>

## Live-edit adaptation (v5.1.1)

This template is `delivery_mode: constrained` (draft to a file). If forked to `delivery_mode: live-edit` to mutate an existing landing page (rebrand, content refresh), replace step 1's Recite step with a pre-edit-state capture + enumeration:

> Capture the pre-edit state of the landing page (DOM or CMS export). Enumerate `edit_candidates` (existing body sections, social-proof blocks, CTAs to revise — each with proposed change), `create_candidates` (new sections the rebrand implies — e.g., a vertical-specific section, a new social-proof category), and `delete_candidates` (obsolete sections to remove). Do not pre-prune. The proposal phase enumerates; `scope-shrink-watcher` reviews completeness in council.

See `core/TYPED-ARTIFACTS.md` §Live-Edit Proposal Artifacts.

### Redirect implications (v5.1.1)

If a live-edit fork of this task renames the landing-page slug, trashes a section that lived at its own URL, or restructures the page hierarchy, populate `redirect_implications` in the completion report:

```yaml
redirect_implications:
  - from_url: "/old-landing/"
    to_url: "/new-landing/"
    reason: "rebrand slug rename; preserves inbound links"
    status: planned
```

Set `status: excluded` with a reason for intentional 410-Gone removals (e.g., a deprecated offer that should not redirect anywhere). At session.handoff, every row with `status: applied` must have a paired `external_state.read_back` against the platform's redirections-list endpoint. See `templates/artifact-templates/redirect-coverage-report.md`.
