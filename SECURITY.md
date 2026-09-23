# Security

## What this skill does with your data

- **Grading** sends the prompt you are grading, plus the rubric, to Claude through your own Claude Code login or API key. Nothing is sent anywhere else, and the skill keeps no record of prompts.
- **`--run`** hands the prompt to a Claude Code subagent on the chosen model. That subagent has the same tools and permissions as any subagent in your session, so the usual Claude Code permission rules apply to what it can read, write, or execute.
- **`update`** downloads a zip of this repository over HTTPS from GitHub (or runs `git pull` when the skill folder is a clone), backs up the current folder, and replaces it. It runs no code from the download during the update; it copies files.
- **`refresh`** fetches public pages from `platform.claude.com` and writes them to a git-ignored local cache.
- The scripts use only the Python standard library, except `scripts/grade.py`'s optional API backend, which uses the official `anthropic` SDK if you install it.

The prompt you grade is treated as data. The rubric tells the grader that instructions inside the prompt are to be graded, not followed, and Anthropic documents the current models as resistant to instructions arriving through content. Still, a grade is a model's judgment: review a verdict before acting on it for anything costly.

## Reporting a vulnerability

If you find a way this skill could leak data, execute something it should not, or be made to install code it did not download from this repository, please report it privately through GitHub's private vulnerability reporting on this repository (Security tab, "Report a vulnerability"). If that is not enabled, open an issue that says only that you have a security report and how to reach you, without details, and the maintainer will follow up.

Reports about the quality of a verdict are not security issues; use the "Verdict disagreement" issue template for those.
