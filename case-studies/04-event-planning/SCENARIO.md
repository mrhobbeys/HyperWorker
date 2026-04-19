# Scenario Brief: Event Planning

> **Primary mechanism showcase:** Atomicity — rigid task decomposition with hard deadlines, where each task must be completable in one session because event logistics don't wait.

## The Project

Plan and execute a 100-person industry networking event. Venue, catering, speakers, promotion, registration, day-of logistics, and follow-up. Estimated 10-14 tasks across 4 phases with a fixed event date creating a hard deadline.

## How the Six Mechanisms Apply

### Lock
The networking event is the active project. When someone suggests "we should also do a podcast" — that goes to the backlog. The event has a fixed date; distractions directly threaten the deadline.

### Atomicity (Primary Showcase)
Event planning is the strongest argument for atomic task decomposition. Every task has a real-world deadline and a physical dependency. You can't "kind of" book a venue — it's booked or it isn't. You can't "partially" confirm catering — the headcount is locked or it isn't.

Well-decomposed event tasks:

```
Phase 1: Foundation (8+ weeks out)
  01: Define event concept, audience, and success metrics
  02: Research and book venue (depends on: 01)
  03: Set budget and allocate by category (depends on: 02 — venue cost known)

Phase 2: Content & Logistics (4-8 weeks out) [checkpoint]
  04: Recruit and confirm speakers (depends on: 01, 02)
  05: Select and confirm catering (depends on: 02, 03)
  06: Design registration page and open registration (depends on: 01, 02)
  07: Plan promotion campaign — email + social (depends on: 06)

Phase 3: Pre-Event (1-4 weeks out) [checkpoint]
  08: Finalize headcount and confirm with vendors (depends on: 05, 06)
  09: Create day-of run sheet and assign roles (depends on: 04, 08)
  10: Prepare speaker materials and AV requirements (depends on: 04)
  11: Send attendee confirmation emails with logistics (depends on: 08)

Phase 4: Post-Event (1 week after)
  12: Send follow-up emails and feedback survey (depends on: event complete)
  13: Compile post-mortem and capture discoveries (depends on: 12)
```

**Why atomicity matters here:** Each task has a clear "done" state that's verifiable in the real world. Task 02 is done when the venue contract is signed. Task 05 is done when the catering order is confirmed with a headcount. Task 09 is done when every 15-minute block of the event day has an assigned owner. There's no ambiguity — which means the executor can execute the task, check the list, and stop.

**The anti-pattern this prevents:** "Work on event stuff" → the AI drafts a venue comparison, starts a speaker list, half-writes a promo email, and suggests a menu. None of it is finished. With atomicity, each task gets done completely before the next one starts.

### Dependency
The dependency chain is shaped by real-world constraints. You can't send attendee confirmations (Task 11) until headcount is finalized (Task 08). You can't finalize headcount until catering is confirmed (Task 05) and registration is running (Task 06).

**Cascade example:** If the venue changes (Task 02 gets re-done), it cascades to: catering (venue kitchen availability may change), registration page (address and directions change), speaker materials (AV setup may differ), run sheet (room layout changes). The TASK-STATE engine flags all of these.

### Memory Pipeline
Discoveries from event planning are highly reusable:

- **DISC-001:** "Venue required a certificate of insurance 30 days before the event — we almost missed the deadline." → Scope: `Universal`. Promotes to: "Add insurance certificate to venue booking task checklist, with a 30-day reminder."
- **DISC-002:** "Catering minimum was 80% of room capacity, not 80% of registered attendees. Budgeted wrong." → Scope: `Universal`. Promotes to: "Confirm catering minimum calculation basis during vendor selection."
- **DISC-003:** "The AV system at this specific venue doesn't support HDMI — only USB-C." → Scope: `Venue:[Name]`. Stays venue-specific.

### Precedence
Example tiers for event planning:

| Tier | Name | Example Rules |
|---|---|---|
| 1 | SAFETY-LEGAL | Fire code occupancy limits. Insurance requirements. Alcohol service regulations. Accessibility compliance. |
| 2 | BUDGET | Total spend cannot exceed approved budget. No new vendor commitments without budget line item. |
| 3 | VENUE-CONSTRAINTS | Room capacity. AV capabilities. Catering kitchen limitations. Load-in/load-out windows. |
| 4 | EXPERIENCE | Networking time > presentation time. Name badges, not table tents. Music during registration. |

**Conflict example:** Tier 4 says "networking time should exceed presentation time." But two speakers need 45-minute slots each and the venue (Tier 3) only allows 3 hours total. Budget (Tier 2) doesn't allow extending the venue booking. The precedence resolves it: reduce networking time, not speaker time, because venue constraints override experience preferences.

## Config Highlights

```yaml
precedence_tiers:
  1: "SAFETY-LEGAL"
  2: "BUDGET"
  3: "VENUE-CONSTRAINTS"
  4: "EXPERIENCE"

scope_taxonomy:
  - "Universal"
  - "Venue:[Name]"
  - "Vendor:[Name]"
  - "Event:[Name]"

checkpoints:
  gate_type: "human"
  default_checkpoint_frequency: "per-phase"  # Critical — each phase has real-world commitments

executor:
  draft_only: true       # All vendor communications reviewed before sending
  content_mode: "generate"
```

## What This Case Study Demonstrates

1. **Atomic tasks with real-world verifiability** — each task has a physical "done" state
2. **Hard deadline pressure** making the Lock mechanism non-negotiable
3. **Dependency cascades** from a single change (venue swap) rippling through the entire project
4. **Discoveries that compound** across future events
5. **Precedence resolving conflicts** between experience goals and physical constraints

## Reference
For full file examples, see the [Marketing Funnel Launch](../01-marketing-funnel/) case study.
