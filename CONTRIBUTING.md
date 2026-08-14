# Contributing to HyperWorker v6.0.0

v5.0 is a structural test of a hypothesis. The bar for changes is high. This document explains what we want, what we don't, and how contributions are evaluated.

## What we want

- **New project schemas.** Domains under-represented in the shipped defaults. Each schema must include the full set: `schema.yaml`, `precedence-tiers.yaml`, `artifact-extensions.yaml`, `capability-gates.yaml`, `verification.yaml`, `council.yaml`, `project-template.md`, `rules-template.md`, `task-templates/`, README. Bar: meaningfully different from existing schemas (different domain extensions, different council composition, different default tasks). Use the marketing-campaign schema as the structural reference.

- **Per-model profile additions.** A new profile for a model not yet in `templates/models/`. Cite observed behaviors with evidence — postmortems, framework docs, sample-size-disclosed observations. Do not declare a model "worse" than another.

- **Sharper failure-mode documentation.** `reference/FAILURE-MODES.md` should grow as v5.0 is observed in real use. Document failures that fall *outside* any hypothesis in the spec — these indicate missing primitives.

- **Structural check refinements.** Better citation-validation logic, tighter recitation overlap heuristics, deterministic compression improvements. Each refinement must produce an effect verifiable without asking the agent if it complied.

- **Council convergence-rule additions.** New convergence patterns for new verification contexts. Document the trigger that motivates each pattern.

## What we don't want

- **A sixth mechanism.** Five mechanisms plus substrate. If a failure mode you observe seems to require a sixth, the first ask is: does the substrate's primitives compose to handle it? If genuinely not, surface the failure mode in an issue with the falsifiable hypothesis a sixth mechanism would test. Do not submit a sixth-mechanism PR cold.

- **Verbal-rule additions to the executor prompt.** The 30-line bound is load-bearing. If the agent needs to know something, encode it in the substrate (a schema, a citation, a Layer 1 check) — not as a rule the agent is asked to follow.

- **Auto-tuning, feedback loops, meta-orchestration, dashboards, hosted-service features.** All explicit non-goals (see `VISION.md` §What HyperWorker Will Not Become).

- **CLI implementations of `hw`.** `hw` is an agent protocol, deliberately. A binary CLI is a downstream tool, not core. We won't merge a Python or Node implementation that becomes the new dependency for using the harness.

- **Migration tooling from v4.1.1.** v5.0 is a clean break. Helping operators move artifacts from one harness to another is welcome as a separate downstream project; it is not part of v5.0.

## The bar

A change must either:

1. **Produce a structural check** the substrate can compute without asking the agent if it complied, OR
2. **Remove a primitive** that requires the agent's word.

A change that adds rules without structural enforcement fails the bar. A change that adds a primitive whose hypothesis we can't falsify fails the bar.

## How to contribute

1. Open an issue describing the failure mode the change addresses, or the schema/profile gap.
2. Reference which mechanism(s) are involved.
3. If submitting a PR, include a before/after showing the structural check (what the substrate now verifies that it didn't before).
4. For schema PRs, include a sample bootstrap walkthrough demonstrating the schema in use.

## Code of conduct

Be constructive. Be specific. Respect the scope boundaries.

---

# Updating and Contributing Schemas

This section is the canonical reference for schema work. v5.1.1 establishes a "core-substrate-with-schema-config" pattern that this guide makes explicit; if you are adding a new schema or extending an existing one, read all eight subsections before opening a PR.

## §1 — Schema directory layout

Every project schema lives under `schemas/projects/<schema-name>/` and contains the following files. All are required unless marked optional.

| File | Purpose |
|---|---|
| `schema.yaml` | Root metadata: `schema_id`, `schema_version`, `harness_version`, `description`, `bootstrap_questions`, `includes`, `default_tasks`. |
| `precedence-tiers.yaml` | Tier 1–4 precedence rules with `@@SCAN_n_m` markers at decision boundaries. |
| `artifact-extensions.yaml` | Schema-specific artifact kinds and `field_overrides` for OR base fields. |
| `capability-gates.yaml` | Capability-gate declarations including the v5.1.1 mandatory blocks (`scope_completeness`, optionally `external_state_readback`) and any schema-specific gates. |
| `verification.yaml` | Layer 1 / Layer 2 / Layer 3 check declarations specific to this schema. |
| `council.yaml` | Council members with roles, triggers, convergence rules, pass/fail conditions, and `context_asymmetry` framing. |
| `bootstrap-probe.md` | v5.1.1 — schema-specific probe instructions for `bootstrap.inventory_sweep`. May document a stub if the probe shape is awaiting first-project empirical signal. |
| `project-template.md` | The `PROJECT.md` template the bootstrap ceremony renders into the project root. Includes a `## Scope` section the inventory-sweep ceremony populates against. |
| `rules-template.md` | The `00-REFERENCE-rules.md` template; carries the schema's tier 1 NON-NEGOTIABLE language. |
| `task-templates/` | Per-task markdown templates. At least one required. Numbered prefix for ordering (`00-`, `01-` …); `zz-` for end-of-session tasks. |
| `README.md` | Schema-level docs: purpose, when to use, when not to use. |
| `artifact-templates/` | Optional. Schema-specific artifact-kind templates beyond the OR defaults (e.g., report-synthesis ships `source-template.md`, `claim-template.md`, `contradiction-template.md`). |

If you copy an existing schema as a starting point, expect to rewrite every file. Schemas are not lightly customized; they encode the domain's actual shape.

## §2 — Adding a new project schema from scratch

Step-by-step walkthrough.

1. **Pick the closest existing schema** (`marketing-campaign`, `report-synthesis`, `software-feature-ship`, `client-onboarding`, `event-planning`, or `compliance-audit`) and copy its directory to `schemas/projects/<new-name>/`.
2. **Rewrite `schema.yaml`.** Set `schema_id`, `schema_version: 1.0`, `harness_version: "6.0.0"`. Write `description` (2–3 sentences). Replace `bootstrap_questions` with questions appropriate to the domain (operating-reality fields plus any domain-specific scope declarations). Update `default_tasks.templates` to reference the new task templates.
3. **Rewrite `precedence-tiers.yaml`.** Identify Tier 1 (immutable source-fidelity / NON-NEGOTIABLE), Tier 2 (operator-asserted scope), Tier 3 (project-derived facts), Tier 4 (style / voice). Place `@@SCAN_n_m` markers at decision-boundaries. The compressed rules file (regenerated at bootstrap) carries these markers; the executor answers each via `task.scan` events.
4. **Rewrite `artifact-extensions.yaml`.** Declare any new artifact kinds the schema needs beyond the OR base set (decision, finding, anti-pattern, operating-reality). For each new kind, declare canonical fields + types. Use `field_overrides` to mark base OR fields optional or to widen their types.
5. **Rewrite `capability-gates.yaml`.** Declare the v5.1.1 mandatory `scope_completeness:` block (every schema accepts `[complete, deferred, excluded-after-discovery, escalated]` by default; tighten only if the schema's delivery shape genuinely forbids some terminal states). Declare `external_state_readback:` if the schema's tasks mutate external state. Declare any schema-specific capability gates (e.g., per-task-kind required tools).
6. **Rewrite `verification.yaml`.** Define Layer 1 checks specific to the schema (e.g., report-synthesis Layer 1 includes "every claim has a hash-citation"; marketing-campaign Layer 1 includes redirect-coverage). Layer 2 = pre-actuation council. Layer 3 = post-actuation evidence. Risk-level routing (standard / elevated / critical) goes here.
7. **Rewrite `council.yaml`.** Define members with context-asymmetric framing (members see the artifact + spec + acceptance criteria, not the implementer's chain-of-thought). Include domain-aligned members (e.g., `source-fidelity-watcher` for synthesis; `brand-voice-guard` for marketing-campaign) and `scope-shrink-watcher` for any schema with multi-candidate task surfaces. Declare triggers and convergence rule.
8. **Write `bootstrap-probe.md`.** Document the probe method for the v5.1.1 inventory sweep. If the probe shape is unclear without empirical signal, ship a documented stub that emits `bootstrap.probe_skipped` with a reason; mark for revision after the first project bootstraps under the schema.
9. **Write `project-template.md` and `rules-template.md`.** PROJECT.md should have a `## Scope` section with `### Included` and `### Explicitly Excluded` subsections; the v5.1.1 scope-completeness check reads bullets under `### Included`.
10. **Write at least one task template** under `task-templates/`. Convention: numbered prefix for ordering, `zz-` for end-of-session tasks. Each template's frontmatter declares `id`, `kind`, `schema`, `phase`, `risk_level`, `required_tools`, `delivery_mode`, `depends_on`, `consumes`, `acceptance_criteria`.
11. **Write `README.md`.** Cover purpose, scope, when-to-use vs when-not-to-use, the schema's hypothesis-under-test if any.
12. **Update root `README.md` and `HARNESS.md`.** Both list the available schemas; add the new entry.
13. **Add a CHANGELOG entry** under the current version with the format from §7 below: "Added schema: `<name>`. Reason: …"

## §3 — Extending an existing schema

For each extension type:

**Adding a task template.**
- Add file under `task-templates/`.
- Register in `schema.yaml` `default_tasks.templates`.
- Update `project-template.md` if the new task should be surfaced in default scope.
- If the task introduces a new artifact kind, also update `artifact-extensions.yaml`.
- If the task targets external state, ensure `capability-gates.yaml` `external_state_readback.required_for` covers it.

**Adding a council member.**
- Add to `council.yaml` with full block: `id`, `role`, `family_default`, `prompt_template` (or trigger-keyed pair), `triggers`, `pass_condition`, `fail_condition`, `context_asymmetry`.
- Update any task templates whose proposals should fire this member.
- Update `verification.yaml` if the member's PASS becomes a Layer 1 requirement.

**Adding a capability gate.**
- Add to `capability-gates.yaml`.
- Update task templates that the gate applies to.
- Update `tools/hw-verify.py` if the gate is enforced at Layer 1 universally; most gates are template-level guidance, not Layer 1 — be deliberate.

**Adding artifact-extension fields.**
- Add to `artifact-extensions.yaml`.
- Use `field_overrides` for OR base fields; declare new kinds in their own block.
- Always include `description`. Always include `type`, allowing union types where transitional (e.g., `string|list[string]|null`).
- For event-emitting fields (rare but possible), reference the event kind in `core/SUBSTRATE.md`.

## §4 — Core-substrate-with-schema-config patterns (v5.1.1 establishes this shape)

v5.1.1 introduces the pattern: a substrate primitive lives in `core/` with universal enforcement; schemas configure its trigger, payload defaults, or strictness via `capability-gates.yaml` (or another schema-side config file).

| Core primitive | Schema config |
|---|---|
| `scope.complete` event kind + Layer 1 check (universal) | `capability-gates.yaml` `scope_completeness.allowed_terminal_states` (per-schema strictness) |
| `external_state.read_back` event kind + Layer 1 check (universal mechanism) | `capability-gates.yaml` `external_state_readback.required_for` (per-schema opt-in with task patterns) |
| `bootstrap.inventory_sweep` ceremony (universal) | `bootstrap-probe.md` per schema (probe method per domain) |
| `redirect_implications` field on task-completion artifacts (marketing-campaign-specific in v5.1.1) | `artifact-extensions.yaml` `task_completion.field_overrides.redirect_implications` (schema declares the field, substrate aggregates at session.handoff) |

When contributing a schema, identify which core primitives apply and configure them. When contributing a core primitive, design the schema-config surface from the start; do not bake schema-specific assumptions into core. Core primitives should be schema-agnostic in their substrate machinery; the strictness and the trigger are schema-configurable.

A test for whether a primitive belongs in core: would more than one schema benefit from it? If yes, design it as core with schema-config. If no, keep it in the schema directly.

## §5 — `harness_version` and versioning

Every schema declares `harness_version` in `schema.yaml` to pin it to the substrate version it was designed against. The harness MUST refuse to run a schema whose `harness_version` exceeds the harness's own version. When the substrate bumps, schemas using new primitives bump their `harness_version` to match.

This project has a single operator. Breaking changes are allowed and expected. There are no backward-compat layers, no transition periods, no dual-form acceptance for new field shapes, and no exemption mechanisms for in-flight projects. When a substrate change requires a schema update, update the schema directly. When a schema change requires a project artifact update, update the project artifacts directly. (See §8 below for the full single-operator policy and the rare exceptions.)

`schema_version` is documentation of intent rather than a compatibility contract: bump on any meaningful change, with a one-line CHANGELOG note explaining what changed and what consumers should adjust.

| Version field | Bump on |
|---|---|
| `harness_version` | Any change in `core/` that the schema relies on. |
| `schema_version` | Any meaningful change to the schema's contract: new task, new council member, removed field, widened type. Bump even if backward-compatible — the version is documentation, not a gate. |

## §6 — Validation: `hw verify` and schema-specific checks

Before submitting a schema change, run:

1. **`hw verify`** against a minimal `events.jsonl` that exercises the schema's typical chain. Verify all Layer 1 checks PASS. Use `tools/hw-verify.py` as the reference implementation: `python tools/hw-verify.py --workspace <path>`.
2. **`hw verify` against a malformed events.jsonl** (missing required fields, wrong types, missing scope.complete before session.handoff). Verify Layer 1 FAILs with the expected error code.
3. **For new artifact kinds, verify hash-citation round-trip.** Serialize the artifact, hash it, cite it, dereference the citation, confirm bytes-equal.
4. **For new council members, simulate a proposal that should trigger the member.** Verify the member fires; verify both PASS and FAIL paths produce the expected `council.report` events.
5. **For new task templates, walk through the template manually** in a test project to surface any prompt ambiguity before contributors see it.
6. **For new capability gates, verify the gate's enforcement.** A capability gate that does not produce a structural failure when violated is documentation, not enforcement.
7. **For new bootstrap probes, run the probe** against a real project surface and verify the diff shape is correct.

A PR that does not include validation evidence in its description fails review. The bar is "the substrate computes the check without asking the agent."

## §7 — CHANGELOG entry shape

Every schema change gets a CHANGELOG entry under the current harness version. Format:

```markdown
### Schema: <schema-name>

- **Added** `<feature>`. Reason: <one-sentence motivation>. (commit-hash)
- **Changed** `<field>` from `<old-type>` to `<new-type>`. Reason: <motivation>. (commit-hash)
- **Removed** `<feature>`. Reason: <motivation>. (commit-hash)
```

For substrate changes that affect multiple schemas, log under §Substrate then cross-reference under each affected schema's section. Example from v5.1.1:

```markdown
### Substrate

- **Added** `scope.complete` event kind. Reason: catch silent in-scope skips at session.handoff. (Patch 1, commit-hash)

### Schema: marketing-campaign

- **Added** `scope_completeness:` block in capability-gates.yaml. Cross-reference: Substrate Patch 1.
```

Include the commit hash so the diff is traceable from the CHANGELOG. Use the most descriptive commit hash if the change spans multiple commits (typically the final or merge commit).

## §8 — Single-operator policy and clean-break changes

This harness has a single operator. There are no in-flight third-party projects to protect, no public API contract, no shipped consumers depending on stable shapes. Breaking changes are allowed and routine.

When making a change that would normally require backward-compat:

- **Make the change cleanly.** Do not accept dual-form values, do not add exemption mechanisms, do not relax new requireds to "recommended" to grandfather in old projects.
- **Update any in-tree projects** (e.g., test fixtures, the `example-rebrand-rollout` project's PROJECT.md, any active `events.jsonl`) to the new shape in the same commit or an immediately-following commit.
- **Document what changed and what was updated** in CHANGELOG.

The two pre-ship fixes from V5.1-BUILD-REPORT.md (`fire_id` optional fallback, `brand_voice_anchor` dual-form acceptance) are exceptions, not the rule, and they were made strictly to preserve unmigrated v5.0.1 projects' validity. Future versions may tighten those back to single-form once the in-tree projects are caught up. The pattern is: introduce strictly, accept dual-form only when an in-tree project genuinely cannot be migrated in the same commit, and tighten when it can.

If at some future point this harness gains additional operators, this policy will need revision. Until then, prefer clarity over compatibility. Document any exception explicitly in CHANGELOG with the rationale, so the next person making changes does not mistake the exception for a precedent.
