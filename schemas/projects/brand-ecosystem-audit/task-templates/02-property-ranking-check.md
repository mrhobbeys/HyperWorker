---
id: T-002
kind: task
schema: brand-ecosystem-audit
phase: B
risk_level: standard
required_tools: [file_read, file_write, browser]
delivery_mode: constrained
depends_on: [T-000]
consumes: ["[OR-001#<short-hash>]", "[PROP-NNN#<short-hash>]"]
acceptance_criteria:
  - "Checks run from a NEUTRAL account (no connection/subscription, incognito-style); method_note records this on every ranking-check."
  - "Each item reviewed individually; branded, title/product, and topical-discovery queries covered."
  - "All results restated on ONE common where_it_lands scale (e.g. 'pos1 branded' / 'page2' / 'Absent')."
---

# Task T-002: Property Ranking Check (neutral account)

## Objective
Establish how the property is actually found by an ordinary stranger — not flattered by
personalization. Weak branded ranks and Absent topical results are significant findings.

## Steps
1. From a neutral, non-personalized account, search: branded terms, title/product terms, and
   topical-discovery terms relevant to the property.
2. Record each as a `ranking-check` with query_kind, where_it_lands (common scale), and a
   method_note naming the neutral setup. Review each item individually.
3. Append to log. Answer @@SCAN markers.

## Completion Report
- Acceptance: <X/Y> · Property: [PROP-NNN#hash] · Outputs: RC-NNN…
- Branded vs topical picture: <…> · Method: <neutral-account note>
