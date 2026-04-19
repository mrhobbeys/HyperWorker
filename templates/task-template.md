---
task_id: "XX"
title: "[Descriptive Task Name]"
depends_on: []
assumptions:
  - "[Assumption 1 — what must be true for this task to succeed]"
  - "[Assumption 2]"
phase: 1
status: pending
risk_level: standard  # standard | elevated | critical — see core/VERIFICATION.md
---

# Task XX: [Descriptive Task Name]

> **This is a project task file.** The worker executing this task should follow the instructions below and nothing else. Read `00-REFERENCE-rules.md` before starting.

## What To Do
[One paragraph stating the exact objective. Be specific about the end state.]

## Step-by-Step Instructions

1. [Exact instruction — URL to navigate, button to click, field to fill]
2. [Next step — include exact content to deliver if applicable]
3. [Continue...]

## CRITICAL — [Domain-Relevant Check]
[A mandatory check relevant to the project domain. Examples:]
[- Scan all text for Tier 1 violations from the reference file]
[- Verify all URLs resolve correctly]
[- Confirm output meets platform constraints]
[- Run automated validation if available]

## Do NOT Touch
- [Explicit item 1 — e.g., "Do not modify the About section"]
- [Explicit item 2 — e.g., "Do not change any configuration outside this scope"]
- [Explicit item 3 — e.g., "Do not edit any harness infrastructure files"]

## Baseline
[OPTIONAL — include for tasks that modify existing state. Capture current state before changes.]
[Remove this section for net-new creation tasks.]

## Verification Checklist
- [ ] [Specific, observable deliverable — e.g., "Subject line under 50 characters"]
- [ ] [Specific, observable deliverable — e.g., "Run npm test — all tests pass, exit code 0"]
- [ ] Zero violations of reference rules (Tier 1 checked first)
- [ ] No unintended changes to out-of-scope areas
- [ ] [CONDITIONAL: "All content saved as DRAFT (not published)" — if draft_only is true]
- [ ] STOP HERE — do not proceed to next task

## Evidence Trail

| Check | Method | Result | Pass |
|---|---|---|---|
| [Checklist item] | [How you verified it] | [What you found] | [Yes/No] |

## Post-Task Discovery Capture
If you encountered anything unexpected — a failed assumption, a platform behavior
that wasn't documented, a constraint that should exist but doesn't — note it here.
The orchestrator will review and decide whether to promote it to DISCOVERIES.md.

- **Discovery:** [what you found — leave blank if nothing unexpected]
- **Assumption affected:** [which assumption was wrong or missing]
- **Suggested rule:** [what rule would have prevented this]
