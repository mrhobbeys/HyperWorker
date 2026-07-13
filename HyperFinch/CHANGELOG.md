# Changelog — HyperFinch

## v0.2.0 (2026-06-09) — Tool-call loop + structural checks

The v0.2 roadmap item, shipped: a trial can now *operate* a HyperWorker bootstrap, not just emit files.

- **Tool-call loop.** When a plan declares `tools:`, `finch.py` runs a real OpenAI function-calling loop (pass `tools` + `tool_choice: auto`, parse `tool_calls`, execute against the trial workspace, append `role: tool` results, reprompt until `finch_done` / `FINCH_DONE` / `max_turns`). The v0.1 file-block loop is unchanged and still the default when `tools` is absent.
- **Built-in `hyperworker` toolset.** `hw_read_file`, `hw_list_dir`, `hw_append_event`, `hw_write_file`, `hw_verify`, `finch_done`. `hw_append_event` assigns the `EV-NNNN` id, timestamp, and `prev_hash` and computes the canonical SHA-256 (mirroring `core/SUBSTRATE.md` §Canonical Serialization and `tools/hw-verify.py`) — the model supplies only `kind/actor/project/payload`, so the chain is valid by construction. Cross-validated: a chain a model builds through this loop passes the reference `tools/hw-verify.py` (zero tamper, zero chain breaks).
- **`structural` check type.** Promotes the recorded structural metrics into scored predicates: `{type: structural, metric: task_complete, min: 1}`. `metric` is a named count or `kind:<event.kind>`; tested against `min`/`max`/`equals`. `structural_metrics` now also returns a `by_kind` histogram.
- **Token detail captured per trial:** `completion_tokens` and `reasoning_tokens` (from `usage.completion_tokens_details`), so the thinking-layer cost is first-class. **Leaderboard** gains median-tokens and median-reasoning columns per cell.
- **First real sweep — run.** `examples/ceremony-cost-plan.yaml` (full-protocol vs. lightweight vs. no-harness) with prompts `ceremony-{full,lightweight,none}.md`; `examples/ceremony-cost-mock.yaml` dry-runs the machinery with no model; per-model variants `ceremony-cost-{gptoss20b,qwen4b}.yaml`; `examples/compare-ceremony.py` for the side-by-side. Executed live on LM Studio (CPU): **gpt-oss-20b operates the full 11-step protocol 100% reliably (chains pass `tools/hw-verify.py`)**; the thinking-layer comparison vs. qwen3-4b-thinking is the finding. See `examples/CEREMONY-COST-FINDINGS.md` and `examples/CEREMONY-COST-COMPARISON.md`.
- Mock endpoint extended: with `tools` active it emits a deterministic tool-call sequence (a minimal bootstrap) so the loop is testable without a live model.

Hypotheses carried by v0.2.0:

| ID | Claim | Falsifier |
|---|---|---|
| H-F3 | A built-in tool that owns canonical hashing lets a model operate the event log without per-session serialization divergence or fabricated hashes. | A chain produced through the tool loop fails `hw verify`, OR models are observed bypassing the tool to hand-roll events. |
| H-F4 | Ceremony cost is measurable: full protocol, lightweight, and no-harness separate on tokens-per-completed-task and completion rate at small model sizes. | Across tested local models the three ceremony levels show overlapping spreads on both measures (ceremony is free, or uniformly fatal — either way the axis carries no signal). |

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
