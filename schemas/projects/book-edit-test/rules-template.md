# 00-REFERENCE-rules.md — {{ project_name }}

Cross-cutting rules with explicit precedence. Lower tier ordinal wins on conflict.

---

## Tier 1: PRESERVATION-FIDELITY (NON-NEGOTIABLE)

The author's voice is preserved. Real-world examples, case studies, anecdotes, and direct quotes are quoted verbatim — not paraphrased, restructured, or composited. Banned patterns (operator-declared, e.g., em dash; AI-indicator phrases the author has rejected) do not survive any chapter pass. Source content the author considers canonical (specific framework names, dates, URLs, brand names, product names) appears verbatim wherever it appears.

**Verbatim quotation principle.** When an artifact summarizes operator intent or describes a preservation rule, quote verbatim where possible. Paraphrase only when the original is too long to embed (more than 3 sentences); flag the paraphrase explicitly with `[paraphrase: ...]` markers and ensure the paraphrase preserves the original's qualifiers.

@@SCAN_1_1: Did your pass preserve the voice anchor (every excerpt the chapter cited remained verbatim)?

@@SCAN_1_2: Did any banned pattern survive your pass? (em dash, AI-indicator phrases on the approved list, operator-declared others)

@@SCAN_1_3: Did your pass paraphrase, restructure, or composite any real example, case study, or direct quote?

---

## Tier 2: OPERATOR-ALIGNMENT (SCOPE)

Each chapter pass adheres to its declared edit philosophy (light-copyedit | substantive-edit | structural-rewrite). Per-pass changes stay under the configured max_line_delta_pct (default 30%). Excluded topics from OR-001 do not get introduced. Operator-declared preservation rules are honored verbatim.

@@SCAN_2_1: Did your pass introduce any content beyond what the chapter's edit philosophy authorizes?

@@SCAN_2_2: Did your pass exceed max_line_delta_pct?

---

## Tier 3: EDIT-QUALITY (TECHNICAL)

Spelling correction is the floor — every pass corrects every spelling error it identifies. Grammar correction follows the chapter's edit philosophy. Internal consistency: each chapter's references to other chapters resolve correctly; characters, terms, framework names, and examples used in multiple chapters appear consistently. Unfinished bits decided to leave are noted; cut are gone; expand are filled.

@@SCAN_3_1: Did your pass leave any spelling errors uncorrected?

@@SCAN_3_2: Did your pass create or worsen any internal-reference inconsistency?

---

## Tier 4: STYLE

Voice consistency, formatting, sentence-rhythm signature, vocabulary register. Tier 4 is overridden by Tier 1 if any conflict surfaces. Citation format throughout: `[SRC-NNN#hash]` for sources, `[DEC-NNN#hash]` for decisions, `[F-NNN#hash]` for findings, `[VA-NNN#hash]` for voice-anchor, `[BP-NNN#hash]` for banned-pattern, `[EP-NNN#hash]` for edit_proposals, `[AM-NNN#hash]` for assembly-map, `[CTR-NNN#hash]` for contradictions, `[AP-NNN#hash]` for anti-patterns.

(Operator-declared style overrides go below — populated at T-002 voice-anchor-extraction completion.)

---

## Banned patterns (project-specific)

Banned-pattern artifacts authored at bootstrap and added during Phase A T-003. Each chapter pass `consumes:` the full list.

| BP-ID | Pattern | Class | Replacement Rule | Source |
|---|---|---|---|---|
| | | | | |

(Populated as banned-pattern artifacts are added.)

---

## Preservation rules (project-specific)

Decisions with `synthesis_role: preservation-rule`. Each chapter pass `consumes:` every active preservation rule.

| DEC-ID | Rule | Why |
|---|---|---|
| | | |

(Populated as preservation-rule Decisions are added.)

---

## Canonical facts — do not normalize

Brand names, product names, framework names, dates, URLs, platform IDs (ISBN, ASIN, etc.), and other specific tokens that must appear verbatim wherever they appear.

| Fact | Form | Reason |
|---|---|---|
| | | |
