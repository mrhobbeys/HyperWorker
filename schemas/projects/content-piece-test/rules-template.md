# 00-REFERENCE-rules.md — {{ piece_slug }}

Cross-cutting rules with explicit precedence. Lower tier ordinal wins on conflict.

---

## Tier 1: SOURCE-AND-VOICE-FIDELITY (NON-NEGOTIABLE)

The operator's voice (OR-001.voice_anchor) is non-negotiable. Verbatim_keeper artifacts are not silently rewritten. Source material is cited honestly; the v5.0.1 verbatim-quotation principle applies — quote operator and source verbatim where possible; paraphrase only when the original is too long, with explicit `[paraphrase: ...]` markers preserving qualifiers.

@@SCAN_1_1: Does every quote of the operator in your output appear verbatim or carry a `[paraphrase: ...]` marker?

@@SCAN_1_2: Are all approved verbatim_keeper VK-NNN appearing byte-for-byte in at least one applicable variant?

@@SCAN_1_3: Did you invent any anecdote, quote, or claim the operator did not provide?

---

## Tier 2: OPERATOR-RULES (verbatim, with structural counterparts)

The operator's ground rules, captured verbatim from the bootstrap directive. Each rule has a structural counterpart enforced by the harness — the verbal rule is not load-bearing, the structural counterpart is.

> **R-1.** Never ask me more than two questions at a time.
> **Structural:** `capability-gates.yaml` `interview_question_budget.max_per_turn: 2`. Layer 1 fails T-002 turns with ≥3 questions.

> **R-2.** Don't summarize my input back to me in a way that just restates it — add interpretation.
> **Structural:** `interpretation-watcher` council member; Layer 2 `interpretation_density` check on findings and outputs.

> **R-3.** If my rough draft has a line that's especially strong and sounds like me, keep it verbatim and flag it so I know you kept it.
> **Structural:** `verbatim_keeper` artifact kind (VK-NNN). T-003 emits one VK per kept line; T-004 Layer 1 hash-citation freshness blocks any silent rewrite.

> **R-4.** Always tell me which format you're working on before you output it.
> **Structural:** T-004 task protocol — agent emits a "## Format: <id>" announcement before each variant's content. Layer 2 `format_native_structure` check confirms presence.

> **R-5.** If something I gave you is too thin to write from honestly, tell me instead of padding it.
> **Structural:** `thinness-watcher` council member; OR-001.thinness_protocol = refuse-rather-than-pad. Anti_pattern artifact + STOP rather than pad.

@@SCAN_2_1: Did your most recent interview turn contain ≤2 questions?

@@SCAN_2_2: Did the most recent finding you wrote add interpretation, not just restate input?

@@SCAN_2_3: Did you announce which format you were producing before outputting it?

@@SCAN_2_4: If material was thin, did you refuse-and-stop rather than pad?

---

## Tier 3: QUALITY-AND-FORMAT-NATIVE

Each variant matches its declared format structure. The three variants differentiate format-natively on `ab_variant_axis: publication_format`.

@@SCAN_3_1: Does each variant match its OR-001.formats[id].structure?

@@SCAN_3_2: Pairwise: do the three variants differ format-natively, not just paraphrase each other?

---

## Tier 4: STYLE

Citation format: `[SRC-NNN#hash]` for sources, `[CLM-NNN#hash]` (not used in this schema) for claims, `[F-NNN#hash]` for findings, `[DEC-NNN#hash]` for decisions, `[VK-NNN#hash]` for verbatim_keepers, `[OR-001#hash]` for operating-reality.

Voice details: see OR-001.voice_anchor (verbatim).

---

## Banned tokens (project-specific, optional)

(empty — operator did not declare banned tokens at bootstrap)

| Banned Token | Replacement | Reason |
|---|---|---|
| (empty) | | |

---

## Canonical facts — do not normalize (project-specific, optional)

(empty — operator did not declare canonical facts at bootstrap)

| Fact | Form | Reason |
|---|---|---|
| (empty) | | |
