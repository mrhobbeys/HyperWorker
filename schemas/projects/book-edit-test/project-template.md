# PROJECT.md — {{ project_name }}

## Book

- **Title:** {{ book_title }}
- **Short title:** {{ book_short_title }}
- **Platform ID (e.g., ISBN, ASIN):** {{ book_platform_id }}
- **Listing URL:** {{ book_listing_url }}
- **Target re-release:** {{ target_release }}

## Goal

Polish {{ book_short_title }} for re-release: voice-preserving copy edit, AI-indicator pattern removal, spelling and grammar correction, surfacing and resolving unfinished bits the author left mid-draft, and final assembly into both an updated digital manuscript and a print-ready layout. The author's voice is preserved; real examples are quoted verbatim; banned patterns (e.g., em dash) are enforced at Layer 1.

## Source corpus

- **Canonical manuscript (source-of-truth):** `{{ source_manuscript_path }}` — read-only; live edits happen against the per-chapter splits, not this file. This is the input to Phase A T-001 chapter-split.
- **Per-chapter working folder:** `{{ input_folder }}` — populated by T-001. Phase B chapter passes live-edit the per-chapter files in this folder.
- **Archive folders (reference, hash-pinned, not edited):** {{ archive_folders }}
- **Candidate-content folder (under evaluation):** `{{ candidates_folder }}`

## Voice anchor

- **Strategy:** {{ voice_anchor_strategy }}
- **Operator-supplied excerpts:** captured at T-002 voice-anchor-extraction or as part of bootstrap operator-overrides.

The voice anchor is consumed by every Phase B chapter pass and by every council fire that includes voice-preservation-watcher.

## Edit philosophy

- **Default per chapter:** {{ edit_philosophy_default }}
- **Per-chapter overrides:** captured as Decisions with synthesis_role: chapter-edit-philosophy and chapter_scope set.

## Banned patterns

- **Bootstrap seed (operator-direct):** {{ banned_patterns_seed }}
- **AI-indicator research:** {{ ai_indicator_research }} (run | skip). When run, T-003 surfaces a candidate list; operator approves; approved items become banned-pattern artifacts.

## Preservation rules

- **Examples preservation:** {{ examples_preservation }} (yes | no). When yes, real examples, case studies, anecdotes, and direct quotes are quoted verbatim — never paraphrased, restructured, or composited.
- **Operator-declared others:** captured as Decisions with synthesis_role: preservation-rule.

## Per-pass guardrails

- **max_line_delta_pct:** {{ max_line_delta_pct }} (default 30; per-chapter override allowed via DEC with synthesis_role: chapter-edit-philosophy).

## Phase shape

**Phase A — Setup.** Inventory sweep. Chapter split. Voice anchor extraction. AI-indicator research. Candidates evaluation. Unfinished-bits scan. Per-chapter edit-philosophy declaration.

**Phase B — Per-chapter edit passes.** One subagent per chapter, hermetic, live-edit on the chapter's working file. Pre/post hashes captured. Council fires per pass. Operator promotes between chapters; that is the cadence.

**Phase C — Cross-chapter continuity.** Character/term/reference/example consistency. Each contradiction → Decision before Phase D.

**Phase D — Assembly + Voice Guidelines.** Reassemble per-chapter files into the polished manuscript per the Phase A assembly map. Generate Voice & Editing Guidelines from the run's events log. Final read-through.

**Phase E — Print-ready.** Trim size, margins, page numbers, front matter, back matter, chapter heading styling, widow/orphan control, image resolution.

## Hard scope boundaries

- The polished manuscript cannot contain content the source manuscript and operator-approved candidate-content folds-in did not provide.
- The polished manuscript cannot violate any preservation-rule Decision (Tier 1).
- The polished manuscript cannot contain any banned-pattern instance (Tier 1).
- Operator review is required before any chapter pass actuates (per-chapter cadence).
- Operator review is required before assembly, final-read, and print-ready phases land their deliverables.

## Scope

(Populated from `bootstrap.scope_locked` event payload after the inventory sweep reconciliation.)

## Deliverables

1. `{{ deliverable_path }}` — polished re-release manuscript (Phase D).
2. `{{ voice_guidelines_path }}` — Voice & Editing Guidelines (Phase D, byproduct).
3. `{{ print_ready_path }}` — print-ready laid-out manuscript (Phase E, if print_ready_required).
4. Backlog (post-archive): {{ post_archive_backlog }}

## Completion criteria

- Every registered chapter has a terminal-state edit_proposal: applied | deferred | excluded-after-discovery.
- Every banned-pattern artifact has zero surviving instances in the assembled manuscript (Layer 1).
- Every preservation rule has zero violations in the assembled manuscript (Tier 1 council pass).
- All cross-chapter continuity contradictions are resolved or deferred with operator approval.
- Council pass at final-read (critical risk).
- Operator approval at assembly, voice-guidelines-doc, final-read, and print-ready.
