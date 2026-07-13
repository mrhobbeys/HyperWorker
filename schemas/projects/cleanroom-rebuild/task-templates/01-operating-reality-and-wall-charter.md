---
id: T-001
kind: task
schema: cleanroom-rebuild
phase: A
risk_level: standard
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-000]
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "OR-001 is populated with legacy_system, target_stack, data_strategy, wall_strictness, build_executor, observation_oracle, and deliverable_path (all required fields present and well-typed)."
  - "build_executor names a LOCAL endpoint structurally incapable of reaching the original; the completion report states why it cannot reach the original (no app_driver / no network-to-original)."
  - "Tier 1 CLEANROOM-WALL in 00-REFERENCE-rules.md is populated with the project's concrete build_executor id, and the wall SCAN markers are present."
  - "Tier 4 STYLE is populated (or explicitly marked 'no operator override beyond schema defaults')."
  - "Banned-tokens and canonical-facts tables are either populated with operator-confirmed entries OR marked empty (headers retained, body explicitly empty)."
  - "Zero Tier 1 violations from 00-REFERENCE-rules."
---

# Task T-001: Operating Reality + Wall Charter

## Objective

Lock the project's operating reality and the cleanroom wall before any observation or build work. Confirm OR-001 carries the rebuild's stack/data/wall fields, and encode the wall as concrete Tier 1 rules in `00-REFERENCE-rules.md` — substituting the project's real `build_executor` id so downstream tasks re-anchor on the actual walled endpoint. This is a setup task (`target-inventory` kind, read/write to observed/spec/src as needed for charter authoring); it does not face the original.

## Step-by-Step Instructions

1. Recite OR-001. Confirm `legacy_system`, `target_stack`, `data_strategy`, `wall_strictness`, `build_executor`, `observation_oracle`, `deliverable_path` are all present. If any is missing, block with `reason: or_incomplete` and ask the operator.
2. **Build-executor isolation check.** Confirm `build_executor` is a local endpoint (e.g., `lmstudio:...`) with no `app_driver` and no network path to the original. Record the justification in the completion report. If it can reach the original, block — the wall cannot stand.
3. SCAN: answer the @@SCAN markers (this is not a build-room task).
4. **Wall charter:** in `00-REFERENCE-rules.md`, populate Tier 1 CLEANROOM-WALL. Replace the `{{ build_executor }}` placeholder with the actual endpoint id from OR-001. Confirm @@SCAN_1_1, @@SCAN_1_2, @@SCAN_1_3 are present verbatim.
5. **Style anchor:** populate Tier 4 STYLE with the target-stack idiom from OR-001.target_stack, or write the explicit line `No operator override beyond schema defaults; citation format per SUBSTRATE.md §Citation Format.`
6. **Banned tokens / canonical facts.** If original product names/trademarks must be kept out of the rebuilt app's user-facing surface, populate the banned-tokens table. If protocol literals / data-field names must appear verbatim for interop, populate canonical facts. If neither applies, retain the headers with an explicit empty row.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…]
- **SCAN markers answered:** <count>
- **Zones read / written:** read: spec / written: spec (rules file is project-canonical)
- **Outputs produced:** updated OR-001 (if amended), updated 00-REFERENCE-rules.md (Tier 1 wall + Tier 4 + tables)
- **Build-executor isolation justification:** <why build_executor cannot reach the original>
- **Recommended follow-up:** "Operator review the wall charter before observation begins."
