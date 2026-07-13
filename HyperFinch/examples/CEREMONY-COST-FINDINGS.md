# Ceremony-Cost Sweep — Findings

> The first real HyperFinch sweep (FINCH.md §Hypothesis Map, last row).
> **Question:** can a small local model operate the HyperWorker harness at all,
> and at what token overhead? Three ceremony levels — full protocol, lightweight,
> no-harness — over the v0.2 tool-call loop.

## Status

| Stage | State |
|---|---|
| v0.2 tool-call machinery | **Validated** (mock dry-run, below) |
| Live sweep — gpt-oss-20b | **Complete & verified** (LM Studio, CPU) — see "Live results" |
| Live sweep — qwen3-4b-thinking | **Run** (reduced n, latency-bound) — see "Live results" |
| Model comparison (thinking layer) | See `CEREMONY-COST-COMPARISON.md` |

## What the sweep measures

- **Completion rate** — the `completed` structural check (`task_complete >= 1`):
  did a `task.complete` event actually land? This is "did the model operate the
  harness to the end," not "did the model claim success."
- **Tokens per completed task** — the leaderboard's median-tokens column, read
  against the completion rate. Ceremony cost is `tokens(full) − tokens(none)`.
- **Did it operate the harness at all** — `activated` (`project.activate >= 1`)
  and, for the full protocol, `scope_locked` (`bootstrap.scope_locked >= 1`).

Cells (one ceremony level each):

| Cell | Prompt | Ceremony |
|---|---|---|
| `baseline` | `ceremony-lightweight.md` | minimum the substrate accepts |
| `prompt=ceremony-full.md` | `ceremony-full.md` | full bootstrap (inventory diff, OR-001, recite, scan, verify) |
| `prompt=ceremony-none.md` | `ceremony-none.md` | no harness; produce the deliverable directly (control) |

## Machinery validation (mock dry-run)

`python finch.py run examples/ceremony-cost-mock.yaml` — 3 cells × 3 trials, no model:

```
| Cell                     | n | mean  | min   | max   | invalid | med tokens |
| baseline                 | 3 | 0.400 | 0.400 | 0.400 | 0       | 323        |
| prompt=ceremony-full.md  | 3 | 0.400 | 0.400 | 0.400 | 0       | 546        |
| prompt=ceremony-none.md  | 3 | 0.400 | 0.400 | 0.400 | 0       | 147        |
Verdict: Top cells have overlapping spreads — no detected difference at this n.
```

What this confirms:

1. The tool-call loop executes (`tool_calls=3` per trial: two `hw_append_event`
   + one `finch_done`).
2. The events the loop writes are a valid hash chain — the resulting
   `.hyperworker/events.jsonl` passes the reference `tools/hw-verify.py` with
   `result: PASS`, zero tamper, zero chain breaks. **A model driving the loop
   never computes a hash, yet the chain verifies.**
3. Structural metrics are computed and the `structural` checks score them
   (`activated` ✓ weight 1, `completed` ✗ weight 3, `clean_layer1` ✓ weight 1 →
   0.4), and the leaderboard reports per-cell median tokens.
4. The honesty guard works: the mock responder ignores the prompt, so all three
   cells are identical and the verdict correctly refuses to crown a winner.

The mock cannot answer the *ceremony-cost* question (it doesn't read prompts and
never emits `task.complete`). That needs a live model.

## Running it live

A live endpoint is required. With the small model under test served on an
OpenAI-compatible API (Ollama, LM Studio, llama.cpp, vLLM):

```bash
# edit examples/ceremony-cost-plan.yaml -> endpoint.base_url / endpoint.model
python finch.py run examples/ceremony-cost-plan.yaml
cat results/ceremony-cost/LEADERBOARD.md
```

Then read, per cell, from `results/ceremony-cost/results.jsonl`:
`tokens` (overhead), `checks.completed` (completion rate), `tool_calls` (how much
the model actually used the harness), and `structural.by_kind` (which ceremony
steps it managed to emit).

## Live results

Run on LM Studio (CPU, 64 GB RAM, ~no VRAM), 2026-06-09/10.

### gpt-oss-20b — `examples/ceremony-cost-gptoss20b.yaml`, n=5

| Cell | mean score | compl. | med tokens | med reasoning | med tool calls |
|---|---|---|---|---|---|
| full-protocol | **1.000** | 5/5 | 26,679 | 148 | 12 |
| lightweight (baseline) | 0.833 | 5/5 | 8,339 | 24 | 7 |
| no-harness | 0.167 | 0/5 | 779 | 6 | 0 |

**Verdict (finch):** `full` beats `lightweight` with non-overlapping spread — but
on *score*, not cost; both complete the task. The interesting axis is tokens.

**Findings:**

1. **A capable 20B operates the full harness, 100% reliably.** Every full-protocol
   trial emitted the complete protocol in order (`project.activate →
   bootstrap.inventory_diff → bootstrap.scope_locked → operating-reality.add →
   task.create → task.status → task.recite → task.scan → task.complete`) and
   scored 1.000 with zero variance across 5 trials.
2. **The produced chains are real.** A full-protocol trial's `events.jsonl`,
   written entirely through the tool loop, passes the reference
   `tools/hw-verify.py`: `result: PASS`, 0 tamper, 0 chain breaks. The model never
   computed a hash — `hw_append_event` did. This is H-F3 confirmed on a live model.
3. **Ceremony cost is large but flat-rate.** Token floor (no-harness) ≈ 779;
   lightweight ≈ 8.3k (**~11×** the floor); full ≈ 26.7k (**~34×** the floor,
   **~3.2×** the lightweight path). For this model, ceremony is "heavy upfront"
   exactly as the HyperWorker README claims — and affordable: it never failed.
4. **Reasoning is negligible** (6 / 24 / 148 tokens) — gpt-oss-20b runs at low
   reasoning effort, so its token cost is almost entirely protocol ceremony, not
   thinking. This is the control for the qwen3-4b comparison.

### qwen3-4b-thinking — latency-bound

The multi-turn cells (`examples/ceremony-cost-qwen4b.yaml`) are **latency-bound**
on CPU and time out: a single warm harness-step call is ~185 s with **91% of
completion tokens spent on reasoning**, and per-turn latency grows with the
multi-turn context until a later turn exceeds the (900 s) per-call ceiling. The
lightweight cell timed out 2/2; the full protocol (~12 turns) only compounds it.
The 4B emits *correct* tool calls — this is a latency failure, not a capability one.

The no-harness floor was captured separately (`examples/ceremony-cost-qwen4b-none.yaml`,
single-turn, feasible): median **2,910 total / 1,567 reasoning** tokens (~94% of
output is thinking) vs. gpt-oss-20b's **779 / 6** on the identical task — and even
one no-harness trial timed out (918 s) on a reasoning spiral.

See `CEREMONY-COST-COMPARISON.md` for the full head-to-head. _The honest framing:_
params are not the axis that matters here — the thinking layer is. A 4B that
reasons is slower and far more token-hungry per harness step than a 20B that does
not, even at one-fifth the size.
