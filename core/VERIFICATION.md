# Mechanism: Verification — Evidence-Based Completion

## The Problem It Solves

Tasks get marked "done" without evidence they are actually done. Verification claims are prose, not structured. There is no before/after comparison. Regressions in previously-completed work are invisible until a downstream task fails. The executor says "looks good" and moves on. The planner trusts the claim. The operator discovers the problem three tasks later.

This is not a discipline problem. It is a structural one. If the system does not require evidence, evidence is optional. If evidence is optional, it will be skipped under time pressure.

---

## How It Works

Verification has six components. The first two are foundational (every task uses them). The remaining four are contextual (used when applicable).

---

### 1. Verification Checklist (Foundational)

Every task file includes a verification checklist. This is not new — v3 had checklists. What changes in v4 is the standard: checklist items must be **observable and specific**.

**Bad checklist item:** "Page works correctly."

**Good checklist item:** "Landing page loads in under 3 seconds on mobile (test via PageSpeed Insights or equivalent)."

**Bad:** "Tests pass."

**Good:** "Run `npm test` — all 47 tests pass, exit code 0."

The rule: if an executor cannot determine pass/fail without judgment, the item is too vague. Rewrite it.

The checklist lives in the task file, in the `## Verification Checklist` section. See `templates/task.md` for the format.

---

### 2. Evidence Trail (Foundational)

When completing verification checklist items, the executor records **what was checked and what happened** — not just a checkmark.

The evidence trail lives in the task file, in the `## Evidence Trail` section, using this format:

```markdown
## Evidence Trail

| Check | Method | Result | Pass |
|---|---|---|---|
| Landing page loads < 3s | PageSpeed Insights mobile test | 2.1s load time, score 94 | Yes |
| No Tier 1 violations | Scanned all copy against banned phrases table | 0 matches found | Yes |
| Email subject < 50 chars | Character count | "Your next step is waiting" = 29 chars | Yes |
```

**Why a table instead of checkmarks:** A checkmark proves the executor thought about the item. An evidence trail proves the executor verified it and records what they found. When the planner reviews completed work, evidence trails let them verify the verification — without re-running every check.

Evidence trails are mandatory for every task. The executor fills them in during the verification step. If a check cannot be performed (e.g., the tool required is unavailable), the executor records "Unable to verify — [reason]" in the Result column and "N/A" in Pass. The planner decides how to handle unverifiable items.

---

### 3. Baseline-After Pattern (Contextual)

For tasks that **modify existing state** (editing a page, refactoring code, updating a configuration), capture the baseline before modification. After task completion, the evidence trail includes the before and after.

**When to use:** Any task where the deliverable is a change to something that already exists, not a net-new creation.

**How it works:**

1. Before starting the task, the executor captures the current state of the thing being modified. This goes in the task file under `## Baseline`.
2. After completing the task, the evidence trail includes a comparison row:

```markdown
| Headline matches spec | Before: "Get More Leads" / After: "Stop Losing Clients to Bad Follow-Up" | Matches approved copy in Task 01 output | Yes |
```

**Why this matters:** Without a baseline, the planner cannot tell whether the executor changed the right thing, changed too much, or introduced unintended side effects. The baseline-after pattern makes the delta visible.

This section is optional in the task template. The planner adds it when authoring tasks that modify existing state. Net-new creation tasks skip it.

---

### 4. Verification Checkpoint (Contextual)

The Verification Checkpoint is the mandatory three-question gate for new projects. It is defined in HARNESS.md under "Bootstrap Protocol" and is the first place Verification appears in any project lifecycle.

**Additionally**, the Verification Checkpoint is re-triggered when:
- A discovery invalidates a core assumption of the project (the planner re-presents the affected scope for confirmation).
- A phase checkpoint is reached (the planner reviews all completed work in the phase before opening the next phase).
- The operator requests a mid-project review ("Status check" followed by "Does this still match your intent?").

The checkpoint is not a mechanism the executor uses. It is a planner-level gate.

---

### 5. The Ratchet Principle (Contextual)

Improvements are kept. Regressions discard the completion claim.

**How it works in the harness:**

A completed task that introduces a regression in a previously-completed task is **not actually complete**. The Dependency mechanism (TASK-STATE.yaml) tracks output hashes and assumptions. When a newly-completed task's output conflicts with a prior task's output or invalidates its assumptions:

1. The planner flags the conflict.
2. The newly-completed task's status moves from `complete` back to `blocked`.
3. The blocking reason is documented.
4. The executor must resolve the regression before the task can be re-completed.

**The principle:** The project can only move forward. A task that moves it backward is not done, regardless of whether its own checklist passes.

This integrates with the Dependency mechanism — it is not a separate tracking system. The planner enforces the ratchet during review by checking whether newly-completed work is consistent with previously-completed work.

---

### 6. Risk Classification (Contextual)

Not all tasks carry the same risk. A config tweak and an auth system change should not require the same verification rigor.

Tasks can be tagged with a risk level in their YAML frontmatter:

```yaml
risk_level: standard | elevated | critical
```

| Risk Level | When to Use | Verification Requirements |
|---|---|---|
| **standard** | Routine tasks, additive content, config changes | Verification checklist + evidence trail |
| **elevated** | Tasks modifying existing deliverables, cross-task dependencies, tasks touching multiple outputs | Checklist + evidence trail + baseline-after pattern |
| **critical** | Tasks involving compliance, security, legal, financial, or irreversible changes | Checklist + evidence trail + baseline-after + planner review before marking complete |

**Default is `standard`** if not specified. The planner sets the risk level when authoring tasks. The executor follows the verification requirements for the assigned level.

---

### 7. Pushback Protocol (Contextual)

Before executing a task, the executor evaluates whether the instructions make sense in the current context. If the task would:

- **Conflict** with existing completed work
- **Rest on a false assumption** (e.g., depends on something that has changed)
- **Introduce unnecessary complexity** when a simpler approach exists
- **Violate** a precedence rule that the task instructions don't account for

...the executor should **push back** rather than blindly proceeding.

**How to push back:**

1. STOP before executing.
2. Document the concern in the Post-Task Discovery Capture section.
3. Set task status to `blocked`.
4. Report the specific concern to the planner.

This upgrades the existing Escalation Protocol in ATOMICITY.md. The difference: Escalation is reactive (the executor hits a problem during execution). Pushback is proactive (the executor identifies a problem before execution begins).

Pushback is not defiance. It is quality control. An executor that blindly executes a task with a known problem is less valuable than one that flags the problem first.

---

## Relationship to Other Mechanisms

| Mechanism | How Verification Interacts |
|---|---|
| **Atomicity** | Every task file has a verification checklist and evidence trail section. The executor fills both before marking the task complete. |
| **Dependency** | The ratchet principle uses output hashes and assumption tracking from the Dependency engine to detect regressions. |
| **Precedence** | Critical risk classification items (compliance, legal, security) are often Tier 1 rules. Verification ensures Tier 1 compliance is proven, not assumed. |
| **Memory** | Verification failures generate discoveries. A check that repeatedly fails across tasks becomes a candidate for a learning rule. |
| **Lock** | No direct interaction. Lock prevents scope drift; Verification prevents completion drift. |

---

## What Verification Is NOT

- **Not automated testing.** The harness does not run scripts or make API calls. Verification is the executor checking and recording. If automated checks are available (test suites, linters, validators), the executor runs them and records the results in the evidence trail.
- **Not a quality gate that blocks all progress.** Standard-risk tasks need a checklist and evidence trail. That's lightweight. Only critical-risk tasks require planner review before completion.
- **Not perfection enforcement.** A task can pass verification with known limitations — as long as those limitations are documented in the evidence trail and the planner accepts them.
