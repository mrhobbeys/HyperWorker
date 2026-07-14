# 00-REFERENCE-rules.md — {{ course_name }}

> File-canonical (Mutable Surface). Operator edits this directly. The compressed projection (`00-REFERENCE-rules.compressed.md`) is what enters agent prompts.

## Precedence Order

When rules conflict, lower tier ordinal wins. Tier 1 cannot be overridden. Same-tier conflicts are an authoring error and block tasks.

---

## Tier 1: LENS-FIDELITY (NON-NEGOTIABLE)

The lens (OR-001.lens_anchor) shapes voice and framing. **Verbatim quotation principle**: when an artifact summarizes operator intent or source content, quote verbatim where possible. Paraphrase only when the original is too long (typically: more than 3 sentences); flag explicitly with `[paraphrase: ...]` markers and preserve qualifiers (numbers, dates, conditional clauses). Loose paraphrase of the lens or operator workflow rules is a Tier 1 violation.

The lens guides — module premises are discovered from corpus and operator's actual learning, not pre-determined by the lens itself.

@@SCAN_1_1: Is every operator-stated lens framing or workflow rule in this output a verbatim quote, or marked with [paraphrase: ...]?

@@SCAN_1_2: Did this output infer a module premise from the lens, rather than from operator-stated learning or corpus evidence?

---

## Tier 2: SCOPE-INTEGRITY (overrides decision-discipline and style)

L1 owns the master plan only. L1 does **not** produce lesson content (L2/L3) or actuate platform entities beyond Phase A.2 read-only familiarization (L2 actuation tasks own actuation).

The slug-premise-pause invariant is non-negotiable: every child-project spawn STOPS after `child_project.scaffolded` and waits for operator `continue` (or `continue without resources`) before T-001 fires. Skipping the pause because operator intent seems clear is a Tier 2 violation.

Promo work routes to L2 promo-* projects (or external surface if `OR-001.promotion_scope: external`). L1 does not draft promo copy.

@@SCAN_2_1: If this turn spawned a child project, did the agent STOP after child_project.scaffolded and wait for operator continue?

@@SCAN_2_2: Did this output produce lesson content or actuate platform entities? L1 should answer "no" for both unless this is the Phase A.2 read-only familiarization.

---

## Tier 3: DECISION-DISCIPLINE (overrides style)

Curriculum and tier-policy decisions are typed Decision artifacts (DEC-001 sequence, DEC-002 tier policy), not loose conversation. Reordering and tier moves are supersedes with explicit reason and movement_history append. Operator mid-flow directives are typed Decisions per HARNESS.md §Operator mid-flow directives.

@@SCAN_3_1: If a curriculum reorder or tier move was discussed, was it captured as a DEC-001 / DEC-002 supersede with reason, or left in conversation?

@@SCAN_3_2: If an operator mid-flow directive surfaced, was it captured as a typed Decision artifact with synthesis_role?

---

## Tier 4: STYLE

Voice consistency across cross-project artifacts. Match `OR-001.lens_anchor[0]` voice in master plan prose. Citations: `[KIND-NNN#12-hex]` per SUBSTRATE.md §Citation Format.

@@SCAN_4_1: Does the master plan prose voice in this output reflect lens_anchor[0]?

---

## Banned Tokens / Replacements (project-specific, optional)

| Banned Token | Replacement | Tier | Why |
|---|---|---|---|
| | | | |

---

## Canonical Facts — Do Not Normalize (project-specific, optional)

| Fact | Canonical Form | Do NOT Normalize To |
|---|---|---|
| | | |

---

## Operator Workflow Rules (verbatim — Tier 2 SCOPE)

> Reproduced verbatim from the bootstrap prompt's "Operator workflow rules" section. Paraphrasing is a Tier 1 violation.

### LENS — guides, doesn't dominate

Skool variant (primary):
> I tried the thing, learned this, now I'm teaching you what I learned so you can avoid mistakes and apply the lesson.

Cross-channel variant (secondary, kept for cross-promotional coherence):
> The multi-business stopping point. I'm running several things at once. Here's what I poked at this week, here's what one business taught me that another couldn't, here's where I stopped and why.

The lens shapes voice and framing in spawned content. Premise of each module is discovered through the work, not pre-determined.

### SLUG-PREMISE-PAUSE PROTOCOL

For every L2 spawn (module / course-task / promo) and every L3 content-piece spawn:
1. Operator gives slug + premise.
2. Agent scaffolds the project skeleton + an empty `resources/` folder.
3. Agent STOPS, surfaces "scaffold ready, drop materials, reply continue".
4. Operator drops materials (or skips).
5. Operator replies continue.
6. Agent inventories `resources/`, emits `child_project.resources_ready`, hands off.

Agent CANNOT advance past step 3 without explicit operator continue.

### ORDER DISCOVERY

Curriculum sequence is supersedable. Reorders happen because we learn from real student signal — module belongs in free tier, this module needs to come first, etc. When a reorder is initiated, capture as DEC-001 supersede with the reason, and let the ratchet flag affected in-flight L2 projects. Don't lock sequences too early; don't be surprised when they change.

### PROMOTION SCOPE

Promo lives in-harness as L2 promo-* projects by default. If promotion needs its own surface (different cadence, different team, different audience), flip OR-001.promotion_scope to external — that's a supersede, not a catastrophe — and route promo work to its own project from that point on.

### THE LENS IS NOT THE PREMISE

The premise of any specific module is what the operator learned and is teaching. The lens is the shape of HOW it's taught. If the lens drives the content premise rather than the operator's actual learning, push back.

@@SCAN_2_3: For any L2 spawn proposed in this output, did the operator state a premise (not just a slug)?
