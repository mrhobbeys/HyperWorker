# Changelog — HyperWorker

## v5.0 (2026-04-25) — Clean break from v4

### Philosophy

v5.0 is not a refactor of v4.1.1. The diagnoses are different. v1–v4 designed against *"how do we make the agent follow rules reliably?"* — the answer compounded into more rules, more verification components, more state files. v5.0 designs against *"how do we make the agent's compliance structurally enforceable rather than verbally requested?"* — the answer is event-sourced state with regenerable projections, hash citations, capability gates, and a layered verification pyramid.

v4.1.1 remains on GitHub as the prior theory. **There is no migration path.** Operators with running v4.1.1 projects complete them under v4.1.1; new projects start on v5.0.

### Removed (clean break, not deprecation)

- **Memory mechanism in its v4 form.** `memory/DISCOVERIES.md`, `memory/LEARNINGS.md`, `memory/LEARNINGS-ARCHIVE.md`, the validation gate, the lifecycle states (ACTIVE / REFERENCE / DEPRECATED / ARCHIVED), the periodic review cadences. **Replaced by Typed Artifacts** (decision, finding, anti-pattern, operating-reality) over event-sourced substrate with projection-based access. Validation is a *field* (`confidence: provisional | validated`); supersede semantics replace deletion. Knowledge is not "managed"; it is recorded and superseded.

- **Per-step `SESSION-STATE.md` writes.** Resume is replay-based via `events.jsonl`. No per-step parallel state file. Tasks that genuinely need finer granularity should be decomposed further; v4.1.1's per-step write was a compensating mechanism that the substrate makes unnecessary.

- **READ-BACK as a separate ceremony (`templates/executor-prompt.md` Rule 15, `core/VERIFICATION.md` §3).** Replaced by hash-citation freshness checks at Layer 1, automatic on every event. The same guarantee — that an artifact has not silently changed since it was cited — is now structural rather than ceremonial.

- **15-rule executor prompt.** v4.1.1's `templates/executor-prompt.md` was 80+ lines of verbal rules: "do only what the task says," "do not look ahead," "do not act on discoveries," etc. v5.0's prompt is under 30 lines. The substrate now enforces what the rules used to request: hermetic working set via `consumes:` (rule about staying-in-lane), capability gate via tool schema (rule about not exceeding scope), Layer 1 citation check (READ-BACK rule), task state machine (status-transition rules).

- **Forced-verbosity instructions in prompts.** "Be concise" and length limits in the executor prompt are removed. Per-model profiles handle verbosity declaratively. The Anthropic 2026-04-23 4.7 postmortem documented that forced-concision degrades 4.7 output quality; the v5.0 `claude-opus-4-7.yaml` profile encodes this.

- **Pushback Protocol as runtime default (`core/VERIFICATION.md` §8).** v4.1.1's pre-execution "evaluate whether the task makes sense" step produced low-signal interventions. v5.0 makes pushback a Layer 3 trigger fired by structural conditions: council non-convergence, repeated Layer 1/2 failure past retry budget, schema-declared pivot triggers. Standard-risk routine work does not invoke pushback.

- **`reference/RESEARCH-PROTOCOL.md` as a top-level optional feature.** Folded into project schemas: any schema may include domain research as a setup step. Not a separate top-level configurable.

- **`case-studies/` as static teaching artifacts.** Replaced by `schemas/projects/` as executable bootstraps. Five default schemas ship: `marketing-campaign` (deepest port from v4.1.1's case-study 01), `software-feature-ship`, `client-onboarding`, `event-planning`, `compliance-audit`. Each is meaningfully different in domain extensions, default tasks, and council composition.

- **Dependency mechanism as a separate mechanism.** Absorbed into Atomicity. The dependency graph is now a projection (`TASK-STATE.yaml`) over `task.create`, `task.status`, and `task.complete` events. Mechanism count drops from six to five. The substrate is added as a separate concern below the mechanisms.

- **`core/MEMORY.md`, `core/DEPENDENCY.md`.** Deleted (concerns absorbed elsewhere).

- **`templates/session-state-template.md`.** Deleted (no per-step state file).

- **`templates/post-mortem-template.md`.** Deleted; post-mortem prose lives directly in `done/<task-id>/post-mortem.md` as file-canonical Mutable Surface, no template required.

### Added

- **Substrate.** `core/SUBSTRATE.md` documents `.hyperworker/events.jsonl` (canonical append-only event log, hash-chained), the projection regeneration protocol, the hash sidecar (`.hyperworker/hashes.json`), and the precise file-system protocols for every `hw` operation. The `hw` namespace is **agent protocol, not a CLI** — every operation is a documented set of read-and-write steps an agent can execute by reading the markdown.

- **Five mechanisms over the substrate.** `core/LOCK.md`, `core/ATOMICITY.md`, `core/TYPED-ARTIFACTS.md`, `core/VERIFICATION.md`, `core/PRECEDENCE.md`. Each carries explicit hypotheses and falsifiers in §Hypothesis sections.

- **Branch / fold (in `core/ATOMICITY.md`).** Exploratory subwork opens a branch (`hw branch`); on completion, `hw fold` collapses the branch into a 1–3 sentence projection in the parent while preserving the full sub-trajectory in events. Pattern from Sun et al., *AgentFold*; made structural via the projection-rendering protocol.

- **Capability gates (in `core/ATOMICITY.md`).** Each subagent declares `provides:` in `.hyperworker/agents/<id>.yaml`; each task declares `required_tools:` in frontmatter. The harness composes the subagent's tool schema by intersection. Mismatch produces `capability_gap.md`; the harness refuses to delegate. Re-enables subagents safely after their v4.1.1 removal.

- **Typed Artifacts (`core/TYPED-ARTIFACTS.md`).** Four default kinds: decision (DEC), finding (F), anti-pattern (AP), operating-reality (OR). Each is event-sourced, hash-citable, schema-validated. Per-project schema extensions add domain fields. Citations are `[KIND-ID#short-hash]`. Stale citations block writes at Layer 1.

- **Consumption Protocol.** Each task declares `consumes:`; before any state-changing tool call, the agent updates `consumed-inputs.md` with paraphrases of each consumed artifact. Layer 1 computes Jaccard overlap between paraphrase and source; below the per-model-profile threshold, the recitation is rejected. Pattern from Manus; made structural via `task.recite` events.

- **SCAN markers (in `core/PRECEDENCE.md`).** Each tier section in `00-REFERENCE-rules.md` ends with `@@SCAN_n_m:` markers. Before any state-changing event, the agent emits a token-level answer to each marker via `task.scan` events. Output token generation restores attention; passive re-reading does not. Pattern from dev.to/nikolasi.

- **Compression (in `core/TYPED-ARTIFACTS.md`).** Reference content is regenerated in two forms: `*.md` (human-readable, operator-edited) and `*.compressed.md` (deterministic transform that preserves code, paths, IDs, dates, version numbers, currency amounts, quoted strings byte-for-byte; compresses prose only). The compressed version is what enters the agent's prompt. Pattern from caveman-prompting research thread.

- **Verification Pyramid (`core/VERIFICATION.md`).** Three layers: Layer 1 cheap-fast structural (schema, citation, recitation overlap, hash chain), Layer 2 mid behavioral (acceptance criteria, SCAN compliance, failure scenarios), Layer 3 high-cost judgmental (council with context-asymmetric framing, optional cross-family). Risk levels (`standard | elevated | critical`) declared at task authoring; locked once written.

- **Council Review.** Multiple subagent perspectives configured per schema (`council.yaml`). Verifiers run with context-asymmetric framing — they see the artifact, the spec, and the consumes list; not the implementer's chain-of-thought. Triggers are structural (`project.activate`, `phase.complete`, `task.complete` for elevated/critical, schema-declared pivots, manual `hw council`). Convergence rules: `all-agree-or-escalate`, `majority-or-escalate`, `any-fail-blocks`.

- **Per-Model Harness Profiles.** Six profiles ship at `templates/models/`: `default`, `claude-opus-4-7`, `claude-opus-4-6`, `claude-sonnet-4-6`, `claude-haiku-4-5`, `github-copilot`. Each declares verbosity assumptions, suppress-concise-directives setting, context-fill thresholds (4.7 lower because tokenizer encodes more), recitation thresholds, council size defaults. Profiles document differences with citations (e.g., Anthropic 2026-04-23 postmortem for 4.7); they do not declare a model "worse" than another. Profiles are templates; projects copy one into `.hyperworker/models/` at bootstrap.

- **Five default project schemas at `schemas/projects/`.** Each is a full executable bootstrap: `schema.yaml`, `precedence-tiers.yaml`, `artifact-extensions.yaml`, `capability-gates.yaml`, `verification.yaml`, `council.yaml`, `project-template.md`, `rules-template.md`, README, plus task templates. The marketing-campaign schema is the deepest (full port of v4.1.1's case-study 01 with eight task templates plus a discovery task). The other four are competent baselines, meaningfully different in domain extensions, default tasks, council members, and capability gates.

- **Ratchet (in `core/ATOMICITY.md`).** When `task.complete` fires, the harness re-runs Layer 1 citation checks across all complete-status tasks. Any prior task whose `consumes:` is now stale due to the new task's outputs is moved back to `blocked` automatically. Regression detection is structural; the agent does not need to remember to check.

- **Cross-project artifact visibility (in `core/TYPED-ARTIFACTS.md`).** Tag-based, opt-in. An artifact tagged `cross-project:<scope>` is visible to projects whose `config.yaml` includes that scope in `cross_project_subscriptions:`. Replaces v4.1.1's Universal/Vertical/Client/Engagement scope hierarchy with a more general tag-and-subscription mechanism.

### Changed

- **Mechanism count: 6 → 5 + substrate.** Dependency absorbed into Atomicity. Substrate is not counted as a mechanism; it is the medium the mechanisms compute against.
- **Executor prompt: 80+ lines, 15 rules → under 30 lines, 0 rules.** Substrate enforcement replaces verbal rules.
- **Project state files: TASK-STATE.yaml + SESSION-STATE.md → TASK-STATE.yaml only (as projection).** SESSION-STATE eliminated.
- **Verification: 8 components → 3 layers (pyramid).** Same checks, different organization, with cost-classified routing.
- **Reference rules file: 1 form → 2 forms.** `*.md` (operator-edited, file-canonical) and `*.compressed.md` (regenerated, agent-prompt-loaded).
- **`reference/VALIDATION.md`** — preserved with light revision; the eight-step validation walk still applies, mapped to v5.0's structures.
- **`reference/FAILURE-MODES.md`** — rewritten for v5.0 failure modes (some old ones disappear with the Memory pipeline; new ones appear around event-log corruption, projection drift, and capability-gate refusals).
- **`CONTRIBUTING.md`** — updated to focus on schema contributions, per-model profile additions, and structural-check refinements over rule additions.

### Hypotheses (full list in `HYPERWORKER-V5-SPEC.md` §15)

Each primitive carries an explicit hypothesis with a falsifier. v5.1 retires whatever fails its falsifier in real use. Operators running v5.0 in real projects should record observed failures against the hypothesis table.

---

## v4.1.1 (2026-04-19) — Final v4 release

(See git history for the v4 changelog. v4.1.1 is unchanged in this repo.)
