# HyperWorker v4.0.1 — Context Optimization Plan

## Context

HyperWorker exists to help AI agents stay on task without losing context. But the harness files themselves consume context tokens. An analysis of v4.0 measured the full harness at ~14,975 tokens. The Routing Table already prevents worst-case loading (executor loads ~2,369 tokens vs 14,975 — an 84% reduction), but three gaps remain:

1. **No role-based routing** — the Routing Table doesn't distinguish planner vs executor workflows, leading to over-loading
2. **No context recovery path** — when an agent loses context mid-project, there's no guidance on minimal re-orientation (agents reload HARNESS.md at ~2,919 tokens when they only need ~900 tokens of state files)
3. **Stale example + prose redundancy** — ATOMICITY.md contains a pre-v4 task anatomy example missing `risk_level`, `Baseline`, and `Evidence Trail`, and several mechanism files have compressible explanatory prose

These are refinements to existing mechanisms (the Routing Table, the mechanism docs), not new mechanisms. **Version: v4.0.1 (patch).**

## Analysis Summary

| Metric | Value |
|--------|-------|
| Full harness token cost (all core + templates) | ~14,975 tokens |
| Typical executor task cost (via Routing Table) | ~2,369 tokens |
| HARNESS.md alone | ~2,919 tokens |
| Context recovery without guidance (reload HARNESS.md) | ~2,919 tokens |
| Context recovery with guidance (state files only) | ~900 tokens |
| Direct token waste from redundancy/prose | ~480 tokens |
| Routing Table effectiveness (current) | 84% reduction vs full load |

## Changes

### Change 1: Enhanced Routing Table (HARNESS.md) — HIGH PRIORITY

Replace the current 8-row Routing Table with a role-aware version adding a **Role** column (Planner/Executor/Either) and two new rows:

**Proposed table:**

```markdown
| Operation | Role | Read These Files |
|---|---|---|
| Scaffolding a new project | Planner | HARNESS.md → templates/* |
| Executing a task | Executor | 00-REFERENCE-rules.md → task file → templates/executor-prompt.md |
| Reviewing completed work | Planner | TASK-STATE.yaml → completed task files in done/ → core/VERIFICATION.md (criteria only) |
| Resuming a project (context recovery) | Planner | active_project.md → PROJECT.md → TASK-STATE.yaml → 00-REFERENCE-rules.md |
| Resolving a blocked task | Planner | task file → TASK-STATE.yaml → relevant core/*.md |
| Managing memory | Planner | core/MEMORY.md → memory/DISCOVERIES.md → memory/LEARNINGS.md |
| Resolving rule conflicts | Planner | core/PRECEDENCE.md → 00-REFERENCE-rules.md |
| Verifying completion | Executor | task's verification checklist → evidence trail (within task file) |
| Understanding a mechanism | Either | The specific core/*.md file for that mechanism |
| Validating in a new domain | Planner | reference/VALIDATION.md → templates/ → case-studies/ |
```

Key changes vs current:
- Added **Role** column (Planner / Executor / Either)
- Added **"Resuming a project"** row — the context recovery path (~2,000 token savings per recovery)
- Added **"Resolving a blocked task"** row — currently missing
- Removed HARNESS.md from "Reviewing completed work" (~2,919 token savings per review)
- Simplified "Verifying completion" to point within task file

**File**: `HARNESS.md` (Routing Table section)
**Token impact**: +30 tokens to table, prevents 500-2,000 tokens of unnecessary loading per event
**Risk**: Low — additive refinement

### Change 2: Fix Stale Task Anatomy in ATOMICITY.md — HIGH PRIORITY (correctness)

The task file code block example (lines ~14-52) is missing v4 fields (`risk_level`, `## Baseline`, `## Evidence Trail`). An agent reading ATOMICITY.md to understand task structure gets the wrong format. This is a correctness bug.

**Changes:**
- Replace 39-line stale code block with brief reference to `templates/task-template.md`
- Compress "Key Design Principles" prose (~110 words) into bullet list (~60 words)
- Compress "Content Delivery Modes" prose (~130 words) into 2-row table (~50 words)
- Add cross-reference in Escalation Protocol pointing to `core/VERIFICATION.md` for Pushback Protocol

**File**: `core/ATOMICITY.md`
**Token savings**: ~290 tokens
**Risk**: Low — correctness fix + lossless compression

### Change 3: Compress VERIFICATION.md Explanatory Prose — MEDIUM PRIORITY

- Convert "What Verification Is NOT" to single-line-per-item format (not paragraph bullets)
- Replace escalation re-explanation in Pushback Protocol with cross-reference to ATOMICITY.md

**File**: `core/VERIFICATION.md`
**Token savings**: ~80 tokens
**Risk**: Very low

### Change 4: Compress MEMORY.md Platform Integration — LOW PRIORITY

Convert "Integration with Platform-Native Memory" prose (~80 words) to 2-row comparison table:

```markdown
| System | Purpose | Lifecycle |
|---|---|---|
| Platform memory | How the operator works (preferences, corrections) | Platform-managed |
| Harness memory | What the business has learned (domain knowledge, failures) | File-managed, cross-project |
```

**File**: `core/MEMORY.md`
**Token savings**: ~55 tokens
**Risk**: Very low

### Change 5: Compress PRECEDENCE.md "Why a Single File" — LOW PRIORITY

Reduce ~65 word paragraph to one sentence: "Multiple reference files create ambiguity about which file's rules win — a single consolidated file with explicit tiers eliminates this entirely."

**File**: `core/PRECEDENCE.md`
**Token savings**: ~55 tokens
**Risk**: Very low

## Non-Changes (explicitly excluded)

| File | Why Not |
|------|---------|
| VISION.md | Never loaded during execution |
| README.md | Human-facing, not agent-consumed |
| executor-prompt.md | Already tight — every word is operational |
| task-template.md | Scaffolding instructions disappear after instantiation |
| config-skeleton.yaml | Comments help during one-time configuration |
| "Relationship to Other Mechanisms" sections | Loaded individually, provide local navigation |
| "The Problem It Solves" sections | ~55 words each, minimal cost, useful context during conflict resolution |
| reference/*.md | Low-frequency documents, explanatory nature appropriate |
| case-studies/ | Not auto-loaded during execution |
| Boundary rule mentions (HARNESS.md + executor-prompt) | Different audiences, different times — not redundancy |
| Tier 1 check mentions (4 locations) | Intentional reinforcement, never loaded together |

## Token Budget

| Category | Savings |
|----------|---------|
| Direct file compression (Changes 2-5) | ~480 tokens |
| Indirect: context recovery path avoids HARNESS.md reload | ~2,000 tokens per recovery event |
| Indirect: review path avoids HARNESS.md reload | ~2,919 tokens per review pass |
| Net table addition | +30 tokens |

## Commit Strategy

Single commit:
- All five file changes
- CHANGELOG.md v4.0.1 entry

## Files to Modify

1. `HARNESS.md` — Routing Table section
2. `core/ATOMICITY.md` — task anatomy example, prose compression, pushback cross-ref
3. `core/VERIFICATION.md` — "What Verification Is NOT", pushback preamble
4. `core/MEMORY.md` — platform integration section
5. `core/PRECEDENCE.md` — "Why a Single File" section
6. `CHANGELOG.md` — v4.0.1 entry

## Verification

After implementation:
1. Routing Table has Role column and both new rows (Resuming, Resolving blocked)
2. ATOMICITY.md references `templates/task-template.md` instead of inline stale code block
3. No information loss in compressed sections (same content, fewer words)
4. All v4.0 sweep checks still pass (no stale refs reintroduced)
