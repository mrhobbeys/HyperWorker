# 00-REFERENCE-rules.md — {{ project_name }}

Cross-cutting rules with explicit precedence. Lower tier ordinal wins on conflict. Renaming a tier does not change ordinal precedence.

---

## Tier 1: SOURCE-FIDELITY (NON-NEGOTIABLE)

Every claim in the synthesis output cites at least one [SRC-NNN#hash] or [CLM-NNN#hash]. Synthesis cannot contradict a source without explicitly noting and resolving via Decision. Synthesis cannot make claims that no source supports.

@@SCAN_1_1: Does every claim in your last output cite at least one source by hash?

@@SCAN_1_2: Did you contradict any source without resolving via a Decision artifact?

---

## Tier 2: OPERATOR-ALIGNMENT (SCOPE)

Synthesis serves the declared OR-001 purpose. Out-of-scope content is excluded even if sources cover it. Operator weighting rules are applied at extraction.

@@SCAN_2_1: Is anything you wrote in the last step out of scope per OR-001?

@@SCAN_2_2: Did you apply OR-001.weighting_rule when handling multi-round sources?

---

## Tier 3: SYNTHESIS-QUALITY (TECHNICAL)

Output structure declared upfront and held. No internal contradictions. Every input source has been processed (incorporated, contradicted-and-resolved, or discarded with reason). Anti-patterns from earlier rounds are referenced where relevant.

@@SCAN_3_1: Has every source you processed been classified as incorporated, contradicted-and-resolved, or discarded?

@@SCAN_3_2: Are there contradictions between sections of your synthesis output you have not surfaced?

---

## Tier 4: STYLE

Voice consistency, formatting, citation format ([SRC-NNN#hash] for sources, [CLM-NNN#hash] for claims, [DEC-NNN#hash] for synthesis decisions, [F-NNN#hash] for findings). Match operator's brand voice if declared in OR-001.

---

## Banned tokens (project-specific, optional)

If the synthesis output is for an audience with voice constraints, list banned tokens here. Most synthesis projects leave this empty.

| Banned Token | Replacement | Reason |
|---|---|---|
| | | |

---

## Canonical facts — do not normalize (project-specific, optional)

If the operator has facts that must appear verbatim in the synthesis (e.g., dates, regulatory framework names, specific URLs), list them here.

| Fact | Form | Reason |
|---|---|---|
| | | |
