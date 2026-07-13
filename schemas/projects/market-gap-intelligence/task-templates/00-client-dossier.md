---
id: T-000
kind: task
schema: market-gap-intelligence
phase: A
risk_level: standard
required_tools: [file_read, file_write, browser]
delivery_mode: constrained
depends_on: []
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "OR-001 is complete: decision_statement, client_identity (with NAP), geography, buyer, services, scope_mode, available_tools, brand_constraints (populated or explicit none), deliverable_path."
  - "money_terms exist — either operator-supplied or derived from the service pages and listed for operator confirmation."
  - "Any NAP inconsistency, name collision, or domain/TLD risk observed on the live site/listings is registered as a finding (provenance: OBSERVED)."
  - "Tier 4 STYLE + brand_constraints recorded in 00-REFERENCE-rules.md (or explicit 'no override beyond schema defaults')."
  - "evidence/EVIDENCE-LOG.md initialized for downstream tasks to append to."
---

# Task T-000: Client Dossier + Operating Reality

## Objective
Make the project a laser: any agent handed it operates as a focused specialist on
exactly this client, in this geography, for this buyer, with no bleed from other
clients. Populate OR-001 from observable reality first; ask the operator only for
what can't be observed.

## Step-by-Step
1. Read OR-001 bootstrap answers.
2. Load the client site (browser; web_fetch acceptable for static pages). Extract:
   real services and priority, money pages, positioning/voice, NAP, domain/TLD.
3. Check listings for NAP consistency and brand/name collisions. Register any
   inconsistency or collision as a `finding` (provenance: OBSERVED) — these are
   ranking blockers, not cosmetic. Map NAP/entity fixes to the
   local-search-ranking-planner skill if local.
4. Derive money_terms if not supplied: from the service list + buyer intent. List
   them for operator confirmation; do not silently lock guesses.
5. Record brand_constraints. For health/legal/finance, default to listing the
   real claim limits rather than `none`.
6. Populate Tier 4 STYLE and any banned tokens / canonical facts in
   00-REFERENCE-rules.md, or write the explicit no-override line.
7. Initialize `evidence/EVIDENCE-LOG.md` (columns: artifact, source, date, provenance).
8. Answer @@SCAN markers.

## Completion Report
- Acceptance criteria: <X/Y>
- Citations consumed: [OR-001#…]
- Outputs: updated OR-001; F-NNN (NAP/entity/TLD findings); initialized evidence log
- money_terms (for confirmation): <list>
- Observed blockers: <NAP errors, name collisions, TLD geo-risk, etc.>
- Recommended follow-up: "Operator confirm money_terms + geography before discovery."
