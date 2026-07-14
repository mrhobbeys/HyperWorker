# Failure Modes — v5.1

> Known limits and structural failure modes of v5.0 / v5.0.1 / v5.1. Distinct from per-project failures. The harness is a theory; some primitives will fail their hypotheses in real use. Document those here as evidence accumulates.

---

## Hypothesis Falsification (Tracked Cases)

The hypotheses in `core/*.md` §Hypothesis sections and the v5.1-spec §7 each name a falsifier. As v5.x is run on real projects, observed falsifications accumulate here. v5.x.y retires whatever has falsified.

(empty — populate as evidence is gathered)

### v5.1 hypotheses under empirical evaluation

The v5.1 spec adds seven hypotheses (H-F1 through H-F8, with H-F7 omitted from the spec) covering each new structural primitive. v5.1 ships with all primitives implemented; empirical evaluation begins on the first v5.1 run. Operators record observed falsifications here so v5.1.x can retire what fails.

| ID | Primitive | Falsifier signal to watch |
|---|---|---|
| H-F1 | `friction.log` event kind + auto-prompts | v5.1 runs still need post-hoc reconstruction to surface friction; auto-prompts fired but agents rejected them as false-positives at high rates. |
| H-F2 | `council.report` projection | Operators still grep `events.jsonl` to find council verdicts; per-fire and INDEX projections not consulted. |
| H-F3 | `session.handoff` event kind | Resuming agents ignore `SESSION-HANDOFF.md` projection or paraphrase incorrectly; `requires_handoff_acknowledge: true` not enforced because tasks did not declare it. |
| H-F4 | `ab-variant` delivery mode | Variants produced under `ab-variant` are trivially paraphrased without real differentiation on the declared axis; `variant-comparison-watcher` PASSes a paraphrase pair. |
| H-F5 | `delegation_policy` OR field | Operator sets the field; agent demonstrably ignores it; intervention rate unchanged from no-field baseline. |
| H-F6 | T-001 corpus-scan task (synthesis) | Synthesis runs still require operator intervention to refuse premature OR locking; T-001 surfaces purposes that match bootstrap framing rather than corpus signal. |
| H-F8 | `model_selection_policy` OR field | Operator sets `prefer: cheapest-capable`; harness still routes most or all work to the largest model. |

---

## Structural Limits

### Single-instance lock

The Lock mechanism is per-harness-instance. Truly parallel workstreams (an urgent hotfix while a feature project is active) require either parking the current project or running a second harness instance with a separate `events.jsonl`. Multi-project parallelism is not supported within one instance.

**Mitigation (v5.3).** One instance per workstream, coordinated by a program project — see `core/LOCK.md` §Programs and the `program` schema. Prior to v5.3 this page called multi-instance operation "a workaround, not a feature"; three field deployments then built the coordination layer ad hoc, so v5.3 names and schematizes it. Cross-instance coordination remains files-and-citations only.

### Concurrent writers on one event log (v5.3)

Two dated field incidents: parallel actors (council members in one, concurrently dispatched sessions in the other) appended to a single `events.jsonl` and produced EV-id collisions, chains forking from one tail event, and broken hashes. This is not a rare edge — it is the default outcome of dispatching parallel work into one instance.

**Mitigation.** `core/SUBSTRATE.md` §Single-Writer Rule (H-S3): parallel actors write draft files; one convergence writer appends serially. `hw verify` surfaces violations as `chain_breaks`. There is deliberately no filesystem lock primitive; if a deployment following the draft/convergence protocol still corrupts logs, H-S3 is falsified and a lock primitive gets reconsidered.

### Perpetual work has no terminal state (pre-v5.3)

Projects with no natural "done" (a weekly sweep, a standing registry, an ongoing maintenance plan) could not truthfully archive; field runs improvised `deferred (ongoing)` statuses and off-harness cadence conventions, twice, independently.

**Mitigation (v5.3).** `lifecycle: ongoing` with `cycle.open`/`cycle.close` events and a computed `next_due` — see `core/LOCK.md` §Ongoing Projects (H-L2). Overdue cycles surface structurally in `hw status`.

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

### Friction-log auto-prompt false-positive rate (v5.1)

The `friction.log.prompt` heuristics (Layer 1 repeat fail, Layer 2 fail, training-fill markers, mid-flow directive Decision, council non-convergence on critical) fire on observable signals; the false-positive rate is unknown until v5.1 sees real use. A high false-positive rate means the agent rejects most prompts as spurious, which produces noise without value. A low false-positive rate means the heuristics are well-tuned but possibly miss real friction (false negatives are harder to measure).

**Mitigation.** Operators record the prompt-to-actual-`friction.log` ratio per heuristic. The heuristic that produces the most rejected prompts is the candidate for revision in v5.1.x.

### Delegation policy ignored by agent (v5.1)

`delegation_policy` is declared on OR-001 and read at dispatch time, but enforcement is soft: the agent decides whether to comply. If observed agent behavior diverges from the declared policy at material rates, the field is not load-bearing. Hard enforcement (e.g., harness blocks subagent dispatch when `subagent_use: never`) is deferred to v5.2.

**Mitigation.** Track whether operator interventions occur at the same rate with the field set as without. If yes, falsifier H-F5 is met and v5.1.x revisits.

### Model selection policy ignored by dispatch (v5.1)

`model_selection_policy.prefer: cheapest-capable` resolves through per-model profile rankings, but if the dispatch path does not actually consult the rankings (e.g., the agent self-routes to a more-capable model regardless), the policy is decorative. The chosen profile is recorded in dispatch events; observed routing should match the declared `prefer`.

**Mitigation.** Track the chosen-profile distribution per dispatch event. Routing distribution that does not reflect the declared `prefer` indicates falsifier H-F8 is met.

### ab-variant trivial-paraphrase failure (v5.1)

`ab-variant` produces N differentiated artifacts in one pass. If the executor produces variants that are trivial paraphrases (e.g., three CTAs that differ only in word order on the same framing), the differentiated-output premise is unmet. The optional `variant-comparison-watcher` council role detects this with pairwise diff against a configurable threshold; the threshold is intentionally placeholder in v5.1 and tuning is empirical.

**Mitigation.** Schemas with frequent `ab-variant` use should opt into `variant-comparison-watcher` and tune the threshold per their domain. PASSing variants that the operator subsequently judges trivially-similar is a tuning signal, not a structural failure.

### Session handoff not consumed (v5.1)

`session.handoff` produces a substrate event whose projection (`SESSION-HANDOFF.md`) is what the resuming agent should read. If the resuming agent ignores the projection or paraphrases it incorrectly, the structural anchor is not load-bearing — the v5.0/v5.0.1 informal-prose handoff is no better than the v5.1 event-based one. Tasks that benefit from explicit handoff acknowledgement should set `requires_handoff_acknowledge: true` in their frontmatter; the substrate then enforces acknowledgement before the first state-changing event in the resuming session.

**Mitigation.** Long-project schemas should set `requires_handoff_acknowledge: true` on their entry tasks. If acknowledgement is set and resuming agents still mishandle handoffs, falsifier H-F3 is met.

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
