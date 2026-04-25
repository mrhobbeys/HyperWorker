# 00-REFERENCE-rules.md — <Project Name>

> File-canonical (Mutable Surface). Operator edits this file directly. The compressed projection (`00-REFERENCE-rules.compressed.md`) is what the agent prompt loads.

## Precedence Order

When rules conflict, higher tiers override lower tiers. Tier 1 cannot be overridden. Same-tier conflicts are an authoring error and block tasks.

### Tier 1: NON-NEGOTIABLE  (absolute — never override)

- <rule>
- <rule>
- <rule>

@@SCAN_1_1: <attention-restoration question whose answer touches a Tier 1 category>
@@SCAN_1_2: <attention-restoration question>

### Tier 2: SCOPE  (overrides technical and style)

- <rule>
- <rule>

@@SCAN_2_1: <attention-restoration question>

### Tier 3: TECHNICAL  (overrides style)

- <rule>

@@SCAN_3_1: <attention-restoration question>

### Tier 4: STYLE  (lowest precedence)

- <rule>

@@SCAN_4_1: <attention-restoration question>

## Banned Tokens / Replacements (optional)

| Banned Token | Safe Replacement | Tier | Why |
|---|---|---|---|

## Canonical Facts — Do Not Normalize (optional)

| Fact | Canonical Form | Do NOT Normalize To |
|---|---|---|

## Target Audience (optional)

<who all output in this project is for>

## Correct Links / URLs (optional)

| Purpose | URL |
|---|---|

## Platform Specifications (optional)

| Platform / Use | Constraint | Format | Notes |
|---|---|---|---|
