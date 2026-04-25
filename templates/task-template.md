---
id: T-XXX
kind: task
schema: <project-schema>
phase: 1
risk_level: standard            # standard | elevated | critical (locked at authoring)
required_tools: [file_write]    # see .hyperworker/agents/<agent>.yaml provides
delivery_mode: constrained      # prescribed | constrained | bounded-iteration
depends_on: []
consumes:
  - "[OR-001#<short-hash>]"     # operating-reality
  # - "[DEC-XXX#<short-hash>]"  # decision
  # - "[F-XXX#<short-hash>]"    # finding (validated or provisional)
  # - "[AP-XXX#<short-hash>]"   # anti-pattern
acceptance_criteria:
  - "<observable, pass/fail criterion>"
  - "<observable, pass/fail criterion>"
  - "Zero Tier 1 violations from 00-REFERENCE-rules."
# preview_surface, version_naming, convergence_criterion, max_passes:
#   required iff delivery_mode is bounded-iteration
---

# Task T-XXX: <Descriptive Title>

## Objective

<One paragraph stating the exact end state. Specific, observable, scoped to the consumed inputs.>

## Step-by-Step Instructions

1. <Exact instruction. Cite consumed artifacts inline by ID where relevant.>
2. <Next step.>
3. <…>

## Field-Value Map (UI tasks only — remove if unused)

| Field | Target Value | Source |
|---|---|---|
| <field name> | <exact value> | <[KIND-ID#hash] or task-internal> |

## Failure Scenarios (required iff risk_level ∈ {elevated, critical} AND output is end-user-facing)

1. **Scenario:** <realistic situation in which a real end-user follows this output>  
   **Outcome:** <what actually happens>  
   **Safe?** <yes / no — single no blocks the task>
2. ...
3. ...

## Completion Report (filled by executor before `hw write --status complete`)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** <list of artifact IDs with paraphrase status>
- **SCAN markers answered:** <count>
- **Outputs produced:** <paths>
- **Discoveries (raw):** <items the executor surfaces; planner decides whether to write findings/anti-patterns>
- **Recommended follow-up artifacts:** <"Write F-… capturing X" / "Write AP-… capturing Y" / "none">
