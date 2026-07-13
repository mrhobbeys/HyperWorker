---
id: T-005
kind: task
schema: lead-mining
phase: C
risk_level: standard
required_tools: [file_read, file_write]
depends_on: [T-004]
acceptance_criteria:
  - "Master lead list compiled (spreadsheet): name, email, company, role, need, status, source mailbox, last contact, priority."
  - "List prioritized; scope.complete + session.handoff written."
---
# T-005 Compile master list + handoff
Compile the deduped/verified leads into the master spreadsheet with priority ranking. Summarize counts (by status, by need). Emit scope.complete + session.handoff. Report to orchestrator.
