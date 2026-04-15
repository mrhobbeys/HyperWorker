# Scenario Brief: Software Feature Ship

> **Primary mechanism showcase:** Dependency — a strict code → test → review → deploy chain where skipping a step breaks everything downstream.

## The Project

Ship a new user authentication feature (OAuth2 social login) for a web application. The feature touches the database schema, backend API, frontend UI, and deployment pipeline. Estimated 8-12 tasks across 3 phases.

## How the Five Mechanisms Apply

### Lock
The auth feature is the active project. A request to "also fix the dashboard bug" gets logged to the backlog. The operator decides later whether to park auth and promote the bug fix, or finish auth first.

### Atomicity
Each task is one unit of work that fits in a single AI session. Examples of well-sized tasks: "Write the database migration for the users table" (not "build the auth system"). "Write unit tests for the OAuth callback handler" (not "test everything"). Each task file includes the exact files to modify, the exact tests to run, and an explicit "Do NOT Touch" list preventing scope creep into unrelated code.

### Dependency (Primary Showcase)
This is where the harness earns its keep. The dependency chain is strict:

```
Phase 1: Foundation
  01: Database migration (depends on: nothing)
  02: OAuth provider config (depends on: nothing)
  03: Backend auth routes (depends on: 01, 02)
  04: Unit tests for auth routes (depends on: 03)

Phase 2: Integration [checkpoint — human reviews all Phase 1 before continuing]
  05: Frontend login component (depends on: 03)
  06: Frontend tests (depends on: 05)
  07: Integration tests — full auth flow (depends on: 04, 06)

Phase 3: Ship
  08: Update API documentation (depends on: 03)
  09: Staging deployment + smoke test (depends on: 07)
  10: Production deployment (depends on: 09)
```

If Task 03 changes the API contract, Tasks 04-10 all need re-evaluation. The TASK-STATE engine catches this: when Task 03's output hash changes, all downstream tasks with `depends_on: ["03"]` (and their dependents) get flagged. The orchestrator reviews whether the change breaks assumptions.

**Key assumption to track:** "OAuth provider API is stable and matches documented spec." If this assumption fails mid-project (provider changes their API), every task depending on Task 02 gets invalidated.

### Memory Pipeline
Discoveries captured during this project:

- **DISC-001:** "Provider X's OAuth token refresh endpoint returns 500 intermittently under load." → Promoted to LEARNINGS.md with scope tag `Provider:X` (affects only projects integrating Provider X — not Universal, because a project that never touches Provider X has no use for this rule).
- **DISC-002:** "Frontend OAuth redirect fails silently in Safari when third-party cookies are blocked." → Promoted with scope tag `Feature:Auth` (only affects auth-related work).
- **DISC-003:** "The staging environment's database connection pool maxes out at 10 connections." → Promoted with scope tag `Environment:staging` (affects anything deploying to this environment — not Universal, because production and other environments have different pool sizes).

### Precedence
Example tiers for a software project:

| Tier | Name | Example Rules |
|---|---|---|
| 1 | SECURITY | No secrets in code. All auth tokens encrypted at rest. Input validation on all user-facing endpoints. |
| 2 | ARCHITECTURE | Follow existing API patterns. No new external dependencies without review. Database migrations must be reversible. |
| 3 | TESTING | All new code requires unit tests. Integration tests for cross-service calls. No deploying without passing CI. |
| 4 | STYLE | Follow team code style guide. Descriptive variable names. Comments explain "why" not "what." |

**Conflict example:** A Tier 4 style rule says "keep functions under 20 lines." But implementing proper input validation (Tier 1: SECURITY) on the OAuth callback requires a 35-line function. Tier 1 wins — security over style. The worker doesn't need to guess; the precedence resolves it.

## Config Highlights

```yaml
precedence_tiers:
  1: "SECURITY"
  2: "ARCHITECTURE"
  3: "TESTING"
  4: "STYLE"

scope_taxonomy:
  - "Universal"
  - "Feature:[Name]"
  - "Service:[Name]"

worker:
  draft_only: false        # Code goes directly to branch, not "draft"
  content_mode: "generate" # Worker writes code within constraints
  output_hashing: true     # Critical for detecting API contract changes
```

## What This Case Study Demonstrates

1. **Strict dependency chains** where one change cascades through the entire project
2. **Assumption tracking** as a first-class concern (provider API stability)
3. **Phase checkpoints** gating integration work until foundation is solid
4. **Discovery capture** distinguishing universal findings from feature-specific ones
5. **Precedence resolving real conflicts** between security requirements and code style

## Reference
For full file examples, see the [Marketing Funnel Launch](../01-marketing-funnel/) case study — it uses the same file formats with a different domain.
