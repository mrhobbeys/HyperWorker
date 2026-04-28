# Bootstrap Probe — compliance-audit

> Read by the executor at `hw bootstrap` time. The probe enumerates audit-framework controls in scope against the framework's canonical control list. See `core/SUBSTRATE.md` §Bootstrap Inventory Sweep.

## Probe shape — schema-declared stub (pending first project)

Compliance-audit probes are framework-specific and v5.1.1 ships this as a documented stub. Until the first compliance-audit project surfaces the canonical probe, the shape is:

```yaml
probe_method: "schema-declared-stub-pending-audit-framework"
expected_schema_declarations:
  - audit_framework:
      type: enum
      values: [nist-csf, soc2, hipaa-security, iso-27001, pci-dss-4, custom]
      required: true
  - canonical_control_list_source:
      nist-csf:       "NIST CSF 2.0 control catalog"
      soc2:           "AICPA TSC 2017 (with 2022 points-of-focus)"
      hipaa-security: "HIPAA Security Rule 164.308 / 164.310 / 164.312 / 164.314 / 164.316"
      iso-27001:      "ISO/IEC 27001:2022 Annex A"
      pci-dss-4:      "PCI DSS v4.0 requirements 1-12"
      custom:         "operator-supplied control list as a markdown file"
```

For v5.1.1, the agent at bootstrap asks the operator to declare framework + scope (which controls / Trust Service Criteria / domains apply). The agent emits:

```
bootstrap.probe_skipped
  reason: "compliance-audit probe is stubbed pending first-project empirical signal; operator manually attested control scope at bootstrap"
```

## When the probe is implemented

Once a compliance-audit project surfaces the canonical probe shape (e.g., parsing an XBRL feed of NIST CSF, fetching a SOC 2 readiness checklist API), this file gets rewritten. Until then, manual attestation is the documented path.

## Operator manual attestation shape

The conversation should produce structured attestation:

```
Framework: <nist-csf | soc2 | hipaa-security | iso-27001 | pci-dss-4 | custom>
Audit type: <readiness | gap-analysis | full-audit | recertification>
In-scope controls (by ID or domain):
  - <ID-or-domain>: <name>
  - <ID-or-domain>: <name>
Out-of-scope controls (with rationale):
  - <ID-or-domain>: <reason>
Auditor: <internal | external + firm name>
Target completion: <date or null>
```

The agent records the attestation as `declared`; PROJECT.md §Scope is written from it.
