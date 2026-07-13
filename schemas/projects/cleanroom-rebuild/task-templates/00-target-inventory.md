---
id: T-000
kind: task
schema: cleanroom-rebuild
phase: A
risk_level: standard
required_tools: [file_read, file_write, app_driver, sql_query]
delivery_mode: constrained
depends_on: []
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "The original's surface is enumerated: screen list, DB catalog (tables/views), and peripheral list, each captured as an OBS artifact (observation_type: screen | sql-trace | hardware-io | other) with capture_method and source_ref populated."
  - "Every OBS written carries source=original, zone=observed, consumable_by_build=false (Layer 1 zone-write-discipline holds: this task writes only to observed/)."
  - "PROJECT.md §Scope Included/Excluded reflects the enumerated surface; out-of-scope screens/tables are listed in §Explicitly Excluded."
  - "Inventory projection regenerates byte-identical from events."
  - "Zero Tier 1 violations from 00-REFERENCE-rules."
---

# Task T-000: Target Inventory

## Objective

Enumerate the original system's surface so the observation and spec phases have a known scope. Catalog every screen, every database object, and every peripheral as an `observation` (OBS) artifact in the `observed/` zone. This is an observation-room task (`target-inventory` kind): it MAY face the original via `app_driver` and `sql_query`, and it writes only to `observed/`.

## Step-by-Step Instructions

1. Recite OR-001. Note `legacy_system`, `observation_oracle`, `data_strategy`, and `excluded_scope`.
2. SCAN: answer the @@SCAN markers. (This is NOT a build-room task; @@SCAN_1_1/1_2 answer "not a build-room task"; @@SCAN_1_3 answers "no — inventory only enumerates the surface, it does not read binaries/decompilation.")
3. Drive the original via the declared observation oracle. Enumerate screens/forms; for each, write an OBS with `observation_type: screen`, `capture_method: gui-driver` (or manual), and `source_ref` = the screen id/name.
4. Query the original's database catalog (`sql_query`). For each table/view, write an OBS with `observation_type: sql-trace` or `other`, `capture_method: sql-query`, `source_ref` = the object name.
5. List peripherals (printer, cash drawer, MSR, sig-pad, scale). For each, write an OBS with `observation_type: hardware-io`, `capture_method: manual`, `source_ref` = device name.
6. Write each via `hw add observation < draft-obs-NNN.md` per substrate protocol. Confirm every OBS has `source: original`, `zone: observed`, `consumable_by_build: false`.
7. Populate PROJECT.md §Scope: Included = the surface to rebuild; Excluded = screens/tables/devices out of scope (cite OR-001.excluded_scope).

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…]
- **SCAN markers answered:** <count>
- **Zones read / written:** read: observed, spec, src (catalog only) / written: observed
- **Outputs produced:** OBS-001 through OBS-NNN; updated PROJECT.md §Scope
- **Surface counts:** <N screens, M tables, K peripherals>
- **Out-of-scope items noted:** <list with reason>
- **Recommended follow-up:** "Operator confirm scope boundary before Phase B observation begins."
