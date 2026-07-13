---
id: T-004
kind: task
schema: lead-mining
phase: C
risk_level: elevated
required_tools: [file_read, file_write, email_search]
depends_on: [T-003]
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "Each lead confirmed a valid external contact with a usable email."
  - "Status set: active / cold / current-customer; last-contact date recorded."
---
# T-004 Verify & status
Confirm each is a real, reachable external contact. Set status (active / cold / current customer) and last-contact date from the mailbox. Flag bounced/invalid.
