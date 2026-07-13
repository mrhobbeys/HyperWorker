---
id: T-004
kind: task
schema: brand-ecosystem-audit
phase: C
risk_level: standard
required_tools: [file_read, file_write, browser]
delivery_mode: constrained
depends_on: [T-000]
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "Benchmarked against TRUE peers (same category/stage), not aspirational giants."
  - "Gaps framed as concrete best-practice targets, with provenance; >=1 disconfirming finding surfaced if the brand is stronger/weaker than the operator assumes."
---

# Task T-004: Competitor Benchmark (cross-brand)

## Objective
Place the brand against real peers so the synthesis paths are calibrated (where it already
leads vs. where best-practice gaps are).

## Steps
1. Identify true peers. Compare on the levers that matter (owned hub authority, email capture,
   handle consistency, discovery, conversion).
2. Write findings; mark at least one disconfirming if the data complicates the operator's
   assumption (e.g. "most established peer, but worst at email capture").
3. Append to log. Answer @@SCAN markers.

## Completion Report
- Acceptance: <X/Y> · Where brand leads / lags: <…> · Disconfirming: <…>
