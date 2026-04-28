---
id: T-006
kind: task
schema: marketing-campaign
phase: 2
risk_level: standard
required_tools: [file_write]
delivery_mode: constrained
depends_on: [T-005]
consumes:
  - "[OR-001#<short-hash>]"
  - "[F-001#<short-hash>]"
  - "[DEC-001#<short-hash>]"
  - "[DEC-002#<short-hash>]"
acceptance_criteria:
  - "Subject line ≤ 50 characters."
  - "Body 150–300 words."
  - "Names the top three objections (typically: price, time, trust) and addresses each in one paragraph."
  - "Address-of-objection language is direct, not evasive ('it's not for everyone' is not an objection answer)."
  - "CAN-SPAM elements present."
---

# Task T-006: Email 4 — Objection Handling

## Objective

Fourth email — handle the top three objections explicitly. Each gets one short paragraph. No "this is the only solution" language; no "but with us…" pivots that read as defensive.

## Step-by-Step Instructions

1. Recite + SCAN.
2. Identify the top three objections from `F-001` audience-description and the operator's stated context. If fewer than three are documented, ask the operator before drafting.
3. For each, draft one paragraph that acknowledges the objection in the audience's words and answers it without overclaiming.
4. Soft CTA — visit a resource or reply.
5. Footer.

## Completion Report

- **Acceptance criteria:** <X/Y pass>
- **Outputs:** outputs/email-4-objections.md (DRAFT)

## Live-edit adaptation (v5.1.1)

This template is `delivery_mode: constrained`. A live-edit fork uses the v5.1.1 enumeration: `edit_candidates` for the existing objections-email subject + body, `create_candidates` empty for a single-slot replacement (state explicitly), `delete_candidates` for obsolete objection responses no longer relevant. See `core/TYPED-ARTIFACTS.md` §Live-Edit Proposal Artifacts.
