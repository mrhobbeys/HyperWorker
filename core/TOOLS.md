# Tools — The Catalog Contract

> **Not a mechanism, and not a dependency.** The harness is markdown and YAML; it stays that way. But agents working under it write code constantly — a hasher, a JSON differ, a thing that pokes an endpoint and checks the response — and every fresh session writes it again, slightly differently, unverified. This file is the contract for using a shared catalog of proven tools instead. The harness works exactly as well when no catalog is reachable.

The catalog is **HyperOtter** (`<your-git-host>:<user>/HyperOtter.git`), a sibling repo in the Hyper ecosystem. It holds small, single-file, hash-pinned tools, each with a manifest and a check predicate that proves it works. What follows is HyperWorker's side of the contract: when to look, what to verify, when to ignore it entirely, and what you owe back.

---

## Hypothesis

| ID | Claim | Falsifier |
|---|---|---|
| H-TC1 | A hash-pinned, check-predicated catalog removes the per-session tool-rewriting tax without becoming a dependency, because every step degrades to "build it locally" when the catalog is unreachable. | Agents reach for the catalog when they should have built something better and ship capped work — or the fetch-and-verify ceremony costs more than rewriting the tool, and agents skip verification rather than skip the catalog. |

---

## 1. Check the catalog before building

Before writing a tool, look for one that already exists.

The join is the **capability slug**. A task declares `required_tools:` (`core/ATOMICITY.md` §Capability Gates); a catalog manifest declares `capabilities_provided:`. They are the same namespace — short, lowercase, dot-namespaced (`env.identify`, `file.hash`, `http.probe`) and stable once published, because renaming a slug breaks every schema that references it.

1. Read the catalog index. Match the slug you need against the `capability` column.
2. If nothing matches, or nothing matches well, build it (§3). That is a normal, supported outcome, not a fallback.
3. If something matches, fetch and verify it (§2) before it does anything for you.

A capability gate that a catalog tool satisfies is still a gate: fetching a tool does not add it to your `provides:` list retroactively. Declare what you have, then meet the gate.

---

## 2. Fetching is verify-then-check, in that order

A fetched tool is untrusted code until two independent things say otherwise. Do both. Neither is optional, and the order matters — a corrupt file can still print the right words.

**(a) Verify the recorded SHA-256.** Every file in a tool's directory has its hash recorded in the manifest's `files:` block. Compute the hash of the bytes you actually received and compare. A mismatch means stop — not "probably a line-ending thing", not "close enough". This is what makes a copy verifiable *without trusting the transport it arrived over*, which matters because the transport is sometimes a human carrying a file (§5).

**(b) Run the manifest's check predicate.** The manifest carries a `check:` block — a command, an expected exit code, and optionally an expected output substring. Run it on **your** box before trusting the tool. It passing in the catalog is a claim about somebody else's machine.

This is `core/SUBSTRATE.md` §Checked Claims applied to code you did not write: the predicate shape is deliberately the same as the `cmd_exit` claim kind, for the same reason. A tool's own assertion that it works is not evidence; a command that ran and exited zero is. If the check fails, do not use the tool — fall back to building your own, and say so in the contribution notes if the failure is worth fixing.

**Pin what you keep.** A fetched tool that becomes part of the workspace's hash-computing toolchain is pinned like any other: emit `toolchain.anchor` with its path and SHA-256 (`core/SUBSTRATE.md` §Toolchain Anchor). After that, silent drift is a Layer 1 FAIL rather than a mystery.

---

## 3. A stronger agent is licensed to build fresh

**Old tooling conventions never cap a better agent.** If your capabilities exceed what the catalog holds — you can write something more robust, with fewer dependencies, covering a platform the cataloged version misses, or simply better — build it. The catalog is leverage, not a leash, and an agent that degrades its own work to match a two-year-old script has used it wrong.

The bar for "better" is one sentence you could say to the existing tool's author that they would agree is an upgrade, not a different way of writing the same thing.

The only obligation is to **contribute it back**, per the catalog's own CONTRIBUTING protocol. Three things travel with the tool and none of them are optional:

| | What | Why |
|---|---|---|
| Manifest | `MANIFEST.yaml` — capability slugs, interface, per-file SHA-256, provenance, maturity | Without hashes and slugs the next agent cannot verify it or find it. |
| Check predicate | A command that actually ran and actually passed on your box | An unverified claim that a tool works is the exact failure the catalog exists to prevent. |
| No secrets | A scan of every file, then the manifest's explicit attestation | Same rule as `core/SUBSTRATE.md` §Secrets Gate, for the same reason: catalogs are copied, and a leaked credential in a copied file is permanent in more places than one. |

New contributions start at `experimental` maturity and are promoted by *use in a second, different engagement* — not by confidence.

---

## 4. The catalog is an accelerator, never a dependency

**A HyperWorker harness must keep working perfectly well when the catalog is completely unreachable.** No network, repo down, air-gapped box, wrong side of a firewall — none of it changes what the harness can do. The catalog only ever makes things faster when it happens to be there.

Concretely, that means:

- No task, schema, template, or verifier check may require a catalog fetch to pass. Nothing in `core/` reads a manifest.
- An unreachable catalog is a normal condition, not an error state. Build the tool locally, exactly as you would if the catalog did not exist, and move on. It does not warrant a `capability.gap`, a block, or an operator interrupt.
- If contributing back is impossible right now (no network, no push rights), that does not block the work either. Leave the tool and its manifest where the operator will find them and note it in the handoff.

This asymmetry is the whole design. Everything in §1–§3 is worth doing *when it is cheap*; none of it is worth stalling for.

---

## 5. Shape of a good tool

Field evidence, not preference. On one engagement an executor box had **no Python installed at all**. The only way to get tooling onto it was for a human to hand-carry a PowerShell bundle by some out-of-band route and hash-verify it on arrival. Every rule here is that incident generalized.

- **Single file.** A tool you can copy in one operation is a tool you can hand-carry. A tool that is a directory tree with an install step is not.
- **Standard library only.** No package installs. The box may have no package manager, or no network to reach one, and finding that out mid-task is the expensive way to learn it.
- **Platform variants are encouraged**, not exotic. A widely-used tool that ships Python *and* PowerShell *and* shell variants works regardless of what happens to be on the box. Each variant is its own file with its own recorded hash and its own invocation line.
- **Plain ASCII.** Smart quotes and non-breaking spaces survive neither hand-carrying nor diffing, and they change the bytes, which changes the hash.
- **No secrets, ever** — not in a tool, not in a manifest, not as a realistic-looking placeholder.

---

## Relationship to Other Mechanisms

| Mechanism | Interaction |
|---|---|
| Atomicity | `required_tools:` capability slugs are the catalog's `capabilities_provided:` slugs. A missing capability is still a `capability.gap`, whether or not a catalog exists. |
| Verification | A manifest's `check:` predicate is the §Checked Claims discipline applied to fetched code: a command that ran, not an assertion that it works. |
| Substrate | A kept tool is pinned by `toolchain.anchor`; a contributed tool passes the same secrets bar as any payload. Nothing about the catalog enters `events.jsonl` as a new kind. |
| Lock, Precedence, Typed Artifacts | No interaction. The catalog is outside the harness, by design. |
