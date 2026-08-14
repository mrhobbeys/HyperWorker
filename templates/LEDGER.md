# Ledger — {{ project_id }}

> **Generated projection of the whole chain, newest first.** Lives at `projects/<project-id>/LEDGER.md`. Regenerated on every state-changing event; never hand-edited (`core/SUBSTRATE.md` §Projection rules).
>
> Why this file exists: in the field, a hand-curated newest-first ledger beat the machine-perfect event log for rebuilding working context after every compaction — the executor's exit interview ranked the event log **last**. The hand-kept version also drifted: blocks filed out of sequence, superseded sections edited by hand. So the harness generates it. Read this first after `hw verify`, then the handoff, then raw artifacts as needed.

---

## 2026-08-14 — session close EV-0198

**Done**
- T-014 rebuild the reconciler — claim `file_exists` PASS
- T-013 inventory the drop directories

**Decided**
- DEC-021 one directory per instance; sync is additive on both legs
- ~~DEC-017 mirror the inbound leg nightly~~ [superseded by DEC-021]

**Found**
- F-031 four replies existed only on the pull side
- F-030 the push leg had been failing silently since 06-02 [suspect]

**Loops**
- opened L-007 vendor confirmation on the export format (external)
- closed L-003 rejoin the standby server — operator approved, done

**Operator said**
- "you're claiming it works — you only checked that it compiled"

**Friction**
- the recitation band rejected three honest paraphrases in a row

## 2026-08-13

**Done**
- T-012 reproduce the delete on a scratch pair — claim `cmd_exit` FAIL

---

## Rendering protocol

A fresh agent must produce this file byte-identically from an event prefix (`core/SUBSTRATE.md` §Projection rules, rule 2). Nothing here is summarized by judgment: every line is a field copied out of a payload. If you find yourself rewording, you are writing a handoff, not a ledger.

1. Filter `events.jsonl` to this `project`, in append order.
2. **Block boundaries:** a new block starts at each change of `ts` UTC date, and a `session.handoff` closes the block it lands in. Blocks render **newest first**. Lines *inside* a block stay in append order — the block is what happened, in the order it happened.
3. **Heading:** `## <YYYY-MM-DD>`, plus ` — session close <EV-NNNN>` when a `session.handoff` closed the block.
4. **Sections, in this fixed order**, each omitted entirely when empty (a block with no sections is not emitted):

   | Section | Source | Line |
   |---|---|---|
   | `**Done**` | `task.complete` | `<task_id> <title from task.create>` + ` — claim <predicate-kind> PASS\|FAIL` when the payload carries a `claim:` block |
   | `**Decided**` | `decision.add` | `<artifact_id> <title>` — title only, no rationale |
   | `**Found**` | `finding.add` | `<artifact_id> <title>` + ` [<status>]` when the payload carries a hypothesis `status` |
   | `**Loops**` | `loop.open` / `loop.close` | `opened <loop_id> <description> (<blocking_on>)` / `closed <loop_id> — <resolution>` |
   | `**Operator said**` | `operator.correction` | `"<note>"` |
   | `**Friction**` | `friction.log` | `<note>` (rich pre-v6 entries use `description`) |

5. **Superseded items are struck through, never deleted:** `- ~~<original line>~~ [superseded by <new_id>]`. The item keeps its original block and position — a ledger that quietly drops what turned out wrong is the hand-kept ledger's failure mode, not a fix for it.
6. One line per item, first line only, no line breaks. Titles are copied verbatim.
7. Write the file, compute its SHA-256, and update `hashes.json` for `projects/<project-id>/LEDGER.md`.

Nothing in the render depends on today's date, so the same event prefix always produces the same bytes.

## See also

- `core/SUBSTRATE.md` §Narrative Ledger — the primitive and H-S11
- `HARNESS.md` §Recovery Order — where this file sits when picking up cold
- `templates/session-handoff-template.md` — the handoff, read second
