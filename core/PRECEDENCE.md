# Mechanism: Precedence — Tiered Rule Resolution

> **Audit trace:** D1-D6, D11-D12, E3

## The Problem It Solves

Projects accumulate rules from multiple sources — legal constraints, regulatory scope, technical limits, style guidelines, external methodologies. When rules conflict, workers have to guess which one wins. Guessing produces silent failures. The Precedence mechanism establishes an explicit hierarchy: higher tiers override lower tiers, and the hierarchy is declared once in a single reference file.

## How It Works

### The Reference File

Each project gets a single `00-REFERENCE-rules.md` that contains all cross-cutting rules organized by precedence tier. Workers read this file before every task. When two rules conflict, the higher tier wins — no judgment call required.

```markdown
# 00-REFERENCE-rules.md — [Project Name]

## Precedence Order
When rules conflict, higher tiers override lower tiers.
Workers must check Tier 1 first.

### Tier 1: [NON-NEGOTIABLE] (absolute — never override)
[Rules that cannot be broken under any circumstances]

### Tier 2: [SCOPE/REGULATORY] (overrides technical and style)
[Rules from external authorities — regulatory, contractual, scope limits]

### Tier 3: TECHNICAL (overrides style)
[Platform constraints, tool limits, format requirements]

### Tier 4: STYLE (lowest precedence)
[Methodology, voice, tone, formatting preferences]
```

### Default Tier Names

The four tiers have default names that work across most domains. They can be renamed in `config-skeleton.yaml`:

| Tier | Default Name | Purpose | Examples |
|---|---|---|---|
| 1 | NON-NEGOTIABLE | Rules that cannot be broken regardless of context | Legal constraints, safety requirements, ethical boundaries |
| 2 | SCOPE/REGULATORY | External constraints that govern the work | Regulatory rules, contractual limits, white-label requirements, data handling |
| 3 | TECHNICAL | Platform and tool constraints | Image dimensions, character limits, API constraints, URL standards |
| 4 | STYLE | Preferences for tone, voice, and methodology | Copywriting frameworks, reading level targets, proof-over-promise |

Some domains may need more or fewer tiers. A safety-critical domain (nuclear, aviation) might add a "Tier 0: SAFETY" above all others. A creative agency might collapse tiers 1-2 into a single "CONSTRAINTS" tier. Empty tiers are valid — not every project has rules at every level. The mechanism is the tiered hierarchy — the specific tiers are configurable.

### The Banned/Replacement Table

For domains with prohibited language (regulated industries, brand guidelines), the reference file includes a table mapping banned phrases to safe replacements:

```markdown
| Banned Phrase | Safe Replacement | Tier | Why |
|---|---|---|---|
| [prohibited phrase] | [approved alternative] | [tier] | [reason] |
```

This table is optional. Not all domains need it. When present, workers check it before any output that includes language (copy, documentation, communications).

### Framework Integration Pattern

External methodologies (copywriting frameworks, design systems, coding standards, etc.) integrate at four layers:

1. **As reference knowledge** — A standalone document in the project folder.
2. **As rules in the reference file** — Codified as Tier 4: STYLE rules.
3. **As constraints in the worker prompt** — A rule in WORKER-PROMPT.md: "Apply the methodology specified in the reference file."
4. **As patterns in individual tasks** — Each task uses framework formulas explicitly in its instructions.

Loading the methodology at every layer makes it impossible for the AI to forget or deprioritize it. The methodology itself is a configuration choice — the integration pattern is universal.

### Why a Single File

Multiple reference files create ambiguity. If `legal-rules.md` says one thing and `style-guide.md` says another, the worker has to figure out which file wins. A single consolidated file with explicit tiers eliminates this failure mode entirely.

If the reference content is large, use sections within the file rather than splitting into separate files.

### Worker Behavior

The worker prompt includes a rule: "Check Tier 1 rules before any output." This means even if a lower-tier rule (e.g., a style guideline) produces something that sounds good, the worker must verify it doesn't violate a higher-tier rule (e.g., a legal constraint).

If tiers conflict and the worker can't determine which applies, the escalation protocol activates (see Atomicity — Escalation Protocol).

## Relationship to Other Mechanisms

- **Lock** determines which project's reference file is active.
- **Atomicity** provides the task-level enforcement of precedence rules.
- **Dependency** may be affected when rule conflicts invalidate assumptions.
- **Memory Pipeline** may surface new rules that need to be added to the reference file with appropriate tier placement.
