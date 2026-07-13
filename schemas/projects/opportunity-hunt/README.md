# opportunity-hunt schema

Find, qualify, and pursue revenue opportunities in ONE non-government channel
(commercial-direct | cooperative-contracts | channel-partner | grants-funding).

## Bootstrap
> Read `HARNESS.md`. Bootstrap a project from the `opportunity-hunt` schema named `<channel>`.

The agent asks the `bootstrap_questions` in `schema.yaml`, writes OR-001 (channel, offering, target buyers, geographies, eligibility/membership gates, subcontracting, cadence), clones the 6 task templates, runs the project.activate council, and runs `hw next-step`.

## Artifacts
- **OR-001** — channel scope + eligibility/membership reality (the pursuit gate).
- **SRC-NNN** — each monitored source/program (marketplaces, co-op purchasing portals, partner program portals, grant databases, aggregators, associations).
- **Findings (F-NNN)** — each discovered opportunity, with status: pursuing | watch | excluded (reason).
- **Decisions (DEC-NNN)** — pursue/skip calls, scope decisions, weighting rules.
- **Anti-patterns (AP-NNN)** — wasted-effort patterns (e.g., a listing category that is always out of channel).

## Tasks
T-000 access/eligibility + source inventory → T-001 opportunity sweep → T-002 qualify & prioritize → T-003 positioning assets / capability statement → T-004 pursue/skip decision + draft top → T-005 tracker update + handoff.

## Notes
- Needs `web_search` + `web_fetch`; gated sources need a browser session (capability gap, satisfied by a human-driven browser, not a failure).
- `schema.yaml` lists the 6 canonical task templates.
