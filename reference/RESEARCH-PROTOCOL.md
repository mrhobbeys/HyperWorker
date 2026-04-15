# Domain Research Protocol (Optional)

## Purpose

This protocol is for operators who want the orchestrator to research their domain before scaffolding a project. It is **optional** — the harness works without it. Enable it in `config.yaml` by setting `research.enabled: true`.

## When to Use This

Use domain research when the operator is new to the harness AND the orchestrator lacks domain knowledge that would improve the initial scaffold. The research step adds 3-5 minutes of latency before real work begins. If the operator already knows their domain well and can answer the orchestrator's questions directly, skip this step.

## How It Works

### What the Orchestrator Does

1. Ask the operator: "What domain is this project in? What does a successful version of this project look like?"
2. Research the domain using available tools (web search, file reading, etc.) to understand common constraints, dependencies, failure modes, and quality standards for that type of work.
3. Produce **exactly two draft outputs** — nothing else:
   - A **draft `config.yaml`** with domain-appropriate values (precedence tier names, scope taxonomy, learning categories)
   - A **draft `00-REFERENCE-rules.md`** with domain-appropriate rules populated in each tier

### What the Orchestrator Does NOT Do

- Does not produce a "research document" or "case study" that sits in the project folder
- Does not pre-populate task files (tasks come from the operator's specific project, not generic domain knowledge)
- Does not spend more than the configured `max_duration_minutes` (default: 5)
- Does not treat its research findings as authoritative — they are **drafts for the operator to verify**

### The Verification Gate

After producing the two drafts, the orchestrator presents them to the operator with:

> "I've drafted a config and reference file based on what I found about [domain]. Review these — they're starting points, not final. What needs to change?"

The operator edits, confirms, or replaces the drafts. Only then does the orchestrator proceed to project scaffolding.

This is a subset of the standard Verification Checkpoint (see SYSTEM.md). The research drafts feed into the checkpoint — they don't bypass it.

## Hallucination Risk

The orchestrator may produce domain "best practices" that sound authoritative but are fabricated, outdated, or generic. This is the primary risk of domain research.

**Mitigations built into the protocol:**

1. Research outputs are explicitly labeled as **drafts for human review**, not authoritative knowledge.
2. The Verification Checkpoint requires the operator to confirm before any work begins.
3. Research produces only config seeds and reference file seeds — not standalone documents that could accumulate in the project folder.
4. The operator can provide a **real artifact** from their domain (an actual project plan, checklist, or workflow) instead of relying on the orchestrator's research. Real artifacts are always better than researched generics.

## Configuration

```yaml
# In config.yaml:
research:
  enabled: true
  max_duration_minutes: 5
  outputs:
    - "draft config.yaml"
    - "draft 00-REFERENCE-rules.md"
```

## When Research Fails

If the orchestrator cannot find useful domain knowledge within the time limit, it should say so and fall back to the standard onboarding flow: ask the operator questions directly and scaffold from their answers. Research failure is not a blocking condition.

If the operator provides a real artifact from their domain, use that artifact as the primary source instead of research. Real artifacts contain the actual constraints, language, and priorities that generic research misses.
