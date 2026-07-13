---
id: BR-XXX
kind: behavior-rule
created_at: <ISO 8601>
hash: sha256:<filled-by-harness>
title: "<one line: the business rule this captures>"
rule_statement: "<the rule as an algorithm, in our own words — precise enough to implement without seeing the original>"
worked_examples:               # at least one measured input->output pair
  - input: "<concrete input>"
    output: "<measured output>"
    measured_via: "[OBS-NNN#hash]"   # the experiment that produced this pair, if individually traceable (else null)
oracle_cases:                  # at least one recorded input->expected-output case the build is verified against (T-011)
  - case_id: "<BR-XXX-C1>"
    input: "<concrete input>"
    expected_output: "<expected output>"
derived_from:                  # at least one [OBS-NNN#hash] (sql-trace / db-diff / report-output) the rule was measured from
  - "[OBS-NNN#hash]"
zone: spec                     # always spec
source: cleanroom              # always cleanroom — measured black-box, re-expressed in our words
consumable_by_build: true      # always true — BR is build-consumable
tags: []
---

# Behavior Rule BR-XXX — <Title>

## Rule

<The rule_statement expanded if needed: the algorithm in full, including conditions, ordering, and rounding/precision behavior. State it as logic to implement, not as a description of the original's code (which you have not read). For money rules, be explicit about precision, rounding mode, and sign handling.>

## Worked examples (measured)

<Walk through 2-4 of the worked_examples, showing input -> output and citing the OBS each was MEASURED from. These are black-box measurements, not derived from reading code. Include boundary cases (zero, max, rounding edges, refund/negative) for money rules.>

## Oracle cases

<The oracle_cases the built app is verified against in T-011. Each is a recorded input->expected output. These flow into the T-009 test oracle. PASS/FAIL in build is judged against these cases — never against re-running the original.>

## Derived from (provenance)

<List the OBS this rule was measured from, citing [OBS-NNN#hash]. The build room never sees these OBS; this is the audit trail. If the measurements were too sparse to fix the rule's boundaries, note the gap and request re-measurement (T-003) rather than inferring from code.>
