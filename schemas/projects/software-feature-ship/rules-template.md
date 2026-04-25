# 00-REFERENCE-rules.md — <Feature Name>

## Precedence Order

When rules conflict, higher tiers override lower tiers. Tier 1 cannot be overridden.

### Tier 1: SECURITY  (absolute — never override)

- No secrets in code, commit history, logs, or test fixtures.
- All auth tokens encrypted at rest.
- Input validation on every user-facing endpoint.
- PII handled per the project's declared compliance scope only.

@@SCAN_1_1: Name any user-facing input introduced or modified by this task.
@@SCAN_1_2: Confirm no secrets are written to code, logs, or commits (yes / not-applicable).

### Tier 2: ARCHITECTURE  (overrides testing and style)

- Database migrations must be reversible. A down migration is required.
- API contract changes are versioned. No edits to existing version contracts.
- No new external dependencies without a `DEC-XXX` decision artifact.
- Backend ↔ frontend communicate only through documented contracts.

@@SCAN_2_1: Does this task alter an existing API contract? If yes, state the version bump and migration path.

### Tier 3: TESTING  (overrides style)

- Every new code path requires a unit test.
- Cross-service calls are covered by integration tests.
- No deploy without passing CI on the target branch.

@@SCAN_3_1: Name the test command this task runs and the expected exit code.

### Tier 4: STYLE  (lowest precedence)

- Follow the team code style guide.
- Comments explain why, not what.
- Descriptive variable names.

## Canonical Facts — Do Not Normalize

| Fact | Canonical Form | Do NOT Normalize To |
|---|---|---|
| Production base URL | "https://api.example.com" | "api.example.com" |
| Default port for staging | "8443" | "443" |
