# Schema: cleanroom-rebuild

## What this is for

You have a legacy application — abandonware, an unmaintainable stack, a vendor that disappeared — and you need to reproduce it on a modern stack WITHOUT copying its code. You own the data and the right to run the original, but you cannot (legally, or for cleanliness) lift its source, binaries, or decompilation into the rebuild.

This schema runs a **cleanroom**: a strict two-room wall separates OBSERVATION (drive the original, measure its behavior black-box) from BUILD (implement from specification only). Behavior is MEASURED — input->output experiments, SQL traces, DB before/after diffs, hardware I/O captures — re-expressed as our own specification, and verified against a spec-derived oracle. The build room never touches the original.

## The wall (the load-bearing idea)

Three rooms, one inviolable wall between spec and build:

- **Observation room** may face the original. Produces `observation` (OBS) artifacts: `source=original`, zone `observed/`, **NOT consumable by build**.
- **Spec room** reads OBS and writes `spec` (SPEC) and `behavior-rule` (BR): `source=cleanroom`, zone `spec/`, **build-consumable**. The only family that reads `observed/` and writes `spec/`.
- **Build room** runs on an isolated local model (e.g., LM Studio or another walled local endpoint) and implements from SPEC/BR ONLY. It cannot read `observed/`, cannot run the original (no smoke run), cannot read its binaries or decompilation (no peek).

The wall is enforced four ways, not by good intentions:

- **Capability** (`capability-gates.yaml`): build task-kinds declare `executor: local_model`, `forbidden_reads: [observed]`, `no_smoke_run`, `no_peek`. Delegation is refused if a subagent's tools intersect the forbidden set.
- **Precedence** (`precedence-tiers.yaml`): the wall is Tier 1, with SCAN markers that force re-anchoring before any state-changing build action.
- **Verification** (`verification.yaml`): the five `wall_enforcement` checks (`build-no-observed-read`, `build-executor-isolation`, `no-smoke-no-peek`, `spec-purity`, `zone-write-discipline`) run at Layer 1 on every event. A breach is a FAIL surfaced to the operator.
- **Council** (`council.yaml`): a dedicated `cleanroom-integrity-auditor` audits for breach at every fire and unconditionally at the spec->build boundary.

## When to use it

- You can run/drive the original and own its data, but must not copy its code.
- Behavior is knowable by measurement (screens, traces, I/O) rather than only by reading source.
- The rebuild must be defensibly cleanroom (legal, licensing, or hygiene reasons).
- You want a spec-derived oracle as the verification truth, independent of the original.

## When NOT to use it

- You have the original source and a license to use it → just port it; a cleanroom is overhead you do not need.
- The original cannot be run or observed at all → there is nothing to measure; this schema has no inputs.
- The "rebuild" is a greenfield feature with no legacy behavior to reproduce → use `software-feature-ship`.

## What the schema gives you

**Structural wall enforcement.** The build executor is a local model with no capability path to the original. Layer 1 rejects any build event citing an OBS artifact or an `observed/` path. The wall is a capability fact, not a promise.

**Measured, not read, behavior.** Behavior rules carry an algorithm plus worked input->output examples plus oracle cases, all derived from black-box experiments. Reading code to author a rule is a wall breach in `pure-black-box` strictness.

**Provenance you can audit.** Every SPEC/BR cites the OBS it was measured from by hash. Spec purity is checked: verbatim original strings are only allowed where functionally necessary and justified.

**A spec-derived oracle.** Verification compares the new app to the recorded oracle (input->expected output), never to the original. The original is never in the build/verify loop.

**A dedicated integrity auditor.** The `cleanroom-integrity-auditor` council member exists solely to find wall breaches, and fires critically at the spec->build boundary — the one moment the wall is crossed for real.

## Phase shape

**Phase A — Setup.** Target inventory (T-000) + operating-reality and wall charter (T-001). OR-001 declared; the wall locked into Tier 1.

**Phase B — Observation (original-facing).** Screen/flow capture (T-002), data-layer behavior trace (T-003), hardware I/O capture (T-004). Produces OBS only.

**Phase C — Spec (cleanroom authoring).** Data dictionary (T-005), behavior rules (T-006), screen specs (T-007), hardware spec (T-008), test oracle (T-009). Reads OBS, writes SPEC/BR. The wall falls at the end of this phase.

**Phase D — Build (WALLED, local executor).** Implement-from-spec (T-010), verify-against-oracle (T-011). No original access. SPEC/BR + src/ only.

## What this schema is NOT

A decompiler or a code-porting tool. It does not lift the original's code; it measures behavior and re-expresses it. In `decompilation-assisted` strictness the observation room may read decompiled code, but the build room is walled regardless.

A guarantee of legal cleanliness on its own. The schema makes the wall structural and auditable; whether that satisfies a specific licensing or legal requirement is the operator's call with counsel.

## Bootstrap

```
hw bootstrap --schema cleanroom-rebuild --name <rebuild-id>
```

The schema asks for the legacy system, target stack, data strategy, wall strictness, the walled build executor, how the original is observed, and the deliverable path. After bootstrap, the project.activate council confirms the wall is structurally declared before observation begins.
