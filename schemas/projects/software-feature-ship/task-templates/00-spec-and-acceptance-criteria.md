---
id: T-000
kind: task
schema: software-feature-ship
phase: 1
risk_level: standard
required_tools: [file_write]
delivery_mode: constrained
depends_on: []
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "Spec names the user-observable behavior change in one paragraph."
  - "API contract diff (added/changed/removed endpoints) listed."
  - "Database schema diff listed (or 'none')."
  - "Acceptance criteria are observable and pass/fail."
---

# Task T-000: Feature Spec + Acceptance Criteria

Produce `DEC-000` capturing the feature decision and a spec body in `docs/spec.md`. The spec is consumed by every downstream task.

## Steps

1. Recite `OR-001`. Confirm CI/CD provider and required status checks are visible.
2. Draft `DEC-000` with title, alternatives considered, rationale, and `surface: cross-surface` if multi-surface.
3. Author `docs/spec.md` with: behavior change, API contract diff, schema diff, acceptance criteria.
4. Run `hw add decision < draft-dec-000.md`.
