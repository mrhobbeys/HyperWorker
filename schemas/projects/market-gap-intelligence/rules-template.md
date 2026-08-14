# 00-REFERENCE-rules.md — {{ project_name }}

Cross-cutting rules with explicit precedence. Lower tier ordinal wins on conflict.

---

## Tier 1: EVIDENCE-INTEGRITY (NON-NEGOTIABLE)
Every recommendation rests on MEASURED/OBSERVED evidence cited by hash, or on
ESTIMATED values whose inputs are MEASURED/OBSERVED. An ASSUMED-only
recommendation is a hypothesis-to-test, labeled as such — never shipped as a
conclusion. Every evidence-bearing artifact carries a provenance tag. Fluency is
not evidence.

**Verbatim principle.** Quote buyer questions, review complaints, and operator
directives verbatim in the artifact (`question`, `prior_direction`, Decision
bodies). Paraphrase only when too long, with `[paraphrase: ...]` markers that
preserve qualifiers (numbers, geos, conditions).

@@SCAN_1_1: Does every recommendation in your last output cite MEASURED/OBSERVED by hash (or ESTIMATED on measured inputs)?
@@SCAN_1_2: Is any shipped recommendation supported only by ASSUMED inputs? Relabel it a hypothesis.

---

## Tier 2: CLIENT-ALIGNMENT (SCOPE)
The intelligence serves THIS client's OR — geography, buyer, services, brand
constraints. No cross-client bleed. Out-of-scope opportunities are noted, not
recommended.

@@SCAN_2_1: Is anything in the last step out of the OR geo/buyer/scope, or borrowed from another client?
@@SCAN_2_2: Did a brand/regulatory constraint apply to anything you suggested, and did you honor it?

---

## Tier 3: INTELLIGENCE-QUALITY (TECHNICAL)
Competitors discovered from live SERPs, not assumed. Channel traps flagged, never
sold as beatable. Gaps require demand AND a weak answer. ≥1 disconfirming finding.

@@SCAN_3_1: Was every competitor discovered from a live SERP and tagged with comp_type?
@@SCAN_3_2: Did you flag SERP channel traps instead of listing them as beatable rivals?
@@SCAN_3_3: Do you have at least one disconfirming finding? If not, you under-searched.

---

## Tier 4: STYLE
Citation format: [F-NNN#hash] findings; [CMP/FP/GAP/TGT-NNN#hash] domain artifacts;
[DEC-NNN#hash] decisions. Lead the deliverable with the decision + evidence, not
methodology. Match the operator/brand voice if declared.

---

## Anti-hallucination checklist (T-008 must pass before the deliverable ships)
- [ ] Every decision-driving claim carries a provenance tag; none are ASSUMED-only.
- [ ] Competitors were discovered from SERPs, not assumed (every CMP has found_on).
- [ ] ≥1 finding contradicts or complicates the original hypothesis.
- [ ] Numbers come from a tool with a date, or a labeled formula on tool inputs.
- [ ] Tool-gap sections are marked hypotheses-to-verify, not presented as facts.
- [ ] Channel reality checked (SERP ownership, local-ads-program eligibility e.g. LSA where applicable, software-vs-service intent).
- [ ] A skeptic could trace every recommendation back to evidence.

---

## Banned tokens / canonical facts (project-specific)
Populate for regulated audiences (health/legal/finance claim limits) or leave an
explicit empty row. {{ brand_constraints }}

---

## Ranking-factor discipline (Tier 1 addendum)
The only trusted source for what is or isn't a Google ranking factor is Google's
own documentation (Search Central / Search Essentials). Everything else is a
third-party heuristic, labeled as such.
- **E-E-A-T is NOT a ranking factor** - it is what Google's raters assess, not a
  measured ranking input. Never recommend an action "to improve E-E-A-T for
  rankings"; recommend the concrete underlying fix and cite Google docs.
- **Domain authority / domain strength** (e.g. Moz/Ahrefs-style domain-authority
  constructs, or whatever equivalent metric the available tooling provides) are
  [ESTIMATED] winnability heuristics only - never written as [MEASURED] Google
  ranking factors.
- Any recommendation resting on a ranking-factor claim cites Google documentation
  by URL, or is labeled a hypothesis.
- **Structured data is not a free win.** Google has deprecated several rich-result
  types recently. Never recommend a schema.org type for rich results without
  confirming it is currently supported in Google's Search Central docs at run time;
  label deprecated/unsupported types as such and state whether the benefit claimed
  is a rich result or only machine understanding.
