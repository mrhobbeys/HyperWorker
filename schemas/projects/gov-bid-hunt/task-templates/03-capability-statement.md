---
id: T-003
kind: task
schema: gov-bid-hunt
phase: C
risk_level: standard
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-002]
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "A reusable 1-2 page capability statement exists for this segment (company, NAICS/codes, differentiators, past performance, contact, UEI/registration once available)."
  - "It is honest about current registration status and names the subcontracting partner where relevant."
---

# Task T-003: Capability Statement
Draft the reusable capability statement used to respond to Sources Sought / RFIs and attach to bids. Keep a version that works even before SAM.gov is active (for Sources Sought / RFI responses, which can be submitted now to build agency relationships).

## Completion Report
- Capability statement path: <file>
- Gaps to fill once registered (UEI, CAGE, certs): <list>
