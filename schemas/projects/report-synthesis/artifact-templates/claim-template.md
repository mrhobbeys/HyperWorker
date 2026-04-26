---
id: CLM-XXX
kind: claim
created_at: <ISO 8601>
hash: sha256:<filled-by-harness>
from_source: "[SRC-NNN#hash]"
text: "<the claim, in the agent's words but tightly faithful to the source>"
claim_type: <observation | statistic | recommendation | definition | hypothesis | methodology-note | finding-of-fact>
source_confidence: <stated-by-source | inferred-from-source | contested-in-source>
page_or_section: null          # or string locator within the source
tags: []
---

# Claim CLM-XXX

## Claim

<The claim, expanded to one paragraph if needed for clarity. The frontmatter `text` field is the citation-ready short form; the body can elaborate.>

## Source context

<2-3 sentences quoting (or tightly paraphrasing with explicit `[paraphrase: ...]` markers per Tier 1 verbatim quotation principle) the source passage this claim was extracted from. The source is at file_path; this section preserves the local context for future synthesis tasks.>

## Granularity note (optional)

<If this claim was the result of splitting a compound source statement, note the sibling claim IDs. If it was kept as one despite internal qualifiers, note the qualifiers preserved. Helps future audits validate the granularity choice. See T-002 §Granularity guidance.>
