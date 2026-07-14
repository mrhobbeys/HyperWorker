---
id: T-011
kind: task
schema: book-edit-test
phase: D
risk_level: standard
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-010]
consumes:
  - "[OR-001#<short-hash>]"
  - "[VA-001#<short-hash>] (voice anchor)"
  - "ALL [BP-NNN#hash] (banned patterns: bootstrap seed + AI-indicator-research approvals)"
  - "ALL Decisions with synthesis_role: preservation-rule"
  - "ALL Decisions with synthesis_role: chapter-edit-philosophy"
  - "ALL Decisions with synthesis_role: ai-indicator-policy"
  - "ALL [F-NNN#hash] with finding_kind: spelling-pattern | grammar-pattern (from chapter passes)"
  - "Discoveries fields from completed-task completion reports (read via tasks/<id>-completion.md projections)"
acceptance_criteria:
  - "Voice & Editing Guidelines.md is written to OR-001.voice_guidelines_path."
  - "The document includes: (1) voice profile (from VA-001), (2) banned patterns (full BP list with replacement rules), (3) preservation rules (from preservation-rule Decisions), (4) edit philosophies and when to apply each (from chapter-edit-philosophy Decisions, generalized), (5) common spelling/grammar patterns specific to this author (from spelling-pattern / grammar-pattern findings), (6) AI-indicator policy (from ai-indicator-policy DEC), (7) practical edit-process notes (from completion-report discoveries)."
  - "The document is portable: brand-clean, domain-generic enough that the author can apply it to other book projects without customizing structure."
  - "Citations within the doc point at the project's run for traceability (e.g., 'derived from VA-001 created at T-002 of project book-edit-test'); a reader of the doc can re-derive each rule from the run if curious."
---

# Task T-011: Voice & Editing Guidelines Document

## Objective

Assemble a portable Voice & Editing Guidelines document from the run's events log. The doc is the operator's distilled editing playbook for this book and for future books — it captures voice profile, banned patterns, preservation rules, edit-philosophy choices, common spelling/grammar patterns, AI-indicator policy, and practical edit-process notes that emerged during the run.

This task is structurally a projection: every input is a typed artifact or a projection in the substrate, and the doc is assembled from them. The agent's job is the synthesis (organizing the inputs into a readable document the author will actually use), not the substance (which is captured in the source artifacts).

## Step-by-Step Instructions

1. Read all consumed artifacts.
2. **Read every chapter-edit-pass branch's completion report** (`projects/book-edit-test/tasks/T-007.ch-NN-completion.md` for each chapter). Extract:
   - Discoveries that surfaced common spelling/grammar patterns specific to the author.
   - Discoveries that surfaced voice-of-author signature observations not in VA-001 originally.
   - Council failure → revision patterns that led to learnings about the author's voice.
3. **Build the document with these sections:**

   **§1 — Voice Profile** (from VA-001)
   - Tone descriptors (verbatim from VA-001).
   - Sentence rhythm signature.
   - Vocabulary register.
   - Voice don't-list.
   - Operator overrides (em dash → parentheses/ellipsis, etc.).
   - 3-5 representative excerpts (verbatim from VA-001 sample_excerpts).

   **§2 — Banned Patterns** (from BP-NNN artifacts and ai-indicator-policy DEC)
   - Per pattern: pattern, pattern_class, replacement_rule, source.
   - Group by source: operator-direct (em dash, etc.); ai-indicator-research-approved; voice-anchor-derived; council-finding.
   - Note any patterns the operator deferred (so future runs know to surface them again).

   **§3 — Preservation Rules** (from preservation-rule Decisions)
   - Per rule: the rule itself (verbatim from the Decision body), the why (from rationale), examples of what it protects.
   - Examples-preservation rule with worked examples from this book.

   **§4 — Edit Philosophies** (generalized from chapter-edit-philosophy Decisions)
   - When to choose light-copyedit vs substantive-edit vs structural-rewrite. Use the chapter-by-chapter signal table from this run as the worked example.
   - max_line_delta_pct guidance: when 30 is right, when 50 is right, when no cap is right.
   - Per-chapter override rationale patterns (what kinds of findings push you up).

   **§5 — Author-Specific Spelling and Grammar Patterns** (from spelling-pattern / grammar-pattern findings)
   - Common spelling errors the author makes (e.g., specific word swaps, possessive vs plural confusion, etc.).
   - Common grammar patterns (e.g., comma-splice habit, possessive apostrophe drops, etc.).
   - Per pattern: example, correction, frequency observed in this book.

   **§6 — AI-Indicator Policy** (from ai-indicator-policy DEC)
   - The full approve/reject/defer decision verbatim.
   - The reasoning: how voice-anchor cross-check shaped the policy.
   - Patterns to revisit at next book (deferred items).

   **§7 — Edit-Process Notes** (from completion-report discoveries)
   - Patterns the run encountered that aren't in the above sections: friction with subagent context bleed, council false positives, line-delta-cap edge cases, docx-handling gotchas, etc.
   - Recommendations for future runs.

   **§8 — How to Use This Document for Your Next Book**
   - At the start of a future book project, reuse: voice profile (modulo any voice evolution), banned patterns (subject to refresh of AI-indicator research), preservation rules (the examples-preservation rule generalizes), spelling/grammar patterns (these are author-specific and persistent).
   - At the start of a future book project, refresh: voice profile excerpts (use the new book's chapters); AI-indicator research (run T-003 again — patterns drift quickly).

4. **Write the document** to `OR-001.voice_guidelines_path`.
5. **Council does not fire on this task** — standard risk. Operator review is the canonical check; the operator confirms the doc captures what they want before the project archives.
6. Answer @@SCAN markers.

## Specific guidance

**Portability matters.** The doc is for the operator to use across future book projects. Brand-generic structure (don't lock to this book's specific section names; describe the patterns abstractly with examples drawn from this book). Citations point back at the project run for traceability — "this rule was approved as DEC-NNN in book-edit-test on <date>" — so the operator can re-derive any rule.

**Don't paraphrase the source artifacts.** Voice profile is verbatim from VA-001; banned patterns are verbatim from BP-NNN; preservation rules are verbatim from the Decision bodies. The doc's value is organization and accessibility, not rewriting. Tier 1 verbatim-quotation principle applies.

**Discovery synthesis is the agent's substantive contribution.** Sections 5 and 7 require reading completion-report discoveries and synthesizing recurring patterns. This is the only place the doc generates content beyond the source artifacts; the synthesis should cite the originating completion reports.

**Future-book guidance (§8) is operational.** It's not philosophical. The operator reads it when they start their next book and wants concrete advice on what to copy forward and what to refresh.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [VA-001#…], [BP-…], [DEC-…], [F-…]
- **SCAN markers answered:** <count>
- **Document path:** {{ voice_guidelines_path }}
- **Document section count:** 8
- **Banned patterns documented:** <count>
- **Preservation rules documented:** <count>
- **Spelling/grammar patterns documented:** <count>
- **Edit-process notes documented:** <count>
- **Operator review:** approved | revised | rejected
- **Discoveries:** <e.g., "The author has a consistent comma-splice habit that surfaced as 23 separate corrections across chapter passes — this is the highest-frequency grammar pattern and the most useful for the author to know about for future projects">
- **Recommended follow-up:** "T-012 final-read can run; T-013 print-ready-formatting follows."
