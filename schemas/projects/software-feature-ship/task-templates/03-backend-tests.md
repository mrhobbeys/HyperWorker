---
id: T-003
kind: task
schema: software-feature-ship
phase: 1
risk_level: standard
required_tools: [file_write, file_read, test_run]
delivery_mode: constrained
depends_on: [T-002]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-000#<short-hash>]"
acceptance_criteria:
  - "Every new code path in T-002 has at least one unit test (Tier 3)."
  - "Test command exits 0; declared in @@SCAN_3_1."
  - "No flake detected in three consecutive runs."
---

# Task T-003: Backend Tests

## Steps

1. Recite + SCAN.
2. Author unit tests for new endpoints.
3. Run test suite three times; record exit code and duration each run.
