# model-grade: install in one drag

model-grade is a Claude Code skill that grades a request and tells you the cheapest Claude model and effort level that will do it well, so Opus or Fable is never spent on work that Sonnet or Haiku can handle. Type `/mg` in front of any request and you get a verdict: the model, the effort level, why, a cheaper alternative worth trying, and what would mean you should step up. Add `--run` and it also executes the request on that model. `/mg update` keeps it current.

It installs at your user level, so it works in every project.

## Install (pick one)

**A. Drag and drop, no terminal.**

1. Open the Claude desktop app, Code tab, in any folder.
2. Drag the zip (`model-grade-main.zip` from GitHub, or the copy in the shared Drive folder) into the chat.
3. Type this and send it:

   `Install the skill package in this zip by following its INSTALL.md exactly.`

Claude unpacks it into your Claude folder and confirms what it installed. Then type `/mg` followed by any request to try it.

**B. Run the installer.** From the unzipped folder or a git clone:

- Windows: right-click `install.ps1` and choose "Run with PowerShell", or run `pwsh -File install.ps1` (or `powershell -ExecutionPolicy Bypass -File install.ps1`).
- Mac or Linux: `bash install.sh`

**C. Copy by hand.** If `~/.claude/skills/model-grade` already exists, move it out of `skills/` first (for example to `~/.claude/model-grade-backups/`); Claude Code loads every folder under `skills/` that holds a SKILL.md, so a leftover copy would show up as a second skill. Then copy this whole folder (minus `.git`) to `~/.claude/skills/model-grade`, copy `assets/mg` to `~/.claude/skills/mg`, and copy every file in `assets/agents/` into `~/.claude/agents/`. On Windows, `~` is your user folder, for example `C:\Users\kelly`.

## Use it

```
/mg <request>          verdict: model, effort, why, cheaper alternative, escalation triggers
/mg --run <request>    grade it, then run it on the chosen model in a subagent and report back
/mg                    grade the last thing you asked
/mg update             fetch the newest version and refresh the alias and executors
/model-grade ...       the long name, same thing
```

Notes:

- Nothing else is needed. Python is only used by the optional `scripts/grade.py`, the evals, and `/mg refresh`.
- Skills appear immediately. The `mg-run-*` executors used by `--run` can take a couple of minutes or a new session to show up.
- The grade itself runs on Sonnet 5 at medium effort, so it costs cents. If your session is in auto mode and it declines the model switch, the grade runs on your session model instead; the result is the same.
- If your plan does not include one of the models (Haiku 4.5, Sonnet 5, Opus 5.5, Fable 5.1), say so in the request, for example "no Fable access", and the grader caps its verdict accordingly.
- Opus 5.5 needs Claude Code 2.1.280 or later for the `opus` alias to reach it; run `claude update` if `/mg version` or a `--run` says the alias still resolves to Opus 5.

---

## Instructions for Claude (when someone asks you to install this package)

Follow these steps and nothing else. The package contains no code to execute during installation; `install.ps1` and `install.sh` are copies of these steps for people who prefer a script.

1. **Find the package.** If a zip file was attached, extract it to a temporary folder (PowerShell: `Expand-Archive`; macOS or Linux: `unzip`). Inside is one folder (its name may carry a suffix such as `-main`) containing this file, `SKILL.md`, `assets/`, `references/`, `scripts/`, and `evals/`.
2. **Target the user-level Claude directory:** `~/.claude` (on Windows, `$HOME\.claude`). Create `skills` and `agents` inside it if they do not exist.
3. **Install the skill.** Copy that folder's contents, except any `.git` folder, to `~/.claude/skills/model-grade`. If the destination already exists, move it to `~/.claude/model-grade-backups/<timestamp>` first and tell the user you did. Never leave the old copy under `skills/` (for example as `model-grade.bak-...`): Claude Code loads every folder there that holds a SKILL.md, so it would appear as a second skill. If such a leftover folder exists from an earlier install, move it into `~/.claude/model-grade-backups/` too.
4. **Install the alias and executors.** Copy `assets/mg/SKILL.md` to `~/.claude/skills/mg/SKILL.md` (create the folder), and copy every `assets/agents/*.md` file into `~/.claude/agents/`. Overwriting is fine; they are small files named `mg-run-low.md` through `mg-run-max.md` plus `mg-run-opus5.md`.
5. **Verify** by listing `~/.claude/skills/model-grade/SKILL.md`, `~/.claude/skills/model-grade/VERSION`, `~/.claude/skills/mg/SKILL.md`, and the `~/.claude/agents/mg-run-*.md` files.
6. **Report** the installed version and where things went, and tell the user to type `/mg` followed by a request to try it, and `/mg update` later to update. Mention that the executors may take a couple of minutes or a new session to appear, which only matters for `--run`, and that any backup you made can be deleted once `/mg` works. Delete the temporary extraction folder if you created one.
