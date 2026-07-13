# Bootstrap Probe — single-opportunity

> Read by the executor at `hw bootstrap` time. The probe inventories the actual deal documents and stakeholders behind the operator's answers, so §Scope reflects ground truth rather than the operator's recollection. See `core/SUBSTRATE.md` §Bootstrap Inventory Sweep.

## Default probe — deal-document & stakeholder inventory

Single-opportunity projects declare a `source` (channel/portal + link), a `buyer` (+ key contact), `key_dates`, and `eligibility_gates` at bootstrap. The probe:

1. Collects the deal documents the operator named or linked (base solicitation/RFP, amendments, Q&A logs, required forms/attachments) plus any operator-provided files already on disk.
2. Fetches the `source` link and each document URL (`web_fetch`, falling back to a human-driven browser session for login-gated portals) and records reachability and access level (`open | registration-required | login-gated | operator-provided`).
3. Cross-checks the declared `key_dates` against dates visible in the fetched documents; any discrepancy (deadline mismatch, missed questions-due date, an amendment that moved the deadline) is surfaced for correction.
4. Enumerates stakeholders: the declared `buyer` contact vs contacts actually named in the documents (contracting officer, technical POC, portal support). Contacts in the documents the operator did not name are added to the diff.

The probe records:

- `probe_method: "deal-document-inventory"`
- `declared`: the documents, dates, and stakeholders the operator named at bootstrap.
- `found`: documents confirmed reachable (with access level), dates as they appear in the documents, and stakeholders named in them.
- `missing_from_declared`: documents, amendments, dates, or contacts found in the source material that the operator did not mention.
- `missing_from_found`: declared documents that were unreachable or ambiguous (wrong link, removed listing, login wall), and declared dates or contacts no fetched document supports.

## Operator reconciliation

The operator confirms the document list per item (in scope / not this deal), supplies missing documents or corrected links, and resolves date discrepancies — each key date ends up either verified against a document or explicitly `unconfirmed`. Eligibility gates are recorded as they ARE, not as they are planned to be — the honest go/no-go at qualification (Tier 1) depends on this being true.

After reconciliation, the agent emits `bootstrap.scope_locked` with the confirmed document list, reconciled key dates, and stakeholder roster. PROJECT.md §Scope is written from that event; T-000 (qualify the deal) consumes the locked list.

## When to skip

If the operator cannot grant network access at bootstrap time, or the deal documents are operator-provided files already on disk and previously verified (e.g., re-bootstrap of a pursuit already in flight), the probe emits `bootstrap.probe_skipped` with `reason: "<reason>"`. T-000 assumes responsibility for document inventory and live verification in the skip case.

## Cross-reference to T-000

T-000 (qualify the deal) inherits the probe's verified document list, reconciled dates, and stakeholder roster rather than rebuilding them. T-000 still re-verifies the deadline and requirements live, registers each confirmed document as a SRC artifact with full access metadata, records the deal facts in OR-001, and produces the go/no-go recommendation.
