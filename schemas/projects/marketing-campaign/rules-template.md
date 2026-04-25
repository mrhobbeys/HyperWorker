# 00-REFERENCE-rules.md — <Project Name>

> Marketing-campaign rules. The compressed projection (`00-REFERENCE-rules.compressed.md`) is what enters agent prompts.

## Precedence Order

When rules conflict, higher tiers override lower tiers. Tier 1 cannot be overridden. Same-tier conflicts are an authoring error.

### Tier 1: BRAND-ABSOLUTE  (absolute — never override)

- No income guarantees or implied earnings claims.
- No fabricated testimonials or case studies. All social proof must be from real clients with permission.
- No claims that cannot be independently verified.
- Include CAN-SPAM-compliant unsubscribe link in every email.
- Physical mailing address must appear in email footer.
- No disparaging competitors by name.

@@SCAN_1_1: List the Tier 1 banned phrase categories that apply to this task's output.
@@SCAN_1_2: Confirm the unsubscribe link and physical mailing address requirements apply to this output (yes / no / not-applicable).

### Tier 2: OFFER-SCOPE  (overrides technical and style)

- This funnel sells <declared offer> only — do not mention or sell products, courses, or retainers outside scope.
- Pricing is discussed only on calls — no pricing on landing page or in emails.
- Draft-only: all content saved as drafts. Never publish without operator review.
- Target audience: <segment description>. Anchored to `[OR-001#<hash>]`.

@@SCAN_2_1: Restate, in one sentence, the single offer this campaign sells.

### Tier 3: PLATFORM-LIMITS  (overrides style)

- Landing page headline ≤ 12 words.
- Landing page subhead ≤ 25 words.
- Email subject line ≤ 50 characters.
- Email body 150–300 words.
- Landing page mobile PageSpeed score ≥ 90.
- Form fields: name and email only.

@@SCAN_3_1: State the body word-count window for this content kind.

### Tier 4: COPY-METHOD  (lowest precedence)

- Lead with the reader's problem, not the solution.
- Use second person ("you") throughout. Never third person.
- One CTA per page or email. Never split attention.
- Social proof before CTA. Establish credibility, then ask.
- Reading level Flesch-Kincaid ≤ 8.
- Short paragraphs (1–3 sentences max).
- Proof over promise — show results, do not claim them.

@@SCAN_4_1: Name the methodology rule that governs CTAs for this content kind.

## Banned Tokens / Replacements

| Banned Token | Safe Replacement | Tier | Why |
|---|---|---|---|
| guaranteed results | proven approach | 1 | Income claim. |
| you'll make $X | clients have seen [specific metric] | 1 | Earnings claim. |
| risk-free | no-pressure conversation | 1 | Implied guarantee. |
| best in the industry | trusted by [number] businesses | 1 | Unverifiable superlative. |
| act now or miss out | spots are limited this month | 2 | False scarcity. |
| our competitors can't | (remove entirely) | 1 | Competitor disparagement. |
| — (em dash) | , or . or ( ) | 4 | AI tell — breaks voice. |

## Canonical Facts — Do Not Normalize

| Fact | Canonical Form | Do NOT Normalize To |
|---|---|---|
| Vanity phone (if used) | "1-800-FLOWERS" | "1-800-356-9377" |
| Date-anchored deadline | "by end of Q1 2026" | "in about 3 months" |

## Target Audience

<paragraph: who, role, pain points, decision authority, anchored to OR-001 fields>

## Safe Claims (operator pre-approved)

- "We've helped <N> businesses build consistent lead pipelines" (only if N is current and verifiable).
- "Free, no-pressure discovery call."
- "No long-term contracts."

## Correct Links / URLs

| Purpose | URL |
|---|---|
| Landing page | <https://...> |
| Booking page | <https://...> |
| Unsubscribe | {{unsubscribe_link}} (platform variable) |

## Platform Specifications

| Platform / Use | Constraint | Format | Notes |
|---|---|---|---|
| Landing page | Max 12-word headline, mobile-first | HTML/responsive | PageSpeed ≥ 90 |
| Email | 50-char subject, 150–300 word body | HTML template | Test in Gmail, Outlook, Apple Mail |
| Booking page | Calendar embed required | HTML/responsive | Must show available slots |
