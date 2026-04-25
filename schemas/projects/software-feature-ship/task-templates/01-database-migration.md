---
id: T-001
kind: task
schema: software-feature-ship
phase: 1
risk_level: elevated
required_tools: [file_write, file_read, sql_validate]
delivery_mode: constrained
depends_on: [T-000]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-000#<short-hash>]"
acceptance_criteria:
  - "Forward migration applies cleanly against a schema-equivalent staging database."
  - "Down migration applies cleanly and reverts all forward changes."
  - "Migration is idempotent under retry (running twice is a no-op the second time, or fails before partial state)."
  - "No data loss on rollback (down migration preserves pre-existing rows)."
---

# Task T-001: Database Migration  *(elevated risk)*

## Steps

1. Recite + SCAN.
2. Author forward migration in `migrations/<timestamp>_<name>.up.sql`.
3. Author down migration in `migrations/<timestamp>_<name>.down.sql`.
4. Validate against staging schema clone.
5. Three failure scenarios required: (a) rollback after partial production write, (b) concurrent forward migration on a separate replica, (c) downstream service running pre-migration code reading post-migration schema.

## Failure Scenarios

1. **Scenario:** Rollback during production traffic.  
   **Outcome:** <fill in>  
   **Safe?** <yes/no>
2. **Scenario:** Concurrent migration on a replica.  
   **Outcome:** <fill in>  
   **Safe?** <yes/no>
3. **Scenario:** Pre-migration service reads post-migration schema.  
   **Outcome:** <fill in>  
   **Safe?** <yes/no>
