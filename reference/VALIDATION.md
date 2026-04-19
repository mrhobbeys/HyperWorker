# Validation Guide — Applying the Harness to a New Domain

## Purpose

This document describes how to validate that the harness works in a domain other than the one it was originally developed in. If you can stand up a project in a new domain using only the core mechanisms and templates — without importing domain-specific assumptions — the harness is domain-agnostic.

## The Validation Test

Pick a domain you (or a test user) know well that is NOT the domain the harness was built in. Run through this checklist:

### Step 1: Structural Verification

1. Confirm `HARNESS.md` exists and is readable.
2. Confirm the folder structure matches the layout declared in HARNESS.md's "Truth Layer vs Mutable Surface" section.
3. Copy `templates/config-skeleton.yaml` to your harness root as `config.yaml`.

**Pass criterion:** The manifest accurately describes the harness structure. No missing files.

### Step 2: Configure

1. Fill in every field in `config.yaml`. Pay attention to:
   - **Precedence tier names** — Do the default four tiers map to your domain? If not, rename or add tiers.
   - **Scope taxonomy** — Does the default hierarchy (Universal / [Vertical] / Client / Engagement) fit? If not, define your own.
   - **Memory cadence** — Is quarterly review appropriate, or do you need monthly?
   - **Worker behavior** — Is draft-only appropriate, or does your domain auto-publish?
   - **Verification checkpoint** — Leave enabled unless you have a specific reason to disable.

**Pass criterion:** Every config field can be filled without referencing another domain's values.

### Step 3: Create a Project

1. Use `templates/project-template.md` to define a real project in the new domain.
2. Fill in Objective, Scope (included and excluded), Key Constraints, Dependencies, and Completion Criteria.

**Pass criterion:** The template accommodates the project naturally. No fields are irrelevant or missing.

### Step 4: Build the Reference File

1. Use `templates/rules-template.md` to create `00-REFERENCE-rules.md`.
2. Populate all four tiers with real rules from the new domain.
3. Fill in the banned phrases table (if applicable), target audience, and platform specs.

**Pass criterion:** The precedence tiers resolve real conflicts in the new domain. If a tier is empty, consider whether the tier should be removed or if the project genuinely has no rules at that level.

### Step 5: Verification Checkpoint

Present the scaffolded project to the operator (or test user) and ask:

1. "Does this project description match your intent?" → Show PROJECT.md
2. "Do these priority tiers make sense?" → Show 00-REFERENCE-rules.md
3. "Does this task breakdown look right?" → Show TASK-STATE.yaml

**Pass criterion:** The checkpoint catches at least one assumption mismatch OR the operator confirms all three without confusion. Either outcome is valid signal.

### Step 6: Decompose into Tasks

1. Break the project into 5-10 tasks using `templates/task-template.md`.
2. Build `TASK-STATE.yaml` with real dependencies and assumptions.
3. Ensure at least one task has a cross-task dependency and at least one phase has a checkpoint.

**Pass criterion:** The task format accommodates the work. Dependencies are expressible. Assumptions are capturable.

### Step 7: Execute One Task

1. Load the worker prompt (`templates/worker-prompt-template.md`) into a worker session.
2. Attach the reference file and one task file.
3. Let the worker execute the task fully.
4. Review the completion report and any discoveries.

**Pass criterion:** The worker stays in scope, follows precedence, and uses the escalation/discovery protocols appropriately. The worker does not confuse harness files with project files.

### Step 8: Test the Memory Pipeline

1. Introduce a simulated discovery (a failed assumption or unexpected platform behavior).
2. Capture it in DISCOVERIES.md using the entry format.
3. Promote it to LEARNINGS.md with appropriate scope tag and lifecycle.

**Pass criterion:** The memory formats accommodate the new domain's knowledge without modification.

## What Failure Looks Like

- **Template gaps:** A template field is missing that the new domain needs (→ add the field).
- **Hardcoded assumptions:** A mechanism assumes something that isn't true in the new domain (→ make it configurable).
- **Precedence mismatch:** The four default tiers don't map (→ add guidance for custom tier hierarchies).
- **Scope taxonomy mismatch:** The default scope levels don't fit (→ improve the taxonomy documentation).
- **Memory categories mismatch:** The default learning categories don't cover the new domain's knowledge types (→ expand the category list).
- **Boundary confusion:** The worker treated harness files as project files or vice versa (→ improve manifest clarity or worker prompt framing).
- **Checkpoint failure:** The verification checkpoint didn't catch an assumption mismatch that caused problems later (→ add more checkpoint criteria).
- **Structural misfit:** The project requires parallel tasks, multiple operators, or non-sequential workflows that the harness can't accommodate (→ document in FAILURE-MODES.md).

## Recording Validation Results

Document the validation in a separate file:

```markdown
# Validation: [Domain Name]
**Date:** [YYYY-MM-DD]
**Validator:** [Name/role]
**Harness version:** 3.1

## Config Adjustments Needed
[What had to change from defaults and why]

## Template Modifications
[Any template fields added, removed, or renamed]

## Mechanism Gaps
[Any mechanism that didn't accommodate the domain]

## Checkpoint Results
[What the verification checkpoint caught or confirmed]

## Boundary Clarity
[Did the worker correctly distinguish harness files from project files?]

## Overall Assessment
[Pass / Pass with modifications / Fail]
[If modifications were needed, were they configuration-level or mechanism-level?]
```

Configuration-level adjustments are expected and healthy. Mechanism-level changes mean the harness has a gap that should be addressed in a future version.
