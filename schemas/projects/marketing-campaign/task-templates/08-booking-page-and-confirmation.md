---
id: T-008
kind: task
schema: marketing-campaign
phase: 3
risk_level: elevated
required_tools: [file_write]
delivery_mode: constrained
depends_on: [T-001, T-007]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-001#<short-hash>]"
  - "[DEC-002#<short-hash>]"
acceptance_criteria:
  - "Booking page page-copy section: under 80 words, single CTA on the form."
  - "Confirmation page (post-submit) sets clear expectations for what happens next."
  - "Calendar embed contract noted (operator handles configuration; this task is copy only)."
  - "Tone matches DEC-002. Zero Tier 1 banned tokens."
  - "Saved as DRAFT."
---

# Task T-008: Booking Page Copy + Post-Submit Confirmation  *(elevated risk)*

## Objective

The funnel's terminal step. Two short pieces of copy: the booking-page form area and the post-submit confirmation. Calendar configuration is out of scope; this task produces copy only.

## Step-by-Step Instructions

1. Recite + SCAN.
2. Draft booking-page copy: a one-sentence headline matching `DEC-001`'s offer phrasing, two-sentence supporting text, single CTA on the form ("Book a call"), no pricing.
3. Draft confirmation copy: short headline, three-bullet "what happens next" list, one closing line that previews the call's first question.
4. Banned-token scan, tone match, word counts.

## Failure Scenarios

1. **Scenario:** Booker arrives expecting different content than the email promised.  
   **Outcome:** <fill in>  
   **Safe?** <yes/no>
2. **Scenario:** Calendar is broken; submit-handler fails silently.  
   **Outcome:** <fill in — task should note calendar verification is operator's responsibility>  
   **Safe?** <yes/no>
3. **Scenario:** Booker sees the confirmation, then cancels two days later.  
   **Outcome:** <fill in>  
   **Safe?** <yes/no>

## Completion Report

- **Acceptance criteria:** <X/Y pass>
- **Outputs:** outputs/booking-page-copy.md, outputs/booking-confirmation.md (both DRAFT)

## Live-edit adaptation (v5.1.1)

This template is `delivery_mode: constrained`. A live-edit fork against an existing booking page (e.g., MS Bookings, Calendly intro page, or a CMS-hosted booking landing) uses the v5.1.1 enumeration:

- **edit_candidates:** existing booking-page headline, supporting text, CTA copy, confirmation copy.
- **create_candidates:** any net-new sections the rebrand mission implies (a new pre-call FAQ, a new "what to expect" block).
- **delete_candidates:** obsolete copy from a prior brand iteration.

Do not pre-prune. `scope-shrink-watcher` reviews completeness in council. See `core/TYPED-ARTIFACTS.md` §Live-Edit Proposal Artifacts.

### Redirect implications (v5.1.1)

If a live-edit fork moves the booking page to a new URL (e.g., from `/book-a-call/` to `/cybersecurity-review/`), populate `redirect_implications` in the completion report. The from→to redirect preserves any inbound traffic from the prior CTA links. At session.handoff, every row with `status: applied` must have a paired `external_state.read_back` against the platform's redirections-list endpoint. See `templates/artifact-templates/redirect-coverage-report.md`.
