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
  - "For each top target, the channel where the buyer actually decides is confirmed (organic, map pack/GBP, directories, LSAs, referral, paid) — not assumed."
  - "LSA (Local Services Ads) eligibility is checked for the client's category, not guessed."
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
   directory-listed, ad/LSA, or does the buyer decide off-search (referral)?
2. Check LSA / Google Guaranteed eligibility for the client's category at
   ads.google.com/local-services-ads (e.g., home services & healthcare often
   eligible; IT/computer-repair typically NOT). Do not guess eligibility.
3. Compare the winning channel to what the client can execute. Flag mismatches.
4. Write a channel-call Decision with the recommended mix per target. Best-channel
   ordering for local service businesses (verify rates each run): referrals/reviews
   → local SEO + GBP → LSAs (if eligible) → Search ads → Meta → LinkedIn (B2B) →
   YouTube (branding).
5. Append to evidence log. Answer @@SCAN markers.

## Completion Report
- Acceptance criteria: <X/Y>
- Outputs: DEC-NNN (channel-call), updated TGT notes
- Channel mismatches flagged: <list>
- LSA eligibility: <eligible categories / not>
