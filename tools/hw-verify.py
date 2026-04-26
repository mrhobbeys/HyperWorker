#!/usr/bin/env python3
"""
hw-verify.py — Reference implementation of the `hw verify` agent protocol.

Replays the event log, recomputes hashes, validates the chain, and checks every
projection hash and citation. Implements the algorithm specified in
core/SUBSTRATE.md §`hw verify`.

Usage:
    python tools/hw-verify.py --workspace <path>
    python tools/hw-verify.py --workspace <path> --since EV-0042

Exits 0 on PASS, 1 on FAIL. Untracked-projection and stale-citation findings
are reported as warnings; they do not change the exit code.

This is a reference implementation. Agents may reimplement the algorithm in
their environment, but the canonical serialization and citation rules in
core/SUBSTRATE.md are authoritative — divergence from those rules is a bug.
"""

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

CITATION_RE = re.compile(r"\[([A-Z]+)-(\d{3,})#([0-9a-f]{12})\]")
ARTIFACT_DIRS = ("decisions", "findings", "anti-patterns", "operating-reality",
                 "sources", "claims", "contradictions")
ZERO_HASH = "0" * 64
ZERO_HASH_PREFIXED = "sha256:" + ZERO_HASH


def canonical_serialize(obj) -> bytes:
    """Canonical JSON serialization for hashing. See SUBSTRATE.md §Canonical Serialization."""
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def event_hash(event: dict) -> str:
    """Recompute an event's hash from its content (excluding the hash field)."""
    canonical = {k: v for k, v in event.items() if k != "hash"}
    return sha256_hex(canonical_serialize(canonical))


def short_hash(full_hex: str) -> str:
    return full_hex[:12]


def normalize_recorded_hash(recorded: str) -> str:
    """Strip optional `sha256:` prefix to get bare hex."""
    if recorded.startswith("sha256:"):
        return recorded[len("sha256:"):]
    return recorded


def projection_short_hash(path: Path) -> str:
    return short_hash(sha256_hex(path.read_bytes()))


def collect_citations(payload) -> list:
    """Extract all citations from a payload (recursively walks dicts/lists/strings)."""
    found = []

    def walk(obj):
        if isinstance(obj, str):
            for match in CITATION_RE.finditer(obj):
                found.append((f"{match.group(1)}-{match.group(2)}", match.group(3)))
        elif isinstance(obj, dict):
            for value in obj.values():
                walk(value)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(payload)
    return found


def find_projection_path(workspace: Path, artifact_id: str, hashes_index: dict) -> Path | None:
    """Locate a projection file for an artifact ID. Prefer hashes.json, else search."""
    for projection_path in hashes_index:
        if Path(projection_path).stem == artifact_id:
            candidate = workspace / projection_path
            if candidate.exists():
                return candidate
    for projects_dir in (workspace / "projects").glob("*/"):
        for sub in ARTIFACT_DIRS:
            candidate = projects_dir / sub / f"{artifact_id}.md"
            if candidate.exists():
                return candidate
    return None


def verify(workspace: Path, since: str | None) -> dict:
    events_path = workspace / ".hyperworker" / "events.jsonl"
    hashes_path = workspace / ".hyperworker" / "hashes.json"

    result = {
        "events_scanned": 0,
        "tamper": [],
        "chain_breaks": [],
        "projection_drift": [],
        "missing_projections": [],
        "untracked_projections": [],
        "broken_citations": [],
        "stale_citations": [],
        "result": "PASS",
    }

    if not events_path.exists():
        result["result"] = "FAIL"
        result["error"] = f"events.jsonl not found at {events_path}"
        return result

    events = []
    with events_path.open(encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            events.append(json.loads(line))
    result["events_scanned"] = len(events)

    skip_until = since
    skipping = skip_until is not None
    prev_recorded_hash = ZERO_HASH

    for idx, event in enumerate(events):
        if skipping:
            prev_recorded_hash = normalize_recorded_hash(event["hash"])
            if event["id"] == skip_until:
                skipping = False
            continue

        recomputed = event_hash(event)
        recorded = normalize_recorded_hash(event["hash"])
        if recomputed != recorded:
            result["tamper"].append(event["id"])

        recorded_prev = normalize_recorded_hash(event["prev_hash"])
        if idx == 0 and since is None:
            if recorded_prev != ZERO_HASH:
                result["chain_breaks"].append(event["id"])
        else:
            if recorded_prev != prev_recorded_hash:
                result["chain_breaks"].append(event["id"])

        prev_recorded_hash = recorded

    hashes_index = {}
    if hashes_path.exists():
        try:
            hashes_index = json.loads(hashes_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            result["result"] = "FAIL"
            result["error"] = f"hashes.json is not valid JSON at {hashes_path}"
            return result

    for projection_path, recorded_short in hashes_index.items():
        full_path = workspace / projection_path
        if not full_path.exists():
            result["missing_projections"].append(projection_path)
            continue
        actual_short = projection_short_hash(full_path)
        recorded_short_bare = normalize_recorded_hash(recorded_short)
        if actual_short != recorded_short_bare:
            result["projection_drift"].append(projection_path)

    tracked_paths = {workspace / p for p in hashes_index}
    projects_root = workspace / "projects"
    if projects_root.exists():
        for project_dir in projects_root.iterdir():
            if not project_dir.is_dir():
                continue
            for sub in ARTIFACT_DIRS:
                sub_dir = project_dir / sub
                if not sub_dir.exists():
                    continue
                for projection in sub_dir.glob("*.md"):
                    if projection not in tracked_paths:
                        result["untracked_projections"].append(
                            str(projection.relative_to(workspace)).replace("\\", "/")
                        )

    artifact_short_hashes = {}
    for projection_path in hashes_index:
        artifact_id = Path(projection_path).stem
        artifact_short_hashes[artifact_id] = normalize_recorded_hash(hashes_index[projection_path])

    for event in events:
        for artifact_id, cited_short in collect_citations(event.get("payload", {})):
            current = artifact_short_hashes.get(artifact_id)
            if current is None:
                projection = find_projection_path(workspace, artifact_id, hashes_index)
                if projection is None:
                    result["broken_citations"].append(
                        f"[{artifact_id}#{cited_short}] @ {event['id']}"
                    )
                    continue
                current = projection_short_hash(projection)
            if cited_short != current:
                result["stale_citations"].append(
                    f"[{artifact_id}#{cited_short}] @ {event['id']} (current: {current})"
                )

    blocking = (
        result["tamper"]
        or result["chain_breaks"]
        or result["projection_drift"]
        or result["missing_projections"]
        or result["broken_citations"]
    )
    result["result"] = "FAIL" if blocking else "PASS"
    return result


def render(result: dict) -> str:
    lines = [
        "hw verify",
        f"  events_scanned:        {result['events_scanned']}",
        f"  tamper:                {len(result['tamper'])} {result['tamper']}",
        f"  chain_breaks:          {len(result['chain_breaks'])} {result['chain_breaks']}",
        f"  projection_drift:      {len(result['projection_drift'])} {result['projection_drift']}",
        f"  missing_projections:   {len(result['missing_projections'])} {result['missing_projections']}",
        f"  untracked_projections: {len(result['untracked_projections'])} {result['untracked_projections']}",
        f"  broken_citations:      {len(result['broken_citations'])} {result['broken_citations']}",
        f"  stale_citations:       {len(result['stale_citations'])} {result['stale_citations']}",
        f"  result:                {result['result']}",
    ]
    if "error" in result:
        lines.append(f"  error:                 {result['error']}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Reference implementation of `hw verify`.")
    parser.add_argument("--workspace", required=True, type=Path,
                        help="Workspace root containing .hyperworker/")
    parser.add_argument("--since", default=None,
                        help="Skip the chain re-walk for events before this EV-NNNN ID")
    args = parser.parse_args()

    workspace = args.workspace.resolve()
    if not workspace.is_dir():
        print(f"Workspace path is not a directory: {workspace}", file=sys.stderr)
        return 2

    result = verify(workspace, args.since)
    print(render(result))
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
