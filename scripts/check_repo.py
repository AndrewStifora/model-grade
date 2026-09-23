#!/usr/bin/env python3
"""Repository self-check.

Compiles the scripts, validates every JSON file, and cross-checks the pieces that
must agree with each other: the eval labels against the verdict schema's model and
effort lists, the grader's model maps against the schema, the executor definitions
against their file names, and VERSION against CHANGELOG.md. Exit 0 when everything
passes, 1 otherwise. The validate and release workflows run it; run it yourself
before committing a rubric or schema change.
"""

from __future__ import annotations

import json
import py_compile
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

errors: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # invalid JSON or unreadable
        errors.append(f"json: {path.relative_to(ROOT)}: {exc}")
        return None


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not match:
        errors.append(f"frontmatter missing: {path.relative_to(ROOT)}")
        return {}
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


# 1. Everything compiles.
for path in sorted((ROOT / "scripts").glob("*.py")) + sorted((ROOT / "evals").glob("*.py")):
    try:
        py_compile.compile(str(path), doraise=True)
    except py_compile.PyCompileError as exc:
        errors.append(f"compile: {exc}")

# 2. Every JSON file parses.
schema = load_json(ROOT / "scripts" / "verdict_schema.json")
evals = load_json(ROOT / "evals" / "evals.json")
for path in sorted((ROOT / ".claude-plugin").glob("*.json")) if (ROOT / ".claude-plugin").exists() else []:
    load_json(path)
if (ROOT / "references" / "sources.json").exists():
    load_json(ROOT / "references" / "sources.json")

models: set[str] = set(schema["properties"]["model"]["enum"]) if schema else set()
efforts: set = set(schema["properties"]["effort"]["enum"]) if schema else set()
deps: set[str] = set(schema["properties"]["signals"]["properties"]["dependencies"]["items"]["enum"]) if schema else set()

# 3. The grader's maps agree with the schema.
try:
    import grade  # noqa: E402

    check(set(grade.TIER) == models, f"grade.TIER keys {sorted(grade.TIER)} differ from schema models {sorted(models)}")
    check(set(grade.DISPLAY) == models, "grade.DISPLAY keys differ from schema models")
    check(set(grade.ID_TO_ALIAS) == models, "grade.ID_TO_ALIAS keys differ from schema models")
    check(all(m in models for m in grade.ALIAS_TO_ID.values()), "grade.ALIAS_TO_ID points at a model the schema does not list")
except Exception as exc:  # import failure
    errors.append(f"import grade: {exc}")

# 4. Eval labels only use known models, efforts, and dependencies.
if evals:
    ids = [e["id"] for e in evals["evals"]]
    check(len(ids) == len(set(ids)), "duplicate eval ids")
    for e in evals["evals"]:
        expected = e.get("expected", {})
        check(bool(e.get("prompt")), f"eval {e['id']}: empty prompt")
        check(bool(expected.get("models")), f"eval {e['id']}: no expected models")
        for m in expected.get("models", []) + expected.get("forbid_models", []):
            check(m in models, f"eval {e['id']}: unknown model {m}")
        for ef in expected.get("effort_ok", []):
            check(ef in efforts, f"eval {e['id']}: unknown effort {ef!r}")
        for d in expected.get("dependencies", []):
            check(d in deps, f"eval {e['id']}: unknown dependency {d}")

# 5. Skill, alias, and executor frontmatter.
fm = frontmatter(ROOT / "SKILL.md")
check(fm.get("name") == "model-grade", "SKILL.md: name must be model-grade")
check(bool(fm.get("description")), "SKILL.md: description missing")
fm = frontmatter(ROOT / "assets" / "mg" / "SKILL.md")
check(fm.get("name") == "mg", "assets/mg/SKILL.md: name must be mg")
agents = sorted((ROOT / "assets" / "agents").glob("*.md"))
check(len(agents) >= 6, f"expected at least six executor definitions, found {len(agents)}")
for agent in agents:
    fm = frontmatter(agent)
    check(fm.get("name") == agent.stem, f"{agent.name}: frontmatter name differs from file name")
    check(fm.get("effort") in efforts, f"{agent.name}: effort {fm.get('effort')!r} is not a known level")

# 6. Version and changelog agree.
version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
check(re.fullmatch(r"\d+\.\d+\.\d+", version) is not None, f"VERSION {version!r} is not MAJOR.MINOR.PATCH")
check(f"## {version} " in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), f"CHANGELOG.md has no section for {version}")

if errors:
    print("FAIL")
    for message in errors:
        print(" -", message)
    sys.exit(1)
print(f"OK: {len(agents)} executors, {len(evals['evals']) if evals else 0} evals, version {version}")
