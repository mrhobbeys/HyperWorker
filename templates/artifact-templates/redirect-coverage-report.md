---
artifact_kind: redirect_coverage_report
authority: projection
projection_path: projects/<id>/REDIRECT-COVERAGE-REPORT.md
generated_from: "task.complete events with redirect_implications + external_state.read_back events for redirections-list endpoints"
---

# Redirect Coverage Report — `<project-id>`

> Aggregated projection at session.handoff. Regenerated from every `task.complete` event in this project's chain whose payload includes `redirect_implications`, joined against `external_state.read_back` events whose `artifact_url` references the platform's redirections-list endpoint. The report is a projection — the events are the source of truth. Hand-edits are overwritten on next regeneration.

## Coverage table

| from_url | to_url | reason | status | source task | applied at | verified at |
|---|---|---|---|---|---|---|
| <old-url> | <new-url> | <one-sentence reason> | planned \| applied \| verified \| deferred \| excluded | T-NNN | <ts or — > | <ts or — > |
| ... | ... | ... | ... | ... | ... | ... |

## Status legend

| Status | Meaning |
|---|---|
| `planned` | Redirect is intended but not yet applied to the platform. |
| `applied` | Redirect was created on the platform; awaiting paired `external_state.read_back` verification. |
| `verified` | Applied AND a paired `external_state.read_back` against the redirections-list endpoint confirms the entry exists with the expected `from`/`to` values and `divergence_detected: false`. |
| `deferred` | Operator decided to apply later; the row is recorded for visibility, not action. |
| `excluded` | Intentionally NO redirect (e.g., a 410 Gone — the URL is supposed to disappear). The reason captures why. |

## Layer 1 verification rule

Every row with `status: applied` must have a paired `external_state.read_back` event whose `artifact_url` is the platform's redirections-list endpoint and whose `divergence_detected: false`. Without that pair, the row stays `applied` indefinitely; Layer 1 FAILs `redirect_coverage_unverified` at session.handoff.

For platforms without a queryable redirections list (e.g., manual operator-applied redirects on a static-site host), `equality_method: manual-attestation` on the read-back is acceptable.

For rows with `status: deferred` or `status: excluded`, the reason field is required and Layer 1 reads it as the rationale; no read-back is required.

## Aggregation algorithm

1. Scan `events.jsonl` for every `task.complete` event in the active project. Collect all `redirect_implications` lists (skip events where the field is null).
2. For each row, find the most recent `task.complete` mentioning that exact `from_url`. If multiple tasks declare the same `from_url`, the most recent declaration wins; older declarations are listed in the report's "Superseded rows" section for traceability.
3. Join against `external_state.read_back` events whose `artifact_url` matches the platform's redirections-list endpoint pattern. Match `from_url` against the read-back's `post_state_ref` (REST roundtrip with the entry visible) or attestation token.
4. Sort rows by `status` (verified, applied, deferred, excluded, planned) then alphabetically by `from_url`.
5. Render the table.

## Superseded rows

| from_url | to_url | reason | status | superseded by task | superseded at |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

(Empty unless the same `from_url` was declared by more than one task.)

## See also

- `core/SUBSTRATE.md` §External State Read-Back
- `schemas/projects/marketing-campaign/artifact-extensions.yaml` `task_completion.field_overrides.redirect_implications`
- `schemas/projects/marketing-campaign/verification.yaml` redirect-coverage check
