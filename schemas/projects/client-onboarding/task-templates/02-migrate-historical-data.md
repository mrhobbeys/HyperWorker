---
id: T-002
kind: task
schema: client-onboarding
phase: 1
risk_level: elevated
required_tools: [import_tool, file_read, file_write]
delivery_mode: prescribed
depends_on: [T-001]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-001#<short-hash>]"
acceptance_criteria:
  - "Source data delimiter, encoding, and schema validated before import (cross-project AP: CSV semicolon-vs-comma)."
  - "Import record count matches source record count."
  - "Sample of 25 randomly-selected records verified field-by-field."
  - "Logged: timestamp, source, destination, record count (Tier 1)."
---

# Task T-002: Historical Data Migration  *(elevated; critical if HIPAA)*

## Steps

1. Recite + SCAN. Read subscribed APs with `integration: data-import`.
2. Validate source data: delimiter, encoding, schema.
3. Run import.
4. Verify counts; sample 25 records.
5. Three failure scenarios.
