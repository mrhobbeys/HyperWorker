---
event_kind: evidence.capture
projection_path: projects/<id>/evidence/<ED-NNN>.md
authority: projection
---

# ED-NNN — <one-line summary>

> Projection of one `evidence.capture` event. The event payload is the source of truth; this file is the readable rendering. Hand-edits are overwritten on next regeneration.

- **Event:** `EV-NNNN`
- **Captured at:** `<ISO 8601 UTC>`
- **Produced by:** `<the exact command, request, or action>`
- **Summary:** <one line: what this output shows>

## Output

```
<the content field, verbatim and sanitized — no credentials, tokens, keys, or customer data>
```

<Or, when the capture used the path form:>

- **Content path:** `<workspace-relative path>`
- **SHA-256:** `<full hex>`

## Cited by

<Filled as citations appear; `—` when none yet.>

- `[F-012]` — excluded on this capture (`test_ref: ED-NNN`)

## See also

- `core/SUBSTRATE.md` §Evidence Capture — payload schema and the one-of-content-or-path rule
- `core/VERIFICATION.md` §Layer 1 check 20 — `evidence_id_malformed`, `duplicate_evidence_id`, `evidence_capture_no_content`, `evidence_capture_content_ambiguous`, `evidence_capture_path_without_hash`
- `templates/ELIMINATION.md` — where an `ED` id most often ends up being cited
