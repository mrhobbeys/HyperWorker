# Changelog — HyperFinch

## v0.1.0 (2026-06-09) — Initial design + runner

Split out of the HyperWorker workspace as a standalone project. HyperFinch is not bound by HyperWorker's no-shipped-code posture: it ships `finch.py`.

- `FINCH.md` design spec: flight plans, axes/cells/trials, one-at-a-time default (factorial opt-in), trial-validity quarantine, mechanical checks, structural metrics from HyperWorker `events.jsonl` when present, hypothesis map turning HyperWorker's falsifiers into runnable experiments, validity rules (spread reporting, no auto-tuning at small n).
- `finch.py` runner (stdlib + pyyaml): OpenAI-compatible endpoints, built-in `mock` endpoint for dry runs, bounded multi-turn file-block loop, append-only `results.jsonl` with `LEADERBOARD.md` as a regenerable projection, non-overlapping-spread verdict line.
- `templates/flight-plan-template.yaml`, `examples/smoke-plan.yaml` + `examples/smoke-task.md` (mock smoke test).

Hypotheses carried by v0.1.0:

| ID | Claim | Falsifier |
|---|---|---|
| H-F1 | Controlled one-axis sweeps with mechanical scoring detect prompt/condition effects that eyeball iteration misses or invents. | Across 5+ real sweeps, leaderboard verdicts never contradict the operator's prior eyeball judgment (the procedure adds cost, not signal). |
| H-F2 | A local model can operate a HyperWorker-style protocol at measurable token overhead. | No tested local model completes a minimal harness task within budget at any overhead (integration axis is dead weight; cut it). |
