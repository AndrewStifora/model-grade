# How well does it work?

The grader is Claude Haiku 5.5 at medium effort, pinned by model ID. The question the evals answer is whether the rubric makes that grader pick the cheapest model and effort that will do the job, measured against 29 labeled prompts that span all four tiers, latent-difficulty cases, documented hard constraints, and prompts that depend on a skill, connectors, a repository, or the conversation.

Every prompt is graded with the rubric and model profiles (`with_skill`) and with only a one-paragraph description of the models (`without_skill`), by the same grader at the same effort. Each verdict is scored on five or six assertions: the exact model, the model within one tier, an acceptable effort level, no forbidden model, escalation triggers present, and, where labeled, the dependencies detected.

## Results (version 1.5.0, 2026-11-15)

| Configuration | Assertions passed | Grading time | List-price cost |
|---|---|---|---|
| Haiku 5.5 at medium, with the rubric (two runs of 29) | 302 of 302 (100%) | 714 s | $0.32 |
| Same grader, without the rubric (two runs of 29) | 267 of 302 (88%) | 463 s | $0.11 |
| Sonnet 5 at medium, with the rubric (the grader until 1.4.5; one run) | 148 of 151 (98%) | 479 s | $4.01 |
| Sonnet 5 at medium, without the rubric (one run) | 137 of 151 (91%) | 353 s | $1.12 |
| Haiku 5.5 at high, with the rubric (one run) | 151 of 151 (100%) | 580 s | $0.08 |

A grade costs about half a cent on Haiku 5.5 and about 14 cents on Sonnet 5, list price. The Haiku 5.5 run at high cost less than the runs at medium, which is probably a prompt-cache effect of running it straight after them; do not read it as high being cheaper.

### Why the grader changed

Haiku 5.5 was tested as the grader because it costs a twentieth of Sonnet 5 per token and its docs name `high` effort for "strict instruction following". On the first pass it scored 151 of 151 at both medium and high, against 148 of 151 for Sonnet 5 on the same rubric. Medium is the pin because it scored the same as high and grades in about 12 seconds instead of 20.

Sonnet 5's three misses were borderline readings, not rule failures: Sonnet 5.5 at medium where the label says low (prompt 3), Haiku 5.5 for the unverified script on the grounds that running it is a check (prompt 5), and Opus 5.5 at high for the whole-product build, reading it as hours of work (prompt 15).

### What the evals changed in the rubric

The first three Haiku 5.5 runs at medium scored 446 of 453. Six of the seven misses came from two sentences that were new in this release, and both were rewritten:

- Prompt 8, a rename across 30 files, went to Opus 5.5 at low in two runs, because the new cheap-first-attempt rule named Opus 5.5 at low for every tier-2 task. Mechanical multi-file work now steps down to Sonnet 5.5 at medium, as it did before 1.5.0.
- Prompt 29, an unchecked legal answer, went to Fable 5.2 in two runs: reasoning 2 put it at tier 2, and the costly-and-unverified rule stepped it up a tier. Anthropic's research benchmark has Fable 5.2 below Opus 5.5, so the step from tier 2 is now one effort level on Opus 5.5, not a move to Fable.

The remaining miss was prompt 3 at Sonnet 5.5 medium, the same borderline as above. After the two rewrites, two full runs scored 302 of 302. The labels were not changed after seeing results.

Read the baseline column as what a capable small model does on its own: it under-routes hard work (Sonnet 5.5 for the multi-file feature, the dashboard screenshot, the financial model, the flaky test, and the multi-hour migration; Opus 5.5 for the deadlock hunt and the whole-product build), and it misses the documented constraints (Opus 5.5 or Sonnet 5.5 for the pipeline that forces `tool_choice`, Sonnet 5.5 for the harness that edits history). The rubric's value is in those constraints and in effort: review and bug hunting at medium rather than low, research on Opus 5.5 rather than Fable 5.2, and Haiku 5.5 only where a checker or a reviewer catches a miss.

## Per prompt

Verdicts are from the two final runs with the rubric and the two runs without it; where two runs differ, both are shown.

| # | Prompt | Expected | With rubric | Without rubric |
|---|---|---|---|---|
| 1 | Classify 300 support tickets into four labels | Haiku 5.5 @ low/medium | Haiku 5.5 @ low | Haiku 5.5 @ medium |
| 2 | Uppercase 80 city names into a file | Haiku 5.5 @ low/medium | Haiku 5.5 @ low | Haiku 5.5 @ low |
| 3 | Extract name, email, company from 40 messy signatures | Haiku 5.5 @ low/medium/high; Sonnet 5.5 @ low | Haiku 5.5 @ low | Haiku 5.5 @ medium |
| 4 | Add a --dry-run flag, run the tests | Haiku 5.5 @ medium/high; Sonnet 5.5 @ low/medium | Haiku 5.5 @ medium | Haiku 5.5 @ medium |
| 5 | Script: revenue per month from a CSV | Sonnet 5.5 @ low/medium | Sonnet 5.5 @ medium | Haiku 5.5 @ medium (missed 1) |
| 6 | Decisions, owners, deadlines from a 40-page transcript | Sonnet 5.5 @ medium/high | Sonnet 5.5 @ medium | Sonnet 5.5 @ medium |
| 7 | Unit tests for the edge cases in a docstring | Sonnet 5.5 @ low/medium; Haiku 5.5 @ medium/high | Haiku 5.5 @ medium | Sonnet 5.5 @ medium |
| 8 | Rename a function across 30 files, keep tests green | Sonnet 5.5 @ low/medium | Sonnet 5.5 @ medium | Sonnet 5.5 @ medium |
| 9 | Implement a spec end to end: migration, service, API, React | Opus 5.5 @ low/medium/high | Opus 5.5 @ medium | Sonnet 5.5 @ high (missed 2) |
| 10 | Review a 1,200-line auth PR for bugs and security issues | Opus 5.5 @ medium/high | Opus 5.5 @ high; Opus 5.5 @ medium | Sonnet 5.5 @ high (missed 1); Opus 5.5 @ high |
| 11 | Which service caused the spike in this dashboard screenshot | Opus 5.5 @ low/medium/high | Opus 5.5 @ high; Opus 5.5 @ medium | Sonnet 5.5 @ high (missed 2) |
| 12 | Three-statement financial model in Excel for the CFO | Opus 5.5 @ medium/high | Opus 5.5 @ high | Sonnet 5.5 @ high (missed 2) |
| 13 | Find policy conflicts across 600K tokens of contracts | Opus 5.5/Fable 5.2 @ medium/high | Opus 5.5 @ high | Opus 5.5 @ high |
| 14 | Rare scheduler deadlock chased for weeks, fix with a regression test | Fable 5.2 @ high/xhigh | Fable 5.2 @ high | Opus 5.5 @ high (missed 1) |
| 15 | Build the whole MVP autonomously from a brief | Fable 5.2 @ high/xhigh | Fable 5.2 @ high | Opus 5.5 @ high (missed 1) |
| 16 | Compare six vector databases on twelve criteria, write a memo | Opus 5.5 @ medium/high; Sonnet 5.5 @ high | Opus 5.5 @ medium | Sonnet 5.5 @ high |
| 17 | A test that fails 1 in 20 runs on CI, passes locally | Opus 5.5 @ medium/high/xhigh | Opus 5.5 @ high | Sonnet 5.5 @ high (missed 1) |
| 18 | Fuzzing harness plus crash triage for an image parser | Opus 5.5/Opus 5 @ high/xhigh | Opus 5.5 @ high | Opus 5.5 @ high; Sonnet 5.5 @ high (missed 1) |
| 19 | Build a 12-slide deck with the slide-design skill | Sonnet 5.5/Opus 5.5 @ medium/high | Sonnet 5.5 @ high | Sonnet 5.5 @ medium |
| 20 | Gmail to Trello to Slack workflow across three connectors | Opus 5.5/Sonnet 5.5 @ medium/high | Opus 5.5 @ medium | Sonnet 5.5 @ medium |
| 21 | Two-line bug fix in a 2,400-file monorepo | Opus 5.5 @ medium/high | Opus 5.5 @ medium | Sonnet 5.5 @ high (missed 1) |
| 22 | Build and query a knowledge graph with a scripted skill | Sonnet 5.5 @ low/medium | Sonnet 5.5 @ medium | Haiku 5.5 @ medium (missed 1); Sonnet 5.5 @ medium |
| 23 | "Do the same for the other three endpoints we discussed" | Sonnet 5.5/Opus 5.5 @ low/medium/high | Opus 5.5 @ high | Sonnet 5.5 @ high; Sonnet 5.5 @ medium |
| 24 | Multi-hour Python 2 to 3 migration with parallel subagents | Opus 5.5 @ medium/high/xhigh | Opus 5.5 @ high | Sonnet 5.5 @ high (missed 2) |
| 25 | Claims pipeline that forces `tool_choice` on every request | Sonnet 5/Opus 5 @ medium/high | Opus 5 @ high | Opus 5.5 @ high (missed 2); Sonnet 5.5 @ high (missed 2) |
| 26 | Ticket router, 50,000 calls a day, forced `tool_choice`, schema validator | Haiku 5.5 @ low/medium | Haiku 5.5 @ low | Haiku 5.5 @ low |
| 27 | Agent harness that edits earlier turns, multi-file refactors | Opus 5 @ medium/high/xhigh | Opus 5 @ high | Sonnet 5.5 @ high (missed 1) |
| 28 | One-function fix with a two-second test file | Haiku 5.5 @ medium/high; Sonnet 5.5 @ low/medium | Haiku 5.5 @ medium | Sonnet 5.5 @ medium; Haiku 5.5 @ medium |
| 29 | GDPR retention answer pasted into a policy unreviewed | Opus 5.5 @ medium/high; Sonnet 5.5 @ high | Opus 5.5 @ high | Opus 5.5 @ high |

Prompts 26 to 29 are new in 1.5.0. They cover a forced `tool_choice` at tier 0 (Haiku 5.5 is the one current model that accepts it), an API harness that edits earlier turns (Fable 5.2 rejects it on every account), a small fix with fast tests (the Haiku-first attempt), and an answer nobody will check (not Haiku, and not Fable either).

## Caveats

- The labels were written alongside the rubric from the same Anthropic pages, so this is a consistency check on the rubric's reading of the docs, not an independent measurement of task outcomes. A verdict you disagree with is worth an issue, with the docs sentence that backs your expectation.
- Runs are few and at one effort level; a verdict can move between runs on genuinely borderline prompts (3, 13, 15, 19, 23, 25). Where the docs support two answers, the label accepts both.
- The evals grade through the headless CLI with the rubric in the prompt and the verdict schema enforced. In a session, the `mg-grade` subagent reads the same files with its own tools and no schema enforcement. Two end-to-end runs of that path returned valid verdicts that matched the rubric's worked examples, but it is not what these numbers measure.
- Costs are list-price equivalents reported by the headless CLI; on a subscription they consume plan quota instead.

## Reproduce

```
python evals/run_evals.py --workers 3
```

Results land in `../model-grade-workspace/iteration-N/` with a `summary.md`, a `benchmark.json`, and a standalone `review.html` that shows every prompt, verdict, and assertion side by side. `python evals/run_evals.py --ids 4,9,17 --runs 2 --configs with_skill --no-viewer` is the cheap spot-check form, and `--grader-model claude-sonnet-5 --effort medium` grades with the previous grader instead.
