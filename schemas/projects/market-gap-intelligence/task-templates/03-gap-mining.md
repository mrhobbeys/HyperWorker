---
id: T-003
kind: task
schema: market-gap-intelligence
phase: B
risk_level: elevated
required_tools: [file_read, file_write, browser]
delivery_mode: constrained
depends_on: [T-001]
consumes:
  - "[OR-001#<short-hash>]"
  - "[FP-NNN#<short-hash>]"   # competitor gaps from T-002 (optional but ideal)
acceptance_criteria:
  - "Candidate questions harvested from ≥3 distinct sources (PAA, autocomplete, Planner, Trends-rising, Reddit/Quora/forums, review-mining, sales-inbox), each tagged with its source."
  - "Every surviving gap was SERP-tested for answer weakness — it carries BOTH a demand_signal AND a current_answer weakness note."
  - "Channel traps owning a gap's SERP are flagged, not listed as easy wins."
  - "Voice-of-customer phrasing is preserved verbatim in the question field."
  - "Gaps classified: money / trust / education / voice-of-customer."
---

# Task T-003: Gap Mining (Q3 — what are people asking that nobody answers well?)

## Objective
Find demand with a weak or missing answer. A gap needs BOTH evidence of demand AND
evidence the current answer is weak/missing/off-intent. Drop anything missing either.

## Step-by-Step
1. Read OR-001 + competitor gaps (FP artifacts). Competitor blind spots are the
   first place to look.
2. Harvest candidates, tagging source: PAA trees, autocomplete (term + a–z +
   how/why/can/best/vs), Planner question/long-tail terms with real volume+CPC,
   Trends rising/breakout, Reddit/Quora/Facebook groups/forums, 1–3★ review
   complaints, and the client's own inbox/sales calls if available.
3. For each promising candidate, run the live SERP and judge answer quality: who
   answers (forum-only/aggregator = beatable; strong business page = not a gap;
   software/publisher = trap), AI Overview thin/absent?, intent match?
4. Keep only candidates with demand AND weak answer. Record why each survived.
5. Classify gap_type. Write GAP artifacts; preserve buyer phrasing verbatim.
6. Append to evidence log. Answer @@SCAN markers.

## Completion Report
- Acceptance criteria: <X/Y>
- Citations consumed: [OR-001#…], [FP-NNN#…]
- Outputs: GAP-001…NNN
- Top money gaps: <list → feed T-006>
- Sources used: <list>
- Disconfirming note: <any gap evidence that complicates the operator's hypothesis → tag a finding intel_role: disconfirming>
