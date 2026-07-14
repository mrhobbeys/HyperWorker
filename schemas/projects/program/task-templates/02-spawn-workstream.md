---
id: T-002
kind: task
schema: program
phase: B
risk_level: elevated
required_tools: [file_read, file_write, hash_compute]
delivery_mode: constrained
depends_on: [T-001]
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "A workstream.spawn_proposed event exists with slug + one-paragraph premise + schema_choice before any operator decision."
  - "The agent STOPPED after emitting workstream.spawn_proposed and surfaced the proposal to the operator — no workstream.add for this proposal_id appears before a paired workstream.spawn_decided."
  - "workstream.spawn_decided exists for the same proposal_id with operator_confirmed: true. If decision: declined, no workstream is registered for this proposal_id."
  - "If approved: a spawn Decision (synthesis_role: spawn-decision) is recorded, citing the proposal, before the workstream is registered."
  - "The workstream is registered (origin: spawned) only after the operator separately confirms the new instance actually exists at a given instance_path — this task never runs hw bootstrap itself."
---

# Task T-002: Spawn Workstream (repeatable)

## Objective

Propose a new workstream, pause for explicit operator approval, record the spawn as
a Decision, and register it once the operator confirms the new instance exists. This
task's procedure repeats every time the operator initiates a spawn — run each
invocation as a branch of this task (`hw branch T-002 <slug>`, folded back with the
resulting `WS-NNN`), rather than editing this task file per spawn.

**The actual `hw bootstrap` of the new instance happens in the new instance, not
here** (`core/LOCK.md` §Programs point 2). This task never scaffolds files outside
this program instance.

## Step-by-Step Instructions

1. Draft the proposal: `slug` (short handle), one-paragraph `premise` (what this
   workstream covers and why it needs its own instance), `schema_choice` (which
   schema it will bootstrap from).
2. Emit `workstream.spawn_proposed` with `{proposal_id, trigger: spawn, slug, premise, schema_choice, promoted_from: null, proposed_by}`.
3. **STOP.** Surface the proposal to the operator: "Proposed workstream `<slug>` —
   `<premise>` — schema `<schema_choice>`. Approve, decline, or refine?" The agent
   CANNOT advance past this point without an explicit operator response. There is
   no "skip the pause" path in this schema (`00-REFERENCE-rules.md` Tier 2).
4. Operator responds. Emit `workstream.spawn_decided` with
   `{proposal_id, decision: approved|declined, decision_artifact: null, operator_confirmed: true}`.
5. If `decision: declined`: record the reason in the completion report; do NOT
   register a workstream for this proposal_id. Done.
6. If `decision: approved`: record a Decision (`synthesis_role: spawn-decision`,
   `cites_workstream: []` — none exist yet — body cites the proposal verbatim).
   Update `workstream.spawn_decided.decision_artifact` to the new `[DEC-NNN#hash]`.
7. Tell the operator: "Approved. Bootstrap the new instance at
   `<instance_path>` with `hw bootstrap --schema <schema_choice> --name <slug>`
   when ready, then confirm back here." Wait.
8. Once the operator confirms the new instance exists (names its actual
   `instance_path` and `child_project_id`), register the workstream: `hw add
   workstream` with `origin: spawned`, `lifecycle` (as the sibling instance
   declares), `status: active`, `premise`, `spawn_decision: [DEC-NNN#hash]`,
   `last_rollup_citation: null`.
9. Answer @@SCAN markers.

## Completion Report (filled by executor, per invocation)

- **Acceptance criteria:** <X/Y pass>
- **Proposal:** `<slug>` — `<premise>` — `<schema_choice>`
- **Decision:** approved / declined
- **Outputs produced:** workstream.spawn_proposed EV-NNNN;
  workstream.spawn_decided EV-NNNN; DEC-NNN (if approved); WS-NNN (once
  instance confirmed, if approved)
- **Operator pause duration:** <if notable>
- **Discoveries:** <e.g., "operator wanted to refine the premise mid-proposal — recorded as a second workstream.spawn_proposed with a new proposal_id rather than editing the first">
- **Recommended follow-up:** "none" / "Operator has not yet confirmed the new instance exists — WS-NNN registration is pending."
