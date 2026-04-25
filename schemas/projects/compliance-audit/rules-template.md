# 00-REFERENCE-rules.md — <Framework> Audit Cycle <Year>

## Precedence Order

When rules conflict, higher tiers override lower tiers. Tier 1 cannot be overridden.

### Tier 1: REGULATORY  (absolute — never override)

- All controls must meet `<Framework>` requirements as published. Cite the criterion / clause.
- Evidence must be independently verifiable.
- No fabricated, simulated, or backdated evidence.
- Auditor communications go through `OR-001.auditor_contact` only.

@@SCAN_1_1: Name the framework criterion / clause this task's output supports.
@@SCAN_1_2: Confirm the evidence is from production (not staging) and is system-generated, not screenshot.

### Tier 2: AUDIT-SCOPE  (overrides technical and documentation)

- Only prepare evidence for controls in the confirmed audit scope.
- Do not remediate out-of-scope items.
- Scope changes require operator approval and a new `DEC-XXX`.

@@SCAN_2_1: Cite the AUDIT-SCOPE line placing this control in scope.

### Tier 3: TECHNICAL  (overrides documentation)

- Evidence from production systems only.
- Reports include date ranges matching `OR-001.audit_period`.
- Access logs must be tamper-evident.

@@SCAN_3_1: State the audit period date range and confirm this evidence falls inside.

### Tier 4: DOCUMENTATION  (lowest precedence)

- Follow organization's policy template format.
- Consistent naming conventions for evidence files.
- Revision history on all policies.

## Banned Tokens

| Banned Token | Safe Replacement | Tier | Why |
|---|---|---|---|
| approximately | <exact value> | 1 | Audit evidence requires precision. |
| should be | is | 1 | Hedging triggers auditor follow-up. |
| we believe | <evidence-citation> | 1 | Belief is not evidence. |
