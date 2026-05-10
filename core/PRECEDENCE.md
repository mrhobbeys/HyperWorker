# Mechanism: Precedence — Tiered Rule Resolution

> Tiered rule conflict resolution remains the right primitive for "which rule wins" questions. v4.1.1's design is sound; the change in v5.0 is the substrate underneath. Rules cite typed artifacts by hash, and each tier section ends with SCAN markers that force attention restoration before state-changing actions.

---

## Hypothesis

| ID | Claim | Falsifier |
|---|---|---|
| H-P1 | Tiered rule conflict resolution with anchored citations and SCAN markers resolves rule conflicts without requiring agent judgment. | A rule conflict in active project work is not resolved by tier ordinal and forces operator intervention. |

---

## The Reference File

Each project has one `00-REFERENCE-rules.md` (file-canonical, Mutable Surface). Tiers are declared in the project schema — default names for each tier are `NON-NEGOTIABLE / SCOPE / TECHNICAL / STYLE`, but the schema overrides. Higher tier wins on conflict; the ordinal does the resolving, not the agent.

```markdown
# 00-REFERENCE-rules.md — <project-name>

## Precedence Order
When rules conflict, higher tiers override lower tiers. Tier 1 cannot be overridden.

### Tier 1: NON-NEGOTIABLE  (absolute — never override)
- <rule>  — anchored: [DEC-002#a3f9c2b1e0f4]
- <rule>
- <rule>

@@SCAN_1_1: <attention-restoration question>
@@SCAN_1_2: <attention-restoration question>

### Tier 2: SCOPE  (overrides technical and style)
- <rule>
- <rule>

@@SCAN_2_1: <attention-restoration question>

### Tier 3: TECHNICAL
- <rule>

@@SCAN_3_1: <attention-restoration question>

### Tier 4: STYLE  (lowest precedence)
- <rule>

@@SCAN_4_1: <attention-restoration question>

## Banned Tokens / Replacements

| Banned Token | Safe Replacement | Tier | Why |
|---|---|---|---|

## Canonical Facts — Do Not Normalize

| Fact | Canonical Form | Do NOT Normalize To |
|---|---|---|
```

The schema declares tiers, default rule examples, and SCAN markers. The operator fills in project-specific rules at bootstrap.

---

## Citing Typed Artifacts in Rules

A rule anchors to an artifact: `[DEC-002#a3f9c2b1e0f4]` after the rule means "this rule was set by DEC-002 at hash a3f9…". Layer 1 verification checks rule citations every time the file renders to its compressed form.

When `DEC-002` is superseded, the rule citation goes stale. Layer 1 emits `verify.layer1.fail` and the file is flagged for operator update. The rule is not auto-updated; the operator decides whether the new decision changes the rule's content.

---

## SCAN Markers

Each tier section ends with `@@SCAN_n_m: <question>` markers (n = tier ordinal, m = local index). Before any state-changing action in a task, emit a short answer to each marker via a `task.scan` event.

**Why output, not re-read.** Passive re-reading does not restore attention — the model glances at the section and continues with whatever pattern it had cached. Generating a token-by-token answer forces the model's attention back to the rule section. The pattern (from dev.to/nikolasi research thread) costs under 0.5% of context per task; the cost of a Tier 1 violation that slips through because the agent never re-anchored on the rule is far higher.

**Marker design.** Good markers have one-word or short-phrase answers and are constructed so the answer can be verified by inspection of the question's source. Examples:

| Tier | Marker | Good answer |
|---|---|---|
| 1 | `@@SCAN_1_1: List the Tier 1 banned phrase categories that apply to this task's output.` | "Income claims; fabricated testimonials; competitor disparagement." |
| 2 | `@@SCAN_2_1: Confirm draft-only applies to this task's output (yes / no / not-applicable).` | "Yes." |
| 3 | `@@SCAN_3_1: State the body word-count window for this email kind.` | "150–300." |
| 4 | `@@SCAN_4_1: Name the methodology rule that governs CTAs for this content kind.` | "One CTA per email; never split attention." |

Markers are project-specific. Each project's `rules-template.md` ships with stub markers; the operator adapts them.

**Layer 2 enforcement.** A `task.complete` event is rejected if the task is missing a `task.scan` event for any marker, recorded *before* the first state-changing event in the task. Order matters: SCAN runs before, not after, the state-changing work it prepares for. After-the-fact answers do not restore attention; they document compliance theatre.

---

## Compression and the Agent Prompt

`00-REFERENCE-rules.md` regenerates to a compressed form (`00-REFERENCE-rules.compressed.md`) on every change. The compressed file is what enters the agent's prompt. Compression preserves: code, paths, IDs, dates, hashes, version numbers, currency amounts, and quoted strings byte-for-byte. Only prose compresses.

See `core/TYPED-ARTIFACTS.md` §Compression for the deterministic transform. The agent's prompt always carries the compressed form; the operator edits the source form.

---

## Default Tier Set

The harness ships with a four-tier default. Project schemas may override.

| Tier | Default Name | Purpose |
|---|---|---|
| 1 | NON-NEGOTIABLE | Cannot be broken under any circumstances. Legal, safety, ethical. |
| 2 | SCOPE | External constraints. Regulatory, contractual, white-label, data handling. |
| 3 | TECHNICAL | Platform and tool limits. Image dimensions, character counts, format constraints. |
| 4 | STYLE | Methodology, voice, tone, formatting preferences. |

Schemas in `schemas/projects/` rename tiers for their domain (e.g., marketing-campaign uses `BRAND-ABSOLUTE / OFFER-SCOPE / PLATFORM-LIMITS / COPY-METHOD`). A schema may add a Tier 0 for safety-critical contexts; empty tiers are valid.

---

## Conflict Resolution Protocol

When two rules conflict during execution:

1. Identify both rules and their tiers from `00-REFERENCE-rules.compressed.md`.
2. Higher tier wins. Record the resolution in the completion-report's evidence trail.
3. If both rules are in the same tier, the conflict is structurally unresolved → `task.status → blocked` with `reason: tier_conflict <rule1> vs <rule2>`. The planner adjusts the rules (clarifies which is higher, splits to different tiers, or revises one).

Do not invent a resolution. Same-tier conflicts are an authoring error, not a runtime decision.

---

## Banned Tokens / Replacements

A two-column-plus table for content domains:

| Banned Token | Safe Replacement | Tier | Why |
|---|---|---|---|
| "guaranteed results" | "proven approach" | 1 | Income claim. |
| — (em dash) | , or . or ( ) | 4 | AI tell — breaks voice. |

Layer 2 acceptance-criteria evaluation includes a banned-token scan when the project's rules file declares the table. The scan is a literal substring match (case-insensitive, Unicode-NFC-normalized); a banned token in output blocks task completion.

---

## Canonical Facts — Do Not Normalize

A facts table that prevents AI normalization (e.g., "1-800-FLOWERS" → "1-800-356-9377"):

| Fact | Canonical Form | Do NOT Normalize To |
|---|---|---|
| Vanity phone | "1-800-FLOWERS" | "1-800-356-9377" |
| Date-anchored deadline | "by end of Q1 2026" | "in about 3 months" |

Layer 2 checks output for the "Do NOT Normalize To" column entries; matches block task completion.

---

## Why a Single File

Multiple reference files create ambiguity about which file's rules win. One consolidated file, with explicit tiers, eliminates the question. Large rule sets use sections within the file; they do not split into separate files.

The Mutable Surface principle applies: this file is operator-editable, file-canonical, versioned via git. The substrate does not generate it; it consumes it (compresses + cites).

---

## Relationship to Other Mechanisms

| Mechanism | Interaction |
|---|---|
| Lock | The active project's rule file is in force. |
| Atomicity | Tasks consume the compressed rules file as part of their working set. |
| Typed Artifacts | Rules cite artifacts by hash to anchor to specific decisions/findings. |
| Verification | SCAN events feed Layer 2; banned-token scan feeds Layer 2 acceptance criteria. |
