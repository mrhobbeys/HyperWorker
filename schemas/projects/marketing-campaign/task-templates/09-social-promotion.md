---
id: T-009
kind: task
schema: marketing-campaign
phase: 3
risk_level: standard
required_tools: [file_write]
delivery_mode: constrained
depends_on: [T-001, T-002, T-008]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-001#<short-hash>]"            # offer statement
  - "[DEC-002#<short-hash>]"            # tone-of-voice decision
acceptance_criteria:
  - "LinkedIn post: ≤ 1,300 characters, single explicit CTA, no income guarantees, no fabricated case studies."
  - "Image-carousel script: 5-7 slides, each slide ≤ 25 words copy + a one-line image-direction note."
  - "Short-form video script: ≤ 60-second read time at moderate pace; opens with the audience's pain in the first 3 seconds."
  - "Each output respects the offer phrasing in DEC-001 and the tone-of-voice in DEC-002."
  - "Zero Tier 1 banned tokens across all three outputs."
  - "Saved as DRAFT (operator publishes manually)."
---

# Task T-009: Social Promotion Variants

## Objective

Produce three channel-specific promotion variants for the campaign: a LinkedIn post, an image-carousel script (slide-by-slide copy + image direction), and a short-form video script. Each consumes the same offer (`DEC-001`) and tone-of-voice (`DEC-002`) anchors as the funnel above; each is shaped for its channel without re-deriving the offer.

## Why this exists

The earlier funnel tasks (T-001 through T-008) produce the landing page + email sequence + booking page. Most lead-magnet campaigns need promotion-channel variants on top of the core funnel — LinkedIn organic, paid social carousel, short-form video — that share the offer but adapt the framing per channel. v5.0 left these implicit; v5.1 makes them a first-class default task so the friction-log entry FL-007 ("social promotion was needed but not in the schema") closes structurally rather than via in-flight schema extension.

## Step-by-Step Instructions

1. Recite each consumed artifact in `consumed-inputs.md`. Confirm each paraphrase passes Layer 1 overlap.
2. Answer every `@@SCAN_n_m:` marker.
3. **LinkedIn post.** Open with the audience's pain. State the offer in one sentence. Add 2-4 sentences of context that justify why this offer addresses that pain. Close with a single explicit CTA matching the funnel's primary call-to-action. Word it for the LinkedIn voice (third-person professional, no first-person "I" stories unless the operator's voice doc explicitly authorizes). ≤ 1,300 characters total. No emojis unless the operator's voice doc authorizes (default: none).
4. **Image-carousel script.** Produce 5-7 slides. Slide 1 is the hook (audience pain + offer headline). Slides 2-N break down the value or process. Final slide is the CTA. Each slide carries ≤ 25 words of slide copy and one line of image direction (e.g., "image direction: clean diagram showing workflow stages"). The image direction is a brief; the operator or designer produces the image.
5. **Short-form video script.** ≤ 60 seconds at moderate pace. Open with the audience's pain in the first 3 seconds (the hook bar). Move through one or two value points. Close with a CTA that matches the LinkedIn post's CTA so the campaign is consistent across channels. Include cue notes (`[on-screen text: ...]`, `[B-roll: ...]`) where relevant.
6. Banned-token scan across all three outputs.
7. Save all three to `outputs/social-promotion/` as DRAFT.

## Specific guidance

**Each variant is a different channel-shaped framing of the same offer, not three rewrites of the same content.** A LinkedIn post that is identical in voice and length to the email-1-welcome from T-003 has not done the work; the LinkedIn channel reads differently and the post should reflect it.

**`delivery_mode: ab-variant` is NOT used here.** This task produces three different *channel* variants, one per channel. Each channel gets exactly one output. ab-variant is for cases like "produce three versions of the same LinkedIn post on different CTA framings" — that is a layered task, not this one. If the operator wants A/B variants of the LinkedIn post, the planner declares an additional task with `delivery_mode: ab-variant`, `ab_variant_count: 3`, `ab_variant_axis: "primary CTA framing"` consuming this task's output.

## Completion Report

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [DEC-001#…], [DEC-002#…]
- **SCAN markers answered:** <count>
- **Outputs produced:** outputs/social-promotion/linkedin-post.md, outputs/social-promotion/carousel-script.md, outputs/social-promotion/video-script.md (all DRAFT)
- **Discoveries:** <items — e.g., "Audience-language note: 'practice manager' resonates more on LinkedIn than 'office manager'; flag as F-XXX">
- **Recommended follow-up artifacts:** "none" or "Write F-XXX capturing channel-specific framing observed during drafting"

## Live-edit adaptation (v5.1.1)

This template is `delivery_mode: constrained`. A live-edit fork against existing pinned LinkedIn posts, scheduled carousel content, or platform-published video posts uses the v5.1.1 enumeration:

- **edit_candidates:** existing scheduled or pinned posts whose copy needs updating.
- **create_candidates:** new channel-shaped variants the rebrand mission implies — a vertical-specific LinkedIn post, a new carousel for a market the campaign now targets.
- **delete_candidates:** scheduled or pinned posts that contradict the rebrand and should be unpublished.

Do not pre-prune. `scope-shrink-watcher` reviews completeness in council. See `core/TYPED-ARTIFACTS.md` §Live-Edit Proposal Artifacts.
