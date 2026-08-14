# Session Handoff — {{ project_id }}

> **Projection of the most recent `session.handoff` event.** Lives at `projects/<project-id>/SESSION-HANDOFF.md`. Overwritten on each handoff — only the latest is kept on disk; older handoffs are reconstructable from the event log.
>
> Authoritative state lives in `events.jsonl` and projections. This file is a navigation aid for picking up cold. Nothing here is load-bearing; nothing here contradicts the substrate. The failure mode this template prevents: the closing agent embeds a decision in the handoff prose ("we agreed to skip Phase 3"), the resuming agent reads the prose, and the decision affects the project without ever existing as a Decision artifact. Anything load-bearing belongs in events; this file points at events.

---

## Project ID and active state

- **Project:** {{ project_id }}
- **Schema:** {{ schema_name }}
- **Last event ID:** EV-NNNN (the closing agent's last appended event)
- **Last event hash:** sha256:<full-hash>  (resuming agent uses this as the `hw verify --since=` baseline)
- **`hw verify` result at handoff:** PASS | FAIL: <brief>

## Tasks

- **Last completed task:** T-NNN (`<task title>`) at `tasks/NN-<name>-completion.md`
- **Next pending task:** T-MMM (`<task title>`) — `hw next-step` should select this
- **Tasks in-progress at handoff:** <list with task IDs and what state they're in>
- **Tasks blocked at handoff:** <list with task IDs and the blocker>

## Active artifacts

The closing agent should list the artifacts the resuming agent will most need to load:

| Artifact | Purpose | Citation |
|---|---|---|
| OR-NNN | Operating reality (current) | `[OR-NNN#hash]` |
| DEC-NNN | <name of decision> | `[DEC-NNN#hash]` |
| ... | ... | ... |

Do not list every artifact — only the ones whose absence from the resuming agent's context window would cause re-discovery. The full set is in `projects/<id>/decisions/`, `findings/`, etc.

## Open operator questions

Questions the closing agent did not resolve and that the resuming agent should address before continuing — or surface to the operator if the resuming agent is also unable:

1. <Question 1, with the relevant artifact citation if any>
2. <Question 2>

## Recommended first action for resuming agent

One concrete step. Do not write a list; pick the highest-leverage move.

> Example: "Run `hw verify --since=EV-0142` to confirm chain integrity from this handoff baseline, then read OR-003 and the T-006 structure decision before proceeding to T-007 drafting."

## Operator corrections promoted this session (v6.0.0)

**Do this before writing the handoff event.** Read every `operator.correction` event appended since the last handoff. For each one, write the information into its `should_have_lived` home so the operator never has to give that reminder again — an operating-reality field, a line in `00-REFERENCE-rules.md`, an anti-pattern, a decision. Then record the promotion here.

| Correction (one line) | Should have lived | Promoted to | Event |
|---|---|---|---|
| <the operator's words> | operating-reality | `[OR-NNN#hash]` | EV-NNNN |
| <...> | rules | `00-REFERENCE-rules.md` §<section> | EV-NNNN |

If a correction was **not** promoted, say so and why — an unpromoted correction is the next session's repeat reminder. `none` if the operator corrected nothing this session. See `core/SUBSTRATE.md` §Operator Correction.

## Friction notes

If the closing agent encountered friction worth recording, note it here briefly with the friction-log entry it became (or that should be added). The friction log itself lives at workspace root or `projects/<id>/friction-log.md` per HARNESS.md §Friction Logs; this section is just a pointer.

- <Brief note + friction log entry ID>
- <...>

---

**Closing agent timestamp:** <ISO 8601>
**Closing agent identity:** <model name + session/turn count if known>
