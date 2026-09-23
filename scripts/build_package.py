#!/usr/bin/env python3
"""Build the distributable zip, or print the changelog notes for a version.

  python scripts/build_package.py --out dist/model-grade-install.zip   # zip with a model-grade/ top folder
  python scripts/build_package.py --notes 1.2.0                        # the CHANGELOG section for that version

The zip is what INSTALL.md's drag-and-drop route and the update scripts consume: one
top-level folder containing SKILL.md. It leaves out .git, .github, caches, and dist.
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".github", "__pycache__", "docs-cache", "dist"}


def build(out: Path, top: str) -> int:
    out.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(ROOT.rglob("*")):
            rel = path.relative_to(ROOT)
            if not path.is_file() or any(part in SKIP_DIRS for part in rel.parts) or path.suffix == ".pyc":
                continue
            archive.write(path, f"{top}/{rel.as_posix()}")
            count += 1
    return count


def notes(version: str) -> str:
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    match = re.search(rf"^## {re.escape(version)} .*?$(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not match:
        raise SystemExit(f"CHANGELOG.md has no section for {version}")
    return match.group(1).strip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, help="zip path to write")
    parser.add_argument("--top", default="model-grade", help="name of the top-level folder inside the zip")
    parser.add_argument("--notes", metavar="VERSION", help="print the CHANGELOG section for VERSION and exit")
    args = parser.parse_args(argv)
    if args.notes:
        sys.stdout.write(notes(args.notes))
        return 0
    if not args.out:
        parser.error("give --out PATH or --notes VERSION")
    count = build(args.out, args.top)
    print(f"{count} files -> {args.out} ({args.out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
