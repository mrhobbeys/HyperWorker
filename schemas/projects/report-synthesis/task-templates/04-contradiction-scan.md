---
id: T-004
kind: task
schema: report-synthesis
phase: C
risk_level: elevated
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-003]
consumes:
  - "[OR-001#<short-hash>]"
  - "ALL live [CLM-NNN#hash] (earlier-round-corrected claims excluded)"
acceptance_criteria:
  - "Topic-cluster pre-step ran (see §Pre-step). Completion report records the cluster groups (G1..GN) and their claim counts so the scan coverage is auditable."
  - "Within-group pairwise comparisons completed for each cluster; cross-group tension comparisons completed for each cluster pair. Completion report records both pair counts so coverage is countable."
  - "Suspected contradictions ruled compatible (false positives from the heuristic check) are listed in the completion report with the reason each is compatible — not silently dropped."
  - "Contradiction artifacts cite the conflicting claims by hash (Layer 1 enforces) and the completion report records the nature distribution (count per nature value) so the operator can spot-check that 'factual' is not being used as catch-all."
---

# Task T-004: Contradiction Scan

## Objective

Walk the live claim corpus pairwise and surface disagreements between sources. Each contradiction becomes a typed artifact for T-005 to resolve.

## Pre-step: Topic Clustering

Pairwise contradiction scan across N claims is O(N²). For typical synthesis projects with N>50 claims, the unclustered scan is impractical:

| Claims | Unclustered pairs (N(N-1)/2) | Clustered (8 groups, ~equal size) | Reduction |
|---|---|---|---|
| 50 | 1,225 | ~175 within-group + 28 cross-group tension scans | ~84% fewer |
| 100 | 4,950 | ~625 within-group + 28 cross-group tension scans | ~87% fewer |
| 158 (Session 2 actual) | 12,403 | ~1,575 within-group + 28 cross-group tension scans | ~87% fewer |

Without clustering, the scan is either impossibly expensive (full pairwise) or superficial (sampled). Clustering keeps the scan tractable while preserving cross-domain contradiction detection.

**Clustering procedure:**

1. Read each live claim's text and tags.
2. Group claims by topic. Use the `tags` field if populated; otherwise cluster by topic-keyword overlap. 5-10 groups is typical for projects with 50-200 claims.
3. Document the groups (G1..GN) and their claim counts in the completion report. The groups are scaffolding — they are not artifacts and don't need to be hash-cited.
4. **Within-group scan:** pairwise across all claims in each group. Most contradictions surface here.
5. **Cross-group tension scan:** for each pair of groups (G_i, G_j), explicitly check whether the dominant assertions in G_i tension with the dominant assertions in G_j. This catches contradictions that cross domains (e.g., a "market sizing" claim contradicting a "go-to-market strategy" claim).

For N<50, clustering is optional — the unclustered pairwise scan (≤1,225 pairs) is tractable. For N≥50, clustering is mandatory.

This pre-step was a Session 2 invention on the brand-foundation-synthesis run (friction log B-6); it is now ship-canonical for T-004.

## Step-by-Step Instructions

1. Read OR-001 and 00-REFERENCE-rules.md.
2. Read all live `claim` artifacts (excluded: claims discarded in T-003 anti-pattern capture).
3. Run the topic-clustering pre-step above. Document G1..GN and counts.
4. Pairwise within each group, then cross-group tension scan per the pre-step:
   - Do two claims make incompatible assertions about the same thing?
   - Distinguish disagreement from different angles on the same thing. Two claims about different aspects of a topic are not contradicting each other.
5. For each contradiction:
   - Determine `nature`:
     - **factual:** sources disagree on a fact (statistic, definition, observable).
     - **methodological:** sources reach different conclusions because of methodological differences.
     - **recommendation-conflict:** sources recommend different paths.
     - **scope-conflict:** sources disagree about what is in or out of a topic's scope.
     - **temporal:** sources reflect different points in time; both may have been correct at their respective times.
   - Run `hw add contradiction < draft-ctr-NNN.md`. Status: open.
6. If a "contradiction" turns out to be one source generalizing while another specifies, do not register a contradiction — these are compatible. Note in completion report.
7. Answer @@SCAN markers.

## Heuristics

The substrate runs a Layer 2 `contradiction_surfacing` heuristic check that scans claim text for keyword conflicts and structural inconsistencies. It produces suspected contradictions; the agent confirms each as a real contradiction or marks compatible. Heuristic, not exhaustive — agent judgment is required.

For high-density disagreement domains (e.g., audits across rounds, multiple competitive analyses), the contradiction count may be high. The synthesis is more valuable for it.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Live claims scanned:** <count>
- **Citations consumed:** [OR-001#…], [CLM-…]
- **Contradictions registered:** [CTR-001 through CTR-NNN]
- **Suspected contradictions ruled compatible:** <list with brief reason>
- **Contradictions by nature:** factual=<n>, methodological=<n>, recommendation=<n>, scope=<n>, temporal=<n>
- **SCAN markers answered:** <count>
