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
  - "Every open contradiction has terminal status: resolved (with a Decision) OR deferred (with operator-approved reason). No open contradictions remain when the task completes."
  - "For each Decision, alternatives_considered enumerates the original conflicting claims verbatim or with explicit paraphrase markers — not glossed. Loose paraphrase of the losing side is the failure mode (it erases the lost-decision signal); the completion report flags any decision whose alternatives_considered is shorter than 50% of the median for this task as a candidate for review."
  - "Each Decision rationale cites OR-001.weighting_rule when the resolution depends on round/weight precedence, OR explicitly states 'weighting rule did not apply because <reason>' if not. Layer 1 enforces citation existence; this criterion enforces that the rule was actually consulted."
  - "Deferred contradictions have an operator-approved reason recorded in the contradiction artifact's deferral note. Operator approval is captured as either an operator-actor task.status event or quoted in the completion report."
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
