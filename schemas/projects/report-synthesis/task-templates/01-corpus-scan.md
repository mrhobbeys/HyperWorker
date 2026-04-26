---
id: T-001
kind: task
schema: report-synthesis
phase: A
risk_level: standard
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-000]
consumes:
  - "[OR-001#<short-hash>]"
  - "ALL [SRC-NNN#<short-hash>]"
acceptance_criteria:
  - "Section-level scan completed across every registered source: filenames, first 20 lines, and section headers for each. Full content is NOT read at this step (claim extraction in T-002 is the content-read pass)."
  - "Completion report surfaces 2-3 plausible synthesis purposes with brief justification anchored to the corpus signal — not generic descriptions of what the deliverable could be."
  - "Operator confirms the current OR-001.synthesis_purpose OR the operator triggers a supersede with a refined purpose. The supersede event (or the explicit confirmation) is captured in events.jsonl before T-002 begins."
  - "The completion report records which sources contributed to which surfaced purpose, so the operator can spot-check whether the agent's reading of the corpus matches the operator's."
---

# Task T-001: Purpose-Fit Corpus Scan

## Objective

After T-000 has registered every source as a `source` artifact, the agent reads section-level summaries of every source (filename + first 20 lines + section headers — NOT full content) and surfaces 2-3 plausible synthesis purposes with brief justification anchored to what the corpus actually contains. The operator either confirms the current `OR-001.synthesis_purpose` or triggers a supersede with a refined purpose before T-002 (claim extraction) begins.

## Why this exists

In the v5.0 brand-foundation-synthesis run the highest-leverage operator intervention was refusing to lock the synthesis purpose without seeing what the corpus actually contained. v5.0.1 had no structural step for this; the operator had to know to push back. v5.1 makes the corpus-vs-purpose check a structural step so the harness surfaces mismatches before extraction begins, instead of the operator having to catch them.

This is the v5.1 form of "do not let bootstrap-time framing lock in a synthesis purpose that the corpus does not actually support."

## Step-by-Step Instructions

1. Read OR-001. Note the current `synthesis_purpose`, `target_audience`, `output_format`, `excluded_topics`, and `weighting_rule`.
2. List every `source` artifact registered in T-000. For each source:
   - Read `source.title`, `source.source_type`, `source.round`, `source.weight`, `source.author`, `source.date`.
   - Open the file at `source.file_path`. Read **only** the first 20 lines and any section headers (lines starting with `#`, `##`, `###`). Close the file. Do not read the body.
3. Build a corpus signal table in your working notes — for each source, what topic clusters appear in the section headers, what dates / scopes / authors are represented, what shape the source has (audit, recommendation, research, etc.).
4. From the corpus signal, surface 2-3 **plausible synthesis purposes**. Each must be anchored to specific sources — *"a synthesis aimed at X, supported by SRC-001, SRC-004, SRC-009"* — not a generic description of what a synthesis could produce. If the corpus signal supports the current `OR-001.synthesis_purpose` and only that, surface it as one of the 2-3; if the signal does not support the current purpose at all, that is itself a finding to report.
5. Present the surfaced purposes to the operator. The operator answers:
   - **Confirm** — the current `OR-001.synthesis_purpose` is what the corpus supports. Record the explicit confirmation in the task's working log; no supersede.
   - **Refine** — the corpus signals a different (or sharper) purpose. The agent runs `hw add operating-reality` for `OR-002` with `reverses: OR-001` and the refined `synthesis_purpose`. The supersede event captures the change.
   - **Defer** — the operator wants more context (e.g., spot-read a specific source body before deciding). The agent surfaces the requested context and re-presents.
6. Confirm the supersede chain (if any) is traversable: the older OR's projection has `superseded_by: [OR-002#hash]`, and the new OR is what `consumes:` lists in downstream tasks reference.
7. Answer @@SCAN markers from `00-REFERENCE-rules.md`.

## Specific guidance

**Do** anchor every surfaced purpose to specific sources by ID. *"A synthesis of competitive landscape claims, supported by SRC-003, SRC-005, SRC-008"* is anchored. *"A competitive landscape synthesis"* is generic and fails the acceptance criterion.

**Do NOT** read source bodies at this step. Section headers + first 20 lines is sufficient signal for purpose-vs-corpus matching; reading bodies bleeds T-002's content-read pass into T-001 and produces over-fit framing.

**Do** treat zero-anchor purposes as a signal that the corpus is misaligned with the bootstrap-time framing. If the corpus genuinely does not support what bootstrap declared, that is the high-leverage finding — surface it explicitly and let the operator decide whether to re-scope or to acquire more sources.

**Do NOT** "solve" a misalignment by inventing a generic purpose that everything could support. The point of the scan is to surface the mismatch, not to paper over it.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [SRC-001#…] through [SRC-NNN#…]
- **SCAN markers answered:** <count>
- **Surfaced synthesis purposes (2-3):**
  1. <Purpose 1> — anchored to: [SRC-NNN], [SRC-MMM], ...
  2. <Purpose 2> — anchored to: [SRC-NNN], [SRC-MMM], ...
  3. <Purpose 3, if applicable>
- **Operator decision:** confirmed / refined-with-supersede / deferred (with reason)
- **Supersede event (if any):** EV-NNNN — OR-002 supersedes OR-001 with refined synthesis_purpose: "<verbatim new purpose>"
- **Discoveries:** <e.g., "Sources SRC-002, SRC-007, SRC-011 cluster on a topic adjacent to but distinct from the bootstrap purpose; flagged for operator review.">
- **Recommended follow-up:** "Proceed to T-002 (claim extraction) with confirmed OR." or "Re-scope the corpus before T-002 begins."
