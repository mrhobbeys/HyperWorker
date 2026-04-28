---
event_kind: external_state.read_back
authority: event
---

# External State Read-Back — `<task-id>`

> Projection-form record of a single `external_state.read_back` event. The event itself is the source of truth; this template documents the human-readable form an agent or operator might write before emitting the event.

## Event payload (this template's fields populate the payload directly)

| Field | Value |
|---|---|
| `task_id` | `T-NNN` |
| `artifact_url` | `<URL of the external surface that was re-read>` |
| `pre_state_ref` | `screenshot:tasks/T-NNN-pre.png` \| `hash:<sha256>` \| `manual-attestation:operator-confirmed` \| `none` |
| `post_state_ref` | `screenshot:tasks/T-NNN-post.png` \| `hash:<sha256>` \| `manual-attestation:operator-confirmed` |
| `equality_method` | `visual-diff` \| `rest-roundtrip` \| `manual-attestation` |
| `divergence_detected` | `true` \| `false` |
| `divergence_notes` | `<one or two sentences if divergence_detected; else null>` |

## Equality method guide

| Method | Use when |
|---|---|
| `visual-diff` | The platform surfaces the mutation visibly (a CMS page, a published email template). Agent records pre- and post-screenshots; equality is byte-equality of relevant regions or operator visual confirmation. |
| `rest-roundtrip` | The platform surfaces the mutation via a queryable API. Agent records the SHA-256 of the canonical JSON of the GET response before and after; equality is hash-equal on relevant fields. |
| `manual-attestation` | The platform does not surface state for re-read (e.g., closed-system third-party integrations). Agent records `manual-attestation:<operator-token>` with operator-recorded confirmation. The schema's `fallback_equality_method` declares this as acceptable. |

## When this is required

The schema's `capability-gates.yaml` `external_state_readback.required_for` list declares which tasks need a paired read-back. v5.1.1 enables this for marketing-campaign with two patterns:

- Tasks marked `critical-risk: true` in front-matter.
- Tasks with `delivery_mode: live-edit`.

A task matching any pattern requires this event within 5 events after `task.complete`. Layer 1 verification FAILs `external_state_readback_missing` if absent.

## Divergence handling

If `divergence_detected: true`, Layer 1 emits a WARNING and requires a follow-up `friction.log` event referencing the divergence. The friction-log entry captures the surprise; the read-back captures the structural fact that pre- and post-state differed in a way the mutation should not have produced.

## See also

- `core/SUBSTRATE.md` §External State Read-Back
- `core/VERIFICATION.md` §Layer 1 — Structural Checks (row 9)
- `schemas/projects/marketing-campaign/capability-gates.yaml` `external_state_readback:` block
