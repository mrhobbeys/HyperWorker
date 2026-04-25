---
id: T-006
kind: task
schema: software-feature-ship
phase: 2
risk_level: elevated
required_tools: [file_write, file_read, test_run]
delivery_mode: constrained
depends_on: [T-003, T-005]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-000#<short-hash>]"
acceptance_criteria:
  - "End-to-end test exercises the full user-observable behavior."
  - "Test runs against a staging-equivalent environment."
  - "Test command exits 0; council reviews coverage."
---

# Task T-006: Integration Tests  *(elevated)*

## Steps

1. Recite + SCAN.
2. Author end-to-end test that exercises the full feature.
3. Three failure scenarios: (a) database under load returning slow query, (b) frontend retry on 5xx, (c) auth boundary failure.
