# 00-REFERENCE-rules.md — [Project Name]

> **This is the single source of truth for all cross-cutting rules in this project.** Executors read this file before every task. When rules conflict, higher tiers win. Do not split rules across multiple files.

## Precedence Order

When rules conflict, higher tiers override lower tiers.
Executors must check Tier 1 first. If a lower-tier rule produces output that violates Tier 1, Tier 1 wins.

### Tier 1: [NON-NEGOTIABLE] (absolute — never override)
- [Rule 1 — e.g., "No guarantees of specific outcomes"]
- [Rule 2 — e.g., "No claims that cannot be independently verified"]
- [Rule 3]

### Tier 2: [SCOPE/REGULATORY] (overrides technical and style)
- [Scope limitation — what the project covers and does NOT cover]
- [White-label / vendor rules — names that can or cannot appear publicly]
- [Draft-only rule — if applicable: "Never publish without human review"]
- [Data handling / privacy requirements]

### Tier 3: TECHNICAL (overrides style)
- [Platform constraints — image dimensions, character limits]
- [URL canonical list]
- [API or tool constraints]
- [Format requirements per platform or system]

### Tier 4: STYLE (lowest precedence)
- [Methodology rules — e.g., framework formulas, writing patterns]
- [Voice and tone guidelines]
- [Reading level target]
- [Quality principles — e.g., "proof over promise"]

## Banned Phrases / Safe Replacements (if applicable)

| Banned Phrase | Safe Replacement | Tier | Why |
|---|---|---|---|
| [phrase] | [replacement] | [tier] | [reason] |
| [phrase] | [replacement] | [tier] | [reason] |

## Target Audience
[Who all output in this project is for — role, pain points, decision-making authority]

## Safe Claims (if applicable)
[Pre-approved language that can be used freely without additional review]

## Correct Links / URLs (if applicable)
[Canonical list of URLs. Executors paste these exactly.]

| Purpose | URL |
|---|---|
| [Main website] | [URL] |
| [Booking / CTA] | [URL] |

## Platform Specifications (if applicable)

| Platform / Use | Constraint | Format | Notes |
|---|---|---|---|
| [Platform] | [Dimensions / limits] | [Format] | [Notes] |
