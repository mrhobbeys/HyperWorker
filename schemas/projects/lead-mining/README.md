# lead-mining schema
Mine the operator's OWN inbound email (multi-account, multi-year) into one verified
master lead list with each contact's need, company/role, and status.
Bootstrap: "Read HARNESS.md. Bootstrap a project from `lead-mining` named `email-lead-mining`."
Artifacts: OR-001 (accounts/range/filters), SRC (each mailbox), Findings (each lead),
Decisions (include/exclude rules), Anti-patterns (false-positive patterns).
Tasks: T-000 accounts+filters -> T-001 harvest (fan-out) -> T-002 filter/dedupe ->
T-003 enrich+infer need -> T-004 verify+status -> T-005 master list + handoff.
Needs an EMAIL CONNECTOR matching each mailbox's provider (e.g., Outlook/M365, Gmail, or another mail provider) + web_search/web_fetch for enrichment.
Inbound-only; never fabricates; operator approves any outreach later.
