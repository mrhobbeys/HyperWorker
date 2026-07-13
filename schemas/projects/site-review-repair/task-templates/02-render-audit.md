---
id: T-002
kind: task
schema: site-review-repair
phase: 1
risk_level: standard
task_kind: audit
delivery_mode: constrained
depends_on: [T-001]
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "Broken images, CSS, and JS enumerated with the exact failing URLs."
  - "Mobile/responsive and console-error issues noted."
---

# Task T-002: Render Audit

Find what the migration broke visually: 404 assets, wrong paths, missing CSS/JS, console errors. List exact failing resource URLs.
