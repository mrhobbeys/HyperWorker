---
id: T-007
kind: task
schema: site-monetization
phase: 4
risk_level: standard
task_kind: verify
delivery_mode: constrained
depends_on: [T-006]
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "STATUS.md updated for orchestrator; open items handed to SEO."
  - "scope.complete emitted for every PROJECT.md Scope item; then session.handoff."
---

# Task T-007: Handoff

Write final STATUS.md, hand open items to SEO, close scope cleanly.
