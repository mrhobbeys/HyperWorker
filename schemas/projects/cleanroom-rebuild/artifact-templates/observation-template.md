---
id: OBS-XXX
kind: observation
created_at: <ISO 8601>
hash: sha256:<filled-by-harness>
title: "<one line: what original-system fact this captures>"
observation_type: <screen | navigation-edge | sql-trace | db-diff | hardware-io | report-output | error-state | other>
capture_method: <gui-driver | screenshot | sql-trace | db-diff | io-monitor | http-loop | manual | other>
source_ref: "<where on the ORIGINAL this was captured: screen id / table / action / device + timestamp>"
zone: observed                 # always observed — capability gates forbid build read of this zone
source: original               # always original — the wall keys on this; never crosses into build
consumable_by_build: false     # always false — a build event citing this is a Layer 1 wall breach
artifact_path: null            # or "observed/<...>" path to the raw capture (screenshot/trace/byte dump)
tags: []
---

# Observation OBS-XXX — <Title>

## What was measured

<2-3 sentences in our own words: what fact about the original this captures, and how it was MEASURED (black-box). Do not infer from code — observations are measurements only.>

## Captured detail

<The substance of the capture. For a screen: the vision-model description of the layout/fields/controls. For a sql-trace: the statements issued. For a db-diff: the row-level before/after delta. For hardware-io: the byte sequence / device-protocol calls (e.g., OPOS). Raw artifacts (screenshots, trace files, byte dumps) live at artifact_path; this section is the readable summary the spec room consumes.>

## Provenance (wall note)

This is a `source=original` artifact in the `observed/` zone. It is NOT consumable by the build room. Spec-room tasks (T-005–T-009) may read it to author SPEC/BR; build-room tasks (T-010, T-011) must never cite it. Citing this from a build event is a Layer 1 wall breach.

## Repeatability note (optional)

<If the captured behavior is input-dependent or non-deterministic, note the inputs used and whether re-measurement is needed to seed behavior-rule worked_examples / oracle_cases (T-006).>
