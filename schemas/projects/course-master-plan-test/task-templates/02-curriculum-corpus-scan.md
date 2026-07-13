---
id: T-002
kind: task
schema: course-master-plan-test
phase: A
phase_step: 3
risk_level: elevated
required_tools: [file_read, file_write]
delivery_mode: bounded-iteration
ab_variant_count: null
depends_on: [T-000]
consumes:
  - "[OR-001#<short-hash>]"
  - "[SRC-*#<short-hash>]"  # all sources registered by T-000
acceptance_criteria:
  - "Every registered source (SRC-NNN from T-000) was read at section-summary level (filenames + first 20 lines + section headers, OR fuller reads where the source is small). Sources NOT read get explicit excluded-after-discovery status with reason."
  - "2-3 plausible curriculum structures surfaced (NOT a single 'best' answer). Each structure includes: module sequence (5-15 modules typical), tier-gate proposal (which modules free vs paid), 1-2 sentence learning-objective summary per module, coverage map (which sources informed which modules)."
  - "Each candidate structure passes the lens-fidelity heuristic: module premises reflect operator-stated learning (the lens), not lens-fitted inferences from the corpus."
  - "Operator picked / refined / superseded one of the surfaced structures. The chosen structure is captured as DEC-001 (curriculum-sequence) + DEC-002 (tier-policy)."
  - "Council fires (course-charter-aligner + scope-shrink-watcher) at task.complete; both PASS or escalation captured."
  - "scope-shrink-watcher confirms no candidate module from the surfaced structures was silently dropped without paired Decision (inclusion-exclusion) or excluded-after-discovery scope-completeness entry."
---

# Task T-002: Curriculum Corpus Scan

## Objective

Read every registered source at section-summary level (filenames + first 20 lines + section headers; NOT full content unless small). Surface 2-3 plausible curriculum structures anchored to corpus signal — module sequence + tier-gate proposal + 1-2 sentence learning-objective summary per module + coverage map. Operator picks/refines/supersedes; chosen structure becomes DEC-001 + DEC-002.

This task inherits report-synthesis T-001 (purpose-fit corpus scan) pattern adapted for curriculum discovery.

## Granularity guidance

A "module" in this context is roughly the unit a student would experience as one cohesive learning chunk — usually 1-3 lessons, 30-90 minutes of total content. Don't propose 50 modules. 5-15 is typical. If the corpus suggests fewer (3-4) or more (20+), surface that observation as a Finding rather than forcing the count.

## Lens-fidelity check

Every proposed module premise must reflect what the operator (per their lens) tried, learned, and is teaching. If a corpus document suggests a topic but the operator has no stated learning on it, that module's premise is lens-fitted, not lens-real — surface this in the candidate structure as a flag, not as a polished module.

## Step-by-Step Instructions

1. Read OR-001. Note `course_name`, `lens_anchor` (full list), `cross_project_scope`, `tier_policy.policy_mode`, `curriculum_discovery_mode`. Note `lens_anchor[0]` as the dominant frame.

2. List every registered source from T-000. For each:
   - Read filename + first 20 lines + all section headers.
   - For sources under ~5KB, read the full content (cheap; better signal).
   - Record per-source: domain (what it covers), shape (research / notes / draft / analysis), provisional-relevance (high / medium / low) for curriculum.

3. **Cluster by topic.** Group sources covering the same domain. Surface the cluster set as F-NNN (clustering-finding).

4. **Propose 2-3 candidate curriculum structures.** Each candidate is a different way to sequence and tier the curriculum. Variants axis suggestions:
   - Sequence: "foundations-first" vs. "narrative-first" vs. "problem-first".
   - Tier-gate: more-free-up-front vs. more-paid-up-front vs. tiered-by-progression.
   - Module count: lean (5-7) vs. comprehensive (12-15).

   Each candidate includes:
   - Module sequence (numbered list with proposed titles).
   - Tier assignment per module (free | paid).
   - 1-2 sentence learning-objective summary per module.
   - Coverage map: which SRC-NNNs inform each module.
   - Lens-fidelity note per module: is the premise rooted in operator-stated learning, or lens-fitted?

5. **Surface to operator.** Present the 2-3 candidates side-by-side. Operator picks one, refines elements, or supersedes with a custom structure.

6. **Capture the chosen structure as DEC-001.**
   ```yaml
   id: DEC-001
   kind: decision
   title: "Curriculum sequence for {{ course_name }}"
   synthesis_role: curriculum-sequence
   alternatives_considered:
     - "<candidate 1 — reason rejected>"
     - "<candidate 2 — reason rejected>"
   rationale: "Chosen because <operator's reason>; cites [SRC-NNN#hash] for each module's source."
   constraints_imposed:
     - "Every L2 module spawn cites this DEC-001 by hash. Reorders are DEC-001 supersedes."
   ```
   Include the full module list (with sequence position, title, learning-objective, source coverage) in the body.

7. **Capture tier policy as DEC-002.**
   ```yaml
   id: DEC-002
   kind: decision
   title: "Initial tier policy for {{ course_name }}"
   synthesis_role: tier-policy
   ```
   Body declares: policy_mode (per OR-001.tier_policy.policy_mode), default_tier, free_tier_modules (the explicit list), movement_history (empty initially).

8. **Update OR-001 if curriculum_discovery_mode changed.** Supersede OR-001 with the now-confirmed mode (from-corpus / from-draft / hybrid).

9. **Council fires** at task.complete: course-charter-aligner (on_output prompt) + scope-shrink-watcher. Both must PASS for the task to count complete. scope-shrink-watcher specifically checks no candidate module from the surfaced structures was silently dropped.

10. Answer @@SCAN markers.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…]; [SRC-001#…] through [SRC-NNN#…]
- **SCAN markers answered:** <count>
- **Sources read at full content:** <list of small SRC-NNNs>
- **Sources read at section-summary only:** <list>
- **Sources excluded-after-discovery:** <list with reason>
- **Candidate structures surfaced:** <names of 2-3>
- **Operator pick:** <which candidate, with refinements if any>
- **Outputs produced:** DEC-001 (curriculum-sequence), DEC-002 (tier-policy); F-NNN (clustering-finding); F-NNN (lens-fidelity per-module flags) if any
- **Council outcomes:** course-charter-aligner: <PASS/FAIL>; scope-shrink-watcher: <PASS/FAIL>
- **Discoveries:** <e.g., "corpus suggests 7 modules but operator's lens implies stronger weight on module-3 — module-3 carries 2 lessons instead of 1">
- **Recommended follow-up:** "Operator initiates Phase B spawn cycle for the first module, OR initiates additional supersedes on DEC-001 if the structure surfaces gaps."
