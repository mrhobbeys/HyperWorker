# 00-REFERENCE-rules — {{ project_name }} (lead-mining)

## Tier 1 — ABSOLUTE
- Inbound only: include a contact ONLY if they emailed the operator. Never fabricate contacts, emails, or details; unverifiable = "unconfirmed".
- Exclude vendors/suppliers, newsletters/automated/no-reply, and internal staff + personal/family.
- This project builds a LIST. Do NOT send outreach; operator approves any future sends separately.
- Privacy: operator's own mailbox data; do not share/export contacts to third parties or external tools beyond what's needed to enrich a company name.

## Tier 2 — SCOPE
- Mine only the operator-listed mailboxes and date range. Current customers included only if OR-001 says so (flag as upsell).

## Tier 3 — QUALITY
- Dedupe by person and by company/domain; one row per real lead.
- Each lead cites its source (mailbox + message/thread reference) where possible.
- Prioritize by: clarity of need > recency > deal size potential > fit with our services.

## Tier 4 — STYLE
No operator override beyond schema defaults.

## @@SCAN markers
- @@SCAN-accounts: exact mailboxes + connector status (from OR-001).
- @@SCAN-range: date range (from OR-001).
