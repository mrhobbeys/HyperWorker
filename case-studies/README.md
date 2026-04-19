# Case Studies — HyperWorker v4.0

These case studies show the harness applied to five different domains. They serve as reference patterns when the optional domain research is turned off, or as supplementary examples alongside research.

Each case study highlights a different core mechanism to demonstrate the full range of the harness.

## The Case Studies

| # | Domain | Type | Primary Showcase | Use When... |
|---|---|---|---|---|
| 01 | [Marketing Funnel Launch](01-marketing-funnel/) | **Full worked example** | Precedence | Your project involves content creation, brand rules, or platform-specific deliverables |
| 02 | [Software Feature Ship](02-software-feature-ship/) | Scenario brief | Dependency | Your project has strict build → test → deploy chains or code dependencies |
| 03 | [Client Onboarding](03-client-onboarding/) | Scenario brief | Memory | Your project is repeatable across clients/accounts and benefits from knowledge compounding |
| 04 | [Event Planning](04-event-planning/) | Scenario brief | Atomicity | Your project has hard deadlines, physical deliverables, and tasks with verifiable real-world "done" states |
| 05 | [Compliance Audit Prep](05-compliance-audit/) | Scenario brief | Precedence + Lock | Your project is regulation-driven with strict rule hierarchies and zero distraction tolerance |

## How to Use These

**If you're an agent scaffolding a new project:** Read the case study closest to the user's domain. Use it to inform how you decompose tasks, name precedence tiers, define scope tags, and structure the dependency chain. All six mechanisms appear in every case study — the "primary showcase" just tells you which one gets the deepest treatment.

**If you're a human setting up the harness:** Browse the case study closest to your work. It shows you what a configured harness looks like for your type of project — how to name your rules, what your task breakdown might look like, and what discoveries you should expect to capture.

**If none of these match your domain:** The mechanisms are universal. Pick the case study with the most structural similarity (not domain similarity) to your project. An architecture firm might learn more from Event Planning (physical deliverables, hard deadlines) than from Software Feature Ship (even though both are "building things").

## Full vs. Brief

The Marketing Funnel Launch (01) includes complete file artifacts — config, PROJECT.md, TASK-STATE.yaml, reference rules, and task files. All other case studies are scenario briefs: a single markdown file that maps the domain to the six mechanisms with example values. The briefs reference the full example for file format patterns.

This keeps maintenance manageable. If you need a full worked example for a different domain, use the Marketing Funnel as a structural template and fill it with your domain's content.
