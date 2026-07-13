You are an agent operating a HyperWorker v5.2 harness. You have tools that let you
append hash-chained events and write files into a workspace. The harness computes
every hash for you when you call `hw_append_event` — you never compute SHA-256
yourself; you supply only `kind`, `actor`, `project`, and `payload`.

Your job: bootstrap a tiny project and complete one task, recording each step as
an event, following the **full protocol**. The project id is `ceremony-demo`,
schema `report-synthesis`. The deliverable is a one-paragraph synthesis note on:
"{{topic}}".

Do these steps in order, one `hw_append_event` per step (use sensible payloads):

1. `project.activate` — payload `{project_id, name, schema, started_at}`.
2. `bootstrap.inventory_diff` — payload with `{schema, probe_method, declared,
   found, missing_from_declared, missing_from_found, operator_reconciliation}`.
   This is a single-source project; reconcile by confirming the one note as the
   scope (set `operator_reconciliation` to a non-null object).
3. `bootstrap.scope_locked` — payload `{project_id, locked_at, scope_items}`.
4. `operating-reality.add` — OR-001, payload with at least `{id, created_at,
   budget, timeline, team, authority, tags}`.
5. `task.create` — T-001, payload `{task_id, title, frontmatter}` where
   frontmatter has `phase, risk_level, depends_on, consumes`.
6. `task.status` — T-001 `{task_id, from: "pending", to: "in_progress"}`.
7. `task.recite` — `{task_id, consumed_id, paraphrase, overlap_score}` paraphrasing
   OR-001 in your own words.
8. `task.scan` — `{task_id, marker_id, answer}` for one rule marker.
9. Write the deliverable with `hw_write_file` to
   `projects/ceremony-demo/tasks/T-001/note.md`.
10. `task.complete` — `{task_id, completion_report_path}`.
11. Call `hw_verify`, then call `finch_done` with a one-line summary.

Be concise in payloads. Do not skip steps. Call the tools; do not just describe them.
