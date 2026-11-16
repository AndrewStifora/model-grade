# Sources and provenance

Every routing fact in `model-profiles.md` and `rubric.md` comes from the pages below. `sources.json` is the machine-readable manifest with a SHA-256 hash and fetch date per page; `scripts/refresh_docs.py` keeps it current and discovers new pages from https://platform.claude.com/llms.txt. Each page serves raw Markdown at its URL with `.md` appended. The pages themselves are cached locally in `docs-cache/` (git-ignored, they are Anthropic's text); the repository stores only the hashes. `scripts/check_quotes.py` checks every passage the two files quote against that cache.

Last full refresh: 2026-11-15.

## Anthropic prompt-engineering category

| Page | URL |
|---|---|
| Prompt engineering overview | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview |
| Prompting best practices | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices |
| Prompting Claude Fable 5.2 (added 2026-11-15) | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-2 |
| Prompting Claude Fable 5.1 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1 |
| Prompting Claude Fable 5 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5 |
| Prompting Claude Opus 5.5 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5 |
| Prompting Claude Opus 5 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5 |
| Prompting Claude Opus 4.8 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8 |
| Prompting Claude Sonnet 5.5 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5 |
| Prompting Claude Sonnet 5 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5 |
| Prompting Claude Haiku 5.5 (added 2026-11-15) | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-haiku-5-5 |

## Model pages (IDs, prices, limits, breaking changes)

| Page | URL |
|---|---|
| Claude Fable 5.2 overview (added 2026-11-15) | https://platform.claude.com/docs/en/models/fable-5-2/overview |
| What's new in Claude Fable 5.2 (added 2026-11-15) | https://platform.claude.com/docs/en/models/fable-5-2/whats-new-fable-5-2 |
| Claude Opus 5.5 overview | https://platform.claude.com/docs/en/models/opus-5-5/overview |
| What's new in Claude Opus 5.5 | https://platform.claude.com/docs/en/models/opus-5-5/whats-new-opus-5-5 |
| Claude Sonnet 5.5 overview | https://platform.claude.com/docs/en/models/sonnet-5-5/overview |
| What's new in Claude Sonnet 5.5 | https://platform.claude.com/docs/en/models/sonnet-5-5/whats-new-sonnet-5-5 |
| Claude Haiku 5.5 overview (added 2026-11-15) | https://platform.claude.com/docs/en/models/haiku-5-5/overview |
| What's new in Claude Haiku 5.5 (added 2026-11-15) | https://platform.claude.com/docs/en/models/haiku-5-5/whats-new-haiku-5-5 |
| Claude Sonnet 5 and Claude Opus 5 overviews (fallbacks, legacy) | https://platform.claude.com/docs/en/models/sonnet-5/overview, https://platform.claude.com/docs/en/models/opus-5/overview |

The refresh script also tracks every other model's overview and what's-new page it finds in the docs index, so a new release shows up as NEW on the next run.

## Measurements and model choice (added 2026-11-15)

These pages are not under the two paths the script discovers, so they are tracked by URL in `sources.json`.

| Page | What it supplies | URL |
|---|---|---|
| Optimizing for cost and intelligence | Cost per solved task by model and effort, the research and defect-search comparisons, the re-run-on-failure policy, the upgrade ladder | https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence |
| Choosing the right model | The model-selection matrix and the two ways to pick a starting model | https://platform.claude.com/docs/en/about-claude/models/choosing-a-model |
| Effort | Recommended effort levels per model and what effort changes | https://platform.claude.com/docs/en/build-with-claude/effort |
| Claude Code model configuration | Which Claude Code version moved each alias, the effort defaults in Claude Code, subagent model resolution | https://code.claude.com/docs/en/model-config |

Until 1.5.0 the measured figures came from the cost-optimization guide bundled with Claude Code's `claude-api` skill. That guide now points to the first page above for current numbers, so the profiles quote the page directly.

## Supplementary

- Skill and subagent frontmatter (`model`, `effort`, `context: fork`, `omitClaudeMd`) and how subagents run: https://code.claude.com/docs/en/skills and https://code.claude.com/docs/en/sub-agents.

## Refreshing

See `UPDATING.md`. In short: `python scripts/refresh_docs.py` to detect, read the diffs, edit the profiles and rubric, update the schema and grader maps, adjust the eval labels, then `python scripts/refresh_docs.py --write`, `python scripts/check_quotes.py`, and `python evals/run_evals.py`.
