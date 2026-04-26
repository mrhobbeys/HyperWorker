---
id: T-008
kind: task
schema: report-synthesis
phase: D
risk_level: critical
required_tools: [file_read]
delivery_mode: constrained
depends_on: [T-007]
consumes:
  - "[OR-001#<short-hash>]"
  - "ALL [SRC-NNN#hash]"
  - "Draft at {{ deliverable_path }}.draft.md"
acceptance_criteria:
  - "Every registered source has status: incorporated | contradicted-and-resolved | discarded-with-reason. No source is orphan."
  - "Every claim in the draft cites at least one source by hash."
  - "No internal contradictions in the draft."
  - "Council pass: source-fidelity-watcher, coverage-auditor, contradiction-finder, operator-goal-aligner, weighting-checker (if applicable)."
  - "Audit report written to `tasks/08-completeness-audit-completion.md` per harness completion-report convention."
---

# Task T-008: Completeness Audit

## Objective

Audit the draft for source coverage, citation integrity, and internal consistency. This is the structural check before operator review. The full council fires here (critical risk).

This task is read-only on the synthesis draft. It does not modify the draft. It produces an audit report; if the audit fails, T-007 is reopened.

## The 7-Check Methodology (canonical)

The audit runs seven checks in this order. The Session 3 agent on the brand-foundation-synthesis run invented this methodology because T-008 said "audit for completeness" without specifying what; the methodology caught five real issues and is now ship-canonical for T-008.

1. **Section completeness.** Every section declared in the structure Decision (T-006) is present in the draft and contains content (not a placeholder). Empty sections fail.
2. **Citation integrity.** Every assertion in the draft has at least one `[KIND-NNN#hash]` citation. No floating prose. (Layer 1 caught most of this on event write; this is the document-level re-confirmation.)
3. **Source coverage.** Every registered SRC has terminal status: incorporated (cited at least once) | contradicted-and-resolved (linked to a CTR resolved by DEC) | discarded-with-reason (Decision artifact stating why). No orphan sources.
4. **OR constraint compliance.** Excluded topics from OR-001 do not appear in the draft. Output_format matches the structure. If OR declared a confidence_floor of validated, no provisional findings are cited.
5. **Anti-pattern consistency.** Where the draft takes a direction the supersede chain captured as an AP, the AP is cited and the supersession noted. AP citations are not silently dropped.
6. **Internal consistency.** Pairwise scan across sections for contradictions. Two sections cannot make conflicting assertions without an internal note. (Layer 2 `synthesis_internal_consistency` check supports this.)
7. **Decision coverage.** Every resolved contradiction's Decision is cited at least once in the draft, OR an explicit note in the audit report explains why a particular resolution was not surface-relevant for the draft.

Each check is recorded individually in the audit report (`tasks/08-completeness-audit-completion.md`) with PASS/FAIL and findings. Overall verdict is FAIL if any of checks 1-6 fails; check 7 failures are warnings unless the schema's `confidence_floor` is `validated` (in which case decision coverage becomes blocking).

## Step-by-Step Instructions

1. Read OR-001, the structure Decision, all source artifacts, and the draft.
2. **Coverage audit (Check 3):** for each registered source artifact, classify its status by examining the draft:
   - **Incorporated:** the source's claims are cited in the draft (one or more times).
   - **Contradicted-and-resolved:** the source's claims appear in a resolved contradiction artifact and the resolution Decision is cited in the draft.
   - **Discarded-with-reason:** the source has an explicit Decision artifact stating why it was discarded.
   - **Orphan (FAIL):** none of the above. List in audit report.
3. **Citation integrity:** scan the draft for assertions that lack citations. Layer 1 verification has already run during T-007 writes; this is a re-confirmation at the document level.
4. **Internal consistency:** pairwise scan synthesis sections for contradictions. The Layer 2 `synthesis_internal_consistency` check runs here.
5. **Operator-goal alignment:** confirm draft serves OR-001.synthesis_purpose. Sample the deliverable from the audience perspective.
6. **Weighting check:** if sources had multi-round chains, confirm the weighting rule was applied. Earlier-round content should appear as anti-patterns or be discarded; not as live claims.
7. Council fires. Each member runs context-asymmetric (sees draft + structure + sources, not the implementer's reasoning).
8. Write audit report to `tasks/08-completeness-audit-completion.md` (the harness completion-report path for this task — T-009 consumes by this exact path). Structure:
   - Coverage summary (table of source ID → status).
   - Citation integrity result.
   - Internal consistency result.
   - Operator-goal alignment result.
   - Weighting result (if applicable).
   - Council member results (one line each per VERIFICATION.yaml format).
   - Overall verdict: PASS / FAIL : <reasons>.
9. If FAIL, T-007 reopens with the audit report as input. If PASS, T-009 begins.
10. Answer @@SCAN markers.

## What this task is NOT

Not the operator review. The operator review happens in T-009. This task is structural audit — citations, coverage, consistency. The operator sees the audit report alongside the draft when T-009 runs.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Sources audited:** <count>
- **Sources orphan (FAIL if >0):** <count, with list>
- **Citation integrity:** PASS | FAIL : <count of unfulfilled claims>
- **Internal consistency:** PASS | FAIL : <pairs found>
- **Operator-goal alignment:** PASS | FAIL : <misalignments>
- **Weighting:** PASS | FAIL | NA
- **Council verdicts:** <one line each>
- **Overall verdict:** PASS | FAIL
- **Audit report path:** tasks/08-completeness-audit-completion.md
- **Failure scenarios documented (per critical risk):** 3
- **SCAN markers answered:** <count>
