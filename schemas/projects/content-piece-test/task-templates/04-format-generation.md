---
id: T-004
kind: task
schema: content-piece-test
phase: D
risk_level: critical
required_tools: [file_read, file_write]
delivery_mode: ab-variant
ab_variant_count: 3
ab_variant_axis: publication_format
delegation_recommended: true
delegation_isolation: hermetic_subagent
depends_on: [T-003]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-002#<short-hash>]"
  - "ALL [F-NNN#<short-hash>] from T-002"
  - "ALL [VK-NNN#<short-hash>] with operator_approved:true"
  - "[SRC-DRAFT#<short-hash>] (operator rough draft from T-003)"
acceptance_criteria:
  - "Three variants generated, one per format declared in OR-001.formats[]: substack-longform, x-longform, youtube-leadins."
  - "Each variant is its own artifact projection with its own hash. Layer 1 citation freshness applies per variant."
  - "Each variant cites its consumes by hash. Layer 1 blocks any variant where a verbatim_keeper hash mismatches (i.e., the line was silently rewritten)."
  - "Substack variant: hook → free section → paywall cliff (marked with HTML comment <!-- PAYWALL CLIFF: <reason> -->) → insight section → closing. Each section's structure matches OR-001.formats[substack-longform].structure."
  - "X variant: thread or article. Each chunk standalone-terminable. No manufactured cliffhangers."
  - "YouTube variant: 3 sub-options × 3-5 sentences each, one per declared framing (controversy / curiosity / utility)."
  - "Format-announce: agent emits '## Format: <id>' before each variant's content body."
  - "All five council members fire (voice-watcher, angle-anchor-watcher, thinness-watcher, verbatim-keeper-fidelity, variant-comparison-watcher). All-agree-or-escalate convergence. All-PASS unblocks operator review."
---

# Task T-004: Ab-Variant Format Generation (Substack, X, YouTube)

## Why this is one task with three variants

`delivery_mode: ab-variant`. One subagent runs, produces three differentiated variants in one pass. Sequential separate tasks lose cross-format differentiation pressure (the second variant ends up as a paraphrase of the first because the subagent has the first in context).

The hermetic subagent does NOT see prior variant prose during its own draft. It sees the consumes set by hash citation, materializes the consumed content from projections, and emits each variant independently — but it knows in advance that all three are coming, which forces format-native structuring rather than incremental polish.

## Step-by-Step Instructions

### Setup (subagent)

1. Read consumes by hash, materialize from projections:
   - OR-001 (voice_anchor governs phrasing; formats[] declares the three structures).
   - DEC-002 (central angle — the load-bearing claim).
   - All F-NNN findings from T-002 (interview material).
   - All VK-NNN with operator_approved:true (lines that must survive verbatim).
   - The operator's rough draft from T-003.
2. Update `consumed-inputs.md` with paraphrase of each consumed artifact. Layer 1 recitation overlap check fires.
3. Answer @@SCAN markers from 00-REFERENCE-rules.md (Tier 1, Tier 2, Tier 3).

### Variant 1: substack-longform

4. Announce: `## Format: substack-longform`
5. Produce:
   - **Hook** (1-2 sentences that earn the read; lead with the strongest take, do not bury).
   - **Free section** — context, setup, story (free preview content).
   - `<!-- PAYWALL CLIFF: <one-sentence reason; what's behind the cliff -->`
   - **Insight or breakdown section** — the load-bearing analysis (paywalled).
   - **Closing** that doesn't wrap up too neatly.
6. Confirm every approved VK in vk.applies_to_formats containing "substack-longform" appears byte-for-byte. Citation: `[VK-NNN#hash]` in the variant's footer references list.
7. Save to `outputs/<piece-slug>/substack-longform.md`.

### Variant 2: x-longform

8. Announce: `## Format: x-longform`
9. Produce: thread or long-form article. Each chunk (paragraph or thread tweet) ends at a point where the reader stopping there is acceptable — no "but wait" hooks. Lead with the strongest take or most surprising fact.
10. Confirm every approved VK in vk.applies_to_formats containing "x-longform" appears byte-for-byte.
11. Save to `outputs/<piece-slug>/x-longform.md`.

### Variant 3: youtube-leadins

12. Announce: `## Format: youtube-leadins`
13. Produce 3 sub-options × 3-5 sentences each, one per framing in OR-001.formats[youtube-leadins].framings (default: controversy-or-challenge, curiosity-or-mystery, practical-or-utility):
    - **Option A — controversy/challenge:** lead with a contrarian or challenging claim.
    - **Option B — curiosity/mystery:** lead with a hook the viewer has to keep watching to resolve.
    - **Option C — practical/utility:** lead with the value the viewer gets if they stick around.
14. Each option is written for the spoken voice (short sentences, contractions OK, no parenthetical clauses).
15. VK enforcement is exempt for YouTube unless a keeper was tagged as a hook line.
16. Save to `outputs/<piece-slug>/youtube-leadins.md`.

### Wrap

17. Emit `task.complete` with `completion_report_path: tasks/T-004/04-format-generation-completion.md`.
18. Council fires (per council.yaml triggers): voice-watcher, angle-anchor-watcher, thinness-watcher, verbatim-keeper-fidelity, variant-comparison-watcher.
19. All-agree-or-escalate convergence. On all-PASS, operator review unblocks.

## Cross-format polish-leak prevention

The subagent does not see Variant 1's prose while drafting Variant 2. The substrate enforces this by running each variant generation in a fresh subagent context, with consumes materialized but prior variants in the run NOT in the consumes list (until that variant is hash-citable as its own projection).

This is the v5.1 ab-variant trivial-paraphrase falsifier (H-CW2): if the variants all read as the same piece with whitespace differences, ab-variant is not earning its load-bearing role.

## Specific guidance

**Do** match OR-001.voice_anchor. Short sentences. No corporate fluff. Strong-take leads. Match register.

**Do** verify VK byte-fidelity before declaring complete. Run `grep -F "<vk.text>"` against each applicable variant. Layer 1 will catch a miss but the agent should pre-check.

**Do NOT** invent anecdotes, quotes, or claims not present in F-NNN, SRC-NNN, or VK-NNN. Tier 1 SOURCE-AND-VOICE-FIDELITY.

**Do NOT** smooth over a thin material problem by padding. If Variant 2 is genuinely shorter than Variant 1 because the material doesn't carry, that is the correct outcome; the thinness-watcher will PASS on the shorter variant if it is honest, and FAIL on a padded one.

## Completion Report

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [DEC-002#…], F-NNN…, VK-NNN…, SRC-DRAFT
- **SCAN markers answered:** <count>
- **Variants produced:**
  - substack-longform.md (<word count>)
  - x-longform.md (<word count>)
  - youtube-leadins.md (3 options × 3-5 sentences)
- **VK fidelity check (pre-council):** <count> approved VKs / <count> verified byte-for-byte / <count> flagged for fix
- **Council members fired:** voice-watcher, angle-anchor-watcher, thinness-watcher, verbatim-keeper-fidelity, variant-comparison-watcher
- **Convergence outcome:** all-PASS / escalated with <reason>
- **Recommended follow-up:** "Operator reviews three variants; on approval, run hw wrap; hw schema save extracts content-piece schema."
