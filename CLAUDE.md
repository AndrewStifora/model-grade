# Working in the model-grade repository

This repository is a Claude Code skill: `SKILL.md` at the root is what runs when someone types `/model-grade` or `/mg`. The folder is installed verbatim at `~/.claude/skills/model-grade`, so everything here ships to users.

## Commands

```
python scripts/check_repo.py                 # compiles, validates JSON, cross-checks labels, maps, agents, version
python evals/run_evals.py --workers 3        # grades all evals with and without the rubric (needs the claude CLI login)
python evals/run_evals.py --ids 4,9,17 --runs 2 --configs with_skill --no-viewer   # a cheap spot check
python scripts/refresh_docs.py               # report NEW and CHANGED Anthropic pages (exit 3 = something to read)
python scripts/refresh_docs.py --write       # accept the current pages into sources.json after the rubric caught up
python scripts/build_package.py --out dist/model-grade-install.zip
```

Eval results land outside the repo in `../model-grade-workspace/iteration-N/` (summary.md, benchmark.json, review.html).

## Rules that keep the pieces consistent

- A rubric or profile change needs a sentence from Anthropic's docs behind it. Quote it in `references/model-profiles.md`; `references/sources.md` and `sources.json` say which pages count.
- The verdict schema (`scripts/verdict_schema.json`), the grader's maps (`ALIAS_TO_ID`, `ID_TO_ALIAS`, `TIER`, `DISPLAY` in `scripts/grade.py`), the executor definitions in `assets/agents/`, and the eval labels in `evals/evals.json` must name the same models. `check_repo.py` enforces it.
- A rubric change is not done until the evals ran: the with-rubric pass rate should stay at or near 100% and the no-rubric baseline clearly below it. Read any eval that moved before deciding the change is right.
- `SKILL.md` runs on Sonnet 5 at medium effort (its frontmatter) and is loaded whole on every invocation. Keep it short; put reasoning in `references/`.
- `references/docs-cache/` is generated and git-ignored. Never commit it, never edit it.
- The `mg` alias lives at `assets/mg/SKILL.md` and the executors at `assets/agents/`; installers and `update` copy them out. Edit them here, not in `~/.claude`.
- For a new model, follow `references/UPDATING.md` in order. Then bump `VERSION`, add a `CHANGELOG.md` section, and tag `vX.Y.Z` to release.

## Things to avoid

- Adding a tier just because a model is new. Most releases replace a tier's model; the schema, the maps, and every label change when a tier is added.
- Hard-coding a Claude Code version's alias resolution. The docs say which version moved an alias; state it, don't assume it.
- Running the full eval set for a one-line wording change; use the spot-check form first.
