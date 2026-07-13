# Schema: course-master-plan-test

> **Test schema for the course-master-plan pattern.** This is the in-build schema used by `projects/course-master-plan-test/`. After the L1 run validates the patterns, `hw schema save --from course-master-plan-test --as course-master-plan` extracts the brand-clean reusable schema. The `-test` suffix exists so the saved schema can use the canonical name without collision.

## What this is for

You have a course you want to build on a community-or-classroom platform (Skool, Circle, Mighty Networks, Discord+lessons, etc.). You have research, notes, and possibly a draft master plan. You want to:

- Discover the curriculum sequence from the corpus rather than locking it at bootstrap.
- Spawn per-module sub-projects when each module is ready to be designed and produced — without polluting the L1 master-plan project's context.
- Spawn per-content-piece sub-sub-projects (lesson scripts, video scripts, platform-specific promo) without polluting the L2 module project's context.
- Let the curriculum reorder as student feedback arrives, with the harness catching stale cross-references in published copy.
- Actuate platform entities (create modules, set tier gates, upload assets) with structural read-back verification.

This schema gives you all of that as a three-layer L1/L2/L3 orchestration pattern with a slug-premise-pause spawn protocol.

## When to use it

- Multi-module course on a platform that exposes admin-side module/lesson/asset creation.
- Curriculum sequence is genuinely uncertain — you want corpus-driven discovery, not pre-locked outline.
- Tier policy (free vs. paid, gated vs. open) may evolve as you learn what students value.
- You expect to publish modules incrementally, not as a single big drop, so cross-references between published modules will become stale on reorders.
- You want promo content to inherit voice/lens from the master plan without restating it per channel.

## When NOT to use it

- You already have a fully-locked module list and just need content production. Use a simpler content-pipeline pattern.
- The platform exposes no admin API or admin UI you can drive (everything is operator-typed). The `external_state.read_back` capability gate is load-bearing here.
- The course is a single live cohort with no persistent platform — actuation patterns don't apply.
- You don't need cross-project lens propagation (single module, one operator authoring everything in one place).

## What this schema gives you

**Three-layer L1/L2/L3 orchestration.** L1 owns the master plan and curriculum sequence; L2 owns per-module/per-task/per-promo design and platform actuation; L3 owns individual content pieces (lesson scripts, video scripts, channel-specific promo). Lens and curriculum decisions propagate L1→L2→L3 via cross-project artifact subscription.

**Slug-premise-pause spawn protocol.** Every L2 spawn (and every L3 spawn from an L2) follows the same shape: operator gives slug + premise → agent scaffolds skeleton → STOP, surface to operator → operator drops materials into `resources/` → operator says continue → agent inventories `resources/` and hands off. Layer 1 fails `child_project_pause_skipped` if a child project's T-001 fires without a paired `child_project.resources_ready` (or `resources_skipped`) event.

**Curriculum-as-DEC pattern.** DEC-001 is the curriculum sequence (module order + tier assignment + learning-objective summary). Reordering is a DEC-001 supersede that fires the v5.0 ratchet on in-flight L2 projects citing the prior hash. `redirect_implications` field on completion artifacts captures stale cross-references in already-published lesson copy.

**Tier policy as DEC with append-only movement history.** DEC-002 is the tier policy. `policy_mode: evolving` (default) lets modules move between free/paid tiers; each move is a DEC-002 supersede with documented reason. `movement_history` accumulates so patterns surface over time.

**Platform actuation with manual-attestation read-back.** L2 actuation tasks navigate the platform via Claude in Chrome (operator-named browser codename), emit `external_state.read_back` with `equality_method: manual-attestation`, and trigger a `friction.log` REGRESSION/OPERATOR-CONFUSION entry if divergence is detected.

**Lens anchor as `list[string]`.** OR-001.lens_anchor inherits the marketing-campaign `brand_voice_anchor` widening pattern. First-listed dominates; additional entries hold for cross-channel coherence. Lens guides voice/framing; module premises are discovered from operator's actual learning, not pre-determined by the lens.

## Phase shape

**Phase A — Setup, intake, platform familiarization.**
- A.1 (T-000) — Bootstrap inventory sweep on `inputs/`. SHA-256 dedup, source registration, operator scope reconciliation.
- A.2 (T-001) — Platform familiarization. One-time-per-cycle walk of the platform's admin nav; produces `<project root>/<platform>-site-guide.md`.
- A.3 (T-002) — Curriculum corpus scan. Surface 2-3 plausible curriculum structures; operator picks/refines/supersedes; capture as DEC-001 + DEC-002.

**Phase B — L2 spawn cycle (repeating).** Per operator-initiated module/task/promo: scaffold L2 project skeleton, emit `child_project.scaffolded`, STOP, await operator continue, emit `child_project.resources_ready`, register in spawned-project registry. L2 execution happens in its own session.

**Phase C — Reordering and tier-move handling.** Operator initiates a reorder or tier move → DEC-001 (or DEC-002) supersede → ratchet flags affected in-flight L2 projects → operator decides per-project (keep, pivot, park) → redirect_implications spawned for affected published copy.

**Phase D — Wrap.** When DEC-001 is fully spawned (or operator wraps mid-roster), `hw schema save --from course-master-plan-test --as course-master-plan` extracts the validated brand-clean schema. Optional second save: `<platform>-site-explorer` if A.2 produced enough portable platform-actuation pattern.

## What this schema is NOT

A content production system. L1 produces the master plan; content production happens in L2 modules and L3 content-pieces. L1 does not author lessons, scripts, or promo copy.

A direct platform integration. Platform actuation runs through a browser-driven agent (Claude in Chrome or equivalent). No platform API integration is assumed — though if one exists, `external_state.read_back.equality_method` can shift from `manual-attestation` to `rest-roundtrip` per task.

A multi-author tool. One operator + one or more agents per session. L2/L3 projects are operator-launched in their own sessions; they do not run concurrently inside L1.

## Bootstrap

```
hw bootstrap --schema course-master-plan-test --name <project-id>
```

Or, for the inheritance-from-source build:

```
hw bootstrap --schema custom --inherit-from report-synthesis --name <project-id>
```

The schema asks for: course name, course URL, platform, admin user, test member (optional), lens anchor (list), cross-project scope tag, tier policy mode, promotion scope, active model profile.

## Inherits from

- **`report-synthesis`** — T-000 source-inventory pattern (SHA-256 dedup, register-once); T-001 corpus-scan pattern adapted as the curriculum corpus scan; central-decision-as-DEC-001 pattern; Tier 1 verbatim quotation rule.
- **`marketing-campaign`** — `external_state.read_back` capability gate with manual-attestation; `redirect_implications` field pattern; scope-completeness Layer 1 check; `brand_voice_anchor: list[string]` widening pattern (renamed `lens_anchor`).
- **substrate primitives directly** — `ab-variant` delivery mode, `friction.log` auto-prompts, `bootstrap.inventory_sweep`, `session.handoff` projection.

## Novel primitives (proposed for substrate promotion in v5.1.2 if H-CB1 holds)

- `child_project.scaffolded` event kind — emitted when L1 finishes scaffolding an L2/L3 skeleton; pairs with operator-pause.
- `child_project.resources_ready` event kind — emitted after operator drops materials into the child's `resources/` and says continue.
- Layer 1 check `child_project_pause_skipped` — fails if a child project's T-001 fires without a paired `resources_ready` (or explicit `resources_skipped`) event.
