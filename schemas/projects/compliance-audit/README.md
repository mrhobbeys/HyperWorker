# Schema: compliance-audit

> Use when: preparing for a regulatory or quality audit (SOC 2, ISO 27001, HIPAA, PCI DSS, industry-specific, internal QMS). The schema's value is twofold: (1) Tier 1 REGULATORY rules dominate every decision, and (2) audits cycle annually, so cross-project anti-patterns from prior cycles compound.

## What this schema gives you

- A four-tier system named `REGULATORY / AUDIT-SCOPE / TECHNICAL / DOCUMENTATION`.
- Twelve default tasks across three phases (Assessment, Remediation, Package).
- Capability gates including `evidence-gathering` and `package-assembly`.
- The most aggressive default risk levels in v5.0: every evidence-gathering task is critical.
- A five-member council including a `regulator-perspective` reviewer that reads framework clauses by exact text.
- Banned tokens that surface hedging language (an auditor failure mode).

## Cross-cycle compounding

Year-over-year, anti-patterns tagged `framework:<name>` and `auditor_observation:<text>` accumulate. Subscribing to `cross-project:framework-<framework>` at bootstrap pulls them forward. The `cross-cycle-anti-pattern-watcher` council member surfaces the relevant ones during review.

## Bootstrap

```
hw bootstrap --schema compliance-audit --name <framework>-<year>
```

## Customization

- Replace the `<Framework>` placeholder in `rules-template.md` with the actual framework name and clause numbers.
- Add framework-specific control families as enums in `artifact-extensions.yaml`.
- Adjust `auto_escalation_rules` if your framework has a different highest-stakes path (e.g., HIPAA → PHI handling; PCI → cardholder data).
