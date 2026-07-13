---
id: T-005
kind: task
schema: market-gap-intelligence
phase: C
risk_level: standard
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-001]
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "Prior reports, decisions, and the client's existing positioning in the project are read for earlier wrong-turns."
  - "Each identified wrong-turn is registered as an anti-pattern artifact with prior_direction and a superseding_direction citation."
  - "Wrong-turns are preserved as cautionary signal, not silently dropped or re-litigated."
---

# Task T-005: Prior-Direction Anti-Pattern Capture

## Objective
Earlier strategic wrong-turns are signal, not noise. Capture them so the
recommendation does not silently repeat them and downstream agents inherit the
caution. This is where a premise like "we pivoted on a regulatory-news urgency
without checking competition" becomes a durable anti-pattern.

## Step-by-Step
1. Read OR-001, prior reports/spreadsheets in the project, and any existing
   Decisions. Look for directions that were taken on weak evidence, or abandoned
   for good reason.
2. For each, write an `anti-pattern` artifact: prior_direction (the wrong turn,
   verbatim where possible), why it was wrong, and superseding_direction
   ([DEC/F-NNN#hash] of the corrected direction once it exists — may be filled by T-008).
3. Do not re-argue settled directions; record and move on.
4. Append to evidence log. Answer @@SCAN markers.

## Completion Report
- Acceptance criteria: <X/Y>
- Outputs: AP-001…NNN
- Wrong-turns captured: <list>
- Open supersessions (to fill at T-008): <list>
