#!/usr/bin/env python3
"""Refresh the Anthropic documentation this skill is built from and report what changed.

Tracked pages live in references/sources.json (url, title, sha256, fetched date).
Discovery reads https://platform.claude.com/llms.txt and picks up every page under
/build-with-claude/prompt-engineering/ plus each model's overview and what's-new
page under /models/<model>/, so a newly released model shows up as NEW without
anyone editing a list. The raw Markdown of every page is cached in
references/docs-cache/ (git-ignored: the pages are Anthropic's, the repository
stores only hashes), and a unified diff of each changed page is written to
references/docs-cache/changes/.

Usage
  python refresh_docs.py              report only; exit 0 = nothing changed, 3 = NEW or CHANGED pages
  python refresh_docs.py --write      also update sources.json and the cache
  python refresh_docs.py --add URL    track an extra page (repeatable)
  python refresh_docs.py --no-discover   skip llms.txt discovery, refresh tracked pages only

Standard library only.
"""

from __future__ import annotations

import argparse
import datetime
import difflib
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
MANIFEST = SKILL / "references" / "sources.json"
CACHE = SKILL / "references" / "docs-cache"
LLMS_TXT = "https://platform.claude.com/llms.txt"
DISCOVER = [
    re.compile(r"^https://platform\.claude\.com/docs/en/build-with-claude/prompt-engineering/[^/)\s]+\.md$"),
    re.compile(r"^https://platform\.claude\.com/docs/en/models/[^/)\s]+/(overview|whats-new-[^/)\s]+)\.md$"),
]


def fetch(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "model-grade-refresh/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def slug(url: str) -> str:
    return url.split("/docs/en/")[-1].replace("/", "__")


def discover() -> dict[str, str]:
    text = fetch(LLMS_TXT).decode("utf-8", "replace")
    found: dict[str, str] = {}
    for match in re.finditer(r"\[([^\]]+)\]\((https://[^)\s]+)\)", text):
        title, url = match.group(1), match.group(2)
        if any(pattern.match(url) for pattern in DISCOVER):
            found.setdefault(url, title)
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true", help="update sources.json and the cache")
    parser.add_argument("--cache-only", action="store_true", help="refresh the cache (so the next run can diff) but leave sources.json alone; used by the scheduled check")
    parser.add_argument("--add", action="append", default=[], help="extra page URL to track")
    parser.add_argument("--no-discover", action="store_true", help="skip llms.txt discovery")
    args = parser.parse_args(argv)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {"pages": []}
    tracked = {p["url"]: p for p in manifest.get("pages", [])}
    discovered = {} if args.no_discover else discover()
    for url in args.add:
        discovered.setdefault(url, url.rsplit("/", 1)[-1])
    urls = list(tracked) + [u for u in discovered if u not in tracked]

    today = datetime.date.today().isoformat()
    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / "changes").mkdir(exist_ok=True)

    new: list[str] = []
    changed: list[tuple[str, int, int]] = []
    unchanged = 0
    failed: list[tuple[str, str]] = []
    pages_out: list[dict] = []

    for url in urls:
        prior = tracked.get(url)
        try:
            body = fetch(url)
        except Exception as exc:  # network or 404
            failed.append((url, str(exc)))
            if prior:
                pages_out.append(prior)
            continue
        digest = sha256(body)
        name = slug(url)
        cached = CACHE / name
        title = (prior or {}).get("title") or discovered.get(url) or name
        entry = {"url": url, "title": title, "sha256": digest, "fetched": today}

        if prior is None:
            new.append(url)
        elif prior.get("sha256") != digest:
            added = removed = 0
            if cached.exists():
                old_lines = cached.read_text(encoding="utf-8", errors="replace").splitlines()
                new_lines = body.decode("utf-8", "replace").splitlines()
                diff = list(difflib.unified_diff(old_lines, new_lines, "previous", "current", lineterm="", n=2))
                (CACHE / "changes" / f"{name}.diff").write_text("\n".join(diff) + "\n", encoding="utf-8")
                added = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
                removed = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
            changed.append((url, added, removed))
        else:
            unchanged += 1
            entry["fetched"] = prior.get("fetched", today)

        if args.write or args.cache_only:
            cached.write_bytes(body)
        pages_out.append(entry if args.write else (prior or entry))

    print(f"model-grade docs refresh, {today}")
    print(f"NEW ({len(new)}):")
    for url in new:
        print(f"  {url}   \"{discovered.get(url, '')}\"")
    print(f"CHANGED ({len(changed)}):")
    for url, added, removed in changed:
        note = f"+{added}/-{removed} lines, diff in references/docs-cache/changes/{slug(url)}.diff" if (added or removed) else "no cached copy to diff against"
        print(f"  {url}   ({note})")
    print(f"UNCHANGED: {unchanged}")
    if failed:
        print(f"FAILED ({len(failed)}):")
        for url, err in failed:
            print(f"  {url}   {err}")

    if args.write:
        MANIFEST.write_text(json.dumps({"fetched": today, "discovery": LLMS_TXT, "pages": pages_out}, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {MANIFEST.relative_to(SKILL)} and refreshed {CACHE.relative_to(SKILL)}/")
    elif new or changed:
        print("report only; re-run with --write after you have read the changes")

    if new or changed:
        print("next: work through references/UPDATING.md for each NEW or CHANGED page")
        return 3
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass
    sys.exit(main())
