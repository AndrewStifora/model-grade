# Changelog

## 1.5.0 (2026-11-15)

- Claude Fable 5.2 replaces Fable 5.1 as the tier-3 model (`claude-fable-5-2`, $8 / $40 per million tokens, down from $10 / $50), and Claude Haiku 5.5 replaces Haiku 4.5 at tier 0 (`claude-haiku-5-5`, $0.10 / $0.50 for prompts up to 100K tokens, $0.50 / $2.50 beyond; 1M context; effort levels, default medium). Both old models are now legacy and are no longer routed to. Sonnet 5 and Opus 5 stay as the fallbacks.
- Every verdict now carries an effort level. Haiku 5.5 takes one, so `effort` is no longer `null` for Haiku, the schema requires it, and a `--run` on Haiku uses the `mg-run-<effort>` executors like every other tier.
- Three rules changed because Anthropic's measurements changed, not because a model is new:
  - Research and comparison memos no longer go to Fable at low. On DeepResearch Bench II, Fable 5.2 cost 4.3 times as much as Sonnet 5.5 for no measurable gain and 2.9 times as much as Opus 5.5 for a lower score. They go to Opus 5.5 at medium, with Sonnet 5.5 at high as the cheaper alternative.
  - Code review and bug hunting no longer go to Opus 5.5 at low. On an internal defect-search benchmark it scored 34 points lower at low than at medium, and 13.3 points lower on a research benchmark. Low stays for coding with a checker and for chart reading.
  - For coding, Opus 5.5's effort goes up before the tier does. At high it solved 95.5% of the SWE-bench Pro subset for $0.30 per solved task against Fable 5.2 at low's 94.6% for $0.39, and at xhigh it is level with Fable 5.2 at high for a little over half the cost. Fable 5.2 is for reasoning-3 problems, runs longer than hours, and work Opus 5.5 at high has already failed.
- Haiku 5.5 is a real first attempt, not only a classifier. It scores six points below Sonnet 5.5 on knowledge questions (85% against 91%) at a tenth of the cost per correct answer, and it passed 93% of a Managed Agents task set where Haiku 4.5 passed 62%. Tier 0 now covers anything a checker or a reviewer will catch, and a small tier-1 task with fast tests starts on Haiku 5.5 at medium with Sonnet 5.5 as the re-run. It stays off unchecked answers that matter, image work, and multi-system tool chains.
- New and changed hard constraints: a pipeline that forces `tool_choice` can stay on Haiku 5.5, the one current model that accepts it; an API harness that edits earlier turns cannot use Fable 5.2, which rejects it on every account; the biology, security, and competing-AI constraints now cover Haiku 5.5 and Fable 5.2; the 200K-context rule for Haiku is gone, replaced by its fivefold price step above 100K prompt tokens; Haiku 5.5 has no server-side fallback, so a refusal there re-runs on Sonnet 5.
- The measured figures now come from Anthropic's Optimizing for cost and intelligence page, which the refresh script tracks together with Choosing the right model, the Effort page, and the Claude Code model configuration page. The cost-optimization guide bundled with the `claude-api` skill, the earlier source, no longer carries the numbers.
- New `scripts/check_quotes.py` checks every passage the rubric and the profiles quote against the cached pages. Its first run found ten quoted passages that no longer matched Anthropic's pages, most of them reworded since September and two removed; all are corrected.
- `CLAUDE_CODE_VERSION` is 2.1.321, the first Claude Code release where `haiku`, `sonnet`, `opus`, and `fable` all reach the models the rubric routes to (`haiku` moved in 2.1.293, `fable` in 2.1.321). The skill also says that a family alias resolves to the session's own model when the session is on that family.
- The grader is now Haiku 5.5 at medium effort, pinned by model ID in `assets/agents/mg-grade.md`, `grade.py`, and the eval runner. It was adopted on the evals: 151 of 151 assertions on its first pass at both medium and high, against 148 of 151 for Sonnet 5 at medium on the same rubric, at about half a cent a grade instead of about 14 cents. Because Haiku 5.5 has safety classifiers of its own, the skill grades inline on the session model when the grader declines a prompt about security or biology.
- Two sentences that were new in this release misled the grader on later passes and were rewritten: mechanical multi-file work with a checker steps down to Sonnet 5.5 at medium instead of Opus 5.5 at low, and a costly, unchecked task at tier 2 raises Opus 5.5's effort instead of moving to Fable 5.2. Final result: 302 of 302 assertions over two runs with the rubric, 267 of 302 without it. See `docs/eval-report.md`.
- Evals: tier-0 and tier-3 labels moved to the new models; the review label drops low effort; the research-memo label moves to Opus 5.5 or Sonnet 5.5; labels can now give acceptable effort levels per model. Four evals added (26 to 29): a forced-tool ticket router, a harness that edits history, a small fix with two-second tests, and an unchecked policy answer.

## 1.4.5 (2026-11-15)

- A grade no longer rewrites your conversation to Sonnet 5's prompt cache (#16). `SKILL.md` pinned `model: claude-sonnet-5` and `effort: medium` without `context: fork`, so Claude Code ran the invoking turn inline on Sonnet 5. Prompt caches are per model, so that turn wrote the whole conversation to a cache that is usually cold, and it read the rubric into the conversation, where every later turn carried it. The skill now stays on the session model and hands the prompt to a new subagent, `mg-grade`, pinned to `claude-sonnet-5` at medium effort with only `Read`, `Glob`, and `Grep`. The grader reads the rubric, the model profiles, and the verdict schema in its own context and returns the verdict.
- Measured with headless runs on a Sonnet 5.5 session: before, the whole session ran on `claude-sonnet-5` and wrote 69.6K tokens to its cache, the session's entire context plus the rubric. After, the session kept its own model, and `claude-sonnet-5` served only the grader, which wrote 24K to 29K tokens however long the conversation was. The saving therefore grows with the conversation; on a conversation shorter than about 50K tokens a grade costs about the same as before.
- `context: fork` was not an option: a forked skill does not see the conversation, and `/mg` with no arguments grades the previous request. The skill resolves that request itself, describes the session in a `<context>` block (session model, the skill that would trigger, tools, project, conversation, attachments), and the grader works from that block, as it already does in the evals.
- In an interactive session Claude Code runs subagents in the background, so the verdict arrives a few seconds after `/mg` instead of in the same turn. `--run` then starts the executor the same way.
- If the grader agent is not listed yet (new agent definitions appear after a short delay or in a new session), the skill grades inline on the session model and says so.
- `check_repo.py` fails if `SKILL.md` or the alias pins `model:` or `effort:`, and checks that `mg-grade` names the same model and effort as `GRADER_MODEL` and the new `GRADER_EFFORT` in `grade.py`. The manifest registers the agent, and `validate` covers it in both layouts.
- Rubric section 1b now says the grader works from the `<context>` block in a session too, and that the session's model is the one named there, not the grader's own. The second sentence fixes a miss the spot check found: on the follow-up eval (23) the grader once took its own model, Sonnet 5, for the session's and stayed on it. With the sentence, eval 23 passed three runs of three, and the other four dependency evals passed.

## 1.4.4 (2026-11-15)

- `/mg` no longer pins a model (#14). The alias set `model: sonnet` and `effort: medium` without `context: fork`, so its one turn, which only calls the `model-grade` skill, ran inline on Sonnet 5.5 (the `sonnet` alias from Claude Code 2.1.284). Prompt caches are per model, so that turn wrote the whole conversation to a usually cold cache, and `model-grade` then wrote it again on Sonnet 5. The alias turn now stays on the session model, whose cache is warm, and `model-grade`'s own pin is the only switch: one full-context cache write per `/mg` instead of two, the same as `/model-grade`. Grades are unchanged.
- An installed `~/.claude/skills/mg/SKILL.md` keeps the old fields until `/mg update` copies the new alias out.

## 1.4.3 (2026-10-07)

- The `--run` executors no longer load twice (#12). Every install puts the whole repository at `~/.claude/skills/model-grade`, `.claude-plugin/plugin.json` included, and since Claude Code 2.1.157 a skills folder holding that manifest loads as the plugin `model-grade@skills-dir`, which registers the seven executors as `model-grade:mg-run-*`. The installers and `update` also copied them into `~/.claude/agents/`, so each executor was listed twice (about 0.8k tokens a turn). They now copy the executors only for a folder without the manifest, and move copies an earlier release left in `~/.claude/agents/` to `~/.claude/model-grade-backups/<timestamp>-agents/`. Other files in `~/.claude/agents/` are left alone.
- Do not disable `model-grade@skills-dir` in `/plugin` to remove the duplicates: it also unloads `/model-grade` and `/mg`.
- The update that installs 1.4.3 is carried out by the previous release's script, so the old copies are moved out on the next update, or right away by running `install.ps1` or `install.sh` from the skill folder.
- `SKILL.md` names the plugin-prefixed executors first and copies `assets/agents/` only when the manifest is missing. `check_repo.py` now checks that the manifest lists every executor and carries the release version. `validate` covers both layouts and a stale copy in `agents/` on Linux and Windows.

## 1.4.2 (2026-09-29)

- The CLI grader now runs with your hooks disabled (`--settings '{"disableAllHooks": true}'`), just as it already runs without built-in tools or MCP servers. Before this, a `UserPromptSubmit` hook's context was added to every grade, so grades and eval results depended on whoever ran them. Each grade also waited for the hooks to start: on a Windows machine with two PowerShell hooks, a session took 6 to 13 s instead of 2 to 3 s. Hooks could act outside the grade too, as when a spoken-summary hook cut off the interactive session's audio on every grade of an eval run. The skill itself and the `--run` executors are unaffected.

## 1.4.1 (2026-09-29)

- The CLI grader no longer drops a verdict after three invalid tool calls. `claude -p --json-schema` returns the verdict through a StructuredOutput tool call, and when a call fails the schema, the grader tries again on the next turn. About four grades in ten need one retry, most often because the grader passed the whole verdict as a single JSON string. `--max-turns 3` allowed three calls, so three invalid calls in a row ended the grade with `error_max_turns` (evals 8 and 25 in the 1.3.0 runs). `grade.py` now allows five calls, which is Claude Code 2.1.284's own limit. If a session still ends without a verdict, it grades once more in a fresh session, because a session that keeps repeating the same invalid call does not recover (eval 25 leaving out `cheaper_alternative`). Reported tokens and cost include both sessions.
- Evals 8 and 25, five runs each with the rubric: 10 of 10 verdicts and 49 of 50 assertions, against 9 of 10 and 45 of 50 before the change. The one miss is eval 25 at xhigh, the known effort miss. The user's hooks and the 1.3.0 schema were ruled out: the same retries happen with hooks disabled and on the 1.2.2 grader.

## 1.4.0 (2026-09-29)

- `/mg update` now ends by checking the Claude Code CLI: it compares `claude --version` with `CLAUDE_CODE_VERSION` (2.1.284, the first release where both the `sonnet` and `opus` aliases reach Sonnet 5.5 and Opus 5.5) and recommends `claude update` when the CLI is older, because an older CLI can send a `--run` to a different model than the verdict names. A missing CLI or an unreadable version only skips the check; it never fails the update. `/mg version` runs the same check.
- The check lives in `scripts/check_claude_code.ps1` and `scripts/check_claude_code.sh`, which also run on their own. The update that installs 1.4.0 is carried out by the previous release's script, so the check first appears on the next update; run `/mg version` to see it now.
- `check_repo.py` validates `CLAUDE_CODE_VERSION`; `validate` covers an older, a current, and a missing CLI on Linux and Windows; `references/UPDATING.md` says when to bump it.

## 1.3.0 (2026-09-28)

- Claude Sonnet 5.5 added as the tier-1 model (`claude-sonnet-5-5`, $2 / $10 per million tokens, the same as Sonnet 5; default effort high; recalibrated effort levels). Sonnet 5, now legacy, stays available as the fallback for work that Sonnet 5.5's `cyber`, `bio`, `frontier_llm`, or `general_harms` classifiers may decline, and for integrations that force `tool_choice`, send `thinking: disabled`, or use `computer_20251124`. Server-side fallback already retries `cyber` and `frontier_llm` declines on Sonnet 5.
- Rubric: new hard constraint for work that builds or trains competing AI models; the security, biology, forced-tool, thinking-disabled, and computer-use constraints now cover Sonnet 5.5; Sonnet 5.5 effort notes from its prompting page (verification at low, check-ins at low and medium, "Think the problem through before you answer." for short structured reasoning at high); cache continuity notes that no other model reads Sonnet 5.5 thinking blocks.
- The grader stays on Sonnet 5 at medium, now pinned by model ID in the skill's frontmatter, in `grade.py` (`GRADER_MODEL`), and in `run_evals.py`, so a Claude Code alias move cannot change it. The CLI backend passes the full model ID. The `sonnet` alias resolves to Sonnet 5.5 from Claude Code 2.1.284 (Sonnet 5 before that), so the pin keeps a `claude update` from switching the grader, and Sonnet 5 fallbacks go through `mg-run-sonnet5`.
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
