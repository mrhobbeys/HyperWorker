---
id: T-002
kind: task
schema: cleanroom-rebuild
phase: B
risk_level: standard
required_tools: [file_write, app_driver, gui_driver, screenshot, vision_describe]
delivery_mode: constrained
depends_on: [T-001]
consumes:
  - "[OR-001#<short-hash>]"
  - "[OBS-NNN#<short-hash>]"  # the screen-inventory OBS for the screen(s) this branch captures
acceptance_criteria:
  - "Every in-scope screen from the T-000 inventory is captured: one OBS (observation_type: screen) per screen state, with a screenshot under observed/ referenced in artifact_path."
  - "Each screen OBS has a vision-derived description produced by the LOCAL VLM (vision_describe), keeping original imagery off any build context."
  - "Navigation edges between screens are captured as OBS (observation_type: navigation-edge), forming a navigation graph; every edge cites its source/target screen OBS."
  - "All OBS carry source=original, zone=observed, consumable_by_build=false; this task writes only to observed/ (Layer 1 zone-write-discipline)."
  - "Zero Tier 1 violations from 00-REFERENCE-rules."
---

# Task T-002: Screen / Flow Capture

## Objective

Drive the original GUI, capture each screen state, describe each via a local vision model, and build the navigation graph. This is an observation-room task (`screen-flow-capture` kind): it faces the original (`app_driver`, `gui_driver`), reads and writes only `observed/`. It is a strong subagent fit — per-screen capture is hermetic.

## Branching Note

For systems with many screens, branch one subagent per screen via `hw branch T-002 screen-NNN` and fold back with each branch's OBS count. Subagents need `file_write`, `gui_driver`, `screenshot`, `vision_describe`; capability gates enforce. Note the rationale in capability-gates.yaml: vision description runs on a LOCAL VLM so original imagery never enters a build context.

## Step-by-Step Instructions

1. Recite OR-001 and the assigned screen-inventory OBS. SCAN (not a build-room task).
2. For the assigned screen, drive the original to that state with `gui_driver`.
3. Capture a screenshot; store it under `observed/screens/<screen-id>.png` and reference it in the OBS `artifact_path`.
4. Run `vision_describe` (LOCAL VLM) on the screenshot. Write an OBS with `observation_type: screen`, `capture_method: gui-driver`, `source_ref` = screen id, and the vision description in the body.
5. For each control/exit that navigates to another screen, capture a `navigation-edge` OBS citing the source and target screen OBS.
6. Write each via `hw add observation < draft-obs-NNN.md`. Confirm `source: original`, `zone: observed`, `consumable_by_build: false`.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [OBS-NNN#…]
- **SCAN markers answered:** <count>
- **Zones read / written:** read: observed / written: observed
- **Outputs produced:** screen OBS [OBS-… through OBS-…]; navigation-edge OBS [...]; screenshots under observed/screens/
- **Screens captured / unreachable:** <list; note any screen that could not be reached and why>
- **Recommended follow-up:** "Spec room: screen-specs (T-007) consume these OBS."
