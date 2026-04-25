---
id: T-002
kind: task
schema: event-planning
phase: 1
risk_level: standard
required_tools: [file_write, file_read]
delivery_mode: constrained
depends_on: [T-001]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-001#<short-hash>]"
acceptance_criteria:
  - "Budget broken out by category (venue / catering / AV / promotion / etc.) with line totals."
  - "Sum of allocations ≤ OR-001.budget.amount."
  - "Each line tagged refundable | non-refundable."
---

# Task T-002: Budget Allocation
