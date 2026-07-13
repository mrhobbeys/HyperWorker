![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-blue.svg)

# HyperFinch

**Variation → measurement → selection, for LLM tasks.**

Named for Darwin's finches: the canonical case of small variations, measured against an environment, selecting what survives. HyperFinch does that to your prompts, conditions, and inputs.

Everyone is looping. Almost nobody is *measuring*. The common loop is: tweak the prompt, eyeball the output, tweak again — vibes-based iteration with no record of what was tried, no controlled comparison, and no honest accounting of variance. HyperFinch replaces that with a flight plan: one task, one local LLM endpoint, a declared set of variations, N trials per variant, mechanical scoring, and a leaderboard you can argue with.

HyperFinch is a standalone project. It is **not** part of HyperWorker and is not bound by HyperWorker's no-shipped-code posture — it ships a working runner (`finch.py`). It pairs *well* with a HyperWorker workspace (structural metrics come free from `events.jsonl`), but it will sweep any prompt-shaped task against any OpenAI-compatible endpoint.

## Quick start

```bash
pip install pyyaml

# smoke test against the built-in mock endpoint (no LLM needed)
python finch.py run examples/smoke-plan.yaml

# real run against a local model (Ollama, LM Studio, llama.cpp, vLLM)
python finch.py run my-plan.yaml
```

Results land in `results/<plan-name>/`:

```
results/<plan-name>/
  results.jsonl        # append-only trial log — one JSON line per trial
  LEADERBOARD.md       # cells ranked by mean score, with spread
  trials/<cell>/<n>/   # each trial's workspace, prompt, and raw response
```

## The shape of a sweep

1. **Plan.** Copy `templates/flight-plan-template.yaml`. Declare the task (a prompt file plus inputs), the endpoint, the **axes** (what varies: an input value, a sampling param, or a whole prompt file), trials per cell, and the scoring checks.
2. **Run.** `finch.py run plan.yaml`. Baseline cell runs first, then one axis varied at a time (factorial is opt-in — it explodes combinatorially and usually answers a question nobody asked).
3. **Read.** `LEADERBOARD.md` reports mean, min, and max per cell. If the spread within a cell is larger than the gap between cells, the honest conclusion is "no detected difference at this n" — and the leaderboard says so rather than crowning a winner.

## What it measures

- **Mechanical checks** — regex, contains, word-count windows, file-exists, declared in the plan with weights. Pass/fail per trial, no judgment calls.
- **Structural metrics** — if a trial workspace contains a HyperWorker `.hyperworker/events.jsonl`, Finch automatically counts Layer 1/2 failures, recitation rejections, and completion events. A harness run becomes a scoreable object for free.
- **Judge (optional)** — a second model scores 1–5 against a declared rubric. Off by default; judges are noisy and the rubric is always visible in the plan, never implicit.

## What it refuses to do

**Auto-tune.** Finch reports; a human decides. Not inherited piety from HyperWorker's ethos — at n=10 trials per cell, automated "optimization" is a machine for laundering noise into confident-looking config changes. When the n is large enough that auto-selection would be statistically honest, that can be revisited.

**Crown winners from noise.** Every leaderboard line carries its spread. A bare mean is a lie of omission.

## Files

```
README.md                          — this file
FINCH.md                           — design spec: concepts, protocol, plan schema, scoring
finch.py                           — the runner (stdlib + pyyaml)
templates/flight-plan-template.yaml
examples/smoke-plan.yaml           — runs against the built-in mock endpoint
examples/smoke-task.md
CHANGELOG.md
LICENSE
```

## License

MIT — see [LICENSE](LICENSE).

---

*Built by [@mrhobbeys](https://x.com/mrhobbeys).*
