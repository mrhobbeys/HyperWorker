# Field Report — Machine 2 ("laptop"), July 2026 gather

Second-machine field gather for the HyperWorker repo. Scope: collect harness-applicable
friction evidence, import genericized schema packs, mechanical fixes only. All identities
below are genericized: real clients, vendors, brands, and paths are replaced with neutral
descriptions. Sources on the machine were treated read-only.

## Machine survey summary

- 16 HyperWorker installations found, versions spanning v4.1.1 → v5.2.0. Types: two v4.1.1
  reference copies, one v4.1.1-era archived workspace (pre-substrate, root `projects/` +
  `active_project.md`, no `.hyperworker/`), several v5.0 test-run installs (the 5.0 / 5.0.1 /
  5.1 / 5.1.1 test-report folders), and three v5.2.0 installs including one live production
  case (a vendor billing-dispute reconciliation).
- 11 live workspaces with `.hyperworker/events.jsonl` (7–297 events each). No workspace had
  more than one `.hyperworker/` directory; no literal simultaneous-instance violations found.
- ~80 schema pack copies total, almost all duplicates of the six stock packs. Four packs
  unique to this machine; three imported (below), one skipped.

## Schemas imported to `schemas/projects/` (genericized)

1. **`content-piece-test`** — one piece of creator content fanned out to three
   format-native variants (longform newsletter, longform social, video lead-ins).
   Inherits from `report-synthesis`. Novel patterns: operator voice as load-bearing OR
   field, interview with hard question budget, `verbatim_keeper` artifacts with
   hash-citation freshness, single-task three-variant ab-variant generation. Complete pack
   including artifact-templates.
2. **`book-edit-test`** — voice-preserving re-release edit of a shipped manuscript:
   per-chapter hermetic edit passes, `voice-anchor` + `banned-pattern` artifacts,
   unfinished-bits surfacing, round-aware corpus chains (`supersedes`/`superseded_by`),
   print-ready assembly. Complete standard shape (no artifact-templates dir).
3. **`course-master-plan-test`** — multi-module course build on a community platform
   (Skool/Circle-class). **Notable: this schema is itself a three-layer L1/L2/L3
   orchestration pattern** — L1 master plan spawns per-module L2 projects which spawn
   per-content-piece L3 projects, with a slug-premise-pause spawn protocol, cross-project
   artifact subscription for lens propagation, curriculum-as-DEC with supersede ratchet,
   and a `child_project_pause_skipped` Layer-1 check. Task-template series is truncated
   (only T-000–T-002 were authored before the run stalled); root files are complete.

### Found but not imported

- **`pm-site-explorer-test`** (project-management site explorer): only 4 of ~11 standard
  files (schema.yaml, council.yaml, capability-gates.yaml, bootstrap-probe.md). Incomplete
  pack bound to one platform-exploration run; recorded here per the
  `site-keyword-research` precedent.
- Project-instance workspaces (brand audits, a WordPress multisite migration, the vendor
  billing-dispute case) — instances, not reusable schema shapes.

## Mechanical fixes applied

- `content-piece-test/artifact-extensions.yaml`: two `{..., type: list[string], ...}`
  entries inside flow mappings — invalid YAML (`[` in flow context). Quoted to
  `"list[string]"`. The unquoted form parses fine in block context, which is why it
  survived in the source; footgun worth knowing about. (Source copy left as-is,
  read-only rule.)

## Harness-critical friction evidence

### 1. Concurrent-writer event-log corruption — strongest corroboration of machine 1's one-writer finding

A WordPress multisite migration project (v5.2.0-era) hit a full, dated incident:
parallel council members appended to `events.jsonl` concurrently, producing EV-id
collisions (multiple EV-0033/0034/0035 lines), three chains forking from one tail event,
and broken hash chains. Four friction entries (F-011, F-014, F-018, F-019 — two marked
blocking) plus a decision record. Key quotes (close paraphrase, paths genericized):

> "The append-only event log primitive needs an explicit single-writer or file-lock
> convention; without it, parallel council members corrupt each other's appends." (F-011)

> "The substrate's H-S1 hypothesis ('append-only event log eliminates writers-disagree
> failure mode') was contradicted by parallel writers. Operator confirmed: this was a
> dispatch error, not a HyperWorker bug — the framework assumes single-writer; the
> dispatch broke that assumption." (decision record DEC-014)

The project's local fix: per-member draft files + one serial "convergence" writer. The
decision explicitly rejected waiting for a substrate file-lock primitive and closes with
the operator intending to file this upstream: "either the substrate gets a documented
serialization primitive, or the bootstrap protocol needs to make the per-file convergence
pattern explicit." **That substrate primitive still does not exist.**

Related: F-015 found a filename collision between dotted vs. underscore-normalized
council-projection filenames on case-insensitive Windows filesystems.

### 2. Hash-canonicalization defect recurred after being "fixed"

A book-edit run (v5.1.1-era) had its executor hand-roll an event emitter using Python
`json.dumps` defaults (`ensure_ascii=True`) while the reference verifier uses
`ensure_ascii=False`; 9 of 51 events failed the tamper check and `hw verify` FAILed,
requiring a manual ledger repair pass (F-006, the run's most severe entry). The same
serialization ambiguity was flagged in the very first v5.0 test run (entry B-1) and
closed in v5.0.1's CHANGELOG — evidence that a documented spec fix did not propagate
into executor tooling. The operator caught the executor about to log-and-move-on:
"We aren't trying to take shortcuts. Are we?"

### 3. Scope-completeness and verification-gate issues

- Silent in-scope skip: a task with no completion artifact simply vanished from active
  tracking under the v5.1 closing path; only structural enumeration surfaced it (FL-022).
  (v5.1.1's `scope.complete` event addressed this; the fix-run report nominates further
  tightening for v5.1.2.)
- Declared-vs-actual scope drift: a fresh CMS probe returned 58 published pages where the
  project declared 18 (FL-023); an earlier run inventoried 19 of 54 (FL-010).
- `hw-verify.py check_scope_completeness` anchors on `handoff_indices[-1]`; a retroactive
  fix-run appending `scope.complete` after a prior `session.handoff` produces a
  structurally false-positive FAIL (FL-024). **This bug is in a file that lives in this
  repo (`tools/hw-verify.py`); left unfixed here because it is a mechanism change —
  flagged for the primary session.**
- Pre-bootstrap territory is unmonitorable: a file-listing false-negative was propagated
  as a structural-gap claim because no `events.jsonl` exists yet, "the gap was claimed in
  territory the harness cannot self-monitor" (F-001, blocking).
- Verification overhead: "For tasks that emit 1-2 events the verification is heavier than
  the work itself" (C-4, first v5.0 run).
- Harness jargon blocked an operator decision gate until re-explained in plain language
  (F-003).
- Browser-automation worked example broke in the field: the documented REST-edit pattern
  was blocked by the browser tool's cookie/query-string guard, requiring an undocumented
  workaround (FL-025).

### 4. Amend/supersede gaps — reinforces machine 1's "no amend/supersede command" finding

From the migration project (F-027/F-028/F-029):

> "The supersede event payload is `{old_id, new_id, reason}` — no field for
> `supersede_kind: full | mechanism-only | scope-narrowing` and no field for
> `surviving_principles`… a fresh agent reading the chain cannot distinguish 'this
> decision is dead, ignore it' from 'its principle is alive and still load-bearing.'"

Also: the substrate's `reverses:` field is singular-only; one decision needed to reverse
three priors and was worked around with a YAML list plus three separate
`decision.supersede` events. Separately, operator mid-flow structural directives (e.g., a
secrets-minimization posture) have no documented `synthesis_role` tag — flagged twice as
a "substrate gap (repeat)".

### 5. Recurring/iterative delivery unsupported

The marketing-campaign templates "assume a single-winner selection model; real marketing
campaigns test multiple variants… task templates assume a linear single-draft workflow"
(FL-011/FL-012, v5.0.1 run). Reinforces machine 1's recurring-cadence finding at the
task-template level.

### 6. Secrets handling — machine 1's "secrets refused at `hw add`" plan is NOT yet real anywhere here

No substrate-level secrets gate exists in this corpus. Secrets discipline is entirely
project-level convention ("token lives in the executor env — NEVER in chat, this file, or
the bus"; "keys/passwords live on the respective boxes, never in bus files") plus one
Tier-1 code-review rule in `software-feature-ship`. Neither confirms nor contradicts the
v5.3 plan; shows the field currently self-enforcing what the plan would structuralize.

## Rule-breaking / orchestrator usage — collect, don't design

### A live orchestrator layer above a locked project

The vendor billing-dispute case (v5.2.0, production, not a test) has an explicit
"Orchestrator" brief above the harness: "You are the ORCHESTRATOR… You own the entire
case end to end." It defines three parallel tracks. After HyperWorker adoption, the
status doc reads: "Active locked project: [the reconciliation]… **Tracks B and C parked
in backlog.md**" — and the workspace's `backlog.md` confirms both tracks parked as
BL-001/BL-002 ("Parked: secondary to the reconciliation must-win"). The single-project
LOCK forced two of three live tracks into the backlog, with the orchestrator persisting
as an extra-harness coordination layer.

### A perpetual cadence task with no archive trigger

Same case: a scheduled check-in task runs every ~2h two days a week (cron
`0 8-18/2 * * 1,4`) against a live dispute, with a WAITING-PERIOD HOLD rule and no
closure condition. It predates and outlives the locked project. Direct evidence for
machine 1's "recurring cadence with no substrate primitive" and "perpetual projects with
no natural done" findings.

### A hand-built multi-agent concurrency-control roster

The migration project's DEC-064 defines a standing roster: an orchestrator agent that
"plans, reviews, opens/closes loops," plus two executor agents with hard lane boundaries
(one server-side, one frontend; a frontend task needing a server change "OPENS A LOOP,
never does it directly"; conflicts arbitrated by the orchestrator). Rationale: "these
boundaries are what keeps parallelism from becoming two agents mutating the same
multisite from different directions." Built entirely outside HyperWorker's mechanisms.

### A cross-project meta-tracker over ~250 projects

A separate tracker tool on this machine (not part of HyperWorker) is explicitly designed
as the layer above: "~250 projects… The API process is the single writer… the API
serializes every write, so nothing corrupts," with subprojects nested via
`parent_project_id` to arbitrary depth, and a stated rejection of SQLite over synced
filesystems ("WAL/journal sidecars desync"). Independently reproduces machine 1's
one-writer conclusion as a *solution*, and evidences the demand for multi-project
tracking above the lock.

### An L1/L2/L3 orchestration pattern encoded INSIDE a schema

The imported `course-master-plan-test` schema formalizes umbrella + subproject + 
sub-subproject spawning (slug-premise-pause protocol, cross-project artifact
subscription, Layer-1 `child_project_pause_skipped` check). The rule-breaking usage has
graduated from ad-hoc workaround to a written, gated schema pattern.

### Counter-evidence: discipline also absorbs the pressure

An older workspace's backlog routes two recurring needs ("Repeatable Content Engine…
on recurring cadence"; "Runbook Maintenance Protocol… review cadence per phase") into
*discrete, closeable* future harness projects rather than perpetual ones — the operator
sometimes re-scopes to stay inside the Lock model instead of building around it.

### The design contradiction, stated plainly

VISION.md (both v4 and v5 lines): "**We are not building a meta-harness**… If an
operator needs many parallel projects, run many harness instances." LOCK.md: "If parallel
workstreams are needed, each gets its own harness instance." No cross-instance protocol
exists (FAILURE-MODES.md's own entries: no multi-operator support, no cross-harness
memory sharing, no version-coexistence/migration path, structural-misfit detection never
shipped). The field evidence above shows the operator building exactly the rejected
layer — orchestrator briefs, rosters, meta-trackers, in-schema L1/L2/L3 — because the
design punts coordination without providing it. Decision belongs to the operator and the
primary session; this report only records that both VISION.md's position and the field's
contradiction of it are real and dated.

## Version-history notes (from local CHANGELOGs and patch prompts)

- The v5.0 reframe is stated as: v1–v4 asked "how do we make the agent follow rules
  reliably?"; v5.0 asks "how do we make compliance structurally enforceable rather than
  verbally requested?" No migration path from v4.1.1.
- A v5.1 pre-ship fix prompt caught a backward-compat break (`fire_id` required on
  council events would fail v5.0.1-era chains) — relevant precedent for any future
  validator tightening.
- The v5.2.0 mega-prompt explicitly defers a "workflow/knowledge layer split" as a
  "v6 contingency, not yet justified empirically" — the only v6 reference found.
- A patch prompt states the single-operator assumption baldly: "Breaking changes are
  allowed and expected. No backward-compat layers… no exemption mechanisms for in-flight
  projects."

## Repo/process discrepancy noted during this gather

At gather start, machine 1's push (v5.2.1 baseline + eight schemas + ecosystem tools) was
absent from the canonical remote — it had been sitting behind an operator approval gate
on the Gitea side and landed mid-gather. Worth a process note: field sessions should
verify `origin/main` actually contains the expected baseline before diffing, and pushes
should be confirmed landed, not just sent.

## Corroboration scorecard vs machine 1

| Machine-1 finding | This machine |
|---|---|
| Orchestrator layers built above the lock | **Reinforced** (billing-dispute orchestrator; agent roster; meta-tracker; in-schema L1/L2/L3) |
| One-writer rule after shared-event-log corruption | **Strongly reinforced** (full dated incident + decision record; tracker tool independently adopts single-writer) |
| Recurring `cadence` fields with no substrate primitive | **Reinforced** (cron cadence task; backlog "recurring cadence" items; single-winner template friction) |
| Perpetual projects with no natural "done" | **Reinforced** (cadence task with no closure condition; parked tracks) |
| No built-in amend/supersede command | **Reinforced** (supersede payload gaps F-027/28/29; singular-only `reverses:`) |
| Checked claims (v5.3 plan) | Adjacent support only ("prove completion, don't claim it" lineage; operator anti-shortcut challenge) |
| Test-gated exclusion (v5.3 plan) | No matching material found |
| Secrets refused at `hw add` (v5.3 plan) | No such gate exists in field; secrets are project-convention only |
