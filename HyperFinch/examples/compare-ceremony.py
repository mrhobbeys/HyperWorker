#!/usr/bin/env python3
"""
compare-ceremony.py — side-by-side analysis of two ceremony-cost runs.

Reads two HyperFinch results.jsonl logs (one per model) and emits a markdown
comparison focused on the thinking-layer question: how a small reasoning model
(qwen3-4b-thinking) stacks against a larger near-zero-reasoning model
(gpt-oss-20b) when both operate the HyperWorker harness through the v0.2 tool
loop. Per (model, cell): completion rate, mean score, and median total /
reasoning / completion tokens, tool calls, and seconds.

Usage:
    python examples/compare-ceremony.py \
        --a results/ceremony-cost-gptoss20b/results.jsonl --a-label gpt-oss-20b \
        --b results/ceremony-cost-qwen4b/results.jsonl     --b-label qwen3-4b-thinking
"""

import argparse
import json
import statistics
from pathlib import Path

CELL_ORDER = ["baseline", "prompt=ceremony-full.md", "prompt=ceremony-none.md"]
CELL_LABEL = {
    "baseline": "lightweight",
    "prompt=ceremony-full.md": "full-protocol",
    "prompt=ceremony-none.md": "no-harness",
}


def load(path: Path) -> list:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def med(xs):
    return int(statistics.median(xs)) if xs else 0


def cell_stats(rows: list, cell: str) -> dict:
    rs = [r for r in rows if r.get("cell") == cell]
    valid = [r for r in rs if r.get("valid")]
    completed = [r for r in valid if (r.get("checks") or {}).get("completed")]
    return {
        "n": len(rs),
        "valid": len(valid),
        "invalid": len(rs) - len(valid),
        "completion_rate": (len(completed) / len(valid)) if valid else 0.0,
        "mean_score": (statistics.mean([r.get("score", 0.0) for r in valid])
                       if valid else 0.0),
        "med_tokens": med([r.get("tokens", 0) for r in valid]),
        "med_reasoning": med([r.get("reasoning_tokens", 0) for r in valid]),
        "med_completion": med([r.get("completion_tokens", 0) for r in valid]),
        "med_tool_calls": med([r.get("tool_calls", 0) for r in valid]),
        "med_seconds": med([r.get("seconds", 0) for r in valid]),
    }


def render(a_rows, a_label, b_rows, b_label) -> str:
    out = ["# Ceremony-Cost — model comparison",
           "",
           f"**A = {a_label}** vs **B = {b_label}**. Same task, prompts, axes, and "
           "structural checks; only the model differs. The contrast isolates the "
           "thinking layer.",
           "",
           "## Per-cell (median over valid trials)",
           "",
           "| Model | Cell | n | compl. rate | mean score | tokens | reasoning | "
           "completion | tool calls | sec |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for label, rows in ((a_label, a_rows), (b_label, b_rows)):
        for cell in CELL_ORDER:
            s = cell_stats(rows, cell)
            if s["n"] == 0:
                continue
            inv = f" (+{s['invalid']} invalid)" if s["invalid"] else ""
            out.append(
                f"| {label} | {CELL_LABEL.get(cell, cell)} | {s['valid']}{inv} | "
                f"{s['completion_rate']*100:.0f}% | {s['mean_score']:.3f} | "
                f"{s['med_tokens']} | {s['med_reasoning']} | {s['med_completion']} | "
                f"{s['med_tool_calls']} | {s['med_seconds']:.0f} |")

    out += ["", "## Thinking-layer cost", ""]
    for label, rows in ((a_label, a_rows), (b_label, b_rows)):
        valid = [r for r in rows if r.get("valid")]
        comp = sum(r.get("completion_tokens", 0) for r in valid)
        reas = sum(r.get("reasoning_tokens", 0) for r in valid)
        pct = (reas / comp * 100) if comp else 0.0
        out.append(f"- **{label}:** {reas} reasoning / {comp} completion tokens "
                   f"across {len(valid)} valid trials = **{pct:.0f}% of output is "
                   f"reasoning**.")

    out += ["",
            "## Ceremony overhead (full − none, median total tokens)", ""]
    for label, rows in ((a_label, a_rows), (b_label, b_rows)):
        full = cell_stats(rows, "prompt=ceremony-full.md")["med_tokens"]
        none = cell_stats(rows, "prompt=ceremony-none.md")["med_tokens"]
        light = cell_stats(rows, "baseline")["med_tokens"]
        mult = (full / none) if none else float("inf")
        out.append(f"- **{label}:** none={none}, lightweight={light}, full={full} "
                   f"→ full is **{mult:.1f}×** the no-harness floor.")
    out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--a-label", default="A")
    ap.add_argument("--b", required=True)
    ap.add_argument("--b-label", default="B")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    text = render(load(Path(args.a)), args.a_label,
                  load(Path(args.b)), args.b_label)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8", newline="")
        print(f"wrote {args.out}")
    print(text)


if __name__ == "__main__":
    main()
