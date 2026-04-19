# Changelog — HyperWorker

## v4.1.1 (2026-04-19) — Cleanup patch

### Philosophy
Infrastructure hygiene. No mechanism changes, no rule changes, no behavior changes. Restores the "healthcare/vendor references removed from core" invariant first stated in v2 — v4.1 regressed against it by leaking domain-specific worked examples into the Truth Layer. v4.1.1 scrubs those examples, closes two small open ambiguities in the same patch, and rewrites git history so the leaked strings do not persist in the public log.

### Fixed
- **Domain-specific worked examples scrubbed from core** — `core/VERIFICATION.md` Read-Back example (§3), end-user audience list (§7), and Failure Scenario example (§7) replaced with domain-neutral SaaS equivalents. `templates/rules-template.md` Canonical Facts rows (vanity phone, date-anchored deadline) replaced with widely recognized neutral examples. The patterns those examples illustrate are unchanged; only the specific strings changed.
- **`HARNESS.md` version header** — line 1 corrected from `v4.0` to `v4.1.1` (missed during the v4.1 bump).
- **Task-completion actor named** — Rule 16 (`templates/executor-prompt.md`) and `core/ATOMICITY.md` §Session State previously described the completion write in passive voice. Rule 16 now mandates a final SESSION-STATE write by the executor before the Completion Report, and the ATOMICITY.md relationship paragraph now names the executor (end-of-task write) and planner (next-task assignment) as the two writers. Closes the risk of orphaned `in_progress` state when a task finishes.

### Changed
- **Git history rewritten.** The leaked strings above were present in an earlier commit on the `v4.0.2` branch. History was rewritten to replace them in-place. All collaborators with a local clone of this repo must delete the clone and re-clone from origin. Commit SHAs on `v4.0.2` have changed; references to prior SHAs are stale.
- **Plan files excluded from version control.** `PLAN-*.md` added to `.gitignore`. Plan documents live outside the repo going forward.

---

## v4.1.0 (2026-04-19) — Execution enforcement gaps

### Philosophy
v4.1 closes a class of failure that v4.0's six mechanisms didn't structurally prevent: silent save failures, split-field instructions, creative iteration colliding with strict atomicity, missing scenario gates on end-user content, subtle-tell leakage in prescribed copy, and mid-task session loss. Each surfaced repeatedly in a meta-analysis of 30 production sessions. Fixes are additive inside the existing six-mechanism model — no new mechanisms.

### Fixed
- **Stale template path references** — Nine references in `HARNESS.md` (Routing Table, Truth Layer tree, Bootstrap Protocol scaffold list) and one in `core/VERIFICATION.md` still pointed at pre-v4.0 bare names (`templates/task.md`, etc.). Replaced with the `-template.md` equivalents. An agent following the Bootstrap Protocol literally would have hit file-not-found. Originally scoped as v4.0.2; rolled into v4.1 since the prior release was still unmerged.

### Added
- **Read-Back Verification (`core/VERIFICATION.md` §3)** — New contextual component. For tasks that modify external state (UI fields, API config, CMS updates), the executor must re-read the changed value from the source and record it in the Evidence Trail. A save is not complete until it has been read back. Subsequent components renumbered (§4 Baseline-After through §8 Pushback).
- **Executor Rule 15: READ-BACK** in `templates/executor-prompt.md` — Enforces post-write read-back on any external state change.
- **Field-Value Map section** in `templates/task-template.md` — Optional section for UI tasks. Every field appears in exactly one row with its exact target value. Step-by-step describes navigation; Field-Value Map describes destination state.
- **One-field-one-row principle** in `core/ATOMICITY.md` Key Design Principles — Codifies the rule that a single field's value never appears in more than one row or step.
- **Iterate-within-boundaries delivery mode** in `core/ATOMICITY.md` — Third Content Delivery Mode for visual assets, copy exploration, and design work where first-pass fidelity is impossible. Requires preview surface, version preservation, and explicit convergence criterion. Iteration is bounded, not open-ended.
- **Delivery Mode declaration** + **Iteration Protocol section** in `templates/task-template.md` — Per-task mode selection and the protocol fields required when iterate-within-boundaries is chosen.
- **Failure Scenario gate (`core/VERIFICATION.md` §7 Risk Classification)** — Tasks at `elevated` or `critical` risk that produce end-user-facing content require three realistic failure scenarios recorded in the Evidence Trail before completion. A single failed scenario blocks the task.
- **Failure Scenarios section** in `templates/task-template.md` — Optional section structured for the three required scenarios.
- **Banned Punctuation guidance** in `templates/rules-template.md` — Banned Phrases table now reads "Banned Token" and includes an em-dash example row. Em dashes in prescribed copy are an AI tell that breaks voice.
- **Canonical Facts — Do Not Normalize section** in `templates/rules-template.md` — Table for facts (vanity phone numbers, date-anchored deadlines) that must be preserved exactly to prevent AI normalization.
- **Step-Level Session State (`core/ATOMICITY.md` §Session State, `templates/session-state-template.md`)** — New file per project: `projects/[project-name]/SESSION-STATE.md`. Records active task, step number, last action, Evidence Trail pointer, next action, blockers. Overwritten on every numbered step completion. Closes the mid-task session-loss gap (TASK-STATE.yaml is task-level only). Layer 3 / action-level state tracking explicitly out of scope.
- **Executor Rule 16: CHECKPOINT** in `templates/executor-prompt.md` — Write SESSION-STATE.md after every numbered step.
- **Resume check (Dependency Check step 5)** in `templates/executor-prompt.md` — Read SESSION-STATE.md before starting; resume at first incomplete step if Status is `in_progress` for the requested task.

### Changed
- **`core/VERIFICATION.md`** — "Six components" → "eight components." Sections renumbered for Read-Back Verification insertion at §3.
- **`HARNESS.md` Routing Table — "Resuming a project" row** — Load order updated from `active_project.md → PROJECT.md → TASK-STATE.yaml → 00-REFERENCE-rules.md` to `active_project.md → SESSION-STATE.md → TASK-STATE.yaml → active task file → 00-REFERENCE-rules.md`. SESSION-STATE.md (~150 tokens) is more specific than PROJECT.md (~500 tokens) for resume; the active task file is added because SESSION-STATE points to it.
- **`HARNESS.md` Routing Table — "Scaffolding a new project" row** — Includes `templates/session-state-template.md`.
- **`HARNESS.md` Bootstrap Protocol step 2** — Scaffold list includes `SESSION-STATE.md` initialized to `ready` / Active task `none`.
- **`HARNESS.md` Truth Layer tree** — Adds `session-state-template.md` to the templates listing.

---

## v4.0.2 (2026-04-19) — Context optimization

### Changed
- **HARNESS.md Routing Table** — Added Role column (Planner/Executor/Either) and two new rows: "Resuming a project (context recovery)" and "Resolving a blocked task." Removed HARNESS.md from the review path. Prevents 500-2,000 tokens of unnecessary loading per context recovery or review event.
- **core/ATOMICITY.md** — Replaced stale 39-line task anatomy code block (missing v4 fields `risk_level`, `Baseline`, `Evidence Trail`) with reference to `templates/task-template.md`. Compressed Key Design Principles to bullet list, Content Delivery Modes to table. Added Pushback Protocol cross-reference.
- **core/VERIFICATION.md** — Compressed "What Verification Is NOT" to single-line-per-item format. Replaced escalation re-explanation in Pushback Protocol with cross-reference to ATOMICITY.md.
- **core/MEMORY.md** — Converted Platform-Native Memory integration prose to comparison table.
- **core/PRECEDENCE.md** — Compressed "Why a Single File" from paragraph to one sentence.

---

## v4.0 (2026-04-18) — Agent-agnostic refactor

### Philosophy
HyperWorker v4 is a ground-up refactor informed by research into Anvil's verification ledger, Karpathy's ratchet pattern, the folder-as-workspace architecture, Goose/OpenClaw agent systems, and the emerging harness engineering discipline. The five proven mechanisms are preserved and sharpened. A sixth mechanism (Verification) is added to address the documented failure mode of unproven completion claims.

### Added
- **HARNESS.md** — Self-bootstrapping entry point replacing HARNESS.manifest and core/SYSTEM.md. An AI agent reads one file and knows: what the system is, how to bootstrap a project, where every file lives, and what the six mechanisms enforce. Includes Routing Table, Truth Layer vs Mutable Surface boundary declaration, adaptive execution model, Bootstrap Protocol, and twelve Core Principles.
- **core/VERIFICATION.md** — Sixth core mechanism. Seven components: (1) Verification Checklist (sharpened: observable, specific items), (2) Evidence Trail (structured table recording what was checked and what happened), (3) Baseline-After Pattern (capture state before modification for regression detection), (4) Verification Checkpoint (promoted from SYSTEM.md, extended for mid-project use), (5) Ratchet Principle (from Karpathy: improvements kept, regressions discard the completion claim), (6) Risk Classification (standard/elevated/critical determining evidence requirements), (7) Pushback Protocol (executor flags concerns before executing rather than blindly proceeding).
- **Principle 12: "Prove completion, don't claim it."** — Evidence over assertion. Baseline-after comparison over "looks good."
- **Agent capabilities declaration** in config-skeleton.yaml — Operators declare what their AI agent supports (subagents, platform memory, hooks, MCP tools). The harness adapts its execution model accordingly.
- **"Works with" section** in README.md — Explicit agent-agnostic positioning listing Claude Code, Cursor, Goose, Copilot, and any capable LLM.

### Changed
- **Execution model: Worker → Executor, Orchestrator → Planner.** Platform-neutral terminology. The two roles (planning vs execution) are described by function, not by platform mechanism. Works with subagents, single-agent mode switching, or two separate models.
- **Core structure flattened.** `core/lock/LOCK.md` → `core/LOCK.md`, `core/atomicity/ATOMICITY.md` → `core/ATOMICITY.md`, etc. Five single-file subdirectories eliminated.
- **core/MEMORY-PIPELINE.md → core/MEMORY.md.** Simplified name. Strengthened platform-native memory integration section.
- **templates/worker-prompt-template.md → templates/executor-prompt.md.** Added Rule 14 (Pushback Protocol), evidence recording in Rule 10, risk_level awareness in dependency check.
- **templates/task-template.md** — Added `risk_level` field in YAML frontmatter, `## Baseline` section (optional), `## Evidence Trail` table. Verification checklist items now require observable, specific phrasing.
- **templates/config-skeleton.yaml** — Version 4.0. `platform` → `agent`. Added `capabilities` section. `worker` section → `executor` section. `orchestrator_model` → `planner_model`, `worker_model` → `executor_model`.
- **README.md** — Complete rewrite. Agent-agnostic positioning, six mechanisms, simplified getting-started (two steps), planner/executor terminology, new structure diagram.
- **VISION.md** — Six mechanisms, agent-agnostic philosophy, adaptive execution model principle, "prove completion" principle.
- **All case studies** — Updated terminology (Worker→Executor, orchestrator→planner, five→six mechanisms).
- **reference/FAILURE-MODES.md** — Updated for adaptive execution model, planner/executor terminology.
- **reference/VALIDATION.md** — Updated for HARNESS.md entry point, executor terminology.
- **reference/RESEARCH-PROTOCOL.md** — Updated SYSTEM.md reference to HARNESS.md.
- **starter/README.md** — Simplified to two-step quick start.
- **CONTRIBUTING.md** — Six mechanisms, executor terminology.

### Removed
- **HARNESS.manifest** — Absorbed into HARNESS.md "Truth Layer vs Mutable Surface" section.
- **core/SYSTEM.md** — Absorbed into HARNESS.md.
- **core/lock/, core/atomicity/, core/dependency/, core/memory-pipeline/, core/precedence/** — Empty subdirectories removed after flattening.
- **All Cowork-specific references** — Platform badge, tagline, and "Built for Claude Cowork" branding removed.
- **"v4 only if..."** language in VISION.md — v4 happened. The failure mode that the five mechanisms couldn't address was unproven completion claims.

---

## v3.1.1 (2026-04-15) — Memory scope default hardening

### Changed
- **MEMORY-PIPELINE.md example row** — Changed the LEARNINGS.md example from scope `Universal` to `Engagement:[ID]`. The most-read template was teaching the maximally-broad scope as the default, which causes cross-project contamination. This mirrors a fix the OpenClaw project made to their memory subsystem (defaulting to separated storage instead of unified).
- **MEMORY-PIPELINE.md** — Added an explicit "default to the narrowest scope that fits" rule. Universal now requires the operator to answer a disambiguation question before applying. Makes the principle match what VISION.md already claimed.
- **case-studies/02-software-feature-ship/SCENARIO.md** — Corrected two misapplied Universal scopes. DISC-001 (OAuth provider endpoint flakiness) is now `Provider:X`. DISC-003 (staging DB pool size) is now `Environment:staging`. The Universal tags were actively teaching the wrong pattern.

### Added
- **VISION.md** — Architectural constitution with explicit "What HyperWorker Will Not Become" section. Documents the Council #5 rejections (learning systems, feedback loops, meta-orchestration) as out-of-scope on purpose. Prevents re-litigation.
- **LICENSE** — MIT.
- **README.md** — Repo-level README (distinct from starter/README.md).
- **.gitignore** — Standard ignores, operator-sandbox directory excludes.

## v3.1 (2026-04-15)

### Added
- **HARNESS.manifest** — Machine-readable structural boundary declaration. Defines which files are harness infrastructure and which are project content. Addresses the blind test failure where Claude confused the harness with the project it was managing.
- **Verification Checkpoint** — Mandatory human confirmation gate for new projects. After scaffolding, the orchestrator pauses and asks the operator to confirm: project description, precedence tiers, and task breakdown. Prevents the AI from proceeding with wrong assumptions.
- **Startup Validation** — The orchestrator verifies harness structural integrity before executing any task (manifest readable, config populated, active project valid, task files exist).
- **RESEARCH-PROTOCOL.md** — Optional domain research protocol. When enabled, the orchestrator researches the user's domain before scaffolding, producing exactly two bounded outputs: a draft config and a draft reference file. Includes hallucination risk mitigations.
- **starter/README.md** — Quick-start guide for new operators.
- **CHANGELOG.md** — Version history.
- **Structural misfit detection** — Added to FAILURE-MODES.md. Documents the risk of projects that don't match harness assumptions (parallel tasks, multi-operator, non-sequential).
- **Harness version coexistence** — Added to FAILURE-MODES.md and config. Documents what happens when the harness evolves but existing projects remain on older versions.
- **Principle 11: "Verify before executing"** — New core principle in SYSTEM.md.

### Changed
- **SYSTEM.md** — Added role clarity header ("Read HARNESS.manifest before this file"), Getting Started section, Verification Checkpoint section. Updated architecture diagram to include manifest, config.yaml, starter/, and CHANGELOG.md.
- **Worker prompt template** — Added role clarity header ("You are a WORKER in a project management harness"), boundary awareness section referencing HARNESS.manifest, explicit rule against modifying harness infrastructure files.
- **Task template** — Added role clarity header ("This is a project task file").
- **Project template** — Added role clarity header ("This is a project file managed by the harness").
- **Rules template** — Added role clarity header ("This is the single source of truth for cross-cutting rules").
- **config-skeleton.yaml** — Added `harness_version`, `verification` section, `research` section.
- **VALIDATION.md** — Added Step 1 (Structural Verification) and Step 5 (Verification Checkpoint). Updated failure modes to include boundary confusion and checkpoint failure.
- **FAILURE-MODES.md** — Added structural misfit detection, harness version coexistence.

### Removed
- **Step 0 (formal onboarding workflow)** — Replaced by the Verification Checkpoint + optional Research Protocol. The blind test showed Claude's natural Q&A handles onboarding adequately; the gap was verification, not onboarding.

### Not Implemented (v4 candidates)
- Learning system / feedback loops (post-mortems feeding into case study libraries)
- Automated structural compatibility checking during scaffolding
- Cross-harness memory sharing
- Automated task chaining

## v3.0 (2026-04-15)

### Added
- Domain-agnostic core extracted from v2 (healthcare-specific)
- Five core mechanisms: Lock, Atomicity, Dependency, Memory Pipeline, Precedence
- Generic templates for all file types
- config-skeleton.yaml with all configurable parameters
- VALIDATION.md for domain testing
- FAILURE-MODES.md for known limitations
- SaaS validation case study (proved domain-agnostic design)
- Bakery test explanation (plain-language mechanism description)

### Changed
- All healthcare/vendor references removed from core
- Precedence tiers renamed to generic defaults
- Memory pipeline scope tags made configurable
- Worker prompt generalized (removed platform-specific rules)
