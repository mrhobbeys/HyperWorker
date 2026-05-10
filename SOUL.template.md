---
type: operator_soul_anchor
operator: <<OPERATOR_HANDLE>>
created: <<YYYY-MM-DD>>
version: 1.0.0
---

# Soul

> **Operator-identity anchor.** This file is the operator's own. The harness reads it at bootstrap and fires `operator_soul_anchor` (see `core/SUBSTRATE.md` §Operator Soul Anchor). The `soul_consistency_watcher` council member (see `core/VERIFICATION.md` §Council Role Library) checks substrate decisions against the values declared here.
>
> Fill each section below in your own voice. Replace `<<OPERATOR_HANDLE>>` and `<<YYYY-MM-DD>>` in the frontmatter. Length discipline: aim for ≤1000 words total. Tight beats long. The watcher reads this file with every council fire; verbose prose loses the load-bearing rules in the noise.
>
> See `SOUL.example.md` for one filled-in soul.md from a real operator. Headers below are the recommended structure; the example shows how a real operator adapted them. Adapt the headers to your own framing if the recommended ones do not fit how you actually think — the watcher reads section content, not section names.

## Quality Bar

[100-200 words. What does "done" feel like to this operator? What is the standard the work has to clear before it ships? Use specific identity-language, not procedure. Example shape: "Not 'good enough' but 'holy shit, that's done.' Tested. Documented. Complete." The operator fills in their own.]

## Excuses That Don't Apply

[100-150 words. Anti-excuse list. What is never an acceptable reason to ship incomplete? Time, fatigue, complexity, scope creep, etc. Operator's call. Each excuse named is a structural pattern the agent will not be allowed to surface; if the operator's posture is "complexity is not an excuse, it is the work," then the agent treats every "this is too complicated" surface as a failure mode rather than a stop.]

## Anti-Patterns This Operator Refuses

[100-150 words. What workarounds, half-measures, "table this for later" patterns, or polite shortcuts are forbidden? Wrapped as identity, not as rules. The watcher checks every `task.complete` proposal against this list; if a proposal contains "would normally," "for now," "leaving X for a later pass," and the operator has named those patterns as refused, the watcher fires.]

## Voice and Posture

[100-150 words. How does the agent communicate with this operator? What tone? What level of directness? What is the energy? This is the brand_voice_anchor's identity-side counterpart — `brand_voice_anchor` governs output to end users; soul.md governs the agent's communication TO the operator. They are independent and frequently differ.]

## When in Doubt

[50-100 words. Default behavior when uncertain. What is the operator's preferred fallback? "Run the cheapest empirical check first" / "ask the operator with two concrete options and a recommended path" / "ship what you have and surface the uncertainty as a finding." Operator's call.]

---

*Operator fills in each section. The harness reads this file at bootstrap and fires `operator_soul_anchor`. The `soul_consistency_watcher` council member checks substrate decisions against these values. Length discipline: ≤1000 words total. Tight beats long. The watcher's effectiveness drops when the soul.md is verbose enough to dilute the load-bearing rules.*
