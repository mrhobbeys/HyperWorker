---
id: T-005
kind: task
schema: cleanroom-rebuild
phase: C
risk_level: standard
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-000, T-003]
consumes:
  - "[OR-001#<short-hash>]"
  - "[OBS-NNN#<short-hash>]"  # catalog + trace OBS describing the data layer
acceptance_criteria:
  - "Every in-scope table/view/column observed in T-000/T-003 is described in a SPEC (spec_type: data-dictionary): name, type, semantics, constraints, relationships — in our own words."
  - "Each data-dictionary SPEC cites the OBS it derives from in derived_from (at least one [OBS-NNN#hash])."
  - "Data-field names retained verbatim for interop are listed in verbatim_carryover with justification (functional necessity); no other verbatim original expression."
  - "All SPEC carry source=cleanroom, zone=spec, consumable_by_build=true; this task reads observed+spec and writes only spec/."
  - "Zero Tier 1 violations from 00-REFERENCE-rules."
---

# Task T-005: Data Dictionary

## Objective

Re-express the original's data layer as a cleanroom data dictionary the build room can implement against. Spec-room task (`spec-author` kind): reads `observed/` + `spec/`, writes only `spec/`. This is one of the only tasks that reads OBS — it must introduce no verbatim original expression beyond functional necessity (data-field names, where interop requires them).

## Step-by-Step Instructions

1. Recite OR-001 and the catalog/trace OBS. SCAN: confirm @@SCAN_2_1 (every SPEC cites an OBS) and @@SCAN_2_2 (no over-quoting). Not a build-room task.
2. For each table/view, author a SPEC (`spec_type: data-dictionary`): describe each column's type, meaning, constraints, and relationships in our own words.
3. Cite the source OBS in `derived_from`.
4. Where a data-field name (or enum literal) must be retained verbatim so the rebuilt app can read existing data (`OR-001.data_strategy` = migrate-in-place / migrate-and-transform), list it in `verbatim_carryover` with a one-line justification.
5. `hw add spec < draft-spec-NNN.md`. Confirm `source: cleanroom`, `zone: spec`, `consumable_by_build: true`.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [OBS-NNN#…]
- **SCAN markers answered:** <count>
- **Zones read / written:** read: observed, spec / written: spec
- **Outputs produced:** data-dictionary SPEC [SPEC-… through SPEC-…]
- **Verbatim carryover (field names/literals retained):** <list with justification>
- **Recommended follow-up:** "Behavior-rules (T-006) consume these SPEC for field semantics."
