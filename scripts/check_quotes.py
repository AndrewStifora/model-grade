#!/usr/bin/env python3
"""Check that the passages quoted in the profiles and the rubric still appear in Anthropic's pages.

Anthropic rewords its pages between releases, and a quote that was verbatim when it was
written can go stale without the fact behind it changing. This script reads every
double-quoted passage of 30 or more characters in references/model-profiles.md and
references/rubric.md and looks for it in the cached pages under references/docs-cache/.
"..." and "[...]" split a passage into fragments, and each fragment of 12 or more
characters has to appear in one page. Typographic quotes, Markdown links, backticks and
emphasis are ignored on both sides. The worked-example prompts in the rubric are not docs
quotes, so lines that open with a bold quoted prompt are skipped.

Run it after `python scripts/refresh_docs.py --write` (or `--cache-only`), which fills the
cache. Exit 0 when every passage is found, 1 when one is missing, 2 when the cache is empty.

Standard library only.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "references" / "docs-cache"
FILES = ("references/model-profiles.md", "references/rubric.md")
MIN_QUOTE = 30
MIN_FRAGMENT = 12


def norm(text: str) -> str:
    for old, new in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'),
                     ("–", "-"), ("—", "-"), ("\\_", "_")):
        text = text.replace(old, new)
    text = re.sub(r"<sup>.*?</sup>", "", text)  # footnote markers
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # Markdown links -> their text
    text = text.replace("`", "").replace("*", "")
    return re.sub(r"\s+", " ", text).lower()


def main() -> int:
    pages = sorted(CACHE.glob("*.md")) if CACHE.exists() else []
    if not pages:
        print("references/docs-cache/ is empty; run `python scripts/refresh_docs.py --cache-only` first")
        return 2
    sources = {page.name: norm(page.read_text(encoding="utf-8", errors="replace")) for page in pages}

    checked = missing = 0
    for name in FILES:
        for lineno, line in enumerate((ROOT / name).read_text(encoding="utf-8").splitlines(), 1):
            if line.startswith('**"'):
                continue
            # Quote marks pair up left to right, so the passages are the odd-numbered pieces.
            for quote in line.split('"')[1::2]:
                if len(quote) < MIN_QUOTE:
                    continue
                for fragment in re.split(r"\s*\.\.\.\s*|\[[^\]]*\]", quote):
                    fragment = fragment.strip(" .,;:")
                    if len(fragment) < MIN_FRAGMENT:
                        continue
                    checked += 1
                    needle = norm(fragment)
                    if not any(needle in body for body in sources.values()):
                        missing += 1
                        print(f"MISSING {name}:{lineno}: {fragment[:140]}")
    print(f"{checked} quoted passages checked against {len(sources)} cached pages, {missing} not found")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
