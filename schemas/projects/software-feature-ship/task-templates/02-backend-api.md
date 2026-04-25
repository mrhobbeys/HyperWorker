---
id: T-002
kind: task
schema: software-feature-ship
phase: 1
risk_level: standard
required_tools: [file_write, file_read, code_lint]
delivery_mode: constrained
depends_on: [T-001]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-000#<short-hash>]"
acceptance_criteria:
  - "Endpoint signature matches DEC-000 contract diff."
  - "Input validation on all parameters (Tier 1 SECURITY)."
  - "Lint passes on changed files."
  - "No new external dependency added unless DEC-XXX records the choice."
---

# Task T-002: Backend API

Implement the new endpoints declared in `DEC-000`'s API contract diff. Tests are a separate task (T-003).

## Steps

1. Recite + SCAN.
2. Implement endpoints in code.
3. Lint pass.
4. Note any deviation from `DEC-000` in completion report; if behavior changed, write a follow-up `DEC-XXX` instead of editing.
