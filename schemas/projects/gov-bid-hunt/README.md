# gov-bid-hunt schema

Find, qualify, and pursue government bid opportunities for ONE service-line segment.

## Bootstrap
> Read `HARNESS.md`. Bootstrap a project from the `gov-bid-hunt` schema named `<segment>`.

The agent asks the `bootstrap_questions` in `schema.yaml`, writes OR-001 (segment scope, routing, geographies, registration/eligibility gates, subcontracting, cadence), clones the 6 task templates, runs the project.activate council, and runs `hw next-step`.

## Artifacts
- **OR-001** — segment scope + registration/eligibility reality (the bidding gate).
- **SRC-NNN** — each monitored portal/source (SAM.gov, state procurement portals, local/tribal boards, aggregators).
- **Findings (F-NNN)** — each discovered opportunity, with status: pursuing | watch | excluded (reason).
- **Decisions (DEC-NNN)** — bid/no-bid calls, scope decisions, weighting rules.
- **Anti-patterns (AP-NNN)** — wasted-effort patterns (e.g., "utility-scale solar is out of segment").

## Tasks
T-000 registration + portal inventory → T-001 opportunity sweep → T-002 qualify & prioritize → T-003 capability statement → T-004 bid/no-bid + draft top response → T-005 tracker update + handoff.

## Notes
- Needs `web_search` + `web_fetch`; gated portals need a browser session (capability gap, satisfied by a human-driven browser, not a failure).
