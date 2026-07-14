---
id: WS-XXX
kind: workstream
created_at: <ISO 8601>
hash: sha256:<filled-by-harness>
confidence: validated
reverses: null                 # or "WS-<old-id>" if this is a status-change supersede
tags: []
child_project_id: "<project id inside the sibling instance>"
name: "<human-readable workstream name>"
origin: <existing-registered | spawned>
instance_path: "<relative path from this program instance's workspace root>"
bootstrapped_from_schema: "<schema name>"
lifecycle: <terminal | ongoing>
status: <active | parked | promoted | retired | done>
premise: "<operator-stated one-paragraph premise, or null for existing-registered>"
spawn_decision: "[DEC-NNN#<short-hash>]"   # or null for existing-registered
promoted_from: null            # "[WS-NNN#<short-hash>]" if this exists via promotion
last_rollup_citation:          # null until the first roll-up cycle covers this workstream
  path: null
  sha256: null
  cycle_id: null
  checked_at: null
---

# Workstream WS-XXX — <name>

## What this workstream is

<1-2 sentences: what subject matter this workstream covers and why it is its own
instance rather than folded into another workstream.>

## Origin

<If origin: existing-registered — when/how T-000's probe found it. If origin:
spawned — the proposal_id, and a pointer to [DEC-NNN#hash] (the spawn or promote
Decision), and if promoted, [WS-NNN#hash] of the source workstream.>

## Current status

<status> as of <date>. <One line on why, if the status just changed — the
reasoning lives in the citing Decision; this is a pointer, not a restatement.>

## Status history

<Chronological list of prior WS-XXX entries this one reverses, each with its
status and the Decision that authorized the change. Traverse via `reverses` back
to the origin entry.>

## Last roll-up

<Citation to the SESSION-HANDOFF.md / CYCLES.md this workstream was last rolled
up from, per rules-template.md §Cross-Instance Citation Format, or "not yet rolled
up" if this is the workstream's first cycle.>
