# Changelog — HyperWorker

## v5.1 (2026-04-26) — Structural primitives from second empirical run

A second empirical run (the cyber-insurance-audit lead-magnet on the marketing-campaign schema) plus carry-forward observations from the v5.0 brand-foundation-synthesis run produced a friction log of structural gaps that v5.0.1's documentation-and-templates-only patch cycle could not close. v5.1 adds the structural primitives those friction entries motivated: three new substrate event kinds, two new operating-reality fields, a new delivery mode, a new task in the synthesis schema, a new task in the marketing-campaign schema, and per-schema field reconciliation. v5.1 is **strictly additive over v5.0.1** — a v5.0.1 project running today runs identically under v5.1 unless it opts into the new primitives.

Each primitive carries an explicit hypothesis with a falsifier (see HYPERWORKER-V5.1-SPEC §7); v5.1.x will retire whatever fails its falsifier in real use.

### Substrate event kinds and projections

- **`friction.log` event kind + auto-prompts.** `core/SUBSTRATE.md` §Friction Log Event Kind documents the payload schema (type, patch_id, description, surfaced_by, severity, suggested_target) and the projection at `friction-log.md` (workspace-scoped by default; `projects/<id>/friction-log.md` if `friction_log_scope: project`). Substrate-level `friction.log.prompt` events fire on observable signals — Layer 1 verification fail-3-on-same-check, any Layer 2 fail, training-fill markers in agent output, an operator mid-flow directive captured as a Decision, council non-convergence on a critical-risk task. The agent reads each prompt and decides whether to follow with an actual `friction.log` entry. Hypothesis H-F1; falsifier: friction logs in v5.1 runs still require post-hoc reconstruction. (Maps to FL self-referential.)
- **`council.report` projection.** `core/SUBSTRATE.md` §Council Report Projection regenerates `projects/<id>/council/<fire_id>-<trigger>.md` per council fire (grouped by `fire_id` payload field on `council.invoke`/`council.report`/`council.converged`/`council.escalated`) plus an aggregate `projects/<id>/council/INDEX.md` listing fires chronologically. Operator can answer "did council fire on this task and what did it find" without grepping `events.jsonl`. Hypothesis H-F2; falsifier: operators still grep events.jsonl. (General improvement carried forward from v5.0.1 deferred list.)
- **`session.handoff` event kind.** `core/SUBSTRATE.md` §Session Handoff Event Kind documents the payload (project_id, closing_actor, last_completed_task, next_pending_task, active_artifact_state, open_operator_questions, recommended_first_action, context_compaction_summary) and the projection at `projects/<id>/SESSION-HANDOFF.md` (overwritten on each handoff; not chained). Task templates may declare `requires_handoff_acknowledge: true` to enforce structural acknowledgement before the resuming session's first state-changing event. Hypothesis H-F3; falsifier: resuming agents ignore the projection or paraphrase it incorrectly. (Maps to v5.0.1 deferred D-6.)

### Operating-reality extensions

- **`delegation_policy` field.** Optional OR field captures operator engagement preferences once at bootstrap so they propagate across sessions: `mode` (step-by-step / run-to-completion / hybrid), `subagent_use` (never / when-helpful / aggressive), `pause_on` (council-failures, layer1-failures-after-N-retries, operator-mid-flow-directives, phase-boundaries, critical-risk-task-completion), `resume_authority`. Soft enforcement: the agent reads the field and decides; v5.1 does not block dispatch on violation. Hard enforcement deferred to v5.2 if needed. `core/ATOMICITY.md` §Delegation Policy documents how dispatch consults the field. Hypothesis H-F5; falsifier: operator interventions occur at the same rate with the field set as without. (Maps to v5.0.1 deferred D-4 + D-5.)
- **`model_selection_policy` field.** Optional OR field declares cost/speed/capability preferences for subagent dispatch and council-member instantiation: `prefer` (cheapest-capable / fastest-capable / most-capable / manual-only), `fallback_trigger` (layer1-failure-after-N / layer2-failure / council-non-convergence / never), `fallback_target` (explicit profile_id), `per_task_overrides`. Per-model profiles in `templates/models/*.yaml` declare `relative_cost`, `relative_capability`, `relative_speed` (1-5 scale) so `cheapest-capable` resolves deterministically. Operators with non-default rosters override rankings in `templates/models/_ranking.yaml`. `core/ATOMICITY.md` §Model Selection Policy and `templates/models/README.md` §v5.1 — model_selection_policy resolution document the algorithm. Hypothesis H-F8; falsifier: operator sets `prefer: cheapest-capable` and the harness still routes most work to the largest model.

### Delivery modes and council roles

- **`ab-variant` delivery mode.** `templates/task-template.md` and `core/ATOMICITY.md` §Delivery Modes add `ab-variant` to the `delivery_mode` enum with conditional-required `ab_variant_count` (2-5, default 3) and `ab_variant_axis` fields. The executor produces N differentiated variants in one pass — each is its own artifact projection with its own hash; Layer 1 citation rules apply per variant. For intentional variation (campaign A/B test, design alternatives, deployment options); not for iteration toward a single winner (that's `bounded-iteration`). Hypothesis H-F4; falsifier: variants are trivially paraphrased without real differentiation on the declared axis.
- **`variant-comparison-watcher` council role.** Opt-in role added to `core/VERIFICATION.md` §Council Role Library. When a task declares `delivery_mode: ab-variant`, schemas may include this role to verify variants meaningfully differ on the declared `ab_variant_axis` via pairwise diff against a configurable threshold. Threshold is intentionally placeholder in v5.1; tuning is empirical.

### Synthesis schema additions

- **T-001 (purpose-fit corpus scan).** New `schemas/projects/report-synthesis/task-templates/01-corpus-scan.md` (uses the previously-skipped T-001 slot). After T-000 registers every source, the agent reads section-level summaries (filenames + first 20 lines + section headers; NOT full content) and surfaces 2-3 plausible synthesis purposes anchored to the actual corpus signal. Operator confirms current `OR-001.synthesis_purpose` OR triggers a supersede with a refined purpose; the supersede event is captured before T-002 begins. `schema.yaml` `default_tasks.templates` updated to include the new task; T-002's `depends_on` updated from `[T-000]` to `[T-001]`. Hypothesis H-F6; falsifier: synthesis runs still require operator intervention to refuse premature OR locking. (Maps to v5.0.1 deferred A-10 + D-2.)

### Per-schema patches

- **marketing-campaign.** `bootstrap_questions` adds `contact_info` (CAN-SPAM physical address + company legal name + contact email) — the artifact-extensions already required `contact_info` on operating-reality but bootstrap did not ask for it (FL-005). `brand_voice_anchor` widens from `string|null` to `list[string]|null` to support multi-source voice composition (operator voice doc + competitor-tone analysis + brand guide); first-listed dominates on conflict (FL-009). New T-009 (`09-social-promotion.md`) ships LinkedIn post + image-carousel script + short-form video script consuming DEC-001 (offer) and DEC-002 (tone) — closes FL-007 (social promotion needed but not in the schema). Field overrides mark budget, team, operator_profile optional.
- **software-feature-ship.** `field_overrides`: budget, team, operator_profile optional (timeline + authority required by domain).
- **client-onboarding.** `field_overrides`: budget, operator_profile optional. New required `contact_info` object (vendor_legal_name + vendor_contact_email + client_legal_name) reflecting multi-party onboarding.
- **event-planning.** `field_overrides`: authority, operator_profile optional (timeline/team/budget required by domain).
- **compliance-audit.** `field_overrides`: budget, team optional (timeline/authority required; operator_profile required because internal-vs-external auditor changes deliverables).

### Tooling

- **`tools/hw-verify.py` updated for v5.1 event kinds.** New constants `KNOWN_EVENT_KINDS` (closed set including `friction.log`, `friction.log.prompt`, `session.handoff`, plus all v5.0/v5.0.1 kinds) and `REQUIRED_PAYLOAD_FIELDS` (per-kind structural payload checks). Result struct gains `unknown_event_kinds` (warning only) and `malformed_payloads` (blocking). v5.0.1 events.jsonl files validate unchanged.

### Documentation

- **HARNESS.md.** Title bumped to v5.1. §Friction Logs reframed: the projection is now event-sourced (regenerated from `friction.log` events) instead of a working artifact. File-structure block adds `council/`, `SESSION-HANDOFF.md`, `friction-log.md`, `templates/models/_ranking.yaml`, `templates/session-handoff-template.md`.
- **`reference/FAILURE-MODES.md`.** Title bumped to v5.1. New §Hypothesis Falsification table for v5.1 hypotheses under empirical evaluation. New structural-limit entries: friction-log auto-prompt false-positive rate, delegation-policy ignored by agent, model-selection-policy ignored by dispatch, ab-variant trivial-paraphrase failure, session-handoff not consumed.

### Version

- `harness_version: "5.1"` across all six schema files and HARNESS.md title.

### Not in v5.1 (deferred)

- **`scope_presets`.** Operator pushback (likely-trap risk: pre-defined presets at schema level lock in patterns before empirical signal supports them) deferred. Operators continue to declare scope subsets conversationally at bootstrap, unchanged from v5.0.1.
- **Hard enforcement of `delegation_policy`.** v5.1 ships soft enforcement; hard enforcement (e.g., harness blocks delegation when `subagent_use: never`) deferred to v5.2 if real use shows it is needed.
- **Stuck-loop detection.** Observed in the v5.0.1 lead-magnet run (agent retried a broken React form-input save method for ~20 minutes before being told to try something else); not exactly an `ab-variant` problem (which is intentional variation). Out of v5.1 scope; flagged in HYPERWORKER-V5.1-SPEC §9 as v5.2 candidate primitive (`task.stuck-loop` event kind triggered by repetition threshold).

---

## v5.0.1 (2026-04-25) — Cleanup patch

Empirical use of v5.0 on a strategic-foundation synthesis (the brand-foundation-synthesis run, 3 sessions, 227 events, 14 input files, 1 final deliverable) produced a 37-entry friction log. v5.0.1 closes the documentation, template, and type gaps that surfaced; it is **strictly additive and clarifying** — no new mechanisms, no schema-level behavior changes, no new event kinds. A v5.0 project completed under v5.0 runs identically under v5.0.1.

Structural additions surfaced by the run (purpose-fit corpus scan, friction logging as substrate event kind, council-outcome projection visibility, operator delegation policy as OR field, context-aware session handoff as substrate event kind) are deferred to v5.1.

### Documentation

- **Hash serialization canonical spec.** `core/SUBSTRATE.md` §Canonical Serialization for Hashing now specifies `json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False)` with explicit per-option rationale. The `ensure_ascii=False` choice is load-bearing — switching to Python's default `ensure_ascii=True` produces divergent hashes on any non-ASCII content and breaks chain integrity. (Friction B-1.)
- **Citation format spec.** `core/SUBSTRATE.md` §Citation Format formalizes `[KIND-NNN#hhhhhhhhhhhh]` with the 12-lowercase-hex truncation rule explicit. Schema-declared kinds (`SRC`, `CLM`, `CTR`) are listed alongside the defaults. (Friction B-2.)
- **events.jsonl path convention.** `core/SUBSTRATE.md` §File Locations adds an explicit table clarifying that `events.jsonl`, `hashes.json`, and `config.yaml` live at `.hyperworker/` under workspace root, never under `projects/<id>/`. (Friction A-15.)
- **`hw verify` algorithm fully specified.** `core/SUBSTRATE.md` §`hw verify` replaces the prior brief description with the complete algorithm: event hash recompute → chain integrity → projection drift → citation valid/stale/broken → structured PASS/FAIL result. Adds `--since=EV-NNNN` flag spec for incremental verification. (Friction A-14, C-4.)
- **Bootstrap clarifications.** `core/SUBSTRATE.md` §`hw bootstrap` clarifies that filenames are copied verbatim with frontmatter IDs preserved (the prior "renumbered" wording was misleading), specifies that operator-declared input folders are created at scaffold time if missing, documents the mid-bootstrap supersede pattern for OR corrections, and points at the operator-mid-flow-directive convention. (Friction A-2, A-3, A-6, A-12.)
- **Superseded artifact back-link rule.** `core/SUBSTRATE.md` §Superseded Artifact Back-Link specifies that an artifact superseded by another gets `superseded_by: [B-NNN#hash]` written into its frontmatter on the next projection regeneration. Clarifies hash propagation through the supersede chain. (Friction A-9.)
- **null vs `[]` semantics.** `core/SUBSTRATE.md` §null vs `[]` for Empty-Set Fields documents that `[]` means "declared empty" and `null` means "not declared / not applicable"; canonical serialization treats them as different bytes. (Friction A-8.)
- **Friction-log location convention.** `HARNESS.md` §Friction Logs declares workspace-root as the default (`bootstrap-friction-log.md`), with per-project override at `projects/<id>/friction-log.md`. (Friction A-5.)
- **Operator mid-flow directive pattern.** `HARNESS.md` §Operator mid-flow directives documents that mid-bootstrap or mid-task operator instructions outside `bootstrap_questions` are captured as typed Decision artifacts, not loose conversation. (Friction A-12.)
- **Trigger-aware council prompts pattern.** `core/VERIFICATION.md` documents `prompt_template_on_activate` / `prompt_template_on_output` as the schema-level mechanism for giving a council member trigger-specific prompts. (Friction A-7, C-5.)

### Templates

- **T-001 (synthesis charter) merged into T-000 (source inventory).** Bootstrap already populates OR fields and runs the project.activate council, leaving T-001 with no substantive work. T-001 task template is deleted; its residual responsibilities (Tier 4 STYLE, banned-tokens table, canonical-facts table) fold into T-000 acceptance criteria. Numbering preserved (T-002 onward keep their IDs); T-002's `depends_on` updated from `[T-001]` to `[T-000]`. The T-001 slot is documented as intentionally skipped in `schema.yaml`. (Friction C-1.)
- **T-009 rewrite (final-synthesis) removes dead references.** Eliminates references to `deliverable.finalize` event kind (does not exist), `hw wrap` protocol (does not exist), council "archive trigger" framing (the existing `project.archive` trigger is referenced correctly), and `audit-report-T008.md` filename (the actual file is `tasks/08-completeness-audit-completion.md` per harness convention). T-008 audit-report path updated correspondingly. (Friction A-16, A-17, A-18.)
- **Tautological acceptance criteria replaced.** T-002, T-004, T-005, T-006 had criteria that are tautologically satisfied by doing the task at all (e.g., T-006's "Structure declared as Decision artifact" — the task IS that). Each is replaced with a quality check the executor can fail. (Friction C-3.)
- **`lightweight_completion: true` flag** added to `templates/task-template.md`. When set, completion report is a 3-line summary instead of the full template (acceptance criteria result, outputs, follow-up). T-003 (anti-pattern capture) and T-006 (synthesis structure) marked lightweight. Documented in `core/SUBSTRATE.md` §Lightweight Completion. (Friction C-2.)
- **T-000 explicit duplicate detection step.** Step 2 specifies SHA-256 hashing before registration so byte-identical files collapse to a single source artifact and the duplicate is flagged in the completion report. (Friction A-11.)
- **T-002 granularity guidance.** New §Granularity guidance section codifies the split-vs-keep heuristic with examples. (Friction B-3.)
- **T-004 topic-clustering pre-step.** New §Pre-step section formalizes the clustering optimization (8 groups for ~200 claims) the Session 2 agent invented. Mandatory for N≥50 claims. (Friction B-6.)
- **T-007 prose style guidance.** New §Prose Style section codifies dense-analytical voice with claim-level citation density. (Friction B-7.)
- **T-008 7-check methodology canonicalized.** §The 7-Check Methodology documents the seven checks (section completeness, citation integrity, source coverage, OR constraint compliance, anti-pattern consistency, internal consistency, decision coverage) the Session 3 agent invented. (Friction B-8.)
- **Verbatim quotation principle (Tier 1).** `schemas/projects/report-synthesis/rules-template.md` Tier 1 adds the verbatim-quotation rule with `[paraphrase: ...]` markers required for any non-verbatim summary of operator intent or source content. New SCAN_1_3 marker. (Friction D-3.)

### Reference implementation

- **`tools/hw-verify.py`** ships as the canonical Python reference implementation of the `hw verify` algorithm. Standalone script: `python tools/hw-verify.py --workspace <path> [--since EV-NNNN]`. Exits 0 PASS / 1 FAIL with a structured report. Agents may reimplement for their environment but should match this algorithm. (Friction A-14.)

### New templates

- **`schemas/projects/report-synthesis/artifact-templates/source-template.md`** — schema for `source` artifact kind (was inferred ad-hoc in Session 1). (Friction B-4.)
- **`schemas/projects/report-synthesis/artifact-templates/claim-template.md`** — schema for `claim` artifact kind. (Friction B-3.)
- **`schemas/projects/report-synthesis/artifact-templates/contradiction-template.md`** — schema for `contradiction` artifact kind (was invented in Session 2). (Friction B-5.)
- **`templates/session-handoff-template.md`** — canonical session-handoff format (`projects/<id>/SESSION-HANDOFF.md`, overwritten on each handoff). Marked explicitly as a working artifact, not event-sourced. (Friction A-13. Substrate-event-kind handoffs deferred to v5.1, friction D-6.)

### Convention declarations

- **`output_format` is now `type: enum`** in `schemas/projects/report-synthesis/schema.yaml` and the corresponding `operating-reality` extension, matching the values already enumerated in the bootstrap prompt (`structured-doc | decision-matrix | executive-brief | strategic-foundation | other`). The prior `type: string` declaration could not be schema-validated. (Friction A-4.)
- **Bootstrap-question vs base-OR-field reconciliation.** `schemas/projects/report-synthesis/artifact-extensions.yaml` adds `field_overrides` marking the base operating-reality fields (`budget`, `timeline`, `team`, `authority`, `operator_profile`) as optional for synthesis projects. The synthesis schema doesn't ask for these and the constraint set it does ask for (purpose/audience/format/sources/scope/deliverable) is sufficient. (Friction A-1.)

### Bug fixes

- **T-008 audit-report path.** Was specified as `audit-report-T008.md` in project root; the actual harness convention writes completion reports to `tasks/<NN-name>-completion.md`. Updated to `tasks/08-completeness-audit-completion.md`. T-009 `consumes:` updated to match. (Friction A-18.)

### Version

- `harness_version: "5.0.1"` across all six schema files and HARNESS.md title.

### Deferred to v5.1 (require new mechanisms or new event kinds)

- Purpose-fit corpus scan as a structural step (friction A-10 + D-2)
- Friction logging as a substrate event kind (friction self-referential)
- Council outcome visibility as a projection (general improvement)
- Operator delegation policy as an OR field (friction D-4 + D-5)
- Context-aware session handoff as a substrate event kind (friction D-6)
- Anti-pattern + contradiction artifact templates as global default templates (the report-synthesis-specific templates ship in v5.0.1; non-synthesis schemas wait)

---

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
