---
id: T-001
kind: task
schema: brand-ecosystem-audit
phase: B
risk_level: elevated
required_tools: [file_read, file_write, browser]
delivery_mode: constrained
depends_on: [T-000]
consumes: ["[OR-001#<short-hash>]", "[PROP-NNN#<short-hash>]"]   # ONE property per branch/chat
acceptance_criteria:
  - "Exactly ONE property audited; no comparison to other properties (stay focused)."
  - "Reviewed LIVE in a rendered browser, page-by-page — popups, forms, hero, checkout/mobile. verified_live: true for any broken/works claim."
  - "property-audit written: score (1-5 common scale), strengths, issues (impact-first), goal_mechanics, top_fixes (week/next/bigger-bet)."
  - "Weighted toward highest revenue/goal impact per unit of effort, not an even spread."
---

# Task T-001: Property Deep-Dive (one property)

## Objective
Produce a self-contained read of ONE surface: what a real visitor/searcher sees, and the
highest-impact changes toward OR.primary_goal.

## Dispatch note
Per OR.dispatch_mode. Social/login surfaces (e.g. FB, LinkedIn, IG, X, YouTube, TikTok, or
any other platform needing a logged-in session) run as a SEPARATE
agent-driven chat — the agent drives the browser; the human assists only at login / an
irreducible click. A subagent without a sustained interactive browser must refuse + emit
capability_gap.md.

## Steps
1. Open the property live; render it (don't trust static HTML). Note anything that only
   appears/breaks with JS (popups, preloaders, reCAPTCHA, payment).
2. Cover: first-impression/UX, trust signals, brand clarity, conversion/goal mechanics + leaks,
   content, discoverability. Verify before asserting.
3. Write the `property-audit` (verified_live true where you claim broken/works). Append to log.
4. Answer @@SCAN markers.

## Completion Report
- Acceptance: <X/Y> · Property: [PROP-NNN#hash] · Output: PA-NNN · Score: <n/5>
- Top fixes (week/next/bigger): <…> · Anything needing login you couldn't see: <open items>
