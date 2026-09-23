# Sources and provenance

Every routing fact in `model-profiles.md` and `rubric.md` comes from the pages below. `sources.json` is the machine-readable manifest with a SHA-256 hash and fetch date per page; `scripts/refresh_docs.py` keeps it current and discovers new pages from https://platform.claude.com/llms.txt. Each page serves raw Markdown at its URL with `.md` appended. The pages themselves are cached locally in `docs-cache/` (git-ignored, they are Anthropic's text); the repository stores only the hashes.

Last full refresh: 2026-09-23.

## Anthropic prompt-engineering category (eight pages)

| Page | URL |
|---|---|
| Prompt engineering overview | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview |
| Prompting best practices | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices |
| Prompting Claude Fable 5.1 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1 |
| Prompting Claude Fable 5 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5 |
| Prompting Claude Opus 5.5 (added 2026-09-23) | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5 |
| Prompting Claude Opus 5 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5 |
| Prompting Claude Opus 4.8 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8 |
| Prompting Claude Sonnet 5 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5 |

## Model pages (IDs, prices, limits, breaking changes)

| Page | URL |
|---|---|
| Claude Opus 5.5 overview | https://platform.claude.com/docs/en/models/opus-5-5/overview |
| What's new in Claude Opus 5.5 | https://platform.claude.com/docs/en/models/opus-5-5/whats-new-opus-5-5 |
| Effort (recommended levels per model) | https://platform.claude.com/docs/en/build-with-claude/effort |

The refresh script also tracks every other model's overview and what's-new page it finds in the docs index, so a new release shows up as NEW on the next run.

## Supplementary

- Cost-optimization guide bundled with Claude Code's `claude-api` skill (`shared/cost-optimization.md`, sections 2.6 and 2.7, and the workload-shape table). Source of the measured effort curves, the re-run-on-failure figures, the Opus 5 versus Fable 5 coding comparison, and the Haiku knowledge-question comparison. It cites Anthropic's cookbook.
- Claude Code model aliases and environment variables: https://code.claude.com/docs/en/model-config. Skill and subagent frontmatter (`model`, `effort`, `context: fork`): https://code.claude.com/docs/en/skills and https://code.claude.com/docs/en/sub-agents.

## Refreshing

See `UPDATING.md`. In short: `python scripts/refresh_docs.py` to detect, read the diffs, edit the profiles and rubric, update the schema and grader maps, adjust the eval labels, then `python scripts/refresh_docs.py --write` and `python evals/run_evals.py`.
