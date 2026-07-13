# 00-REFERENCE-rules.md — {{ project_name }}

Cross-cutting rules with explicit precedence. Lower tier ordinal wins on conflict. Renaming a tier does not change ordinal precedence. Tier 1 cannot be overridden.

---

## Tier 1: CLEANROOM-WALL (NON-NEGOTIABLE — absolute, never override)

The two-room separation is absolute. The build room implements from SPEC/BR ONLY and has no path to the original. Crossing the wall is a Layer 1 FAIL surfaced to the operator, not a runtime judgment.

- **No build reads observed/.** No build-room task (`build-from-spec`, `verify-against-oracle`) may cite an OBS artifact or reference any path under `observed/`. SPEC/BR (`source=cleanroom`, `consumable_by_build:true`) are the ONLY original-derived inputs the build room may read.
- **Build executor is the walled local model.** Build-room tasks run with `executor=local_model` on the declared `build_executor` ({{ build_executor }}), which has no `app_driver` / network-to-original capability. A build task run on the orchestrator (which CAN reach the original) is a wall breach.
- **No smoke run.** No build-room task runs the ORIGINAL to check behavior. PASS/FAIL is judged against the spec-derived ORACLE, never against the original.
- **No peek.** No build-room task reads the original's binaries, decompilation, or source.
- **Zone-write discipline.** A task writing outside its declared `write_zones` is a breach (build -> `observed/`, observation -> `src/`).
- **OBS never crosses.** Observation artifacts (`source=original`) never enter build context. Only re-expressed SPEC/BR cross the wall.

@@SCAN_1_1: Is this a build-room task? If yes, confirm it cites only SPEC/BR (no OBS, no path under observed/).

@@SCAN_1_2: Is this a build-room task? If yes, confirm executor=local_model on the declared build_executor, not the orchestrator.

@@SCAN_1_3: Did this task run the original system, or read its binaries / decompilation, in any step (yes / no)?

---

## Tier 2: SPEC-FIDELITY (overrides quality and style)

Every SPEC/BR re-expresses MEASURED behavior in our own words and cites the OBS it derives from by hash. Specs make no claim the observations do not support and contain no verbatim original expression beyond functional necessity (data-field names, protocol byte values, justified in `verbatim_carryover`). Behavior rules carry an algorithm + worked input->output examples + oracle cases, all measured black-box.

@@SCAN_2_1: Does every SPEC/BR you wrote cite at least one OBS by hash in derived_from?

@@SCAN_2_2: Does any SPEC body quote original code or UI strings verbatim beyond functional necessity (and is it justified in verbatim_carryover)?

---

## Tier 3: REBUILD-QUALITY (overrides style)

Target-stack correctness and the spec-derived oracle hold. Every captured screen has a screen spec; every measured rule has an oracle case; the built app passes the oracle. OR-001.data_strategy is honored. Deviations from SPEC/BR during build become Decisions (`deviates_from_spec` set), never silent edits.

@@SCAN_3_1: Has every captured screen / measured rule been turned into a SPEC/BR with an oracle case, or explicitly noted as deferred?

@@SCAN_3_2: Did any build step deviate from a SPEC/BR without recording a Decision?

---

## Tier 4: STYLE (lowest precedence)

Target-stack code style, naming, presentation. Citation format throughout: [OBS-NNN#hash] for observations, [SPEC-NNN#hash] for specs, [BR-NNN#hash] for behavior rules, [DEC-NNN#hash] for decisions, [F-NNN#hash] for findings. Comments explain why, not what; spec documents state behavior, not implementation.

---

## Banned tokens (project-specific, optional)

If original product names, trademarks, or copyrighted UI strings must be kept out of the rebuilt app's user-facing surface, list them here. Most rebuilds leave this empty unless legal scope requires it.

| Banned Token | Safe Replacement | Tier | Why |
|---|---|---|---|
| | | | |

---

## Canonical facts — do not normalize (project-specific, optional)

If protocol byte values, data-field names, or interop literals must appear verbatim in the spec/build for the rebuilt app to interoperate, list them here so they are not "cleaned up."

| Fact | Canonical Form | Do NOT Normalize To |
|---|---|---|
| | | |
