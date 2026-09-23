# model-grade

![model-grade: the right Claude for the job](docs/social-preview.png)

[![validate](https://github.com/AndrewStifora/model-grade/actions/workflows/validate.yml/badge.svg)](https://github.com/AndrewStifora/model-grade/actions/workflows/validate.yml)
[![release](https://img.shields.io/github/v/release/AndrewStifora/model-grade?label=release)](https://github.com/AndrewStifora/model-grade/releases)
[![license](https://img.shields.io/github/license/AndrewStifora/model-grade)](LICENSE)

A Claude Code skill that grades a prompt and picks the cheapest Claude model and effort level that will complete it well, so Opus or Fable is never committed to work that Sonnet or Haiku can do. Type `/mg` in front of any request and you get a verdict: the model, the effort level, why, a cheaper alternative worth trying, and what would mean you should step up. Add `--run` and it executes the request on that model.

Built from Anthropic's prompt-engineering and model pages (see `references/sources.md`), with a rubric that quotes them. Version in `VERSION`, history in `CHANGELOG.md`.

[Install](#install) · [Use it](#use-it) · [How well does it work?](docs/eval-report.md) · [Keeping it current](#keeping-it-current) · [Contributing](CONTRIBUTING.md) · [Report a bug](https://github.com/AndrewStifora/model-grade/issues/new/choose)

## What it does

- Scores the prompt on scope, horizon, ambiguity, reasoning depth, verification available, cost of error, context size, modality, domain flags, output shape, and volume, and checks what it depends on beyond its own text: a skill that would trigger, connectors or tools, project context, or the conversation.
- Applies the documented hard constraints: Haiku's 200K window, dense charts and screenshots go to Opus 5.5, biology and dual-use security stay off Fable and Opus 5.5 because of their classifiers, forced tool calls and thinking-disabled pipelines need Opus 5 or Sonnet 5, and so on.
- Picks a tier (Haiku 4.5, Sonnet 5, Opus 5.5, Fable 5.1, with Opus 5 kept only as the classifier fallback) and an effort level (low to max), then runs a cross-tier check: would the stronger model at lower effort be cheaper per completed task? The docs say it often is, and the rubric says when.
- Reports a verdict with a cheaper alternative and concrete escalation triggers, so a cheap first attempt is safe.
- Grades on Sonnet 5 at medium effort: the skill's frontmatter switches the invoking turn to that model, so the grade costs cents.

## Install

Everything installs at the user level, so it works in every project: `~/.claude/skills/model-grade` (this repository), `~/.claude/skills/mg` (the alias, from `assets/mg`), and `~/.claude/agents/mg-run-*.md` (the executors, from `assets/agents`). Pick one route:

- **Drag and drop, no terminal.** Download `model-grade-install.zip` from the [latest release](https://github.com/AndrewStifora/model-grade/releases/latest) (or the repository zip from the green Code button), drag it into a Claude Code chat, and send: `Install the skill package in this zip by following its INSTALL.md exactly.`
- **Scripts.** From a clone or an unzipped copy: `pwsh -File install.ps1` on Windows, `bash install.sh` on macOS or Linux.
- **Git.** `git clone https://github.com/AndrewStifora/model-grade ~/.claude/skills/model-grade`, then run `install.ps1` or `install.sh` once from that folder to place the alias and executors. Later updates are `git pull` or `/mg update`.
- **Plugin (experimental).** `claude plugin marketplace add AndrewStifora/model-grade` then `claude plugin install model-grade@andrewstifora`. The skill, the alias, and the executors load under the `model-grade:` prefix (the bare `/mg` and `/model-grade` still work unless another skill owns those names). Do not combine this with a user-level install of the same skill.

`INSTALL.md` has the full instructions, including the steps Claude follows for the drag-and-drop route.

## Use it

```
/mg Convert the 80 city names in cities.txt to uppercase and save as cities_upper.txt
/mg --json @prompt.txt
/mg --run Add a --dry-run flag to scripts/cleanup.py and run the tests
/mg
/mg update
/mg version
/mg refresh
```

The bare form grades the previous request in the conversation. `--run` hands the prompt to a subagent pinned to the chosen model and effort, then relays the result and escalates once if the executor fails or refuses. `update` pulls or downloads the newest version and refreshes the alias and executors; `version` prints the installed version; `refresh` re-fetches the Anthropic pages and reports what changed. `/model-grade` is the long name of the same skill.

Claude also invokes the skill on its own when you ask which model to use, whether something needs Opus or Fable, or how to save cost on a task.

A verdict looks like this:

```
model-grade -> Opus 5.5 @ medium   (confidence 0.80)
Why: Multi-file feature with a test suite; complexity 2. Opus 5.5 at medium matches Opus 5 at high in fewer tokens.
Cheaper: Sonnet 5 @ high -- when the spec is tight and the suite is trusted; escalate on failure.
Escalate if: the suite still fails after one full pass; the change spreads beyond src/notifications/.
Signals: scope 2 | horizon 2 | ambiguity 1 | reasoning 1 | checker | medium ctx | code | depends on project
```

## How well does it work?

On 24 labeled prompts across all four tiers, the Sonnet 5 grader with the rubric passed 125 of 126 assertions (100% after one rule fix), against 116 of 126 for the same grader without it. The baseline's misses are the ones this skill exists to prevent: Opus for problems that needed Fable, Sonnet for a deep-research memo, Haiku for an unverified script, and high effort on nearly every Opus task where the docs say medium or low holds. Per-prompt results, caveats, and how to reproduce: [docs/eval-report.md](docs/eval-report.md).

## Keeping it current

Anthropic ships models faster than anyone re-reads docs, so the repository watches the docs for you.

- `python scripts/refresh_docs.py` (or `/mg refresh`) reads the docs index, tracks every prompt-engineering page and every model overview and what's-new page, hashes them against `references/sources.json`, and reports NEW and CHANGED pages with diffs. A new model shows up by itself.
- The `docs-check` workflow runs that script every Monday and opens (or updates) an issue when something changed.
- `references/UPDATING.md` is the checklist for turning a new model page into rubric, schema, grader, and eval changes, in the order that keeps them consistent.
- Bump `VERSION`, add a `CHANGELOG.md` section, push a `vX.Y.Z` tag, and the `release` workflow publishes the zip. Everyone else runs `/mg update`.

## The grader as a script

`scripts/grade.py` runs the same rubric outside a session, for pipelines and for the evals.

```
python scripts/grade.py "prompt text"                 # Claude API backend (pip install anthropic; ANTHROPIC_API_KEY or `ant auth login`)
python scripts/grade.py --backend cli "prompt text"   # headless `claude -p` backend, uses your Claude Code login
python scripts/grade.py -f prompt.txt --pretty        # readable block
echo "prompt" | python scripts/grade.py - --usage     # verdict plus token usage
```

The API backend calls `claude-sonnet-5` with `output_config.effort = medium`, a JSON-schema structured output, and the rubric in a cached system block. The CLI backend runs `claude -p` with built-in tools and MCP servers disabled, a custom system prompt, and `--json-schema`. The verdict's `model` field is the exact model ID to pass to the API; `effort` is `null` for Haiku, which has no effort parameter.

## Repository layout

```
SKILL.md                the skill; runs on Sonnet 5 at medium (frontmatter)
references/             rubric.md, model-profiles.md, sources.md + sources.json, UPDATING.md
scripts/                grade.py, verdict_schema.json, refresh_docs.py, update.ps1/.sh, check_repo.py, build_package.py
assets/                 mg/SKILL.md (the alias) and agents/ (the executors), installed outside the skill folder
evals/                  evals.json (24 labeled prompts) and run_evals.py
docs/                   eval-report.md, social-preview.py + the images
.claude-plugin/         plugin and marketplace manifests
.github/                validate, docs-check, and release workflows; issue and PR templates
```

## Caveats

- A skill cannot change the session's own model. Without `--run`, the verdict tells you which model to pick in the model menu.
- `--run` executors start without the conversation history and inherit the session's tool definitions, which in an MCP-heavy setup is tens of thousands of cached tokens; for tiny tasks the skill says in-session is cheaper.
- The Claude Code `opus` alias resolves to Opus 5.5 from v2.1.280 and to Opus 5 before that (`claude update`). The verdict names the exact model; `--run` reports which one the alias will actually hit.
- If your organization's model allowlist excludes Sonnet, or auto mode declines the switch, grading runs on the session model. The rubric is the same.
- Fable 5.1 and Opus 5.5 picks come with a note about their safety classifiers; in an API pipeline configure the server-side fallback.

## Contributing and security

Verdict disagreements, new evals, and new-model updates are the most useful contributions; see [CONTRIBUTING.md](CONTRIBUTING.md). For anything security-related, see [SECURITY.md](SECURITY.md).

## License

MIT, see [LICENSE](LICENSE). The rubric quotes short passages from Anthropic's public documentation, which remains Anthropic's; the repository stores hashes of those pages, not copies.
