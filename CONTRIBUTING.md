# Contributing

Thanks for looking. This skill is small on purpose, and most useful contributions are one of three things: a verdict you disagree with, an eval that captures a case the rubric gets wrong, or the work of folding in a new model. Here is how each one goes.

## Report a verdict you disagree with

Open an issue with the "Verdict disagreement" template. Include the prompt (or a faithful paraphrase), the verdict you got, the verdict you expected, and, if you have it, the sentence in Anthropic's docs that supports your expectation. That last part matters: the rubric only changes where the docs back the change, so a disagreement with a quote is halfway to a fix.

## Propose a rubric change

1. Find the sentence in the docs that supports it and add it, quoted, to `references/model-profiles.md`.
2. Change `references/rubric.md`. Prefer explaining why over adding a rule; the grader is a model reading prose, and it generalizes from reasons better than from imperatives.
3. Add or adjust an eval in `evals/evals.json` so the change is measurable (see below).
4. Run the checks and the evals:

   ```
   python scripts/check_repo.py
   python evals/run_evals.py --workers 3
   ```

   The with-rubric pass rate should stay at or near 100% and the no-rubric baseline should stay clearly below it. Include both numbers in the pull request.

## Add an eval

Each entry in `evals/evals.json` is a realistic prompt with a label:

- `models`: the model IDs that count as the right answer (usually one; two when the docs support both).
- `effort_ok`: the acceptable effort levels for that model (`null` for Haiku).
- `forbid_models`: models that would be a hard-constraint failure.
- `within_one_tier`: `true` when an adjacent tier is acceptable on the lenient assertion.
- `dependencies` (optional): what the grader must detect, from `skill`, `tools`, `project`, `session`.
- `context` (optional): what an in-session grader would see (repo size, available skills, connectors).

Write prompts the way people actually type them: file paths, a little backstory, casual phrasing. Label what the docs justify, not what a bigger model would do better.

## Fold in a new model

Follow `references/UPDATING.md`. It lists the files in the order that keeps the schema, the grader's maps, the executors, and the eval labels consistent. The weekly `docs-check` workflow opens an issue when Anthropic's pages change; that issue is the starting point.

## Housekeeping

- Bump `VERSION` and add a `CHANGELOG.md` section for anything users would notice. Pushing a `vX.Y.Z` tag publishes a release.
- `references/docs-cache/` is generated and git-ignored; never commit it. `references/sources.json` is committed and holds only hashes.
- Keep `SKILL.md` lean. It runs on Sonnet 5 at medium effort, and every line is loaded on every invocation.
- Commit messages: a short imperative summary; mention the eval numbers when the rubric changed.
