---
id: T-007
kind: task
schema: cleanroom-rebuild
phase: C
risk_level: standard
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-002, T-005]
consumes:
  - "[OR-001#<short-hash>]"
  - "[OBS-NNN#<short-hash>]"  # screen + navigation-edge OBS
  - "[SPEC-NNN#<short-hash>]"  # data-dictionary SPEC for fields bound to the screen
acceptance_criteria:
  - "Every captured screen (OBS observation_type: screen) is covered by a SPEC (spec_type: screen-spec): layout, fields, controls, validation, and navigation, in our own words. (Layer 2 screen_spec_coverage requires full coverage before the build room opens.)"
  - "Navigation is specified from the navigation-edge OBS as a SPEC (spec_type: navigation-spec) or within the screen-specs."
  - "Each screen-spec cites the screen OBS (and data-dictionary SPEC for bound fields) in derived_from."
  - "UI strings retained verbatim are listed in verbatim_carryover with justification; no copyrighted UI text is carried into the rebuilt app beyond functional necessity."
  - "All SPEC carry source=cleanroom, zone=spec, consumable_by_build=true; reads observed+spec, writes only spec/."
  - "Zero Tier 1 violations from 00-REFERENCE-rules."
---

# Task T-007: Screen Specs

## Objective

Re-express each captured screen as a cleanroom screen spec the build room can implement, and the navigation graph as a navigation spec. Spec-room task (`spec-author` kind): reads `observed/` + `spec/`, writes only `spec/`. Layer 2 `screen_spec_coverage` will block the spec->build boundary if any captured screen is uncovered.

## Step-by-Step Instructions

1. Recite OR-001, the screen/navigation OBS, and the data-dictionary SPEC. SCAN: confirm @@SCAN_2_1 / @@SCAN_2_2. Not a build-room task.
2. For each screen OBS, author a SPEC (`spec_type: screen-spec`): describe layout regions, each field (bound to a data-dictionary SPEC entry where applicable), controls, validation behavior, and on-screen logic — in our own words from the vision description, not the original imagery.
3. Author navigation: either a `navigation-spec` SPEC built from the navigation-edge OBS, or a §Navigation section per screen-spec citing the edges.
4. List any UI string retained verbatim (e.g., a regulated label) in `verbatim_carryover` with justification. Otherwise re-word.
5. Cite source OBS (and bound-field SPEC) in `derived_from`.
6. `hw add spec < draft-spec-NNN.md`. Confirm `source: cleanroom`, `zone: spec`, `consumable_by_build: true`.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [OBS-NNN#…], [SPEC-NNN#…]
- **SCAN markers answered:** <count>
- **Zones read / written:** read: observed, spec / written: spec
- **Outputs produced:** screen-spec / navigation-spec SPEC [SPEC-… through SPEC-…]
- **Screen coverage:** <N of M captured screens specced; list any uncovered + reason>
- **Verbatim UI strings retained:** <list with justification>
- **Recommended follow-up:** "Build-from-spec (T-010) implements these screen-specs."
