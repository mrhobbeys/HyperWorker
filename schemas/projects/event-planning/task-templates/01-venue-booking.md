---
id: T-001
kind: task
schema: event-planning
phase: 1
risk_level: critical
required_tools: [file_write, email_send]
delivery_mode: constrained
depends_on: [T-000]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-000#<short-hash>]"
acceptance_criteria:
  - "Venue contract signed; deposit invoice received and recorded as DEC-001."
  - "Insurance certificate window noted (Tier 1 lead-time AP)."
  - "Capacity matches OR-001.target_headcount with 10% buffer."
  - "Cancellation deadlines added to project calendar (DEC-001.cancellation_deadline)."
---

# Task T-001: Venue Booking  *(critical — non-refundable deposit risk)*

Critical risk: venue deposits are typically non-refundable, so changing this decision after signing has real cost. Council fires on completion to cascade-check downstream tasks.
