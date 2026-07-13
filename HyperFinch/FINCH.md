# HyperFinch — Design Spec (v0.2.0)

> One task. One endpoint. A declared set of variations. N trials per variant. Mechanical scores. A leaderboard that admits its own noise. Read this file to understand the design; read `README.md` to run a sweep.

---

## Why this exists

Prompt iteration as practiced is an uncontrolled experiment: one trial per variant, no fixed comparison set, results judged by eyeball, history kept nowhere. Conclusions drawn this way are indistinguishable from sampling noise — and they get baked into production prompts anyway.

The fix is not intelligence; it is *procedure*. Hold the task fixed, vary one thing at a time, repeat each variant enough times to see the spread, score with checks that don't require judgment, and write everything down. HyperFinch is that procedure as a tool.

A second motivation: HyperWorker (the sibling project this was split from) defines every primitive as a hypothesis with a falsifier — and ships no instrument to test one. Finch is the instrument. See §Hypothesis Map.

---

## Concepts

| Term | Meaning |
|---|---|
| **Flight plan** | The YAML file declaring everything: task, endpoint, axes, trials, scoring. One plan = one experiment. |
| **Axis** | One variable under test, with 2+ **levels**. Targets an input value, a sampling parameter, or a whole prompt file. |
| **Cell** | One configuration to be trialed. In `one-at-a-time` mode: the baseline plus one cell per (axis, level). In `factorial` mode: the cross-product. |
| **Trial** | One execution of one cell: fresh workspace, prompt rendered, endpoint called, checks scored. |
| **Check** | A mechanical pass/fail predicate with a weight. |
| **Score** | Weighted fraction of checks passed, 0.0–1.0. |
| **Verdict** | The leaderboard plus the run summary. Always reports spread; never reports a bare mean. |

## Protocol

1. **Expand cells.** `baseline` first (the plan with no axis overrides), then cells per mode. One-at-a-time is the default because factorial cost grows multiplicatively and most questions are "does X matter?", not "what is the optimal corner of a 4-dimensional grid?".
2. **Run trials.** For each cell, `trials_per_cell` independent trials. Each trial gets a fresh workspace directory; anything in `workspace.copy` (e.g., a HyperWorker checkout) is copied in clean. No state leaks between trials — a trial that mutates its workspace cannot contaminate the next one.
3. **Render the prompt.** `task.prompt_file` text with `{{key}}` placeholders substituted from `task.inputs`, after cell overrides are applied.
4. **Call the endpoint.** OpenAI-compatible `/chat/completions`. `endpoint.base_url: mock` short-circuits to a deterministic built-in responder so the machinery is testable without a model.
5. **Agentic turns (bounded).** If `budget.max_turns > 1`, the model may emit fenced file blocks (` ```file:relative/path `) which Finch materializes into the trial workspace, then it is reprompted to continue. The loop stops at `FINCH_DONE` in the response or at `max_turns`, whichever comes first. Bounded by construction — there is no "until it works".
   - **Tool-call loop (v0.2).** When the plan declares `tools:` (e.g. `tools: hyperworker`), Finch instead passes an OpenAI `tools` array to the endpoint and runs a real function-calling loop: parse `tool_calls` from the assistant message, execute each against the trial workspace, append `role: tool` results, reprompt. The loop ends when the model calls `finch_done`, emits `FINCH_DONE`, or hits `max_turns`. This lets a trial *operate* a HyperWorker bootstrap rather than just emit files. See §Tool-Call Loop.
6. **Score.** Run every check against the final response text and the trial workspace. Collect structural metrics if `.hyperworker/events.jsonl` is present.
7. **Record.** Append one JSON line to `results.jsonl` per trial: cell, overrides, turns, seconds, per-check results, score, paths. The log is append-only across re-runs; a re-run extends history rather than overwriting it.
8. **Report.** Regenerate `LEADERBOARD.md` from `results.jsonl` (the leaderboard is a projection; the JSONL is canonical — one idea worth keeping from the sibling project).

### Trial validity

A trial that fails for *infrastructure* reasons (endpoint unreachable, timeout, malformed response) is recorded with `"valid": false` and excluded from cell statistics. Conflating "the variant performed badly" with "the network hiccuped" corrupts every comparison downstream; the distinction is structural, not judgment.

## Flight plan schema

```yaml
finch: 1
name: subject-line-sweep          # results land in results/<name>/
mode: one-at-a-time               # one-at-a-time | factorial
trials_per_cell: 5

endpoint:
  base_url: "http://localhost:11434/v1"   # any OpenAI-compatible server; "mock" for the built-in responder
  model: "llama3.1:8b"
  api_key: null                            # or env var name prefixed with $, e.g. "$FINCH_KEY"

params:                            # sampling defaults; axes may override
  temperature: 0.7
  max_tokens: 1024
  seed: 42                         # passed through; honored only if the backend supports it

budget:
  max_turns: 1                     # >1 enables the bounded agentic loop
  max_seconds_per_trial: 120

workspace:
  copy: []                         # files/dirs copied into each trial workspace

task:
  prompt_file: task-prompt.md      # {{key}} placeholders substituted from inputs
  inputs:
    tone: "direct"
    audience: "solo operators"

axes:
  - id: tone                       # target: input — varies a task input
    target: input
    key: tone
    levels: ["direct", "playful", "urgent"]
  - id: temperature                # target: param — varies a sampling parameter
    target: param
    key: temperature
    levels: [0.2, 0.9]
  - id: prompt                     # target: prompt_file — swaps the whole prompt
    target: prompt_file
    levels: ["task-prompt.md", "task-prompt-v2.md"]

scoring:
  checks:
    - {id: has_subject, type: regex,          pattern: "^Subject:",  weight: 2.0}
    - {id: short,       type: word_count_max, value: 300,            weight: 1.0}
    - {id: no_hype,     type: not_contains,   pattern: "guaranteed", weight: 1.0}
    - {id: artifact,    type: file_exists,    path: "out/email.md",  weight: 1.0}
  structural: auto                 # auto | off — score .hyperworker/events.jsonl when present
  judge: null                      # optional: {model: "...", rubric: "...", weight: 1.0}
```

Check types: `regex`, `contains`, `not_contains`, `word_count_max`, `word_count_min`, `file_exists`, and (v0.2) `structural`. Each is decidable by inspection; if a desired criterion needs judgment, it belongs in `judge`, with the rubric stated in the plan where reviewers can see it.

A **`structural`** check (v0.2) reads a metric off the trial's `.hyperworker/events.jsonl` and tests it against `min` / `max` / `equals`. This *promotes* the structural metrics below from recorded-only into scored predicates:

```yaml
- {id: completed,    type: structural, metric: task_complete,             min: 1, weight: 3.0}
- {id: activated,    type: structural, metric: "kind:project.activate",   min: 1, weight: 1.0}
- {id: clean_layer1, type: structural, metric: layer1_fail,               max: 0, weight: 1.0}
```

`metric` is one of the named counts (`events`, `layer1_fail`, `layer2_fail`, `task_complete`, `council_escalated`, `recite_reject`) or `kind:<event.kind>` for an arbitrary event-kind count. A missing log reads as `0`, so a trial that never operated the harness simply fails its structural checks rather than erroring.

## Structural metrics (HyperWorker integration, optional)

When a trial workspace ends with `.hyperworker/events.jsonl`, Finch records per trial: total events, `verify.layer1.fail` count, `verify.layer2.fail` count, `task.recite` rejection count, `task.complete` count, `council.escalated` count, plus a `by_kind` histogram of every event kind. These are *recorded* alongside the score; as of v0.2 they are also **promotable into scoring** via the `structural` check type (above). This is the property that makes harness primitives testable: a harness run leaves a mechanical trace, and Finch compares traces across variants.

## Tool-Call Loop (v0.2)

The v0.1 file-block loop lets a model *write* files but not *operate* a harness — appending a hash-chained event requires computing a canonical SHA-256, which a model cannot do by generating tokens. v0.2 closes this with a real OpenAI tool-calling loop and a built-in `hyperworker` toolset.

**Enabling.** Set `tools: hyperworker` in the plan (or a list to subset). With tools active, Finch passes the OpenAI `tools` array and `tool_choice: auto`, then loops: read `tool_calls`, execute each against the trial workspace, append `role: tool` results, reprompt — until `finch_done`, `FINCH_DONE`, or `max_turns`.

**The `hyperworker` toolset.**

| Tool | Effect |
|---|---|
| `hw_read_file(path)` | Read a workspace file (schema, `bootstrap-probe.md`, template). |
| `hw_list_dir(path)` | List a workspace directory. |
| `hw_append_event(kind, actor, project, payload)` | Append one event to `.hyperworker/events.jsonl`. **The tool assigns `EV-NNNN`, `ts`, `prev_hash`, and computes the canonical hash.** The model supplies only the four fields. |
| `hw_write_file(path, content)` | Write a projection or Mutable-Surface file. |
| `hw_verify()` | Replay the log; recompute every event hash; report `tamper`, `chain_breaks`, PASS/FAIL. |
| `finch_done(summary)` | End the trial. |

`hw_append_event` is the load-bearing tool. It is the toolchain-anchor idea from `core/SUBSTRATE.md` made concrete: exactly one implementation of the canonical serialization exists, the model calls it rather than improvising, and the resulting chain is valid by construction. (Verified: a chain produced by a model driving this loop passes the reference `tools/hw-verify.py` with zero tamper and zero chain breaks.) Every tool is bounded — writes are confined to the trial workspace, and a malformed argument returns an error result rather than crashing the trial.

## Hypothesis Map

HyperWorker's `core/*.md` files declare falsifiable hypotheses and no instrument. Each maps to a flight plan:

| Hypothesis (HyperWorker) | Axis | Measure |
|---|---|---|
| H-T3 / H-T4 — recitation closes the consume-without-reading gap; band beats floor-only | recitation on/off; floor-only vs. band | downstream constraint-miss rate (checks targeting load-bearing constraints) |
| H-P1 — SCAN markers restore attention to rule tiers | SCAN markers present/absent in rules file | Tier-1 violation rate in outputs |
| H-V1 — most failures are caught at Layer 1 | layers enabled: {1} vs {1,2} vs {1,2,3} | failure counts by layer; operator escalations |
| H-S1 — event-sourced state beats mutable files | harness substrate vs. plain-files control | state-disagreement incidents per run |
| Ceremony cost (README "heavy upfront, light ongoing") | full protocol vs. lightweight_completion vs. no harness | tokens per completed task; completion rate by model size |

The last row is the first sweep worth running: *can a local model operate the harness at all, and at what token overhead?* Whatever the answer, it is a finding. As of v0.2 it is runnable: `examples/ceremony-cost-plan.yaml` sweeps full-protocol vs. lightweight vs. no-harness over the tool-call loop, scoring completion with a `structural` check (`task_complete >= 1`) and reading tokens-per-completed-task off the leaderboard. `examples/ceremony-cost-mock.yaml` dry-runs the whole machinery with no model.

## Validity rules (read before trusting a leaderboard)

- **Small n.** At `trials_per_cell: 5–10`, only large effects are detectable. The leaderboard prints spread (min–max) per cell; overlapping spreads mean "no detected difference", and the verdict line says so.
- **Seeds.** `params.seed` is passed through, but many local backends ignore it or implement it inconsistently. Treat trials as stochastic; that is what repetition is for.
- **One change at a time.** Factorial mode exists, but an interaction effect at n=5 per cell is a coin flip wearing a lab coat.
- **No auto-tuning.** Finch never edits your prompts, plans, or harness based on results. Reports inform; humans patch. This is a statistics position, not an ethos inheritance: at these sample sizes, an automated selector optimizes noise.

## Roadmap (earns its place or doesn't)

- v0.2 — **shipped.** Tool-call loop (beyond file blocks) so a trial can operate a full HyperWorker bootstrap via a built-in `hyperworker` toolset; structural metrics promotable into checks (`structural` check type); the ceremony-cost sweep (`examples/ceremony-cost-plan.yaml`) made runnable. See §Tool-Call Loop.
- v0.3 — paired-comparison judge mode (A/B, not 1–5 scales — pairwise is more reliable for LLM judges); significance hinting on the leaderboard when n supports it.
- Each addition follows the house rule carried over from the sibling project, which survives because it is correct, not because it is inherited: state the hypothesis, state the falsifier, retire what fails.
