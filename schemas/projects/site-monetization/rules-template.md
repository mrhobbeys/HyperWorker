# 00-REFERENCE-rules.md — <site_domain> Monetization

## Precedence Order
Higher tiers override lower. Tier 1 cannot be overridden.

### Tier 1: OPERATOR-EXECUTES-SENSITIVE (absolute)
- Never enter credentials, payment, bank, or ID numbers.
- Never click activate / accept terms / link or authorize accounts / submit forms — the OPERATOR does these.
- Report-first: propose steps + an operator checklist; no self-execution beyond operator-approved quick wins.
- COMMIT to one recommended path — never refuse to recommend; separate "my recommendation" from "operator executes".
- Operator decisions are FINAL: record verbatim, never re-open or contradict. Raise a concern once, then comply.
- No live ad-code/placement change without operator approval AND a rollback.

@@SCAN_1_1: Confirm this step is a proposal/checklist, not a credentialed action the agent performed.

### Tier 2: SCOPE
- Assigned site, Monetization only. Scope changes need operator approval + a new DEC-XXX.

@@SCAN_2_1: Confirm this is Monetization for the assigned site.

### Tier 3: TECHNICAL
- On Ezoic sites, AdSense runs THROUGH Ezoic mediation — never double-serve.
- ads.txt managed by Ezoic; verify, don't hand-edit conflicting copies.
- Respect the operator's ad-density goal.

### Tier 4: DOCUMENTATION
- Keep STATUS.md current. Clear operator checklists.

## Banned Tokens
| Banned | Safe Replacement | Tier | Why |
|---|---|---|---|
| I activated | operator to activate | 1 | The agent never activates monetization. |
