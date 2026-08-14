---
id: T-007
kind: task
schema: market-gap-intelligence
phase: D
risk_level: elevated
required_tools: [file_read, file_write, browser]
delivery_mode: constrained
depends_on: [T-006]
consumes:
  - "[OR-001#<short-hash>]"
  - "[TGT-NNN#<short-hash>]"
  - "[CMP-NNN#<short-hash>]"
acceptance_criteria:
  - "For each top target, the channel where the buyer actually decides is confirmed (organic, map pack/GBP, directories, local-ads programs, referral, paid) — not assumed."
  - "If a local-ads program applies to the client's category and geo (e.g. Google Local Services Ads / LSA), eligibility is checked, not guessed; otherwise it's marked not-applicable and the real paid-channel options are named instead."
  - "Any target where the winning channel is NOT the one the client can execute is flagged with the correct channel."
  - "A channel-call Decision (intel_role: channel-call) records the recommended channel mix."
---

# Task T-007: Channel Reality Audit

## Objective
Confirm WHERE each target is won before recommending HOW. Demand without the right
channel is a dead end. Catches the classic error of recommending content for a
term that is actually won in the map pack, a directory, or by referral.

## Step-by-Step
1. For each top TGT, re-read its SERP: is the win organic, map-pack/GBP,
   directory-listed, ad/local-ads-program, or does the buyer decide off-search (referral)?
2. If the client's category is local-intent, check eligibility for the relevant
   local-ads program (e.g. Google Local Services Ads / LSA / Google Guaranteed at
   ads.google.com/local-services-ads — home services & healthcare are often eligible
   categories; IT/computer-repair typically is not). Do not guess eligibility. For
   non-local, B2B, or national clients where no such program applies, mark it
   not-applicable and evaluate the client's actual paid-channel options instead
   (e.g. Search ads, LinkedIn Ads, marketplace ads).
3. Compare the winning channel to what the client can execute. Flag mismatches.
4. Write a channel-call Decision with the recommended mix per target. Example
   channel ordering for a local service business (verify rates each run, and adapt
   to the client's actual category/geography — a national B2B client's ordering
   looks different, e.g. organic content → paid search → LinkedIn/webinars →
   partnerships): referrals/reviews → local SEO + GBP → local-ads program (if
   eligible) → Search ads → Meta → LinkedIn (B2B) → YouTube (branding).
5. Append to evidence log. Answer @@SCAN markers.

## Completion Report
- Acceptance criteria: <X/Y>
- Outputs: DEC-NNN (channel-call), updated TGT notes
- Channel mismatches flagged: <list>
- Local-ads program eligibility (e.g. LSA), if applicable: <eligible categories / not / not-applicable>
