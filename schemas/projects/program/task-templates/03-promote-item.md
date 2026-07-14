---
id: T-003
kind: task
schema: program
phase: B
risk_level: critical
required_tools: [file_read, file_write, hash_compute]
delivery_mode: constrained
depends_on: [T-001]
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "The promoted item was identified by reading the source workstream's own projections (SESSION-HANDOFF.md / its own artifact projections) READ-ONLY, never by writing into that instance."
  - "The item explicitly meets OR-001.promote_criteria — the promote Decision states which criterion, not a bare 'this seems hot.'"
  - "The promote proposal followed the identical spawn-pause protocol as T-002 (workstream.spawn_proposed with trigger: promote, promoted_from set; workstream.spawn_decided with operator_confirmed: true) before any registration."
  - "The promote Decision carries source_item_citation (relative path + short hash of the source item at the moment of promotion)."
  - "The new dedicated workstream is registered with promoted_from citing the source workstream. The source workstream itself is NOT edited by this task — that update happens in the source instance's own session."
  - "Operator review completed before the promote Decision is recorded (critical risk — see verification.yaml)."
---

# Task T-003: Promote Item (repeatable)

## Objective

When an item inside an existing workstream meets `OR-001.promote_criteria`,
graduate it to its own dedicated workstream — a new instance, not a nested child
(`core/LOCK.md` §Programs point 3, "promote-and-swap, not nesting"). Reuses the
T-002 spawn-and-pause protocol with `trigger: promote`. Run each promotion as a
branch of this task (`hw branch T-003 <slug>`), same convention as T-002.

## Step-by-Step Instructions

1. Read `OR-001.promote_criteria`.
2. Read the candidate source workstream's own projections **read-only**:
   `SESSION-HANDOFF.md`, and, if this program's operator has direct filesystem
   access to the sibling instance, its relevant artifact projection (e.g. a
   Finding describing the hot item). Never open the source instance's
   `events.jsonl` as a writer (`00-REFERENCE-rules.md` Tier 1).
3. Confirm the item meets `promote_criteria` concretely — cite the specific
   language of the criterion and the specific evidence in the source projection,
   not a vibe.
4. Compute the SHA-256 of the source projection file at the moment of reading;
   record `{path, sha256}` as the candidate `source_item_citation`.
5. Draft the promote proposal: `slug`, one-paragraph `premise` (why this item
   warrants its own instance), `schema_choice` (typically a single-item-focused
   schema — e.g. `single-opportunity` — but follow the operator's actual choice).
6. Emit `workstream.spawn_proposed` with
   `{proposal_id, trigger: promote, slug, premise, schema_choice, promoted_from: <source WS-NNN>, proposed_by}`.
7. **STOP.** Surface to operator with the `source_item_citation` attached: "Promote
   candidate from `<source workstream>`: `<item summary>`, citing
   `<path>@sha256:<hash>`. Meets promote criteria: `<which one, how>`. Approve,
   decline, or refine?"
8. Operator responds. Emit `workstream.spawn_decided` as in T-002.
9. If approved: record a Decision (`synthesis_role: promote-decision`,
   `cites_workstream: [<source WS-NNN#hash>]`, `source_item_citation` populated).
10. Wait for operator confirmation the new instance exists, then register the new
    workstream (`origin: spawned`, `promoted_from: <source WS-NNN#hash>`,
    `spawn_decision: <this DEC-NNN#hash>`).
11. **Do not edit the source workstream's item.** Tell the operator: "Promoted.
    The source workstream's own session should mark this item `promoted` and cite
    `[DEC-NNN#hash]` back — that update happens there, not here (Single-Writer
    Rule)." The source workstream keeps running; promotion does not retire it.
12. Answer @@SCAN markers.

## Completion Report (filled by executor, per invocation)

- **Acceptance criteria:** <X/Y pass>
- **Source workstream:** [WS-NNN#…]
- **Source item citation:** `<path>@sha256:<hash>`
- **Promote criterion met:** <which, with evidence>
- **Decision:** approved / declined
- **Outputs produced:** workstream.spawn_proposed EV-NNNN;
  workstream.spawn_decided EV-NNNN; DEC-NNN (promote-decision); new WS-NNN (once
  instance confirmed, if approved)
- **Reciprocal citation status:** pending (source instance's own session has not
  yet marked the item promoted) / confirmed
- **Discoveries:** <e.g., "promote_criteria as written was ambiguous about deadline proximity — flagged for OR-001 supersede">
- **Recommended follow-up:** "Confirm reciprocal citation lands in the source workstream at its next session."
