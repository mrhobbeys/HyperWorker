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
| `recitation_overlap_threshold` | Jaccard threshold below which Layer 1 rejects a recitation. |
| `notes` | Citation-backed notes about model-specific behaviors. |

## Override semantics

Profile fields are merged into the harness defaults at project load time. Order of precedence (lowest → highest):

1. Harness defaults (hard-coded in `core/*.md`).
2. The active model profile (`.hyperworker/models/<name>.yaml`).
3. Schema-level overrides (`schemas/projects/<name>/*.yaml`, e.g., a schema declaring `recitation_overlap_threshold: 0.75`).
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
