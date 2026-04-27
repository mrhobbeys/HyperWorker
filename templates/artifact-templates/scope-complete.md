---
event_kind: scope.complete
projection_path: projects/<id>/SCOPE-COMPLETE.md
authority: projection
---

# Scope Completeness Snapshot — <project-id>

> Projection of the most recent `scope.complete` event. The event payload is the source of truth; this file is the human-readable rendering. Hand-edits are overwritten on next regeneration.

## Snapshot

- **Project:** `<project-id>`
- **Event:** `EV-NNNN`
- **Captured at:** `<ISO 8601 ts>`
- **Closing actor:** `<actor-id>`

## Scope items

| ID | Name | Terminal state | Reason |
|---|---|---|---|
| T-NNN | <name> | complete \| deferred \| excluded-after-discovery \| escalated | <one-line reason or null> |
| T-NNN | <name> | ... | ... |

## Allowed terminal states (per schema `capability-gates.yaml`)

| Value | Meaning |
|---|---|
| `complete` | The §Scope item was actuated to its declared terminal state. |
| `deferred` | The item is in scope but was intentionally not actuated this session; reason captures why and what gates resumption. |
| `excluded-after-discovery` | The item, after probing the actual project surface, fell outside the rebrand/synthesis/deployment mission; reason captures the discovery. |
| `escalated` | The item could not be classified by the closing actor; operator decides at handoff acknowledgement. |

A schema's `scope_completeness.allowed_terminal_states` declares the subset acceptable for that schema. Layer 1 verification rejects any entry whose `terminal_state` is outside the declared set.

## Layer 1 verification check

The harness runs three checks at `session.handoff` time:

1. The most recent `scope.complete` event precedes the `session.handoff`. If absent, FAIL `scope_completeness_missing`.
2. Every entry's `terminal_state` is in the schema's allowed set. If not, FAIL `scope_completeness_terminal_state_disallowed`.
3. Every PROJECT.md §Scope item appears (by `id` or `name`) in the snapshot. If a §Scope item is missing, FAIL `scope_completeness_unrepresented_item`.

## See also

- `core/SUBSTRATE.md` §Scope Completeness
- `core/VERIFICATION.md` §Layer 1 — Structural Checks
- `schemas/projects/<schema>/capability-gates.yaml` `scope_completeness:` block
