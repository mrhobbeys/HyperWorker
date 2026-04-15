# Changelog — Focus & Execution Harness

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
