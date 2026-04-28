---
id: T-003
kind: task
schema: marketing-campaign
phase: 2
risk_level: standard
required_tools: [file_write]
delivery_mode: constrained
depends_on: [T-001]
consumes:
  - "[OR-001#<short-hash>]"
  - "[F-001#<short-hash>]"
  - "[DEC-001#<short-hash>]"
  - "[DEC-002#<short-hash>]"
acceptance_criteria:
  - "Subject line ≤ 50 characters."
  - "Body 150–300 words."
  - "Single CTA — must NOT be the booking page (that's T-007)."
  - "CAN-SPAM unsubscribe link present (Tier 1)."
  - "Physical mailing address present (Tier 1)."
  - "Tone matches DEC-002 schema."
  - "Reading level Flesch-Kincaid ≤ 8."
  - "Saved as DRAFT (not sent)."
---

# Task T-003: Email 1 — Welcome and Value Proposition

## Objective

First email in the nurture sequence; fires immediately after form submission. Confirm the subscriber made a good decision, deliver any promised value, and set expectations. Soft CTA only — do not push the booking page yet.

## Step-by-Step Instructions

1. Recite consumed artifacts.
2. Answer SCAN markers.
3. Draft a subject line ≤ 50 characters that feels personal, not promotional. Avoid spam trigger words (acceptance criterion).
4. Open with a one-line acknowledgment.
5. Deliver core value in 2–3 sentences that mirror the landing-page headline language.
6. Set expectations for the next emails in one sentence.
7. Single soft CTA — reply to the email or visit a resource. Do NOT push the booking page.
8. Footer: unsubscribe link + physical address pulled from `OR-001.contact_info`.
9. Banned-token scan, word count, reading level.

## Completion Report

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [F-001#…], [DEC-001#…], [DEC-002#…]
- **SCAN markers answered:** <count>
- **Outputs produced:** outputs/email-1-welcome.md (DRAFT)
- **Discoveries:** <items>

## Live-edit adaptation (v5.1.1)

This template is `delivery_mode: constrained` (draft email; operator publishes via the email platform). A live-edit fork would target an existing automation slot (e.g., editing an existing welcome email in Mailster/Mailchimp). For that fork:

- **edit_candidates:** the existing welcome email's subject + body (proposed replacement copy).
- **create_candidates:** likely empty for this slot — no `create_candidates` expected for this task shape, single-email replacement only. State this explicitly in the proposal so the omission is intentional, not a scope-shrink slip.
- **delete_candidates:** any out-of-date footer fragments, expired CTAs.

See `core/TYPED-ARTIFACTS.md` §Live-Edit Proposal Artifacts.
