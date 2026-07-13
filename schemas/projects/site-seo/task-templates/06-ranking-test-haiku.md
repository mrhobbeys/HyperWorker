---
id: T-006
kind: task
schema: site-seo
phase: 4
risk_level: elevated
task_kind: ranking-test
delivery_mode: constrained
depends_on: [T-002]
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "HAIKU subagents run per ranking-test-haiku.md (one query/snippet each), results aggregated to outputs/ranking-test-results.md."
  - "A Duplicate/Scraper list (copying URL + verbatim evidence snippet) is produced for the DMCA phase."
---

# Task T-006: Ranking Test (Haiku subagents) + Duplicate Detection

Dispatch HAIKU subagents per ranking-test-haiku.md to test target-query rankings AND detect duplicate/scraped copies. Aggregate results; hand the duplicate list to T-007.
