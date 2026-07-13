---
id: T-001
kind: task
schema: lead-mining
phase: B
risk_level: elevated
required_tools: [file_read, file_write, email_search]
depends_on: [T-000]
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "Each mailbox searched across the full date range for INBOUND messages."
  - "Each distinct external sender captured as a raw Finding: name, email, domain, first/last contact date, subject snippets."
  - "No fabricated contacts; large mailboxes handled via fan-out (per account / per quarter) subagents."
---
# T-001 Harvest inbound contacts
Pull inbound senders per account across the date range. For big mailboxes, fan out subagents (one per account or per quarter) each with email_search. Capture raw contacts as Findings (mark exclude-candidates for T-002, don't drop yet). Record source mailbox + dates.
