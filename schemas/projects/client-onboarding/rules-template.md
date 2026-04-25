# 00-REFERENCE-rules.md — <Client Name> Onboarding

## Precedence Order

When rules conflict, higher tiers override lower tiers. Tier 1 cannot be overridden.

### Tier 1: DATA-SECURITY  (absolute — never override)

- No client data in unencrypted channels.
- Access provisioned on least-privilege basis.
- All data transfers logged with timestamp, source, destination, and record count.
- Compliance scope (`OR-001.client_compliance_scope`) is inherited by every task.

@@SCAN_1_1: List the data classes this task touches (PII / PHI / financial / public-only).
@@SCAN_1_2: Confirm all data transfers in this task are over encrypted channels (yes / not-applicable).

### Tier 2: CLIENT-CONTRACT  (overrides platform and process)

- Onboarding must complete within the SLA in `OR-001.contract_sla_days`.
- Only deliver features in the signed scope.
- Client communications go through the designated contact only (`OR-001.client_designated_contact`).

@@SCAN_2_1: Is this task in the signed scope? Cite the OR-001 line.

### Tier 3: PLATFORM  (overrides process)

- SSO supports SAML 2.0 and OIDC only.
- Data import max file size: 500MB. Larger imports use the bulk-API path.
- Account provisioning requires admin access; routine users cannot self-provision.

@@SCAN_3_1: Name any platform constraint that affects this task's approach.

### Tier 4: PROCESS  (lowest precedence)

- Document configuration decisions as `DEC-XXX`.
- Training sessions recorded with client consent.
- Handoff includes a written runbook.
