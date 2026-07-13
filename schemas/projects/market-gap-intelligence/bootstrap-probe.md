# Bootstrap Probe — market-gap-intelligence

> Read by the executor at `hw bootstrap`. Unlike report-synthesis (which inventories a static file corpus), this probe inventories the CLIENT'S live footprint and any prior work already in the project, so §Scope reflects ground truth before discovery begins.

## Default probe — client + prior-work sweep

Two passes:

**1. Live client footprint.** From `client_url`, record (no deep crawl yet):
```
fetch(client_url) → site title, declared services, NAP, domain/TLD
list internal nav + footer links (candidate money/service/location pages)
```
The probe records `declared_services`, `observed_nap`, and `tld_risk` (e.g., a
ccTLD like `.it` read as a foreign geo). These seed T-000.

**2. Prior work in the project folder.** Walk the project root for existing
reports, spreadsheets, and exports the operator dropped in:
```
walk(project_root, recursive=true)
filter(extension in [".md", ".xlsx", ".csv", ".docx", ".pdf"])
classify(prior-report | competitor-map | keyword-export | other)
```
Prior competitor maps and keyword exports are MEASURED/OBSERVED evidence already
collected — register them so T-001/T-002 build on them instead of re-running
searches from scratch. Earlier strategy reports feed T-005 (anti-pattern capture).

The probe records:
- `declared`: money_terms / competitors the operator named at bootstrap (often empty).
- `found`: client pages + prior-work files on disk.
- `prior_evidence`: classified prior reports/exports with a one-line note each.
- `missing_from_declared`: pages/files the operator did not name (operator confirms include/exclude).

## Operator reconciliation
For "just look at everything," one keystroke confirms the found list. The operator
flags any prior report as superseded (feeds anti-pattern capture, not live claims).

After reconciliation the agent emits `bootstrap.scope_locked` with the money-term
list + the prior-evidence inventory. PROJECT.md §Scope is written from that event;
T-000 consumes it.

## When to skip
If `client_url` is unreachable or the engagement is pre-launch (no live site), the
probe emits `bootstrap.probe_skipped` with the reason; T-000 builds the dossier
from operator-supplied facts and marks the missing live signals as TBD-verify.

## Cross-reference to T-000 / T-005
T-000 (dossier) inherits the verified footprint instead of rebuilding it. T-005
(anti-pattern capture) consumes the `prior_evidence` reports flagged as superseded.
