---
id: T-007
kind: task
schema: marketing-campaign
phase: 2
risk_level: elevated
required_tools: [file_write]
delivery_mode: constrained
depends_on: [T-006]
consumes:
  - "[OR-001#<short-hash>]"
  - "[F-001#<short-hash>]"
  - "[DEC-001#<short-hash>]"
  - "[DEC-002#<short-hash>]"
acceptance_criteria:
  - "Subject line ≤ 50 characters."
  - "Body 150–300 words."
  - "Single hard CTA: book a discovery call. Booking-page URL pulled from rules file."
  - "No earnings claim. No guarantee."
  - "CAN-SPAM elements present."
---

# Task T-007: Email 5 — Hard CTA to Book Discovery Call  *(elevated risk)*

## Objective

Final email in the sequence. The first four built trust; this one asks. Single hard CTA: book a discovery call. Elevated risk because the CTA email is the most likely to slip into earnings or guarantee claims.

## Step-by-Step Instructions

1. Recite + SCAN.
2. Draft a subject line that makes the next step explicit ("book your call" not "want to chat?").
3. One paragraph framing why now: time-bound based on the operator's actual capacity (`OR-001.team`), not invented urgency.
4. One paragraph stating exactly what the call is and what it isn't: free, no-pressure, fact-finding. No pricing.
5. Hard CTA with the canonical booking-page URL.
6. Footer.

## Failure Scenarios

1. **Scenario:** Reader books the call expecting a sales pitch.  
   **Outcome:** <fill in>  
   **Safe?** <yes/no>
2. **Scenario:** Reader books expecting a quoted price.  
   **Outcome:** <fill in>  
   **Safe?** <yes/no>
3. **Scenario:** Reader doesn't book — what does the email leave them with?  
   **Outcome:** <fill in>  
   **Safe?** <yes/no>

## Completion Report

- **Acceptance criteria:** <X/Y pass>
- **Failure scenarios:** 3 evaluated.
- **Outputs:** outputs/email-5-cta.md (DRAFT)
