---
id: T-001
kind: task
schema: site-seo
phase: 2
risk_level: elevated
task_kind: diagnosis
delivery_mode: constrained
depends_on: [T-000]
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "The correct /sitemap_index.xml resubmission + reindex requests are SPECIFIED (depends on Recovery having fixed the docroot sitemap/robots)."
  - "The 130 not-found 404s are each classified restore-vs-301-vs-leave."
  - "SERVER-HANDOFF produced for any server-side work (sitemap/robots/redirects)."
---

# Task T-001: Technical Indexing Foundation

Specify the indexing fix: resubmit the correct sitemap (after Recovery), resolve the 404s (restore/301), request reindexing. End with a SERVER-HANDOFF for anything server-side.
