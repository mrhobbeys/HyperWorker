---
id: T-000
kind: task
schema: lead-mining
phase: A
risk_level: standard
required_tools: [file_read, file_write, email_search]
depends_on: []
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "Exact mailboxes confirmed with connector access verified (Outlook for business mailboxes; Gmail for personal)."
  - "Date range + exclude rules + verification scope locked in OR-001."
  - "Each mailbox registered as a SRC artifact."
---
# T-000 Account inventory + filters
1. Confirm with operator the EXACT addresses for: the primary business mailbox (<business mailbox>), personal mailbox (<personal mailbox>), any OTHER business/brand mailboxes, and any OLDER/former addresses.
2. Verify connector access for each (M365/Outlook connector; Google/Gmail connector). If a connector is missing, request it before harvesting that account.
3. Lock date range (default last 4 years), exclude rules (vendors; newsletters/automated; internal/personal), include-current-customers = yes (flag upsell), and verification scope.
4. Register each mailbox as a SRC. Answer @@SCAN-accounts, @@SCAN-range.
