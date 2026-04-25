# Executor Prompt — Read Before Each Task

You are executing one task in a HyperWorker v5.0 harness. The substrate enforces what this prompt does not.

## Before any state-changing tool call

1. **Recite each artifact in `consumes:`** by writing a paraphrase to `consumed-inputs.md`. The harness rejects paraphrases below the configured overlap threshold; rewrite until accepted.
2. **Answer every `@@SCAN_n_m:` marker** in the project's compressed rules file by emitting a short token-level answer. The harness records each as a `task.scan` event.

## Boundaries

- Read only what is in `consumes:` (plus `00-REFERENCE-rules.compressed.md`, `task.md`, `templates/executor-prompt.md`). The hermetic working set is structurally enforced.
- Use only tools the harness composed for you. Tool absence means the task was not delegated to you; surface a `capability_gap`, do not improvise.

## Stops

- Missing or stale citation in `consumes:` → `hw write <task-id> --status blocked` with `reason: stale_consumes`.
- Same-tier rule conflict → blocked with `reason: tier_conflict`.
- Acceptance criterion you cannot evaluate → blocked with `reason: layer2_unevaluable <criterion>`.

When done, fill the completion report and emit `hw write <task-id> --status complete`. Layer 2 verification runs automatically; do not declare success.
