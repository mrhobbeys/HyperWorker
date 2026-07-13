#!/usr/bin/env python3
"""
finch.py — HyperFinch runner v0.1.0

Variation -> measurement -> selection for LLM tasks.
See FINCH.md for the design spec and README.md for usage.

Usage:
    python finch.py run <plan.yaml> [--out results/]

Dependencies: Python 3.9+, pyyaml.
"""

import argparse
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


# ---------------------------------------------------------------- endpoint

def call_endpoint(plan: dict, params: dict, messages: list) -> dict:
    """Return {text, usage} or raise RuntimeError on infrastructure failure."""
    ep = plan["endpoint"]
    if ep["base_url"] == "mock":
        last = messages[-1]["content"]
        text = ("Subject: Mock subject line for cell\n\n"
                "This is the deterministic mock responder. Prompt chars: "
                f"{len(last)}.\n\n```file:out/email.md\nSubject: Mock subject line\n\n"
                "Body of the mock email.\n```\n" + DONE_TOKEN)
        return {"text": text, "usage": {"total_tokens": len(last) // 4}}
    url = ep["base_url"].rstrip("/") + "/chat/completions"
    body = {"model": ep["model"], "messages": messages}
    for k in ("temperature", "max_tokens", "seed", "top_p"):
        if k in params and params[k] is not None:
            body[k] = params[k]
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
        return {"text": data["choices"][0]["message"]["content"],
                "usage": data.get("usage", {})}
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"malformed endpoint response: {e}") from e


def materialize_file_blocks(text: str, ws: Path) -> int:
    n = 0
    for rel, content in FILE_BLOCK_RE.findall(text):
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

def run_checks(plan: dict, response_text: str, ws: Path) -> dict:
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
        else:
            sys.exit(f"unknown check type: {ctype}")
        results[cid] = ok
        total_w += w
        weighted += w if ok else 0.0
    score = (weighted / total_w) if total_w else 0.0
    return {"checks": results, "score": round(score, 4)}


def structural_metrics(ws: Path) -> dict:
    log = ws / ".hyperworker" / "events.jsonl"
    found = list(ws.glob("**/.hyperworker/events.jsonl")) if not log.exists() else [log]
    if not found:
        return {}
    counts = {"events": 0, "layer1_fail": 0, "layer2_fail": 0,
              "task_complete": 0, "council_escalated": 0}
    for line in found[0].read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        counts["events"] += 1
        try:
            kind = json.loads(line).get("kind", "")
        except json.JSONDecodeError:
            continue
        if kind == "verify.layer1.fail":
            counts["layer1_fail"] += 1
        elif kind == "verify.layer2.fail":
            counts["layer2_fail"] += 1
        elif kind == "task.complete":
            counts["task_complete"] += 1
        elif kind == "council.escalated":
            counts["council_escalated"] += 1
    return counts


# ---------------------------------------------------------------- run loop

def run_trial(plan: dict, plan_dir: Path, cell: dict, n: int, out_dir: Path) -> dict:
    trial_dir = out_dir / "trials" / re.sub(r"[^A-Za-z0-9_.=+-]", "_", cell["id"]) / f"t{n}"
    trial_dir.mkdir(parents=True, exist_ok=True)
    ws = make_workspace(trial_dir, plan, plan_dir)
    inputs, params, prompt = apply_overrides(plan, cell, plan_dir)
    (trial_dir / "prompt.md").write_text(prompt, encoding="utf-8")

    record = {"cell": cell["id"], "trial": n, "overrides": cell["overrides"],
              "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "valid": True, "turns": 0, "seconds": 0.0, "tokens": 0}
    messages = [{"role": "user", "content": prompt}]
    transcript, t0 = [], time.time()
    try:
        for turn in range(1, int(plan["budget"]["max_turns"]) + 1):
            result = call_endpoint(plan, params, messages)
            record["turns"] = turn
            record["tokens"] += int(result["usage"].get("total_tokens", 0) or 0)
            transcript.append(result["text"])
            materialize_file_blocks(result["text"], ws)
            if DONE_TOKEN in result["text"] or turn == int(plan["budget"]["max_turns"]):
                break
            messages.append({"role": "assistant", "content": result["text"]})
            messages.append({"role": "user",
                             "content": f"Continue. Emit {DONE_TOKEN} when finished."})
    except RuntimeError as e:
        record["valid"] = False
        record["error"] = str(e)
    record["seconds"] = round(time.time() - t0, 2)

    full_text = "\n\n---\n\n".join(transcript)
    (trial_dir / "response.md").write_text(full_text, encoding="utf-8")
    if record["valid"]:
        record.update(run_checks(plan, full_text, ws))
        structural = structural_metrics(ws)
        if structural and plan["scoring"].get("structural", "auto") != "off":
            record["structural"] = structural
    return record


def render_leaderboard(plan: dict, out_dir: Path):
    rows = []
    results_path = out_dir / "results.jsonl"
    for line in results_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    cells = {}
    for r in rows:
        cells.setdefault(r["cell"], {"scores": [], "invalid": 0})
        if r.get("valid"):
            cells[r["cell"]]["scores"].append(r.get("score", 0.0))
        else:
            cells[r["cell"]]["invalid"] += 1
    ranked = sorted(cells.items(),
                    key=lambda kv: (sum(kv[1]["scores"]) / len(kv[1]["scores"]))
                    if kv[1]["scores"] else -1, reverse=True)
    lines = [f"# Leaderboard — {plan['name']}", "",
             "> Projection of `results.jsonl` (canonical, append-only). "
             "Overlapping spreads mean *no detected difference at this n* — "
             "do not crown a winner from noise.", "",
             "| Cell | n | mean | min | max | invalid |",
             "|---|---|---|---|---|---|"]
    for cid, stats in ranked:
        s = stats["scores"]
        if s:
            lines.append(f"| {cid} | {len(s)} | {sum(s)/len(s):.3f} "
                         f"| {min(s):.3f} | {max(s):.3f} | {stats['invalid']} |")
        else:
            lines.append(f"| {cid} | 0 | – | – | – | {stats['invalid']} |")
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
    print(f"HyperFinch: {plan['name']} — {len(cells)} cells × "
          f"{plan['trials_per_cell']} trials = {total} trials")
    results_path = out_dir / "results.jsonl"
    done = 0
    with results_path.open("a", encoding="utf-8") as fh:
        for cell in cells:
            for n in range(1, int(plan["trials_per_cell"]) + 1):
                record = run_trial(plan, plan_path.parent, cell, n, out_dir)
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
                fh.flush()
                done += 1
                status = f"score={record.get('score')}" if record["valid"] \
                         else f"INVALID ({record.get('error', '?')[:60]})"
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
