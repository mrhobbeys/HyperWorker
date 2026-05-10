# Schema: marketing-campaign

> Use when: producing a campaign with brand-absolute rules, channel-specific platform limits, and copy that needs to ship as drafts for operator review. The failure mode this schema prevents: agent generates 5 emails and a landing page in one pass, ships all six as the deliverable, and 30% of them carry a Tier 1 voice or compliance violation that only surfaces when an operator finally reads them after the operator has already started routing them. Brand-absolute rules at Tier 1 + draft-only at Tier 2 + per-task Layer 2 verification = no ship without per-piece operator review.

This is the deepest schema shipped — it ports the full marketing-funnel case study from v4.1.1 into the schema-as-bootstrap form. Use it as a structural reference when writing custom schemas.

## What this schema gives you

- A four-tier precedence system named for marketing context (`BRAND-ABSOLUTE / OFFER-SCOPE / PLATFORM-LIMITS / COPY-METHOD`).
- A banned-tokens table covering common marketing-language failure modes (income claims, false scarcity, competitor disparagement, em-dash AI tell).
- Eight default tasks across three phases (Foundation, Nurture, Conversion).
- Capability gates declaring what tools each task kind requires (`copy-generation`, `copy-iteration`, `platform-publish-draft`, etc.).
- Auto-escalation rules: drafts touching Tier 1 footer language are critical-risk by default.
- A four-member council with `operator-reality-calibrator`, `brand-voice-guard`, `scope-guard`, and `anti-pattern-watcher`.

## Bootstrap

```
hw bootstrap --schema marketing-campaign --name <campaign-id>
```

The harness asks the bootstrap questions in `schema.yaml`, writes `OR-001` from your answers, and clones the eight default task templates into `projects/<id>/tasks/`. Verification Checkpoint runs immediately with `operator-reality-calibrator` and `scope-guard`.

## Customization

You will likely customize:

- **The eight default tasks.** Edit task instructions, acceptance criteria, and the consumes list to match your campaign's actual structure. Removing tasks is fine; adding tasks beyond eight is also fine.
- **Banned tokens.** Add brand-specific banned phrases. Remove tokens that don't apply.
- **Council members.** If you have a brand-style or voice guide finding (`F-XXX`), the `brand-voice-guard` will use it as the basis for verification.

## Save your version

After your first campaign, run:

```
hw schema save --from projects/<campaign-id> --as marketing-campaign-<your-name>
```

This extracts the configurable substrate (tier names with edits, banned-token additions, council additions, task templates) and writes a derivative schema. Reuse it for the next campaign.
