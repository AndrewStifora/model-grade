# How well does it work?

The grader is Claude Sonnet 5 at medium effort, pinned by model ID. The question the evals answer is whether the rubric makes that grader pick the cheapest model and effort that will do the job, measured against 25 labeled prompts that span all four tiers, latent-difficulty cases, documented hard constraints, and prompts that depend on a skill, connectors, a repository, or the conversation.

Every prompt is graded twice: once with the rubric and model profiles (`with_skill`) and once with only a one-paragraph description of the models (`without_skill`), by the same grader at the same effort. Each verdict is scored on five or six assertions: the exact model, the model within one tier, an acceptable effort level, no forbidden model, escalation triggers present, and, where labeled, the dependencies detected.

## Results (version 1.3.0, 2026-09-28)

| Configuration | Assertions passed | Time | List-price cost |
|---|---|---|---|
| Sonnet 5 at medium, with the rubric | 125 of 126 graded (99%); 125 of 131 counting one grader error | 392 s | $2.87 |
| Same grader, without the rubric | 112 of 131 (85%) | 334 s | $0.96 |
| Sonnet 5.5 at medium as the grader, with the rubric (comparison only) | 129 of 131 (98%) | 220 s | $5.54 |

One with-rubric grade (prompt 8) returned no verdict: the headless CLI stopped at its three-turn cap (`error_max_turns`), which is a harness failure, not a routing one. A spot check of prompts 8 and 25, two runs each, graded prompt 8 correctly both times (Sonnet 5.5 at low) and prompt 25 as Opus 5 at high on its valid run; the other run hit the same cap. The single graded miss is prompt 25's first run, which picked the right model (Opus 5) at xhigh where the rubric's Opus 5 note says to start at high.

Prompt 25 is new in 1.3.0: a claims pipeline that forces `tool_choice`, which Sonnet 5.5, Opus 5.5, and Fable 5.1 reject. Every valid grade excluded all three, stepped up from Sonnet because approvals go to payment unchecked, and landed on Opus 5, and the notes said that switching the pipeline to `tool_choice: auto` with strict tool use would reopen the newer models.

The Sonnet 5.5 comparison row is there to inform a later grader switch. It passed 129 of 131; both misses sent Fable-level work (the autonomous MVP and the research memo) to Opus 5.5, and it cost nearly twice as much per pass. The grader stays on Sonnet 5 for now.

Read the baseline column as what a capable model does on its own: it under-routes hard work (Opus for the deadlock hunt, the autonomous MVP, and the research memo; Sonnet for the multi-file feature, the flaky test, and the large-repo fix), over-routes easy work (Sonnet for the ticket classifier, Haiku for an unverified script), and still names Sonnet 5 where Sonnet 5.5 is the current model. The rubric's value is mostly in effort and in the hard constraints: it sends review and chart reading to Opus 5.5 at low and the multi-file feature to medium, where the docs say quality holds, and it keeps forced-tool pipelines off the models that reject them.

## Per prompt

| # | Prompt | Expected | With rubric | Without rubric |
|---|---|---|---|---|
| 1 | Classify 300 support tickets into four labels | Haiku 4.5 | Haiku 4.5 | Sonnet 5.5 @ low |
| 2 | Uppercase 80 city names into a file | Haiku 4.5 | Haiku 4.5 | Haiku 4.5 |
| 3 | Extract name, email, company from 40 messy signatures | Haiku 4.5 or Sonnet 5.5 @ low | Sonnet 5.5 @ low | Sonnet 5 @ low |
| 4 | Add a --dry-run flag, run the tests | Sonnet 5.5 @ low/medium | Sonnet 5.5 @ low | Sonnet 5 @ medium |
| 5 | Script: revenue per month from a CSV | Sonnet 5.5 @ low/medium | Sonnet 5.5 @ low | Haiku 4.5 |
| 6 | Decisions, owners, deadlines from a 40-page transcript | Sonnet 5.5 @ medium/high | Sonnet 5.5 @ medium | Sonnet 5.5 @ medium |
| 7 | Unit tests for the edge cases in a docstring | Sonnet 5.5 @ low/medium | Sonnet 5.5 @ low | Sonnet 5.5 @ medium |
| 8 | Rename a function across 30 files, keep tests green | Sonnet 5.5 @ low/medium | grader error; spot check Sonnet 5.5 @ low (2 of 2) | Sonnet 5.5 @ medium |
| 9 | Implement a spec end to end: migration, service, API, React | Opus 5.5 @ low/medium/high | Opus 5.5 @ medium | Sonnet 5.5 @ high |
| 10 | Review a 1,200-line auth PR for bugs and security issues | Opus 5.5 @ low/medium/high | Opus 5.5 @ low | Opus 5.5 @ high |
| 11 | Which service caused the spike in this dashboard screenshot | Opus 5.5 @ low/medium/high | Opus 5.5 @ low | Opus 5.5 @ high |
| 12 | Three-statement financial model in Excel for the CFO | Opus 5.5 @ medium/high | Opus 5.5 @ high | Opus 5.5 @ high |
| 13 | Find policy conflicts across 600K tokens of contracts | Opus 5.5 or Fable 5.1 @ medium/high | Opus 5.5 @ high | Opus 5.5 @ high |
| 14 | Rare scheduler deadlock chased for weeks, fix with a regression test | Fable 5.1 @ high/xhigh | Fable 5.1 @ high | Opus 5.5 @ high |
| 15 | Build the whole MVP autonomously from a brief | Fable 5.1 @ high/xhigh | Fable 5.1 @ high | Opus 5.5 @ high |
| 16 | Compare six vector databases on twelve criteria, write a memo | Fable 5.1 @ low/medium | Fable 5.1 @ low | Opus 5.5 @ high |
| 17 | A test that fails 1 in 20 runs on CI, passes locally | Opus 5.5 @ medium/high/xhigh | Opus 5.5 @ high | Sonnet 5 @ high |
| 18 | Fuzzing harness plus crash triage for an image parser | Opus 5.5 or Opus 5 @ high/xhigh | Opus 5.5 @ high | Opus 5.5 @ high |
| 19 | Build a 12-slide deck with the slide-design skill | Sonnet 5.5 or Opus 5.5 @ medium/high | Sonnet 5.5 @ high | Sonnet 5.5 @ high |
| 20 | Gmail to Trello to Slack workflow across three connectors | Opus 5.5 or Sonnet 5.5 @ medium/high | Opus 5.5 @ medium | Sonnet 5.5 @ medium |
| 21 | Two-line bug fix in a 2,400-file monorepo | Opus 5.5 @ medium/high | Opus 5.5 @ medium | Sonnet 5.5 @ high |
| 22 | Build and query a knowledge graph with a scripted skill | Sonnet 5.5 @ low/medium | Sonnet 5.5 @ medium | Sonnet 5 @ medium |
| 23 | "Do the same for the other three endpoints we discussed" | Sonnet 5.5 or Opus 5.5, session-dependent | Sonnet 5.5 @ high | Sonnet 5 @ medium |
| 24 | Multi-hour Python 2 to 3 migration with parallel subagents | Opus 5.5 @ medium/high/xhigh | Opus 5.5 @ medium | Opus 5.5 @ high |
| 25 | Claims pipeline that forces `tool_choice` on every request | Sonnet 5 or Opus 5 @ medium/high | Opus 5 @ xhigh; spot check Opus 5 @ high | Opus 5.5 @ medium |

## Caveats

- The labels were written alongside the rubric from the same Anthropic pages, so this is a consistency check on the rubric's reading of the docs, not an independent measurement of task outcomes. A verdict you disagree with is worth an issue, with the docs sentence that backs your expectation.
- Runs are single samples at medium effort; a verdict can move between runs on genuinely borderline prompts (13, 19, 23, 25). Where the docs support two answers, the label accepts both.
- Costs are list-price equivalents reported by the headless CLI; on a subscription they consume plan quota instead.

## Reproduce

```
python evals/run_evals.py --workers 3
```

Results land in `../model-grade-workspace/iteration-N/` with a `summary.md`, a `benchmark.json`, and a standalone `review.html` that shows every prompt, verdict, and assertion side by side. `python evals/run_evals.py --ids 4,9,17 --runs 2 --configs with_skill --no-viewer` is the cheap spot-check form, and `--grader-model claude-sonnet-5-5` grades with Sonnet 5.5 instead.
