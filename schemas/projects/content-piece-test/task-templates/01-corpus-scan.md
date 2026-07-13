---
id: T-001
kind: task
schema: content-piece-test
phase: A
risk_level: standard
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-000]
consumes:
  - "[OR-001#<short-hash>]"
  - "ALL [SRC-NNN#<short-hash>]"
acceptance_criteria:
  - "Section-level scan completed across every registered source: filenames, first 20 lines, section headers. Bodies NOT read at this step (T-002 interview is the deep-content pass)."
  - "Outcome: ANCHOR (central_angle_supplied=true; agent confirms supplied angle is supported by corpus, OR proposes a sharpening with operator approval), or SURFACE (central_angle_supplied=false; agent applies default_lens to surface 2-3 candidate angles each anchored to specific sources)."
  - "Operator confirms the angle (or supersede) before T-002 begins."
---

# Task T-001: Corpus Scan with Central-Angle Confirmation OR Default-Lens Application

## Objective

After T-000 registers every source, the agent reads section-level summaries (filename + first 20 lines + section headers — NOT bodies) and either:

- **ANCHOR mode** (when `OR-001.central_angle_supplied: true`): confirms the supplied angle (DEC-002) is supported by the corpus. If the corpus signal suggests a sharper or adjacent angle, surface it as a refinement candidate. Operator confirms or supersedes DEC-002.

- **SURFACE mode** (when `OR-001.central_angle_supplied: false`): applies `OR-001.default_lens` to the corpus to surface 2-3 candidate angles. Each candidate is anchored to specific sources by ID. Operator picks one or supersedes with their own.

## Why this exists

Inherited from report-synthesis T-001 (purpose-fit corpus scan). The pattern: don't let bootstrap-time framing lock in an angle the corpus does not actually support. For piece work, the same pressure applies — an X article expanded into a Substack longform should anchor to what the original article actually said, not what the agent imagines it said.

## Step-by-Step Instructions

1. Read OR-001. Note `central_angle_supplied`, `default_lens`, `voice_anchor`. If `central_angle_supplied: true`, also read DEC-002 (central angle).
2. List every `source` artifact registered in T-000.
3. For each source:
   - Read source.title, source_type, weight, author, date.
   - Open the file at source.file_path. Read **only** the first 20 lines and any section headers (lines starting with `#`, `##`, `###`). Close the file.
4. Build a corpus signal table in your working notes — for each source, what topic clusters appear, what stance the source takes, what is named or claimed.
5. **ANCHOR mode** (if central_angle_supplied: true):
   - Cross-reference the signal table with DEC-002.body. Confirm at least one source carries the angle's load.
   - If no source carries the angle's load: this is a thinness signal — surface to operator that the corpus does not support the supplied angle, and ask whether to acquire more sources or to re-scope the angle.
   - If sources carry it cleanly: confirm. If sources suggest a sharper angle: surface the sharpening candidate to operator with anchored source IDs.
6. **SURFACE mode** (if central_angle_supplied: false):
   - Apply OR-001.default_lens to the corpus signal. Each surfaced angle must be anchored to specific source IDs.
   - Surface 2-3 candidate angles, each one sentence, each anchored.
   - Treat zero-anchor candidates as a thinness signal (the lens does not find traction in this corpus); refuse-and-stop is on the table.
7. Present the outcome to the operator. Operator answers:
   - **Confirm** — DEC-002 stands. Record explicit confirmation in the task working log.
   - **Refine** — agent runs `hw add decision` for DEC-NNN with `reverses: DEC-002` and the refined central angle.
   - **Defer** — operator wants to spot-read a specific source body before deciding. Agent reads the requested body and re-presents.
8. Answer @@SCAN markers.

## Specific guidance

**Do** anchor every surfaced or confirmed angle to specific source IDs. *"X article + originating tweet support the angle: '<operator's stated angle, one sentence>'"* is anchored. *"This is about AI productivity"* is generic and fails.

**Do NOT** read source bodies at this step. Section headers + first 20 lines is the budget; reading bodies bleeds T-002's interview content-read pass into T-001 and produces over-fit framing.

**Do** treat zero-anchor outcomes as the high-leverage finding. If the corpus genuinely does not support what bootstrap declared, surface it and let the operator decide.

## Completion Report

- **Mode:** ANCHOR | SURFACE
- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [SRC-001#…] through [SRC-NNN#…]
- **SCAN markers answered:** <count>
- **Outcome (ANCHOR):** confirmed / sharpened-with-supersede / corpus-doesn't-support-angle
- **Outcome (SURFACE):** 2-3 candidate angles surfaced — operator picked <N> / supersede recorded as DEC-NNN
- **Recommended follow-up:** "Proceed to T-002 (interview) with confirmed central angle."
