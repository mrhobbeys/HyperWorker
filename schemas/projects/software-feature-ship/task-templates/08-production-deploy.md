---
id: T-008
kind: task
schema: software-feature-ship
phase: 3
risk_level: critical
required_tools: [deploy_trigger, monitoring_read, http_fetch, file_write]
delivery_mode: prescribed
depends_on: [T-007]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-000#<short-hash>]"
acceptance_criteria:
  - "Pre-deploy council passes (contract-stability, test-coverage, security, rollback)."
  - "Production deploy succeeds; deploy ID recorded."
  - "Smoke test in production passes."
  - "Monitoring shows no error-rate increase 30 minutes post-deploy."
  - "Rollback plan rehearsed and timing recorded (target: < 5 minutes to revert)."
---

# Task T-008: Production Deploy  *(critical)*

## Steps

1. Recite + SCAN. Confirm OR-001 declares this task is allowed under operator authority.
2. Pre-deploy council fires automatically. Wait for `council.converged`.
3. Trigger production deploy.
4. Smoke test.
5. Monitoring 30-minute window; baseline-after recorded.
6. Three failure scenarios: (a) deploy succeeds but immediate error spike, (b) deploy succeeds but cache invalidation fails, (c) rollback triggered — does the down-migration from T-001 succeed cleanly under production traffic?
