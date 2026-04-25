---
id: T-001
kind: task
schema: client-onboarding
phase: 1
risk_level: elevated
required_tools: [admin_console, file_write]
delivery_mode: prescribed
depends_on: [T-000]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-001#<short-hash>]"
acceptance_criteria:
  - "Account provisioned with least-privilege defaults."
  - "SSO configured (SAML or OIDC); login round-trip tested with the designated contact."
  - "DNS propagation buffer noted in task timeline (cross-project anti-pattern: SSO-config requires up-to-48h propagation)."
---

# Task T-001: Provision Account + SSO  *(elevated)*

## Steps

1. Recite + SCAN. Read any subscribed AP-* with `integration: sso`.
2. Provision account.
3. Configure SSO. Document any vendor quirks observed as anti-pattern candidates.
4. Test login round-trip with the designated contact's credentials.
5. Three failure scenarios: (a) SSO callback URL misconfigured, (b) IdP rejects metadata, (c) DNS propagation incomplete at first login attempt.
