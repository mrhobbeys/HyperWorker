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
  - "Every substantive assertion in the source is captured as a `claim` artifact OR explicitly noted in the completion report as out-of-scope (per OR-001.excluded_topics, with the topic) OR discarded with reason. Chrome content (TOC, methodology preamble, acknowledgments) is exempt and need not appear in the report."
  - "Each claim cites its source by hash (Layer 1 will reject any claim event without a valid [SRC-NNN#hash])."
  - "Claim-type distribution is recorded in the completion report (count per claim_type) so the operator can spot-check that 'observation' is not being used as a catch-all bucket."
  - "Source-confidence distribution is recorded in the completion report. If 100% of claims are tagged stated-by-source, the executor is asked whether the source genuinely contained no inferred or contested content (often a sign of skim-extraction)."
  - "No claim contains content the source does not support. Spot-check: the executor cites verbatim source text for at least one randomly chosen claim per 25 claims extracted, in the completion report."
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

## Granularity guidance

A claim is one discrete testable assertion. Two heuristics determine when to split a source statement into multiple claims and when to keep it as one:

**Split if** the source statement combines multiple independently verifiable assertions joined by `and`, `but`, semicolons, or parallel clauses. Each becomes its own claim.

> Source: "The TAM is 150K-200K and saturation in our segment is 2 out of 5."
> → CLM-A: "TAM is 150K-200K" (claim_type: statistic)
> → CLM-B: "Saturation in segment is 2/5" (claim_type: observation)

**Keep as one if** the source statement is a single assertion with internal qualifiers that scope or condition it. Qualifiers don't multiply claims.

> Source: "The target buyer is the practice manager at behavioral-health groups of 5 to 25 clinicians."
> → CLM-X: "Target buyer is practice-manager at BH groups, 5-25 clinicians" (claim_type: definition)

The qualifiers ("at BH groups", "5 to 25 clinicians") scope the assertion; they are not separate claims.

**Compound recommendations** typically split. "We recommend doing A, then B, then C" is three claims (or a single claim with sub-steps if the steps are inseparable from the recommendation's logic — judgment call; default to splitting).

**Numeric assertions** stay together with their qualifier. "Sample N=432, response rate 67%" is one claim, not two — the response rate is meaningless without the sample size.

The granularity target is 10-20 claims per substantive source page. Density much lower suggests skim-extraction; density much higher suggests over-splitting (the synthesis later has to recombine). Both are flagged in the completion report's claim-distribution check.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Source processed:** [SRC-NNN#hash]
- **Citations consumed:** [OR-001#…], [SRC-NNN#…]
- **SCAN markers answered:** <count>
- **Outputs produced:** [CLM-NNN through CLM-MMM]
- **Out-of-scope content noted:** <list with brief reason>
- **Discarded content noted:** <list with reason>
- **Suspected-correction-by-later-round:** <list of claim IDs flagged for T-003 review>
