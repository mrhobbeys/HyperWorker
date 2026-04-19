# Scenario Brief: Client Onboarding Process

> **Primary mechanism showcase:** Memory Pipeline — repeatable process where each client teaches you something, and scope tags prevent one client's quirks from infecting another's setup.

## The Project

Onboard a new client onto your service platform. This is a repeatable process — you do it for every new client — but each client has unique requirements, integrations, and constraints. The project covers: kickoff call prep, account provisioning, data migration, configuration, training, and handoff. Estimated 6-8 tasks across 2 phases.

## How the Six Mechanisms Apply

### Lock
Client onboarding for "Acme Corp" is the active project. When another client signs mid-onboarding, their setup gets logged to the backlog. You finish Acme before starting the next client — no half-configured accounts.

### Atomicity
Each task is one onboarding step. "Provision the client's account and configure SSO" is one task. "Migrate their historical data" is a separate task. Each has its own verification checklist: SSO works, data counts match, user permissions are correct.

### Dependency
Typical onboarding dependency chain:

```
Phase 1: Setup
  01: Kickoff call — confirm requirements (depends on: nothing)
  02: Provision account + SSO config (depends on: 01)
  03: Migrate historical data (depends on: 02)
  04: Configure custom integrations (depends on: 02, 01)

Phase 2: Handoff [checkpoint — client reviews before training]
  05: Build client-specific dashboard (depends on: 03, 04)
  06: Conduct training session (depends on: 05)
  07: Handoff + support documentation (depends on: 06)
```

**Key assumption:** "Client's existing data is in a format we can import." If this fails (Task 03 discovers their data is in an unsupported format), Task 03 blocks and downstream tasks (05-07) can't proceed until the planner decides how to handle it.

### Memory Pipeline (Primary Showcase)
This is where the harness compounds knowledge across clients.

**Discoveries from Acme Corp onboarding:**
- **DISC-001:** "Acme's legacy system exports CSV with semicolons, not commas — our import tool choked." → Scope: `Client:AcmeCorp` (specific to their data format)
- **DISC-002:** "SSO configuration requires a 24-hour DNS propagation window we didn't account for in the timeline." → Scope: `Universal` (affects all future onboardings)
- **DISC-003:** "Acme's compliance team requires all data handling documentation before they'll approve migration." → Scope: `Client:AcmeCorp` (their specific requirement)

**What gets promoted to LEARNINGS:**
- DISC-002 becomes Learning L-014: "Add 24-48 hour buffer between SSO configuration and data migration tasks to account for DNS propagation." Category: Workflow. Scope: Universal. Every future onboarding project loads this learning.
- DISC-001 becomes Learning L-015: "When importing CSV data, verify delimiter format before running the import tool." Category: Tool Behavior. Scope: Universal (generalized from the specific incident).
- DISC-003 stays as a discovery scoped to `Client:AcmeCorp`. If a second client requires the same, it gets promoted to `Universal` with the pattern "Ask about compliance documentation requirements during kickoff."

**The scope tag payoff:** When onboarding the next client ("Beta Inc"), the planner loads LEARNINGS.md filtered for `Universal` scope. L-014 and L-015 appear. Acme-specific learnings don't — because Beta's data format and compliance requirements may be different. This prevents cross-client contamination while preserving universal lessons.

### Precedence
Example tiers for a service onboarding:

| Tier | Name | Example Rules |
|---|---|---|
| 1 | DATA-SECURITY | No client data in unencrypted channels. Access provisioned on least-privilege basis. All data transfers logged. |
| 2 | CLIENT-CONTRACT | Onboarding must be completed within the contractual SLA. Only deliver features included in the signed scope. |
| 3 | PLATFORM | Account provisioning requires admin access. SSO supports SAML 2.0 and OIDC only. Data import max file size: 500MB. |
| 4 | PROCESS | Follow the standard onboarding checklist. Document all configuration decisions. Training session must be recorded. |

## Config Highlights

```yaml
precedence_tiers:
  1: "DATA-SECURITY"
  2: "CLIENT-CONTRACT"
  3: "PLATFORM"
  4: "PROCESS"

scope_taxonomy:
  - "Universal"
  - "Client:[Name]"
  - "Integration:[Type]"

memory:
  review_cadence_months: 1    # High client volume = monthly review

executor:
  draft_only: true             # All configs reviewed before applying
  content_mode: "execute"      # Follow the checklist exactly
```

## What This Case Study Demonstrates

1. **Scope tags preventing cross-client contamination** — the core memory pipeline value
2. **Discovery → Learning promotion** with explicit generalization from specific incidents
3. **Repeatable project structure** where the template stays the same but content changes per client
4. **Assumption tracking** on data format compatibility
5. **Knowledge compounding** — each onboarding makes the next one smoother

## Reference
For full file examples, see the [Marketing Funnel Launch](../01-marketing-funnel/) case study.
