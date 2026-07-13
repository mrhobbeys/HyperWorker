---
id: T-005
kind: task
schema: brand-ecosystem-audit
phase: D
risk_level: standard
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-001, T-002, T-003, T-004]
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "A `manifest` artifact indexes every produced report: file -> unit(property) -> type -> treatment."
  - "Generic filenames are disambiguated; do-not-double-count pairs flagged; non-source files listed under skip."
  - "open_items lists every login-required/not-run report with what it would have told us."
---

# Task T-005: Build the Manifest

## Objective
Create the fan-in index so the synthesis never mis-attributes, double-counts, or treats a
process doc as evidence. (Mirrors the pilot engagement's `_SYNTH-MANIFEST.md`.)

## Steps
1. List every produced report. For each: file, unit (property), type, treatment (authoritative /
   raw-source / do-not-double-count / generic-filename->X / weight-heavily).
2. Fill open_items (missing/login-gated reports + what each would tell). Fill skip (templates,
   prompts, process docs).
3. Write the `manifest` artifact. Answer @@SCAN markers.

## Completion Report
- Acceptance: <X/Y> · Output: MAN-NNN · Entries: <n> · Open items: <n> · Skipped: <n>
