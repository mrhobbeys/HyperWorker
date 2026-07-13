---
id: T-002
kind: task
schema: opportunity-hunt
phase: B
risk_level: elevated
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-001]
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "Every open Finding has a status: pursuing | watch | excluded (with reason)."
  - "Each pursuing Finding is eligibility-checked against OR-001 (actionable now, or teaming/sub, or blocked)."
  - "Findings are ranked: eligibility > fit > value > effort > deadline proximity."
---

# Task T-002: Qualify & Prioritize

## Steps
1. Read OR-001 + all open Findings.
2. For each, score fit, eligibility, and effort; set status pursuing | watch | excluded (reason).
3. Flag any that need teaming/subcontracting (eligibility gates we don't meet; capability gaps → the OR-001 subcontracting partner).
4. Produce a ranked shortlist for pursuit.

## Completion Report
- Pursuing: <IDs ranked>  |  Watch: <IDs>  |  Excluded: <IDs + reasons>
- Teaming/sub needed: <IDs>
- Recommended top pursuit: <ID + why>
