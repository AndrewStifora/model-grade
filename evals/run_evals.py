#!/usr/bin/env python3
"""Run the model-grade evals.

Grades every labeled prompt in evals.json twice: with the rubric (with_skill) and
without it (without_skill, the baseline), scores both against the labels, and
writes results in the skill-creator workspace layout so its aggregate_benchmark.py
and generate_review.py can consume them.

Usage
  python run_evals.py                          # next iteration, all evals, both configs
  python run_evals.py --ids 1,4,9 --configs with_skill
  python run_evals.py --backend api --runs 2 --workers 4
  python run_evals.py --skill-creator <dir>    # where the skill-creator skill lives

Layout written under <workspace>/iteration-N/ (default workspace: ../../model-grade-workspace)
  eval-<id>-<name>/eval_metadata.json
  eval-<id>-<name>/<config>/run-<k>/outputs/verdict.json   (+ verdict.txt)
  eval-<id>-<name>/<config>/run-<k>/grading.json
  eval-<id>-<name>/<config>/run-<k>/timing.json
  summary.md, and benchmark.json + review.html when skill-creator is found
"""

from __future__ import annotations

import argparse
import concurrent.futures
import glob
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))
import grade as grader  # noqa: E402

EFFORT_RANK = {None: -1, "low": 0, "medium": 1, "high": 2, "xhigh": 3, "max": 4}
CONFIG_RUBRIC = {"with_skill": True, "without_skill": False}


def display(model_id: str) -> str:
    return grader.DISPLAY.get(model_id, model_id)


# ---------------------------------------------------------------- scoring

def score(verdict: dict, expected: dict) -> list[dict]:
    model = verdict["model"]
    effort = verdict.get("effort")
    tier = grader.TIER[model]
    exp_models = expected["models"]
    exp_tiers = [grader.TIER[m] for m in exp_models]
    effort_ok = expected.get("effort_ok", [])
    forbid = expected.get("forbid_models", [])
    evidence = f"verdict: {display(model)} @ {effort or 'n/a'} (confidence {verdict.get('confidence')})"

    exact = model in exp_models
    within = any(abs(tier - t) <= 1 for t in exp_tiers)

    # Effort is judged relative to the expected model. One tier up needs no more
    # effort than expected; one tier down needs at least the expected floor.
    ranks = sorted(EFFORT_RANK[e] for e in effort_ok)
    if exact:
        effort_pass = effort in effort_ok
        effort_note = f"acceptable for {display(exp_models[0])}: {effort_ok}"
    elif within and ranks:
        nearest = min(exp_tiers, key=lambda t: abs(t - tier))
        if tier > nearest:
            effort_pass = EFFORT_RANK[effort] <= ranks[-1]
            effort_note = f"one tier up, so effort must be at most {effort_ok[-1]}"
        else:
            effort_pass = EFFORT_RANK[effort] >= ranks[0]
            effort_note = f"one tier down, so effort must be at least {effort_ok[0]}"
    else:
        effort_pass = False
        effort_note = "model is more than one tier from expected, effort not comparable"

    expectations = [
        {
            "text": f"Picks {' or '.join(display(m) for m in exp_models)}",
            "passed": exact,
            "evidence": evidence,
        },
        {
            "text": "Model is within one tier of the expected model",
            "passed": within,
            "evidence": evidence + f"; expected tier(s) {exp_tiers}, got tier {tier}",
        },
        {
            "text": f"Effort is acceptable ({', '.join(str(e) for e in effort_ok)})",
            "passed": bool(effort_pass),
            "evidence": evidence + "; " + effort_note,
        },
        {
            "text": "Avoids forbidden models (" + ", ".join(display(m) for m in forbid) + ")" if forbid else "No forbidden models for this eval",
            "passed": model not in forbid,
            "evidence": evidence,
        },
        {
            "text": "Gives escalation triggers, or is already at the top tier",
            "passed": tier == 3 or len(verdict.get("escalate_if") or []) > 0,
            "evidence": f"escalate_if has {len(verdict.get('escalate_if') or [])} item(s)",
        },
    ]
    deps_expected = expected.get("dependencies") or []
    if deps_expected:
        found = (verdict.get("signals") or {}).get("dependencies") or []
        expectations.append({
            "text": "Detects dependencies: " + ", ".join(deps_expected),
            "passed": all(d in found for d in deps_expected),
            "evidence": f"signals.dependencies = {found}",
        })
    return expectations


def failed_expectations(expected: dict, reason: str) -> list[dict]:
    texts = [
        f"Picks {' or '.join(display(m) for m in expected['models'])}",
        "Model is within one tier of the expected model",
        f"Effort is acceptable ({', '.join(str(e) for e in expected.get('effort_ok', []))})",
        "Avoids forbidden models",
        "Gives escalation triggers, or is already at the top tier",
    ]
    if expected.get("dependencies"):
        texts.append("Detects dependencies: " + ", ".join(expected["dependencies"]))
    return [{"text": t, "passed": False, "evidence": f"no valid verdict: {reason}"} for t in texts]


# ---------------------------------------------------------------- one run

def run_one(ev: dict, config: str, run_number: int, iter_dir: Path, args) -> dict:
    eval_dir = iter_dir / f"eval-{ev['id']}-{ev['name']}"
    run_dir = eval_dir / config / f"run-{run_number}"
    outputs = run_dir / "outputs"
    outputs.mkdir(parents=True, exist_ok=True)

    metadata = {"eval_id": ev["id"], "eval_name": ev["name"], "prompt": ev["prompt"],
                "assertions": [], "expected": ev["expected"]}
    (eval_dir / "eval_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (run_dir / "eval_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    started = time.time()
    verdict = None
    usage: dict = {}
    error = None
    try:
        verdict, usage = grader.grade(
            ev["prompt"], context=ev.get("context"), rubric=CONFIG_RUBRIC[config],
            backend=args.backend, grader_model=args.grader_model, effort=args.effort,
            timeout=args.timeout,
        )
    except (grader.BackendError, grader.InvalidVerdict, subprocess.TimeoutExpired) as exc:
        error = f"{type(exc).__name__}: {exc}"
    elapsed = time.time() - started

    if verdict is not None:
        (outputs / "verdict.json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")
        (outputs / "verdict.txt").write_text(grader.render(verdict), encoding="utf-8")
        expectations = score(verdict, ev["expected"])
    else:
        (outputs / "error.txt").write_text(error or "unknown error", encoding="utf-8")
        expectations = failed_expectations(ev["expected"], error or "unknown error")

    passed = sum(1 for e in expectations if e["passed"])
    total = len(expectations)
    duration_ms = int(usage.get("duration_ms") or elapsed * 1000)
    total_tokens = sum(int(usage.get(k) or 0) for k in (
        "input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
    timing = {
        "total_tokens": total_tokens,
        "duration_ms": duration_ms,
        "total_duration_seconds": round(duration_ms / 1000, 2),
        "cost_usd": usage.get("cost_usd"),
        "grader_model": usage.get("grader_model"),
        "backend": usage.get("backend"),
    }
    (run_dir / "timing.json").write_text(json.dumps(timing, indent=2), encoding="utf-8")
    grading = {
        "expectations": expectations,
        "summary": {"passed": passed, "failed": total - passed, "total": total,
                    "pass_rate": round(passed / total, 4) if total else 0.0},
        "execution_metrics": {"tool_calls": {}, "total_tool_calls": 0, "total_steps": 1,
                              "errors_encountered": 0 if verdict is not None else 1,
                              "output_chars": len(json.dumps(verdict)) if verdict else 0,
                              "transcript_chars": 0},
        "timing": {"total_duration_seconds": timing["total_duration_seconds"]},
    }
    (run_dir / "grading.json").write_text(json.dumps(grading, indent=2), encoding="utf-8")

    return {"id": ev["id"], "name": ev["name"], "config": config, "run": run_number,
            "verdict": verdict, "error": error, "passed": passed, "total": total,
            "timing": timing, "expected": ev["expected"]}


# ---------------------------------------------------------------- reporting

def write_summary(results: list[dict], iter_dir: Path, evals: list[dict]) -> str:
    by_key = {(r["id"], r["config"], r["run"]): r for r in results}
    configs = sorted({r["config"] for r in results})
    runs = sorted({r["run"] for r in results})
    lines = ["# model-grade eval summary", "",
             f"Iteration: {iter_dir.name}   Runs per config: {len(runs)}", ""]
    header = "| # | eval | expected | " + " | ".join(f"{c} (pass)" for c in configs) + " |"
    lines += [header, "|" + "---|" * (3 + len(configs))]
    totals = {c: [0, 0] for c in configs}
    for ev in evals:
        exp = ev["expected"]
        exp_txt = f"{'/'.join(display(m) for m in exp['models'])} @ {'/'.join(str(e) for e in exp.get('effort_ok', []))}"
        cells = []
        for c in configs:
            parts = []
            for k in runs:
                r = by_key.get((ev["id"], c, k))
                if not r:
                    continue
                totals[c][0] += r["passed"]
                totals[c][1] += r["total"]
                if r["verdict"]:
                    v = r["verdict"]
                    parts.append(f"{display(v['model'])} @ {v.get('effort') or 'n/a'} ({r['passed']}/{r['total']})")
                else:
                    parts.append(f"ERROR ({r['passed']}/{r['total']})")
            cells.append("; ".join(parts) or "-")
        lines.append(f"| {ev['id']} | {ev['name']} | {exp_txt} | " + " | ".join(cells) + " |")
    lines += ["", "## Totals", ""]
    for c in configs:
        p, t = totals[c]
        rate = f"{100 * p / t:.0f}%" if t else "n/a"
        cost = sum((r["timing"].get("cost_usd") or 0) for r in results if r["config"] == c)
        secs = sum(r["timing"]["total_duration_seconds"] for r in results if r["config"] == c)
        lines.append(f"- {c}: {p}/{t} assertions passed ({rate}); {secs:.0f}s total; list-price cost ${cost:.2f}")
    text = "\n".join(lines) + "\n"
    (iter_dir / "summary.md").write_text(text, encoding="utf-8")
    return text


def find_skill_creator(explicit: str | None) -> Path | None:
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    env = os.environ.get("SKILL_CREATOR_DIR")
    if env:
        candidates.append(Path(env))
    candidates.append(Path.home() / ".claude" / "skills" / "skill-creator")
    appdata = os.environ.get("APPDATA")
    if appdata:
        pattern = str(Path(appdata) / "Claude" / "local-agent-mode-sessions" / "skills-plugin" / "*" / "*" / "skills" / "skill-creator")
        candidates += [Path(p) for p in sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)]
    for c in candidates:
        if (c / "scripts" / "aggregate_benchmark.py").exists():
            return c
    return None


def build_benchmark_and_viewer(iter_dir: Path, skill_creator: Path) -> None:
    py = sys.executable
    subprocess.run(
        [py, "-m", "scripts.aggregate_benchmark", str(iter_dir), "--skill-name", "model-grade",
         "--skill-path", str(SKILL_DIR)],
        cwd=str(skill_creator), check=False,
    )
    benchmark = iter_dir / "benchmark.json"
    review = iter_dir / "review.html"
    cmd = [py, str(skill_creator / "eval-viewer" / "generate_review.py"), str(iter_dir),
           "--skill-name", "model-grade", "--static", str(review)]
    if benchmark.exists():
        cmd += ["--benchmark", str(benchmark)]
    subprocess.run(cmd, check=False)
    if review.exists():
        print(f"review page: {review}")


# ---------------------------------------------------------------- main

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--workspace", default=str(SKILL_DIR.parent / "model-grade-workspace"))
    parser.add_argument("--iteration", type=int, help="iteration number (default: next unused)")
    parser.add_argument("--ids", help="comma-separated eval ids to run (default all)")
    parser.add_argument("--configs", default="with_skill,without_skill")
    parser.add_argument("--runs", type=int, default=1, help="runs per configuration")
    parser.add_argument("--backend", choices=["auto", "api", "cli"], default="cli")
    parser.add_argument("--grader-model", default="sonnet")
    parser.add_argument("--effort", default="medium", choices=grader.EFFORTS)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=600, help="seconds per grade")
    parser.add_argument("--skill-creator", help="path to the skill-creator skill for benchmark + viewer")
    parser.add_argument("--no-viewer", action="store_true", help="skip benchmark.json and review.html")
    args = parser.parse_args(argv)

    evals_all = json.loads((HERE / "evals.json").read_text(encoding="utf-8"))["evals"]
    wanted = {int(x) for x in args.ids.split(",")} if args.ids else None
    evals = [e for e in evals_all if wanted is None or e["id"] in wanted]
    configs = [c.strip() for c in args.configs.split(",") if c.strip()]
    for c in configs:
        if c not in CONFIG_RUBRIC:
            parser.error(f"unknown config {c}; choose from {list(CONFIG_RUBRIC)}")

    workspace = Path(args.workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    if args.iteration is None:
        existing = [int(p.name.split("-")[1]) for p in workspace.glob("iteration-*") if p.name.split("-")[1].isdigit()]
        iteration = max(existing, default=0) + 1
    else:
        iteration = args.iteration
    iter_dir = workspace / f"iteration-{iteration}"
    iter_dir.mkdir(parents=True, exist_ok=True)

    jobs = [(ev, c, k) for ev in evals for c in configs for k in range(1, args.runs + 1)]
    print(f"{len(jobs)} grading runs -> {iter_dir}  (backend {args.backend}, grader {args.grader_model} @ {args.effort})")
    results: list[dict] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {pool.submit(run_one, ev, c, k, iter_dir, args): (ev, c, k) for ev, c, k in jobs}
        for fut in concurrent.futures.as_completed(futures):
            ev, c, k = futures[fut]
            r = fut.result()
            results.append(r)
            v = r["verdict"]
            got = f"{display(v['model'])} @ {v.get('effort') or 'n/a'}" if v else f"ERROR {r['error']}"
            print(f"  [{c:13}] {ev['id']:>2} {ev['name']:<28} {r['passed']}/{r['total']}  {got}")

    results.sort(key=lambda r: (r["id"], r["config"], r["run"]))
    print()
    print(write_summary(results, iter_dir, evals))

    if not args.no_viewer:
        sc = find_skill_creator(args.skill_creator)
        if sc:
            build_benchmark_and_viewer(iter_dir, sc)
        else:
            print("skill-creator not found; skipped benchmark.json and review.html (pass --skill-creator <dir>)")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass
    sys.exit(main())
