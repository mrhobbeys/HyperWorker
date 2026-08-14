---
id: T-XXX
kind: task
schema: <project-schema>
phase: 1
risk_level: standard            # standard | elevated | critical (locked at authoring)
required_tools: [file_write]    # see .hyperworker/agents/<agent>.yaml provides
delivery_mode: constrained      # prescribed | constrained | bounded-iteration | ab-variant
# ab_variant_count and ab_variant_axis are required iff delivery_mode is ab-variant.
# ab_variant_count: 3                # integer, range 2-5; default 3
# ab_variant_axis: "primary CTA framing"  # string; the dimension variants differ on
depends_on: []
# read_only_pass: true               # optional (v6.0.0) — read, measure, capture, report;
                                      # mutate nothing this pass. May be added AFTER the task
                                      # is issued; the executor picks it up by re-reading this
                                      # file immediately before its first state-changing
                                      # action. See SUBSTRATE.md §Read-Only Pass.
# lightweight_completion: true       # optional — see SUBSTRATE.md §Lightweight Completion.
                                      # When true, completion report is a 3-line summary
                                      # (acceptance criteria result, outputs, follow-up).
                                      # Use only for mechanical tasks (standard risk).
                                      # Locked at authoring; cannot be opted into mid-task.
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
# ab_variant_count, ab_variant_axis:
#   required iff delivery_mode is ab-variant — see Atomicity §Delivery Modes
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

## Lightweight Completion (used iff frontmatter `lightweight_completion: true`)

When `lightweight_completion: true` is set in frontmatter, replace the full completion report above with a 3-line summary:

- **Acceptance criteria:** <X/Y pass>
- **Outputs:** <paths>
- **Follow-up:** <one-line note or "none">

The `task.complete` event still emits with `completion_report_path`. Layer 2 still runs. The full template applies for elevated/critical risk tasks regardless; `lightweight_completion` is for standard-risk mechanical work (anti-pattern extraction from supersede chains, declarative structure decisions, mechanical inventories) where the event log carries the substantive state. Do not set this flag on judgment work — the failure mode is a 3-bullet "X/Y pass / outputs / none" summary that hides a Tier 1 violation the full completion report would have surfaced.
