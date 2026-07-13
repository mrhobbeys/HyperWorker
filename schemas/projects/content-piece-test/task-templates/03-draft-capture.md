---
id: T-003
kind: task
schema: content-piece-test
phase: C
risk_level: standard
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-002]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-002#<short-hash>]"
  - "ALL [F-NNN#<short-hash>] from T-002"
acceptance_criteria:
  - "Operator's rough draft is captured verbatim. Agent does NOT clean up or correct."
  - "Agent flags missing context, internal contradictions, claims unsupported by F-NNN findings — without rewriting them away."
  - "Agent identifies 'lines that sound especially like the operator' and emits one verbatim_keeper artifact per kept line. Each VK has source_finding_or_draft, keep_verbatim:true, applies_to_formats (default [substack-longform, x-longform])."
  - "Operator reviews the keeper list. Each VK flips to operator_approved:true OR operator says 'no, drop it' (in which case the VK is superseded with a new VK marked keep_verbatim:false)."
  - "Keeper list is operator-approved before T-004 begins."
---

# Task T-003: Rough Draft Capture and Verbatim-Keeper Flagging

## Objective

Operator pastes a rough draft (or brain dump). Agent captures it as-is, flags issues without fixing them, and identifies lines that should survive into the final variants byte-for-byte.

## Step-by-Step Instructions

### Capture

1. Receive operator's rough draft. Save to `projects/<piece-slug>/tasks/T-003/operator-draft.md` verbatim.
2. Confirm receipt: "Got it. <word count> words. Reading it now."
3. Read the draft end-to-end.

### Issue-flagging (without rewriting)

4. Identify and surface to operator (do NOT fix):
   - Missing context (the draft references something a reader won't know).
   - Internal contradictions (paragraph 2 says X; paragraph 7 says not-X).
   - Claims unsupported by F-NNN findings or SRC-NNN sources (the operator wrote it but it's not grounded in interview material).
5. For each issue, surface with location + 1-sentence description. Operator decides whether to address in their own next pass or to let T-004 handle (depends on the issue).

### Verbatim_keeper flagging

6. Re-read the draft looking for "lines that sound especially like the operator." Heuristics (matched against OR-001.voice_anchor):
   - Strong-take leads ("I was wrong about X.", "Most people are confused about Y but it's actually Z.").
   - Operator's distinctive phrasings (specific word choices, sentence rhythms that match voice_anchor).
   - Self-aware admissions ("I tried this and it didn't work.", "I don't have a clean answer.").
   - Specific concrete examples in the operator's words.
7. For each candidate, emit a verbatim_keeper draft (do NOT add to events yet — operator approves first):
   ```yaml
   ---
   id: VK-NNN  # next ID
   kind: verbatim_keeper
   text: "<the line, exactly>"
   source_finding_or_draft: "[SRC-DRAFT#<short-hash>]" or "[F-NNN#<short-hash>]"
   keep_verbatim: true
   applies_to_formats: [substack-longform, x-longform]  # default; YouTube exempt unless hook line
   operator_approved: false  # flips to true after operator approves
   tags: [keeper-candidate]
   ---
   ```
8. Present the candidates to operator as a list:
   > "I flagged these <N> lines as ones that sound especially like you and should survive verbatim into Substack and X (YouTube is exempt unless you tag a hook line). Approve / reject / move."

### Operator approval

9. Operator goes through each:
   - **Approve** → agent runs `hw add verbatim_keeper` with operator_approved:true.
   - **Reject** → agent runs `hw add verbatim_keeper` with keep_verbatim:false (recorded as a non-keeper for completeness; T-004 won't enforce it).
   - **Modify scope** (e.g., "keep this one for YouTube too") → agent updates applies_to_formats.
10. Once every candidate is decided, T-003 closes.

## Specific guidance

**Do NOT** rewrite the operator's lines to "polish" them. Tier 1 SOURCE-AND-VOICE-FIDELITY blocks this. The whole point of VK is that the operator's distinctive phrasing survives the variant-generation pass.

**Do NOT** flag every well-written sentence as a keeper. Keepers are specifically lines where the operator's voice is doing work the agent could not reproduce — distinctive phrasing, strong-take leads, self-aware admissions. A well-written but generic sentence is not a keeper.

**Do** flag thin draft material as a thinness signal. If the draft is mostly placeholder ("explain why this matters here") and there are few keeper candidates, surface to operator that the piece may need more interview turns or more material before T-004 makes sense.

## Completion Report

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [DEC-002#…], F-NNN through F-MMM
- **Draft word count:** <N>
- **Issues flagged:** <list>
- **Verbatim_keeper candidates:** <count> flagged → <count> approved / <count> rejected / <count> modified scope
- **VK artifacts emitted:** VK-001 through VK-NNN
- **Recommended follow-up:** "Proceed to T-004 ab-variant format generation."
