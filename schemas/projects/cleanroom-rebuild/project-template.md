# PROJECT.md — {{ project_name }}

> Cleanroom reverse-engineer-and-rebuild project. Bootstrapped from `schemas/projects/cleanroom-rebuild/`.

## Status

active

## Legacy system

{{ legacy_system }}

## Target stack

{{ target_stack }}

## Data strategy

{{ data_strategy }}

## The cleanroom wall

This project runs two rooms separated by an inviolable wall.

- **Observation room** (Phase B) MAY face the original. It drives the original, screenshots screens, traces the data layer, and captures hardware I/O. It produces `observation` (OBS) artifacts tagged `source=original` in the `observed/` zone. Captured imagery and traces stay here.
- **Spec room** (Phase C) reads OBS and re-expresses behavior in our own words as `spec` (SPEC) and `behavior-rule` (BR) artifacts tagged `source=cleanroom` in the `spec/` zone. This is the only family that reads `observed/` and writes `spec/`.
- **Build room** (Phase D) is WALLED. Build agents run on the local executor `{{ build_executor }}` and implement from SPEC/BR ONLY. They never read `observed/`, never run the original (no smoke run), never read its binaries or decompilation (no peek). PASS/FAIL is judged against the spec-derived oracle, never against the original.

Wall strictness: `{{ wall_strictness }}`.

The wall is a capability fact (`capability-gates.yaml`), a Tier 1 rule (`00-REFERENCE-rules.md`), a Layer 1 check (`verification.yaml`), and a dedicated council auditor (`council.yaml`). Crossing it is a Layer 1 FAIL surfaced to the operator, not a runtime judgment.

## How we observe the original

{{ observation_oracle }}

## Scope

### Included
- **Observe** the original's surface: screen list, navigation graph, DB catalog, peripherals.
- **Spec** the measured behavior: data dictionary, behavior rules, screen specs, hardware spec, test oracle.
- **Build** the target app from SPEC/BR on the walled local executor.
- **Verify** the build against the spec-derived oracle.

### Explicitly Excluded
- {{ excluded_scope }}
- Copying the original's code, binaries, or decompilation into the build (forbidden by the wall, not merely out of scope).

## Operating Reality

Anchored to `[OR-001#<short-hash>]`. legacy_system, target_stack, data_strategy, wall_strictness, build_executor, observation_oracle, and deliverable_path declared there.

## Deliverable

Built application source: `{{ deliverable_path }}`

## Phase shape

**Phase A — Setup.** Target inventory (T-000) + operating-reality and wall charter (T-001). OR-001 declared; the wall is locked into `00-REFERENCE-rules.md` Tier 1.

**Phase B — Observation (original-facing).** Screen/flow capture (T-002), data-layer behavior trace (T-003), hardware I/O capture (T-004). Produces OBS only.

**Phase C — Spec (cleanroom authoring).** Data dictionary (T-005), behavior rules (T-006), screen specs (T-007), hardware spec (T-008), test oracle (T-009). Reads OBS, writes SPEC/BR. **The wall falls at the end of this phase.**

**Phase D — Build (WALLED, local executor).** Implement-from-spec (T-010), verify-against-oracle (T-011). No original access. Reads SPEC/BR + src/ only.

## Hard scope boundaries

- Build agents cannot read `observed/`, cannot run the original, cannot read its binaries or decompilation.
- Build code and tests derive original behavior only from SPEC/BR, cited by hash. Never from OBS.
- Every SPEC/BR cites the OBS it was measured from.
- Verification compares the new app to the spec-derived oracle, never to the original.
- Operator review is required at the spec->build boundary (before the build room opens) and before archival.

## Completion Criteria

- [ ] Every captured screen has a SPEC screen-spec; every measured rule has an oracle case.
- [ ] Build implements all consumed SPEC/BR; deviations recorded as Decisions.
- [ ] The built app passes every oracle case (judged vs the oracle, not the original).
- [ ] Zero wall breaches across the project (cleanroom-integrity-auditor PASS at every fire).
- [ ] No stale citations across project artifacts.
- [ ] Operator approval at the spec->build boundary and at archival.

## Started

<YYYY-MM-DD>

## Archived

(blank until done)
