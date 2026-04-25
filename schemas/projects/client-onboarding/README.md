# Schema: client-onboarding

> Use when: onboarding a new client through a repeatable flow (kickoff → provision → migrate → configure → train → handoff). The value is cross-client compounding: anti-patterns from past clients inform the current one.

## What this schema gives you

- A four-tier system named `DATA-SECURITY / CLIENT-CONTRACT / PLATFORM / PROCESS`.
- Seven default tasks across two phases.
- Capability gates for `client-meeting`, `account-provision`, `data-migration`, `configuration`, `documentation`.
- A council that includes a `cross-client-anti-pattern-watcher` reading subscribed cross-project anti-patterns.
- Auto-escalation: PII/PHI work → critical; HIPAA-scope migration → critical; SSO provisioning → elevated.

## Cross-project compounding

After completing an onboarding, anti-patterns flagged `client_specific: false` and `vendor_quirk: <name>` should be tagged `cross-project:integration-<vendor>`; future projects subscribing to that scope will read them at the council layer. This is how knowledge actually compounds across clients without contaminating one client with another's quirks.

## Bootstrap

```
hw bootstrap --schema client-onboarding --name <client-id>
```

## Customization

- Adjust integration enum in `artifact-extensions.yaml` to match your platform's actual integrations.
- Add a `vendor:<name>` tag convention to anti-patterns so cross-project subscriptions can target by vendor.
