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

**Prefix issuance precedes first use.** The sanctioned prefix is issued before the channel's first message, not settled after one has already gone out. A sidequest opened on a sender-minted prefix and was reassigned mid-stream; the first message had to be voided and both executors were briefly holding two candidate reply series for one conversation. Issuing the prefix is part of opening the channel — a channel whose prefix is still being decided is not open yet.

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

## Structural contact is plumbing, not a channel

Some agents **structurally require** a human. A login only a person can complete; a trigger only a person can pull; a machine only a person is standing next to. The gate cannot be designed away — an agent that cannot enter a credential will always need someone to sign it in.

So the rule is not *less* contact. It is **narrower** contact.

> **The contact is plumbing, not a channel.** When a human signs an agent in or triggers it, that is a hand on a keyboard, not a meeting. No questions. No findings. No decisions sought. No "while you're here." Everything goes into the record and comes back through the orchestrator.

**Self-check, and it is a reliable one:** if you are composing a sentence to the human that is not *"please sign me in"* or *"done, you can close it"* — **that sentence belongs in a numbered message.** The urge to add it is the drift, caught early.

### Why this matters more than it looks

Repeated contact feels like access. It is the same drift that happens with the employee whose desk is nearest the boss: proximity gets mistaken for a reporting line, and the agents that need a human most are reliably the ones that wander furthest off the chain.

**There are two costs, and the second is the serious one.**

The first is role damage: an agent routing around the orchestrator breaks the structure everyone else is working inside.

The second is that it **hides system flaws**. When a human quietly patches a hole in person, the orchestrator never learns the hole existed. The structure keeps reporting that it works, while what is actually working is a person filling gaps by hand, in conversations that leave no record. **That is how a design failure survives: invisibly, because someone kept fixing it in the hallway.** The next engagement inherits the same flaw and the same undocumented patch, and the harness's own evidence about itself is quietly false.

## Reachability discipline

**Before you reference a document, check that the recipient can actually reach it.** Not whether it exists, not whether it is current — whether *they can open it*. An instruction to "read the project rules file" is worthless to an agent whose only reachable surface is its own mailbox and its own box, and it is worse than worthless when the agent guesses at the contents rather than saying so.

Three obligations follow, and they are cheap:

**1. Keep a who-can-reach-what map.** `OR-001.reachability_map` is the harness-side home (`schemas/artifacts/operating-reality.yaml`); a table in the mailbox's own `README.md` works for a channel that has no OR. One row per party: what it can reach, what it cannot, and how it is triggered. Consult it before writing a reference into any message.

**2. Re-post when a load-bearing document changes materially.** A snapshot placed in a mailbox is immutable and **goes stale silently** — nothing about the file announces that the original moved on. A reader treats it as current because it is the only copy they have, which is the inference-hardening-into-a-fact failure wearing a filename (`core/AUTHORITY.md` §The consequence model). So when the source document changes in a way that would change a reader's behavior, post a **fresh numbered snapshot** to every affected mailbox, marked as **superseding** the previous copy (`Supersedes:` header, §Field additions). Not an edit to the old one — §Corrections are new numbers applies to snapshots exactly as it applies to messages.

**3. An agent told to read something it cannot open SAYS SO.** Standing instruction, every party, no exceptions. Not a workaround, not a reconstruction from context, not an assumption about what the document probably said. One line back — *"I cannot reach that path; send the contents as a numbered message"* — costs one round trip. Guessing costs the entire branch of work built on the guess, and it surfaces late, as a wrong action rather than a wrong belief.

### Batch by trigger capability

How much you send depends on **how the recipient is triggered**, not on how much you have to say.

| Recipient trigger | Batching |
|---|---|
| **Self-polling** — checks its own mailbox | A stream of smaller messages is fine. Send when you know a thing. |
| **Human-triggered** — someone must tell it to check | **Every message is a pending obligation on that human.** Batch direction into fewer complete messages; **front-load the decision tree** so the recipient can work through forks without stopping; never post speculatively. |

A speculative message to a human-triggered agent spends a human interaction to deliver a maybe. Three of them spend three, and the fourth one — the one that mattered — arrives to a human who has learned that checking mail is low-yield.

---

## Field additions (6.0.1)

Two executors on unrelated engagements, asked independently for friction and harness feedback, converged on the same set of mailbox failures. Each rule below is one of them, stated as short as it will go.

**The synced path contract belongs in a README inside the mailbox.** Which subtree actually propagates — commonly `outbox/` and nothing above it — is a fact the executor must have on arrival, not one it derives from a delivery that never happened. An executor wrote two deliverables to the mailbox's parent folder, where nothing syncs; both were silently undelivered and surfaced only when the operator said "mail didn't land." The contract is a property of the mailbox, so it is documented in the mailbox: a `README.md` beside `outbox/` naming exactly what propagates and what does not.

**Verify by exact-path stat, never by directory enumeration.** On a flaky or redirected share the two are not equivalent: enumerating a wedged RDP-redirected link hung for minutes (one tool timeout) while an exact-path existence check on a file in that same directory returned immediately, and the scheduled copy kept working throughout. A share can be present at the root and un-enumerable below it. Since §Write, then re-stat, then claim posted already requires you to name the destination path, stat that path — listing the directory buys nothing and can wedge the session.

**Never read a file the instant it appears.** On an async-synced share the file's name arrives before its bytes. Wait for a **stable, non-zero size** — two consecutive stats agreeing — before reading. A mailbox watcher read a file mid-copy and delivered an empty body to its executor as if it were the message.

**Transient sync errors are routine, not incidents.** Intermittent access-denied and copy-tool failures (robocopy exit 16 among them) are the normal weather on these links. The handling is a retry loop plus a re-stat of the destination, every time, not an escalation. What would actually remove the uncertainty is a **protocol-level delivery ack** — a receipt from the far side rather than an inference from the near side. That does not exist yet; both executors named it as the wanted fix, and it is carried as a known gap in `CHANGELOG.md`.

**Drain and sort the whole inbox, detect supersedes and urgency, then act.** Messages arrive in bursts, and a later message in one burst routinely supersedes an earlier one's method or jumps the queue. Read everything waiting, order it, resolve what supersedes what and what is urgent — and only then take the first action. An executor acted on a message that a message already sitting in the same burst had superseded.

To make that sortable by something other than prose, two header fields join §Every message is self-contained, both optional and both machine-readable:

```
Supersedes: <message id this replaces, or absent>
Priority:   normal | urgent
```

`Supersedes:` states the relationship §Corrections are new numbers already requires in words; `Priority:` is what lets an urgent item be found without reading every body first. Neither replaces reading the messages — they make the sort cheap enough that draining first stops being the expensive option.

**An alarm is not a logger; ship both and never conflate them.** A tripwire that writes only when it trips holds no history — there is nothing to read afterward for trend, baseline, or "when did this start." An operator reasonably assumed the storage tripwire was also the log source ("I thought logs came from the tripwire?") and it never had been. Alarm and logger are two tools with two purposes: the alarm interrupts, the logger accumulates. Say which one a thing is in its own header, and if the question "what did it look like an hour ago" matters, something must have been writing an hour ago.

**Prefix issuance precedes first use.** Stated in full under §Prefixes are assigned, never chosen — a channel whose prefix is still being decided is not open yet.

---

## Related

- `core/SUBSTRATE.md` §Transport Rules — the four rules this pattern instantiates.
- `core/AUTHORITY.md` — why a human in the loop is not automatically a gate, and why an agent that fears consequences routes around the structure.
- `schemas/artifacts/operating-reality.yaml` `reachability_map` — the harness-side home for who-can-reach-what.
- `core/SUBSTRATE.md` §Open Loops — what an operator-gated ask must become.
- `core/SUBSTRATE.md` §Checked Claims — how a re-stat becomes replayable.
- `core/SUBSTRATE.md` §Secrets Gate — a mailbox is a place credentials leak; a sync digest already copied two passwords into an append-only log once.
- `core/LOCK.md` §Programs — the shape of the multi-instance work this pattern usually serves.
