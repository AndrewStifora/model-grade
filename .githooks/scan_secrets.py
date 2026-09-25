#!/usr/bin/env python3
"""Scan files for secrets before they reach git. Part of the workflow kit (claude-setup).

  python .githooks/scan_secrets.py --staged          # staged changes (the pre-commit hook)
  python .githooks/scan_secrets.py --all             # every tracked file (CI)
  python .githooks/scan_secrets.py PATH [PATH ...]   # files or folders

Each finding prints as `rule  path:line  fingerprint  preview`, with the value masked, and
the exit code is 1. To accept a false positive, add a line to `.secrets-allow` at the
repository root, with a reason after `#`:

  sha256:3f2a9c0d11e4b7a8  # dev-only test value, documented in the note
  path:home/claude/skills/archify/**  # design tokens in HTML templates

A `sha256:` entry accepts one exact value anywhere. A `path:` entry silences only the
generic and sensitive-file rules for matching paths; provider-specific rules (Anthropic,
GitHub, Google, AWS, Slack, private keys, ...) can only be accepted by fingerprint.
Standard library only, Python 3.8 or later.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

MAX_BYTES = 5 * 1024 * 1024

PROVIDER_RULES = {
    "anthropic": r"sk-ant-[A-Za-z0-9_\-]{20,}",
    "openai": r"\bsk-(?!ant-)(?:proj-)?[A-Za-z0-9_\-]{32,}",
    "github": r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})",
    "google": r"\bAIza[0-9A-Za-z\-_]{35}\b",
    "slack": r"\bxox[abposr]-[A-Za-z0-9-]{10,}",
    "aws": r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b",
    "firecrawl": r"\bfc-[a-f0-9]{32}\b",
    "gohighlevel": r"\bpit-[a-f0-9]{8}-[a-f0-9\-]{20,}",
    "private-key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "jwt": r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}",
    "stripe": r"\b(?:sk|rk)_live_[0-9a-zA-Z]{20,}",
    "netlify": r"\bnfp_[A-Za-z0-9]{30,}",
    "huggingface": r"\bhf_[A-Za-z0-9]{30,}",
    "replicate": r"\br8_[A-Za-z0-9]{30,}",
    "elevenlabs": r"\bsk_[a-f0-9]{40,}\b",
    "telegram": r"\b\d{8,10}:AA[A-Za-z0-9_-]{33}\b",
}
# key = value, where the value is long, has a letter and a digit, and is not a placeholder.
GENERIC = re.compile(
    r"(?i)\b(?:api[_-]?key|secret|token|passwd|password|client[_-]?secret|access[_-]?key|auth[_-]?token)"
    r"[A-Za-z0-9_\-]*[\"']?\s*[:=]\s*[\"']?(?P<value>[A-Za-z0-9_\-./+=]{20,})"
)
PLACEHOLDER = re.compile(r"(?i)example|placeholder|your[_-]|xxxx|changeme|dummy|redacted|<secret")
SENSITIVE_NAMES = {".env", ".credentials.json", "id_rsa", "id_ed25519", "id_ecdsa", "id_dsa"}
SENSITIVE_SUFFIXES = (".pem", ".key", ".p12", ".pfx")
SENSITIVE_OK = {".env.example", ".env.sample", ".env.template"}

RULES = {name: re.compile(rx) for name, rx in PROVIDER_RULES.items()}


def fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def mask(value: str) -> str:
    return f"{value[:4]}...({len(value)} chars)"


def git(repo: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True).stdout


def load_allow(repo: Path):
    hashes, paths = set(), []
    allow = repo / ".secrets-allow"
    if allow.is_file():
        for raw in allow.read_text(encoding="utf-8").splitlines():
            line = raw.split("#", 1)[0].strip()
            if line.startswith("sha256:"):
                hashes.add(line[7:].strip().lower())
            elif line.startswith("path:"):
                paths.append(line[5:].strip())
    return hashes, paths


def path_allowed(rel: str, patterns) -> bool:
    return any(fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(rel, p.rstrip("*").rstrip("/") + "/*") for p in patterns)


def sensitive_file(rel: str) -> bool:
    name = rel.rsplit("/", 1)[-1]
    if name in SENSITIVE_OK:
        return False
    return name in SENSITIVE_NAMES or name.startswith(".env.") or name.endswith(SENSITIVE_SUFFIXES)


def scan_text(rel: str, data: bytes, hashes, paths):
    findings = []
    if sensitive_file(rel) and not path_allowed(rel, paths):
        findings.append(("sensitive-file", rel, 0, fingerprint(rel), rel))
    if b"\0" in data[:8000] or len(data) > MAX_BYTES:
        return findings
    text = data.decode("utf-8", errors="replace")
    generic_ok = path_allowed(rel, paths)
    for number, line in enumerate(text.splitlines(), 1):
        for name, rx in RULES.items():
            for match in rx.finditer(line):
                value = match.group(0)
                if fingerprint(value) not in hashes:
                    findings.append((name, rel, number, fingerprint(value), mask(value)))
        if generic_ok:
            continue
        for match in GENERIC.finditer(line):
            value = match.group("value")
            if PLACEHOLDER.search(value) or not re.search(r"\d", value) or not re.search(r"[A-Za-z]", value):
                continue
            if fingerprint(value) not in hashes:
                findings.append(("generic", rel, number, fingerprint(value), mask(value)))
    return findings


def staged(repo: Path):
    names = git(repo, "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z").split(b"\0")
    for raw in names:
        if raw:
            rel = raw.decode("utf-8")
            yield rel, git(repo, "show", f":{rel}")


def tracked(repo: Path):
    for raw in git(repo, "ls-files", "-z").split(b"\0"):
        if raw:
            rel = raw.decode("utf-8")
            path = repo / rel
            if path.is_file():
                yield rel, path.read_bytes()


def walk(repo: Path, targets):
    for target in targets:
        target = Path(target).resolve()
        files = [target] if target.is_file() else [p for p in target.rglob("*") if p.is_file() and ".git" not in p.parts]
        for path in files:
            try:
                rel = path.relative_to(repo).as_posix()
            except ValueError:
                rel = path.as_posix()
            yield rel, path.read_bytes()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--staged", action="store_true", help="scan the staged versions of changed files")
    group.add_argument("--all", action="store_true", help="scan every tracked file")
    parser.add_argument("--repo", type=Path, default=None, help="repository root (default: the one containing the current folder)")
    parser.add_argument("paths", nargs="*", help="files or folders to scan")
    args = parser.parse_args(argv)
    start = args.repo or Path.cwd()
    try:
        repo = Path(git(start, "rev-parse", "--show-toplevel").decode().strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        repo = start.resolve()
    hashes, paths = load_allow(repo)
    if args.staged:
        source = staged(repo)
    elif args.all:
        source = tracked(repo)
    elif args.paths:
        source = walk(repo, args.paths)
    else:
        parser.error("give --staged, --all, or paths")
    findings, files = [], 0
    for rel, data in source:
        files += 1
        findings += scan_text(rel, data, hashes, paths)
    for rule, rel, line, fp, preview in findings:
        where = f"{rel}:{line}" if line else rel
        print(f"{rule:14} {where}  sha256:{fp}  {preview}")
    if findings:
        print(f"\n{len(findings)} possible secret(s) in {files} file(s). Remove them, or accept a false positive in .secrets-allow.", file=sys.stderr)
        return 1
    print(f"secret scan: {files} file(s), nothing found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
