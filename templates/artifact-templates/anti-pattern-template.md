---
id: AP-XXX
kind: anti-pattern
created_at: <ISO 8601>
hash: sha256:<filled-by-harness>
title: "<one line: the failure mode>"
triggers:
  - "<plan condition that would activate this anti-pattern>"
applies_to: "<scope — system, tool, platform, content type>"
why_it_fails: "<one paragraph: the mechanism of the failure>"
alternatives:
  - "<better approach 1>"
  - "<better approach 2>"
regression_test: "<path to a test or check that detects regression to this anti-pattern, if available>"
reverses: null               # or "AP-<old-id>" — rare; only if the underlying behavior changed
tags: []
---

# Anti-Pattern AP-XXX — <Title>

## What does not work

<One paragraph: the approach, in plain language.>

## When it applies

<Trigger conditions: how an agent would recognize a plan that's about to step on this.>

## Why it fails

<The mechanism. Be specific — "DOM rerenders on selection change" is more useful than "doesn't work."  Avoid moralizing; describe the failure.>

## What to do instead

<Each alternative is a complete approach, not a hint.>
