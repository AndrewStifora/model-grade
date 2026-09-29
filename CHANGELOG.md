# Changelog

## 1.3.0 (2026-09-28)

- Claude Sonnet 5.5 added as the tier-1 model (`claude-sonnet-5-5`, $2 / $10 per million tokens, the same as Sonnet 5; default effort high; recalibrated effort levels). Sonnet 5, now legacy, stays available as the fallback for work that Sonnet 5.5's `cyber`, `bio`, `frontier_llm`, or `general_harms` classifiers may decline, and for integrations that force `tool_choice`, send `thinking: disabled`, or use `computer_20251124`. Server-side fallback already retries `cyber` and `frontier_llm` declines on Sonnet 5.
- Rubric: new hard constraint for work that builds or trains competing AI models; the security, biology, forced-tool, thinking-disabled, and computer-use constraints now cover Sonnet 5.5; Sonnet 5.5 effort notes from its prompting page (verification at low, check-ins at low and medium, "Think the problem through before you answer." for short structured reasoning at high); cache continuity notes that no other model reads Sonnet 5.5 thinking blocks.
- The grader stays on Sonnet 5 at medium, now pinned by model ID in the skill's frontmatter, in `grade.py` (`GRADER_MODEL`), and in `run_evals.py`, so a Claude Code alias move cannot change it. The CLI backend passes the full model ID. On Claude Code 2.1.282 the `sonnet` alias still resolves to Sonnet 5, so `--run` on a Sonnet 5.5 verdict gets Sonnet 5 until the alias moves.
- Executor `mg-run-sonnet5` added (pinned to `claude-sonnet-5` at high) for verdicts that name Sonnet 5 explicitly; a Sonnet 5.5 refusal re-runs there.
- Evals: tier-1 labels moved to Sonnet 5.5; picking a fallback model without a constraint now fails as it does for Opus 5; eval 25 (a claims pipeline that forces `tool_choice`) added. With the rubric: 125 of 126 graded assertions (one grade hit the CLI's turn cap); without it: 112 of 131. A comparison pass with Sonnet 5.5 as the grader scored 129 of 131 at about twice the cost; see `docs/eval-report.md`.

## 1.2.2 (2026-09-25)

- The repository is public, and every change now goes issue, branch, pull request, green CI, squash merge. `main` is protected by a ruleset, and local hooks in `.githooks/` block direct pushes and scan commits for secrets. Enable them in a clone with `git config core.hooksPath .githooks`.
- The install zip and the installers leave out `.githooks/` and `.claude/` (Claude desktop app session worktrees), so neither lands in an installed skill.
- docs: releases are tagged on `main` after the pull request merges (CLAUDE.md, CONTRIBUTING.md, `references/UPDATING.md`); the pull request template links its issue.

## 1.2.1 (2026-09-23)

- Installing or updating over an existing copy now moves the old copy to `~/.claude/model-grade-backups/<timestamp>` instead of `~/.claude/skills/model-grade.bak-<timestamp>`, where Claude Code would load it as a second skill. The installers and updaters also move any such leftover folder from 1.2.0 out of `skills/`, and INSTALL.md's steps for Claude say the same.
- The installers, when run from a clone that already sits at `~/.claude/skills/model-grade` (the git route), no longer move their own folder away; they only place the alias and executors.
- `update.sh` re-runs itself from a temporary copy when started from the installed folder, because Windows refuses to move a folder that holds an open file.
- docs: the GitHub social preview can only be set once the repository is public.

## 1.2.0 (2026-09-23)

- Claude Opus 5.5 added as the tier-2 model (`claude-opus-5-5`, $4 / $20 per million tokens, default effort medium, thinking always on). Opus 5 stays available as the fallback for work that Opus 5.5's biology or dual-use-security classifiers may decline.
- Effort guidance re-based on the Opus 5.5 page: medium is the default and matches or beats Opus 5 at high on coding and knowledge work; low comes close on several coding evaluations; dense-chart reading at low beats Opus 5 at max.
- New subcommands: `update` (pull or download the newest version, refresh the alias and executors), `version`, and `refresh` (re-fetch the Anthropic pages and report what changed).
- `scripts/refresh_docs.py` discovers prompt-engineering and model pages from the docs index, hashes them, and diffs changes; `references/sources.json` is the manifest; `references/UPDATING.md` is the maintainer checklist for a new model.
- Repository layout: the skill folder is the repo root; the `/mg` alias and executors ship under `assets/` and are installed by `install.ps1` / `install.sh` or refreshed by `update`.
- Executor `mg-run-opus5` added (pinned to `claude-opus-5` at high) for verdicts that name Opus 5 explicitly.
- Evals: expectations updated for Opus 5.5; eval 24 (multi-hour migration with subagents) added. Step-down rule tightened: a flaky, slow, or blind checker does not earn it.
- Repository: MIT license, `validate` / `docs-check` / `release` workflows, plugin and marketplace manifests (experimental install path), contributor guide, security policy, issue and pull-request templates, the eval report under `docs/`, and the social preview image with the script that composes it.

## 1.1.0 (2026-09-20)

- Dependencies signal (skill, tools, project, session) with rules in rubric section 1b; five evals covering it.
- `/mg` alias skill with the permission grants an alias turn needs (`Skill(model-grade), Read, Glob, Grep`).
- Grader script caches the rubric prefix on the API backend.

## 1.0.0 (2026-09-20)

- Initial release: rubric, model profiles, verdict schema, Sonnet 5 at medium grader pinned by frontmatter, `--run` routing through `mg-run-*` executors, API and headless-CLI grader script, 18 labeled evals.
