# Failure Modes — v5.0

> Known limits and structural failure modes of v5.0. Distinct from per-project failures. v5.0 is a theory; some primitives will fail their hypotheses in real use. Document those here as evidence accumulates.

---

## Hypothesis Falsification (Tracked Cases)

The hypotheses in `core/*.md` §Hypothesis sections each name a falsifier. As v5.0 is run on real projects, observed falsifications accumulate here. v5.1 retires whatever has falsified.

(empty — populate as evidence is gathered)

---

## Structural Limits

### Single-instance lock

The Lock mechanism is per-harness-instance. Truly parallel workstreams (an urgent hotfix while a feature project is active) require either parking the current project or running a second harness instance with a separate `events.jsonl`. Multi-project parallelism is not supported within one instance.

**Mitigation.** Two harness instances with shared cross-project subscriptions for compounding artifacts. Documented as a workaround, not a feature.

### Solo-operator assumption

v5.0 is designed for one operator + AI(s). Concurrent operator writes are not orchestrated; if two operators both append to `events.jsonl` simultaneously, the chain breaks (`prev_hash` mismatch on the second write). Multi-operator handoff requires either disjoint harness instances or a server layer outside v5.0's scope.

### Event-log corruption

If `events.jsonl` is corrupted (file truncated, line malformed), `hw verify` reports the chain break. Repair requires either:

1. Restoring from the last clean git commit (if version control is enabled).
2. Manually editing `events.jsonl` to remove the malformed line and re-running `hw project`. The reverted state is whatever the events up to that point imply.

There is no automated repair; the substrate's append-only invariant is the simplest version of the integrity check, and respecting it depends on operator discipline (no manual edits to events.jsonl).

### Projection drift

If an operator hand-edits a projection file (e.g., `decisions/DEC-007.md`), the next `hw verify` flags hash mismatch and the next `hw project` overwrites the edit. Operator-authored content goes in the Mutable Surface (file-canonical files like `task.md`, `00-REFERENCE-rules.md`), not in projections. This is a documented boundary, not a bug.

### Recitation overlap heuristic

The Jaccard-overlap check on paraphrase vs. source detects shallow paraphrase but not all paraphrase failure modes. An agent that paraphrases the title accurately while misrepresenting the body could pass overlap and still produce wrong work. Layer 1 catches lexical drift; Layer 2 (acceptance criteria) and Layer 3 (council) are needed for semantic correctness.

**Future direction.** Embedding-based similarity instead of Jaccard could improve detection. v5.0 keeps Jaccard for determinism and dependency-free operation; the threshold is per-model-profile tunable.

### Capability-gate refusal vs. legitimate need

A task may declare `required_tools` that no available subagent provides. The harness emits `capability_gap.md` and refuses to delegate. The operator must add the tool to an existing agent profile, spawn a new agent profile, or run the task in-line on the parent agent.

This is a feature, not a failure: the alternative — silently degrading or attempting tools not in the schema — is the v4.1.1 failure mode the gate exists to prevent. The cost is occasional friction when capabilities are mis-declared.

### Council non-convergence loops

If a council never converges (members consistently disagree), the harness escalates to operator review. If the operator is unavailable, the task remains `blocked` with `reason: council_escalated`. The harness does not auto-resolve.

**Mitigation.** Schemas should declare convergence rules appropriate to the work: `all-agree-or-escalate` is conservative; `majority-or-escalate` accepts more disagreement before escalating.

---

## Cost Limits

### Heavy-upfront acknowledged

The schema-driven bootstrap is more upfront work than v4.1.1's. A complex marketing-campaign bootstrap can take an hour: writing operating-reality, drafting the rules file, council pre-review, customizing tasks. The hypothesis is that this upfront cost is amortized across runtime autonomy. If it is not — if operators report the upfront cost without runtime savings — the schema design needs revision.

### Recitation cost per task

Each task emits a `task.recite` event for each consumed artifact, and SCAN markers add a `task.scan` event per marker. Empirically these are < 1% of context budget per task; nonetheless, deeply-consuming tasks (8+ artifacts) make the cost visible. Decompose tasks if recitation cost exceeds 5% of context.

### Council token cost

Layer 3 council on critical tasks invokes 3–4 subagents, each reading the artifact and producing a structured PASS/FAIL. For schemas like compliance-audit (council size 4), per-task token cost is meaningful. The default risk routing (most tasks `standard`, council fires only on elevated/critical) keeps the typical cost low; a project where every task fires council is mis-classified.

---

## Compatibility Limits

### Model availability

The five-mechanism harness assumes the planning agent can read large documents (full schema, all consumed artifacts, the rules file in compressed form), and the executor can run with the per-model profile's threshold settings. Models with very small effective context windows (< 32k effective) struggle with the marketing-campaign or compliance-audit schemas as a single agent — they need decomposition into branched sub-projects.

**Mitigation.** Use the `claude-haiku-4-5.yaml` profile as a reference for aggressive thresholds; consider a two-model setup (capable planner + smaller executor) for cost-sensitive cases.

### Cross-family verification

Cross-family verification (e.g., Claude implementer + Copilot CLI verifier) is opt-in via per-member `family:` declaration in `council.yaml`. v5.0 ships with same-family + context-asymmetric framing as default; cross-family is a power-user pattern with infrastructure overhead (need both vendor accounts, both authentication paths, both prompt-style adapters).

---

## What this document is NOT

- A bug tracker. Specific bugs go in issues, not here.
- A risk register. Use this to document *structural* limitations — things v5.0 cannot do by design.
- A change log. New failure modes get added here as evidence accumulates; resolutions land in `CHANGELOG.md`.
