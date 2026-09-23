#!/usr/bin/env bash
# Updates the installed model-grade skill to the newest published version.
#   bash update.sh                 (git pull if the skill is a git clone, otherwise download the repo zip)
#   bash update.sh v1.2.0          (a tag or branch; default main)
# Testing hooks: MODEL_GRADE_HOME=<fake .claude dir>, MODEL_GRADE_ZIP=<local zip>, MODEL_GRADE_REPO=<repo url>.
set -euo pipefail
ref="${1:-main}"
repo="${MODEL_GRADE_REPO:-https://github.com/AndrewStifora/model-grade}"
target="${MODEL_GRADE_HOME:-$HOME/.claude}"
skill="$target/skills/model-grade"
# Previous copies go under $target/model-grade-backups, never beside the skill, where
# Claude Code would load them as a second skill.
bakroot="$target/model-grade-backups"

# Run from the installed copy, this script sits inside the folder about to be replaced, and
# Windows refuses to move a folder that holds an open file. So re-run from a temporary copy.
if [ -z "${MODEL_GRADE_REEXEC:-}" ]; then
  self="$(cd "$(dirname "$0")" && pwd -P)/$(basename "$0")"
  case "$self" in "$skill"/*)
    tmpself="$(mktemp)"; cp "$self" "$tmpself"
    MODEL_GRADE_REEXEC=1 exec bash "$tmpself" "$@" ;;
  esac
else
  trap 'rm -f "$0"' EXIT
fi
before="unknown"; [ -f "$skill/VERSION" ] && before="$(tr -d '[:space:]' < "$skill/VERSION")"

if [ -d "$skill/.git" ]; then
  echo "git clone detected, pulling $ref from origin"
  git -C "$skill" fetch --quiet origin
  git -C "$skill" checkout --quiet "$ref"
  git -C "$skill" pull --ff-only --quiet origin "$ref"
else
  tmp="$(mktemp -d)"
  if [ -n "${MODEL_GRADE_ZIP:-}" ]; then
    zip="$MODEL_GRADE_ZIP"
  else
    zip="$tmp/model-grade.zip"
    case "$ref" in v[0-9]*|[0-9]*) url="$repo/archive/refs/tags/$ref.zip" ;; *) url="$repo/archive/refs/heads/$ref.zip" ;; esac
    echo "downloading $url"
    curl -fsSL "$url" -o "$zip"
  fi
  if command -v unzip >/dev/null 2>&1; then unzip -q "$zip" -d "$tmp"; else python3 -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "$zip" "$tmp"; fi
  src="$(find "$tmp" -maxdepth 2 -name SKILL.md -printf '%h\n' 2>/dev/null | head -1 || true)"
  if [ -z "$src" ]; then src="$(dirname "$(find "$tmp" -maxdepth 2 -name SKILL.md | head -1)")"; fi
  [ -f "$src/SKILL.md" ] || { echo "the archive does not contain a SKILL.md at its top level" >&2; exit 1; }
  if [ -e "$skill" ]; then
    bak="$bakroot/$(date +%Y%m%d-%H%M%S)"; mkdir -p "$bakroot"; mv "$skill" "$bak"; echo "previous version moved to $bak"
  fi
  mkdir -p "$(dirname "$skill")"
  cp -R "$src" "$skill"
  rm -rf "$tmp"
fi

# Backups made by 1.2.0 sat beside the skill; move them out of skills/ too.
for old in "$target"/skills/model-grade.bak-*; do
  [ -e "$old" ] || continue
  mkdir -p "$bakroot"; mv "$old" "$bakroot/"; echo "leftover $(basename "$old") moved to $bakroot"
done

# The alias and the executors live outside the skill folder; refresh them from assets.
mkdir -p "$target/skills/mg" "$target/agents"
cp "$skill/assets/mg/SKILL.md" "$target/skills/mg/SKILL.md"
cp "$skill"/assets/agents/*.md "$target/agents/"

after="$(tr -d '[:space:]' < "$skill/VERSION")"
echo
echo "model-grade $before -> $after   ($skill)"
echo "alias /mg and executors mg-run-* refreshed in $target/skills/mg and $target/agents"
[ -f "$skill/CHANGELOG.md" ] && { echo; head -25 "$skill/CHANGELOG.md"; }
