# Mechanism: Memory Pipeline — Discovery to Learning Lifecycle

> **Audit trace:** A3, B5, B7, C12, E6, F1-F5, F8-F12

## The Problem It Solves

AI systems don't learn from project to project by default. Discoveries made during execution — failed assumptions, platform behaviors, domain constraints — are lost when the session ends. The Memory Pipeline captures raw findings, validates them through a human gate, promotes them to operating knowledge, and enforces decay so stale rules don't silently influence future decisions.

## How It Works

### Architecture: Two Files + Lifecycle

```
memory/
├── DISCOVERIES.md         # Raw capture — awaiting human validation
├── LEARNINGS.md           # Validated knowledge with lifecycle fields
└── LEARNINGS-ARCHIVE.md   # Aged entries — searchable, off critical path
```

Memory lives outside individual project folders because knowledge compounds across projects.

### File 1: DISCOVERIES.md — The Intake

Every unexpected finding, failed assumption, platform behavior, or domain insight gets captured here FIRST. Nothing becomes a learning automatically. This is the human gate that prevents invisible bias.

```markdown
## DISC-[YYYY-MM-DD]-[NNN]
- **Date:** [YYYY-MM-DD]
- **Source:** [Task ID, manual observation, external feedback, etc.]
- **Context:** [What were you doing when this was discovered]
- **Discovery:** [What you found — be specific]
- **Assumption Affected:** [Which assumption was wrong or missing]
- **Suggested Rule:** [What rule would prevent this in the future]
- **Why It Matters:** [Impact if not captured — rework, risk, wrong output]
- **Status:** Open
- **Promoted To:** [blank until validated]
```

**Entry lifecycle:** Open → Validated (promoted to LEARNINGS.md) or Archived (not a pattern).

Workers capture discoveries in the Post-Task Discovery Capture section of their task file. The orchestrator copies them to DISCOVERIES.md during the next planning session.

### File 2: LEARNINGS.md — Validated Operating Knowledge

Only discoveries that the human operator has personally validated get promoted here. Each entry carries structured metadata.

```markdown
| ID | Category | Rule | Confidence | First Observed | Last Validated | Lifecycle | Applies To | Why |
|---|---|---|---|---|---|---|---|---|
| L-001 | [Category] | [The rule, stated clearly] | High | 2026-04-12 | 2026-04-12 | ACTIVE | Universal | [Why this rule exists — the incident or decision] |
```

**Fields:**
- **ID:** Sequential identifier (L-001, L-002, etc.)
- **Category:** Domain of the learning (e.g., Legal Language, Platform Specs, Workflow, Failure Mode, Compliance, Tool Behavior)
- **Rule:** The learning stated as an actionable rule.
- **Confidence:** High / Medium / Low
- **First Observed:** When the discovery was first captured.
- **Last Validated:** When the human last confirmed this is still true.
- **Lifecycle:** ACTIVE / REFERENCE / DEPRECATED (see below).
- **Applies To:** Scope tag (see below).
- **Why:** The incident or decision that created this rule. Prevents justification decay.

### File 3: LEARNINGS-ARCHIVE.md — Cold Storage

Entries older than the archive threshold (configurable, default 12 months) are moved here. The archive is searchable but never auto-loaded into session context.

### The Lifecycle

Knowledge decays. Rules that were true six months ago may not be true now. The lifecycle enforces re-validation:

| Stage | Age Since Last Validation | Behavior |
|---|---|---|
| **ACTIVE** | 0–[review cadence] | Auto-included in orchestrator context. Workers see it through the reference file. |
| **REFERENCE** | [review cadence]–[2× review cadence] | Still in the file but not auto-loaded. Must be explicitly cited in a task or reference doc. |
| **DEPRECATED** | Beyond [2× review cadence] | Flagged for re-validation. If not re-validated within 30 days, moves to archive. |
| **ARCHIVED** | Beyond [archive threshold] | Moved to LEARNINGS-ARCHIVE.md. Off the critical path. |

Default timings: review cadence = 3 months, archive threshold = 12 months. These are configurable in `config-skeleton.yaml`.

### Scope Tags — Preventing Cross-Context Contamination

Every learning is tagged with a scope that controls where it applies:

| Scope Level | Meaning | Example |
|---|---|---|
| **Universal** | True everywhere, all contexts | "Monolithic instructions cause drift after step 5" |
| **[Vertical]-General** | True for all work in a specific vertical | "Regulatory scope for this vertical excludes X and Y" |
| **Client:[Name]** | True only for a specific client or customer | "Acme Corp prefers formal tone in all deliverables" |
| **Engagement:[ID]** | True only for a specific project | "Q2 Migration uses legacy API v2 endpoints" |

When launching a new engagement, filter LEARNINGS.md to only rows where `Applies To` matches: Universal + the relevant vertical + the specific client + the engagement. One context's lessons never silently influence another.

The scope taxonomy is configurable. The four-level hierarchy above works for service businesses with multiple clients. A product team might use: Universal / Feature:[Name] / Release:[Version]. A consulting firm might use: Universal / Industry:[Name] / Client:[Name] / Engagement:[ID].

### Justification Trails — The "Why" Field

Every learning includes a "Why" that documents the incident or decision that created it. This prevents justification decay — the phenomenon where rules outlive their rationale. After six months, the operator might not remember why L-001 exists. The "Why" field tells them.

Without "Why," deprecated rules get blindly re-validated ("it's probably still important") instead of critically assessed.

### Review Protocol

On a configurable cadence (default: quarterly):

1. Read every entry. Check Last Validated date.
2. ACTIVE entries past their review cadence → move to REFERENCE.
3. REFERENCE entries past 2× cadence → move to DEPRECATED.
4. DEPRECATED entries: re-validate (update Last Validated, move back to ACTIVE) or archive.
5. Check DISCOVERIES.md for Open entries sitting more than 30 days — promote or archive.

### Integration with Platform-Native Memory

If the AI platform has its own memory system (e.g., profile preferences, workflow corrections, session context), the harness memory is complementary, not a replacement.

- **Platform memory** = How the operator works (preferences, corrections, personal context)
- **Harness memory** = What the business has learned (domain knowledge, platform limits, compliance rules, failure patterns)

The two systems have different purposes and different lifecycles. The harness memory compounds across projects and persists across platform sessions.

## Relationship to Other Mechanisms

- **Lock** determines which project's discoveries are being captured.
- **Atomicity** provides the Post-Task Discovery Capture section that feeds the pipeline.
- **Dependency** uses learnings to validate assumptions in the task graph.
- **Precedence** may incorporate learnings as rules in the reference file.
