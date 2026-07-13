---
id: T-007
kind: task
schema: site-seo
phase: 5
risk_level: elevated
task_kind: dmca-investigation
delivery_mode: constrained
depends_on: [T-006]
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "Each duplicate/scraper lead from T-006 confirmed (verbatim copy + the copying URL + host)."
  - "DMCA target list assembled with evidence; takedown route noted (Google legal removal + host). Operator decides filing."
---

# Task T-007: DMCA / Stolen-Content Investigation (late phase)

Confirm the scraped copies from T-006, assemble evidence + takedown routes. Report-first: the operator decides which DMCAs to file.
