#!/usr/bin/env python3
"""
finch.py — HyperFinch runner v0.2.0

Variation -> measurement -> selection for LLM tasks.
See FINCH.md for the design spec and README.md for usage.

v0.2.0 adds the tool-call loop: beyond emitting fenced file blocks, a trial can
drive a real OpenAI tool-calling loop. The built-in `hyperworker` toolset lets a
small model operate a HyperWorker bootstrap — appending hash-chained events,
writing projections, verifying the chain — without hand-rolling SHA-256 (the
harness tool computes the canonical hash, exactly the toolchain-anchor idea from
core/SUBSTRATE.md). Structural metrics from the resulting events.jsonl are
promotable into scoring checks via the new `structural` check type.

Usage:
    python finch.py run <plan.yaml> [--out results/]

Dependencies: Python 3.9+, pyyaml.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("HyperFinch needs pyyaml: pip install pyyaml")

FILE_BLOCK_RE = re.compile(r"```file:([^\n`]+)\n(.*?)```", re.DOTALL)
DONE_TOKEN = "FINCH_DONE"
ZERO_HASH = "sha256:" + "0" * 64


# ---------------------------------------------------------------- plan loading

def load_plan(path: Path) -> dict:
    plan = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(plan, dict) or plan.get("finch") != 1:
        sys.exit(f"{path}: not a HyperFinch v1 flight plan (missing `finch: 1`)")
    for key in ("name", "endpoint", "task", "scoring"):
        if key not in plan:
            sys.exit(f"{path}: plan is missing required key `{key}`")
    plan.setdefault("mode", "one-at-a-time")
    plan.setdefault("trials_per_cell", 3)
    plan.setdefault("params", {})
    plan.setdefault("budget", {})
    plan.setdefault("workspace", {})
    plan.setdefault("axes", [])
    plan.setdefault("tools", None)          # None | "hyperworker" | [tool names]
    plan["budget"].setdefault("max_turns", 1)
    plan["budget"].setdefault("max_seconds_per_trial", 120)
    plan["workspace"].setdefault("copy", [])
    return plan


def expand_cells(plan: dict) -> list:
    """A cell is {id, overrides: [{target, key, value}]}. Baseline first."""
    cells = [{"id": "baseline", "overrides": []}]
    axes = plan["axes"]
    if plan["mode"] == "factorial" and axes:
        combos = [[]]
        for axis in axes:
            combos = [c + [(axis, lvl)] for c in combos for lvl in axis["levels"]]
        cells = []
        for combo in combos:
            cid = "+".join(f"{a['id']}={lvl}" for a, lvl in combo)
            cells.append({"id": cid or "baseline",
                          "overrides": [{"target": a["target"],
                                         "key": a.get("key"),
                                         "value": lvl} for a, lvl in combo]})
    else:  # one-at-a-time
        for axis in axes:
            for lvl in axis["levels"]:
                cells.append({"id": f"{axis['id']}={lvl}",
                              "overrides": [{"target": axis["target"],
                                             "key": axis.get("key"),
                                             "value": lvl}]})
    return cells


# ---------------------------------------------------------------- trial setup

def apply_overrides(plan: dict, cell: dict, plan_dir: Path):
    """Return (inputs, params, prompt_path) with cell overrides applied."""
    inputs = dict(plan["task"].get("inputs") or {})
    params = dict(plan["params"])
    prompt_rel = plan["task"].get("prompt_file")
    for ov in cell["overrides"]:
        if ov["target"] == "input":
            inputs[ov["key"]] = ov["value"]
        elif ov["target"] == "param":
            params[ov["key"]] = ov["value"]
        elif ov["target"] == "prompt_file":
            prompt_rel = ov["value"]
        else:
            sys.exit(f"unknown axis target: {ov['target']}")
    if prompt_rel:
        prompt_text = (plan_dir / prompt_rel).read_text(encoding="utf-8")
    else:
        prompt_text = plan["task"].get("prompt", "")
    for k, v in inputs.items():
        prompt_text = prompt_text.replace("{{" + str(k) + "}}", str(v))
    return inputs, params, prompt_text


def make_workspace(trial_dir: Path, plan: dict, plan_dir: Path) -> Path:
    ws = trial_dir / "workspace"
    ws.mkdir(parents=True, exist_ok=True)
    for item in plan["workspace"]["copy"]:
        src = (plan_dir / item).resolve()
        dst = ws / Path(item).name
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        elif src.is_file():
            shutil.copy2(src, dst)
        else:
            print(f"  warn: workspace.copy item not found: {src}", file=sys.stderr)
    return ws


# ---------------------------------------------------------------- canonical hashing
# Mirrors core/SUBSTRATE.md §Canonical Serialization and tools/hw-verify.py byte
# for byte. The hw_append_event tool relies on this so a model never hand-rolls a
# hash — the divergence core/SUBSTRATE.md warns about cannot happen by tool.

def canonical_serialize(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def event_hash(event: dict) -> str:
    canonical = {k: v for k, v in event.items() if k != "hash"}
    return sha256_hex(canonical_serialize(canonical))


# ---------------------------------------------------------------- hyperworker toolset
# A small set of tools sufficient to operate a bootstrap. Each tool is bounded and
# writes only inside the trial workspace. hw_append_event is the load-bearing one:
# it computes the canonical hash and chains the event, so the model supplies only
# {kind, actor, project, payload} and gets a valid event by construction.

HW_TOOL_SCHEMAS = {
    "hw_read_file": {
        "type": "function",
        "function": {
            "name": "hw_read_file",
            "description": "Read a UTF-8 text file from the trial workspace "
                           "(e.g. a schema, bootstrap-probe.md, or template).",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string",
                                        "description": "Workspace-relative path."}},
                "required": ["path"],
            },
        },
    },
    "hw_list_dir": {
        "type": "function",
        "function": {
            "name": "hw_list_dir",
            "description": "List entries of a directory in the trial workspace.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string",
                                        "description": "Workspace-relative path; '.' for root."}},
                "required": ["path"],
            },
        },
    },
    "hw_append_event": {
        "type": "function",
        "function": {
            "name": "hw_append_event",
            "description": "Append one hash-chained event to "
                           ".hyperworker/events.jsonl. The harness assigns the "
                           "EV-NNNN id, timestamp, prev_hash, and computes the "
                           "canonical SHA-256 hash. You supply kind, actor, "
                           "project, and payload only. Returns the event id and hash.",
            "parameters": {
                "type": "object",
                "properties": {
                    "kind": {"type": "string",
                             "description": "Dotted event kind, e.g. project.activate."},
                    "actor": {"type": "string",
                              "description": "<role>:<id>, e.g. executor:T-001, operator, planner."},
                    "project": {"type": "string",
                                "description": "Project id, or _harness for harness-level events."},
                    "payload": {"type": "object",
                                "description": "Kind-specific structured payload."},
                },
                "required": ["kind", "actor", "project", "payload"],
            },
        },
    },
    "hw_write_file": {
        "type": "function",
        "function": {
            "name": "hw_write_file",
            "description": "Write a UTF-8 text file (a projection or Mutable "
                           "Surface file) into the trial workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Workspace-relative path."},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
    },
    "hw_verify": {
        "type": "function",
        "function": {
            "name": "hw_verify",
            "description": "Replay .hyperworker/events.jsonl, recompute every "
                           "event hash, and check chain integrity. Returns counts "
                           "of tamper and chain_breaks and a PASS/FAIL result.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    "finch_done": {
        "type": "function",
        "function": {
            "name": "finch_done",
            "description": "Signal the task is complete. Call this once when "
                           "finished; the trial loop stops after it.",
            "parameters": {
                "type": "object",
                "properties": {"summary": {"type": "string",
                                           "description": "One-line summary of what was done."}},
                "required": [],
            },
        },
    },
}


def resolve_tools(plan: dict):
    """Return (tool_schemas list, names set) for the plan, or (None, None)."""
    spec = plan.get("tools")
    if not spec:
        return None, None
    if spec == "hyperworker" or spec == ["hyperworker"]:
        names = list(HW_TOOL_SCHEMAS.keys())
    elif isinstance(spec, list):
        names = []
        for n in spec:
            if n not in HW_TOOL_SCHEMAS:
                sys.exit(f"unknown tool in plan.tools: {n!r} "
                         f"(known: {sorted(HW_TOOL_SCHEMAS)})")
            names.append(n)
    else:
        sys.exit(f"plan.tools must be 'hyperworker' or a list of tool names, got {spec!r}")
    return [HW_TOOL_SCHEMAS[n] for n in names], set(names)


class HWToolContext:
    """Executes hyperworker tool calls against one trial workspace. Bounded:
    every path is confined to the workspace; hw_append_event chains and hashes
    so events are valid by construction."""

    def __init__(self, ws: Path):
        self.ws = ws.resolve()
        self.events_path = self.ws / ".hyperworker" / "events.jsonl"
        self.done = False
        self.done_summary = None

    def _safe(self, rel: str) -> Path:
        target = (self.ws / rel).resolve()
        if self.ws != target and self.ws not in target.parents:
            raise ValueError(f"path escapes workspace: {rel}")
        return target

    def execute(self, name: str, args: dict) -> str:
        try:
            fn = getattr(self, f"_t_{name}", None)
            if fn is None:
                return json.dumps({"error": f"unknown tool {name}"})
            return fn(args if isinstance(args, dict) else {})
        except Exception as e:  # tools never crash the trial; they report errors
            return json.dumps({"error": f"{type(e).__name__}: {e}"})

    def _t_hw_read_file(self, args) -> str:
        p = self._safe(str(args.get("path", "")))
        if not p.is_file():
            return json.dumps({"error": "not a file", "path": str(args.get("path"))})
        text = p.read_text(encoding="utf-8")
        if len(text) > 8000:
            text = text[:8000] + "\n...[truncated]"
        return json.dumps({"path": str(args.get("path")), "content": text})

    def _t_hw_list_dir(self, args) -> str:
        p = self._safe(str(args.get("path", ".")))
        if not p.is_dir():
            return json.dumps({"error": "not a directory", "path": str(args.get("path"))})
        entries = sorted(e.name + ("/" if e.is_dir() else "") for e in p.iterdir())
        return json.dumps({"path": str(args.get("path")), "entries": entries})

    def _t_hw_append_event(self, args) -> str:
        kind = args.get("kind")
        actor = args.get("actor")
        project = args.get("project")
        payload = args.get("payload")
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                payload = {"text": payload}
        if not (kind and actor and project) or not isinstance(payload, dict):
            return json.dumps({"error": "kind, actor, project (strings) and "
                                        "payload (object) are required"})
        self.events_path.parent.mkdir(parents=True, exist_ok=True)
        prev_hash = ZERO_HASH
        n = 0
        if self.events_path.exists():
            lines = [ln for ln in self.events_path.read_text(encoding="utf-8").splitlines()
                     if ln.strip()]
            n = len(lines)
            if lines:
                prev_hash = json.loads(lines[-1])["hash"]
        event = {
            "id": f"EV-{n + 1:04d}",
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "kind": kind, "actor": actor, "project": project,
            "payload": payload, "prev_hash": prev_hash,
        }
        event["hash"] = "sha256:" + event_hash(event)
        with self.events_path.open("a", encoding="utf-8", newline="") as fh:
            fh.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
        return json.dumps({"id": event["id"], "hash": event["hash"], "kind": kind})

    def _t_hw_write_file(self, args) -> str:
        p = self._safe(str(args.get("path", "")))
        content = args.get("content", "")
        if not isinstance(content, str):
            content = json.dumps(content, ensure_ascii=False)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8", newline="") as fh:
            fh.write(content)
        return json.dumps({"path": str(args.get("path")),
                           "bytes": len(content.encode("utf-8"))})

    def _t_hw_verify(self, args) -> str:
        if not self.events_path.exists():
            return json.dumps({"result": "FAIL", "error": "no events.jsonl"})
        tamper, chain_breaks = [], []
        prev = "0" * 64
        events = [json.loads(ln) for ln in
                  self.events_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        for ev in events:
            rec = ev.get("hash", "").replace("sha256:", "")
            if event_hash(ev) != rec:
                tamper.append(ev.get("id"))
            recprev = ev.get("prev_hash", "").replace("sha256:", "")
            if recprev != prev:
                chain_breaks.append(ev.get("id"))
            prev = rec
        result = "PASS" if not tamper and not chain_breaks else "FAIL"
        return json.dumps({"events_scanned": len(events), "tamper": tamper,
                           "chain_breaks": chain_breaks, "result": result})

    def _t_finch_done(self, args) -> str:
        self.done = True
        self.done_summary = args.get("summary")
        return json.dumps({"ok": True})


# ---------------------------------------------------------------- endpoint

def _mock_message(messages: list, tools) -> dict:
    """Deterministic mock responder. Without tools: returns file-block text (v0.1
    behavior). With tools: drives a minimal bootstrap so the tool loop is testable
    with no model — turn 1 emits two hw_append_event calls (project.activate +
    bootstrap.probe_skipped), the next turn (after tool results) emits finch_done."""
    if not tools:
        last = messages[-1]["content"]
        text = ("Subject: Mock subject line for cell\n\n"
                "This is the deterministic mock responder. Prompt chars: "
                f"{len(last)}.\n\n```file:out/email.md\nSubject: Mock subject line\n\n"
                "Body of the mock email.\n```\n" + DONE_TOKEN)
        return {"role": "assistant", "content": text}
    saw_tool = any(m.get("role") == "tool" for m in messages)
    if not saw_tool:
        return {
            "role": "assistant", "content": None,
            "tool_calls": [
                {"id": "call_mock_1", "type": "function", "function": {
                    "name": "hw_append_event",
                    "arguments": json.dumps({
                        "kind": "project.activate", "actor": "operator",
                        "project": "mock-demo",
                        "payload": {"project_id": "mock-demo", "name": "Mock Demo",
                                    "schema": "report-synthesis",
                                    "started_at": "2026-06-09T00:00:00Z"}})}},
                {"id": "call_mock_2", "type": "function", "function": {
                    "name": "hw_append_event",
                    "arguments": json.dumps({
                        "kind": "bootstrap.probe_skipped", "actor": "executor:bootstrap",
                        "project": "mock-demo",
                        "payload": {"schema": "report-synthesis",
                                    "reason": "mock responder: no external surface"}})}},
            ],
        }
    return {
        "role": "assistant", "content": "Bootstrap appended; verifying done.",
        "tool_calls": [{"id": "call_mock_done", "type": "function", "function": {
            "name": "finch_done",
            "arguments": json.dumps({"summary": "mock minimal bootstrap"})}}],
    }


def call_endpoint(plan: dict, params: dict, messages: list, tools=None) -> dict:
    """Return {message, usage} or raise RuntimeError on infrastructure failure.
    `message` is the assistant message dict (may carry tool_calls)."""
    ep = plan["endpoint"]
    if ep["base_url"] == "mock":
        msg = _mock_message(messages, tools)
        approx = len(messages[-1].get("content") or "") // 4 + 8
        return {"message": msg, "usage": {"total_tokens": approx}}
    url = ep["base_url"].rstrip("/") + "/chat/completions"
    body = {"model": ep["model"], "messages": messages}
    for k in ("temperature", "max_tokens", "seed", "top_p"):
        if k in params and params[k] is not None:
            body[k] = params[k]
    if tools:
        body["tools"] = tools
        body["tool_choice"] = "auto"
    headers = {"Content-Type": "application/json"}
    api_key = ep.get("api_key")
    if api_key:
        if str(api_key).startswith("$"):
            api_key = os.environ.get(str(api_key)[1:], "")
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, json.dumps(body).encode("utf-8"),
                                 headers=headers)
    timeout = plan["budget"]["max_seconds_per_trial"]
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        raise RuntimeError(f"endpoint failure: {e}") from e
    try:
        return {"message": data["choices"][0]["message"],
                "usage": data.get("usage", {})}
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"malformed endpoint response: {e}") from e


def materialize_file_blocks(text: str, ws: Path) -> int:
    n = 0
    for rel, content in FILE_BLOCK_RE.findall(text or ""):
        rel = rel.strip()
        target = (ws / rel).resolve()
        if ws.resolve() not in target.parents and target != ws.resolve():
            print(f"  warn: refused file block escaping workspace: {rel}",
                  file=sys.stderr)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        n += 1
    return n


# ---------------------------------------------------------------- scoring

def run_checks(plan: dict, response_text: str, ws: Path, structural: dict) -> dict:
    results, weighted, total_w = {}, 0.0, 0.0
    for check in plan["scoring"].get("checks", []):
        cid, ctype = check["id"], check["type"]
        w = float(check.get("weight", 1.0))
        if ctype == "regex":
            ok = re.search(check["pattern"], response_text, re.MULTILINE) is not None
        elif ctype == "contains":
            ok = check["pattern"] in response_text
        elif ctype == "not_contains":
            ok = check["pattern"] not in response_text
        elif ctype == "word_count_max":
            ok = len(response_text.split()) <= int(check["value"])
        elif ctype == "word_count_min":
            ok = len(response_text.split()) >= int(check["value"])
        elif ctype == "file_exists":
            ok = (ws / check["path"]).exists()
        elif ctype == "structural":
            ok = eval_structural_check(check, structural)
        else:
            sys.exit(f"unknown check type: {ctype}")
        results[cid] = ok
        total_w += w
        weighted += w if ok else 0.0
    score = (weighted / total_w) if total_w else 0.0
    return {"checks": results, "score": round(score, 4)}


def eval_structural_check(check: dict, structural: dict) -> bool:
    """A structural check reads a metric from the trial's events.jsonl and tests
    it against min/max/equals. `metric` is one of the named counts (events,
    layer1_fail, layer2_fail, task_complete, council_escalated, recite_reject) or
    `kind:<event.kind>` for an arbitrary event-kind count. Missing log -> 0."""
    metric = check["metric"]
    if metric.startswith("kind:"):
        value = (structural.get("by_kind") or {}).get(metric[len("kind:"):], 0)
    else:
        value = structural.get(metric, 0)
    if "min" in check and value < check["min"]:
        return False
    if "max" in check and value > check["max"]:
        return False
    if "equals" in check and value != check["equals"]:
        return False
    return True


def structural_metrics(ws: Path) -> dict:
    direct = ws / ".hyperworker" / "events.jsonl"
    found = [direct] if direct.exists() else list(ws.glob("**/.hyperworker/events.jsonl"))
    if not found:
        return {}
    counts = {"events": 0, "layer1_fail": 0, "layer2_fail": 0,
              "task_complete": 0, "council_escalated": 0, "recite_reject": 0,
              "by_kind": {}}
    for line in found[0].read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        counts["events"] += 1
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind = ev.get("kind", "")
        counts["by_kind"][kind] = counts["by_kind"].get(kind, 0) + 1
        if kind == "verify.layer1.fail":
            counts["layer1_fail"] += 1
        elif kind == "verify.layer2.fail":
            counts["layer2_fail"] += 1
        elif kind == "task.complete":
            counts["task_complete"] += 1
        elif kind == "council.escalated":
            counts["council_escalated"] += 1
        elif kind == "task.recite" and (ev.get("payload") or {}).get("rejected"):
            counts["recite_reject"] += 1
    return counts


# ---------------------------------------------------------------- run loop

def _assistant_with_tool_calls(msg: dict) -> dict:
    """Normalize an assistant message carrying tool_calls for the next request."""
    return {"role": "assistant", "content": msg.get("content") or "",
            "tool_calls": msg.get("tool_calls") or []}


def _parse_tool_call(tc: dict):
    fn = tc.get("function") or {}
    name = fn.get("name", "")
    call_id = tc.get("id") or f"call_{name}"
    raw = fn.get("arguments")
    if isinstance(raw, dict):
        args = raw
    else:
        try:
            args = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            args = {}
    return name, call_id, args


def run_trial(plan: dict, plan_dir: Path, cell: dict, n: int, out_dir: Path) -> dict:
    trial_dir = out_dir / "trials" / re.sub(r"[^A-Za-z0-9_.=+-]", "_", cell["id"]) / f"t{n}"
    trial_dir.mkdir(parents=True, exist_ok=True)
    ws = make_workspace(trial_dir, plan, plan_dir)
    inputs, params, prompt = apply_overrides(plan, cell, plan_dir)
    (trial_dir / "prompt.md").write_text(prompt, encoding="utf-8")
    tools, _ = resolve_tools(plan)

    record = {"cell": cell["id"], "trial": n, "overrides": cell["overrides"],
              "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "valid": True, "turns": 0, "seconds": 0.0, "tokens": 0,
              "completion_tokens": 0, "reasoning_tokens": 0, "tool_calls": 0}
    messages = [{"role": "user", "content": prompt}]
    transcript, t0 = [], time.time()
    ctx = HWToolContext(ws) if tools else None
    try:
        for turn in range(1, int(plan["budget"]["max_turns"]) + 1):
            result = call_endpoint(plan, params, messages, tools=tools)
            record["turns"] = turn
            usage = result["usage"] or {}
            record["tokens"] += int(usage.get("total_tokens", 0) or 0)
            record["completion_tokens"] += int(usage.get("completion_tokens", 0) or 0)
            det = usage.get("completion_tokens_details") or {}
            record["reasoning_tokens"] += int(det.get("reasoning_tokens", 0) or 0)
            msg = result["message"]
            text = msg.get("content") or ""
            tool_calls = msg.get("tool_calls") or []
            if text:
                transcript.append(text)

            if tools and tool_calls:
                messages.append(_assistant_with_tool_calls(msg))
                for tc in tool_calls:
                    name, call_id, args = _parse_tool_call(tc)
                    record["tool_calls"] += 1
                    out = ctx.execute(name, args)
                    messages.append({"role": "tool", "tool_call_id": call_id,
                                     "content": out})
                materialize_file_blocks(text, ws)
                if ctx.done or DONE_TOKEN in text or turn == int(plan["budget"]["max_turns"]):
                    break
            else:
                materialize_file_blocks(text, ws)
                if DONE_TOKEN in text or turn == int(plan["budget"]["max_turns"]):
                    break
                messages.append({"role": "assistant", "content": text})
                messages.append({"role": "user",
                                 "content": f"Continue. Emit {DONE_TOKEN} when finished."})
    except RuntimeError as e:
        record["valid"] = False
        record["error"] = str(e)
    record["seconds"] = round(time.time() - t0, 2)

    full_text = "\n\n---\n\n".join(transcript)
    (trial_dir / "response.md").write_text(full_text, encoding="utf-8")
    if record["valid"]:
        structural = structural_metrics(ws)
        record.update(run_checks(plan, full_text, ws, structural))
        if structural and plan["scoring"].get("structural", "auto") != "off":
            record["structural"] = {k: v for k, v in structural.items() if v}
    return record


def render_leaderboard(plan: dict, out_dir: Path):
    rows = []
    results_path = out_dir / "results.jsonl"
    for line in results_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    cells = {}
    for r in rows:
        cells.setdefault(r["cell"], {"scores": [], "invalid": 0,
                                     "tokens": [], "reasoning": []})
        if r.get("valid"):
            cells[r["cell"]]["scores"].append(r.get("score", 0.0))
            cells[r["cell"]]["tokens"].append(r.get("tokens", 0))
            cells[r["cell"]]["reasoning"].append(r.get("reasoning_tokens", 0))
        else:
            cells[r["cell"]]["invalid"] += 1
    ranked = sorted(cells.items(),
                    key=lambda kv: (sum(kv[1]["scores"]) / len(kv[1]["scores"]))
                    if kv[1]["scores"] else -1, reverse=True)
    lines = [f"# Leaderboard — {plan['name']}", "",
             "> Projection of `results.jsonl` (canonical, append-only). "
             "Overlapping spreads mean *no detected difference at this n* — "
             "do not crown a winner from noise.", "",
             "| Cell | n | mean | min | max | invalid | med tokens | med reasoning |",
             "|---|---|---|---|---|---|---|---|"]
    for cid, stats in ranked:
        s = stats["scores"]
        if s:
            toks = sorted(stats["tokens"])
            med = toks[len(toks) // 2] if toks else 0
            reas = sorted(stats["reasoning"])
            med_r = reas[len(reas) // 2] if reas else 0
            lines.append(f"| {cid} | {len(s)} | {sum(s)/len(s):.3f} "
                         f"| {min(s):.3f} | {max(s):.3f} | {stats['invalid']} | {med} | {med_r} |")
        else:
            lines.append(f"| {cid} | 0 | – | – | – | {stats['invalid']} | – | – |")
    if len(ranked) >= 2 and ranked[0][1]["scores"] and ranked[1][1]["scores"]:
        top, second = ranked[0], ranked[1]
        gap_real = min(top[1]["scores"]) > max(second[1]["scores"])
        verdict = (f"`{top[0]}` beats `{second[0]}` with non-overlapping spread."
                   if gap_real else
                   "Top cells have overlapping spreads — no detected difference "
                   "at this n. Increase `trials_per_cell` before concluding.")
        lines += ["", f"**Verdict:** {verdict}"]
    lines.append("")
    (out_dir / "LEADERBOARD.md").write_text("\n".join(lines), encoding="utf-8")


def cmd_run(args):
    plan_path = Path(args.plan).resolve()
    plan = load_plan(plan_path)
    out_dir = Path(args.out) / plan["name"]
    out_dir.mkdir(parents=True, exist_ok=True)
    cells = expand_cells(plan)
    total = len(cells) * int(plan["trials_per_cell"])
    tool_note = f" [tools: {plan['tools']}]" if plan.get("tools") else ""
    print(f"HyperFinch: {plan['name']} — {len(cells)} cells × "
          f"{plan['trials_per_cell']} trials = {total} trials{tool_note}")
    results_path = out_dir / "results.jsonl"
    done = 0
    with results_path.open("a", encoding="utf-8") as fh:
        for cell in cells:
            for n in range(1, int(plan["trials_per_cell"]) + 1):
                record = run_trial(plan, plan_path.parent, cell, n, out_dir)
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
                fh.flush()
                done += 1
                if record["valid"]:
                    status = f"score={record.get('score')} tokens={record.get('tokens')}"
                    if record.get("tool_calls"):
                        status += f" tool_calls={record['tool_calls']}"
                else:
                    status = f"INVALID ({record.get('error', '?')[:60]})"
                print(f"  [{done}/{total}] {cell['id']} t{n}: {status}")
    render_leaderboard(plan, out_dir)
    print(f"\nLeaderboard: {out_dir / 'LEADERBOARD.md'}")
    print(f"Raw trials:  {results_path}")


def main():
    ap = argparse.ArgumentParser(prog="finch", description="HyperFinch runner")
    sub = ap.add_subparsers(dest="cmd", required=True)
    runp = sub.add_parser("run", help="run a flight plan")
    runp.add_argument("plan")
    runp.add_argument("--out", default="results")
    runp.set_defaults(func=cmd_run)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
