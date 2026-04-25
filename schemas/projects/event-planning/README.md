# Schema: event-planning

> Use when: planning and executing a real-world event with a fixed date and physical vendor dependencies. The schema's value is making cascade-on-change visible: a venue swap or date change ripples through every dependent task automatically.

## What this schema gives you

- A four-tier system named `SAFETY-LEGAL / BUDGET / VENUE-CONSTRAINTS / EXPERIENCE`.
- Twelve default tasks across four phases (Foundation, Logistics, Pre-Event, Day-Of + Follow-up).
- Capability gates for vendor coordination, registration, promotion, attendee communications.
- Auto-escalation: any task triggering non-refundable deposit → critical; any day-of task within 24 hours of event date → critical.
- A council with `deadline-watcher`, `budget-guard`, `venue-constraint-reviewer`, and `cascade-reviewer`.

## The cascade pattern

When a foundational assumption changes (venue, date, capacity), the harness's reference-graph check flags every dependent task as having a stale citation. The `cascade-reviewer` council member explicitly enumerates the downstream cascade so the operator sees the full impact, not just the direct change.

## Bootstrap

```
hw bootstrap --schema event-planning --name <event-id>
```

## Customization

- Tag venue-specific anti-patterns with `cross-project:venue-<name>` so the next event at the same venue inherits them.
- For multi-day events, decompose the day-of-coordination task into per-day tasks rather than running one monster task.
