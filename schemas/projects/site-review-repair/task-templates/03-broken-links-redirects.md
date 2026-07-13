---
id: T-003
kind: task
schema: site-review-repair
phase: 1
risk_level: standard
task_kind: audit
delivery_mode: constrained
depends_on: [T-001]
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "Internal 404s and broken internal links listed with source pages."
  - "Redirect map proposed for any moved/renamed URLs (301 targets)."
---

# Task T-003: Broken Links & Redirects

Find broken internal links and 404s from the move. Propose 301s so no indexed URL is lost (Tier 1/3 SEO preservation).
