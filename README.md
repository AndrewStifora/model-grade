# model-grade

A Claude Code skill that grades a prompt and picks the cheapest Claude model and effort level that will complete it well, so Opus or Fable is never committed to work that Sonnet or Haiku can do. Built from Anthropic's prompt-engineering and model pages (see `references/sources.md`); version in `VERSION`, history in `CHANGELOG.md`.

## What it does

- Reads a prompt and scores it on scope, horizon, ambiguity, reasoning depth, verification available, cost of error, context size, modality, domain flags, output shape, and volume, and checks what it depends on beyond its own text: a skill that would trigger, connectors or tools, project context, or the conversation. Each dependency has documented effects on the verdict (for example, tool-dependent prompts get an effort floor of medium because tool usage falls at low effort).
- Applies documented hard constraints (Haiku's 200K window, dense images go to Opus 5.5, biology and dual-use security stay off Fable and Opus 5.5 because of their classifiers, and so on).
- Picks a tier (Haiku 4.5, Sonnet 5, Opus 5.5, Fable 5.1, with Opus 5 kept only as a classifier fallback) and an effort level (low to max), runs a cross-tier check ("would the stronger model at lower effort be cheaper per completed task?"), and reports a verdict with a cheaper alternative and concrete escalation triggers.
- Grades on Sonnet 5 at medium effort: the skill's frontmatter switches the invoking turn to that model, so the grade itself costs cents.

## Install

Pick one:

- **Drag and drop, no terminal.** Download the repository zip (the green Code button on GitHub, or the copy in the shared Drive folder), drag it into a Claude Code chat, and send: `Install the skill package in this zip by following its INSTALL.md exactly.`
- **Scripts.** From a clone or an unzipped copy: `pwsh -File install.ps1` on Windows, `bash install.sh` on macOS or Linux.
- **Git.** `git clone https://github.com/AndrewStifora/model-grade ~/.claude/skills/model-grade`, then run `install.ps1` or `install.sh` once from that folder to place the alias and executors. Later updates are `git pull` or `/mg update`.

Everything installs at the user level: `~/.claude/skills/model-grade` (this repository), `~/.claude/skills/mg` (the alias, from `assets/mg`), and `~/.claude/agents/mg-run-*.md` (the executors, from `assets/agents`).

## Usage in Claude Code

```
/mg Convert the 80 city names in cities.txt to uppercase and save as cities_upper.txt
/mg --json @prompt.txt
/mg --run Add a --dry-run flag to scripts/cleanup.py and run the tests
/mg
/mg update
/mg version
/mg refresh
```

The bare form grades the previous request in the conversation. `--run` hands the prompt to a subagent pinned to the chosen model and effort, then relays the result and escalates once if the executor fails or refuses. `update` pulls or downloads the newest version and refreshes the alias and executors; `version` prints the installed version; `refresh` re-fetches the Anthropic pages and reports what changed (see "Keeping it current"). `/model-grade` is the long name of the same skill.

Claude will also invoke the skill on its own when you ask which model to use, whether something needs Opus or Fable, or how to save cost on a task.

## The grader as a script

`scripts/grade.py` runs the same rubric outside a session.

```
python scripts/grade.py "prompt text"                 # Claude API backend (pip install anthropic; ANTHROPIC_API_KEY or `ant auth login`)
python scripts/grade.py --backend cli "prompt text"   # headless `claude -p` backend, uses your Claude Code login
python scripts/grade.py -f prompt.txt --pretty        # readable block
echo "prompt" | python scripts/grade.py - --usage     # verdict plus token usage
```

The API backend calls `claude-sonnet-5` with `output_config.effort = medium`, a JSON-schema structured output, and the rubric in a cached system block. The CLI backend runs `claude -p` with built-in tools and MCP servers disabled, a custom system prompt, and `--json-schema`. The verdict's `model` field is the exact model ID to pass to the API; `effort` is `null` for Haiku, which has no effort parameter.

## Keeping it current

Anthropic ships models faster than anyone re-reads docs, so the skill carries its own change detector. `python scripts/refresh_docs.py` (or `/mg refresh`) reads the docs index, tracks every prompt-engineering page and every model overview and what's-new page, hashes them against `references/sources.json`, and prints NEW and CHANGED pages with diffs. Exit code 3 means there is something to read. `references/UPDATING.md` is the checklist for turning a new model page into rubric changes, in the order that keeps the schema, the grader, and the evals consistent. Then bump `VERSION`, note the change in `CHANGELOG.md`, tag, push, and everyone else runs `/mg update`.

## Evals

`evals/evals.json` holds labeled prompts across all four tiers, including latent-difficulty, constraint, and dependency cases. `python evals/run_evals.py` grades each prompt with the rubric (`with_skill`) and without it (`without_skill`), scores both against the labels, and writes results in the skill-creator workspace layout (`../model-grade-workspace/iteration-N/`), plus `benchmark.json` and a standalone review page when the skill-creator scripts are available.

## Caveats

- A skill cannot change the session's own model. Without `--run`, the verdict tells you which model to pick in the model menu.
- `--run` executors start without the conversation history and inherit the session's tool definitions, which in an MCP-heavy setup is tens of thousands of cached tokens; for tiny tasks the skill says in-session is cheaper.
- The Claude Code `opus` alias resolves to Opus 5.5 from v2.1.280 and to Opus 5 before that (`claude update`). The verdict names the exact model; `--run` reports which one the alias will actually hit.
- If your organization's model allowlist excludes Sonnet, or auto mode declines the switch, grading runs on the session model. The rubric is the same.
- Fable 5.1 and Opus 5.5 picks come with a note about their safety classifiers; in an API pipeline configure the server-side fallback.
