---
id: T-002
kind: task
schema: report-synthesis
phase: B
risk_level: standard
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-000]
consumes:
  - "[OR-001#<short-hash>]"
  - "[SRC-NNN#<short-hash>]"  # ONE source per branch — see Branching note below
acceptance_criteria:
  - "Every claim in the source is captured as a `claim` artifact OR explicitly noted as out-of-scope per OR-001.excluded_topics OR explicitly noted as discarded with reason (in completion report)."
  - "Each claim cites its source by hash."
  - "Each claim has claim_type and source_confidence populated."
  - "No claim invents content the source does not support."
---

# Task T-002: Claim Extraction (per-source)

## Objective

Extract every operator-relevant claim from a single source. This task runs once per source — the planner spawns N copies for N sources, optionally branched for parallel subagent execution.

## Branching Note

For projects with many sources, this task is a strong subagent fit. The substrate spawns one branch per source via `hw branch T-002 src-NNN` and folds back with each branch's claim count. Subagents need `file_read` and `file_write`; capability gates enforce.

## Step-by-Step Instructions

1. Read OR-001. Note `synthesis_purpose`, `target_audience`, `excluded_topics`, `weighting_rule`.
2. Read the assigned source artifact. Read the underlying source file at `source.file_path`.
3. Walk the source linearly. For each substantive claim:
   - Confirm it's relevant to OR-001.synthesis_purpose. If not, skip (log in completion report as out-of-scope).
   - Confirm it's not in `excluded_topics`. If it is, skip (log).
   - Determine `claim_type` (observation / statistic / recommendation / definition / hypothesis / methodology-note / finding-of-fact).
   - Determine `source_confidence` (stated-by-source / inferred-from-source / contested-in-source). If the source explicitly hedges or marks uncertainty, that's contested-in-source.
   - Capture in the agent's words but tightly faithful to the source. Do not paraphrase loosely.
   - Run `hw add claim < draft-clm-NNN.md` per substrate protocol.
4. If the source is an earlier round of a `supersedes` chain, flag claims that the later round may correct. Do not yet write anti-patterns; that's task T-003.
5. Answer @@SCAN markers.

## Specific guidance

**Do extract:** claims, observations, statistics, recommendations, definitions stated or clearly inferred from the source.

**Do NOT extract:** chrome (table of contents, methodology preamble unless methodologically significant, acknowledgments, background that's not load-bearing for synthesis_purpose).

**Loose paraphrase is failure.** If a source says "users in our sample reported X happening N% of the time," the claim should preserve N and the sample qualifier. "Users often experience X" is too loose.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Source processed:** [SRC-NNN#hash]
- **Citations consumed:** [OR-001#…], [SRC-NNN#…]
- **SCAN markers answered:** <count>
- **Outputs produced:** [CLM-NNN through CLM-MMM]
- **Out-of-scope content noted:** <list with brief reason>
- **Discarded content noted:** <list with reason>
- **Suspected-correction-by-later-round:** <list of claim IDs flagged for T-003 review>
