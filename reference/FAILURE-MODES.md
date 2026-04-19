# Failure Modes & Known Limitations

## Purpose

This document catalogs the known boundaries, limitations, and failure modes of the harness. Understanding where the system breaks helps operators avoid those edges and helps future versions address them.

## Scaling Boundaries

### Solo Operator Assumption
The system is designed for one human + AI. Multi-user teams would need task assignment protocols, handoff patterns, conflict resolution between operators, and concurrent access controls for TASK-STATE.yaml. None of these are currently defined.

**Impact:** Using the harness with >1 operator without these additions will produce task collisions, duplicate work, and state corruption.

**Mitigation:** If multiple people need to use the system, run separate harness instances per operator with a shared backlog. This is a workaround, not a solution.

### Single Active Project
The lock mechanism enforces one project at a time. This is a feature, not a bug — but it means truly parallel workstreams (e.g., urgent hotfix while a feature project is active) require either parking the current project or running a second harness instance.

### Structural Misfit Detection
The harness assumes sequential tasks, a single operator, and manual verification points. Some projects structurally don't fit these assumptions — they require parallel task execution, multiple operators, or non-linear workflows.

**The harness does not currently detect when a project is a poor structural fit.** A project that doesn't match the harness model may appear to work initially but produce subtle failures: tasks that should run in parallel get serialized (slowing delivery), dependencies that are actually bidirectional get forced into one direction, or verification points that need multiple reviewers get assigned to one.

**Impact:** The harness proceeds confidently with projects that don't fit its model. The operator may not realize the mismatch until failures accumulate.

**Mitigation:** During the Verification Checkpoint, the planner should flag if the project description implies parallel workstreams, multiple operators, or non-sequential dependencies. The operator can then decide whether to adapt the project to fit the harness or use a different management approach.

**Future direction:** Automated structural compatibility check during project scaffolding.

## Execution Limitations

### Manual Task Chaining
The human currently starts each executor session manually. There is no automated task chaining. This means the system requires human presence at every task transition.

**Future direction:** Automated chaining with human checkpoints at phase boundaries.

### Manual Verification
Task verification is manual (the executor checks a list, the planner reviews). There are no automated checks (e.g., scraping a deployed page to verify banned phrases are gone, running tests, or validating API responses).

**Future direction:** Automated verification hooks per task that run after completion.

### Context Window Limits
The one-task-per-session pattern mitigates context degradation but doesn't eliminate it. Very large reference files or very complex tasks may still exceed the AI's effective context window, even in a single session.

**Mitigation:** If a reference file is too large, extract the relevant subset for the task. If a task is too complex for one session, decompose it further.

## Memory Limitations

### Manual Memory Review
The quarterly (or configurable cadence) review is manual. The operator must remember to run "Learning sweep" or schedule it. There is no automated aging, flagging, or notification.

**Future direction:** Automated age-based flagging with operator prompts during routine interactions.

### Memory Validation Is Human-Gated
Every discovery must be manually validated before becoming a learning. This is intentional (it prevents invisible bias) but creates a bottleneck. If the operator doesn't review DISCOVERIES.md regularly, knowledge gets stuck in the intake.

**Mitigation:** Include "Review discoveries" as part of the project completion protocol (this is already built in) and schedule periodic reviews independent of project completion.

### No Cross-Harness Memory Sharing
If multiple harness instances run in parallel (for parallel operators or parallel workstreams), their memory systems are isolated. A discovery in Instance A does not automatically appear in Instance B.

**Mitigation:** Manual synchronization of LEARNINGS.md across instances. Prioritize Universal-scoped entries for synchronization.

## Dependency Engine Limitations

### No Circular Dependency Detection
TASK-STATE.yaml does not automatically detect circular dependencies (A depends on B, B depends on A). The planner must catch these manually during task decomposition.

### Output Hash Limitations
Output hashes provide lightweight change detection but don't track *what* changed. If a completed task's output is modified, the system flags downstream tasks but doesn't describe the modification.

### Assumption Invalidation Is Manual
When a discovery invalidates an assumption, the planner must manually scan TASK-STATE.yaml for all tasks sharing that assumption. There is no automated propagation.

## Version Control Limitations

### Non-Code Deliverables
Version control for code (commits, diffs, branches) works well. Marketing copy, SaaS configurations, social media changes, and platform-native content don't have a natural version control layer. The system can commit files that describe these deliverables but cannot track the deliverables themselves.

**Mitigation:** Use task files and completion reports as the audit trail for non-code deliverables.

### Harness Version Coexistence
When the harness itself evolves (e.g., v3.1 → v4), existing projects created under an earlier version remain in their original structure. The harness version is declared in `HARNESS.md` and `config.yaml`. There is no automated migration path for existing projects to a new harness version.

**Mitigation:** The `harness_version` field in the config allows the planner to detect version mismatches. Projects on older versions should either be completed under their original version or manually migrated.

## Platform Dependencies

### AI Model Availability
The two-tier model assumes access to both a capable planner model and a fast executor model. If only one model tier is available, the separation of planning and execution collapses. The system still works but loses the cost/drift benefits.

### Platform-Native Memory Interaction
The relationship between harness memory (DISCOVERIES/LEARNINGS) and platform-native memory (if any) is documented but not enforced. Conflicts between the two systems must be resolved manually.

## What This Document Is NOT

This is not a risk register or a bug tracker. It documents *structural limitations* — things the harness cannot do by design. Bugs found during use should be captured in DISCOVERIES.md and promoted to LEARNINGS.md through the normal pipeline. If a bug reveals a structural limitation, add it here.
