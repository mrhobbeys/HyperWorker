# PROJECT.md — {{ piece_slug }}

## Piece topic

{{ piece_topic }}

## Voice anchor

The operator's voice description (OR-001.voice_anchor) governs all output. First-listed entry dominates on conflict.

See `operating-reality/OR-001.md` for the verbatim text.

## Default lens (when no central angle is supplied)

{{ default_lens }}

## Central angle

{{ central_angle_status }}
{{ central_angle_text }}

## Inputs

Per-piece source corpus lives at `{{ input_folder }}` (default: `projects/<piece-slug>/inputs/`). Per operator directive DEC-001, the folder is created empty at scaffold-time and populated post-kickoff. T-000 source-inventory runs after operator confirms population.

## Deliverables

Publication-format-native variants — one per entry in `target_formats` (OR-001.formats) — written to `{{ deliverable_path }}` (default: workspace-parent `outputs/<piece-slug>/`). Default example (three formats):

- `substack-longform.md` — hook → free section → paywall cliff (marked) → insight section → closing
- `x-longform.md` — thread / article with chunks each able to terminate the piece
- `youtube-leadins.md` — three sub-options × 3-5 sentences, one per framing (controversy / curiosity / utility)

(If the operator declared different target_formats at bootstrap, the actual ids/structures/filenames replace these.)

## Phase shape

**Phase A — Setup.** T-000 source-inventory + T-001 corpus-scan-with-lens. OR-001 declared, central angle confirmed or refined.
**Phase B — Interview.** T-002 interactive turn-by-turn interview. Findings emit per operator response. Question budget ≤2 per turn.
**Phase C — Draft capture.** T-003. Operator pastes rough draft; agent flags verbatim_keepers; operator approves keeper list.
**Phase D — Format generation.** T-004 ab-variant single-task three-variant pass. Subagent runs hermetic.
**Phase E — Council & wrap.** All five council members fire on T-004 completion. On all-PASS, operator approves; `hw wrap` archives the project; `hw schema save --from <piece-slug> --as content-piece` extracts the validated schema.

## Hard scope boundaries

- Output cannot include claims, anecdotes, or quotes the operator did not supply (interview, rough draft, or registered source).
- Verbatim_keepers (operator-approved) appear byte-for-byte in at least one applicable variant.
- The three variants must differ format-natively, not paraphrase each other.
- Thin material → refuse and stop. No padding.

## Completion criteria

- All three variants generated and saved to `{{ deliverable_path }}`.
- All five council members PASS at T-004 completion.
- Operator approves all three variants.
- Scope.complete event recorded with terminal_state for every Phase A–E item.

## Scope

(Populated by `bootstrap.scope_locked` event after the inventory probe runs. v5.1.1 scope-completeness Layer 1 check fires at session.handoff against this list.)

## Explicitly excluded

(none declared at bootstrap)
