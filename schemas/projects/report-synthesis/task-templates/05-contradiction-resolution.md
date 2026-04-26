---
id: T-005
kind: task
schema: report-synthesis
phase: C
risk_level: elevated
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-004]
consumes:
  - "[OR-001#<short-hash>]"
  - "ALL [CTR-NNN#hash] with status: open"
acceptance_criteria:
  - "Every open contradiction is resolved (resolved) OR explicitly deferred (deferred) with operator approval."
  - "Each resolution is captured as a Decision artifact with synthesis_role: contradiction-resolution."
  - "Each Decision cites the contradiction by hash, alternatives_considered enumerates each conflicting claim, rationale explains the resolution."
  - "Deferred contradictions have an operator-approved reason in their note."
---

# Task T-005: Contradiction Resolution

## Objective

For each open contradiction, write a Decision artifact resolving it. The Decision captures alternatives, rationale, and the chosen direction. The synthesis output uses only resolved or deferred-with-reason contradictions.

## Step-by-Step Instructions

1. Read OR-001. Note `weighting_rule` — it informs resolution when conflicting claims come from different rounds or different weight tiers.
2. Read all open `contradiction` artifacts.
3. For each contradiction, decide a resolution path:
   - **Direct resolution:** one claim is correct, the other is not. Decision states which and why.
   - **Synthesis:** both claims are partially correct; the resolution combines them or articulates a stance covering both.
   - **Context-dependent:** both claims are correct in different contexts. Resolution articulates the contexts.
   - **Deferral:** insufficient information to resolve. Operator approves deferral; deferred contradictions are noted in the synthesis output as open questions.
4. For each resolution:
   - Write a Decision artifact. `synthesis_role: contradiction-resolution`. `resolves_contradiction: [CTR-NNN#hash]`. `alternatives_considered`: list each conflicting claim. `rationale`: explain the choice, citing OR-001 weighting_rule when applicable.
   - Run `hw add decision < draft-dec-NNN.md`.
   - Update contradiction artifact status to `resolved` (via supersede event with resolved_by populated).
5. For deferrals:
   - Confirm deferral reason with operator.
   - Update contradiction status to `deferred` with the operator-approved note.
6. Answer @@SCAN markers.

## Specific guidance

**Use OR-001.weighting_rule.** If the rule says "latest-corrected-round-wins," and two contradicting claims come from primary (final round) and secondary (initial round) sources, the primary wins by default. Override only with explicit operator-approved rationale.

**Document the loss.** Even when one side wins clearly, the alternatives_considered field captures what the other source said and why it was set aside. This preserves the lost-decision signal that summary-style synthesis erases.

**Council fires.** This task is `risk_level: elevated`. After T-005 completion (Phase C boundary), the council members `contradiction-finder` and `source-fidelity-watcher` review.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Contradictions resolved:** <count>
- **Contradictions deferred:** <count, with operator approval status>
- **Citations consumed:** [OR-001#…], [CTR-…]
- **Decisions produced:** [DEC-NNN through DEC-MMM]
- **Failure scenarios documented (per elevated risk):** 2
- **SCAN markers answered:** <count>
