# Golden Fixture — HyperWorker reference workspace

> A tiny, fully hash-chained workspace whose projections are pinned byte-for-byte.
> It turns the substrate's central promise — *two agents rendering from the same
> event prefix produce byte-identical projections* (`core/TYPED-ARTIFACTS.md`
> §Projection Rendering Protocol) — from an assertion into something
> `tools/hw-verify.py` can check.

## Why this exists

The substrate stakes integrity on byte-identical rendering: a citation hash, a
`hashes.json` entry, and a re-render from `events.jsonl` must all agree to the
byte. Until now nothing held that promise to account — the rules lived in prose
and were trusted, not tested. `golden-workspace/` is the reference: a known
`events.jsonl`, the exact projections it must produce, and the `hashes.json`
binding them. A renderer that drifts from these bytes makes `hw verify` FAIL
here, which is exactly the regression signal the fixture is here to provide.

## What's in it

`golden-workspace/` is a complete workspace for one small project, `golden-demo`:

```
golden-workspace/
  .hyperworker/
    events.jsonl          # 7 hash-chained events (canonical, append-only)
    hashes.json           # projection path -> sha256:<short>
  projects/
    active_project.md     # projection (Lock pointer)
    golden-demo/
      PROJECT.md          # Mutable Surface (NOT event-sourced, not in hashes.json)
      TASK-STATE.yaml     # projection (task state)
      decisions/DEC-001.md  # projection (typed artifact)
      findings/F-001.md     # projection (typed artifact; cites DEC-001)
```

The 7-event chain is the smallest arc that still exercises the load-bearing
machinery:

| EV | kind | what it proves the fixture covers |
|----|------|-----------------------------------|
| EV-0001 | `project.activate` | Lock projection (`active_project.md`) |
| EV-0002 | `bootstrap.probe_skipped` | the bootstrap-probe Layer 1 check's skip path |
| EV-0003 | `decision.add` (DEC-001) | typed-artifact projection rendering |
| EV-0004 | `finding.add` (F-001) | a **valid citation** `[DEC-001#<short>]` resolved at the live projection hash |
| EV-0005 | `task.create` (T-001) | task consuming a decision; citation in a `task.create` payload |
| EV-0006 | `task.status` | state transition → `TASK-STATE.yaml` |
| EV-0007 | `task.complete` | terminal task state; `completed_at` rendering |

## How to check it

```bash
python tools/hw-verify.py --workspace tools/fixtures/golden-workspace
# result: PASS
```

`PASS` means: every event hash recomputes, the chain is unbroken from the
all-zeros root, every projection's on-disk bytes match `hashes.json`, and every
citation resolves to a current projection hash. The fixture is verified to
satisfy all of these (see "Properties checked" below).

To confirm the fixture is a *reference* and not just a passing snapshot,
regenerate it and verify nothing changed:

```bash
python tools/make-golden-fixture.py        # deterministic; no clocks, no RNG
git diff --stat tools/fixtures/golden-workspace   # (if tracked) -> empty
```

`make-golden-fixture.py` is the reference renderer. Any independent renderer that
claims substrate-conformance must reproduce these exact bytes from the same
`events.jsonl`.

## Properties verified

These were checked when the fixture was built (and re-checkable any time):

1. **PASS** — `hw verify` reports zero blocking findings.
2. **Idempotent** — regenerating produces byte-identical files (`sha256sum`
   of every file is unchanged across runs).
3. **Drift is caught** — appending a single byte to any projection makes
   `hw verify` report `projection_drift` → FAIL.
4. **Tamper is caught** — mutating an event payload without recomputing its hash
   makes `hw verify` report `tamper` → FAIL.

Properties 3–4 are the point: the fixture fails loudly when rendering or the log
diverges, which is what lets it function as a regression test for any future
renderer or `hw verify` reimplementation.

## Rendering decisions (the reference, made explicit)

`core/TYPED-ARTIFACTS.md` specifies field order and determinism but leaves some
serialization details to the renderer. The fixture commits to these, and any
conformant renderer must match them:

- **Frontmatter field order:** the structural minimum first —
  `id, kind, created_at, hash, confidence, reverses, superseded_by, tags` —
  then schema/kind fields in the order the kind documents them
  (e.g. decision: `title, alternatives_considered, rationale, constraints_imposed`).
- **The `hash:` frontmatter field** carries `sha256:<short>` of the artifact's
  originating `<kind>.add` **event** hash. It deliberately does **not** carry the
  projection-file hash (which would be self-referential — the file cannot contain
  its own hash). The projection-file hash is the citation hash and lives in
  `hashes.json`.
- **String values** are JSON-encoded (`ensure_ascii=False`) so embedded quotes,
  colons, and non-ASCII characters round-trip without ambiguity.
- **Inline lists** (`tags`, `depends_on`, `consumes`) render as
  `[a, b]`; block lists (`alternatives_considered`, `implications`,
  `constraints_imposed`) render as `  - item` lines.
- **Line endings are LF**, UTF-8, no BOM. The substrate hashes projection bytes
  as written to disk; CRLF would change every hash. The generator writes with
  `newline=""` to suppress Windows translation.
- **Citation hash** = first 12 lowercase hex of `sha256(projection bytes)`,
  matching `core/SUBSTRATE.md` §Citation Format and the value in `hashes.json`.

## Regenerating / extending

`tools/make-golden-fixture.py` builds the whole workspace from a fixed event
list. To extend the fixture (add an artifact, a supersede chain, a council
fire), add events to the chain in that script and re-run; the script recomputes
all hashes and the `hashes.json` sidecar. Keep it tiny on purpose — the fixture's
value is in being small enough to read end-to-end and reason about by hand.
