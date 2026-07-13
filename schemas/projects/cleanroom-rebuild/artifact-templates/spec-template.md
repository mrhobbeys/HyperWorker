---
id: SPEC-XXX
kind: spec
created_at: <ISO 8601>
hash: sha256:<filled-by-harness>
title: "<one line: what this spec describes>"
spec_type: <screen-spec | data-dictionary | report-spec | hardware-spec | navigation-spec | other>
derived_from:                  # at least one [OBS-NNN#hash] — a spec with no OBS provenance is unmoored
  - "[OBS-NNN#hash]"
zone: spec                     # always spec — the only original-derived zone the build room may read
source: cleanroom              # always cleanroom — re-expressed in our own words
consumable_by_build: true      # always true — SPEC is build-consumable
verbatim_carryover: null       # or list of original strings retained out of functional necessity, each justified
tags: []
---

# Spec SPEC-XXX — <Title>

## Specification

<The cleanroom specification in our own words: the behavior the build room must implement. For a data-dictionary: each field's type, meaning, constraints, relationships. For a screen-spec: layout, fields, controls, validation, navigation. For a hardware-spec: the call/byte contract with example payloads. Precise enough to implement WITHOUT seeing the original.>

## Derived from (provenance)

<List the OBS this spec re-expresses, citing [OBS-NNN#hash]. State in one line how the observation maps to this spec. The build room never sees these OBS — this section is the audit trail spec-fidelity-watcher checks.>

## Verbatim carryover (wall note — optional)

<If any original string is retained out of functional necessity (data-field name, protocol literal, regulated label), list it here with a one-line justification. Everything else is re-worded. spec-purity (Layer 1) flags un-justified verbatim original expression. Protocol literals/field names that must survive normalization belong in the 00-REFERENCE-rules canonical-facts table too.>

## Open questions (optional)

<Anything the observations did not resolve, so the build room blocks with `spec_gap` rather than peeking at the original. Route gaps back to the observation room (T-002–T-004) for re-measurement.>
