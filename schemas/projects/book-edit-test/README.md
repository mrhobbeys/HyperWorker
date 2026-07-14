# Schema: book-edit-test (working schema; v0.1)

## Status

This is a **working schema** — it is being empirically tested in the run that uses it. After project completion, `hw schema save --from book-edit-test --as book-edit` extracts the validated patterns into a permanent, brand-clean, domain-generic schema at `schemas/projects/book-edit/`. The schema files in this directory are expected to evolve during the run as friction surfaces.

## What this is for

You have a previously-published manuscript (a self-published book — e.g., via Kindle Direct Publishing or another self-publishing platform — that was put together quickly and shipped without professional editing) and you need to prepare it for re-release: polished copy, voice-preserving edit, AI-indicator pattern removal, spelling and grammar correction, surfacing and resolving unfinished bits the author left mid-draft, and final assembly into both an updated digital manuscript and a print-ready layout.

The edit is not a rewrite. The work preserves the author's voice, the real examples and case studies, the chapter structure, and the book's substantive arguments. The transformation is at the level of the prose surface: tightening, correcting, smoothing, removing patterns that have come to read as machine-generated, and resolving incomplete sentences or placeholder markers the author intended to come back to.

## When to use it

- A previously-shipped manuscript exists and is the source of truth for the re-release.
- The author wants the voice preserved — this is editorial polish, not ghostwriting.
- The original was written quickly (hackathon, challenge group, deadline pressure) and contains uneven editing, unfinished bits, or inconsistent formatting.
- The deliverables include both an updated digital manuscript AND a print-ready layout.
- A reusable Voice & Editing Guidelines document is a wanted byproduct (for future books).

## When NOT to use it

- Ghostwriting from an outline or draft fragments. The schema requires a coherent source manuscript as input.
- Translation. Voice preservation across languages is a different problem.
- Multi-author manuscripts where each author wants their voice separately preserved. This schema assumes one author voice.
- Full structural rewrite where chapters, arguments, or examples are being reshaped at the level of the book's logic. Use a different process and come back to book-edit when the structural draft is stable.

## What the schema gives you

**Per-chapter atomic editing.** Each chapter is its own working file (split out of the source manuscript at Phase A) and each edit pass is a hermetic subagent task with file_read + file_write only. No subagent sees other chapters' prose during its pass. The substrate enforces this.

**Voice-preservation enforcement.** A `voice-anchor` artifact, extracted from representative passages of the source manuscript at Phase A, is consumed by every chapter pass. A `voice-preservation-watcher` council member fires on every pass with context-asymmetric framing — it sees the proposed edit and the voice anchor, not the implementer's reasoning.

**Banned-pattern enforcement.** `banned-pattern` artifacts (e.g., em dash, AI-indicator phrases the author has explicitly rejected) are consumed by every chapter pass and verified at Layer 1. Any banned pattern surviving in a chapter rejects the pass.

**Examples-preservation rule.** The author's real-world examples, case studies, anecdotes, and direct quotes from real customers/colleagues are Tier 1 preservation rules. They are quoted verbatim, not paraphrased. A `preservation-rule-watcher` council member checks this on every chapter proposal.

**Unfinished-bits surfacing.** A Phase A scan identifies placeholder markers, incomplete sentences, internal references to unwritten sections, and other signals the author left work undone. Each becomes a `finding` artifact for operator disposition (leave / expand / cut) before the per-chapter passes begin.

**Round-aware processing.** When the corpus contains multiple rounds of the same content (Unformatted → Formatted V1 → V2 → Edited → Completed), the chain is captured via `chapter-source` artifacts with `supersedes` / `superseded_by` relationships. Round-corrected content is preserved as anti-patterns rather than dropped.

**Per-chapter operator review cadence.** Each chapter pass uses `delivery_mode: live-edit` (per the marketing-campaign live-edit shape) with paired `external_state.read_back` events capturing pre/post file hashes. Each chapter task carries `requires_handoff_acknowledge: true` so the operator's session can resume cleanly between chapters without context loss.

**Print-ready as a first-class phase.** Phase E produces a print-ready laid-out manuscript distinct from the polished content manuscript, so the substantive editing and the design layout don't tangle.

**Voice & Editing Guidelines as a deliverable.** The substrate already records every voice rule, banned pattern, preservation rule, edit-philosophy decision, and common-error correction during the run. Phase D assembles those events into a portable markdown reference document the author can use across future book projects.

## Phase shape

**Phase A — Setup.** Bootstrap inventory sweep. Chapter split from source manuscript into per-chapter working files (assembly map captured for Phase D reassembly). Voice anchor extraction. AI-indicator research subagent (web access; only task in the project that has it). Candidates evaluation (notes / unincorporated-material files). Unfinished-bits scan. Per-chapter edit-philosophy declaration.

**Phase B — Per-chapter edit passes.** One subagent per chapter, hermetic, working live-edit on its chapter's working file. Pre/post hashes captured. 30% line-delta cap by default. Council fires per pass. Operator promotes between chapters; that is the cadence.

**Phase C — Cross-chapter continuity.** Character/term/reference/example consistency. Each contradiction → Decision before Phase D.

**Phase D — Assembly + Voice Guidelines.** Reassemble per-chapter files into the polished manuscript per the Phase A assembly map. Generate Voice & Editing Guidelines from the run's events log. Final read-through.

**Phase E — Print-ready.** Trim size, margins, page numbers, front matter, back matter, chapter heading styling, widow/orphan control, image resolution.

## What this schema is NOT

A ghostwriter. The voice is the author's; the schema preserves it.

A typesetter for arbitrary print formats. Phase E produces a docx laid out for a standard POD print pipeline (e.g., KDP Print, IngramSpark, or another print-on-demand service) — exotic typography, multi-language layout, or specialty binding work falls outside the schema's default Phase E.

A multi-author tool. One author voice per project.

## Bootstrap

```
hw bootstrap --schema book-edit-test --name <project-id>
```

The schema asks for book metadata, source manuscript path, candidate-content folder (if any), voice-anchor strategy, edit-philosophy default, line-delta cap, AI-indicator research opt-in, and deliverable paths. After bootstrap, the inventory sweep probes the corpus folder; operator reconciles; §Scope is locked from the reconciliation.

## Inheritance

This schema inherits from `report-synthesis` (per-source atomic extraction, source-fidelity Tier 1, contradiction → Decision protocol, bootstrap probe pattern) and pulls live-edit primitives from `marketing-campaign` (delivery_mode: live-edit, external_state.read_back, scope-shrink-watcher council role, edit/create/delete enumeration). The novel additions are the `chapter-source`, `edit_proposal`, `voice-anchor`, and `banned-pattern` artifact kinds; the `voice-preservation-watcher`, `preservation-rule-watcher`, and `edit-philosophy-aligner` council roles; and the per-chapter `max_line_delta_pct` Layer 2 check.
