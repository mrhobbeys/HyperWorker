---
id: T-002
kind: task
schema: site-seo
phase: 2
risk_level: elevated
task_kind: diagnosis
delivery_mode: constrained
depends_on: [T-001]
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "Every crawled-not-indexed page (+ other exclusions) categorized by likely cause (thin/duplicate/orphan/quality)."
  - "Each category linked to the phase that addresses it (content / structure / on-page)."
---

# Task T-002: Index-Exclusion Diagnosis

Find WHY Google declines pages: categorize the crawled-not-indexed and other exclusions, and route each cause to the right later phase.
