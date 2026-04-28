# Mechanism: Typed Artifacts — Decisions, Findings, Anti-Patterns, Operating-Reality

> Decisions, findings, anti-patterns, and operating-reality are universal cross-cutting concerns of project work. v5.0 makes them addressable, citable, hash-verified, immutable structures over event-sourced substrate. The lifecycle pipeline that v4.1.1 used (DISCOVERIES → LEARNINGS → ARCHIVE) is removed. Validation is a *field*, not a *lifecycle*; supersede semantics replace deletion.

This mechanism replaces v4.1.1's Memory mechanism. The shape of the change: knowledge is no longer a flow through validation gates; it is a set of immutable structured records with hash citations. Operators do not curate a queue; the substrate makes superseded knowledge visible by hash drift.

---

## Hypotheses

| ID | Claim | Falsifier |
|---|---|---|
| H-T1 | Decisions, findings, anti-patterns, and operating-reality, made addressable and hash-cited, replace mutable Memory without losing the captured-knowledge use case. | Operator reports needing the v4.1.1 DISCOVERIES → LEARNINGS pipeline to capture something the four kinds plus supersede cannot represent. |
| H-T2 | Per-project schema customization preserves harness agnosticism while enabling domain fit. | Operator forced to override default schemas in ways the design did not anticipate. |
| H-T3 | The consumption protocol (citation, recitation, SCAN) closes the gap between "the artifact exists" and "the agent's output reflects the artifact at the decision moment." | Cross-task carry-forward failures persist in observation. |

---

## What an Artifact Is

A typed artifact is an event-sourced, ID'd, hash-citable, schema-validated record. The harness defines the substrate machinery (event sourcing, projection rendering, citation validation, supersede semantics). The schema declares which kinds exist, what fields each kind has, and how they validate.

| Concern | Layer |
|---|---|
| Substrate (events, projections, hashes, citations) | `core/SUBSTRATE.md` |
| Default kinds and structural minimum | This file. |
| Per-project schema extensions | `schemas/projects/<name>/artifact-extensions.yaml` |
| Per-kind structural defaults | `schemas/artifacts/<kind>.yaml` |

---

## Structural Minimum

Every artifact, regardless of kind or schema extension, has these fields:

```yaml
id: <PREFIX>-<NNN>          # DEC, F, AP, OR — see Default Kinds
kind: <kind>
created_at: <ISO 8601>
hash: sha256:<short>        # filled by harness on projection render
confidence: provisional     # provisional | validated  (only meaningful for finding)
reverses: null              # or "<KIND>-<ID>" if this artifact supersedes a prior one
tags: []                    # free-form; used for filter and cross-project visibility
```

Every kind extends the structural minimum with kind-specific fields. The schema validates both layers.

---

## Default Kinds

Four kinds ship as defaults. Projects use them as-is, extend their fields via `artifact-extensions.yaml`, replace them, or ignore.

### Decision (DEC)

A choice made during the project, with the alternatives considered and the rationale. Citable to anchor downstream work to the choice's identity, not its prose.

```yaml
id: DEC-007
kind: decision
created_at: 2026-04-26T11:42:00Z
hash: sha256:a3f9c2b1e0f4
title: "Use schema X for tone-of-voice in nurture sequence"
alternatives_considered:
  - "Use schema Y (rejected: misaligned with brand baseline)"
  - "Allow per-email tone variation (rejected: increases consumed-inputs complexity)"
rationale: "Schema X aligns with the brand baseline tone of OR-001 and was successfully used in DEC-005."
constraints_imposed:
  - "All emails in this project consume DEC-007 in their consumes list."
reverses: null
tags: [tone, brand]
```

Decisions are append-only. Reversal happens by writing a new decision with `reverses: DEC-007`; the old decision projection still exists, but downstream tasks will see citation freshness drift if they cited the old hash.

### Finding (F)

A discovered fact about the world, with evidence and confidence. Findings are immutable; correction is supersede, not edit.

```yaml
id: F-014
kind: finding
created_at: 2026-04-26T13:10:55Z
hash: sha256:b8d4e1779a02
title: "Brand voice survey 2026 favors plain language over technical jargon at 7:1 ratio"
evidence: "Survey N=432, run 2026-03-15. Source: brand-survey-2026.csv (committed at <commit-sha>)."
confidence: provisional        # promote with hw promote F-014
applies_to: "nurture-sequence/* and landing-page/*"
implications:
  - "Tier 4 STYLE rule should prefer common-noun phrasing over jargon."
reverses: null
tags: [brand, voice, customer-research]
```

A wrong finding is corrected by writing a new finding with `reverses: F-014`. The chain of supersedes is visible via `hw verify`; nothing is deleted.

### Anti-pattern (AP)

A thing that does not work; high retention, never auto-aged.

```yaml
id: AP-005
kind: anti-pattern
created_at: 2026-04-26T15:00:00Z
hash: sha256:c1d2e3f4a5b6
title: "Click-method automation on the custom-app-X dashboard"
triggers:
  - "Plan involves automating actions in custom-app-X."
applies_to: "custom-app-X/dashboard/*"
why_it_fails: "Dashboard rerenders the DOM on every selection change; click-replay produces detached element errors."
alternatives:
  - "Use the custom-app-X public API."
  - "Use a screen-reader-based selector strategy with explicit wait-for-rerender."
regression_test: "tests/anti-005.md"
tags: [custom-app-x, ui-automation]
```

Anti-patterns are typically the highest-retention artifacts. They tell agents what *not* to do; the cost of forgetting one is repeating a known failure. They are never archived; they are only superseded if the underlying behavior changes (rare).

### Operating-reality (OR)

The fixed constraints of the project as the operator experiences them: budget, timeline, team, authority. Declared once at project bootstrap, updated only on real change.

```yaml
id: OR-001
kind: operating-reality
created_at: 2026-04-25T10:30:00Z
hash: sha256:d2e3f4a5b6c7
budget:
  amount: 500
  currency: USD
  frequency: monthly
timeline:
  hard_deadline: "2026-06-15"
  soft_target: "2026-06-01"
team:
  operator: "Spencer"
  role: "solo"
  others: []
authority:
  can_decide: ["tooling", "scope-within-stated-objective"]
  requires_approval: ["budget_increase", "scope_expansion"]
operator_profile: "solo-operator-modest-budget"
reverses: null
tags: [foundation]
```

Tasks consume `OR-001` when their plan could violate any of these constraints. The operator-reality-calibrator council member (see `core/VERIFICATION.md`) reads `OR-001` as primary input.

**v5.1 optional fields.** OR-001 may declare `delegation_policy` and `model_selection_policy` to capture operator engagement and cost preferences once at bootstrap. Both are optional; omitted fields inherit harness defaults. See `templates/artifact-templates/operating-reality-template.md` for field semantics, and `core/ATOMICITY.md` for how `delegation_policy` is consulted at task dispatch (soft enforcement: the agent reads the field and decides; v5.1 does not block dispatch when the policy is violated). `model_selection_policy.prefer` resolves through the per-model profile rankings declared in `templates/models/*.yaml` and `templates/models/_ranking.yaml`.

---

## Schema Extensions

A project schema declares additional fields for any kind. Extensions add fields; they do not remove or rename structural-minimum fields.

`schemas/projects/<name>/artifact-extensions.yaml`:

```yaml
decision:
  additional_fields:
    - name: revenue_impact
      type: number
      required: false
      description: "Estimated revenue impact in USD over 12 months."
    - name: stakeholders_consulted
      type: list[string]
      required: true

finding:
  additional_fields:
    - name: replication_steps
      type: string
      required: false
      description: "How another agent could reproduce this finding."
```

Validation order: structural minimum, then default kind schema (`schemas/artifacts/<kind>.yaml`), then extensions. Failure at any layer rejects the event.

---

## Projection Rendering Protocol

Every artifact projection is regenerable from its event chain. The protocol:

1. Locate all events for `artifact_id`: the original `<kind>.add`, any subsequent `<kind>.promote`, and any `<kind>.supersede` that *targets* this ID (i.e., a different artifact with `reverses: <this-id>`).
2. The current state is the original `add` payload, with:
   - `confidence` upgraded if any `<kind>.promote` event exists for this ID.
   - `superseded_by: <new-id>` added if any `<kind>.supersede` event targets this ID.
3. Render to markdown:
   - YAML frontmatter with all fields in canonical order: `id`, `kind`, `created_at`, `hash`, `confidence`, `reverses`, `superseded_by`, `tags`, then schema-defined fields alphabetically.
   - Body: kind-specific markdown sections (the `body:` field of the event payload, if present, rendered as the body section).
4. Compute SHA-256 of the file content; record short-hash in `hashes.json` and update the `hash:` field in the projection on the next render.

Two agents rendering from the same event prefix MUST produce byte-identical output. If they don't, the rendering protocol has a bug; report it.

---

## Citations

A citation is `[<KIND>-<ID>#<short-hash>]` (see `core/SUBSTRATE.md` §Citation Format). Citations appear in:

| Location | Purpose |
|---|---|
| Task frontmatter `consumes:` | Hermetic working set. |
| Task instruction body | Reference within the prose. |
| Decision `constraints_imposed`, finding `implications`, anti-pattern `alternatives` | Cross-artifact relationships. |
| Project rules (`00-REFERENCE-rules.md`) | Anchoring a rule to a decision or finding. |

Layer 1 verification (see `core/VERIFICATION.md`) checks every citation on every event. Stale citations block writes.

---

## Consumption Protocol

A typed artifact in events is dead until consumed. The consumption protocol forces the agent to anchor its consumed inputs at the decision moment, not at task start.

### Citation requirement

Tasks declare `consumes:` in frontmatter. At delegation time:

- If any cited artifact does not exist → task is `blocked` with `reason: missing_consumes`.
- If any cited hash is stale → task is `blocked` with `reason: stale_consumes`. The planner updates `consumes:` to the current hash (after re-validating that the new artifact still applies).

### Recitation

Before any state-changing tool call (any tool that writes a file, sends a message, or modifies external state), the agent updates `consumed-inputs.md` with a paraphrase of each consumed artifact in its own words.

The recitation file format:

```markdown
# Consumed Inputs — T-007

## [DEC-002#a3f9c2b1e0f4]
**Title:** Use schema X for tone-of-voice
**Paraphrase (agent):** The decision says we use brand-voice schema X for all nurture-sequence content; alternatives Y and per-email variation were rejected because of brand-baseline alignment and consumed-inputs complexity.

## [F-014#b8d4e1779a02]
**Title:** Brand voice survey favors plain language 7:1
**Paraphrase (agent):** The finding says a 2026-03-15 survey of 432 respondents preferred plain language over jargon at 7:1; this implies our Tier 4 STYLE rule should prefer common-noun phrasing in customer-facing copy.

## [OR-001#d2e3f4a5b6c7]
**Title:** Operating reality for Q3 launch
**Paraphrase (agent):** The operator runs solo on a $500/month budget with hard deadline 2026-06-15; budget increases require approval; scope expansion requires approval.

## [AP-005#c1d2e3f4a5b6]
**Title:** Click-method automation on custom-app-X
**Paraphrase (agent):** Click-replay automation breaks on this dashboard; we should use the public API or a screen-reader strategy with explicit wait-for-rerender.
```

The harness emits a `task.recite` event for each entry containing `{task_id, consumed_id, paraphrase, overlap_score}`. The `overlap_score` is computed by Layer 1 verification:

- Tokenize paraphrase and the source artifact's title + body.
- Compute Jaccard overlap on stemmed tokens (lowercase, drop stopwords, simple Porter-style stemming).
- If overlap < `recitation_overlap_threshold` (declared in the active model profile; default 0.7) → reject the recitation. The agent is asked to re-paraphrase.

Overlap below threshold often means the agent paraphrased something it didn't read. Above-threshold overlap means the agent's words and the source's words share enough lexicon to be plausibly the same content. This is a structural attention restoration check, not a meaning check; it does not catch all paraphrase failures, but it catches the ones where the agent skimmed and produced a generic restatement.

### SCAN markers

Each tier section in `00-REFERENCE-rules.md` ends with one or more SCAN markers:

```markdown
### Tier 1: BRAND-ABSOLUTE (absolute — never override)
- No income guarantees or implied earnings claims.
- No fabricated testimonials or case studies.
- ...

@@SCAN_1_1: List the Tier 1 banned phrase categories that apply to this task's output.
@@SCAN_1_2: Confirm the unsubscribe link and physical mailing address requirements apply to this output (yes / no / not-applicable).
```

Before any state-changing action, the agent emits a short answer to each marker via `task.scan` events. The answers are written into the task's working log; the harness does not re-run them every action, but they MUST appear at least once before the first state-changing event in the task.

The point of SCAN is not the answer's correctness; it is **forcing the model to generate output that touches each rule section**. Output token generation restores attention to the section the marker pointed at. Passive re-reading does not. (Pattern from dev.to/nikolasi.)

The cost of SCAN markers per task: empirically under 0.5% of context.

### Compression

Reference content (rules, schemas, default templates) is regenerated in two forms when the project loads:

| Form | Path | Used by |
|---|---|---|
| Human-readable | `00-REFERENCE-rules.md`, etc. | Operator. Edited directly. |
| Compressed | `00-REFERENCE-rules.compressed.md` | Agent prompt. |

Compression rule: code, paths, IDs, dates, version numbers, currency amounts, and quoted strings pass through byte-for-byte. Only prose compresses. The compressor is documented; the agent runs it as a deterministic transform on every render.

The compressed version is what enters the agent's prompt. The human-readable version is what the operator edits. The compressed file is a projection (regenerated on every change to the source), and its hash is in `hashes.json`.

This is the "caveman" approach (per pattern #3 in the v5.0 research): aggressive compression of prose with strict preservation of structured tokens.

---

## Confidence and Validation

Findings carry `confidence: provisional` or `confidence: validated`. Other kinds also accept the field but typically default to `validated` (decisions are made; operating-reality is declared; anti-patterns are observed).

**Promotion** is `hw promote <artifact-id>` (see `core/SUBSTRATE.md`). Tasks may declare in their `consumes:` that they require validated findings only; the harness rejects delegation if any cited finding is provisional and the task forbids it.

**Demotion** does not exist as an operation. To downgrade a finding, supersede it with a new finding at lower confidence and `reverses: <old-id>`. Promotion and demotion are not symmetric; this is intentional. Validation is a one-way ratchet; un-validating means the artifact was wrong, which is captured by supersede.

There is no DISCOVERIES → LEARNINGS gate. There is no archive. There is no expiry. Findings live as long as they are not superseded. Anti-patterns live until the underlying behavior changes (rare). Decisions and operating-reality live until the project archives.

---

## Cross-Project Visibility

By default, artifacts are scoped to the project that emitted them. Cross-project read access is opt-in via tags:

- An artifact tagged `cross-project:<scope>` is visible to other projects whose `config.yaml` includes that scope in its `cross_project_subscriptions:`.
- Visibility is read-only. A subscribing project sees the artifact and can cite it; it cannot supersede it.

Cross-project citation looks identical to local citation: `[F-014#b8d4e1779a02]`. Layer 1 resolves it by searching the local project first, then the cross-project subscription set.

This replaces v4.1.1's Universal/Vertical/Client/Engagement scope taxonomy. Operators who used the four-level hierarchy now use tags + subscriptions: a `Universal`-equivalent artifact is one tagged `cross-project:all`; a `Client:AcmeCorp`-equivalent is `cross-project:client-acmecorp`. The mechanism is more general; the operator does the categorization in tags.

---

## Why Not a Lifecycle

v4.1.1's Memory pipeline was: capture → human-validate → enter active → age out → archive. The pipeline assumed knowledge ages, gets stale, and needs proactive aging. v5.0 replaces this with:

- **Append-only events.** No knowledge is lost; supersede preserves the prior state.
- **Hash citations.** Stale knowledge is not silently aging; downstream artifacts citing it produce stale-citation failures at Layer 1, immediately and visibly.
- **Tag-based visibility.** Cross-project pollution is opt-in, not the result of a misset scope tag.
- **No archive.** The "off the critical path" idea is replaced by: stop citing it, and it stops affecting decisions. The artifact remains in events; it just no longer flows into prompts.

If an operator wants the v4.1.1 pipeline back, they can implement it on top of this substrate by adding a `lifecycle:` field via schema extension and writing periodic-review tasks. The harness does not enforce the pipeline; it provides the substrate.

---

## Live-Edit Proposal Artifacts (v5.1.1)

When a task declares `delivery_mode: live-edit` (mutating a published asset directly rather than producing a draft for the operator to ship), the proposal artifact a task produces in its enumeration step takes a specific shape. This shape feeds the v5.1.1 `scope-shrink-watcher` council member; without it, the member has no input.

**Required enumeration buckets.**

| Bucket | Meaning |
|---|---|
| `edit_candidates` | Existing items on the live surface that warrant modification, each paired with the proposed change. |
| `create_candidates` | New items the mission implies should exist on the surface, each paired with the proposed creation. |
| `delete_candidates` | Existing items the mission implies should be removed, each paired with the proposed removal. |

The enumeration is exhaustive at proposal time. The proposal does not pre-prune any candidate based on perceived effort. The pruning decision happens in council review, where `scope-shrink-watcher` checks that every enumerated candidate is either actuated, deferred with reason, or marked excluded-after-discovery with reason — never silently dropped.

**Per-candidate fields.** Each candidate is an object:

```yaml
- id: <stable-identifier-on-the-surface>
  surface_ref: "<URL or platform-specific reference>"
  current_state_summary: "<one-sentence description of what is there now>"
  proposed_change: "<what the actuation would do>"
  estimated_effort: low | medium | high
  disposition: actuate | defer | excluded-after-discovery
  disposition_reason: "<one sentence; null only when disposition: actuate>"
```

**No-create-alternative shape.** For task templates whose surface has no plausible create alternative (e.g., a single-string-edit task on a fixed-shape platform field — phone number, business hours, license number), the template explicitly states "no `create_candidates` expected for this task shape — single-field edit only." That note is itself the structural signal that the omission was intentional, not a scope-shrink slip.

**Schema integration.** Schemas that ship live-edit task templates also ship the `scope-shrink-watcher` council member in `council.yaml`, with the appropriate triggers and convergence framing. v5.1.1 enables this for marketing-campaign; other schemas adopt as their delivery shape requires.

---

## Relationship to Other Mechanisms

| Mechanism | Interaction |
|---|---|
| Lock | Artifacts are scoped to the active project unless tagged for cross-project visibility. |
| Atomicity | Tasks declare consumes; recitation projection lives at the task level. |
| Verification | Layer 1 runs citation freshness, schema validation, and recitation overlap on every event. |
| Precedence | Rules in `00-REFERENCE-rules.md` may cite artifacts (e.g., a Tier 1 rule citing `[OR-001#hash]` to anchor budget compliance). |
