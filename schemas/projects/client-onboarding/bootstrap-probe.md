# Bootstrap Probe — client-onboarding

> Read by the executor at `hw bootstrap` time. The probe enumerates the customer accounts, contacts, or tenants in scope against the system of record. See `core/SUBSTRATE.md` §Bootstrap Inventory Sweep.

## Probe shape — schema-declared stub (pending first project)

Client-onboarding probes are platform-specific and v5.1.1 ships this as a documented stub. The first client-onboarding project bootstrapped under v5.1.1 produces empirical signal that nails down the canonical probe; until then, the shape is:

```yaml
probe_method: "schema-declared-stub-pending-customer-system"
expected_schema_declarations:
  - canonical_system_of_record:
      type: enum
      values: [salesforce, hubspot, dynamics, custom]
      required: true
  - probe_implementation:
      salesforce: "SOQL: SELECT Id, Name FROM Account WHERE <scope-criteria>"
      hubspot:    "GET /crm/v3/objects/companies?properties=name&limit=100"
      dynamics:   "GET /api/data/v9.2/accounts?$select=name&$filter=<scope-criteria>"
      custom:     "operator-declared filesystem or REST shape"
```

For v5.1.1, the agent at bootstrap asks the operator to manually attest the inventory: "list the accounts / contacts / tenants in scope," recording the answer. The agent emits:

```
bootstrap.probe_skipped
  reason: "client-onboarding probe is stubbed pending first-project empirical signal; operator manually attested inventory at bootstrap"
```

## When the probe is implemented

After a few client-onboarding bootstraps surface the actual probe shape, this file gets rewritten with the canonical implementation and the schema removes the `bootstrap.probe_skipped` default. Until then, manual attestation is the documented path.

## Operator manual attestation shape

When the agent asks the operator to attest, the conversation should produce a structured list:

```
Account: Acme Corp
  Contact: jane@acmecorp.example
  Tenant ID: acme-prod-01
  Migration source: legacy-stack-export.csv
Account: Beta LLC
  ...
```

The agent records this list and treats it as the `declared` set. PROJECT.md §Scope is written from the attestation. No `bootstrap.inventory_diff` event is emitted in the skip path; the `bootstrap.probe_skipped` event with the attestation-based reason is sufficient for Layer 1.
