# Per-Model Harness Profiles

> Per-model adaptations of harness behavior. Verbose-CoT models, terse models, browser-bound coding agents, and parallelism-aware models each respond differently to the same harness primitives. A profile encodes those adaptations declaratively.

## Hypothesis

Per-model profiles capture model-specific harness adaptations that contradict mainstream "one prompt for all models" guidance. The hypothesis is falsified if the same harness behavior produces wildly different agent quality across models — that would indicate the profile axes are wrong, not that profiles aren't needed.

## How profiles attach

A project's `config.yaml` references a profile from this directory:

```yaml
# In .hyperworker/config.yaml of a running project
model_profile: claude-opus-4-7
```

At project bootstrap, the harness copies the profile file into `.hyperworker/models/<name>.yaml`. From then on, the project uses its frozen copy; updating `templates/models/<name>.yaml` does not retroactively change the project's behavior. To pick up updates, the operator copies the new profile in explicitly (`hw model upgrade`).

## What a profile declares

| Field | Purpose |
|---|---|
| `model_family` | Family identifier — `claude`, `gpt`, `copilot`, `gemini`, `default`. |
| `generation` | Numeric or string — used by docs/citations only. |
| `verbose_cot` | True if the model emits long chain-of-thought by default. |
| `suppress_concise_directives` | True if "be concise" instructions degrade output for this model (cited, not asserted). |
| `auto_summarize_after_phase` | False if the model self-summarizes; true if the harness should append a summary task between phases. |
| `prefer_explicit_acceptance_criteria` | True if implicit context degrades quality on this model. |
| `parallelism_must_be_explicit` | True if the model under-parallelizes without explicit instruction. |
| `context_fill_thresholds.warn_at` | Fraction of context window where the harness warns. |
| `context_fill_thresholds.compact_at` | Fraction where compaction is forced. |
| `council_default_size` | Default council member count for this model. |
| `recitation_overlap_floor` | Jaccard overlap below which Layer 1 rejects a recitation (likely unread; default 0.35). |
| `recitation_overlap_ceiling` | Jaccard overlap above which Layer 1 rejects a recitation (verbatim echo, not paraphrase; default 0.90). v5.2.1; replaces the deprecated single `recitation_overlap_threshold`. |
| `notes` | Citation-backed notes about model-specific behaviors. |
| `relative_cost` | 1-5 ranking axis (1=cheapest, 5=most-expensive) used by v5.1 model_selection_policy. |
| `relative_capability` | 1-5 ranking axis (1=least-capable, 5=most-capable). |
| `relative_speed` | 1-5 ranking axis (1=slowest, 5=fastest). |

## Override semantics

Profile fields are merged into the harness defaults at project load time. Order of precedence (lowest → highest):

1. Harness defaults (hard-coded in `core/*.md`).
2. The active model profile (`.hyperworker/models/<name>.yaml`).
3. Schema-level overrides (`schemas/projects/<name>/*.yaml`, e.g., a schema declaring `recitation_overlap_floor: 0.45`).
4. Project-local overrides (`projects/<id>/.config-override.yaml`, if the operator wants per-project tuning).

A field set at a higher level wins. Schema overrides exist so a compliance-audit schema can require tighter thresholds even on a verbose-CoT model.

## Adding a profile

1. Copy `default.yaml` to `<your-model>.yaml`.
2. Adjust each field per documented model behavior. Cite sources where possible — postmortems, framework documentation, observed behavior with sample size.
3. Do not declare a model "worse" than another. Document what is *different*, not which is preferred.

## Profiles shipped

| File | When to use |
|---|---|
| `default.yaml` | Unknown model or family-mixed setups. Conservative; suppresses none of the substrate. |
| `claude-opus-4-7.yaml` | Anthropic Claude Opus 4.7. See notes for postmortem references. |
| `claude-opus-4-6.yaml` | Anthropic Claude Opus 4.6. Less verbose than 4.7; different threshold defaults. |
| `claude-sonnet-4-6.yaml` | Anthropic Claude Sonnet 4.6. Faster; different verbosity profile. |
| `claude-haiku-4-5.yaml` | Anthropic Claude Haiku 4.5. Smaller context; aggressive compaction defaults. |
| `github-copilot.yaml` | GitHub Copilot CLI agent mode. Coding-specialist profile. |
| `_ranking.yaml` | Operator override for the default cost/capability/speed rankings used by v5.1's `model_selection_policy`. Optional; absent means per-profile defaults apply. See the file itself for schema. |

## v5.1 — model_selection_policy resolution

When `OR-001.model_selection_policy.prefer` is set, the harness consults rankings at dispatch time:

1. Read `relative_cost`, `relative_capability`, `relative_speed` from each profile in the active roster (i.e., the profiles in `.hyperworker/models/` that the operator has materialized).
2. If `templates/models/_ranking.yaml` declares overrides for any profile, those override the per-profile defaults for ranking purposes.
3. Resolve `prefer`:
   - `cheapest-capable` — among profiles with `relative_capability >= task_floor`, choose the lowest `relative_cost`. Ties broken by highest `relative_capability`.
   - `fastest-capable` — among profiles with `relative_capability >= task_floor`, choose the highest `relative_speed`. Ties broken by lowest `relative_cost`.
   - `most-capable` — choose the highest `relative_capability` regardless of cost.
   - `manual-only` — surface the choice to the operator at dispatch time; bypass ranking.
4. If `OR-001.model_selection_policy.per_task_overrides` matches the dispatched task's kind, that override's `prefer` overrides the top-level `prefer` for this dispatch only.
5. On `fallback_trigger` events (e.g., Layer 1 fails N times in a row), the harness re-dispatches to `fallback_target` (an explicit `profile_id`) regardless of `prefer`.

`task_floor` defaults to `3` (mid-capability) and may be overridden in `_ranking.yaml` by task kind.

Soft enforcement — the harness records the chosen profile in the dispatch event but does not block if an agent ignores the policy in self-dispatch. If `prefer: cheapest-capable` and the harness still routes most work to the largest model, the falsifier in spec H-F8 is met and v5.1.x revisits.
