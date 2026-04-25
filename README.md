![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Version: 5.0](https://img.shields.io/badge/Version-5.0-blue.svg)

# HyperWorker v5.0

**A theory of why agent harnesses fail, expressed as a working harness.**

HyperWorker v5.0 is a clean break from v4.1.1. The earlier versions added rules, checks, and ceremony to make agent behavior reliable. v5.0 takes a different position: agent compliance should be **structurally enforceable**, not verbally requested. State should not be mutable; decisions should be hash-cited; verification should be tiered by cost; subagents should run on tool schemas they cannot exceed.

This is a theory. Evaluate it empirically.

---

## What changed from v4.1.1

| v4.1.1 | v5.0 |
|---|---|
| Six mechanisms | Five mechanisms + one substrate |
| Memory pipeline (DISCOVERIES → LEARNINGS → ARCHIVE) | Typed Artifacts: decisions, findings, anti-patterns, operating-reality. Append-only, hash-cited, supersede-not-edit. |
| Per-step `SESSION-STATE.md` writes | Replay from `events.jsonl`. No parallel state file. |
| READ-BACK ceremony | Hash-citation freshness check (Layer 1, automatic on every event). |
| 15-rule executor prompt | Under-30-line executor prompt; substrate enforces what the rules requested. |
| Forced-verbosity instructions in the prompt | Per-model profiles handle verbosity declaratively. |
| `case-studies/` as static teaching | `schemas/projects/` as executable bootstraps. |
| Pushback Protocol as runtime default | Council escalation triggered structurally; no per-task verbal pushback step. |

v4.1.1 remains on GitHub as the prior theory. v5.0 is a new tree, not a migration. **There is no migration path.** Operators with running v4.1.1 projects complete them on v4.1.1; new projects start on v5.0.

---

## What v5.0 is

- **Five mechanisms.** Lock, Atomicity, Typed Artifacts, Verification, Precedence. The Dependency mechanism is absorbed into Atomicity (capability gates + branch/fold).
- **One substrate.** `events.jsonl` (canonical, append-only, hash-chained), regenerable projections, hash sidecar. Every typed artifact is event-sourced; every projection is byte-deterministic from events.
- **Hash citations.** Decisions, findings, anti-patterns, operating-reality cited as `[KIND-ID#hash]`. Stale citations block writes at Layer 1.
- **Capability gates.** Subagents declare what tools they `provides:`; tasks declare `required_tools:`. The harness composes the subagent's tool schema by intersection. Tool absence is not "the agent should know not to call this" — the tool is not in the schema.
- **Bounded subwork.** Branch/fold preserves sub-trajectory in events while keeping the parent's context clean.
- **Per-project schemas.** Five ship as defaults; each is a different shape with different council composition. Marketing-campaign is the deepest port from v4.1.1; software-feature-ship, client-onboarding, event-planning, and compliance-audit are competent baselines meaningfully different in domain, council, and capability gates.
- **Per-model profiles.** Six ship: `default`, `claude-opus-4-7`, `claude-opus-4-6`, `claude-sonnet-4-6`, `claude-haiku-4-5`, `github-copilot`. Profiles document what each model does *differently*, not which is "better."

## What v5.0 is not

- Not a CLI. Not a package. Not a hosted service. The harness is markdown and YAML files. `hw <command>` is an agent protocol, not a binary; every operation is a documented file-system protocol any agent can execute.
- Not a refactor of v4.1.1. The diagnosis is different.
- Not a finished product. v5.0 is a theory; primitives that fail their hypothesis falsifiers (see `core/*.md` §Hypothesis sections) get retired in v5.1.

---

## Get started

```bash
git clone <this-repo>
cd <this-repo>
```

Then tell your AI agent:

> *"Read HARNESS.md. Bootstrap a project from the `<schema-name>` schema for `<short description>`."*

Available schemas:

| Schema | When to use |
|---|---|
| `marketing-campaign` | Lead-gen funnels, email sequences, landing pages, paid ad creative |
| `software-feature-ship` | Schema → API → frontend → tests → deploy |
| `client-onboarding` | Repeatable onboarding flows; cross-client compounding |
| `event-planning` | Real-world events with hard dates and physical vendors |
| `compliance-audit` | SOC 2, ISO, HIPAA, PCI, internal-quality audit prep |

If none fit, the agent scaffolds from default templates and offers `hw schema save` to capture your derived schema after the project completes.

## Read in this order

1. `HARNESS.md` — entry point, file structure, bootstrap protocol.
2. `core/SUBSTRATE.md` — events, projections, hashes, the `hw` agent protocol.
3. The five `core/*.md` mechanism files.
4. The schema closest to your work.

## Works with

Agent-agnostic. Any AI that can read markdown, append to a file, and follow a documented protocol can operate the harness:

- Claude (Opus / Sonnet / Haiku) — see `templates/models/claude-*.yaml`
- GitHub Copilot CLI — see `templates/models/github-copilot.yaml`
- Other models — start with `templates/models/default.yaml` and tune as you observe behavior

## License

MIT. See [LICENSE](LICENSE).

---

*Built by [@mrhobbeys](https://x.com/mrhobbeys).*
