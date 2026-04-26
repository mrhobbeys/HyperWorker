---
id: T-003
kind: task
schema: report-synthesis
phase: B
risk_level: standard
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-002]
lightweight_completion: true
consumes:
  - "[OR-001#<short-hash>]"
  - "ALL [SRC-NNN#hash] with supersedes/superseded_by relationships"
  - "ALL [CLM-NNN#hash] flagged in T-002 as suspected-correction-by-later-round"
acceptance_criteria:
  - "Every supersedes chain has been walked: where the later round corrected the earlier, the wrong direction is captured as an anti-pattern."
  - "Each anti-pattern cites the earlier source by hash and points to the superseding direction (later claim or decision)."
  - "Earlier-round claims that the later round corrected are marked discarded — do not appear as live claims in the synthesis."
---

# Task T-003: Anti-Pattern Capture from Earlier Rounds

## Objective

Walk the supersedes chains from T-000. Where a later round corrects an earlier one, capture the wrong direction as an anti-pattern. This preserves the historical-error signal that would be lost if earlier rounds were silently ignored.

## Step-by-Step Instructions

1. Read OR-001 and 00-REFERENCE-rules.md (Tier 1 source-fidelity, Tier 2 operator-alignment).
2. Identify all sources with `supersedes` or `superseded_by` relationships from the source inventory.
3. For each chain (e.g., `01-website-audit.md` → `01-website-audit-notes.md`):
   - Read the earlier source's claims (already extracted as CLM-* in T-002).
   - Read the later source's claims.
   - Compare. Where the later round contradicts, refines, or replaces an earlier claim, treat the earlier claim as a wrong direction.
4. For each wrong direction:
   - Write an anti-pattern artifact: title states the wrong direction, `from_source` cites the earlier source, `superseding_direction` cites the later claim or a decision that captures the correct direction.
   - Run `hw add anti-pattern < draft-ap-NNN.md`.
5. Mark earlier-round claims that became anti-patterns as discarded (status update via supersede event). They are not used as live claims in synthesis.
6. If a claim from an earlier round was *not* corrected by the later round, it remains a live claim. Flag this in the completion report — it's signal that the earlier round had value beyond just being wrong.
7. Answer @@SCAN markers.

## What this task is NOT

Not anti-pattern capture across unrelated sources. Cross-source contradictions are handled in T-004 contradiction-scan and T-005 contradiction-resolution. This task only handles within-chain (round-corrected) wrong directions.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Chains walked:** <list of supersedes chains>
- **Anti-patterns produced:** [AP-NNN through AP-MMM]
- **Earlier-round claims discarded:** <list>
- **Earlier-round claims preserved (not corrected by later round):** <list with brief note>
- **SCAN markers answered:** <count>
- **Discoveries:** <e.g., "Round 1 had a methodology error explained in Round 2; captured as AP-005">
