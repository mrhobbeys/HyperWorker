#!/usr/bin/env python3
"""
make-golden-fixture.py — deterministic generator for the HyperWorker golden fixture.

The golden fixture is a tiny, fully hash-chained reference workspace: a known
`events.jsonl`, the projections those events must render to (byte-for-byte), and
the `hashes.json` sidecar binding them together. It exists to turn the substrate's
central promise — *two agents rendering from the same event prefix produce
byte-identical projections* (core/TYPED-ARTIFACTS.md §Projection Rendering
Protocol) — from a claim into something `tools/hw-verify.py` can check.

This script IS the reference renderer. Running it regenerates the fixture from
scratch; the output is deterministic (no clocks, no randomness). After writing,
verify with:

    python tools/hw-verify.py --workspace tools/fixtures/golden-workspace

which must print `result: PASS`. If a second, independently written renderer
produces different bytes for any projection, the projection hash drifts and
`hw verify` FAILs on this fixture — which is exactly the regression the fixture
is here to catch.

Canonical serialization (sort_keys, minimal separators, ensure_ascii=False, UTF-8)
mirrors core/SUBSTRATE.md §Canonical Serialization and tools/hw-verify.py exactly.
Rendering decisions this generator commits to are documented in
tools/fixtures/README.md.

Usage:  python tools/make-golden-fixture.py [--out <dir>]
Dependencies: Python 3.9+ stdlib only.
"""

import argparse
import hashlib
import json
from pathlib import Path

PROJECT = "golden-demo"
SCHEMA = "report-synthesis"
ZERO_HASH = "sha256:" + "0" * 64

# A fixed clock. Determinism is the whole point — the fixture must regenerate to
# identical bytes on every machine, so timestamps are pinned, not sampled.
T0 = "2026-06-09T10:00:00Z"
T1 = "2026-06-09T10:00:05Z"
T2 = "2026-06-09T10:01:00Z"
T3 = "2026-06-09T10:02:00Z"
T4 = "2026-06-09T10:03:00Z"
T5 = "2026-06-09T10:30:00Z"
T6 = "2026-06-09T10:45:00Z"


# ----------------------------------------------------------- canonical hashing

def canonical_serialize(obj) -> bytes:
    """Identical to core/SUBSTRATE.md §Canonical Serialization and hw-verify.py."""
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def event_hash(event: dict) -> str:
    canonical = {k: v for k, v in event.items() if k != "hash"}
    return sha256_hex(canonical_serialize(canonical))


def short(full_hex: str) -> str:
    return full_hex[:12]


def write_text(path: Path, text: str) -> None:
    """Write UTF-8 with LF endings (the substrate hashes projection bytes as
    written to disk; CRLF would change every hash). newline='' suppresses the
    Windows translation that would otherwise turn our explicit \\n into \\r\\n."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def proj_short_hash(text: str) -> str:
    """Short hash of a projection = first 12 hex of sha256 of its UTF-8 bytes."""
    return short(sha256_hex(text.encode("utf-8")))


# ----------------------------------------------------------- event chain builder

class Chain:
    """Accumulates hash-chained events, assigning EV-NNNN ids and prev/hash."""

    def __init__(self):
        self.events = []
        self._prev = ZERO_HASH

    def add(self, ts, kind, actor, payload) -> dict:
        ev = {
            "id": f"EV-{len(self.events) + 1:04d}",
            "ts": ts,
            "kind": kind,
            "actor": actor,
            "project": PROJECT,
            "payload": payload,
            "prev_hash": self._prev,
        }
        ev["hash"] = "sha256:" + event_hash(ev)
        self._prev = ev["hash"]
        self.events.append(ev)
        return ev


# ----------------------------------------------------------- projection renderers
# These renderers ARE the reference. The exact formatting choices (frontmatter
# field order, list rendering, the `hash:` field carrying the originating
# add-event's short hash) are documented in tools/fixtures/README.md.

def render_decision(ev: dict) -> str:
    p = ev["payload"]
    h = short(ev["hash"][len("sha256:"):])
    lines = [
        "---",
        f"id: {p['id']}",
        "kind: decision",
        f"created_at: {p['created_at']}",
        f"hash: sha256:{h}",
        "confidence: validated",
        "reverses: null",
        "superseded_by: null",
        f"tags: [{', '.join(p['tags'])}]",
        f"title: {json.dumps(p['title'], ensure_ascii=False)}",
        "alternatives_considered:",
    ]
    for alt in p["alternatives_considered"]:
        lines.append(f"  - {json.dumps(alt, ensure_ascii=False)}")
    lines.append(f"rationale: {json.dumps(p['rationale'], ensure_ascii=False)}")
    lines.append("constraints_imposed:")
    for c in p["constraints_imposed"]:
        lines.append(f"  - {json.dumps(c, ensure_ascii=False)}")
    lines += [
        "---",
        "",
        f"# {p['title']}",
        "",
        p["body"],
        "",
    ]
    return "\n".join(lines)


def render_finding(ev: dict) -> str:
    p = ev["payload"]
    h = short(ev["hash"][len("sha256:"):])
    lines = [
        "---",
        f"id: {p['id']}",
        "kind: finding",
        f"created_at: {p['created_at']}",
        f"hash: sha256:{h}",
        f"confidence: {p['confidence']}",
        "reverses: null",
        "superseded_by: null",
        f"tags: [{', '.join(p['tags'])}]",
        f"title: {json.dumps(p['title'], ensure_ascii=False)}",
        f"evidence: {json.dumps(p['evidence'], ensure_ascii=False)}",
        f"applies_to: {json.dumps(p['applies_to'], ensure_ascii=False)}",
        "implications:",
    ]
    for impl in p["implications"]:
        lines.append(f"  - {json.dumps(impl, ensure_ascii=False)}")
    lines += [
        "---",
        "",
        f"# {p['title']}",
        "",
        p["body"],
        "",
    ]
    return "\n".join(lines)


def render_task_state(create_ev, status_ev, complete_ev) -> str:
    fm = create_ev["payload"]["frontmatter"]
    consumes = ", ".join(f'"{c}"' for c in fm["consumes"])
    depends = ", ".join(fm["depends_on"])
    lines = [
        f'project: "{PROJECT}"',
        f'last_event: "{complete_ev["id"]}"',
        "phases:",
        f"  {fm['phase']}:",
        f'    name: "{fm["phase_name"]}"',
        "    checkpoint: null",
        "    tasks:",
        f"      - id: {create_ev['payload']['task_id']}",
        f'        title: {json.dumps(create_ev["payload"]["title"], ensure_ascii=False)}',
        "        status: complete",
        f"        risk_level: {fm['risk_level']}",
        f"        depends_on: [{depends}]",
        f"        consumes: [{consumes}]",
        f'        completed_at: "{complete_ev["ts"]}"',
        "",
    ]
    return "\n".join(lines)


def render_active_project(activate_ev) -> str:
    p = activate_ev["payload"]
    activated = p["started_at"][:10]
    lines = [
        "# Active Project",
        "",
        f"**Current:** {p['name']}",
        f"**ID:** {p['project_id']}",
        f"**Path:** projects/{p['project_id']}/PROJECT.md",
        f"**Schema:** {p['schema']}",
        f"**Activated:** {activated}",
        "**Status:** in_progress",
        "",
        "## Quick Context",
        "Reference fixture project: a synthesis run reduced to the smallest "
        "chain that still exercises typed artifacts, citations, and task state.",
        "",
    ]
    return "\n".join(lines)


PROJECT_MD = """\
# PROJECT — golden-demo

Bootstrapped from `schemas/projects/report-synthesis/`.

## Objective

Serve as the substrate's golden reference workspace: the smallest event chain
that still renders typed-artifact, task-state, and lock projections, so
`hw verify` can hold the byte-identical-rendering promise to account.

## Schema

`schemas/projects/report-synthesis/`

## Scope

### Included

- T-001 Synthesize the golden reference note

### Explicitly Excluded

- (none)
"""


# ----------------------------------------------------------- build

def build(out: Path) -> None:
    ch = Chain()

    activate = ch.add(T0, "project.activate", "operator", {
        "project_id": PROJECT,
        "name": "Golden Demo",
        "schema": SCHEMA,
        "started_at": T0,
    })

    ch.add(T1, "bootstrap.probe_skipped", "executor:bootstrap", {
        "schema": SCHEMA,
        "reason": "Reference fixture: corpus is the fixture itself; no external "
                  "surface to probe. Inventory is attested by construction.",
    })

    # Decision DEC-001 — built, hashed, then its projection rendered so its
    # short hash can be cited by the finding that follows.
    dec = ch.add(T2, "decision.add", "executor:T-001", {
        "id": "DEC-001",
        "created_at": T2,
        "title": "Render typed-artifact frontmatter in fixed field order",
        "alternatives_considered": [
            "Emit frontmatter in event-insertion order (rejected: non-deterministic across renderers)",
            "Sort all frontmatter keys alphabetically (rejected: structural-minimum order is load-bearing for readers)",
        ],
        "rationale": "A fixed structural-minimum order followed by schema fields "
                     "is the only rule under which two independent renderers agree "
                     "byte-for-byte, which is the property the fixture pins.",
        "constraints_imposed": [
            "Every artifact projection in this workspace renders id, kind, created_at, hash, confidence, reverses, superseded_by, tags first.",
        ],
        "tags": ["substrate", "projection"],
        "body": "The decision fixes projection frontmatter ordering so the "
                "golden fixture has a single canonical byte sequence per artifact.",
    })
    dec_proj = render_decision(dec)
    dec_short = proj_short_hash(dec_proj)

    # Finding F-001 cites DEC-001 at its current projection short hash.
    dec_citation = f"[DEC-001#{dec_short}]"
    find = ch.add(T3, "finding.add", "executor:T-001", {
        "id": "F-001",
        "created_at": T3,
        "title": "Byte-identical projection rendering is testable, not merely assertable",
        "evidence": f"This workspace: regenerating any projection from "
                    f"events.jsonl reproduces the bytes recorded in hashes.json; "
                    f"hw verify reports zero projection_drift. Anchored by {dec_citation}.",
        "confidence": "provisional",
        "applies_to": "projects/golden-demo/decisions/* and findings/*",
        "implications": [
            f"A renderer that diverges from {dec_citation} produces projection_drift, "
            "so the promise is enforced by replay, not by trust.",
        ],
        "tags": ["substrate", "verification"],
        "body": "The finding records that the rendering promise of "
                "core/TYPED-ARTIFACTS.md is now checkable against a fixed reference, "
                f"consuming {dec_citation} as its anchor.",
    })
    find_proj = render_finding(find)
    find_short = proj_short_hash(find_proj)

    # Task T-001 — created consuming DEC-001, advanced to in_progress, completed.
    create = ch.add(T4, "task.create", "planner", {
        "task_id": "T-001",
        "title": "Synthesize the golden reference note",
        "frontmatter": {
            "phase": 1,
            "phase_name": "Foundation",
            "risk_level": "standard",
            "depends_on": [],
            "consumes": [dec_citation],
        },
    })
    ch.add(T5, "task.status", "executor:T-001", {
        "task_id": "T-001", "from": "pending", "to": "in_progress",
    })
    complete = ch.add(T6, "task.complete", "executor:T-001", {
        "task_id": "T-001",
        "completion_report_path": "projects/golden-demo/tasks/T-001/completion-report.md",
    })

    task_state = render_task_state(create, None, complete)
    active = render_active_project(activate)

    # ------- write everything
    ws = out
    hw = ws / ".hyperworker"

    events_text = "".join(
        json.dumps(ev, ensure_ascii=False, separators=(",", ":")) + "\n"
        for ev in ch.events
    )
    write_text(hw / "events.jsonl", events_text)

    projections = {
        f"projects/{PROJECT}/decisions/DEC-001.md": dec_proj,
        f"projects/{PROJECT}/findings/F-001.md": find_proj,
        f"projects/{PROJECT}/TASK-STATE.yaml": task_state,
        "projects/active_project.md": active,
    }
    hashes = {}
    for rel, text in projections.items():
        write_text(ws / rel, text)
        hashes[rel] = "sha256:" + proj_short_hash(text)

    write_text(hw / "hashes.json",
               json.dumps(hashes, indent=2, ensure_ascii=False) + "\n")
    write_text(ws / "projects" / PROJECT / "PROJECT.md", PROJECT_MD)

    print(f"Golden fixture written to {ws}")
    print(f"  events:      {len(ch.events)}")
    print(f"  projections: {len(projections)}")
    print(f"  DEC-001 short: {dec_short}   F-001 short: {find_short}")
    print(f"\nVerify with:\n  python tools/hw-verify.py --workspace {ws}")


def main():
    ap = argparse.ArgumentParser(description="Generate the HyperWorker golden fixture.")
    ap.add_argument("--out", default=str(Path(__file__).parent / "fixtures" / "golden-workspace"))
    args = ap.parse_args()
    build(Path(args.out).resolve())


if __name__ == "__main__":
    main()
