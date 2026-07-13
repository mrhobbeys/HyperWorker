---
id: T-000
kind: task
schema: brand-ecosystem-audit
phase: A
risk_level: standard
required_tools: [file_read, file_write, browser]
delivery_mode: constrained
depends_on: []
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "OR-001 complete: brand_identity, owned_hub_url, surfaces, primary_goal, dispatch_mode, deliverable_path."
  - "Every declared surface is registered as a `property` artifact with role + status (live/dead/wrong-handle/duplicate/missing)."
  - "Surfaces discovered on the owned hub but not declared (e.g. a second handle) are registered and flagged."
  - "dispatch_mode is set (separate-chats if any social/login surface present) and recorded."
---

# Task T-000: Brand Dossier + Surface Inventory

## Objective
Decompose the brand into its atomic UNITS (properties) and lock the operating reality, so
each surface can be audited cleanly and nothing is missed.

## Steps
1. Read OR bootstrap answers. Resolve each declared surface in a browser; register a `property`
   (platform, url_or_handle, role, status, provenance, date).
2. Scan the owned hub's outbound brand links/footer/social icons for surfaces not declared and
   for dead/typo/wrong-handle links; register those too (status accordingly).
3. Confirm dispatch_mode; if any social/login surface exists, default separate-chats.
4. Initialize `evidence/EVIDENCE-LOG.md`. Answer @@SCAN markers.

## Completion Report
- Acceptance: <X/Y> · Outputs: PROP-001…NNN · Surfaces flagged dead/wrong/duplicate: <list>
- Dispatch mode: <mode + why> · Recommended follow-up: "Operator confirm surface list + mode."
