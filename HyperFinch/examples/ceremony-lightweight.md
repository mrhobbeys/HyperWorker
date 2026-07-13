You are an agent operating a HyperWorker v5.2 harness. You have tools that append
hash-chained events and write files into a workspace. The harness computes every
hash for you when you call `hw_append_event` — supply only `kind`, `actor`,
`project`, `payload`.

Your job: bootstrap a tiny project and complete one task using the **lightweight**
path (the minimum the substrate accepts). Project id `ceremony-demo`, schema
`report-synthesis`. The deliverable is a one-paragraph synthesis note on:
"{{topic}}".

Do these steps, one `hw_append_event` per step:

1. `project.activate` — `{project_id, name, schema, started_at}`.
2. `bootstrap.probe_skipped` — `{schema, reason}` (single-source project; no
   external surface to probe).
3. `task.create` — T-001, `{task_id, title, frontmatter}`.
4. Write the deliverable with `hw_write_file` to
   `projects/ceremony-demo/tasks/T-001/note.md`.
5. `task.complete` — `{task_id, completion_report_path}`.
6. Call `finch_done` with a one-line summary.

Call the tools; do not just describe them.
