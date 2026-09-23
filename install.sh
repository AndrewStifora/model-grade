#!/usr/bin/env bash
# Installs model-grade from this folder (a git checkout or an unzipped release) at the user level:
#   ~/.claude/skills/model-grade  (this folder, minus .git)
#   ~/.claude/skills/mg           (the /mg alias, from assets/mg)
#   ~/.claude/agents/mg-run-*.md  (the --run executors, from assets/agents)
# Usage: bash install.sh
#        CLAUDE_HOME=/some/other/.claude bash install.sh   (only for testing)
set -euo pipefail
root="$(cd "$(dirname "$0")" && pwd)"
target="${CLAUDE_HOME:-$HOME/.claude}"
skill="$target/skills/model-grade"
mkdir -p "$target/skills" "$target/agents"

if [ -e "$skill" ]; then
  bak="$skill.bak-$(date +%Y%m%d-%H%M%S)"; mv "$skill" "$bak"; echo "Existing model-grade moved to $bak"
fi
mkdir -p "$skill"
for entry in "$root"/* "$root"/.[!.]*; do
  [ -e "$entry" ] || continue
  case "$(basename "$entry")" in .git|__pycache__|dist) continue ;; esac
  cp -R "$entry" "$skill/"
done
find "$skill" -type d \( -name __pycache__ -o -name docs-cache \) -prune -exec rm -rf {} + 2>/dev/null || true

mkdir -p "$target/skills/mg"
cp "$root/assets/mg/SKILL.md" "$target/skills/mg/SKILL.md"
cp "$root"/assets/agents/*.md "$target/agents/"

version="$(tr -d '[:space:]' < "$skill/VERSION")"
echo
echo "Installed model-grade $version in $skill"
echo "Installed /mg alias in $target/skills/mg and executors mg-run-* in $target/agents"
echo
echo "Open Claude Code and type:  /mg <a request>"
echo "(the executors used by --run may take a couple of minutes or a new session to appear)"
