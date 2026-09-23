# Model profiles for routing

Facts distilled from Anthropic's prompt-engineering pages and model pages (fetched 2026-09-23; URLs and hashes in `sources.md` and `sources.json`) and the cost-optimization guide bundled with the Claude API skill. Prices are first-party API list rates per million tokens. "Alias" is what the Claude Code `--model` flag and the Agent tool accept. Quoted sentences are verbatim from the docs.

| Tier | Model | Model ID | Alias | $ in / out per M | Context | Effort | Thinking |
|---|---|---|---|---|---|---|---|
| 0 | Claude Haiku 4.5 | `claude-haiku-4-5` | `haiku` | 1 / 5 | 200K | not supported (`effort` returns an error) | off unless `budget_tokens` is set |
| 1 | Claude Sonnet 5 | `claude-sonnet-5` | `sonnet` | 2 / 10 | 1M | low, medium, high (default), xhigh, max | adaptive, on by default |
| 2 | Claude Opus 5.5 | `claude-opus-5-5` | `opus` on Claude Code 2.1.280 and later | 4 / 20 | 1M | low, medium (default), high, xhigh, max | always on; cannot be disabled |
| 2, fallback only | Claude Opus 5 | `claude-opus-5` | `opus` on Claude Code before 2.1.280; otherwise pin the ID | 5 / 25 | 1M | low, medium, high (default), xhigh, max | adaptive, on by default; can be disabled only at effort high or below |
| 3 | Claude Fable 5.1 | `claude-fable-5-1` | `fable` | 10 / 50 | 1M | low, medium, high (default), xhigh, max | always on |

Relative price per token: Sonnet = 1x, Haiku = 0.5x, Opus 5.5 = 2x, Opus 5 = 2.5x, Fable = 5x. Per-token price does not predict cost per completed task: a stronger model at lower effort often finishes in fewer tokens, fewer turns, and fewer retries. Judge cost per completed task.

## Tier 0: Claude Haiku 4.5

- Fit: high-volume work with checkable outputs. Classification, extraction into a fixed schema, simple text transforms, routing, answers grounded in text you supply.
- Measured: "Claude Haiku 4.5 answered knowledge questions at about a tenth of Claude Opus 5's cost per question at 63% accuracy versus 92%. It fits high-volume work with checkable outputs, not long agentic loops."
- Constraints: 200K context window, 64K max output. No `effort` parameter (thinking is the older manual `budget_tokens` form and is off by default). It has no model-specific prompting page, so it is the least documented current model.
- Do not use for: multi-step work that nobody checks, agentic loops, judgment calls, or anywhere a 30-point accuracy gap would matter.

## Tier 1: Claude Sonnet 5

- "Claude Sonnet 5 has particular strengths in coding and agentic tasks."
- "Claude Sonnet 5 interprets prompts literally and explicitly, particularly at lower effort levels. It does not silently generalize an instruction from one item to another, and it does not infer requests you didn't make. The upside of this literalism is precision, and it generally performs better for API use cases with carefully tuned prompts, structured extraction, and pipelines where you want predictable behavior."
- "Claude Sonnet 5 is more agentic than Claude Sonnet 4.6 by default and will reach for tools and run self-verification loops more readily."
- Effort: "Claude Sonnet 5 at medium is comparable in intelligence to Claude Sonnet 4.6 at high, and Claude Sonnet 5 at high is comparable to Claude Sonnet 4.6 at max." "At `low` and `medium`, the model scopes its work to what was asked rather than going above and beyond. This is good for latency and cost, but on moderately complex tasks running at `low` effort there is some risk of under-thinking." "`xhigh`: Extra high effort is the recommended setting for the hardest coding and agentic use cases." "`low`: Reserve for short, scoped tasks and latency-sensitive workloads that are not intelligence-sensitive."
- Measured: Fable 5 at low beat Sonnet 5 on a deep-research benchmark at about 10% less cost per task. Sonnet is not automatically the cheapest choice for reasoning-heavy work.
- Constraints: no mid-conversation system messages; `temperature`, `top_p`, `top_k` are rejected; a newer tokenizer produces roughly 30% more tokens than Sonnet 4.6 for the same text. No safety classifiers are documented for it, which makes it the last-resort model for legitimate work the Opus and Fable classifiers decline.
- Fit: bounded coding tasks (one file to a few files) with clear acceptance criteria, scripts, unit tests, summaries, drafting, structured extraction that Haiku is not reliable enough for, interactive coding at high effort.

## Tier 2: Claude Opus 5.5

- "Claude Opus 5.5 is built for long-running agentic coding and knowledge work, priced at $4 / $20 USD per million input / output tokens." It "generates output tokens more than 30 percent faster than Claude Opus 5 and tends to finish the same task with fewer tokens." Existing Opus 5 prompts work without changes.
- Agentic coding and review: "The model is strongest on multistep work in a real repository, such as carrying a change through a large code base until its tests pass. In Anthropic's testing, at its default `medium` effort the model matched or beat Claude Opus 5 at `high` effort on such tasks, in fewer steps and with fewer tokens. It also sustains long-running autonomous work better than Claude Opus 5, such as multi-hour audits and migrations of large code bases run end to end with parallel subagents and little oversight. Early testers also reported stronger code review, with more bugs caught than on Claude Opus 5 and fewer false alarms."
- Knowledge work: "The model is much less likely to state an incorrect figure or cite the wrong source. It's better at financial modeling tasks ... and it catches details that are easy to miss in large inputs ... The spreadsheets, slides, and documents it produces need less editing before you share them."
- Vision and computer use: "even at its lowest effort setting it read values off dense charts more accurately than Claude Opus 5 did at its highest, using a small fraction of the output tokens." Better "where meaning depends on position rather than text" (flowchart arrows, diagram diffs, calendar screenshots). Computer use: "at its default effort it matched the success rate that Claude Opus 5 reached only at a much higher effort setting." For the densest technical drawings, higher-resolution images and crop or zoom tools still add accuracy; raising effort helps drawings but "does little for charts".
- Effort: `medium` is the default and the starting point. "Claude Opus 5.5 at `medium` matches or exceeds Claude Opus 5 at `high` on coding and knowledge-work evaluations, and on several coding evaluations `low` comes close to it at much lower cost." "At a given level, Claude Opus 5.5 tends to think more per turn than Claude Opus 5, especially at `xhigh` and `max`." "Reserve `xhigh` and `max` for work where you've measured a quality gain." Lowering effort "reduces thinking, and with it cost and latency, more reliably than prompt instructions do." Set `max_tokens` up to 128,000 for long agentic turns because thinking counts against it.
- Communication: progress notes between tool calls arrive as progress-update thinking blocks (empty text under the default `display`), and its final reports "say plainly what it did, what it found, and what it needs from you."
- Behaviors to know: "tends to get to work quickly"; on loosely specified multi-app tasks, an instruction to explore the connected apps before acting raised completion noticeably. In chat it may re-examine earlier answers on follow-ups. It resists indirect prompt injection better than earlier Opus models. On unattended runs it may end a turn with a report instead of the next tool call; a standing instruction in the docs addresses that.
- Constraints: safety classifiers for biology ("the same as Claude Fable 5.1's"), cybersecurity ("Finding vulnerabilities in source code is allowed. High-risk dual-use cybersecurity activities are not."), and reasoning extraction. A decline returns `stop_reason: "refusal"` with a category; server-side fallback (`fallbacks: "default"`, beta) retries on the model Anthropic recommends for that category. Thinking cannot be disabled (400). Forced `tool_choice` (`any` or `tool`) returns a 400. Thinking blocks are bound to the model and the conversation, so keep history append-only; Opus 5.5 reads Opus 5, Sonnet, and Haiku thinking blocks but not Fable's, and Fable 5.1 reads Opus 5.5's, so a conversation can step Opus 5 to 5.5 to Fable 5.1 without losing its reasoning. The older `computer_20251124` tool type is not supported. Fast mode is Claude API only.
- Claude Code: the `opus` alias resolves to Opus 5.5 on the Anthropic API from Claude Code v2.1.280 (`claude update`); earlier versions resolve it to Opus 5. Pin with the full ID or the `ANTHROPIC_DEFAULT_OPUS_MODEL` environment variable.
- Fit: the default for real agent workloads, multi-file coding, multi-hour autonomous migrations and audits, code review, dense charts and screenshots, computer use, long-context analysis, financial models and office deliverables, and multi-app workflow automation.

## Tier 2 fallback: Claude Opus 5

Keep Opus 5 only for work Opus 5.5 cannot take. It costs 25% more per token and is documented to do less on every workload the docs compare.

- "Claude Opus 5 is built for complex agentic coding and enterprise work, with particular strengths in long-horizon agentic tasks." Strongest on "multi-file features, larger refactors, and end-to-end feature work"; code review "finds real bugs at a high rate per pass ... Accuracy holds at lower effort settings"; strong on charts, documents, diagrams; 1M window with quality that "stay[s] consistent throughout the window"; multi-sheet spreadsheets and slide decks; coordinates subagent teams well.
- Effort: default high; "use `low` and `medium` liberally as your primary control for token cost and response time wherever quality holds, and step up to `xhigh` for demanding coding and agentic work." Long-horizon coding: about 2 points lost at medium for half the cost, about 8 at low for a quarter.
- Measured: on a coding subset Opus 5 matched Fable 5 (91.7% versus 91.3%) at about 60% of its cost.
- Behaviors: verbose by default; verifies its own work unprompted; delegates readily.
- When to pick it instead of 5.5: biology or life-science work (no biology classifier is documented for Opus 5, and the Opus 5.5 docs call its biology safeguard "new if you're coming from Claude Opus 5"); high-risk dual-use security work that 5.5 declines (Opus 5 has the cybersecurity classifier too, so it is not guaranteed); integrations that must run with thinking disabled; the `computer_20251124` tool type; forced `tool_choice`; or a Claude Code older than 2.1.280 where the `opus` alias still means Opus 5.

## Tier 3: Claude Fable 5.1

- Fable 5 (which 5.1 supersedes at the same price) "takes on problems that were previously too complex, long-running, or ambiguous for prior models, and is particularly effective at end-to-end work that takes a person hours, days, or weeks to complete. The teams seeing the best outcomes apply Claude Fable 5 to their hardest unsolved problems; testing it only on simpler workloads tends to undersell its capability range. It also performs reliably on more straightforward tasks."
- Documented improvements over Opus 4.8: long-horizon autonomy ("completing multiday, goal-directed runs"), "first-shot correctness on complex, well-specified problems", vision on "dense technical images, web applications, and detailed screenshots", enterprise workflows, code review and debugging recall, "navigating ambiguity ... complex, multithreaded requests and asked to determine next steps", and dependable dispatch of parallel subagents.
- Effort: "Effort is the primary control for trading off intelligence, latency, and cost on Claude Fable 5.1." Start at high. "At `medium`, results roughly match Claude Fable 5 at lower cost, so step down to `medium` or `low` where your evals show quality holds. At `low`, Claude Fable 5.1 is often competitive with Claude Opus and Claude Sonnet models on cost per task while scoring higher, so include it in the comparison wherever you'd otherwise run a smaller model at a higher effort level." Those comparisons predate Opus 5.5. At low it calls search and retrieval tools less often. At xhigh and max it may draft a long deliverable twice.
- Longer turns: "Individual requests on hard tasks can run for many minutes at higher effort settings ... and autonomous runs can extend for hours."
- Constraints: safety classifiers can return `stop_reason: "refusal"` for offensive-cyber, bio/life-science, and reasoning-extraction content, and "benign cybersecurity work and beneficial life sciences tasks may also trigger these safeguards". Requires 30-day data retention. Forced `tool_choice` returns a 400. No assistant prefill.
- Fit: the hardest, most ambiguous, or longest-running work (multiday); hard-but-short reasoning at low or medium effort; problems that have resisted other models; multi-agent orchestration at scale.

## Cross-model equivalences the docs state

- Opus 5.5 at medium matches or exceeds Opus 5 at high on coding and knowledge work; on several coding evaluations Opus 5.5 at low comes close. Opus 5.5 at low reads dense charts better than Opus 5 at max. Opus 5.5 at medium matches Opus 5's computer-use success rate at a much higher effort.
- Sonnet 5 medium is comparable to Sonnet 4.6 high; Sonnet 5 high is comparable to Sonnet 4.6 max.
- Fable 5.1 medium roughly matches Fable 5 at its default; Fable 5.1 low often scores higher than Opus (5 and earlier) and Sonnet at competitive cost per task.
- Fable 5 low beat Sonnet 5 on deep research at about 10% less per task; Opus 5 matched Fable 5 on a coding subset at about 60% of the cost.
- Haiku 4.5 scored 63% versus Opus 5's 92% on knowledge questions at about a tenth of the cost.
- Effort curves by workload (Anthropic's runs, pre-Opus 5.5): research and knowledge work are nearly flat (low gave up 1 to 3 points for a third to a half off; medium matched the default at 70% to 85% of its cost); long-horizon coding is a real trade-off; reasoning-ceiling research pays about 2.4 rubric points per effort step.
- Re-run-on-failure: running everything at low and re-running failures at the default reached about 93% pass at about half the cost of running everything at the default, when a checker exists to detect the failures.
