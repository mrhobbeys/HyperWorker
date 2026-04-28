---
id: T-005
kind: task
schema: marketing-campaign
phase: 2
risk_level: elevated
required_tools: [file_write]
delivery_mode: constrained
depends_on: [T-004]
consumes:
  - "[OR-001#<short-hash>]"
  - "[F-001#<short-hash>]"
  - "[DEC-001#<short-hash>]"
  - "[DEC-002#<short-hash>]"
  - "[F-XXX#<short-hash>]"            # finding capturing the verifiable client story (operator-provided)
acceptance_criteria:
  - "Subject line ≤ 50 characters."
  - "Body 150–300 words."
  - "Every claim sources to F-XXX or to the safe-claims list. Zero unverifiable claims."
  - "No fabricated testimonials. Names and outcomes are real and permissioned."
  - "CAN-SPAM elements present."
---

# Task T-005: Email 3 — Case Study / Proof  *(elevated risk)*

## Objective

Third email — a proof story. Elevated risk because Tier 1 prohibits fabricated social proof and the failure mode is producing an "illustrative" example that reads as real. The story must source to a finding (`F-XXX`) the operator captured during discovery, with explicit permission noted.

## Step-by-Step Instructions

1. Recite + SCAN. The proof finding's recitation must include the permission-status field.
2. Verify the finding's `confidence` is `validated` (not `provisional`). If provisional, block: a proof email cannot consume a provisional client story.
3. Draft the email as a 3-act narrative: situation → action → outcome. Names and metrics taken verbatim from the finding.
4. Three failure scenarios required (elevated risk + end-user-facing). Document in completion report.

## Failure Scenarios

1. **Scenario:** Reader infers the named client outcome is typical and expects similar.  
   **Outcome:** <fill in>  
   **Safe?** <yes/no>
2. **Scenario:** Named client sees the email and disputes a detail.  
   **Outcome:** <fill in>  
   **Safe?** <yes/no>
3. **Scenario:** Compliance audit asks for the source of the metric stated in the email.  
   **Outcome:** <fill in — must point at F-XXX>  
   **Safe?** <yes/no>

## Completion Report

- **Acceptance criteria:** <X/Y pass>
- **Failure scenarios:** 3 evaluated; <X> pass.
- **Outputs:** outputs/email-3-proof.md (DRAFT)

## Live-edit adaptation (v5.1.1)

This template is `delivery_mode: constrained`. A live-edit fork against an existing email automation step uses the v5.1.1 enumeration: `edit_candidates` for the existing proof email's subject + body, `create_candidates` empty for a single-slot replacement (state explicitly), `delete_candidates` for obsolete proof references. See `core/TYPED-ARTIFACTS.md` §Live-Edit Proposal Artifacts.
