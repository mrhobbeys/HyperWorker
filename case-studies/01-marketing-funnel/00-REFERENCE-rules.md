# 00-REFERENCE-rules.md — Spring Lead-Gen Funnel

> This is the single source of truth for all cross-cutting rules in this project.

## Precedence Order

When rules conflict, higher tiers override lower tiers.
Workers must check Tier 1 first. If a lower-tier rule produces output that violates Tier 1, Tier 1 wins.

### Tier 1: BRAND-ABSOLUTE (absolute — never override)
- No income guarantees or implied earnings claims ("You'll make $X" / "guaranteed results")
- No fabricated testimonials or case studies — all social proof must be from real clients with permission
- No claims that cannot be independently verified
- Include CAN-SPAM compliant unsubscribe link in every email
- Physical mailing address must appear in email footer
- No disparaging competitors by name

### Tier 2: OFFER-SCOPE (overrides platform limits and copy method)
- This funnel sells discovery calls only — do not mention or sell products, courses, or retainers
- Do not promise a specific number of leads, clients, or revenue outcomes
- Draft-only: all content must be saved as drafts — never published without human review
- Pricing is discussed on calls only — no pricing on landing page or in emails
- Target audience: small business owners age 30-55 with inconsistent lead flow

### Tier 3: PLATFORM-LIMITS (overrides copy method)
- Landing page headline: max 12 words
- Landing page subhead: max 25 words
- Email subject lines: max 50 characters (mobile preview cutoff)
- Email body: 150-300 words per email (optimized for mobile reading)
- Landing page must score 90+ on mobile PageSpeed
- Form fields: name and email only (minimize friction)

### Tier 4: COPY-METHOD (lowest precedence)
- Lead with the reader's problem, not the solution
- Use second person ("you") throughout — never third person
- One CTA per page/email — do not split attention
- Social proof before CTA — establish credibility, then ask
- Reading level: 6th-8th grade (Flesch-Kincaid)
- Short paragraphs (1-3 sentences max)
- Proof over promise: show results, don't claim them

## Banned Phrases / Safe Replacements

| Banned Phrase | Safe Replacement | Tier | Why |
|---|---|---|---|
| "guaranteed results" | "proven approach" | 1 | Income claim |
| "you'll make $X" | "clients have seen [specific metric]" | 1 | Earnings claim |
| "risk-free" | "no-pressure conversation" | 1 | Implied guarantee |
| "best in the industry" | "trusted by [number] businesses" | 1 | Unverifiable superlative |
| "act now or miss out" | "spots are limited this month" | 2 | False scarcity |
| "our competitors can't" | (remove entirely) | 1 | Competitor disparagement |

## Target Audience
Small business owners (30-55) who run service-based businesses with 2-20 employees. Primary pain: lead flow is inconsistent — some months are great, others are dry. They've tried random marketing tactics but nothing sticks. Decision-making authority: they are the decision-maker.

## Safe Claims
- "We've helped [X] businesses build consistent lead pipelines" (if X is accurate)
- "Our clients typically see results within 90 days" (if supported by data)
- "Free, no-pressure discovery call"
- "No long-term contracts"

## Correct Links / URLs

| Purpose | URL |
|---|---|
| Landing page | [https://yourdomain.com/free-call] |
| Booking page | [https://yourdomain.com/book] |
| Unsubscribe | [{{unsubscribe_link}} — platform variable] |

## Platform Specifications

| Platform / Use | Constraint | Format | Notes |
|---|---|---|---|
| Landing page | Max 12-word headline | HTML/responsive | Mobile-first design |
| Email | 50-char subject, 150-300 word body | HTML template | Test in Gmail, Outlook, Apple Mail |
| Booking page | Calendar embed required | HTML/responsive | Must show available time slots |
