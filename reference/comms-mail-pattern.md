# Reference Pattern — File Mailboxes Between Machines

> **A reference pattern, not a core mechanism.** Nothing in `core/` requires it and no verifier check enforces it. It is what ten weeks of a multi-machine production engagement converged on for passing work between agents on different boxes through a shared folder, and it is written down so the next engagement starts where that one finished instead of re-deriving it at the same cost.
>
> Use it when two or more instances communicate by dropping files somewhere both can see. Ignore it entirely when they do not.
>
> One rule from `core/` does apply and is not optional here: `core/SUBSTRATE.md` §Transport Rules. Everything below is that protocol made concrete for a mailbox.

---

## Numbered request/reply pairs

Every exchange is a numbered pair. A request arrives as `PREFIX-###`; its reply goes out as `PREFIXR-###` with the **same number**. The pair is the unit — a reply that does not carry its request's number is unfileable.

- **Counters are per-prefix and independent.** `DC-014` and `HC-014` are unrelated messages. Never maintain one global counter across prefixes.
- **Get the next number by listing the directory newest-first and reading the top.** Do not guess it, do not remember it from last session, and never reuse one. A duplicate number makes two different exchanges indistinguishable forever after.
- If the listing is ambiguous — a gap, a partial write, two files claiming one number — stop and ask. Picking one is how a mailbox loses a message quietly.

## Prefixes are assigned, never chosen

The operator's convention decides which prefix a channel uses. **A sender never invents one.** A prefix is a routing fact about the channel, not a label the author gets to pick, and one improvised prefix splits a conversation into two threads that nobody can list together.

When a message arrives on a prefix the convention does not sanction: **answer it on the convention's prefix, and say so in the reply.** Do not answer on the unsanctioned prefix (that ratifies it), and do not refuse to answer (that loses the content). One line is enough: *"Received as `XX-007`; `XX` is not a sanctioned prefix on this channel, so this reply is filed as `DCR-018`. Please use `DC-` here."*

## Three message classes, not two

Requests and replies are the first two. The third is real and formalizing it beats forbidding it:

| Class | Form | What it is |
|---|---|---|
| Request | `PREFIX-###` | An ask, from whoever owns the channel's asking side. |
| Reply | `PREFIXR-###` | The paired answer. Same number, always. |
| Note | `NOTE-###` | An **unsolicited** observation from an executor: something surprising, something that will bite later, something nobody asked about. Its own counter; never expects a reply. |

Unsolicited notes are where the field evidence actually came from. An executor that has nowhere legitimate to put "this looks wrong" either drops it or smuggles it into an unrelated reply where nobody reads it.

## Corrections are new numbers

A correction, an addendum, or a retraction is a **new numbered message** that references the old one. Never `DCR-014b`, never `DCR-014-revised`, never a second file claiming the same number.

The reason is the same one that makes the event log append-only: the other side may have already read and acted on the original. Numbers are the only handle either side has for what was said, and a suffix reuse makes two parties disagree about what `014` was with nothing to point at.

## Append-only covers attachments and scripts

**This is the rule most likely to be violated and the most expensive when it is.**

Attached documents and scripts are messages too. A correction to an attachment is a **new versioned filename** — `cutover-run-order-v3.md`, not an edit to `cutover-run-order.md`.

*Field incident:* a live cutover run-order document was edited in place. Anyone who had already pulled a copy was holding different instructions from anyone who pulled after, with the same filename on both, during a cutover. Nothing detected it. Editing a script someone else already fetched is the same failure with worse consequences, and it is why `core/TOOLS.md` records a hash for every file it ships.

## Every message is self-contained

The reader may have no context, no scrollback, and no memory of the thread. Header on every message, no exceptions:

```
From:  <machine / instance / role>
To:    <machine / instance / role>
Date:  <ISO 8601>
Re:    <the request number this answers, or the subject if it opens a thread>
Type:  read-only | mutating
```

**`Type` is the load-bearing field.** It declares up front whether acting on this message changes anything.

- `read-only` — nothing on the far side is modified. Investigation, measurement, reporting.
- `mutating` — something changes, and the message **states its rollback** in the same breath. What was changed, and how to put it back. A mutating message with no rollback is not ready to send.

## Asks are ordered numbered lists

Not prose paragraphs with the asks buried in them. Numbered, ordered, one action each — so the reply can answer them by number and both sides can see which ones were not answered. Prose asks get partially answered and nobody notices which part was skipped.

## Report method, not status

"Done", "working on it", and "looks good" are worth nothing to the reader. Report **what you did and how you know**: the command you ran, the output you saw, the path you checked. `core/SUBSTRATE.md` §Evidence Capture is the substrate version of the same habit — keep the bytes, not the conclusion.

## State what is NOT changing

Explicitly. Every mutating message names the things it leaves alone. The far side's model of the system is built from these messages, and unstated scope is assumed scope: silence about a service reads as "unchanged" to one reader and "unspecified" to another, and one of them is about to be wrong.

## Write, then re-stat, then claim posted

A message is not posted until you **re-read it at the destination directory** — the same directory you read the inbound message from. Not the copy's exit code, not the absence of an error, not the source file still sitting there.

Where the schema requires claims, cite the re-stat as the predicate (`file_exists` on the destination path, or `file_sha256` when the content matters) so the assertion is replayable rather than a sentence in a report. See `core/SUBSTRATE.md` §Transport Rules (b) and §Checked Claims.

Corollary, worth stating separately: **posted and received are different facts.** Only a reply, or a re-stat performed by the far side, is evidence of the second one.

## Sync is additive on both legs

Never mirror. Never delete on pull. A half-completed round trip with a mirror flag on the pull leg silently deleted four un-pushed replies on a real engagement. Deletion is a deliberate act on the side that owns the file, never a side effect of copying. `core/SUBSTRATE.md` §Transport Rules (a).

## Archive with a reason

An `archive/` folder under the mailbox, and an `INDEX.md` inside it that says **why each batch was archived** — resolved, superseded, obsolete after a cutover, whatever it was. A dated folder with no reason is a folder nobody can safely delete and nobody can safely read.

**Sync probes and heartbeat files are debug exhaust.** They prove a channel works; they are not correspondence. Archive them once the channel is proven, or the mailbox fills with them and the real messages stop being findable.

## RELAYED- markers when content crosses channels

When an orchestrator carries content from one channel into another, mark it `RELAYED-` and name both ends. Relayed content that looks native makes the receiving side attribute it to the wrong author and reply into a channel the original sender is not reading.

## An operator-gated ask needs an open loop

**Any ask that ends "the only remaining gate is the operator's word" gets a `loop.open` in the harness, immediately.**

*Field incident:* exactly such a message — every technical gate cleared, one human decision outstanding — sat unconsumed for **five weeks**. Nothing was wrong with the work. The failure was that "waiting on the operator" lived in a sentence in a mailbox instead of a row something could count. The divergence surfaced through an unrelated symptom, in production.

`loop.open` with `blocking_on: operator-word` makes it a countable row: `hw status` leads with it once it passes `stale_after_days`, and every `session.handoff` carries it forward. See `core/SUBSTRATE.md` §Open Loops.

## Urgent goes to the human directly

**The operator does not read the bus.** Anything the human must see urgently goes to the human channel, directly, with the **finding first** — not the preamble, not the methodology, not the context that led to it. A mailbox is for machine-to-machine correspondence; it is not, and was never, a notification system.

---

## Related

- `core/SUBSTRATE.md` §Transport Rules — the four rules this pattern instantiates.
- `core/SUBSTRATE.md` §Open Loops — what an operator-gated ask must become.
- `core/SUBSTRATE.md` §Checked Claims — how a re-stat becomes replayable.
- `core/SUBSTRATE.md` §Secrets Gate — a mailbox is a place credentials leak; a sync digest already copied two passwords into an append-only log once.
- `core/LOCK.md` §Programs — the shape of the multi-instance work this pattern usually serves.
