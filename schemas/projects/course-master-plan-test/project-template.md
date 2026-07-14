# PROJECT.md — {{ course_name }}

> L1 project for the course-master-plan pattern. File-canonical (Mutable Surface). Edited by operator/agent as the course evolves. Not event-sourced — curriculum and tier decisions live in DEC-001/DEC-002 events.

## Status

active

## Layer

L1 (master plan). This project owns:

- The curriculum sequence (DEC-001).
- The tier policy (DEC-002).
- The lens anchor (OR-001.lens_anchor).
- The spawned-project registry (SP-NNN spawned-project artifacts).

L1 does **not** produce lesson content (that's L2 modules) or actuate platform entities beyond Phase A.2 read-only familiarization (L2 actuation tasks own actuation).

## Objective

Produce a master plan for `{{ course_name }}` on `{{ platform }}` such that:

- Every module in the curriculum has a learning objective that reflects operator-stated learning (the lens), not lens-fitted inferences.
- Tier policy reflects the operator's current view of free-vs-paid, with append-only movement history capturing every move.
- Each module has a spawned L2 project (or is explicitly deferred).
- The schema saved at wrap (`hw schema save --as course-master-plan`) is brand-clean and reusable for the next course.

## Scope

### Included

- T-000 source inventory of `inputs/`.
- T-001 platform familiarization → `<platform>-site-guide.md`.
- T-002 curriculum corpus scan → DEC-001 + DEC-002.
- Per-module L2 spawn protocol execution (Phase B).
- Reorder/tier-move decision capture (Phase C).
- Wrap + brand-clean schema save (Phase D).

### Explicitly Excluded

- Lesson content production (L2/L3).
- Platform actuation beyond Phase A.2 read-only walk (L2 actuation tasks).
- Promo content drafting (L2 promo-* projects, or external surface if `promotion_scope: external`).
- Operating an active session of L2 or L3 work — those run in their own sessions.

## Operating Reality

Anchored to `[OR-001#<short-hash>]`. See `operating-reality/OR-001.md`.

## Lens

Anchored to `OR-001.lens_anchor`. First-listed entry dominates; secondary entries hold for cross-channel coherence. The lens guides voice and framing; module premises are discovered through the work (T-002 corpus scan + L2 module design), not pre-determined by the lens.

## Phase shape

**Phase A — Setup, intake, platform familiarization.**
- A.1 (T-000) — `inputs/` inventory + bootstrap.inventory_sweep ceremony.
- A.2 (T-001) — Platform familiarization → `<platform>-site-guide.md`.
- A.3 (T-002) — Curriculum corpus scan → DEC-001 + DEC-002.

**Phase B — L2 spawn cycle (repeating).** Per operator-initiated module/task/promo: scaffold L2, emit `child_project.scaffolded`, STOP, await operator continue, emit `child_project.resources_ready`, register in SP-NNN. L2 execution in its own session.

**Phase C — Reordering and tier-move handling.** DEC-001 / DEC-002 supersedes; v5.0 ratchet on in-flight L2; redirect_implications for affected published copy.

**Phase D — Wrap.** `hw schema save --from {{ project_id }} --as course-master-plan`. Optional second save for `<platform>-site-explorer`.

## Hard scope boundaries

- L1 cannot start an L2 task. Spawn protocol stops after `child_project.scaffolded`; operator continues.
- Curriculum sequence and tier policy changes are typed Decision supersedes, not in-prose edits.
- Operator workflow rules (lens, slug-premise-pause, order discovery, promotion scope, lens-not-premise) are reproduced verbatim in `00-REFERENCE-rules.md` Tier 2 with SCAN markers; paraphrasing them is a Tier 1 violation.

## Completion criteria

- DEC-001 has spawned L2 projects for every module (or explicit deferral / excluded-after-discovery).
- `hw verify` clean at wrap.
- Council pass at `project.archive`.
- `<platform>-site-guide.md` exists and L2 actuation tasks reference it by hash.
- Friction log reviewed; non-trivial entries have hypothesis-mapping for v5.1.2+ patches.

## Started

{{ started_date }}

## Archived

(blank until done)
