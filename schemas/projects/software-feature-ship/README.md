# Schema: software-feature-ship

> Use when: shipping a feature with strict surface ordering — schema → API → frontend → tests → deploy — and security as the load-bearing precedence tier.

## What this schema gives you

- A four-tier precedence system named for software context (`SECURITY / ARCHITECTURE / TESTING / STYLE`).
- Nine default tasks across spec, schema migration, backend, tests, frontend, integration, and staging/production deploy.
- Capability gates for `schema-migration`, `code-edit`, `test-write`, `test-run`, `deploy`, and `smoke-test` task kinds.
- Auto-escalation rules: any task touching auth/session code is critical; production deploy is critical; API-contract-changing tasks are elevated.
- A council with `contract-stability-reviewer`, `test-coverage-reviewer`, `security-reviewer`, and `rollback-reviewer`.

## When NOT to use

- For exploration / spike work where contract stability and rollback are not goals → consider a custom schema or no schema (run on default templates).
- For documentation-only work → use a custom schema with relaxed verification.

## Bootstrap

```
hw bootstrap --schema software-feature-ship --name <feature-id>
```

Operator answers schema questions (surfaces touched, deployment targets, test baseline). Verification Checkpoint runs `contract-stability-reviewer` to confirm the spec is consistent with existing contracts.

## Customization

- Edit `verification.yaml` to widen or narrow auto-escalation rules.
- Add domain-specific findings categories via `artifact-extensions.yaml`.
- Adjust task templates to your build system (e.g., replace generic `test_run` with your `pytest`/`go test`/`npm test` invocation).
