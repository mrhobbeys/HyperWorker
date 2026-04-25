---
id: T-004
kind: task
schema: marketing-campaign
phase: 2
risk_level: standard
required_tools: [file_write]
delivery_mode: constrained
depends_on: [T-003]
consumes:
  - "[OR-001#<short-hash>]"
  - "[F-001#<short-hash>]"
  - "[DEC-001#<short-hash>]"
  - "[DEC-002#<short-hash>]"
acceptance_criteria:
  - "Subject line ≤ 50 characters."
  - "Body 150–300 words."
  - "Names a specific problem from F-001 (audience pain) without claiming a specific outcome."
  - "Zero Tier 1 banned tokens."
  - "CAN-SPAM elements present."
---

# Task T-004: Email 2 — Problem Agitation

## Objective

Second email in the sequence. Names the audience's pain in concrete language, without solutioning. Builds urgency around the cost of leaving the problem unsolved. No income claims, no false scarcity.

## Step-by-Step Instructions

1. Recite + SCAN.
2. Draft subject line referencing the problem in plain language (not "are you struggling with X?" — too generic).
3. Open with a specific scenario: a moment in the audience's day when the pain shows up.
4. Two short paragraphs naming the cost of inaction. Cite no metrics that aren't in the safe-claims list.
5. Soft CTA — reply or read a resource. Booking page still off-limits.
6. Footer.

## Completion Report

- **Acceptance criteria:** <X/Y pass>
- **Outputs:** outputs/email-2-problem-agitation.md (DRAFT)
