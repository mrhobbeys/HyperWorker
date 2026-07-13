# 00-REFERENCE-rules.md — <site_domain> Review & Repair

## Precedence Order
Higher tiers override lower. Tier 1 cannot be overridden.

### Tier 1: LIVE-SITE-SAFETY (absolute)
- No destructive/bulk change without operator approval AND a recorded rollback.
- Never change DNS, hosting, permissions, or user access.
- Never permanently delete content or pages.
- Do NOT remediate hack/malware — hand to the Recovery program.
- Never enter credentials, payment, or ID numbers — the operator does that.

@@SCAN_1_1: State the rollback for any change this task makes.
@@SCAN_1_2: Confirm this change is non-destructive or operator-approved.

### Tier 2: SCOPE (overrides technical/docs)
- Assigned site only; Review & Repair only (not Monetization/SEO/DMCA).
- Scope changes need operator approval + a new DEC-XXX.

@@SCAN_2_1: Confirm this work is Review & Repair for the assigned site.

### Tier 3: TECHNICAL (overrides docs)
- Preserve URLs/redirects; moved URLs 301 to replacements.
- Verify each fix on production before marking done.
- Back up a file before editing.

### Tier 4: DOCUMENTATION
- Keep STATUS.md current. Consistent file naming.

## Banned Tokens
| Banned | Safe Replacement | Tier | Why |
|---|---|---|---|
| approximately | <exact value> | 1 | Repairs need precise targets. |
| should be fixed | is fixed (verified at <url>) | 1 | A fix isn't done until verified. |
