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
  - "Pairwise scan completed across all live claims."
  - "Every detected contradiction is registered as a `contradiction` artifact with status: open."
  - "Contradiction artifacts cite the conflicting claims by hash."
  - "Contradiction nature is classified (factual / methodological / recommendation-conflict / scope-conflict / temporal)."
---

# Task T-004: Contradiction Scan

## Objective

Walk the live claim corpus pairwise and surface disagreements between sources. Each contradiction becomes a typed artifact for T-005 to resolve.

## Step-by-Step Instructions

1. Read OR-001 and 00-REFERENCE-rules.md.
2. Read all live `claim` artifacts (excluded: claims discarded in T-003 anti-pattern capture).
3. Group claims by topic/tag. Pairwise within each group:
   - Do two claims make incompatible assertions about the same thing?
   - Distinguish disagreement from different angles on the same thing. Two claims about different aspects of a topic are not contradicting each other.
4. For each contradiction:
   - Determine `nature`:
     - **factual:** sources disagree on a fact (statistic, definition, observable).
     - **methodological:** sources reach different conclusions because of methodological differences.
     - **recommendation-conflict:** sources recommend different paths.
     - **scope-conflict:** sources disagree about what is in or out of a topic's scope.
     - **temporal:** sources reflect different points in time; both may have been correct at their respective times.
   - Run `hw add contradiction < draft-ctr-NNN.md`. Status: open.
5. If a "contradiction" turns out to be one source generalizing while another specifies, do not register a contradiction — these are compatible. Note in completion report.
6. Answer @@SCAN markers.

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
