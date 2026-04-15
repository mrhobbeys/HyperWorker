# Scenario Brief: Compliance Audit Preparation

> **Primary mechanism showcase:** Precedence + Lock — regulatory tiers dominate every decision, and the zero-distraction-tolerance of audit prep makes the Lock mechanism load-bearing.

## The Project

Prepare for an upcoming compliance audit (could be SOC 2, ISO 27001, PCI DSS, industry-specific regulation, or internal quality audit). The project covers: gap assessment, evidence gathering, policy documentation, remediation of gaps, and audit-ready package assembly. Estimated 8-12 tasks across 3 phases.

## How the Five Mechanisms Apply

### Lock
Audit prep is the one domain where the Lock mechanism is non-negotiable. With an audit date approaching, every distraction is a risk. "We should also update the website" → backlog, immediately. "Can we also fix the onboarding flow?" → backlog. The audit has a deadline and consequences for failure.

The distraction-blocking protocol is most valuable here. The operator WILL be tempted to context-switch because audit prep is tedious. The harness's response: "Are we officially shelving audit prep to promote [new idea] to the active slot? The audit is in 6 weeks."

### Atomicity
Audit tasks decompose naturally into evidence-gathering units:

```
Phase 1: Assessment (6+ weeks before audit)
  01: Map audit requirements to current controls (depends on: nothing)
  02: Identify gaps — controls missing or undocumented (depends on: 01)
  03: Prioritize gaps by severity and remediation effort (depends on: 02)

Phase 2: Remediation [checkpoint — gap assessment reviewed before remediation starts]
  04: Draft missing policies/procedures for high-severity gaps (depends on: 03)
  05: Implement technical controls for high-severity gaps (depends on: 03)
  06: Gather evidence for existing controls (depends on: 01)
  07: Conduct internal review of remediated items (depends on: 04, 05, 06)

Phase 3: Package [checkpoint — all remediation reviewed before final assembly]
  08: Assemble audit-ready evidence package (depends on: 07)
  09: Prepare management assertion / self-assessment (depends on: 08)
  10: Conduct mock audit walkthrough (depends on: 08, 09)
  11: Final review and submission (depends on: 10)
```

Each task is verifiable: "Gap assessment complete" means every audit requirement has a control mapping. "Evidence gathered" means every control has supporting documentation. No ambiguity.

### Dependency
The dependency chain is strict and sequential. You can't remediate gaps (Phase 2) until you've assessed them (Phase 1). You can't assemble the evidence package (Phase 3) until remediation is complete.

**Cascade example:** If the regulatory framework updates mid-project (it happens), Task 01 gets re-done. This cascades to Tasks 02-11 — every gap assessment, remediation, and evidence item needs re-evaluation against the new requirements. The TASK-STATE engine flags the entire chain.

**Assumption to track:** "The audit scope has been confirmed and won't change." If the auditor expands scope (adds a new control family), the gap assessment (Task 02) needs re-running and downstream tasks may be invalidated.

### Memory Pipeline
Compliance audit prep is one of the strongest memory pipeline use cases because audits are cyclical — you'll do this again next year.

**Discoveries:**
- **DISC-001:** "Auditor asked for evidence of quarterly access reviews, but our policy only specifies annual. Policy-evidence mismatch." → Scope: `Universal`. Promotes to: "Ensure policy frequency matches evidence frequency before audit."
- **DISC-002:** "Screenshots of security configurations were rejected — auditor wanted system-generated reports with timestamps." → Scope: `Universal`. Promotes to: "Use system-generated reports, not screenshots, for all technical evidence."
- **DISC-003:** "The third-party vendor risk assessment template didn't include a section for subprocessor data handling." → Scope: `Framework:[Specific]`. May promote to `Universal` if multiple frameworks require it.

**Year-over-year compounding:** By the third audit cycle, the harness's LEARNINGS.md contains dozens of validated rules about what auditors accept, what they reject, and what to prepare in advance. Each audit gets smoother. This is the memory pipeline at its most valuable — turning painful annual events into an improving process.

### Precedence (Primary Showcase)
Compliance audit prep uses ALL four tiers at full weight, and conflicts between them are common.

| Tier | Name | Example Rules |
|---|---|---|
| 1 | REGULATORY | All controls must meet the specific framework requirements (SOC 2 criteria, ISO clauses, etc.). No exceptions. Evidence must be independently verifiable. |
| 2 | AUDIT-SCOPE | Only prepare evidence for controls in the confirmed audit scope. Do not remediate out-of-scope items during this project. Auditor communications go through the designated contact only. |
| 3 | TECHNICAL | Evidence must be from production systems only (not staging). Reports must include date ranges matching the audit period. Access logs must be unmodifiable. |
| 4 | DOCUMENTATION | Follow the organization's policy template format. Use consistent naming conventions for evidence files. Include revision history on all policies. |

**Conflict examples that the precedence resolves:**

1. *Tier 4 says: "Follow the organization's policy template."* But the auditor (Tier 1: REGULATORY) requires specific language that doesn't fit the template. Tier 1 wins — rewrite the policy section to meet the regulatory requirement, even if it breaks template consistency.

2. *Tier 3 says: "Evidence must be from production systems."* But a new control was implemented in staging and hasn't been promoted to production yet. The audit scope (Tier 2) says this control is in scope. The resolution: escalate — you can't provide production evidence for something that's only in staging. The task blocks, and the orchestrator decides whether to rush the promotion to production or negotiate the control out of scope with the auditor.

3. *Tier 4 says: "Consistent naming conventions for evidence files."* But one system exports reports with auto-generated names that can't be changed (Tier 3: TECHNICAL). Tier 3 wins — use the auto-generated names and add a mapping document instead of renaming.

## Config Highlights

```yaml
precedence_tiers:
  1: "REGULATORY"
  2: "AUDIT-SCOPE"
  3: "TECHNICAL"
  4: "DOCUMENTATION"

scope_taxonomy:
  - "Universal"
  - "Framework:[Name]"        # e.g., Framework:SOC2, Framework:ISO27001
  - "Control:[Family]"        # e.g., Control:AccessManagement
  - "AuditCycle:[Year]"       # e.g., AuditCycle:2026

memory:
  review_cadence_months: 3    # Quarterly — matches typical audit evidence periods

worker:
  draft_only: true             # All policies and evidence reviewed before submission
  content_mode: "execute"      # Follow remediation instructions exactly
  output_hashing: true         # Critical — evidence must not change after review
```

## What This Case Study Demonstrates

1. **All four precedence tiers loaded and in active conflict** — the fullest use of the Precedence mechanism
2. **Lock mechanism under real deadline pressure** — audit dates don't move
3. **Cyclical projects** where memory compounds year-over-year
4. **Escalation protocol in action** — some conflicts can't be resolved by precedence alone
5. **Assumption tracking** for scope stability (the thing most likely to change mid-project)

## Reference
For full file examples, see the [Marketing Funnel Launch](../01-marketing-funnel/) case study.
