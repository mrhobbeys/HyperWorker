---
id: T-007
kind: task
schema: software-feature-ship
phase: 3
risk_level: elevated
required_tools: [deploy_trigger, monitoring_read, http_fetch, file_write]
delivery_mode: prescribed
depends_on: [T-006]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-000#<short-hash>]"
acceptance_criteria:
  - "Staging deploy succeeds; deploy ID recorded."
  - "Smoke test exercises one happy path and one error path; both pass."
  - "Monitoring shows no error-rate increase 15 minutes post-deploy."
---

# Task T-007: Staging Deploy + Smoke  *(elevated)*

## Steps

1. Recite + SCAN.
2. Trigger staging deploy via the documented deploy command.
3. Smoke test: happy path + error path.
4. Read monitoring 15 minutes post-deploy; record error-rate baseline-after.
5. Three failure scenarios: (a) deploy partially succeeds, (b) smoke test passes but monitoring shows latency regression, (c) deploy succeeds but downstream service returns stale cache.
