---
id: T-004
kind: task
schema: cleanroom-rebuild
phase: B
risk_level: standard
required_tools: [file_write, app_driver, io_monitor]
delivery_mode: constrained
depends_on: [T-001]
consumes:
  - "[OR-001#<short-hash>]"
  - "[OBS-NNN#<short-hash>]"  # the peripheral inventory OBS for the device this branch captures
acceptance_criteria:
  - "For each in-scope peripheral (e.g., printer, cash drawer, card reader, sig-pad, or scale for a retail POS — or whatever devices the original drives), the byte sequences and device-protocol calls (e.g., OPOS) for each operation are captured as OBS (observation_type: hardware-io) with capture_method: io-monitor and source_ref = device + operation."
  - "Each hardware-io OBS records the exact byte sequence / call trace as MEASURED on the wire — not inferred from driver source or decompilation."
  - "Every OBS carries source=original, zone=observed, consumable_by_build=false; this task writes only to observed/."
  - "Zero Tier 1 violations from 00-REFERENCE-rules."
---

# Task T-004: Hardware I/O Capture

## Objective

Capture the byte sequences and OPOS/device calls the original issues to each peripheral, as MEASURED on the wire with an I/O monitor. This is the raw material for the hardware spec (T-008). Observation-room task (`hardware-io-capture` kind): faces the original via `app_driver` / `io_monitor`; reads and writes only `observed/`.

## Branching Note

Branch one subagent per device via `hw branch T-004 device-NNN`. Subagents need `file_write`, `io_monitor`.

## Step-by-Step Instructions

1. Recite OR-001 and the assigned peripheral OBS. SCAN (not a build-room task).
2. Attach `io_monitor` to the device port / OPOS channel.
3. Drive the original to perform each device operation (e.g., print receipt, open cash drawer, read a card swipe, capture a signature, read a scale weight — or whatever operations the original's peripherals perform).
4. Record the byte sequence / call trace for each operation. Write OBS: `observation_type: hardware-io`, `capture_method: io-monitor`, `source_ref` = device + operation. Store raw captures under `observed/hardware/` and reference in `artifact_path`.
5. `hw add observation < draft-obs-NNN.md`. Confirm `source: original`, `zone: observed`, `consumable_by_build: false`.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [OBS-NNN#…]
- **SCAN markers answered:** <count>
- **Zones read / written:** read: observed / written: observed
- **Outputs produced:** hardware-io OBS [OBS-… through OBS-…]; raw captures under observed/hardware/
- **Devices captured / unreachable:** <list>
- **Recommended follow-up:** "Spec room: hardware-spec (T-008) consumes these OBS."
