---
id: T-002
kind: task
schema: site-monetization
phase: 2
risk_level: elevated
task_kind: plan
delivery_mode: constrained
depends_on: [T-001]
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "Step-by-step AdSense connection/activation plan (mediated via Ezoic) with each step marked operator vs worker."
  - "No credentialed step performed by the worker."
---

# Task T-002: AdSense Plan

Draft the AdSense connection/activation steps (via Ezoic mediation). Mark every login/activate/link step as OPERATOR-executed.
