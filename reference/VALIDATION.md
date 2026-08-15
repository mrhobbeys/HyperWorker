# Validation Guide — Applying v5.0 to a New Domain

> If you can stand up a project in a new domain using only the substrate, mechanisms, and a custom or default schema — without bending the harness to fit the domain — v5.0 is domain-agnostic for that domain. This document describes the validation walk.

---

## The Validation Test

Pick a domain you know well that is *not* one of the shipped default schemas (see the README schema table). Run through the steps below. Configuration-level adjustments are expected; mechanism-level changes mean v5.0 has a gap.

### Step 1: Structural Verification

1. `HARNESS.md`, `core/SUBSTRATE.md`, `core/{LOCK,ATOMICITY,TYPED-ARTIFACTS,VERIFICATION,PRECEDENCE,AUTHORITY,TOOLS}.md` readable.
2. `templates/`, `schemas/artifacts/`, `schemas/projects/`, `templates/models/` exist with documented contents.
3. `hw verify` on a fresh `.hyperworker/` returns `PASS` (an empty log still PASSes; a missing `events.jsonl` is a FAIL).

**Pass criterion.** No missing files.

### Step 2: Pick or Custom-Build a Schema

Either:

- **Use a default schema** that structurally matches your domain (not necessarily semantically). An architecture firm running a build-out might match `event-planning` for hard-deadline + physical vendors — try the structural fit first.
- **Custom-build** by scaffolding from `templates/` defaults. After the project completes, `hw schema save --from <project> --as <name>` extracts the configurable substrate as a derived schema.

**Pass criterion.** A schema (default, derived, or custom) accommodates your domain at the structural level.

### Step 3: Bootstrap

```
hw bootstrap --schema <name> --name <project-id>
```

Answer the schema's bootstrap questions. Write `OR-001` from your operator-reality answers via `hw add operating-reality`.

**Pass criterion.** Bootstrap completes; Verification Checkpoint council fires; operator confirms the council summary or addresses concerns.

### Step 4: Configure Rules

Edit `00-REFERENCE-rules.md` to populate your domain's rules at each tier. Add SCAN markers that your domain's tasks should restore attention to.

**Pass criterion.** Real conflicts in your domain resolve by tier ordinal. Empty tiers are fine; same-tier conflicts are an authoring error and should be split or re-tiered.

### Step 5: Decompose

Edit task templates (or write new ones) for your domain. Each task declares `consumes:`, `risk_level`, `required_tools`, `acceptance_criteria`.

**Pass criterion.** The frontmatter accommodates the work. If you find yourself adding a non-frontmatter field repeatedly, propose a schema extension.

### Step 6: Execute One Task

Load the executor prompt (`templates/executor-prompt.md`), invoke a fresh agent, attach the project rules-compressed file and the task file. Let the agent complete the task fully.

**Pass criterion.** The agent stays within `consumes:` (no out-of-set reads). Recitation passes Layer 1 overlap. SCAN markers answered. Acceptance criteria evaluated. The agent emits `hw write --status complete`; Layer 2 verification runs.

### Step 7: Test Capability-Gate Routing

Declare a `required_tools` that no configured subagent provides. Confirm the harness refuses to delegate and emits `capability_gap.md`.

**Pass criterion.** No silent degradation. The gap file lists exactly which tools are missing. Operator can resolve by adjusting the agent profile or running in-line.

### Step 8: Test Council

Force a council invocation: bootstrap a critical-risk task or run `hw council <task-id>` manually.

**Pass criterion.** Each council member runs with context-asymmetric framing (sees artifact and spec, not implementer rationale). The convergence rule produces a `council.converged` or `council.escalated` event.

---

## What Failure Looks Like

| Symptom | Likely cause | Fix |
|---|---|---|
| Task frontmatter cannot express the dependency | The dependency is between artifacts, not tasks | Add the cited artifact to `consumes:`. |
| Verification fails on a task that "should" pass | Acceptance criteria too vague / not observable | Rewrite criteria as pass/fail. |
| Recitation overlap rejects a clearly-correct paraphrase | Profile band is wrong for your model | Tune `recitation_overlap_floor` / `recitation_overlap_ceiling` in the active model profile. |
| Council never converges | Convergence rule too strict for the work | Switch from `all-agree-or-escalate` to `majority-or-escalate` in `council.yaml`. |
| Capability gate refuses delegation when the agent has the tool | Agent profile `provides:` is incomplete | Add the missing capability to `.hyperworker/agents/<id>.yaml`. |
| Layer 1 citation freshness fails on every task | The cited artifact was superseded; downstream `consumes:` not updated | Re-render projections (`hw project`) and update `consumes:` to current hashes. |
| The executor reads files outside `consumes:` | Hermetic working set is not enforced by the agent runtime | Verify the executor-prompt boundary section is loaded; consider per-model profile adjustments. |

The first three are configuration. The rest indicate either mis-authoring or, rarely, a real harness gap. Real harness gaps belong in `reference/FAILURE-MODES.md`.

---

## Recording Validation Results

```markdown
# Validation: <Domain>
**Date:** <YYYY-MM-DD>
**Validator:** <name / role>
**Harness version:** 6.0.0

## Schema used
<default name | custom>

## Configuration adjustments
<what had to change from defaults and why>

## Schema extensions added
<additional artifact fields, additional task kinds, etc.>

## Mechanism gaps
<any mechanism that did not accommodate the domain>

## Council outcomes
<how often council converged on first pass; how often it escalated>

## Capability-gate refusals
<count and pattern>

## Overall assessment
<Pass | Pass with modifications | Fail>
<If modifications were needed, were they configuration-level or mechanism-level?>
```

Configuration-level changes are healthy and expected. Mechanism-level changes mean v5.0 has a gap; surface it in an issue with the failure mode and a falsifiable hypothesis for what would close it.
