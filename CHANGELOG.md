# Changelog — HyperWorker

## 6.0.0 (2026-08-14) — UNRELEASED, in progress

The unification release. Two lines of development that had diverged at `2e1fd54` — `main` (field-derived schema packs plus the over-specificity sweep) and `v5.3/programs` (Programs, ongoing lifecycle, single-writer rule, checked claims) — are merged here on `v6.0/unification`, and the harness version is made coherent across every file that declares one. The major bump is warranted by the substrate additions carried over from the v5.3 line, not by a breaking change to existing projects: v5.2.x projects continue to validate.

**This section is in progress.** Everything under §Landed is committed; everything under §Pending lands via subsequent commits before release.

### Landed — branch unification

- **`v5.3/programs` merged with `main`.** The two branches turned out to have touched disjoint file sets — `main` only the 13 field-derived schema packs, `v5.3` only `core/`, `tools/`, the top-level docs and the new `program` pack — so the merge carried zero conflicts and both sides survive intact. Verified structurally: after the merge, all 13 swept packs are byte-identical to `main`, and the only schema content differing from `main` is the new `program` pack.
- **Over-specificity sweep across the 13 field-derived packs** (from `main`, `a605b74`; previously undocumented here). Parameterizes what one operator's workflow had hardcoded, keeping the real vendor names as `e.g.` examples: ad network / mediation platform become bootstrap questions, and two site-monetization task templates are renamed accordingly — `02-adsense-plan.md` → `02-primary-network-plan.md`, `03-ezoic-optimization-plan.md` → `03-mediation-platform-plan.md`. State-portal, mail-provider, market and platform assumptions opened up; chat-session phrasing became project phrasing; operator residue removed (literal paths, browser codenames, real site metrics in acceptance criteria, real filenames). Methodology untouched.

### Landed — version coherence (fixes a functional bug)

- **Harness version set to `6.0.0` everywhere.** The repo had drifted into an incoherent state: `HARNESS.md` title said v5.2.1, the README badge said 5.2.1, `templates/executor-prompt.md` said v5.2.0, CONTRIBUTING §5 told schema authors to pin `harness_version: "5.2.0"`, and across the 20 shipped schemas 16 declared `5.2.0`, three declared `5.1.1`, and only `program` declared `5.3.0`.
- This was not cosmetic. CONTRIBUTING §5 states that *the harness MUST refuse to run a schema whose `harness_version` exceeds the harness's own version* — so a harness identifying as 5.2.1 was obliged to refuse the `program` schema pinned at 5.3.0, making the newest schema unrunnable by the rule the repo itself declares. The `5.1.1` stragglers were the mirror problem: schemas silently under-pinned against a substrate they actually depend on.
- Changed: `HARNESS.md` title, `README.md` version badge, `CONTRIBUTING.md` title and the §3 pin instruction, `templates/executor-prompt.md` preamble, and `harness_version: "6.0.0"` in all 20 `schemas/projects/*/schema.yaml` including `program`. Historical version references in prose (feature-provenance annotations such as "Execution mode (v5.2.0)", CHANGELOG history, and field-report observations) are deliberately left alone — they date when a primitive landed and are not declarations of the current version.

### Landed — shipped in 6.0.0: Programs, ongoing lifecycle, single-writer rule, checked claims

*(Formerly carried as "Unreleased (2026-07-14, branch `v5.3/programs`)". There is no separate v5.3 release; this work ships as part of 6.0.0.)*

The v5.3 core, derived from both field reports (`reference/field-reports/`). Four primitives and one bugfix; every primitive carries a hypothesis and falsifier.

- **Single-Writer Rule (`core/SUBSTRATE.md`, H-S5)** — one `events.jsonl` has at most one writer; parallel actors write draft files and one convergence writer appends serially. From two dated field incidents of concurrent-append corruption (EV-id collisions, forked chains). Layer 1 surfaces violations as `chain_breaks`.
- **Ongoing lifecycle (`core/LOCK.md` §Ongoing Projects, H-L2)** — `lifecycle: ongoing` projects work in cycles (`cycle.open`/`cycle.close` events, `CYCLES.md` projection, `hw cycle` protocol) with `next_due` computed onto the close event; `hw status` leads with OVERDUE when it passes. Replaces the field-improvised `deferred (ongoing)` terminal state and cadence-in-prose. `hw wrap` on an ongoing project is valid only when the recurring need itself ends.
- **Programs (`core/LOCK.md` §Programs, H-L3; new `program` schema)** — program-shaped work (N concurrent workstreams under one goal) is a schema, not a mechanism: each workstream runs in its own instance; the orchestrator is itself a locked project whose artifacts are a workstream registry (supersede-chained statuses), spawn-pause/promote/retire decisions, and read-only roll-up cycles citing sibling projections by path+hash. H-L1's field status recorded: not falsified. VISION.md's meta-orchestration position clarified, not reversed. Twenty schemas now ship.
- **Checked claims (`core/SUBSTRATE.md` §Checked Claims, H-S4; `core/VERIFICATION.md`; `tools/hw-verify.py --claims`)** — events asserting world-state may carry a machine-checkable predicate (`file_exists`, `file_absent`, `file_sha256`, `cmd_exit`, `url_status`) recorded with its observed result; schemas opt in per event kind via `verification.yaml` `checked_claims.required_for`. `hw verify --claims` replays predicates against the world — truth, separate from chain integrity. `cmd_exit` replay requires both `--allow-cmd` and the schema's shell capability. From the field incident where three systems recorded files as "posted" that did not exist while `hw verify` passed. 25-case test suite added.
- **Supersede payload upgrade (`core/SUBSTRATE.md`)** — `<kind>.supersede` gains `supersede_kind` (`full | mechanism-only | scope-narrowing`) and `surviving_principles`; `reverses:` accepts a list (one supersede event per reversed artifact). From field friction: a fresh agent could not distinguish "dead decision" from "principle still binds."
- **Fix: `check_scope_completeness` false positive (FL-024, `tools/hw-verify.py`)** — retroactive `scope.complete` events appended after the last `session.handoff` now satisfy the check (forward-scan fallback). 7-case test suite added.
- **`reference/FAILURE-MODES.md`** — concurrent-writer and perpetual-work entries added; the single-instance-lock "workaround, not a feature" note superseded by §Programs.

Deferred fast-follows (tracked in the field reports): test-gated exclusion (`suspect` vs `excluded` with `test_ref`), secrets refused at `hw add`, frontier staleness clock, `evidence.capture` event kind, ledger-digest projection, `profile: single-executor`, conditional-task primitive, `hw amend` tooling. Some of these are pulled forward into 6.0.0 — see §Pending below.

### Landed — verifier hardening

Five Layer 1 checks that `core/`, `CONTRIBUTING.md`, or a shipped schema already promised, and that no code performed. Four come from a ten-week production deployment; the fifth from reading the `program` pack against its own implementation. Every one of them was a place where `hw verify` returned PASS on a chain the documentation says is invalid.

- **Event ID integrity (`tools/hw-verify.py`, `core/SUBSTRATE.md` §Deriving the Next Event ID)** — duplicate event IDs and non-increasing IDs are now FAILs (`duplicate_event_id`, `non_monotonic_event_id`). From the field: two agents on one chain, the resuming one deriving its next ID from its own project's last event instead of the chain tail, so `EV-0116`..`EV-0120` exist twice with different content — every `prev_hash` correct, hash chain intact, `hw verify` PASS. Integrity checked the links and nothing checked the names. The duplicate report carries both line numbers, actors and projects, because choosing which same-named event survives is a content judgment the verifier cannot make. Gaps stay legal. New §Deriving the Next Event ID states the rule (tail + 1, never project-scoped state) and records the incident. 18-case test suite.
- **Lock enforcement (`tools/hw-verify.py`, `core/LOCK.md` §The Switch Protocol)** — `project.activate` for a second project with no intervening `project.park` / `project.archive` FAILs `lock_activate_without_release`. The refusal LOCK.md has promised since v5.0 was prose; a field deployment appended exactly that event and nothing objected. Bootstrap and `hw bootstrap --resume` on the already-active project stay legal; `_harness` meta events never move the Lock. 16-case test suite.
- **`harness_version` gate (`tools/hw-verify.py`, `CONTRIBUTING.md` §5)** — `HARNESS_VERSION = "6.0.0"` is now a constant, and a schema whose declared `harness_version` exceeds it is refused (`harness_version_too_new`). CONTRIBUTING §5 has required this since v5.1.1 with no implementation anywhere — which is how the repo reached the 5.2.1-harness / 5.3.0-`program`-schema state the version-coherence commit above had to fix by reading rather than by verifying. Older schema is a note, not a failure; absent or unparseable is a note. Scoped to the active project's schema, since the Lock guarantees one schema in force. §5 gains the outcome table. 17-case test suite.
- **Cycle lifecycle (`tools/hw-verify.py`, `templates/CYCLES.md`)** — the four v5.3 cycle FAILs are implemented: `cycle_close_without_open`, `cycle_open_without_close`, `cycle_on_terminal_lifecycle`, `wrap_with_open_cycle`. Matching is by `cycle_id`; parking with an open cycle stays legal (an ongoing project parks and resumes like any other). `cycle.open` / `cycle.close` were also missing from `KNOWN_EVENT_KINDS` entirely — every ongoing project reported its own lifecycle events as unknown kinds — and are now registered with their required payload fields, `next_due` included. `templates/CYCLES.md` adds the projection template the v5.3 projection table referenced but never shipped, with a rendering protocol precise enough for two agents to produce byte-identical output. 22-case test suite.
- **Schema-declared Layer 1 checks (`tools/hw-verify.py`, `schemas/projects/program/capability-gates.yaml`)** — the `program` pack declared `spawn_pause_skipped`, `registry_status_vs_supersede_chain` and `rollup_citation_stale_or_broken` with `enforce: true` and shipped all three as YAML prose, which CONTRIBUTING §6 names exactly: "a capability gate that does not produce a structural failure when violated is documentation, not enforcement." The dispatcher keys on the declaration rather than the schema name (CONTRIBUTING §4), so any schema declaring an implemented check gets it and `enforce: false` opts out. Roll-up citation staleness honors both severities the YAML states — write-time hard FAIL, later-cycle re-check non-blocking WARNING. Three readings had to be settled to implement at all (how a registration matches a `proposal_id` when the artifact has no such field; whether an unchanged status is a legal supersede, which it must be or every roll-up cycle the schema prescribes would FAIL; what "write time" means to a verifier running after the fact) — each is recorded in the YAML beside the rule it interprets. 43-case test suite.

Reporting gains `duplicate_event_ids`, `non_monotonic_ids`, `lock_violations`, `harness_version`, `harness_version_note`, `cycle_lifecycle`, `schema_checks` and `schema_check_warnings` rows; `core/VERIFICATION.md` §Layer 1 gains rows 14-18. Notes and warnings are reported without changing the exit code, matching the existing `ext_state_warnings` treatment. No existing behavior changed: the checked-claims (25) and scope-completeness (7) suites and the golden fixture pass untouched, alongside 116 new cases.

### Landed — field evidence

Six primitives, each from a documented failure of the same ten-week production deployment. The verifier-hardening block above fixed checks the docs already promised; this block adds what the deployment proved was missing. Every one of them is deliberately small — the deployment's own lesson was that a mechanism heavier than its value does not get used (see the friction-log entry below: four entries in 130 events).

- **Evidence capture (`core/SUBSTRATE.md` §Evidence Capture, H-S7; new `evidence.capture` event kind; `templates/artifact-templates/evidence-capture.md`)** — the raw outputs and error codes that conclusions rested on survived the ten weeks only where a human hand-copied them into a side ledger; everything else died with its session. `evidence.capture` keeps the bytes on the log: `{id: ED-NNN, producing_command, captured_at, content (inline, sanitized) OR content_path + content_sha256, summary}`, projected one file per capture into `projects/<id>/evidence/`. `ED` ids are unique across the whole log, not per project, because `test_ref` and finding evidence cite them bare. New Layer 1 check 20 covers well-formedness and id uniqueness: `evidence_id_malformed`, `duplicate_evidence_id`, `evidence_capture_no_content`, `evidence_capture_content_ambiguous` (both content forms — a capture has one authority), `evidence_capture_path_without_hash`. 22-case test suite.
- **Exclusion discipline (`core/SUBSTRATE.md` §Exclusion Discipline, H-S6; `schemas/artifacts/finding.yaml`; new `templates/ELIMINATION.md`)** — from AP-008, the deployment's most expensive failure: the true root cause was struck off the hypothesis list on the strength of a well-argued STATIC read, and ~19 attempts were burned before anyone revisited it. The rule is one line — *nothing is excluded without a dynamic test*. `finding.yaml` gains optional `status: open|suspect|excluded` and `test_ref`; `excluded` requires a `test_ref` naming an `evidence.capture` id or a checked-claim predicate that actually ran, and a static read may reach `suspect` and no further. New Layer 1 check 19: `excluded_without_test_ref`, `excluded_test_ref_unresolved` (a cited `ED` id no capture produced — a citation to a test nobody ran), `invalid_hypothesis_status`. The check reads `finding.add` plus any `.add` that opts in by carrying `test_ref`, so the program pack's unrelated `workstream.add` `status` field stays out of it. `templates/ELIMINATION.md` generalizes the engagement's elimination matrix — one-line frontier, then hypothesis / status / how-tested / result — the document that was handed to every new agent first and that killed generic-checklist churn. 33-case test suite.

- **Friction log slimmed to one line (`core/SUBSTRATE.md` §Friction Log Event Kind, `HARNESS.md` §Friction Logs)** — the deployment produced **four** `friction.log` entries in 130 events. The mechanism existed and the operator wanted it; six required fields "felt heavier than the value," so the run's best lessons went uncaptured. `friction.log` now requires only `{note}` — one line — with `{category, severity, task_id}` optional. The protocol is documented as literally one step: append one event. No artifact file, no projection to hand-write; promotion to an anti-pattern or finding is a later, optional act. The pre-v6 rich form still verifies unchanged, so no chain migrates: the verifier accepts a payload carrying `note` **or** the full rich set, an either/or that moved out of the flat required-field table into `check_note_payloads`. 17-case test suite.

- **`operator.correction` (`core/SUBSTRATE.md` §Operator Correction, H-S8; `templates/session-handoff-template.md`, `templates/executor-prompt.md`)** — the harness's invisible channel. The operator corrected and reminded agents constantly across ten weeks; none of it was captured, so the same reminder was re-given every session. Corrections cluster two ways — a claim broader than its verification, and environment knowledge only the operator holds — and each shape has a home. New one-line event kind: `{note}` required, `{context, should_have_lived}` optional, where `should_have_lived` names where the information belongs so the reminder is never needed again. The protocol's load-bearing half is the **promotion review at session wrap/handoff**: read this session's corrections and write each into its home (operating-reality, rules file, anti-pattern). That step is now a section of the handoff template and a step in the executor prompt. Layer 1 is well-formedness only — whether a correction was promoted well is a judgment the verifier cannot make, and a check that guessed would teach agents to write nominal values. Test cases folded into the one-line-events suite (27 cases).

- **Open-loop tracking (`core/SUBSTRATE.md` §Open Loops, H-S9; new `loop.open` / `loop.close` event kinds; new `templates/OPEN-LOOPS.md`)** — a gated action sat unconsumed for **five weeks**. A message cleared every technical gate for a server rejoin and said "the only remaining gate is the operator's word"; nothing tracked it, and the divergence between believed and actual state surfaced five weeks later through an unrelated symptom, in production. Nothing was wrong with the work — "waiting on X" was a sentence in a document rather than a row anything could count. `loop.open` carries `{loop_id: L-NNN, description, blocking_on: operator-word|external|other-agent|scheduled, opened_at, stale_after_days (default 7)}`; `loop.close` carries `{loop_id, closed_at, resolution}`. `hw status` now leads with an **OVERDUE OPEN LOOPS** block for anything past its staleness window, above the project summary. `session.handoff` gains a required `open_loops` list (may be `[]`), and `templates/session-handoff-template.md` gains the section that carries it. New Layer 1 check 21: `loop_close_without_open`, `duplicate_loop_open` (loops are never reopened — a recurrence is a new `L` id), `handoff_missing_open_loops`. Backward compatible by design: an **absent** `open_loops` field is a note, not a FAIL, so pre-v6 chains keep verifying — which is why the field is deliberately not in the verifier's flat required-payload table. Staleness itself is not a Layer 1 check: it is date-dependent, and a chain that verified today would fail tomorrow with no event appended. 32-case test suite.
- **`read_only_pass` task gate (`core/ATOMICITY.md` §Task Frontmatter, `core/SUBSTRATE.md` §Read-Only Pass, `templates/task-template.md`, `templates/executor-prompt.md`)** — EV-0042: a "read-only this pass" gate was added to an already-issued task and never reached the executor before it acted. The task file is the Mutable Surface and the executor reads it at dispatch, so anything added afterwards is invisible to an agent already working from its copy. The gate was correct and lost a race. Optional `read_only_pass: true` now exists in the task frontmatter convention and in `TASK-STATE.yaml` (re-read from `task.md` at render time rather than taken from the `task.create` payload, because being addable mid-flight is the whole point — and unlike `lightweight_completion` it is deliberately **not** locked at authoring). The executor prompt gains a mandatory step: immediately before your first state-changing action, re-read the task file; if `read_only_pass` is true, mutate nothing this session — read, measure, capture evidence, report. No verifier change: a check would have to decide which actions were mutations, and it would arrive after the write it was meant to prevent.

Reporting gains `exclusion_discipline`, `evidence_capture`, `open_loops` and `open_loop_notes` rows; `core/VERIFICATION.md` §Layer 1 gains rows 19-21. Existing check numbers are untouched. Notes are reported without changing the exit code, matching the existing `harness_version_note` treatment. Four new suites (evidence capture 22, exclusion discipline 33, one-line events 27, open loops 32) join the seven that shipped earlier in 6.0.0: **262 cases across 11 suites**, plus the golden fixture, all passing.

### Landed — protocol features

Four more, each from a documented production failure. Where the block above added checks, this block adds protocol: what the harness refuses, what it generates, what ceremony it drops, and what it requires of anything that moves a file between two places.

- **Secrets gate (`core/SUBSTRATE.md` §Secrets Gate, H-S10; `tools/hw-verify.py` `scan_for_secrets`; `core/VERIFICATION.md` §Layer 1 check 22)** — a sync digest copied a DSRM password and a local-admin password verbatim into a mailbox. The log is append-only, so a temporary credential is now **permanent**; the only remediation was rotating it in the real world. The fix attempted at the time was a redaction **blocklist** — itself a cleartext file aggregating live credentials, one forgotten entry from the next leak. `hw add` now scans the payload before appending and **refuses** on a hit, instructing store-by-reference: `[REDACTED-SECRET]` plus a pointer to where the secret actually lives. The stated principle: exports and digests copy **allowlisted fields only**; never maintain a blocklist of live secrets. `scan_for_secrets()` implements five detectors — credential assignments, PEM / OpenSSH private-key blocks, connection strings, bearer / vendor-token shapes, and unlabeled high-entropy tokens (Shannon entropy over 4.0 bits/char on tokens of 20+ chars). The false-positive guards are the load-bearing part: the hashes the harness itself requires never trip it (citations, `sha256:` prefixes, 12-64 hex in `hash` / `prev_hash` / `sha256` / `content_sha256` / `soul_hash` / `test_ref`), pure hex cannot reach a 4.0 threshold by construction, and `[REDACTED-SECRET]` — the marker the gate asks for — is never a hit. New Layer 1 check 22 `possible_secret_in_event` is a **WARNING**, never a FAIL by default: historical chains carry leaked secrets and refusing to verify them unleaks nothing, while a verifier that FAILs forever on immutable history is one operators stop running. `--strict-secrets` promotes it to FAIL for new-chain hygiene. Reports name the event, the field and the rule, never the value — a verifier that echoed its findings would be the second copy of the leak. 38-case test suite.

- **Generated narrative ledger (`core/SUBSTRATE.md` §Narrative Ledger, H-S11; new `templates/LEDGER.md`; `HARNESS.md` §Recovery Order)** — across ten weeks the hand-curated newest-first human ledger beat the machine-perfect event log for rebuilding working context after every compaction; the executor's exit interview ranked the event log **last**. But the hand-kept version drifted exactly where hand-keeping drifts: blocks filed out of sequence, superseded sections edited in place. The verdict from the field was not "the log is wrong" but *stop fighting it — generate it*. New projection `projects/<id>/LEDGER.md`: one block per day, closed early by a `session.handoff`, blocks newest first and lines within a block in append order. Each block carries task completions (with claim PASS/FAIL where one was recorded), decisions by id and title, finding one-liners, loops opened and closed, operator corrections and friction notes. **Superseded items render struck through and tagged `[superseded by <id>]`, never deleted** — dropping what turned out wrong is the hand-kept ledger's failure mode, not a fix for it. Nothing is summarized by judgment: every line is a field copied out of a payload, so the render is byte-deterministic from an event prefix like every other projection, and no part of it depends on today's date. The documented recovery order is now explicit in `HARNESS.md` and `templates/session-handoff-template.md`: `hw verify`, then **LEDGER.md first**, then the handoff, then raw artifacts, with `events.jsonl` last and only when two things above disagree.

### Pending in 6.0.0 — lands via subsequent commits

Placeholders. These are in scope for the 6.0.0 release and are not yet written; each gets a real entry when its commit lands.

- **Diverse-agent docs** — *pending.* Documentation for running the harness across heterogeneous agent/model fleets. Entry to be written when the commit lands.

### Also shipping in 6.0.0

The three earlier gather sections below — "Unreleased (2026-07-13)" (machine-2 field gather), "Unreleased (2026-07-13)" (two more field-derived schemas) and "Unreleased (2026-07-03)" (eight field-derived project schemas) — were never cut as their own release. They ship as part of 6.0.0 and are left in place below as the record of how the schema corpus was assembled.

## Unreleased (2026-07-13) — Machine-2 field gather: three creator/education schemas; second field report

Schemas-and-evidence change from the second-machine gather; no mechanism or substrate edits.

- **`content-piece-test`**, **`book-edit-test`**, **`course-master-plan-test`** — the creator-content family, imported genericized from empirical test runs (residual book/content identifiers replaced with neutral placeholders). `content-piece-test` fans one piece of creator content out to three format-native variants with verbatim-keeper hash freshness and an interview question budget. `book-edit-test` is a voice-preserving manuscript re-release edit: per-chapter hermetic passes, voice-anchor and banned-pattern artifacts, round-aware corpus chains. `course-master-plan-test` encodes a three-layer L1/L2/L3 orchestration pattern (slug-premise-pause spawn protocol, cross-project artifact subscription, curriculum-as-DEC) — imported as-found; its orchestration pattern is field evidence, not a sanctioned mechanism. All three keep their working `-test` names: their sources define `hw schema save --from <name>-test --as <name>` as the extraction step, which never ran.
- **YAML fix at import** — `content-piece-test/artifact-extensions.yaml` carried two unquoted `list[string]` tokens inside flow mappings (parse error; same footgun the market-intelligence packs hit). Quoted in the repo copy.
- **`reference/field-reports/laptop-hao-2026-07.md`** — second field report. Headlines: a fully documented concurrent-writer event-log corruption incident (four friction entries + a decision record adopting per-member draft files with a single convergence writer); a live production orchestrator layer whose tracks the LOCK forced into `backlog.md` parking plus a perpetual cron cadence task; the hash-canonicalization defect recurring after its v5.0.1 doc fix; supersede-payload and singular-`reverses:` gaps; a false-positive `check_scope_completeness` FAIL on retroactive fix-run chains (mechanism-adjacent — reported, not fixed). Evidence collection only; decisions deferred to the operator.

Not imported from the same gather: `pm-site-explorer-test` (four-file pack predating the full pack convention, bound to one platform-exploration run).

## Unreleased (2026-07-13) — Two more field-derived schemas; validation-run merge; hygiene

- **`brand-ecosystem-audit`**, **`market-gap-intelligence`** — the market-intelligence family, proven on a live brand-ranking engagement and imported genericized (pilot-engagement names replaced with the repo's standard placeholders). `brand-ecosystem-audit` evaluates a brand across every surface it occupies (owned site, social, marketplaces, review sites) and synthesizes a menu of strategic paths rather than one fixed plan. `market-gap-intelligence` answers four ordered competitive-gap questions with hash-cited MEASURED/OBSERVED evidence and requires at least one disconfirming finding before any recommendation ships. Both packs carry the YAML fixes their schema-test friction logs surfaced (quoted `"list[string]"` tokens in flow mappings; quoted `"yes"`/`"no"` enum values against YAML 1.1 boolean coercion). Sixteen schemas now ship as defaults; README table, `HARNESS.md` file structure, and schema-match step updated.
- **From the CC-test1 validation run** — HyperFinch v0.2.0 (tool-call loop: trials can operate a real bootstrap, not just generate files) with the ceremony-cost experiment pack and findings; `tools/fixtures/golden-workspace` (a pinned 7-event reference project) plus `tools/make-golden-fixture.py` as a regression signal for any `hw verify` or projection-renderer reimplementation. Raw per-trial results intentionally not imported.
- **Version drift fixed** — README badge and `HARNESS.md` header said 5.2.0 while v5.2.1 had shipped; both now say 5.2.1.
- **Repo hygiene** — `.gitattributes` added (LF normalization: hash-cited artifacts must not change bytes because of a checkout on a different OS); `__pycache__/` gitignored.
- **`reference/field-reports/`** — new home for per-machine field-gather reports: harness-applicable friction evidence collected from live deployments, genericized. First report covers the 2026-07 gather (lock strain under program-shaped work, recurring-cadence gap, amend tooling gap, and the checked-claims proposal). Evidence collection only; mechanism decisions remain deferred to the operator.

## Unreleased (2026-07-03) — Eight field-derived project schemas

Schemas-only change; no mechanism or substrate edits. Eight project schemas, all derived from real projects run on the harness, join the six defaults (fourteen total):

- **`site-review-repair`**, **`site-seo`**, **`site-monetization`** — the website-repair family: per-site workstreams for post-incident triage/fix/verify, phased SEO recovery, and ad-revenue restoration. Report-first: the agent diagnoses and proposes; the operator executes anything requiring credentials or account actions. `site-monetization` ships with the later revision of its precedence tiers and rules (operator decisions are final; always commit to one recommended path).
- **`gov-bid-hunt`**, **`opportunity-hunt`**, **`lead-mining`**, **`single-opportunity`** — the work-finder family, forked from `report-synthesis` and re-tooled for live revenue discovery: government bid hunting per service-line segment, channel-agnostic opportunity hunting, inbound-lead mining from the operator's own mailboxes, and a single deal run end-to-end. Curation applied at import: report-synthesis remnants removed (unused claim/contradiction templates and task files); `verification.yaml`, `artifact-extensions.yaml`, `precedence-tiers.yaml`, and `bootstrap-probe.md` — left as verbatim parent copies in the field versions — re-authored per schema so risk routing keys to each schema's actual task kinds and OR-001 requirements match each schema's bootstrap questions; client-specific names, paths, and addresses genericized.
- **`cleanroom-rebuild`** — reproduce a legacy application on a modern stack from measured behavior, never its code, behind a structurally enforced observation/spec/build wall (capability gates + Tier 1 precedence + five Layer 1 wall checks + a dedicated integrity auditor). `bootstrap-probe.md` authored at import (observation-surface sweep).

Docs updated to match: README schema table (six → fourteen), HARNESS.md §file structure and schema-match step, CONTRIBUTING.md and reference/VALIDATION.md reworded version-neutrally ("shipped defaults") so the count can't drift again.

Not imported from the same field haul: `site-keyword-research` (a project-instance snapshot bound to one specific workbook, not a reusable schema) and `cleanroom-workbook-build` (incomplete four-file pack predating the full pack convention).

## v5.2.1 (2026-06-09) — Pre-append validation, recitation band, toolchain anchor

Four changes: a protocol fix (`hw add` no longer dirties the log to reject a bad citation), a semantic fix (recitation overlap becomes a two-sided band — the old floor-only threshold rewarded verbatim copying), one new primitive (`toolchain.anchor`), and a doc-drift sweep (including a location the v5.2.0.1 F7 audit missed). Two hypotheses added; both carry falsifiers.

### `hw add` citation validation moved pre-append

`core/SUBSTRATE.md` §`hw add`: citation checks are a read-only computation against `hashes.json`, so they now run as step 3, *before* anything is written. A broken or stale citation aborts with a structured error; nothing lands in the log. The previous flow appended the event first and reversed it with a supersede-to-null, leaving a rejection pair in the chain for every mistyped citation. The supersede-to-null path remains only for defects discovered after append. `core/VERIFICATION.md` §Layer 1 On-failure wording updated to match.

### Recitation overlap: single threshold → two-sided band (H-T4)

The v5.0–v5.2.0 check rejected paraphrases below a Jaccard threshold (default 0.7). Diagnosis: a high floor rewards the cheapest evasion — quoting the source back verbatim — which proves transcription, not processing, and defeats the attention-restoration purpose. The check is now a band: reject below `recitation_overlap_floor` (default 0.35; likely unread) AND above `recitation_overlap_ceiling` (default 0.90; verbatim echo).

- `core/TYPED-ARTIFACTS.md` §Recitation rewritten; hypothesis H-T4 added with falsifier (in-band recitations still miss load-bearing constraints, or genuine paraphrases get rejected often enough that agents game the band).
- `core/VERIFICATION.md` Layer 1 check 6 updated.
- `templates/executor-prompt.md` recitation instruction updated (keep IDs, numbers, named constraints; recombine the prose).
- All six `templates/models/*.yaml` profiles migrated to floor/ceiling (per-model tuning notes preserved); `templates/models/README.md` field table and override example updated; `reference/VALIDATION.md` symptom row updated.
- Back-compat: a profile declaring only the legacy `recitation_overlap_threshold` gets the v5.2.1 defaults; the legacy field is ignored with WARNING `recitation_threshold_deprecated`.

### Toolchain Anchor (H-V521-2, new primitive)

Every hash the harness depends on requires running code; an agent cannot compute SHA-256 by generating tokens. Unspecified, each session improvises a fresh implementation — serialization divergence or fabricated hashes. New `toolchain.anchor` event kind pins the SHA-256 of every hash-computing tool (shipped or first-run-generated); sessions verify the pins before the first hash-computing operation. Silent drift is Layer 1 FAIL `toolchain_drift` (new check row 12); a hash-bearing workspace with no anchor is WARNING `toolchain_unanchored`. Deliberate tool changes re-anchor with a new event. See `core/SUBSTRATE.md` §Toolchain Anchor. Falsifier: anchored workspaces still produce inter-session hash divergence, or agents bypass the anchored tools.

### `tools/hw-verify.py` event-kind sync

`KNOWN_EVENT_KINDS` gains `operator_soul_anchor` (a v5.2.0 kind that was never added — every soul-anchored workspace produced unknown-kind warnings) and `toolchain.anchor`. `REQUIRED_PAYLOAD_FIELDS` entries added for both.

### Doc-drift sweep

- `README.md` schema table: "Five schemas" → "Six", `report-synthesis` row added. The v5.2.0.1 F7 audit fixed four five-vs-six locations but missed this one.
- `README.md` "Not finished" bullet: version-pinned "v5.0 … retired in v5.1" → version-neutral wording.
- `HARNESS.md` file structure: gains `schemas/projects/report-synthesis/`, `reference/VALIDATION.md`, and `tools/hw-verify.py` — all real files absent from the map.

### README repositioning

- **§Why this exists** — names the project's actual mission: built by an ADHD operator, for brains that don't keep state between interruptions; LLMs share ADHD-shaped failure modes (drift, session amnesia, novelty-driven scope creep), so the substrate is symmetrical by design — the same primitives scaffold the agent and the human.
- **§Work the way you work** — surfaces the existing-but-buried `delegation_policy` / `execution_mode` fields as the answer to interruption fatigue: the operator declares their interruption budget once at bootstrap; the substrate enforces it. No new primitives; the README just stops hiding the ones v5.1/v5.2 shipped.
- **§Works with** — repositioned Cowork-first (primary tested environment) while staying agent-agnostic; local-model row added with pointer to HyperFinch for empirical can-this-model-carry-the-protocol testing.
- **§The Hyper ecosystem** — declares the add-on policy: harness core stays markdown permanently; capabilities needing code ship as sibling `Hyper<animal>` repos (HyperFinch shipped; voice capture planned).
- **§Who this is for** — ADHD operators named explicitly.

---

## v5.2.0.1 (2026-05-10) — Audit patch

A coherence audit walk-through of v5.2.0 surfaced seven findings (F1–F7). Five fixed here; two deferred to v5.2.1 with documented intent.

The triggering observation: H-V52-3 (the soul-anchor hypothesis) cannot be tested if the primitive is invisible to agents following entry-point files. F5 and F6 made `operator_soul_anchor` unreachable from `HARNESS.md` §Bootstrap Protocol and `templates/executor-prompt.md` §At project bootstrap. A v5.2.0 real-work run with v5.2.0 as-shipped would never fire the event and the hypothesis would stay untestable. The soul anchor's own logic ("never present a workaround when the real fix exists") rules out punting these to v5.2.1.

### F1: `soul_anchor_path` field added to operating-reality template

`templates/artifact-templates/operating-reality-template.md` now declares `soul_anchor_path: <path or null>` as an optional v5.2.0 OR field. Documents that `null` inherits `soul.md` at workspace root, otherwise the harness fires no `operator_soul_anchor` event. References `core/SUBSTRATE.md` §Operator Soul Anchor and the SOUL.template.md / SOUL.example.md substrate files.

### F4: Layer 1 row 11 added for `execution_mode` value validation

`core/VERIFICATION.md` Layer 1 check table gains row 11: `execution_mode validity`. Values must be in `{interactive, agent, observer}`. `observer` is reserved (not implemented in v5.2.0); the harness emits a WARNING with code `execution_mode_observer_reserved` and treats the dispatch as `interactive` for behavior. Any value outside the enum is a FAIL with code `execution_mode_invalid`. Closes the dangling "Layer 1 WARNING on dispatch" claim in `core/ATOMICITY.md` §Execution Mode.

### F5: `operator_soul_anchor` inserted into `HARNESS.md` §Bootstrap Protocol

The bootstrap protocol grew from six steps to seven. New step 5 ("Anchor operator identity") runs after OR-001 is written and before the Verification Checkpoint council. Reads `soul.md` from `OR-001.soul_anchor_path` (or workspace root by default), computes SHA-256, emits `operator_soul_anchor`. The completion-signal sentence updated to mention the soul-anchor phase.

### F6: `operator_soul_anchor` inserted into `templates/executor-prompt.md` §At project bootstrap

New subsection "At project bootstrap — anchor operator identity (if declared)" between the inventory-sweep block and the "Before any state-changing tool call" section. Three-step procedure: check `OR-001.soul_anchor_path`, emit `operator_soul_anchor`, re-emit on file change. Completion signal: either `operator_soul_anchor` exists, or no soul.md is declared and the schema does not require one.

### F7: "Five default schemas" corrected to "six" across the substrate

Four locations updated:

- `HARNESS.md` §Bootstrap Protocol step 2: "five default schemas" → "six default schemas (marketing-campaign, software-feature-ship, client-onboarding, event-planning, compliance-audit, report-synthesis)".
- `reference/VALIDATION.md` §The Validation Test: same correction; `report-synthesis` added to the parenthetical (the v5.0.1 addition that was never reflected here).
- `schemas/projects/compliance-audit/council.yaml` header comment: "largest of the five default schemas" → "largest of the six default schemas".
- `CONTRIBUTING.md` §What we want: "under-represented in the five defaults" → "under-represented in the six defaults".

Origin: `report-synthesis` was added as the sixth default in v5.0.1 but the prose references in HARNESS.md, VALIDATION.md, compliance-audit/council.yaml, and CONTRIBUTING.md were never updated. The v5.2.0 copywriting pass did not catch this — the audit did.

### Deferred to v5.2.1 with documented intent (F2, F3)

Both findings involve adding a schema-config field. Defining them blindly now risks baking in the wrong shape — the research schema work in v5.2.1 will inform the right `capability-gates.yaml` extension pattern.

- **F2: `soul_anchor_required` schema-config field location undefined.** Referenced in `core/SUBSTRATE.md` §Operator Soul Anchor and `core/VERIFICATION.md` Council Role Library, but no schema currently declares where the field lives. v5.2.0.1 keeps the references as forward-looking; v5.2.1 lands the slot. Until then, v5.2.0.1 reads `soul.md` from `OR-001.soul_anchor_path` (or workspace root by default) without hard-enforcement.
- **F3: smoke-run marker dictionary "configurable per schema" but no schema config field.** Same shape as F2. v5.2.0.1 keeps the default marker set (`"would normally", "in a real run", "this is a placeholder", "demonstrating the structure"`) and the prose claim that schemas can extend it; v5.2.1 lands the actual extension slot in `capability-gates.yaml`.

These are documented as intent, not omission. The audit found them in a single walk-through; deferring them is a known cost.

### What this patch does NOT change

- No new event kinds (the existing `operator_soul_anchor` event remains as defined in v5.2.0).
- No new schema rules. No new council members. No version bumps to `harness_version` (still `5.2.0` across the six schemas; this is a patch over v5.2.0, not a substrate version change).
- No changes to the substrate copywriting pass, agent mode, or the soul anchor primitive itself — only their wiring into entry-point files and the OR template.

### Repo state after patch

- `5.x` tip: this patch commit.
- `main`: fast-forwarded from `5.x`.
- `v5.2.0`: unchanged, preserved as the original v5.2.0 release branch and tag.
- `v5.2.0.1`: new tag on this patch commit.

The original `v5.2.0` tag is not amended; v5.2.0.1 sits forward of it on the same line so anyone who pulled v5.2.0 already has a coherent reference.

---

## v5.2.0 (2026-05-10) — Substrate copywriting + agent mode + soul anchor

Three concerns shipped together: a substrate-wide copywriting pass that applies the v4 hand-roll's direct-response craft (imperative voice, named failure modes with cost, completion signals); a new `delegation_policy.execution_mode` primitive (agent mode for autonomous-with-safety-floors execution); and a soul anchor primitive (operator-identity event + council member). v5.2.0 is **strictly additive over v5.1.1** — existing schemas validate unchanged; `execution_mode` defaults to `interactive` (current behavior); `soul_consistency_watcher` is opt-in per schema.

Each new primitive carries an explicit hypothesis with a falsifier (H-V52-1 through H-V52-4 below). v5.2.x retires whatever fails its falsifier in real use.

### Substrate copywriting pass

- **HARNESS.md** rewritten to apply the v4 craft. Imperative voice, named failure modes, completion signals on the bootstrap protocol. Banned modals (`should/may/could/might/generally/we usually/try to/consider`) removed; banned framings (`operate at the highest standards / senior engineer mindset / autonomous agent / with the discipline of`) eliminated. Rules preserved verbatim; tables, code blocks, file structure, command list, and version strings byte-for-byte. Hook framing in the header on substrate-over-rules thesis.
- **`core/*.md`** rewritten where prose surfaces benefited. Each commit named the failure mode the primitive prevents:
  - LOCK.md: multi-project drift cost ("neither gets the operator's full reading of state at any moment"), distraction-intake failure mode ("just outline it real quick").
  - PRECEDENCE.md: SCAN attention-restoration failure mode ("model glances at the section and continues with whatever pattern it had cached"), compliance-theatre framing for after-the-fact SCAN answers.
  - ATOMICITY.md: hermetic-set failure mode (F-019 leak corrupting recitation projection and dependency graph), branch/fold parent-context-pollution cost, ratchet silent-drift cost with concrete T-009/T-005 example.
  - VERIFICATION.md: v4.1.1 stacked-eight-component cost, council fabrication-on-mismatched-trigger framing, "two minutes per task, dozens of tasks, hours of operator time on verbal approval" framing for what Pushback becomes.
  - TYPED-ARTIFACTS.md: v4.1.1 lifecycle maintenance-debt cost, citation-without-reading failure mode (downstream agents fabricating a reading from the artifact's title).
  - SUBSTRATE.md: surgical edits to v5.1/v5.1.1 event-kind preambles (Friction Log, Session Handoff, Scope Completeness, External State Read-Back, Bootstrap Inventory Sweep) — each named with a concrete failure mode and cost.
- **`templates/executor-prompt.md`** rewritten — the highest-leverage substrate file. Preamble names the most expensive operator-pull-in pattern (permission-asks at phase boundaries when permission was granted at project init, per v4 Operating Posture).
- **`templates/task-template.md`, `session-handoff-template.md`** light-touch passes on prose-heavy sections. Other templates and `artifact-templates/*` reviewed and judged sufficient as-is — the v4 craft does not add value over the existing imperative field-driven prose.
- **Schema READMEs** light pass. Most are already in v4 voice (especially report-synthesis with "Summaries lose decisions"). One targeted addition to `marketing-campaign/README.md` (the agent-generates-six-pieces-with-30%-Tier-1-violations failure mode).

### Agent mode (`delegation_policy.execution_mode`)

- **Added** `execution_mode` field to the existing v5.1 OR-001 `delegation_policy`. Three modes:
  - `interactive` (default) — current v5.1 behavior unchanged.
  - `agent` (v5.2.0) — proceed autonomously up to the safety floors below.
  - `observer` (reserved) — not yet implemented; declaring it produces a Layer 1 WARNING and the harness behaves as `interactive`.
- **Five non-overridable safety floors** (always pause, regardless of mode):
  1. Critical-risk task completion (`safety_floor_critical_completion`)
  2. Smoke-run language detected by council (`safety_floor_smoke_run`) — configurable marker dictionary, default set: `"would normally" / "in a real run" / "this is a placeholder" / "demonstrating the structure"`.
  3. Layer 1 retry threshold exhausted (`safety_floor_layer1_exhausted`)
  4. Voice/soul anchor breach (`safety_floor_soul_breach`) — fires when `soul_consistency_watcher` returns FAIL on a `task.complete`.
  5. Operator mid-flow directive (`safety_floor_operator_directive`)
- **Implementation** spans `core/ATOMICITY.md` §Execution Mode (full safety-floor table + soft-enforcement framing), `templates/executor-prompt.md` §Execution mode (operationally legible per-floor list), `templates/artifact-templates/operating-reality-template.md` (YAML field added), and `core/PRECEDENCE.md` §Operator Mid-Flow Directives Beat Mode Settings (precedence-over-execution_mode framing). Hypothesis H-V52-2; falsifier: an agent-mode run terminates a critical-risk operation that should have paused.

### Soul anchor primitive

- **Added** `SOUL.template.md` at substrate root — brand-clean structural stub. Operators copy and fill in their own. Length discipline: ≤1000 words; tight beats long.
- **Added** `SOUL.example.md` at substrate root — one filled-in example showing how a real operator adapted the template's intent. Section structure preserved verbatim from the source soul.md (Boil the ocean / Excuses / Anti-patterns / Voice / When in doubt) to demonstrate that operators use their own framing rather than mirroring the template's headers. Operator-specific names and project references genericized to satisfy substrate brand-isolation.
- **Added** `operator_soul_anchor` event kind in `core/SUBSTRATE.md`. Payload `{soul_path, soul_hash, version, fired_at}`. Fired at bootstrap when `OR-001.soul_anchor_path` is declared (or when `soul.md` exists at workspace root and the schema declares `soul_anchor_required: true`). Re-anchoring on file change is a new `operator_soul_anchor` event; the supersede chain captures the change.
- **Added** `soul_consistency_watcher` council member in `core/VERIFICATION.md` §Council Role Library. FAILs on: workaround when real fix is reachable / "tabling for later" with no documented blocker / incomplete-presented-as-done / work product fails the named quality bar from the soul anchor. Reads soul.md content from the most recent `operator_soul_anchor` event by hash. Skipped with `member_skipped: no_soul_anchor` if no anchor exists. Smoke-run marker dictionary is shared with the agent-mode safety floor; one event surfaces per detection, not two duplicates. Hypothesis H-V52-3; falsifier: the watcher never fires across 5+ real runs (anchor is not load-bearing) OR fires constantly (anchor is poorly written).

### Brand isolation

- **Pre-v5.2.0 cleanup** committed on the master line before branching: `core/TYPED-ARTIFACTS.md` operator example bumped (`Spencer` → `the operator`); `schemas/projects/report-synthesis/artifact-extensions.yaml:44` source-author example genericized (`'Spencer'` → `'Operator'`).
- **Final substrate sweep** at commit 11 confirms zero operator-name leaks outside `LICENSE` (copyright), `README.md` (`@mrhobbeys` attribution), `SOUL.example.md` (intentional example content), and `CHANGELOG.md` attribution lines.

### Repo hygiene (pre-v5.2.0)

- **Branch convention aligned** with the operator's intended structure (`main / 3.x / 4.x / 5.x`):
  - `master` renamed to `5.x` (the active 5.x development branch with full v5.0/v5.0.1/v5.1/v5.1.1 history).
  - `3.x` and `4.x` to be created from the existing remote `v3` and `v4` archival branches in the final remote-burst.
  - Stale local branches `v5` and `v5.0` to be deleted (subsumed by `5.x`; `v5.0` was also ambiguous per git's own warning).
- **Gitea remote** added (`https://slh.local/gitea/spencer/HyperWorker.git`) with per-host SSL verification disabled for the local self-signed cert. Gitea force-push reconciliation in the final remote-burst (gitea is a pre-rebase parallel fork; same content, different SHAs; local is canonical).

### Hypotheses under test (v5.2.0)

| ID | Claim | Falsifier |
|---|---|---|
| H-V52-1 | The v4 hand-roll's direct-response copywriting craft, applied across substrate files, measurably reduces middle-section suppression and permission-ask frequency in real-work runs. | The next 3 real-work runs show no measurable shift in behavioral signals captured against the v5.1.1 baseline. |
| H-V52-2 | Agent mode (`execution_mode: agent`) reduces stopping-point cost on agentic-coder workflows (Copilot-style credit consumption, Claude long-session cost) without compromising the safety floors. | A real-work agent-mode run terminates a critical-risk operation that should have paused. |
| H-V52-3 | A structural operator-identity anchor (soul.md + `operator_soul_anchor` event + `soul_consistency_watcher` council member) produces qualitatively different agent behavior than rules-based prose alone. | The watcher never fires across 5+ real runs (anchor is not load-bearing) OR fires constantly on every task (anchor is poorly written and dilutes the Tier 1 boundary). |
| H-V52-4 | Reserved for the editing schema. Deferred to v5.2.1; no claim shipped in v5.2.0. | n/a in v5.2.0. |

### Behavioral signals to watch

When v5.2.0 lands in a real-work run, capture these against the v5.1.1 baseline (friction log, post-mortem):

- **Permission-ask count.** How often the agent paused at a phase boundary or council-converged event waiting for operator approval that v4 Operating Posture says was granted at project init. If the copywriting pass reduces this count, H-V52-1 lives. If not, the pass was decoration.
- **Smoke-run marker emissions.** How often the `soul_consistency_watcher` (where opted-in) or the agent-mode safety floor #2 fires on "would normally" / "for now" / equivalent phrases. Zero fires across 5 runs falsifies H-V52-3 from the under-side; high false-positive rate falsifies it from the over-side.
- **Agent-mode pause profile.** When `execution_mode: agent` is set, what fraction of pauses are safety floors vs. interactive-mode equivalents the operator would have hit anyway? If the floors are doing the right work, agent mode should pause meaningfully less while preserving every irreversible-mutation gate.
- **Soul.md drift.** How often the operator updates soul.md mid-project (re-anchoring event). Zero updates is fine; frequent updates may indicate the initial anchor was vague.

### Not in v5.2.0 (deferred)

- **Editing schema (`schemas/projects/editing/`).** Deferred to v5.2.1. The 5.1.1 Book Fix Test project remains the empirical reference for that schema.
- **Council-skip-with-honesty primitive.** Deferred until after v5.2.0 + the editing schema show whether council-skip is needed as a structural pattern.
- **Workflow / knowledge layer split.** Deferred indefinitely; v6 contingency, not yet empirically justified.
- **Hard enforcement of `execution_mode`.** v5.2.0 ships soft enforcement (the agent reads the field and complies; the harness does not block dispatch). Hard enforcement deferred to v5.3 if needed.
- **`observer` mode.** Reserved enum value, not implemented. Audit-only / no-state-changing-events mode is a v5.3+ candidate.

### Version

- `harness_version: "5.2.0"` across all six schema files. HARNESS.md title bumped to v5.2.0. CONTRIBUTING.md title bumped to v5.2.0. README.md badge bumped to 5.2.0. `templates/executor-prompt.md` preamble bumped to v5.2.0.

### Single-operator clean-break note

This release is strictly additive — every v5.1.1 schema validates unchanged under v5.2.0. `execution_mode: interactive` is the default; existing OR-001 records inherit it without modification. `soul_consistency_watcher` is opt-in per schema; no schema in v5.2.0 enables it by default. There is no migration path required for any existing project.

---

## v5.1.1 (2026-04-27) — Patch release

Five substrate/schema patches addressing gaps surfaced by the v5.1 asset-update empirical run on `example-rebrand-rollout`. Plus one new task template and a CONTRIBUTING.md schema-update guide.

Each patch carries a hypothesis with a falsifier (H-G1 through H-G5; see V5.1.1-BUILD-REPORT.md §4); the next empirical run on the example-rebrand-rollout fix run evaluates them. v5.1.2 retires whatever fails its falsifier in real use.

### Substrate

- **Added** `scope.complete` event kind and Layer 1 scope-completeness check. Records every PROJECT.md §Scope item with a terminal_state at session.handoff; cross-checks against PROJECT.md §Scope to catch silent in-scope skip patterns. Allowed terminal states: `complete`, `deferred`, `excluded-after-discovery`, `escalated`. Per-schema strictness via `capability-gates.yaml` `scope_completeness.allowed_terminal_states`. Hypothesis H-G1; falsifier: a declared scope item resolves to no terminal state and verification PASSes. (Patch 1)
- **Added** `external_state.read_back` event kind. Schema-declared trigger via `capability-gates.yaml` `external_state_readback.required_for`; Layer 1 requires a paired event for tasks matching the patterns. v5.1.1 enables this only on marketing-campaign (critical-risk + live-edit task patterns). `divergence_detected: true` is a WARNING with a required follow-up `friction.log` event. Hypothesis H-G2; falsifier: a critical-risk `task.complete` ships without a paired read_back event and Layer 1 PASSes. (Patch 2)
- **Added** `bootstrap.inventory_sweep` ceremony with three event kinds (`bootstrap.inventory_diff`, `bootstrap.scope_locked`, `bootstrap.probe_skipped`). Probes declared §Scope inventory against ground truth at bootstrap; operator reconciliation gates §Scope locking. Per-schema probe declared in `bootstrap-probe.md`. Hypothesis H-G3; falsifier: a wrong slug or missing page in PROJECT.md §Scope makes it past bootstrap and bites mid-task. (Patch 3)

### Schema: marketing-campaign

- **Added** edit-vs-create-vs-delete enumeration protocol for live-edit task proposals. Documented in `core/TYPED-ARTIFACTS.md` §Live-Edit Proposal Artifacts. Live-edit task templates' step 2 must enumerate `edit_candidates`, `create_candidates`, and `delete_candidates` before proposing actuation; templates with no create-alternative (single-field-edit shapes) state this explicitly. (Patch 4)
- **Added** `scope-shrink-watcher` council member in `council.yaml`. Reviews live-edit task proposals against enumeration; FAILs if any candidate is silently dropped without paired deferral or excluded-after-discovery decision. Context-asymmetric framing: member sees proposal artifact only, not the live asset state. Trigger entry fires on every `task.complete` whose task has `delivery_mode: live-edit`. Hypothesis H-G4; falsifier: an audit task ships only edit_candidates with create_candidates dropped silently and council PASSes. (Patch 4)
- **Added** `redirect_implications` field on task-completion artifacts via `artifact-extensions.yaml` `task_completion.field_overrides`. List of `{from_url, to_url, reason, status: planned|applied|verified|deferred|excluded}`. Aggregated at session.handoff into a `redirect_coverage_report` projection (template at `templates/artifact-templates/redirect-coverage-report.md`). Layer 1 verifies coverage: every row with `status: applied` must have a paired `external_state.read_back` event against the platform's redirections-list endpoint with `divergence_detected: false`. Hypothesis H-G5; falsifier: a trashed/renamed/restructured URL ships without a redirect entry and Layer 1 PASSes. (Patch 5)
- **Added** `zz-seo-impact-audit.md` task template. End-of-session SEO regression check; runs after live-edit tasks complete and before session.handoff. Eight checks (rank_math metadata, sitemap freshness, robots.txt, redirect coverage cross-reference, canonical tags, schema markup, internal link graph, Core Web Vitals) with PASS/WARN/FAIL per item. WARN items go to `deferred-work.md`; FAIL items block session.handoff. Schema-opt-out via PROJECT.md `seo_audit_required: false` if the campaign doesn't touch SEO surface. Registered in `schema.yaml` `default_tasks.templates`.

### Schemas: all six

- **Added** `scope_completeness:` block to every schema's `capability-gates.yaml`. All schemas accept the full set `[complete, deferred, excluded-after-discovery, escalated]` in v5.1.1; future deploy-shaped schemas may tighten to `complete` only. (Patch 1, cross-reference Substrate.)
- **Added** `bootstrap-probe.md` per schema. `marketing-campaign` and `report-synthesis` ship full probes (WP REST + non-WP host platform list; filesystem listing for input_folder). `software-feature-ship` ships a `git ls-files` probe. The four other schemas (`client-onboarding`, `event-planning`, `compliance-audit`) ship documented stubs awaiting first-project empirical signal — they emit `bootstrap.probe_skipped` with operator-attestation as the v5.1.1 default. (Patch 3, cross-reference Substrate.)

### Tooling

- **`tools/hw-verify.py` updated for v5.1.1 event kinds and Layer 1 checks.** New event kinds in `KNOWN_EVENT_KINDS` and `REQUIRED_PAYLOAD_FIELDS`: `scope.complete`, `external_state.read_back`, `bootstrap.inventory_diff`, `bootstrap.scope_locked`, `bootstrap.probe_skipped`. New check functions: `check_scope_completeness`, `check_external_state_readback`, `check_bootstrap_probe`. New result fields: `scope_completeness_failures`, `external_state_readback_failures`, `external_state_readback_warnings`, `bootstrap_probe_failures`. Helper functions: `parse_scope_items_from_project_md`, `parse_capability_gates_yaml`, `find_schema_for_project`, `task_matches_readback_pattern`. v5.1 events.jsonl files validate unchanged.

### Documentation

- **Substantially expanded** `CONTRIBUTING.md` §"Updating and Contributing Schemas" — eight subsections covering directory layout, new-schema walkthrough, extension patterns, core-with-schema-config pattern, versioning, validation, CHANGELOG shape, and single-operator policy / clean-break changes. Title bumped to v5.1.1.
- **Updated** `core/SUBSTRATE.md` with §Scope Completeness, §External State Read-Back, §Bootstrap Inventory Sweep sections + new event-kind table rows.
- **Updated** `core/VERIFICATION.md` Layer 1 check table with rows 8 (scope_completeness), 9 (external_state_readback), 10 (bootstrap_probe).
- **Updated** `core/TYPED-ARTIFACTS.md` with §Live-Edit Proposal Artifacts.
- **Updated** `templates/executor-prompt.md` with the bootstrap-probe ceremony in the first-actions block.

### Version

- `harness_version: "5.1.1"` across all six schema files (note: the schema files retain the historical `"5.1"` string until a future commit updates them; v5.1.1 is strictly additive and v5.1 schemas continue to validate). HARNESS.md title and CONTRIBUTING.md title bumped.

### Hypothesis evaluation criteria reminder

The five hypotheses (H-G1 through H-G5) are evaluated by the next empirical run on `example-rebrand-rollout`, not by this build. Patch 1 catches Mailster-style scope skips, Patch 2 verifies external mutations, Patch 3 surfaces missing-page issues at bootstrap, Patch 4 forces vertical-page create-candidates to be enumerated, Patch 5 catches redirect coverage gaps, and the new `zz-seo-impact-audit.md` task runs the SEO check at the end. The next empirical run produces the falsification signal.

### Single-operator clean-break note

This release enforces all five new Layer 1 checks strictly. Single operator, no in-flight third-party projects, no transition mechanism shipped. Action required for `example-rebrand-rollout` (the only active project): before the v5.1.1 fix run, the operator (or a setup task in the fix-run prompt) updates that project's `events.jsonl` to include a `scope.complete` event reflecting the v5.1 session's terminal states, plus retroactive `external_state.read_back` events for the live-edit tasks that completed without them. This is project-data hygiene, not substrate work — flagged in V5.1.1-BUILD-REPORT.md §6 with the recommended cleanup approach.

---

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

### Backward-compat (pre-ship fixes)

- **`fire_id` on council events is recommended, not required.** v5.0.1 council events pre-date the `fire_id` field. The v5.1 projection generator falls back to the matching `council.invoke` event's `id` when grouping reports without a `fire_id`. v5.0.1 projects validate cleanly under v5.1 `hw verify`. (Fixed pre-ship after V5.1-BUILD-REPORT.md §6.)
- **`brand_voice_anchor` accepts both string and list during transition.** marketing-campaign's `brand_voice_anchor` field type was widened from `string|null` to `list[string]|null` in v5.1 to support multi-source voice anchors. To preserve backward-compat for v5.0.1 projects with a single-string anchor, v5.1 accepts both forms and normalizes string values to a single-element list internally. Operators may migrate to list form at their pace. The dual-form acceptance is a transition-period mechanism; future major versions may tighten to list-only after sufficient adoption signal. (Fixed pre-ship after V5.1-BUILD-REPORT.md §6.)

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
