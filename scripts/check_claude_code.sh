#!/usr/bin/env bash
# Compares the installed Claude Code CLI with the version this model-grade release is built for
# (CLAUDE_CODE_VERSION at the skill root) and recommends `claude update` when the CLI is older.
#   bash check_claude_code.sh              (checks the skill folder this script sits in)
#   bash check_claude_code.sh <skill dir>
# Never fails: a missing CLI or an unreadable version only skips the check. update.sh runs it last.
skill="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
file="$skill/CLAUDE_CODE_VERSION"
[ -f "$file" ] || exit 0
want="$(tr -d '[:space:]' < "$file")"

if ! command -v claude >/dev/null 2>&1; then
  echo "Claude Code check skipped: the claude CLI is not on PATH (model-grade is built for $want or later)."
  exit 0
fi
have="$(claude --version 2>/dev/null | grep -Eo '[0-9]+\.[0-9]+\.[0-9]+' | head -1)"
if [ -z "$have" ]; then
  echo "Claude Code check skipped: 'claude --version' did not report a version (model-grade is built for $want or later)."
  exit 0
fi

# Exit 0 when $1 is an older MAJOR.MINOR.PATCH than $2.
older() {
  awk -v a="$1" -v b="$2" 'BEGIN { split(a, x, "."); split(b, y, ".")
    for (i = 1; i <= 3; i++) { if (x[i] + 0 < y[i] + 0) exit 0; if (x[i] + 0 > y[i] + 0) exit 1 }
    exit 1 }'
}
if older "$have" "$want"; then
  echo "Claude Code $have is older than $want, the version this model-grade release is built for. Run 'claude update'."
  echo "Older versions can resolve the model aliases (sonnet, opus) to earlier models than the ones the rubric routes to, so --run may not get the model its verdict names."
else
  echo "Claude Code $have (model-grade is built for $want or later): ok"
fi
exit 0
