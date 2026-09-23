# model-grade rubric

You are choosing the cheapest (model, effort) pair that will complete one specific prompt well with high probability. Read `model-profiles.md` for what each model is documented to be good at. This file tells you how to turn a prompt into a verdict.

## 0. What you are optimizing, and why the errors are lopsided

The unit of cost is a completed task, not a request. A cheap model that fails costs the failed attempt, the retry on a bigger model, and the user's time. An over-provisioned model costs 2x to 5x on one run. That asymmetry sets two rules:

- When you are genuinely torn between two adjacent tiers, pick the higher tier.
- When you are torn between two effort levels on the same model, pick the higher one only if the task is intelligence-sensitive (reasoning or ambiguity scored 2 or more). Otherwise pick the lower one, because effort is cheap to raise on a retry and expensive to waste on routine work.

Effort is the first lever, model the second. The docs are explicit that a stronger model at lower effort is often the cheaper cell: Opus 5.5 at its default medium "matched or beat Claude Opus 5 at high effort ... in fewer steps and with fewer tokens", and Fable 5.1 at low is "often competitive with Claude Opus and Claude Sonnet models on cost per task while scoring higher". So always run the cross-tier check in section 5 before you finalize.

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

The prompt rarely says what the executor will have to load and do, and that is where hidden complexity lives. Check these before scoring. In a session you can look: the skills list, the tool list, the working directory, the conversation. Through the API script you only have `<context>`, so say in `notes` when you are guessing.

**A skill would run.** Read its description and frontmatter, which is cheap, not the whole skill.

- Bundled scripts that do the mechanical work (graph building, document generation, file conversion) lower the intelligence the task needs. Score horizon and reasoning for what is left after the scripts run, and let the tier drop accordingly.
- A prescribed multi-step workflow with verification loops raises horizon to at least 2 even for a one-line prompt.
- Many rules and exact formats favor a literal follower: Sonnet 5 or Opus 5.5 at medium or above. The Fable 5 page warns that skills written for earlier models "are often too prescriptive" for Fable and can degrade its output, so never step up to Fable because a skill is long.
- If the skill's frontmatter pins `model:` or `effort:`, that setting wins for the turn. Report it in `notes` and grade the rest.

**Connectors or tools are needed.** MCP servers, web search, a browser, anything external.

- The effort floor is medium. Tool usage rises with effort on Sonnet 5 and Opus 4.8, Fable 5.1 at low calls search and retrieval tools less often, and Sonnet 5 with thinking off reaches for tools less. Low effort is where a tool-dependent task quietly answers from memory instead.
- Add one to horizon for each external system beyond the first, capped at 2 unless the steps themselves need reasoning. A read-then-write across two or three systems is a horizon-2 agentic task, not a horizon-3 one.
- Deferred tools (the executor must search for the tool schema first) add a step. Note it.
- If any tool writes somewhere visible or hard to undo (send, post, publish, create records), treat cost_of_error as costly, but do not answer that with a bigger model. The safety lever is a confirm-before-write instruction: list what would be sent or created, then act on approval. Cap the costly-and-unverified step-up at Opus 5.5 for tool plumbing; step to Fable only when reasoning is 3.
- Opus 5.5 "tends to get to work quickly"; for loosely specified multi-app tasks the docs' instruction to explore the connected apps before acting raised completion noticeably. Put it in `notes` for the executor.
- Haiku is out for multi-tool orchestration. The docs place it outside "long agentic loops".

**Project context is needed.** A repository, CLAUDE.md, memory files, or files the prompt does not include.

- Size it before scoring: file count, lines, whether tests exist and how long they take, whether an index or knowledge graph is already built. A two-line prompt against a large unfamiliar codebase is a latent-difficulty marker: horizon at least 2.
- An existing index (a graphify graph, documented architecture, a fast test suite) lowers horizon and can supply the checker. Say which one you found.
- Executors spawned by `--run` do see project files, CLAUDE.md, and memory. They do not see this conversation.

**The conversation is needed.** "The same as before", "the other three", "as we discussed".

- Grade what the earlier turns establish, not the bare sentence. If you cannot see them (the API path), say the verdict is provisional.
- `--run` cannot carry the conversation, so recommend in-session execution and, per the cache note in section 5, the session's current model unless the task clearly outgrows it.

## 2. Hard constraints (apply before anything else)

These come from documented limits, not from judgment. A constraint sets a floor or a ceiling that the scoring below cannot cross.

- **Context over 200K tokens**: Haiku is out (200K window). Prefer Opus 5.5 ("catches details that are easy to miss in large inputs") or Fable 5.1; both have a 1M window.
- **Images**: `images-simple` can go to Sonnet 5. `images-dense`, chart or diagram reading, UI replication, and computer use go to Opus 5.5, which "even at its lowest effort setting ... read values off dense charts more accurately than Claude Opus 5 did at its highest". For the densest technical drawings, give the executor higher-resolution images and a crop or zoom tool; raising effort helps drawings but "does little for charts".
- **Security content**: do not route to Fable 5.1 without a refusal fallback (its classifiers false-positive on benign security work). Opus 5.5's docs say "Finding vulnerabilities in source code is allowed. High-risk dual-use cybersecurity activities are not", so code review for vulnerabilities, auth-flow review, and dependency audits go to Opus 5.5 normally. For dual-use work (exploit development, fuzzing with exploitability triage, malware analysis, offensive tooling) expect possible declines on Fable and on Opus 5.5; route to Opus 5 (which still has a cybersecurity classifier, so say it is not guaranteed), name Sonnet 5 at xhigh as the classifier-free last resort, and recommend a fallback.
- **Biology or life-science content, even benign**: Fable 5.1 and Opus 5.5 run a biology classifier ("the same as Claude Fable 5.1's"); Opus 5 does not document one. Route to Opus 5, or Sonnet 5 at high when the work is within its reach, and mention the Life Sciences Verification Program for organizations that need Opus 5.5 or Fable.
- **Zero-data-retention org** (only if the caller says so): Fable 5.1 is unavailable. Cap at Opus 5.5.
- **Multi-day autonomy**: Fable 5.1 is the documented model for "multiday, goal-directed runs". Multi-hour audits and migrations "run end to end with parallel subagents and little oversight" are documented for Opus 5.5, so hours go to Opus 5.5 and days to Fable.
- **API pipelines that force a tool call** (`tool_choice` any/tool): not Fable 5.1 and not Opus 5.5 (both return 400). Use Opus 5 or Sonnet 5. **Pipelines that must run with thinking disabled**: not Fable 5.1 and not Opus 5.5; Opus 5 at effort high or below, or Sonnet 5.
- **Latency-sensitive interactive use**: prefer Sonnet 5 or Opus 5.5 (which is more than 30% faster than Opus 5) at low or medium. Fable turns on hard tasks run for minutes.

## 3. Choose the tier

Take `complexity = max(scope, horizon, ambiguity, reasoning)`. Use the max, not the sum: one deep dimension is enough to sink a small model, and four shallow ones do not add up to a hard task.

| complexity | Tier | Notes |
|---|---|---|
| 0 | Haiku 4.5 when no constraint blocks it and either (a) the task is a mechanical transform (case changes, format conversion, deterministic reshaping, labeling with a fixed label set) whose output a glance or a one-line check would verify, or (b) output_shape is `structured-short` and verification is `checker` or `human-review`. Otherwise Sonnet 5 at low. | Haiku's documented accuracy gap (63% vs 92% on knowledge questions) is acceptable only when a miss is cheap to spot. Having to read and write a file does not by itself call for Sonnet. |
| 1 | Sonnet 5 | Bounded coding, scripts, tests, summaries, drafting, extraction. Effort from section 4. |
| 2 | Opus 5.5 | The docs' model "for long-running agentic coding and knowledge work": multi-file coding, reviews, dense visuals, long context, financial and office deliverables, multi-app automation. Opus 5 only when a section 2 constraint names it. Exception: reasoning-heavy but short work with modest input (deep research, analysis with few tool calls) is a Fable-at-low candidate; see section 5. |
| 3 | Fable 5.1 | The hardest, most ambiguous, or longest-running (multiday) work. |

**Adjustments, applied in this order:**

1. **Step down one tier** when verification is `checker`, cost_of_error is `trivial` or `reversible`, and a re-run is cheap. Anthropic's runs: everything at low, failures re-run at the default, reached about 93% pass at about half the cost of running everything at the default. The verdict is then the cheap first attempt; name the tier you stepped down from in `escalate_if` as the re-run target. Never step below a hard-constraint floor.
2. **Step up one tier** when cost_of_error is `costly` and verification is `none` or `self-check`. Nobody will catch the mistake, so pay for fewer mistakes.
3. **Step up one tier** when two or more latent-difficulty markers are present and the tier came out at 0 or 1.
4. **Do not step down** just because the prompt is short. Prompt length is not task difficulty.

## 4. Choose the effort level

Sonnet 5, Opus 5, and Fable 5.1 default to high; Opus 5.5 defaults to medium. Start from the workload shape, then adjust by tier.

**By workload shape (measured by Anthropic):**

| Workload | Curve | Effort to use |
|---|---|---|
| Classification, extraction, chat, high-volume routes | flat | low |
| Research and knowledge work | nearly flat: low gave up 1 to 3 points for a third to a half off cost; medium matched the default at 70% to 85% of its cost | low or medium |
| Bounded coding with a checker | flat enough to re-run failures | low or medium first, escalate on failure |
| Long-horizon coding, multi-file features, agentic loops | a real trade-off on Opus 5 (about 2 points lost at medium for half the cost, about 8 at low for a quarter); on Opus 5.5, medium matches Opus 5 at high | Opus 5.5 at medium; high when unverified; xhigh only when demanding and measured |
| Reasoning-ceiling work (deep multi-subtopic research, hard debugging) | every step buys about 2.4 points | high or xhigh |
| Correctness matters more than cost, or the user asked for maximum capability | | max, with a note about diminishing returns and overthinking |

**Per-tier notes:**

- **Haiku 4.5**: no effort parameter; emit `null`.
- **Sonnet 5**: low for short, scoped, non-intelligence-sensitive work; medium when cost-sensitive and reasoning is at most 1; high for anything with reasoning or ambiguity at 2; xhigh for the hardest coding it should still handle. At low there is documented under-thinking risk on moderately complex tasks, so never pair low with reasoning 2.
- **Opus 5.5**: medium is the default and the starting point; it "matches or exceeds Claude Opus 5 at high on coding and knowledge-work evaluations". Low for coding with a checker, code review, chart and screenshot reading, and latency-sensitive routes ("on several coding evaluations low comes close" to medium). High for unverified multi-file agentic work. Xhigh and max only where a gain has been measured: it "tends to think more per turn than Claude Opus 5, especially at xhigh and max", and long turns need `max_tokens` up to 128,000.
- **Opus 5** (fallback only): start at high; use low and medium liberally where quality holds; xhigh for demanding coding and agentic work.
- **Fable 5.1**: high is the documented starting point. Medium roughly matches Fable 5. Low for research, analysis, and knowledge work where it is documented to beat smaller models on cost per task. Avoid xhigh and max for `long-deliverable` outputs (it drafts them twice); if the caller insists, tell them to raise `max_tokens` and add the docs' single-limit note.

## 5. Cross-tier check (do this before finalizing)

Compare your candidate against "one tier up at lower effort" and pick the cheaper likely-to-succeed cell:

- **Sonnet 5 at xhigh versus Opus 5.5 at medium**: for multi-file coding, prefer Opus 5.5 at medium. It costs twice Sonnet per token but is documented to finish "in fewer steps and with fewer tokens" than Opus 5 at high, which in turn matched Fable 5 on a coding subset at 60% of Fable's cost. Opus 5.5 at low is the cheaper first attempt when a checker exists.
- **Opus 5.5 at medium versus Fable 5.1 at low**: for knowledge work that rests on figures and sources, prefer Opus 5.5 at medium ("much less likely to state an incorrect figure or cite the wrong source", at 40% of Fable's token price). For reasoning-ceiling research (deep multi-subtopic synthesis), Fable at low is still the documented winner over Sonnet 5 and the Opus 5 generation on cost per task; treat it as the step-up from Opus 5.5 at medium, and let an eval decide. That saving comes from Fable finishing in fewer output and tool tokens, so it disappears when the input dominates: with `context_tokens` large, Fable's input rate is 2.5 times Opus 5.5's, and an exhaustive pass over a big corpus stays on Opus 5.5 unless reasoning is 3 or the costly-and-unverified step-up from section 3 applies. For coding, keep Opus 5.5.
- **Sonnet 5 at high versus Haiku**: never trade down to Haiku on an unverified task to save half a cent.
- **Opus 5 versus Opus 5.5**: Opus 5 only under a section 2 constraint. Otherwise it costs 25% more and is documented to do less.
- **Cache continuity**: prompt caches are model-scoped. If the prompt is a follow-up inside a long session on some model, switching models forfeits the cached prefix; stay on the session's model unless the saving is large or the task clearly outgrows it. Say so in `notes` when this applies. Thinking blocks survive a move from Opus 5 to Opus 5.5 to Fable 5.1, but not from Fable back down.

## 6. Confidence and the tie-break

Report `confidence` from 0 to 1 for the whole verdict. Below 0.6, step up (tier if the doubt is about capability, effort if it is about depth) and say in `why` that you stepped up for uncertainty. A low-confidence verdict that stays cheap is the one failure mode this skill exists to prevent.

## 7. Verdict format

Emit exactly these fields (the JSON schema is `scripts/verdict_schema.json`):

- `model`: model ID; `alias`: Claude Code alias; `tier`: 0 to 3.
- `effort`: `low` | `medium` | `high` | `xhigh` | `max`, or `null` for Haiku.
- `confidence`: 0 to 1.
- `signals`: the scores and categories from section 1, `dependencies` from section 1b, and `latent_markers`: the latent-difficulty phrases you found, quoted, or an empty list.
- `why`: two to four sentences. Name the deciding signal, the workload shape, and any adjustment or constraint that moved the verdict.
- `cheaper_alternative`: the next cheaper cell that could plausibly work, with `when` describing the condition, or `null` if there is none worth trying.
- `escalate_if`: concrete, observable conditions under which the caller should re-run one tier or one effort level up (a failing test suite after one pass, the change spreading beyond the named files, a refusal, an answer that cites nothing).
- `notes`: constraints that applied, fallback advice for Fable or Opus 5.5 picks, executor instructions worth passing on, cache-continuity remarks. Empty list if none.

Human-readable rendering (used when `--json` is not set):

```
model-grade -> Opus 5.5 @ medium   (confidence 0.80)
Why: ...
Cheaper: Sonnet 5 @ high -- when ...
Escalate if: ...
Signals: scope 2 | horizon 2 | ambiguity 1 | reasoning 1 | checker | medium ctx | code | depends on project
Notes: ...
```

## 8. Worked examples

**"Classify these 300 support tickets (attached CSV) as billing, bug, feature, or other. Output a CSV with ticket_id,label."**
scope 0, horizon 0, ambiguity 0, reasoning 0; checker (a schema and a human skim), structured-short, high-volume. Verdict: Haiku 4.5, effort null, confidence 0.85. Cheaper alternative: none. Escalate if: label distribution looks implausible or spot-checks show more than a few percent errors, then Sonnet 5 at low.

**"Add a --dry-run flag to scripts/cleanup.py that prints what would be deleted without deleting. Follow the existing argparse pattern. Run the tests."**
scope 1, horizon 1, ambiguity 0, reasoning 1; checker (tests), reversible, code-change. Verdict: Sonnet 5 at low, confidence 0.8. Escalate if tests fail after one pass: Sonnet 5 at high.

**"Summarize this 40-page transcript into decisions, owners, and deadlines."**
scope 1, horizon 0, ambiguity 1, reasoning 1; no checker, text, medium context. Verdict: Sonnet 5 at medium, confidence 0.75. Cheaper: Haiku, but only if a person will read the transcript anyway (unverified summaries need Sonnet's reliability).

**"Implement docs/spec-notifications.md: migration, service layer, REST endpoints, and the React inbox component. Tests in tests/ must pass."**
scope 2, horizon 2, ambiguity 1, reasoning 1; checker, reversible, code-change. Complexity 2, so Opus 5.5. Effort: multi-file coding with a checker; medium is the default and matches Opus 5 at high. Verdict: Opus 5.5 at medium, confidence 0.8. Cheaper alternative: Opus 5.5 at low, or Sonnet 5 at high, when the spec is tight and the test suite is trusted. Escalate if the suite still fails after one full pass: Opus 5.5 at high.

**"Review this 1,200-line PR touching our auth flow for bugs and security issues. Report everything you find."**
scope 2, horizon 1, ambiguity 1, reasoning 2; human-review, security flag. Finding vulnerabilities in source code is explicitly allowed on Opus 5.5, which reviews with "more bugs caught ... and fewer false alarms", and review accuracy holds at lower effort. Verdict: Opus 5.5 at low, confidence 0.8. Escalate to medium if the first pass reports fewer findings than the diff's size suggests. Notes: not Fable because of classifier false positives on benign security review.

**"Here's a screenshot of our Grafana dashboard during the incident. Which service caused the latency spike, and why?"**
scope 1, horizon 1, ambiguity 2, reasoning 2; images-dense, no checker. Dense-image floor is Opus 5.5, which reads charts at low better than Opus 5 at max. Verdict: Opus 5.5 at low, confidence 0.75. Escalate to medium with a crop tool if panel text is too small to read. Notes: raising effort does little for charts; resolution and cropping do.

**"Compare six vector databases on twelve criteria with sources and write a decision memo."**
scope 2, horizon 2, ambiguity 1, reasoning 2; research-synthesis, long-deliverable, no checker. Complexity 2 would say Opus 5.5, but the cross-tier check applies: this is reasoning-ceiling research with modest input, where Fable at low is documented to win on cost per task. Verdict: Fable 5.1 at low, confidence 0.7. Cheaper alternative: Opus 5.5 at medium, which is documented to cite sources more reliably, when the memo is more compilation than synthesis. Notes: at low effort Fable searches less, so instruct it to verify each product's current state with a search. Not xhigh or max: long deliverable.

**"Our scheduler has a rare deadlock we've been chasing for weeks. Repo attached plus three stack dumps. Find the root cause and fix it with a regression test."**
scope 2, horizon 2, ambiguity 2, reasoning 3; latent markers ("rare", "for weeks", "root cause"); checker (the regression test, once written). Complexity 3. Verdict: Fable 5.1 at high, confidence 0.8. Cheaper alternative: Opus 5.5 at xhigh. Escalate: none above this; if Fable stalls, split the problem.

**"Write a fuzzing harness for our image parser and triage the crashes it finds."**
scope 2, horizon 2, ambiguity 2, reasoning 2; security flag, dual-use shape. Complexity 2. A fuzzing harness is close to the "high-risk dual-use" line, so Fable is excluded and Opus 5.5 may decline the triage half. Verdict: Opus 5.5 at high, confidence 0.65. Notes: if it refuses, re-run on Opus 5 (the `mg-run-opus5` executor), which is not guaranteed either; Sonnet 5 at xhigh is the classifier-free last resort. Escalate to xhigh if the harness finds crashes it cannot classify.

**"Turn docs/q3-review.md into a 12-slide deck for the leadership meeting, using the slide-design skill."**
dependencies [skill]. The skill's scripts build the file and its rules constrain the design, so what remains is choosing the message for each slide: ambiguity 1, reasoning 1, horizon 2 from the skill's build-render-check loop; the user will look at it before the meeting. Verdict: Sonnet 5 at high, confidence 0.7. Cheaper: Sonnet 5 at medium when the source document already carries the narrative. Escalate to Opus 5.5 at medium if the rendered deck still has layout defects after one fix pass or the narrative needs restructuring. Not Fable: a rule-heavy skill is where the docs say Fable can do worse, and it would be over-commitment anyway.

**"Read the unread Gmail in the Clients label, make a Trello card on the Follow-ups board for each one that asks a question, and post a one-line summary of the new cards in Slack #client-ops."**
dependencies [tools], three systems; horizon 2 (capped: the chain is plumbing), ambiguity 1 (what counts as a question), reasoning 1; the Slack post is visible to others, so cost_of_error is costly and there is no checker. Complexity 2. Effort floor medium because tools are involved. Verdict: Opus 5.5 at medium, confidence 0.7. Cheaper: Sonnet 5 at high when the question rule is spelled out (it reaches for tools readily at high). Escalate if cards appear for messages that ask nothing or the summary is malformed: Opus 5.5 at high. Notes: instruct the executor to show the cards and the Slack line before writing them, and to explore the connected apps before acting; the connectors are deferred tools, so it searches for them first.

**"Fix the bug where invoice totals are off by the tax amount on refunds."** with context: a monorepo of about 2,400 files, a 40-minute test suite, no index.
dependencies [project]. Two lines against a large unfamiliar repo is a latent marker; refund tax handling is accounting logic, so reasoning 2; horizon 2. A checker exists but a re-run costs 40 minutes, so do not step down for it. Verdict: Opus 5.5 at medium, confidence 0.7. Cheaper: Sonnet 5 at high once the refund path is located and turns out to be small. Escalate to Opus 5.5 at high if the fix spreads beyond the refund calculation or tests fail after one pass.

**"Migrate our 300-module Python 2 code base to Python 3 over the next few hours with parallel subagents; keep the test suite green throughout."**
scope 3, horizon 3, ambiguity 1, reasoning 1; checker (the suite), reversible (a branch), code-change. Complexity 3 by scope and horizon, but the shape is exactly what the Opus 5.5 docs describe: "multi-hour audits and migrations of large code bases run end to end with parallel subagents and little oversight". Hours, not days, and a mechanical migration, not an unsolved problem. Verdict: Opus 5.5 at high, confidence 0.7. Cheaper: Opus 5.5 at medium when the suite is fast enough to re-run per module. Escalate to Fable 5.1 at high if the migration turns up design decisions the suite cannot adjudicate, or the run stalls repeatedly. Notes: give the executor a time budget line (elapsed seconds against a budget), which the docs say speeds up multi-agent work; and the unattended-run instruction so it does not stop to report.

## 9. Anti-patterns

- Grading by prompt length. A one-line prompt can be a three-week problem.
- Assuming "code" means Opus. A scoped edit with tests is Sonnet at low.
- Sending security-adjacent or bio work to Fable without a fallback, or bio work to Opus 5.5.
- Picking Opus 5 over Opus 5.5 without a constraint from section 2. It costs 25% more and is documented to do less.
- Pairing Sonnet at low with reasoning 2. The docs flag under-thinking there.
- Choosing xhigh or max on Fable for a long written deliverable, or on Opus 5.5 without a measured gain.
- Choosing Haiku for anything nobody will check.
- Ignoring the session: switching models mid-session throws away the cache; note it.
- Reporting a low-confidence verdict without stepping up.
- Grading a prompt that names a skill or a connector as if it were self-contained.
- Stepping up a tier to make a tool-writing task safer. A confirm-before-write instruction is the safety lever; a bigger model is not.
- Counting a long chain of routine tool calls as horizon 3.
