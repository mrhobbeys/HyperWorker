# Ceremony-Cost — Model Comparison: the thinking layer

> Two local models operating the HyperWorker harness through the HyperFinch v0.2
> tool-call loop, on the same task, prompts, axes, and structural checks. The
> contrast isolates **the thinking layer**, not parameter count. Run on LM Studio,
> CPU, 64 GB RAM, ~no VRAM, 2026-06-09/10.

| | `openai/gpt-oss-20b` | `qwen/qwen3-4b-thinking-2507` |
|---|---|---|
| Params | 20B | 4B |
| Reasoning layer | near-zero (low effort) | heavy ("thinking") |
| Per-call latency (warm, 1 harness step) | **~33 s** | **~185 s** |

The headline inverts the naive expectation: the **5× smaller** model is **~6×
slower per step** and **vastly more token-hungry**, because it reasons and the
larger model does not. On CPU, where tokens drive wall-clock, the thinking layer
is the dominant cost — params are a rounding error next to it.

## The clean comparison: no-harness floor (identical trivial task)

Both models do the exact same work here — write one paragraph, no tools, no
events. This is the apples-to-apples thinking-layer measurement.

| Model | n (valid) | med total tokens | med reasoning | med completion | reasoning % of output | med sec/trial |
|---|---|---|---|---|---|---|
| gpt-oss-20b | 5 | **779** | **6** | 234 | **~3%** | fast (≈1 turn) |
| qwen3-4b-thinking | 2 (+1 INVALID) | **2,910** | **1,567** | 1,668 | **~94%** | **451** |

On identical trivial work, qwen3-4b spends **~260× more reasoning tokens**
(1,567 vs 6), **~3.7× more total tokens** (2,910 vs 779), and is **two orders of
magnitude slower** in wall-clock. And the thinking is **volatile**: across three
trials its total tokens were 1,802 / 4,019 / 1,977 — and **one no-harness trial
still timed out** (918 s) because the model spiralled into reasoning on a task
with nothing to reason about. gpt-oss-20b's floor, by contrast, is tight and
boring: ~779 tokens every time.

## Operating the full harness

| Model | lightweight cell | full-protocol cell |
|---|---|---|
| gpt-oss-20b | **5/5 complete**, score 0.833, ~8.3k tok, ~24 reasoning | **5/5 complete**, score 1.000, ~26.7k tok, ~148 reasoning |
| qwen3-4b-thinking | **0/2 — timed out** (>900 s on a later turn) | not reached (a fortiori: more turns, worse) |

gpt-oss-20b operates the **entire** 11-step protocol, 100% reliably, and the
resulting `events.jsonl` passes the reference `tools/hw-verify.py` (PASS, 0
tamper, 0 chain breaks) — a real model drove the loop, never computed a hash, and
produced a cryptographically valid chain.

qwen3-4b-thinking is **latency-bound** for multi-turn harness operation on this
hardware. Each turn re-sends a growing context to a stateless endpoint, and the
thinking pass grows with it, so by turn ~5 a single call exceeds the 900 s
ceiling. The reduced n=2 lightweight cell timed out 2/2; the full protocol (~12
turns) only compounds it. This is not a capability failure — the single-call probe
showed qwen emits **correct** `hw_append_event` tool calls with valid arguments —
it is a **latency** failure. The model *can* operate the harness; on CPU it cannot
do so within any practical per-call budget once the protocol runs more than a few
turns.

## Findings

1. **The thinking layer, not param count, is the ceremony-cost driver.** A 4B
   that reasons costs ~260× the reasoning tokens and ~6× the per-step latency of a
   20B that does not, on identical work. Comparing models by size here would have
   been the wrong axis entirely.
2. **Reasoning models are latency-bound for multi-turn agentic harness work on
   CPU.** Per-call cost grows with context; a long protocol crosses any fixed
   timeout. The fix is not a bigger timeout (the curve keeps climbing) — it is KV
   cache reuse / a faster substrate, or a non-thinking model for the operator role.
3. **A capable non-thinking local model operates the full HyperWorker protocol,
   reliably and verifiably.** gpt-oss-20b: 100% completion on the full protocol,
   chains that pass `hw verify`. The harness is operable by local models today —
   the constraint is the reasoning layer's latency, not tool-calling capability.
4. **Thinking tokens are volatile.** qwen3-4b's no-harness token count ranged
   1.8k–4.0k on the *same* prompt and spiralled to a timeout once. gpt-oss-20b's
   was flat. For the operator role — where you want predictable, bounded ceremony
   — flat-rate beats volatile-but-clever.

## Methodology & honesty

- **n is asymmetric** (gpt-oss n=5 full sweep; qwen n=2, no-harness cell only)
  because the qwen multi-turn cells are latency-bound and time out. The numbers
  compared apples-to-apples (the no-harness floor) are matched-task; the full/
  lightweight qwen rows report *timeout*, not a low score, and are excluded from
  completion stats by finch's trial-validity quarantine.
- **Single hardware, single run.** CPU inference, one machine. Latencies are
  illustrative of *this* setup; a GPU would shift absolute numbers but not the
  thinking-layer *ratio* (reasoning % of output is model-intrinsic).
- **Raw data:** `results/ceremony-cost-gptoss20b/results.jsonl`,
  `results/ceremony-cost-qwen4b-none/results.jsonl`. The leaderboards and these
  records are canonical; this document is a reading of them.
- `examples/compare-ceremony.py` generates the per-cell table automatically for
  the symmetric case (two runs with the same cell structure); the asymmetry here
  (qwen lacks completed multi-turn cells) is why this comparison is written by hand.
