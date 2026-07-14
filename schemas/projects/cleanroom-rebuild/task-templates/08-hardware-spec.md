---
id: T-008
kind: task
schema: cleanroom-rebuild
phase: C
risk_level: elevated
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-004, T-005]
consumes:
  - "[OR-001#<short-hash>]"
  - "[OBS-NNN#<short-hash>]"  # hardware-io OBS
acceptance_criteria:
  - "Each in-scope peripheral operation is specified as a SPEC (spec_type: hardware-spec): the byte sequence / device-protocol call contract (e.g., OPOS) the rebuilt app must emit, in our own words, with worked example payloads."
  - "Each hardware-spec cites the hardware-io OBS it derives from in derived_from."
  - "Protocol byte values / device literals retained verbatim (required for the device to function) are listed in verbatim_carryover with justification — these are canonical facts, not over-quoting."
  - "Where a behavior-rule governs device output (e.g., receipt formatting depends on a pricing rule), the hardware-spec cross-references the BR."
  - "All SPEC carry source=cleanroom, zone=spec, consumable_by_build=true; reads observed+spec, writes only spec/."
  - "Zero Tier 1 violations from 00-REFERENCE-rules."
---

# Task T-008: Hardware Spec  *(elevated)*

## Objective

Re-express the original's peripheral protocols as a cleanroom hardware spec the build room can implement. Spec-room task (`spec-author` kind): reads `observed/` + `spec/`, writes only `spec/`. Protocol byte values are functional necessity — they belong in `verbatim_carryover` (and the rules file canonical-facts table), not paraphrased away.

## Step-by-Step Instructions

1. Recite OR-001 and the hardware-io OBS. SCAN: confirm @@SCAN_2_1 / @@SCAN_2_2. Not a build-room task.
2. For each device operation, author a SPEC (`spec_type: hardware-spec`): the call contract / byte sequence the rebuilt app must emit, with a worked example payload from the captured OBS.
3. List required protocol literals (control bytes, OPOS method names, or other device-protocol identifiers) in `verbatim_carryover` with justification. Confirm they also appear in the 00-REFERENCE-rules canonical-facts table so they are not normalized.
4. Cross-reference any BR that governs device output (e.g., receipt line formatting tied to a pricing rule).
5. Cite source OBS in `derived_from`.
6. `hw add spec < draft-spec-NNN.md`. Confirm `source: cleanroom`, `zone: spec`, `consumable_by_build: true`.

## Failure Scenarios (elevated — two required)

1. **Scenario:** A device control byte was normalized/"cleaned up" and the rebuilt app's output is rejected by the device.  
   **Outcome:** <fill in>  
   **Safe?** <yes/no>
2. **Scenario:** A timing-dependent device handshake was captured but not specified, so the build implements it as a plain sequence.  
   **Outcome:** <fill in>  
   **Safe?** <yes/no>

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [OBS-NNN#…]
- **SCAN markers answered:** <count>
- **Zones read / written:** read: observed, spec / written: spec
- **Outputs produced:** hardware-spec SPEC [SPEC-… through SPEC-…]
- **Protocol literals carried verbatim:** <list; confirm in canonical-facts table>
- **Recommended follow-up:** "Build-from-spec (T-010) implements these hardware-specs."
