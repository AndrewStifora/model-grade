#!/usr/bin/env bash
# Installs model-grade from this folder (a git checkout or an unzipped release) at the user level:
#   ~/.claude/skills/model-grade  (this folder, minus .git)
#   ~/.claude/skills/mg           (the /mg alias, from assets/mg)
# The --run executors in assets/agents load through .claude-plugin/plugin.json: Claude Code (2.1.157+)
# loads a skills folder holding that manifest as the plugin model-grade@skills-dir. They are copied to
# ~/.claude/agents only for a copy without the manifest; with it, copies would list each executor twice.
# Usage: bash install.sh
#        CLAUDE_HOME=/some/other/.claude bash install.sh   (only for testing)
set -euo pipefail
root="$(cd "$(dirname "$0")" && pwd -P)"
target="${CLAUDE_HOME:-$HOME/.claude}"
skill="$target/skills/model-grade"
mkdir -p "$target/skills"

# A previous copy is kept under $target/model-grade-backups, never beside the skill:
# Claude Code loads every folder under skills/ that holds a SKILL.md, so a leftover
# copy there would show up as a second skill.
bakroot="$target/model-grade-backups"
if [ -d "$skill" ] && [ "$(cd "$skill" && pwd -P)" = "$root" ]; then
  # The git route: this folder already is ~/.claude/skills/model-grade, so only the alias and executors are placed.
  echo "Installing from $skill itself; the skill folder stays as it is"
else
  if [ -e "$skill" ]; then
    bak="$bakroot/$(date +%Y%m%d-%H%M%S)"; mkdir -p "$bakroot"; mv "$skill" "$bak"; echo "Existing model-grade moved to $bak"
  fi
  mkdir -p "$skill"
  for entry in "$root"/* "$root"/.[!.]*; do
    [ -e "$entry" ] || continue
    case "$(basename "$entry")" in .git|.githooks|.claude|__pycache__|dist) continue ;; esac
    cp -R "$entry" "$skill/"
  done
  find "$skill" -type d \( -name __pycache__ -o -name docs-cache \) -prune -exec rm -rf {} + 2>/dev/null || true
fi
for old in "$target"/skills/model-grade.bak-*; do
  [ -e "$old" ] || continue
  mkdir -p "$bakroot"; mv "$old" "$bakroot/"; echo "Leftover $(basename "$old") moved to $bakroot"
done

mkdir -p "$target/skills/mg"
cp "$root/assets/mg/SKILL.md" "$target/skills/mg/SKILL.md"
if [ -f "$skill/.claude-plugin/plugin.json" ]; then
  # Earlier releases copied the executors into agents/ as well; move those copies out.
  moved=""
  for f in "$skill"/assets/agents/*.md; do
    old="$target/agents/$(basename "$f")"
    [ -e "$old" ] || continue
    if [ -z "$moved" ]; then moved="$bakroot/$(date +%Y%m%d-%H%M%S)-agents"; mkdir -p "$moved"; fi
    mv "$old" "$moved/"
  done
  if [ -n "$moved" ]; then echo "Executor copies from an earlier install moved to $moved"; fi
  executors="executors model-grade:mg-run-* load from the plugin manifest"
else
  mkdir -p "$target/agents"
  cp "$skill"/assets/agents/*.md "$target/agents/"
  executors="executors mg-run-* in $target/agents"
fi

version="$(tr -d '[:space:]' < "$skill/VERSION")"
echo
echo "Installed model-grade $version in $skill"
echo "Installed /mg alias in $target/skills/mg; $executors"
echo
echo "Open Claude Code and type:  /mg <a request>"
echo "(the executors used by --run may take a couple of minutes or a new session to appear)"
