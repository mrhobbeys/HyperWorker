# Bootstrap Probe — lead-mining

> Read by the executor at `hw bootstrap` time. The probe verifies the declared mailbox list against connector ground truth, so §Scope reflects mailboxes the harness can actually harvest and connector gaps that are honestly stated. See `core/SUBSTRATE.md` §Bootstrap Inventory Sweep.

## Default probe — mailbox connector sweep

Lead-mining projects declare a set of mailboxes to mine (`accounts`) with their providers and assumed connector status. The probe:

1. Collects the mailboxes the operator named at bootstrap (address + provider), including any older/former addresses mentioned.
2. Verifies connector access to each (`email_search` for that mailbox: fetch a single recent message's metadata — sender, date, subject — nothing more) and records connector status (`connected | missing | pending`). The probe reads the minimum needed to prove access; no message bodies are stored and nothing leaves the project workspace.
3. Diffs declared vs accessible: any declared mailbox the operator marked "connected" that the connector cannot reach is surfaced for correction; any additional mailbox/alias the connectors expose that the operator did not name (e.g., a second business or brand mailbox, a shared inbox) is added to the diff for an explicit include/skip call.

The probe records:

- `probe_method: "mailbox-connector-sweep"`
- `declared`: mailboxes the operator named at bootstrap, with provider and claimed connector status.
- `found`: mailboxes confirmed accessible, with provider and connector status.
- `missing_from_declared`: accessible mailboxes/aliases the connectors expose that the operator did not name.
- `missing_from_found`: declared mailboxes that were unreachable (missing connector, wrong address, retired account).

## Operator reconciliation

The operator confirms the mailbox list per item (mine / skip with reason) and corrects any optimistic connector status. Connector status is recorded as it IS, not as it is planned to be — the inbound-integrity tier (Tier 1) and the harvest fan-out both depend on this being true. Mailboxes surfaced by the probe but not declared are never mined without an explicit operator include (Tier 2: mailbox scope).

After reconciliation, the agent emits `bootstrap.scope_locked` with the confirmed mailbox list and connector status. PROJECT.md §Scope is written from that event; T-000 (account inventory + filters) consumes the locked list and registers each confirmed mailbox as a SRC artifact.

## When to skip

If the operator cannot grant connector access at bootstrap time, or the account set is operator-curated and already verified (e.g., re-bootstrap of a running mining project), the probe emits `bootstrap.probe_skipped` with `reason: "<reason>"`. T-000 assumes responsibility for connector verification in the skip case.

## Cross-reference to T-000

T-000 (account inventory + filters) inherits the probe's verified mailbox list rather than building one from scratch. T-000 still registers each mailbox as a SRC artifact with full metadata (address, provider, account role, connector status, date range) and locks the date range, exclude rules, and verification scope in OR-001.
