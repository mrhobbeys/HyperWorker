# Elimination — {{ project_id }}

> **Projection of the hypothesis state carried on `finding.add` events (`status`, `test_ref`).** Lives at `projects/<project-id>/ELIMINATION.md`. Regenerated whenever a hypothesis is added or its status changes; never hand-edited (`core/SUBSTRATE.md` §Projection rules).
>
> Hand this to a new agent **first**. It is the one file that stops a fresh context from restarting the generic checklist you already ran.

---

**Frontier:** <one line — the single most likely remaining hypothesis, and the next test that would settle it>

## Matrix

| Hypothesis | Status | How tested (test_ref) | Result |
|---|---|---|---|
| F-012 — <one line> | excluded | `ED-014` — ran the import against the live path | Path executed; the symbol resolved. Not this. |
| F-013 — <one line> | suspect | — (static read only) | Argues against, untested. Still live. |
| F-014 — <one line> | open | — | Not investigated. |

Statuses are `open`, `suspect`, `excluded`. **`excluded` requires a `test_ref` naming a dynamic test** — an `evidence.capture` id or a checked-claim predicate that actually ran (`core/SUBSTRATE.md` §Exclusion Discipline). A static read reaches `suspect` and stops there; Layer 1 check 19 FAILs `excluded_without_test_ref` on anything else.

## Rendering protocol

A fresh agent must produce this file byte-identically from an event prefix (`core/SUBSTRATE.md` §Projection rules, rule 2).

1. Filter `events.jsonl` to `finding.add` events for this `project` whose payload carries a `status` field, in append order. A later `finding.add` that `reverses:` an earlier hypothesis replaces its row (same row position, new status).
2. One row per hypothesis, ordered `excluded` last, then by artifact ID ascending — the live frontier reads at the top, the closed ground at the bottom.
3. **Hypothesis** is `<artifact-id> — <title>`. **Status** is the payload's `status`. **How tested** is `test_ref` rendered as inline code plus the payload's one-line note, or `—` when null. **Result** is the first line of the finding's `evidence` field.
4. The **Frontier** line is authored, not derived: the closing agent writes the single most likely remaining hypothesis and the next test. Re-write it on every regeneration; one line, no list.
5. Write the file, compute its SHA-256, and update `hashes.json` for `projects/<project-id>/ELIMINATION.md`.

## See also

- `core/SUBSTRATE.md` §Exclusion Discipline, §Evidence Capture
- `core/VERIFICATION.md` §Layer 1 check 19 — `excluded_without_test_ref`, `excluded_test_ref_unresolved`, `invalid_hypothesis_status`
- `schemas/artifacts/finding.yaml` — the `status` / `test_ref` fields and `exclusion_rule`
