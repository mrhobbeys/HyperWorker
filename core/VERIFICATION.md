# Mechanism: Verification — Evidence-Based Completion

## The Problem It Solves

Tasks get marked "done" without evidence they are actually done. Verification claims are prose, not structured. There is no before/after comparison. Regressions in previously-completed work are invisible until a downstream task fails. The executor says "looks good" and moves on. The planner trusts the claim. The operator discovers the problem three tasks later.

This is not a discipline problem. It is a structural one. If the system does not require evidence, evidence is optional. If evidence is optional, it will be skipped under time pressure.

---

## How It Works

Verification has eight components. The first two are foundational (every task uses them). The remaining six are contextual (used when applicable).

---

### 1. Verification Checklist (Foundational)

Every task file includes a verification checklist. This is not new — v3 had checklists. What changes in v4 is the standard: checklist items must be **observable and specific**.

**Bad checklist item:** "Page works correctly."

**Good checklist item:** "Landing page loads in under 3 seconds on mobile (test via PageSpeed Insights or equivalent)."

**Bad:** "Tests pass."

**Good:** "Run `npm test` — all 47 tests pass, exit code 0."

The rule: if an executor cannot determine pass/fail without judgment, the item is too vague. Rewrite it.

The checklist lives in the task file, in the `## Verification Checklist` section. See `templates/task-template.md` for the format.

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

### 3. Read-Back Verification (Contextual)

For tasks that modify external state (a live platform field, a remote config, a saved draft), the executor must read the changed value back from the source of truth after the write operation completes and record it in the Evidence Trail.

**When to use:** Any task where the deliverable is a persisted change to an external system (web UI edits, API configuration, CMS updates, platform profile changes).

**Rule:** A Save is not complete until it has been read back. The Evidence Trail must contain a post-save row showing the field's value *as read from the platform* after the write.

```markdown
| Field persisted correctly | Re-read headline field after Save | "Fast onboarding for growing teams" | Yes |
```

**Why this matters:** Silent save failures are among the most common platform-automation bugs. React state that doesn't commit, modals that dismiss without firing the submit handler, and permission errors that surface as visual confirmation without server persistence all produce false-positive completion claims. The cost of a read-back is low. The cost of an undetected silent failure is a task marked complete when nothing changed.

---

### 4. Baseline-After Pattern (Contextual)

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

### 5. Verification Checkpoint (Contextual)

The Verification Checkpoint is the mandatory three-question gate for new projects. It is defined in HARNESS.md under "Bootstrap Protocol" and is the first place Verification appears in any project lifecycle.

**Additionally**, the Verification Checkpoint is re-triggered when:
- A discovery invalidates a core assumption of the project (the planner re-presents the affected scope for confirmation).
- A phase checkpoint is reached (the planner reviews all completed work in the phase before opening the next phase).
- The operator requests a mid-project review ("Status check" followed by "Does this still match your intent?").

The checkpoint is not a mechanism the executor uses. It is a planner-level gate.

---

### 6. The Ratchet Principle (Contextual)

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

### 7. Risk Classification (Contextual)

Not all tasks carry the same risk. A config tweak and an auth system change should not require the same verification rigor.

Tasks can be tagged with a risk level in their YAML frontmatter:

```yaml
risk_level: standard | elevated | critical
```

| Risk Level | When to Use | Verification Requirements |
|---|---|---|
| **standard** | Routine tasks, additive content, config changes | Verification checklist + evidence trail |
| **elevated** | Tasks modifying existing deliverables, cross-task dependencies, tasks touching multiple outputs | Checklist + evidence trail + baseline-after pattern. **If output is end-user-facing content:** three failure scenarios generated and recorded. |
| **critical** | Tasks involving compliance, security, legal, financial, or irreversible changes | Checklist + evidence trail + baseline-after + planner review before marking complete. **If output is end-user-facing content:** three failure scenarios generated and recorded. |

**Default is `standard`** if not specified. The planner sets the risk level when authoring tasks. The executor follows the verification requirements for the assigned level.

**Failure Scenario Generation (elevated/critical, end-user-facing content):**

Before marking the task complete, the executor generates three realistic scenarios in which a real end-user follows the output verbatim. Each scenario is recorded in the Evidence Trail under a dedicated row. If any scenario produces an unsafe, non-compliant, or misleading outcome, the task is set to `blocked` with the failing scenario documented.

**What counts as end-user-facing:** copy displayed to customers, partners, employees outside the project team, or any audience who will act on the output. Internal task files, planning documents, and infrastructure changes are not end-user-facing.

**Example Evidence Trail row:**

```markdown
| Failure scenario 1 | User cancels during trial, sees "You will be charged on renewal" message | Copy implies a charge happens even after cancellation — triggers support contact and erodes trust | No |
```

A single failed scenario is sufficient to block the task. Passing all three does not guarantee safety — it means no obvious failure was found, not that none exists.

---

### 8. Pushback Protocol (Contextual)

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

This is the proactive counterpart to the Escalation Protocol in `core/ATOMICITY.md` (which is reactive — triggered during execution). Pushback is triggered before execution begins.

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

- **Not automated testing.** Verification is the executor checking and recording. If automated checks exist, use them and record results in the evidence trail.
- **Not a quality gate that blocks all progress.** Standard-risk tasks need a checklist and evidence trail — that's lightweight. Only critical-risk tasks require planner review.
- **Not perfection enforcement.** Tasks can pass with known limitations if documented in the evidence trail and accepted by the planner.
