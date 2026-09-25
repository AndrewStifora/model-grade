# Keeping model-grade current when Anthropic ships a model

The skill is only as good as its picture of the model lineup. This is the maintainer's checklist. Steps 1 and 2 are automated; the rest is judgment, so do it in a session on a strong model (Opus or Fable), not in the Sonnet turn the skill itself runs on.

## 1. Detect

```
python scripts/refresh_docs.py
```

Reports NEW pages (a new model's prompting page, overview, or what's-new page appears in the docs index automatically) and CHANGED pages, with a diff for each under `references/docs-cache/changes/`. Exit code 3 means there is something to read. `/mg refresh` runs the same script from inside Claude Code. A weekly scheduled task that runs it and messages you on exit code 3 is the cheapest early warning.

## 2. Read

For a new model, read its prompting page, its overview (ID, price, context, output limit, default effort, thinking mode), and its what's-new page (breaking API changes, classifiers, fallback). For a changed page, read the diff. Write down, in one line each: what the model is documented to be best at, how its effort levels compare to the previous model in its tier, what it refuses, and what it costs.

## 3. Decide the tier

Ask, in this order:

- Same price or cheaper than the current model in its tier, and documented as at least as good on that tier's workloads? It replaces the tier's model. Keep the old one only where the new one has a documented gap (a classifier, a missing feature, a platform).
- More expensive? Compare cost per completed task, not per token: the docs usually state an effort-level equivalence ("at medium matches the old model at high"). A stronger model at a lower effort is often the cheaper cell.
- A new tier (a model priced between two existing tiers)? Adding a tier touches the schema, the grader's maps, and every eval label. Do it only when the model does not simply replace an existing one.

## 4. Edit, in this order

1. `references/model-profiles.md`: price table row, a section for the model with quoted strengths, effort notes, constraints, and the "cross-model equivalences" list.
2. `references/rubric.md`: hard constraints (classifiers, context limits, features), the tier table, the per-tier effort notes, the cross-tier check, and the worked examples. Change rules only where a sentence in the docs supports the change; quote it in the profile.
3. `scripts/verdict_schema.json`: model enums (two places).
4. `scripts/grade.py`: `ALIAS_TO_ID`, `ID_TO_ALIAS`, `TIER`, `DISPLAY`.
5. `assets/agents/`: add a pinned executor only if the Claude Code alias does not resolve to the model yet (check with `claude -p "OK" --model <alias> --output-format json` and read `modelUsage`).
6. `evals/evals.json`: update `models` and `effort_ok` for the affected tier; add one eval for anything the docs say the model is newly good at.
7. `SKILL.md` description and `README.md` model list, `references/sources.md`, `CHANGELOG.md`, `VERSION`.

## 5. Verify and publish

```
python scripts/refresh_docs.py --write
python evals/run_evals.py --workers 3
```

The with-rubric pass rate should stay at or near 100% and the no-rubric baseline should stay clearly below it; read any eval that moved. Then open a pull request for the change (issue first, branch `feat/<issue>-<model>`). Once CI is green and it is merged, tag `main` with the version and push the tag: `git switch main`, `git pull`, `git tag v1.2.0`, `git push origin v1.2.0`. The release workflow publishes the zip; tell users to run `/mg update`.

## What changes rarely

The signals in rubric section 1, the dependencies rules in 1b, and the tie-break in section 6 describe tasks, not models. They should survive most releases untouched. If a release makes you want to change them, write down why in the changelog.
