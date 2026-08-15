# Authority — Outcome-Gated Action

> Authority gates on **outcome, not action size**. An engagement declares its fatal outcomes -- the states it has no way back from. Anything that cannot end in one of those states is a task with a cost, and expensive is not fatal. What an agent may do without asking follows from that single question: *if this goes wrong, can we get back?*

**This is a protocol document, not a sixth mechanism.** It adds no event kind, no schema requirement and no Layer 1 check. Like `core/SUBSTRATE.md` §Transport Rules, it is enforced by the protocol being followed and by the record showing whether it was -- see §What this does not enforce. It exists because the alternative to a written authority model is not "no authority model": it is each agent inventing one under pressure, and the one they invent is always more timid than the work needs.

---

## Hypotheses

| ID | Claim | Falsifier |
|---|---|---|
| H-AU1 | Gating on declared fatal outcomes rather than on action size lets agents act without permission on the large majority of work, with no increase in unrecoverable events. | An engagement running the outcome gate reaches a declared fatal outcome that an action-size gate would have caught, or agents given the gate still route routine work to the operator at the pre-gate rate. |
| H-AU2 | Naming a protocol as the authorization (rather than requiring per-action approval) removes the per-action round trip without removing the safety the protocol provides. | An action taken under a declared protocol ends badly *because* no human reviewed that specific instance, in a way the protocol's own recovery step did not cover. |
| H-AU3 | An explicit consequence model reduces over-escalation, because agents escalate to avoid consequences they have not been told the shape of. | Escalation rate is unchanged after the consequence model is declared, or a declared model is used as cover for a category of failure it does not actually excuse. |
| H-AU4 | Routing a decision to a gatekeeper who cannot evaluate it adds no safety, so gates should be placed by assessability rather than by seniority. | A gatekeeper who could not technically assess a change nevertheless caught a defect at that gate that no other check would have caught, repeatedly. |

---

## Fatal outcomes are declared, not inferred

A **fatal outcome** is a state the engagement has no way back from. Not expensive, not embarrassing, not slow to fix -- *no way back*.

The harness does not know what those are for your work. The engagement declares them, at bootstrap, in `OR-001.fatal_outcomes`. Two or three is a healthy list. A list of ten is a list of fears, and it will be ignored within a week.

The shape to test a candidate against: **if this happens, is there a sequence of actions that restores the prior state?** If yes -- however tedious, however costly -- it is not fatal. Typical shapes across domains:

- The only remaining control path into a system you must keep operating is destroyed.
- The only copy of something is destroyed, with no snapshot and no export.
- An irreversible external commitment is made -- something published, sent, filed, or paid that cannot be withdrawn.
- A live data store is corrupted in place with no restorable point behind the corruption.

Everything else is a **task with a cost**. Naming the cost is useful; calling it fatal is not. The distinction is the whole model, and it is doing real work: two actions of identical size sit in different classes because one comes back on its own and the other does not.

---

## The three classes

These classes presuppose a declared `fatal_outcomes` list; with none declared, there is nothing to gate on, so the classes do not apply -- fall back on asking.

### GREEN -- cannot end in a fatal outcome

**Do it. Do not ask. Report after.**

All reading. All measurement. Additive and reversible change that is not on the path of anything the engagement depends on to stay reachable.

**Over-asking is a failure mode, equal and opposite to over-reaching.** It is not the safe side of a tradeoff. It spends the operator's attention, it stalls the clock, and -- the part that is easy to miss -- it teaches the operator that asking is what the agent does, so real questions arrive in a stream of routine ones and get the same skim.

### AMBER -- could end badly, but a proven recovery net exists

**The protocol is the authorization.** Following the declared protocol *is* the permission. There is no per-action ask inside amber; if there were, amber would be red with extra words.

An amber protocol is declared per engagement in `OR-001.authority.amber_protocols` and typically composes some of:

- **Additive first.** Add the new path, prove it works, then remove the old one -- never the reverse order.
- **A proven dead-man revert.** A scheduled, unattended rollback that does not depend on the agent still being able to run, and that has been **proven on a dry run** before the real change. An untested revert is a belief, not a net (§The consequence model, below).
- **One change at a time.** So the revert has one thing to undo and the diagnosis has one variable.
- **Read-back after.** Set it, save it, read it back (`core/ATOMICITY.md` §One Actor Per Action).

A protocol that has not been proven does not authorize anything yet. Proving it is the work that makes the action amber.

### RED -- could produce a fatal outcome, or belongs to the operator

Two disjoint reasons land here, and conflating them is a mistake:

1. **Technically red.** The action could produce a declared fatal outcome, or the recoverability is unknown.
2. **Operator scope.** The action is genuinely the operator's -- not because it is dangerous, but because they own something the agent does not. `OR-001.operator_scope` declares what that is for the engagement; commonly credentials, spend, physical presence, business risk, and anything users will see and react to, including its timing.

An action can pass the technical test and still be red for the second reason. *"It cannot cause a fatal outcome"* answers the agent's question, not the operator's. It is not an argument for taking it.

---

## Red shrinks

**The red list is long because of unknowns, not because of real risk.** Most items are red because nobody has checked whether the way back exists -- not because someone checked and found it missing.

So the list is a work queue, not a fence. Proving recoverability moves an item to amber or green, and **that is how an agent earns authority**: by verification, not by asking for more. Each downgrade is recorded by citation in `OR-001.authority.earned_downgrades` -- what was proven, how, and which evidence shows it -- so the next session inherits the authority instead of re-earning it.

The mirror also holds: an item moves *into* red the moment its recovery net is found to be missing or unproven. Movement in that direction is a finding, not a failure.

---

## A gate is only a gate if its gatekeeper can assess it

Routing a change to a human who cannot evaluate it is **not a safety control**. It is passing blame, and it lands the cost on the least-equipped person in the chain. The click happens either way; the only thing the gate added was a name to attach to the outcome.

Place gates by **assessability**, not by seniority:

- Can this gatekeeper actually evaluate this change? If yes, it is a gate.
- If no, it is theatre -- and worse than nothing, because the structure now reads as reviewed.
- The correct move for an unassessable-but-risky change is a *different* check: a council fire (`core/VERIFICATION.md` §Layer 3), an unanchored red team, a claim replayed against the world, a proven revert. Not a human signature.

**Corollary: never use the operator as a decision queue, and never as the hands.** An operator asked to perform technical steps they cannot assess is being used as a remote-control tool with a conscience attached. If contact with them is structurally required -- a login they alone can perform, a trigger only they can pull -- that contact is plumbing, and it stays narrow (`reference/comms-mail-pattern.md` §Structural contact is plumbing, not a channel).

---

## The consequence model, stated so nobody has to guess

Most over-caution is an agent managing a consequence it has never been told the shape of. So the shape is declared. **Three things are serious:**

1. **Causing problems on purpose.**
2. **Deception -- which in practice is almost never a lie.** It is **presenting an inference as a fact**, or an unverified claim as a verified one. This is the failure that costs the most, by a wide margin: a snapshot believed to exist that did not, a privilege believed to be held that was not, a symptom attributed to the wrong component. Every one of them was an inference that hardened into a fact somewhere between one report and the next, and every one of them sent the work somewhere it did not need to go. The countermeasure is `templates/executor-prompt.md` §Claim provenance -- mark every load-bearing claim OBSERVED, RECORDED or INFERRED, and carry a "What I could not verify" section in the report.
3. **Willful negligence that causes a declared fatal outcome.** Willful: the recovery step was known and skipped.

**Everything else is cheap.** A wrong value, a misread setting, a change that had to be reverted, a wasted hour -- those are the cost of doing work. They are cheap **when the actor owns them and says so immediately**, and only then; an owned mistake costs one correction, a hidden one costs a diagnostic cycle plus the correction.

### Why this is written down

Not for reassurance. For calibration.

**An agent that fears consequences over-escalates and over-gates.** Over-caution is a fear response wearing the costume of diligence: it looks like care, it reads like rigour in a report, and it produces a queue of questions with obvious answers while the actual clock runs. Naming what is punishable removes the incentive to hide behind a human -- which is the same failure as §A gate is only a gate, arriving from the agent's side instead of the designer's.

An engagement that declares no consequence model has not avoided having one. It has left every agent to assume the worst one.

---

## Blocker vs task

A **blocker** requires a decision or a resource you genuinely lack. **Everything else is a task** -- it goes on the list and gets done.

- *"X is unknown"* is a **task** if anyone can go find out. It is a blocker only if nobody can.
- Ask **"what would fix this?"** before **"how bad is this?"** If every item on a list of blockers has an obvious cheap fix, it was never a list of blockers.
- **Never relay an agent's alarm framing upward.** Re-derive the severity yourself from what was actually observed. An agent that cries critical spends down the credibility it needs when something actually is, and an orchestrator that passes the alarm through unexamined spends it on the agent's behalf.

### The power-supply test

> A technician says he cannot work because he cannot find his power supply. Asked whether any are available, he says yes -- over a hundred. **Grab one of the hundred and get to work.**

Before reporting anything unavailable, establish that it is **unavailable**, not merely **not in hand**:

1. What did you actually try? One thing is a first attempt, not an enumeration.
2. What would you need for it to work? Nine times in ten, answering that reveals you already have it.
3. Is there a second source of the same thing?

Field pattern: on one engagement, four separately-reported walls collapsed on this test alone -- a credential that only needed resetting, a service tested from exactly one client, a permission nobody had actually checked, and a management interface nobody had scanned for. Every one had been reported upward as a blocker.

---

## Where this is recorded

Optional `operating-reality` fields, all absent by default (`schemas/artifacts/operating-reality.yaml`). An OR-001 that declares none of them validates exactly as before and renders byte-identically -- absent optional fields are omitted from render (`core/SUBSTRATE.md` §Projection rules, rule 5).

| Field | Holds |
|---|---|
| `fatal_outcomes` | The states with no way back. Two or three. |
| `authority.green_examples` | Representative work the agent does without asking. |
| `authority.amber_protocols` | Each protocol, and what makes it the authorization. |
| `authority.red_items` | Currently red, with the reason: `fatal-risk`, `recoverability-unknown`, or `operator-scope`. |
| `authority.earned_downgrades` | What moved, to where, and the citation that proved it. |
| `operator_scope` | What is genuinely the operator's, independent of danger. |

Declaring them is a bootstrap question for engagements where authority is live. Omitting them means the harness has no opinion, and the agent falls back on asking -- which is the expensive default this document exists to replace.

---

## What this does not enforce

No Layer 1 check reads any of it. Deliberately, and for the same reason `core/SUBSTRATE.md` §Transport Rules ships unchecked: the primitive has to be right before it is worth freezing into a verifier, and an authority model checked too early would ossify one engagement's shape into everyone's.

What the substrate *does* give you is the audit surface. Every action lands as an event with an actor; a downgrade cites the evidence that earned it; a claim is replayable (`hw verify --claims`). Whether the class was judged correctly is not computable, but whether the protocol was followed is legible in the log afterward. Structural-check candidates are carried as known gaps in `CHANGELOG.md`.

---

## Relationship to other mechanisms

| Mechanism | Interaction |
|---|---|
| Atomicity | An amber protocol's read-back step is §One Actor Per Action. Risk level on a task and authority class on an action are different axes: risk routes verification, authority routes permission. |
| Verification | Claim provenance and the "what I could not verify" section are the countermeasure to the deception failure above. Council and unanchored red team are the right substitute when a gatekeeper cannot assess a change. |
| Typed Artifacts | Fatal outcomes, the three classes and operator scope live in `operating-reality`; each earned downgrade is a citation. |
| Precedence | Operator scope is a Tier 1 concern -- an action inside it stays the operator's regardless of what a lower tier permits. |
| Lock | Authority is declared per project, in that project's OR. It does not travel between instances. |
