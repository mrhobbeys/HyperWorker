# Field Report — 2026-07 gather, machine 1

**What this is.** Harness-applicable evidence collected from live HyperWorker deployments on one operator machine plus a prior cross-machine gather archive. Everything is genericized: deployments are described by shape, not by client, domain, or person. This report collects; it does not decide. Mechanism changes derived from it are the operator's call.

**Corpus.** Six-plus deployments were examined: a work-finder program (revenue-opportunity discovery across government bids, commercial channels, and inbound lead mining), a multi-site website-recovery program (per-site repair / SEO / monetization / keyword workstreams), a brand-ranking engagement (source of the `brand-ecosystem-audit` and `market-gap-intelligence` schemas), a legacy point-of-sale cleanroom rebuild (source of `cleanroom-rebuild`), an infrastructure-recovery engagement (source of the checked-claims proposal below), and the harness author's own release-validation runs (source of the ceremony-cost measurements and the golden fixture). Versions observed in the field: v5.2.0 installations carrying v5.2.1 changelogs (version drift, now fixed in this repo).

---

## A. Program-shaped work strains the Lock — and the field converged on one answer

The strongest cross-deployment signal. Three deployments independently built the same structure above the Lock rather than inside it:

1. **The work-finder program** ran ~14 concurrent `.hyperworker` instances: one per bid segment / opportunity channel / dedicated deal, plus an informal orchestrator ("the program") that every schema's handoff task reports up to — a convention, never itself schematized. Its friction log states it plainly: *"Lock assumes one active project per workspace, but the operator treats the whole workspace as 'the' active project with concurrent subprojects... Needs a structural answer (program/subproject hierarchy or multi-lock)."* An open backlog item requests a lock/subproject-model restructure. A decision record contains the operator's own words: *"we are abusing the subproject system design."*
2. **The website-recovery program** runs a per-site orchestrator that is **itself a HyperWorker instance** — its subject matter is the program: a registry of workstream subprojects, routing decisions (14 of them), and roll-ups. Its load-bearing decision: *"The raw HyperWorker model of many 'projects' sharing a single workspace event log is REJECTED here, because concurrent writers corrupt the event log and hashes."*
3. **The cleanroom-rebuild deployment** decomposed one large rebuild into an umbrella tracking project plus 8 subprojects, each a full HyperWorker project activated in sequence with the rest parked — living within the Lock by paying constant park/activate churn.

Supporting evidence:

- A parallel-execution postmortem (work-finder, segment isolation doc): *"Running segment chats in parallel broke the shared HyperWorker substrate... Fix: every chat is fully isolated to its own folder."* **One `events.jsonl` = one writer** is the rule every deployment adopted after contact with reality.
- A director/mailbox coordination layer at a fourth deployment explicitly acknowledges the boundary: *"per VISION, HyperWorker does not become a meta-orchestration layer; the director runs alongside it."*
- Downstream support tooling appeared: a SQLite pipeline tracker (opportunities / activities / quotes / signals tables, claim-with-expiring-lease semantics, optimistic concurrency, idempotent signal intake) built so multiple agents can work many bids in tandem — infrastructure the harness declines to be.
- Promote-and-swap, not nesting: when one opportunity gets hot, the orchestrator spins up a dedicated `single-opportunity` project — a hot Finding graduates to its own project. Sequential promotion; no deployment attempted parent-and-child simultaneously active in one instance.

**Status of H-L1** (`core/LOCK.md`): its falsifier — an operator running two projects concurrently *in one instance* with cleaner outcomes — did **not** fire. Operators who tried concurrent writers in one substrate corrupted it; every deployment retreated to one-writer-per-instance. What the field demonstrates is not "the Lock is wrong" but "the Lock is per-instance and the *program layer above instances* is real, unnamed, and unschematized." Three independent reinventions of the same orchestrator shape is the signal.

## B. Recurring / ongoing work has no lifecycle

- Work-finder schemas carry a `cadence` bootstrap question (default `"weekly"`), and their handoff templates say "next sweep date is set per cadence" — in prose. Nothing in the substrate tracks "next sweep due." Recurrence is manual discipline on top of a one-shot project shape.
- A registrations subproject's friction log: *"client-onboarding assumes a single external client and a terminal handoff... [this] is a perpetual shared-service registry... there is no natural 'done.'"*
- Two deployments independently improvised the same escape hatch: a `deferred (ongoing)` terminal state with status handed to "an orchestrator" (an ongoing-SEO plan task "kept open-ended (no hard wrap)"; a living-workbook project whose Archived section reads "open-ended — ongoing maintenance continues").
- The stock answer to recurrence (compliance-audit: archive, then subscribe to cross-project anti-patterns at next year's bootstrap) fits annual cycles, not weekly sweeps.

## C. Integrity is not truth — the checked-claims proposal

An infrastructure-recovery engagement produced a complete improvement proposal (baselined v5.2.0, targeted v5.3), reproduced here in genericized summary. Its one-line thesis: *"The hash chain did its job. It proved nothing was tampered with. It could not prove anything was true."*

P1 (each prevented a real loss on that engagement):
1. **Checked claims** — any event asserting world-state carries a machine-checkable predicate (`{file_exists: ...}`, `{cmd_exit: ..., expect: ...}`, `{thumbprint: ...}`), and `hw verify` gains a mode that replays predicates against the world, separate from chain integrity. Motivating incident: three systems (agent report, human ledger, harness projection) all recorded two files as "posted" while the files did not exist; `hw verify` passed throughout.
2. **Exclusion requires a dynamic test** — elimination-matrix entries get two states: `suspect` (static read or argument) vs `excluded` (a test exercised the failing operation; invalid without a `test_ref` citing the test event). Motivating incident: a true root cause sat in the EXCLUDED column for two weeks on a fluent static argument.
3. **Secrets never enter the append-only substrate** — gate `hw add` with a secret scanner (entropy + patterns); store by vault reference or hash; replace sync blocklists with allowlists. Motivating incident: a temporary credential is now permanent in an append-only log; only remediation was rotating it in the real world.
4. **Frontier staleness clock** — track the cheapest reproducing test; emit `frontier.stale` after N days or M environment-changing events; re-run the base reproducer before opening any new theory branch. Motivating incident: the fault "self-healed" during a two-week pause and nobody noticed.

P2: an `evidence.capture` event kind (raw output + hash + producing command, so findings cite evidence instead of paraphrasing it); make `friction.log` genuinely one-line cheap (the engagement's highest-reuse lessons — operational gotchas — had no home light enough to use); auto-project a latest-first narrative ledger digest from the event stream (the hand-kept ledger beat the machine-perfect log for context recovery every time); default the per-run sync digest off for single-executor engagements.

P3: a `profile: single-executor` that suppresses multi-actor ceremony (`actor` fields, citation handles nothing consumes).

What that engagement said NOT to change: the hash chain, the gating model, and the typed-artifact vocabulary all earned their keep.

## D. Smaller gaps

- **No amend/supersede tooling.** The website-recovery orchestrator needed bespoke one-off Python scripts to amend decisions (manually replaying the hash chain and re-rendering projections), and a rules file was found stale — still citing a superseded decision — because amendments don't propagate. The supersede *protocol* exists; the operable command path does not.
- **Conditional tasks have no first-class primitive.** Schema authors flagged it while testing the market-intelligence packs: they wanted "run this task only if condition X" and had no declared way to say it.
- **YAML authoring footguns** in schema packs: unquoted `list[string]` tokens inside flow mappings, bare `yes`/`no` coerced to booleans by YAML 1.1, and "required means key-present, not truthy" semantics confusion. The two imported market-intelligence packs carry the fixes; the pattern will recur in any hand-authored pack.
- **Unpruned schema inheritance is not harmless.** Field copies of the work-finder schemas (before import curation) shipped two interleaved `00–05` task-template tracks — the parent report-synthesis spine plus the schema's real spine — with duplicate numeric prefixes, plus orphaned council gates wired to tasks not in `default_tasks`. Import curation removed all of it from the repo copies, but `hw schema save` produced it; the fork-a-schema path wants a prune step.
- **Rules hardened against agent hedging.** A later field revision of one rules-template added two Tier-1 rules that then propagated at import: *"COMMIT to one recommended path — never refuse to recommend"* and *"Operator decisions are FINAL: record verbatim, never re-open or contradict. Raise a concern once, then comply."* Circumstantial evidence of the failure mode they answer.

## Known-uncollected material

A prior cross-machine gather recorded ~1,576 cloud-only paths that were never downloaded, including four named schemas with zero collected content (`book-edit-test`, `content-piece-test`, `course-master-plan-test`, `pm-site-explorer-test`) and several real deployments (content-creation, course-building, CRM-commitment, server-migration, and project-builder shapes). These are the second machine's gather targets.

## Deferred to the operator (deliberately not decided here)

1. Whether program-shaped work (A) becomes: a core lifecycle change, a first-class **program/orchestrator schema** (the shape the field already invented — an orchestrator that is itself a locked HyperWorker project whose artifacts are a subproject registry, routing decisions, and roll-ups), a sibling repo, or a documented pattern only.
2. Whether ongoing/recurring lifecycle (B) enters the substrate (e.g., `lifecycle: terminal | ongoing`, cycle events, a computable next-due) and under what hypothesis/falsifier.
3. Which of the checked-claims proposal items (C) ship in v5.3 and in what order.
4. Whether the amend/supersede command path and a conditional-task primitive (D) are v5.3 or later.
