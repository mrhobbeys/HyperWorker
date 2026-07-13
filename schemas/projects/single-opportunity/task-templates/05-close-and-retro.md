---
id: T-005
kind: task
schema: single-opportunity
phase: C
risk_level: standard
required_tools: [file_read, file_write]
depends_on: [T-004]
acceptance_criteria:
  - "Outcome (win/loss/no-decision) recorded; short retro -> reusable anti-patterns/decisions; orchestrator notified."
---
# T-005 Close & retro
Record outcome; capture what worked/what to change as anti-patterns/decisions; update the source channel/orchestrator.
