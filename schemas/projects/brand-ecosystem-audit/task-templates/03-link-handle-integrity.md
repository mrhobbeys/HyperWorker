---
id: T-003
kind: task
schema: brand-ecosystem-audit
phase: C
risk_level: standard
required_tools: [file_read, file_write, browser]
delivery_mode: constrained
depends_on: [T-000]
consumes: ["[OR-001#<short-hash>]", "[PROP-NNN#<short-hash>]"]
acceptance_criteria:
  - "Every owned link/handle the brand publishes is resolved in a browser; dead (NXDOMAIN), wrong-handle, and duplicate accounts are identified."
  - "Findings written with provenance; the one live/correct handle per channel is named."
---

# Task T-003: Link & Handle Integrity (cross-brand)

## Objective
Catch the guaranteed dead-ends: typo domains in video descriptions, dead footer links, wrong
or duplicate handles that scatter the audience.

## Steps
1. Collect every brand link/handle published across properties. Resolve each live.
2. Flag NXDOMAIN/dead, wrong-handle (links to the wrong place), and duplicate accounts. Name the
   single correct/live handle per channel. Write findings (audit_role: identity/leak).
3. Append to log. Answer @@SCAN markers.

## Completion Report
- Acceptance: <X/Y> · Dead/typo/wrong/duplicate found: <list> · Correct handles: <list>
