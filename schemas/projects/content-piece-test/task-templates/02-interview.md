---
id: T-002
kind: task
schema: content-piece-test
phase: B
risk_level: elevated
required_tools: [file_read, file_write]
delivery_mode: constrained
delegation_recommended: false
depends_on: [T-001]
runs_in: parent_context
requires_handoff_acknowledge: true
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-002#<short-hash>]"
  - "ALL [SRC-NNN#<short-hash>]"
acceptance_criteria:
  - "Every interview turn from the agent contains ≤2 questions (capability-gates.yaml interview_question_budget.max_per_turn). Layer 1 fails on overrun."
  - "Each operator response is captured as a Finding (F-NNN) with synthesis_role: interview-answer and turn_id populated."
  - "Each finding adds interpretation, not just restatement of the operator's words. (interpretation-watcher council member fires on phase.complete-B.)"
  - "Interview closes when agent says 'I think I have enough to write something real' AND operator confirms (or pushes back with a specific 'ask one more about X')."
  - "Phase.complete-B council fires (interpretation-watcher + thinness-watcher); both PASS before T-003 can begin."
---

# Task T-002: Interactive Interview

## Why this runs in the parent context

Subagent dispatch loses turn-by-turn visibility. The interview question budget Layer 1 check needs to fire per-turn, and the interpretation-watcher needs to compare each finding against its source operator response. Both require the parent context to hold the running interview log. T-002 is the only task in this schema that is NOT subagent-dispatched.

## Objective

Through a sequence of agent turns and operator turns, develop the material the piece needs. Each operator response that adds substantive content emits a finding (F-NNN). The agent applies interpretation, not restatement.

## Step-by-Step Instructions

### Setup

1. Read OR-001 and DEC-002. Note voice_anchor (governs phrasing of agent's questions — match register), central angle (the load-bearing claim the interview needs to support).
2. Read all SRC-NNN. For each source, read the body (this is the deep-content pass T-001 deferred).
3. From the source bodies, identify gaps the interview needs to fill: places where the central angle is asserted but not evidenced, places where examples would help, places where the operator's stance is unclear.

### Interview loop (per turn)

4. Draft your turn. **Hard cap: ≤2 questions**. Count "?" terminating sentences in your draft, excluding those inside `[paraphrase: ...]` markers. If 3+, redraft.
5. If you have 0 questions but a substantive observation worth surfacing (e.g., "the X article claims X but doesn't ground it in an example — want me to ask for one?"), say it as a statement and await operator's lead.
6. Operator responds.
7. **Capture each substantive operator response as a finding.** Run `hw add finding` with:
   - `synthesis_role: interview-answer`
   - `turn_id: T-002-turn-NN`
   - body text: include the operator's verbatim words (or `[paraphrase: ...]` for compression) AND your interpretation. Pattern: "Operator said: <verbatim or paraphrase>. Interpretation: <what this implies for the piece — the framing this answer suggests, the angle it sharpens, the example it makes available>."
8. Tag any operator phrasing that is especially distinctive ("sounds like the operator") for later VK-NNN flagging in T-003 — do NOT emit VK artifacts yet (those happen in T-003 after operator approves the keeper list). Note them in the finding's tags as `keeper-candidate`.
9. Repeat from step 4.

### Closure

10. When you believe the corpus + interview has enough material to write something real, say so explicitly: *"I think I have enough to write something real. We have <list of available material in 2-3 sentences>."*
11. Operator confirms ("yes, proceed") OR pushes back ("ask one more about X" / "I want to add one more thing"). On pushback, return to step 4. On confirm, close T-002.
12. Phase.complete-B council fires: interpretation-watcher reviews findings; thinness-watcher reviews source + finding count vs. central angle requirements. On all-PASS, T-003 unblocks.

## Refusal-to-pad

If after 5+ turns the agent suspects the operator does not have enough substantive material to write the piece honestly (operator gives short, non-specific answers; central angle isn't getting traction; examples aren't materializing), the agent surfaces this as a thinness candidate:

> "I'm having trouble finding enough specific material to support the central angle. Want to keep going and see if it shakes out, or pause this piece and revisit when you have more to draw on?"

If operator says pause: emit `anti_pattern.add` artifact documenting the thinness, mark T-002 status `escalated`, hand off via `session.handoff` with `recommended_first_action: "operator decides whether to acquire more material or supersede the central angle."`

## Friction-log auto-prompt expectations

- After 3 question-budget Layer 1 fails on the same task: friction.log.prompt fires. Agent should follow with friction.log if the budget is genuinely too tight, OR confirm the false-positive (e.g., a turn was a clarifying micro-question that shouldn't have counted).
- After interpretation-watcher FAILs on consecutive findings: friction.log.prompt fires.

## Completion Report

- **Acceptance criteria:** <X/Y pass>
- **Turns:** <count agent / count operator>
- **Findings emitted:** F-NNN through F-MMM
- **Question-budget violations:** <count> (each one captured as a verify.layer1.fail; agent re-drafted)
- **Keeper candidates flagged for T-003:** <count, by F-ID>
- **Phase.complete-B council outcome:** PASS | ESCALATED with <reason>
- **Recommended follow-up:** "Operator pastes rough draft; T-003 begins."
