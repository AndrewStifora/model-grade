# model-grade rubric

You are choosing the cheapest (model, effort) pair that will complete one specific prompt well with high probability. Read `model-profiles.md` for what each model is documented to be good at. This file tells you how to turn a prompt into a verdict.

## 0. What you are optimizing, and why the errors are lopsided

The unit of cost is a completed task, not a request. A cheap model that fails costs the failed attempt, the retry on a bigger model, and the user's time. An over-provisioned model costs twice as much on one run for each tier above Sonnet 5.5, and twenty times as much for Sonnet 5.5 over Haiku 5.5. That asymmetry sets three rules:

- When you are genuinely torn between two adjacent tiers, pick the higher tier.
- The exception is the step between Haiku 5.5 and Sonnet 5.5 when a checker or a reviewer will catch a miss: there the failed attempt costs a twentieth of the retry, so try Haiku 5.5 first and name Sonnet 5.5 as the re-run.
- When you are torn between two effort levels on the same model, pick the higher one only if the task is intelligence-sensitive (reasoning or ambiguity scored 2 or more). Otherwise pick the lower one, because effort is cheap to raise on a retry and expensive to waste on routine work.

Effort is the first lever, model the second. A stronger model at lower effort is often the cheaper cell: Opus 5.5 at its default medium "matched or beat Claude Opus 5 at `high` effort ... in fewer steps and with fewer tokens", and at low it "solved about the same share of tasks as Sonnet 5.5 at its default, inside run-to-run noise, for about 7% more per solved task". It is not a law, though: on a research benchmark Fable 5.2 "cost 4.3 times as much as Claude Sonnet 5.5 for no measurable gain in score". So always run the cross-tier check in section 5 before you finalize.

## 1. Signals to extract from the prompt

Read the prompt (and any attached files or conversation context) and score these. Write the scores down; they go in the verdict.

**Scored 0 to 3:**

| Signal | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **scope** | one answer or one transform | one file, function, or document, bounded | several files or components, or a multi-section deliverable | a whole system, a multi-day effort, or open-ended |
| **horizon** (dependent steps that need judgment; a long chain of routine tool calls counts as 2 at most) | none, answer directly | a handful | dozens: explore, change, test, iterate | hours of autonomous work, many iterations, sub-agents |
| **ambiguity** (judgment required) | fully specified, mechanical | minor choices the prompt implies | must choose an approach or design and weigh trade-offs | must work out what the task even is; multi-threaded request; "figure out next steps" |
| **reasoning** (depth) | recall or pattern matching | ordinary problem-solving | multi-step reasoning with non-obvious interactions (concurrency, subtle bugs, proofs, causal analysis) | novel or hard: unsolved for weeks, research-grade synthesis, needs first-shot correctness on something complex |

**Categorical:**

- **verification**: `none` / `self-check` / `checker` (tests, compiler, schema validation, a validator script) / `human-review` (a person will review before anything ships).
- **cost_of_error**: `trivial` / `reversible` / `costly` (production systems, money, legal, external communications, anything hard to undo).
- **context_tokens**: estimate. `small` under 20K, `medium` 20K to 200K, `large` over 200K. Attached files count; so does a large repo the task must read.
- **modality**: `text` / `code` / `images-simple` (ordinary UI screenshots) / `images-dense` (charts, diagrams, technical documents, dense screenshots that need zooming) / `documents` (PDF, spreadsheets, decks).
- **domain_flags**: any of `security` (exploits, fuzzing, malware analysis, pentest, CTF, vulnerability hunting, auth review), `bio` (lab methods, molecular mechanisms, life sciences), `finance-enterprise` (spreadsheets, financial models, slide decks, professional documents), `frontend-design`, `research-synthesis`, `vision`.
- **output_shape**: `structured-short` (enum, JSON, a few lines) / `code-change` / `long-deliverable` (report, long document, large table, a complete file).
- **volume**: `one-off` / `high-volume` (the same prompt shape will run many times) / `latency-sensitive` (an interactive user is waiting).
- **dependencies**: what the executor will need beyond the prompt text. `skill` (a skill in the session would trigger, or the prompt names one), `tools` (MCP connectors, web search, a browser, anything external), `project` (a repository, CLAUDE.md, memory, or files the prompt does not include), `session` (earlier conversation turns). Empty when the prompt is self-contained. Section 1b says how each one moves the verdict.

**Latent-difficulty markers.** These words mean the prompt is harder than it looks. If two or more are present, treat reasoning or horizon as at least 2: "flaky", "intermittent", "sometimes", "race", "deadlock", "we've tried", "for weeks", "root cause", "regression", "memory leak", "works locally but not in prod", "migrate", "across the codebase", "legacy", "no tests", "undocumented", "nobody knows why".

## 1b. What the prompt depends on

The prompt rarely says what the executor will have to load and do, and that is where hidden complexity lives. Check these before scoring. You grade in a context of your own, so you cannot look at the session yourself: the skill that called you, or whoever runs the script, describes it in `<context>` (the skill that would trigger, the tools, the project, the conversation). That block is all you have, so say in `notes` when it leaves you guessing. The model you run on is the grader's, not the session's: take the session's model from `<context>`, and when it is not named there, do not assume one.

**A skill would run.** Work from its description and frontmatter, not the whole skill.

- Bundled scripts that do the mechanical work (graph building, document generation, file conversion) lower the intelligence the task needs. Score horizon and reasoning for what is left after the scripts run, and let the tier drop accordingly.
- A prescribed multi-step workflow with verification loops raises horizon to at least 2 even for a one-line prompt.
- Many rules and exact formats favor a literal follower: Sonnet 5.5 (whose docs say Sonnet 5 prompts "should perform well without changes") or Opus 5.5 at medium or above, and Haiku 5.5 at high, its level for "strict instruction following", when the scripts do the work and the output gets checked. The Fable 5 page warns that skills written for earlier models "are often too prescriptive" for Fable, and Fable 5.2 follows style rules and cautions closely, so never step up to Fable because a skill is long.
- If the skill's frontmatter pins `model:` or `effort:`, that setting wins for the turn. Report it in `notes` and grade the rest.

**Connectors or tools are needed.** MCP servers, web search, a browser, anything external.

- The effort floor is medium. Lower effort means fewer tool calls on every model, Haiku 5.5 at low is "more likely to skip a search, stop early, or skip a check", and Sonnet 5.5 in chat and knowledge work "sometimes answers from its training knowledge when a web search would catch details that have changed". Low effort is where a tool-dependent task quietly answers from memory instead. For a Sonnet 5.5 or Haiku 5.5 pick, pass the docs' instruction to search for specifics that may have changed, and give Haiku 5.5 today's date.
- Add one to horizon for each external system beyond the first, capped at 2 unless the steps themselves need reasoning. A read-then-write across two or three systems is a horizon-2 agentic task, not a horizon-3 one.
- Deferred tools (the executor must search for the tool schema first) add a step. Note it.
- If any tool writes somewhere visible or hard to undo (send, post, publish, create records), treat cost_of_error as costly, but do not answer that with a bigger model. The safety lever is a confirm-before-write instruction: list what would be sent or created, then act on approval. Cap the costly-and-unverified step-up at Opus 5.5 for tool plumbing; step to Fable only when reasoning is 3.
- Opus 5.5 "tends to get to work quickly"; for loosely specified multi-app tasks the docs' instruction to explore the connected apps before acting raised completion noticeably. Put it in `notes` for the executor.
- Haiku 5.5 takes a short, well-specified tool task (one system, a few calls) at medium. A chain across several systems, or one that writes somewhere visible, is not Haiku work.

**Project context is needed.** A repository, CLAUDE.md, memory files, or files the prompt does not include.

- Use the size given in `<context>`: file count, lines, whether tests exist and how long they take, whether an index or knowledge graph is already built. A two-line prompt against a large unfamiliar codebase is a latent-difficulty marker: horizon at least 2.
- An existing index (a graphify graph, documented architecture, a fast test suite) lowers horizon and can supply the checker. Say which one you found.
- Executors spawned by `--run` do see project files, CLAUDE.md, and memory. They do not see this conversation.

**The conversation is needed.** "The same as before", "the other three", "as we discussed".

- Grade what the earlier turns establish, not the bare sentence. If `<context>` does not carry them, say the verdict is provisional.
- `--run` cannot carry the conversation, so recommend in-session execution and, per the cache note in section 5, the session's current model unless the task clearly outgrows it.

## 2. Hard constraints (apply before anything else)

These come from documented limits, not from judgment. A constraint sets a floor or a ceiling that the scoring below cannot cross.

- **Prompts over 100K tokens**: Haiku 5.5 bills such a prompt at five times its base rate, input and output, so its price advantage over Sonnet 5.5 shrinks from twenty times to four. Over 200K tokens prefer Opus 5.5 ("catches details that are easy to miss in large inputs"). Every routed model has a 1M window.
- **Images**: `images-simple` can go to Sonnet 5.5. `images-dense`, chart or diagram reading, UI replication, and computer use go to Opus 5.5, which "even at its lowest effort setting ... read values off dense charts more accurately than Claude Opus 5 did at its highest". For the densest technical drawings, give the executor higher-resolution images and a crop or zoom tool; raising effort helps drawings "but does little for charts". No docs claim covers Haiku 5.5 on images, so do not route image work to it.
- **Security content**: do not route to Fable 5.2 without a refusal fallback (its classifiers can decline benign security work). Opus 5.5's docs say "Finding vulnerabilities in source code is allowed. High-risk dual-use cybersecurity activities are not", and Sonnet 5.5's and Haiku 5.5's say the same, so code review for vulnerabilities, auth-flow review, and dependency audits go to Opus 5.5 (or Sonnet 5.5 at tier 1) normally. For dual-use work (exploit development, fuzzing with exploitability triage, malware analysis, offensive tooling) expect possible declines on Fable 5.2, Opus 5.5, Sonnet 5.5, and Haiku 5.5; route to Opus 5 (which still has a cybersecurity classifier, so say it is not guaranteed), name Sonnet 5 at xhigh as the classifier-free last resort (server-side fallback retries Sonnet 5.5's `cyber` declines there too), and recommend a fallback.
- **Biology or life-science content, even benign**: Fable 5.2, Opus 5.5, Sonnet 5.5, and Haiku 5.5 run a biology classifier (Sonnet 5.5's and Haiku 5.5's leave "Everyday health and educational questions" alone); Opus 5 and Sonnet 5 do not document one. Route to Opus 5, or Sonnet 5 at high when the work is within its reach, and mention the Life Sciences Verification Program for organizations that need the current models.
- **Building or training competing AI models** (training or distilling a language model, generating LLM training data at scale): Fable 5.2, Sonnet 5.5, and Haiku 5.5 list a `frontier_llm` category that may decline it; no Opus page does. Route tier 0 and tier 1 work to Sonnet 5 (server-side fallback already retries Sonnet 5.5's declines there) and harder work to Opus 5.5; say so in `notes`.
- **Zero-data-retention org** (only if the caller says so): Fable 5.2 is unavailable. Cap at Opus 5.5.
- **Long autonomy**: multihour work is documented for Opus 5.5 ("multihour audits and migrations of large code bases run end to end with parallel subagents and little oversight"). Fable 5.2 is for runs that are longer or more open-ended than that, and the docs recommend it "for work where nobody needs frequent updates". So hours go to Opus 5.5, and days, or a run whose design decisions no checker can adjudicate, go to Fable 5.2.
- **API pipelines that force a tool call** (`tool_choice` any/tool): not Fable 5.2, Opus 5.5, or Sonnet 5.5 (all return 400). Haiku 5.5 accepts it, so tier-0 work stays there. Above tier 0 use Sonnet 5 or Opus 5, or tell the caller to switch to `auto` with strict tool use and stay on the newer model. **Pipelines that must run with thinking disabled**: not Fable 5.2 and not Opus 5.5. Haiku 5.5 accepts `disabled` at effort high or below; Sonnet 5.5 rejects it but accepts `between_tools` (no up-front thinking) at effort high or below; otherwise Opus 5 at effort high or below, or Sonnet 5. **The `computer_20251124` tool on the Claude API or Google Cloud**: not Fable 5.2, Opus 5.5, or Sonnet 5.5; Opus 5 or Sonnet 5, or migrate to the `computer_toolset_20260801` toolset.
- **API harnesses that edit earlier turns** (rewriting the system prompt, the tool list, or earlier messages mid-conversation): Fable 5.2 rejects the next request on every account, and Opus 5.5, Sonnet 5.5, and Haiku 5.5 run the same check on newer accounts. Tell the caller to keep the history append-only; if they cannot, Opus 5 or Sonnet 5. Claude Code, claude.ai, and the Agent SDK manage this themselves.
- **Latency-sensitive interactive use**: prefer Haiku 5.5, the fastest current model, at low or medium for simple turns, then Sonnet 5.5 at low or medium (its docs: "For chat and other latency-sensitive work, start at `medium` or `low`"), then Opus 5.5 at low or medium. Fable 5.2 "thinks before almost every reply" at high and above, and its turns take noticeably longer.

## 3. Choose the tier

Take `complexity = max(scope, horizon, ambiguity, reasoning)`. Use the max, not the sum: one deep dimension is enough to sink a small model, and four shallow ones do not add up to a hard task.

| complexity | Tier | Notes |
|---|---|---|
| 0 | Haiku 5.5 when no constraint blocks it and a miss is cheap to spot: (a) the task is a mechanical transform (case changes, format conversion, deterministic reshaping, labeling with a fixed label set), (b) output_shape is `structured-short` (classification, extraction, routing), or (c) verification is `checker` or `human-review`. Otherwise Sonnet 5.5 at low. | Haiku 5.5 answers knowledge questions six points below Sonnet 5.5 (85% against 91%) at a tenth of the cost per correct answer. That trade is right when someone or something catches the miss, and wrong for an answer nobody will check. Having to read and write a file does not by itself call for Sonnet. |
| 1 | Sonnet 5.5 | Bounded coding, scripts, tests, summaries, drafting, research and comparison memos, extraction that must be right unchecked, chat. Effort from section 4. Sonnet 5 only when a section 2 constraint names it. Its own docs send "the hardest long-horizon work" to Opus. |
| 2 | Opus 5.5 | The docs' starting point "for most agent workloads": multi-file coding, reviews, dense visuals, long context, financial and office deliverables, multi-app automation, and research where the figures and sources must be right. Opus 5 only when a section 2 constraint names it. |
| 3 | Fable 5.2 | The hardest, most ambiguous, or longest-running work: problems that have resisted other models, open-ended design across a whole system, runs longer than hours. Its docs say to move to it "when your evals on a Claude Opus model at higher effort still don't meet your requirements". |

**Adjustments, applied in this order:**

1. **Take the cheap first attempt** when verification is `checker`, cost_of_error is `trivial` or `reversible`, and a re-run is cheap. Anthropic's runs on Opus 5.5: everything at low with the failures re-run at high solved about 97% of tasks for a little over half the cost of running everything at high. What the cheap attempt is depends on the tier. At tier 1 it is Haiku 5.5 at medium when the task is small (scope and horizon at most 1), and Sonnet 5.5 at low or medium otherwise. At tier 2 it is Sonnet 5.5 at medium when the work is mechanical (ambiguity 0 and reasoning at most 1, such as a rename across many files), and Opus 5.5 at low otherwise, which costs the same per solved task as Sonnet 5.5 at high and re-runs on the same model. At tier 3 it is Opus 5.5 at high or xhigh, unless reasoning is 3. Name the cell you stepped down from in `escalate_if` as the re-run target. Never step below a hard-constraint floor. The step-down needs a usable failure signal: a checker that is itself flaky or intermittent (a test that fails one run in twenty proves nothing when it passes once), one that takes so long that a re-run is not cheap, or one that cannot observe the failure mode at all does not qualify, and neither does a prompt whose latent-difficulty markers pushed it up in the first place.
2. **Step up** when cost_of_error is `costly` and verification is `none` or `self-check`. Nobody will catch the mistake, so pay for fewer mistakes. From tier 0 or tier 1 that is one tier. From tier 2 it is one effort level on Opus 5.5 (medium to high), not a move to Fable 5.2: on research Fable 5.2 scored below Opus 5.5, and on coding Opus 5.5 at xhigh matches it, so the extra tier does not buy fewer mistakes. Apply the step once.
3. **Step up one tier** when two or more latent-difficulty markers are present and the tier came out at 0 or 1.
4. **Do not step down** just because the prompt is short. Prompt length is not task difficulty.

## 4. Choose the effort level

On the API, Sonnet 5.5, Sonnet 5, Opus 5, and Fable 5.2 default to high; Opus 5.5 and Haiku 5.5 default to medium. In Claude Code the four current models all start at medium, so name the level explicitly. Start from the workload shape, then adjust by tier.

**By workload shape (measured by Anthropic):**

| Workload | Curve | Effort to use |
|---|---|---|
| Classification, extraction, chat, high-volume routes | flat | low |
| Research and knowledge work | depends on the model: Opus 5.5 lost 13.3 points at low against medium on one research benchmark, while Fable 5.2 gained only 3.3 points from low to high for 3.2 times the cost | medium on Opus 5.5; medium or high on Sonnet 5.5; low or medium on Fable 5.2 |
| Bounded coding with a checker | re-running the failures of a low pass at high beat every fixed level on cost | the cheap first attempt from section 3, escalate on failure |
| Long-horizon coding, multi-file features, agentic loops | a real trade-off: Opus 5.5 solved 87.4% at low, 92.8% at medium, 95.3% at high, and 96.7% at xhigh, for $0.11, $0.21, $0.29, and $0.74 a task; Sonnet 5.5 lost about 7 points at medium against high | Opus 5.5 at medium; high when unverified; xhigh only when demanding and measured |
| Code review, bug hunting, root-cause analysis | steep at the bottom: Opus 5.5 lost 34 points at low against medium on defect search | medium or high, never low |
| Reasoning-ceiling work (hard debugging, proofs, open problems) | on Fable 5.2 most of the gain arrives by high, and above it gains are uneven | high; xhigh only with a measured gain |
| Correctness matters more than cost, or the user asked for maximum capability | | max, with a note about diminishing returns and overthinking |

**Per-tier notes:**

- **Haiku 5.5**: medium is the default and the start "for most work, including agentic coding". Low for chat, short tool tasks, and simple high-volume requests such as classification, extraction, and transforms. High for knowledge work, longer agent tasks, and strict instruction following. Never xhigh or max: the docs say to compare those with Sonnet 5.5, and Sonnet 5.5 at low or medium is the better cell. At low and medium it "sometimes reports a code change as done without running a check", so a coding pick carries the docs' instruction in `notes` (run a real check that exercises the change before reporting it done).
- **Sonnet 5.5**: its levels are recalibrated, so do not carry Sonnet 5 settings over. Low for short, scoped, non-intelligence-sensitive work, chat, and latency-sensitive routes; at low it "keeps its thinking short and can skip verifying a change", so a low pick on coding work with a checker carries the same verification instruction in `notes`. Medium is the documented start for well-specified agentic coding and multistep tool use, and fits cost-sensitive work with reasoning at most 1; it gives up about 7 points against high on coding, so medium wants a checker. High for harder or longer agentic tasks, unverified coding, anything with reasoning or ambiguity at 2, and unattended long runs (at low and medium it is "more likely to stop and check in"). A short structured answer that needs a few steps of working out goes at high with the docs' line "Think the problem through before you answer.", because at low and medium it "often answers without thinking first". Xhigh and max only with a measured gain; there it starts its own review rounds, so pass the docs' stop-and-report instruction. Never pair low with reasoning 2.
- **Sonnet 5** (fallback only): low for short, scoped work; medium when cost-sensitive and reasoning is at most 1; high for reasoning or ambiguity at 2; xhigh for the hardest coding it should still handle. At low there is documented under-thinking risk on moderately complex tasks.
- **Opus 5.5**: medium is the default and the starting point. Low only for coding with a checker, with failures re-run at high, and for chart and screenshot reading; never for code review, bug hunting, research, or analysis, where low costs 13 to 34 points. High for unverified multi-file agentic work and for reviews and bug hunts that matter. Xhigh is the last step before Fable: on coding it is "level with Fable 5.2 at `high` for a little over half the cost". Max rarely, and long turns at xhigh or max need a large `max_tokens`.
- **Opus 5** (fallback only): start at high; use low and medium liberally where quality holds; xhigh for demanding coding and agentic work.
- **Fable 5.2**: high is the documented start and where most of the gain arrives. Medium for interactive work and everyday knowledge work. Low for well-specified tasks and subagent-style volume; on coding it solved more at low than Fable 5.1 did at its default. At low or medium on agentic work it ends turns early more often, so pass the docs' finishing-work paragraph in `notes`. Xhigh only for the hardest long-running work where a gain has been measured; max only to measure the ceiling.

## 5. Cross-tier check (do this before finalizing)

Compare your candidate against "one tier up at lower effort" and pick the cheaper likely-to-succeed cell:

- **Haiku 5.5 at high versus Sonnet 5.5 at low**: Haiku 5.5 at high is still the cheaper cell for knowledge work that gets checked. Past high, switch to Sonnet 5.5 instead of raising Haiku's effort.
- **Sonnet 5.5 at high versus Opus 5.5 at low**: the same cell on coding (87.6% for $0.11 per solved task against 87.4% for $0.12). Prefer Sonnet 5.5 for bounded work. Prefer Opus 5.5 at low when the task also needs dense visuals or a large context, or when a failure will be re-run at high on the same model.
- **Sonnet 5.5 at xhigh versus Opus 5.5 at medium**: for multi-file coding, prefer Opus 5.5 at medium, which solved 92.8% for $0.22 per solved task. The Sonnet 5.5 page itself says "For the hardest long-horizon work, an Opus model is the better choice", and at xhigh Sonnet 5.5 thinks much longer and starts its own review rounds.
- **Opus 5.5 at high or xhigh versus Fable 5.2**: raise Opus 5.5's effort before you change tier. On coding, Opus 5.5 at high solved 95.5% for $0.30 per solved task against Fable 5.2 at low's 94.6% for $0.39, and at xhigh it is level with Fable 5.2 at high for a little over half the cost. On research, Fable 5.2 is not the step up at all: it scored 1.9 points below Opus 5.5 at 2.9 times the cost. Step to Fable 5.2 when reasoning is 3, when the run is longer or more open-ended than hours, or when Opus 5.5 at high has already failed. A costly, unchecked answer is not a reason on its own.
- **Sonnet 5.5 versus Haiku 5.5 on unverified work**: do not trade down to Haiku 5.5 where a wrong answer matters and nobody will check it. Six points of accuracy for a tenth of the cost is a good trade only when the miss gets caught.
- **Opus 5 versus Opus 5.5**: Opus 5 only under a section 2 constraint. Otherwise it costs 25% more per token and several times more per solved task.
- **Sonnet 5 versus Sonnet 5.5**: Sonnet 5 only under a section 2 constraint. Same price; it is legacy, and Sonnet 5.5 solved about 10 more points of the coding subset for 87% less per solved task.
- **Cache continuity**: prompt caches are model-scoped. If the prompt is a follow-up inside a long session on some model, switching models forfeits the cached prefix; stay on the session's model unless the saving is large or the task clearly outgrows it. Say so in `notes` when this applies. Thinking blocks follow the same direction: Fable 5.2 reads every routed model's blocks, so stepping up to it keeps the conversation's reasoning, but "No other model reads their blocks", so stepping down from Fable 5.2 starts without it.

## 6. Confidence and the tie-break

Report `confidence` from 0 to 1 for the whole verdict. Below 0.6, step up (tier if the doubt is about capability, effort if it is about depth) and say in `why` that you stepped up for uncertainty. A low-confidence verdict that stays cheap is the one failure mode this skill exists to prevent.

## 7. Verdict format

Emit exactly these fields (the JSON schema is `scripts/verdict_schema.json`):

- `model`: model ID; `alias`: Claude Code alias; `tier`: 0 to 3.
- `effort`: `low` | `medium` | `high` | `xhigh` | `max`. Every routed model takes an effort level.
- `confidence`: 0 to 1.
- `signals`: the scores and categories from section 1, `dependencies` from section 1b, and `latent_markers`: the latent-difficulty phrases you found, quoted, or an empty list.
- `why`: two to four sentences. Name the deciding signal, the workload shape, and any adjustment or constraint that moved the verdict.
- `cheaper_alternative`: the next cheaper cell that could plausibly work, with `when` describing the condition, or `null` if there is none worth trying.
- `escalate_if`: concrete, observable conditions under which the caller should re-run one tier or one effort level up (a failing test suite after one pass, the change spreading beyond the named files, a refusal, an answer that cites nothing).
- `notes`: constraints that applied, fallback advice for picks whose classifiers may decline, executor instructions worth passing on, cache-continuity remarks. Empty list if none.

Human-readable rendering (used when `--json` is not set):

```
model-grade -> Opus 5.5 @ medium   (confidence 0.80)
Why: ...
Cheaper: Sonnet 5.5 @ high -- when ...
Escalate if: ...
Signals: scope 2 | horizon 2 | ambiguity 1 | reasoning 1 | checker | medium ctx | code | depends on project
Notes: ...
```

## 8. Worked examples

**"Classify these 300 support tickets (attached CSV) as billing, bug, feature, or other. Output a CSV with ticket_id,label."**
scope 0, horizon 0, ambiguity 0, reasoning 0; checker (a schema and a human skim), structured-short, high-volume. Verdict: Haiku 5.5 at low, confidence 0.85. Cheaper alternative: none. Escalate if: label distribution looks implausible or spot-checks show more than a few percent errors, then Sonnet 5.5 at low.

**"Add a --dry-run flag to scripts/cleanup.py that prints what would be deleted without deleting. Follow the existing argparse pattern. Run the tests."**
scope 1, horizon 1, ambiguity 0, reasoning 1; checker (tests), reversible, code-change. Complexity 1 says Sonnet 5.5, and the cheap first attempt applies: the task is small, the tests will catch a miss, and a failed Haiku run costs a twentieth of the retry. Verdict: Haiku 5.5 at medium, confidence 0.75. Cheaper alternative: none. Escalate if the tests fail after one pass or it reports done without running them: Sonnet 5.5 at medium. Notes: tell it to run the tests and show their output before reporting done.

**"Summarize this 40-page transcript into decisions, owners, and deadlines."**
scope 1, horizon 0, ambiguity 1, reasoning 1; no checker, text, medium context. Verdict: Sonnet 5.5 at medium, confidence 0.75. Cheaper: Haiku 5.5 at high, but only if a person will check the summary against the transcript (an unverified summary needs Sonnet's reliability).

**"Implement docs/spec-notifications.md: migration, service layer, REST endpoints, and the React inbox component. Tests in tests/ must pass."**
scope 2, horizon 2, ambiguity 1, reasoning 1; checker, reversible, code-change. Complexity 2, so Opus 5.5. A multi-file feature is long enough that a failed first pass is not a cheap re-run, so start at the default. Verdict: Opus 5.5 at medium, confidence 0.8. Cheaper alternative: Opus 5.5 at low with the failures re-run at high, or Sonnet 5.5 at high, when the spec is tight and the suite is fast and trusted. Escalate if the suite still fails after one full pass: Opus 5.5 at high.

**"Review this 1,200-line PR touching our auth flow for bugs and security issues. Report everything you find."**
scope 2, horizon 1, ambiguity 1, reasoning 2; human-review, security flag. Finding vulnerabilities in source code is explicitly allowed on Opus 5.5, which reviews with "more bugs caught ... and fewer false alarms". Review is defect search, where low effort cost Opus 5.5 34 points, so do not go below the default. Verdict: Opus 5.5 at medium, confidence 0.8. Escalate to high if the first pass reports fewer findings than the diff's size suggests. Notes: not Fable because its classifiers can decline benign security review.

**"Here's a screenshot of our Grafana dashboard during the incident. Which service caused the latency spike, and why?"**
scope 1, horizon 1, ambiguity 2, reasoning 2; images-dense, no checker. Dense-image floor is Opus 5.5, which reads charts at low better than Opus 5 at max. Verdict: Opus 5.5 at low, confidence 0.75. Escalate to medium with a crop tool if panel text is too small to read. Notes: raising effort does little for charts; resolution and cropping do.

**"Compare six vector databases on twelve criteria with sources and write a decision memo."**
scope 2, horizon 2, ambiguity 1, reasoning 2; research-synthesis, long-deliverable, tools (web search), no checker. Complexity 2, so Opus 5.5, which is also the docs' pick when figures and sources must be right; research at low costs Opus 5.5 13 points, so medium. Verdict: Opus 5.5 at medium, confidence 0.75. Cheaper alternative: Sonnet 5.5 at high, about 2.4 points lower on the docs' research benchmark for two thirds of the cost, when the memo is more compilation than synthesis. Escalate to Opus 5.5 at high if the memo cites nothing or contradicts itself across criteria. Notes: not Fable 5.2, which cost 2.9 times as much as Opus 5.5 on that benchmark and scored lower; tell the executor to verify each product's current state with a search.

**"Our scheduler has a rare deadlock we've been chasing for weeks. Repo attached plus three stack dumps. Find the root cause and fix it with a regression test."**
scope 2, horizon 2, ambiguity 2, reasoning 3; latent markers ("rare", "for weeks", "root cause"); checker (the regression test, once written). Complexity 3, and the markers rule out the cheap first attempt. Verdict: Fable 5.2 at high, confidence 0.8. Cheaper alternative: Opus 5.5 at xhigh. Escalate: none above this; if Fable stalls, split the problem.

**"Write a fuzzing harness for our image parser and triage the crashes it finds."**
scope 2, horizon 2, ambiguity 2, reasoning 2; security flag, dual-use shape. Complexity 2. A fuzzing harness is close to the "high-risk dual-use" line, so Fable is excluded and Opus 5.5 may decline the triage half. Verdict: Opus 5.5 at high, confidence 0.65. Notes: if it refuses, re-run on Opus 5 (the `mg-run-opus5` executor), which is not guaranteed either; Sonnet 5 (not 5.5 or Haiku 5.5, which have a `cyber` classifier too) at xhigh is the classifier-free last resort. Escalate to xhigh if the harness finds crashes it cannot classify.

**"Turn docs/q3-review.md into a 12-slide deck for the leadership meeting, using the slide-design skill."**
dependencies [skill]. The skill's scripts build the file and its rules constrain the design, so what remains is choosing the message for each slide: ambiguity 1, reasoning 1, horizon 2 from the skill's build-render-check loop; the user will look at it before the meeting. Verdict: Sonnet 5.5 at high, confidence 0.7. Cheaper: Sonnet 5.5 at medium when the source document already carries the narrative. Escalate to Opus 5.5 at medium if the rendered deck still has layout defects after one fix pass or the narrative needs restructuring. Not Fable: a rule-heavy skill is where the docs say Fable can do worse, and it would be over-commitment anyway.

**"Read the unread Gmail in the Clients label, make a Trello card on the Follow-ups board for each one that asks a question, and post a one-line summary of the new cards in Slack #client-ops."**
dependencies [tools], three systems; horizon 2 (capped: the chain is plumbing), ambiguity 1 (what counts as a question), reasoning 1; the Slack post is visible to others, so cost_of_error is costly and there is no checker. Complexity 2. Effort floor medium because tools are involved. Verdict: Opus 5.5 at medium, confidence 0.7. Cheaper: Sonnet 5.5 at high when the question rule is spelled out (tell it to read each message through the connector rather than guess). Escalate if cards appear for messages that ask nothing or the summary is malformed: Opus 5.5 at high. Notes: instruct the executor to show the cards and the Slack line before writing them, and to explore the connected apps before acting; the connectors are deferred tools, so it searches for them first. Not Haiku 5.5: three systems and a visible write.

**"Fix the bug where invoice totals are off by the tax amount on refunds."** with context: a monorepo of about 2,400 files, a 40-minute test suite, no index.
dependencies [project]. Two lines against a large unfamiliar repo is a latent marker; refund tax handling is accounting logic, so reasoning 2; horizon 2. A checker exists but a re-run costs 40 minutes, so the cheap first attempt does not apply, and this is bug hunting, where low effort is out. Verdict: Opus 5.5 at medium, confidence 0.7. Cheaper: Sonnet 5.5 at high once the refund path is located and turns out to be small. Escalate to Opus 5.5 at high if the fix spreads beyond the refund calculation or tests fail after one pass.

**"Migrate our 300-module Python 2 code base to Python 3 over the next few hours with parallel subagents; keep the test suite green throughout."**
scope 3, horizon 3, ambiguity 1, reasoning 1; checker (the suite), reversible (a branch), code-change. Complexity 3 by scope and horizon, but the shape is exactly what the Opus 5.5 docs describe: "multihour audits and migrations of large code bases run end to end with parallel subagents and little oversight". Hours, not days, and a mechanical migration, not an unsolved problem. Verdict: Opus 5.5 at high, confidence 0.7. Cheaper: Opus 5.5 at medium when the suite is fast enough to re-run per module. Escalate to Fable 5.2 at high if the migration turns up design decisions the suite cannot adjudicate, or the run stalls repeatedly. Notes: give the executor a time budget line (elapsed seconds against a budget), which the docs say speeds up multi-agent work; and the unattended-run instruction so it does not stop to report.

**"Our ticket router calls the API about 50,000 times a day with tool_choice forced to our route_ticket tool; a schema validator rejects anything malformed. Which model?"**
scope 0, horizon 0, ambiguity 0, reasoning 0; checker (the validator), structured-short, high-volume. The forced tool call excludes Fable 5.2, Opus 5.5, and Sonnet 5.5, and Haiku 5.5 is the one current model that accepts it, which is also where a routing task belongs. Verdict: Haiku 5.5 at low, confidence 0.85. Cheaper alternative: none. Escalate if the validator's reject rate or a spot check of routes is poor: Haiku 5.5 at medium, then Sonnet 5. Notes: Haiku 5.5 has no server-side fallback, so handle a refusal in the client.

## 9. Anti-patterns

- Grading by prompt length. A one-line prompt can be a three-week problem.
- Assuming "code" means Opus. A scoped edit with tests is Haiku 5.5 at medium or Sonnet 5.5 at low.
- Sending security-adjacent or bio work to Fable without a fallback, or bio work to Opus 5.5, Sonnet 5.5, or Haiku 5.5.
- Naming Sonnet 5.5 or Haiku 5.5 as the classifier-free last resort. That is Sonnet 5.
- Picking Opus 5 over Opus 5.5, or Sonnet 5 over Sonnet 5.5, without a constraint from section 2.
- Pairing Sonnet at low with reasoning 2. The docs flag under-thinking there.
- Sending a research or comparison memo to Fable 5.2. Opus 5.5 at medium scored higher for about a third of the cost.
- Stepping up to Fable 5.2 because an answer is costly and unchecked. Raise Opus 5.5's effort instead.
- Opus 5.5 at low for code review, bug hunting, research, or analysis.
- Choosing xhigh or max on Fable 5.2 or Opus 5.5 without a measured gain, or on Haiku 5.5 at all.
- Choosing Haiku 5.5 for an answer that matters and that nobody will check.
- Ignoring the session: switching models mid-session throws away the cache; note it.
- Reporting a low-confidence verdict without stepping up.
- Grading a prompt that names a skill or a connector as if it were self-contained.
- Stepping up a tier to make a tool-writing task safer. A confirm-before-write instruction is the safety lever; a bigger model is not.
- Counting a long chain of routine tool calls as horizon 3.
