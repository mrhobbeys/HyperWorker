# Schema: brand-ecosystem-audit

## What this is for
Evaluate a brand across ALL its surfaces — owned hub (website), social properties,
marketplaces/retailers, review sites — to see how it is currently **seen and found**,
then hand the operator a **menu of strategic paths** (not one fixed plan). Proven on an
Acme Corp-style brand engagement (e.g. an author/creator brand — the same spine applies
to a company or product brand).

## The spine (shared with market-gap-intelligence)
**Fan-out -> manifest -> synthesize to a paths menu.** Here the *unit* is a brand
**property/surface** (LinkedIn, Instagram, Amazon, the website...). Each is audited
atomically in its own focused chat; a manifest indexes everything; one synthesis turns it
into the master report. The discipline that makes it trustworthy: separate **"where things
are"** (per-property ground truth) from **"where things should be"** (the synthesis).

## When to use it
- A person/company has presence scattered across many surfaces and you need the big picture.
- You want to know where authority/intent leaks between properties and how the brand is found.
- The operator wants options to choose from, not a single prescription.

## When NOT to use it
- A single-page question (use a one-off audit). A market-gap/positioning question (use
  `market-gap-intelligence`). No owned hub or goal to align against.

## What the schema enforces
- **Verify-before-assert** — broken/works claims confirmed in a rendered browser (`verified_live`).
- **Neutral-account rankings** — every ranking-check records a non-personalized method, so weak
  ranks count. `neutral_account_ranking_check` fails any check without it.
- **Coverage** — every declared surface is audited or marked dead/missing/duplicate with reason.
- **Paths menu, not a plan** — `paths_menu_present` requires >=3 strategic-path artifacts +
  >=1 foundational; a single forced plan fails.
- **>=1 disconfirming finding** or the audit under-looked.

## Dispatch mode (operator chooses; director recommends)
`single-agent` for <=4 surfaces with low divergence risk; `separate-chats` otherwise — and
**always for social/login surfaces** (e.g. FB, LinkedIn, IG, X, YouTube, TikTok, or any
other platform that needs a logged-in session), which need a sustained **agent-driven**
browser where the human assists only at login / an irreducible click.
This protects the operator's attention (HyperWorker is an executive-function prosthesis):
agents do the work; humans are pulled in only for the irreducible.

## New artifact kinds
`property` (PROP), `property-audit` (PA), `ranking-check` (RC). Plus the SHARED default kinds
`manifest` (MAN) and `strategic-path` (PATH).

## Bootstrap
```
hw bootstrap --schema brand-ecosystem-audit --name <brand-id>
```
Reuses the `property-audit-prompt-template` style for per-surface deep-dives. After bootstrap,
audit each surface (one chat each per dispatch_mode), then build the manifest and synthesize.
