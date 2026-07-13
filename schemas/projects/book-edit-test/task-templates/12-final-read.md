---
id: T-012
kind: task
schema: book-edit-test
phase: D
risk_level: critical
required_tools: [file_read, file_write, docx_handling]
delivery_mode: constrained
depends_on: [T-010]
consumes:
  - "[OR-001#<short-hash>]"
  - "[VA-001#<short-hash>]"
  - "ALL [BP-NNN#hash]"
  - "ALL Decisions with synthesis_role: preservation-rule"
  - "ALL Decisions with synthesis_role: ai-indicator-policy (including deferred items)"
  - "Assembled manuscript at OR-001.deliverable_path"
acceptance_criteria:
  - "The assembled manuscript was read in full, in order, as a continuous document (not as 14 separate chapters)."
  - "Every issue surfaced is captured as a finding artifact OR resolved in-place if the issue is small enough that fixing it doesn't require operator review (e.g., a single typo missed by a chapter pass)."
  - "Every banned-pattern instance found anywhere in the manuscript is registered as a finding (this should be zero if Phase B was clean; non-zero indicates a Phase B Layer 1 escape)."
  - "Every deferred AI-indicator candidate that appears in the manuscript is surfaced for operator final decision (re-promote-to-banned or accept)."
  - "Every preservation-rule violation found anywhere is registered as a critical finding; if found, the manuscript fails final-read and must be re-passed."
  - "Council fires (critical risk): voice-preservation-watcher, preservation-rule-watcher, chapter-coverage-auditor, continuity-watcher, operator-goal-aligner all PASS."
---

# Task T-012: Final Read

## Objective

Read the assembled manuscript in full as a continuous document and surface any remaining issues the per-chapter passes and the continuity scan missed. This is the document-level pass that catches what only emerges when the book is read straight through.

This task is read-mostly; small in-place corrections are allowed (typos, minor grammar fixes obviously missed) but substantive changes require routing back to chapter passes or to T-009 continuity-resolution.

## Step-by-Step Instructions

1. Read OR-001, VA-001, all banned-pattern artifacts, all preservation-rule Decisions, the ai-indicator-policy Decision (including its deferred items), and the assembled manuscript.
2. **Read the assembled manuscript in full, in order.** Treat it as one continuous document. Pace: front matter → chapter 1 → ... → chapter N → back matter. Do not skim.
3. **For each issue surfaced:**
   - **Banned-pattern instance:** any occurrence of any banned pattern anywhere. This should be zero post-Phase-B; non-zero indicates a Layer 1 escape. Register as a critical finding (`finding_kind: ai-indicator-candidate` or other relevant kind), cite the BP that flags it.
   - **Preservation-rule violation:** an example, case study, or quote that has been paraphrased, restructured, or composited. Register as a critical finding citing the violated preservation-rule DEC. Critical findings here trigger a chapter re-pass; the manuscript fails final-read until resolved.
   - **Deferred AI-indicator pattern instance:** if a pattern that the operator deferred at T-003 appears in the manuscript, surface for the operator's final decision. Either promote to banned (and re-pass the chapters that contain instances) or accept (and document the acceptance in the ai-indicator-policy DEC for future books).
   - **Voice drift:** any passage that reads off-voice (the operator's voice doesn't sound like itself in that passage). Register as a finding citing VA-001; if the drift is substantial, schedule a chapter re-pass.
   - **Continuity issue not caught at T-008:** any inconsistency the cross-chapter scan missed. Register as a contradiction, route to T-009.
   - **Document-level flow issues:** chapter transitions that don't read smoothly, redundant passages, missing connective tissue. Surface for operator's call (in-place fix may not be appropriate; depends on scope).
   - **Typos and minor grammar misses:** small enough to fix in place. Apply the fix; emit external_state.read_back per the live-edit primitive.
4. **Surface to operator** with a structured report:
   - Manuscript word count, chapter count, structural summary.
   - Banned-pattern instances found: <count>. (Should be 0; non-zero is a defect.)
   - Preservation-rule violations found: <count>. (Must be 0 to PASS.)
   - Deferred AI-indicator pattern instances: <count, with operator's call-out per pattern>.
   - Voice-drift findings: <count, with chapter localization>.
   - Continuity findings: <count, with cross-chapter localization>.
   - Document-level flow findings: <count, with locations>.
   - In-place corrections applied: <count, with locations>.
5. **Operator review.** Operator confirms: approve | revise | reject.
   - Approve: T-013 print-ready-formatting can run.
   - Revise: route findings back to appropriate prior tasks (chapter re-pass, T-009 continuity-resolution); T-012 re-runs after.
   - Reject: project defers; operator decides next step.
6. **Council fires** (critical risk per council.yaml). All members PASS gates approval.
7. Answer @@SCAN markers.

## Specific guidance

**Read straight through.** The point of final-read is to catch what only emerges at the document scale. Reading chapter-by-chapter (the Phase B mode) misses redundancy across chapters, transitions that don't flow, voice drift between adjacent chapters that each individually pass.

**In-place corrections are bounded.** Typos and obvious one-character grammar fixes are in-place. Anything bigger routes back to a re-pass. The bar: would a reader notice the fix? If yes, it's not in-place; route it.

**Banned-pattern escapes are friction-log signal.** A surviving em dash in the assembled manuscript means Phase B Layer 1 missed it. That's worth a friction.log event with `type: REGRESSION` and `severity: blocking` (the manuscript can't ship with the violation).

**Preservation-rule violations are the worst kind.** If an example was paraphrased and the assembled manuscript ships, the published book has fabricated detail. Tier 1. Critical-finding mandatory; manuscript fails final-read until resolved.

**Deferred AI-indicator patterns:** the operator deferred them at T-003. The deferral was conditional: "let's see if it bites." This task is where it bites or doesn't. Surface the actual instances in context so the operator can decide concretely, not abstractly.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [VA-001#…], [BP-…], [DEC-…]
- **SCAN markers answered:** <count>
- **Manuscript:** {{ deliverable_path }} (hash: <...>)
- **Word count:** <N>
- **Read time:** <Z minutes>
- **Banned-pattern instances found:** <count> (should be 0)
- **Preservation-rule violations found:** <count> (must be 0 to PASS)
- **Deferred AI-indicator pattern instances:** <count, by pattern>
- **Voice-drift findings:** <count, by chapter>
- **Continuity findings:** <count>
- **Document-level flow findings:** <count>
- **In-place corrections applied:** <count, with locations and external_state.read_back IDs>
- **Council verdicts:** all five members
- **Operator decision:** approved | revised | rejected
- **Failure scenarios documented (per critical risk):** 3
- **Discoveries:** <e.g., "Three em dashes survived Phase B (Layer 1 regex was case-sensitive but a Unicode variant was used); friction.log F-NNN logged">
- **Recommended follow-up:** "T-013 print-ready-formatting can run on operator approval."
