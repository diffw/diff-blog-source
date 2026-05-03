#!/usr/bin/env python3
"""Normalize macOS filesystem birthtime + mtime of all blog posts to the
`date:` field in their front matter.

Why this exists: every time the GitHub Actions bot pushes translation
commits back to this repo, `git pull` on the user's Mac rewrites the
files. APFS resets the birthtime of rewritten files, so Obsidian's
"Sort by Created time (new to old)" stops reflecting the post's actual
publish date and instead clusters everything at the moment of the last
pull. This script fixes that by parsing each post's `date:` and pushing
both birthtime and mtime to that value.

Run manually any time, or wire into a git post-merge hook to make it
self-healing on every pull.
"""
from __future__ import annotations

import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
FRONT_MATTER_RE = re.compile(rb"^---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)


def parse_date(fm: dict) -> datetime | None:
    raw = fm.get("date")
    if raw is None:
        return None
    if isinstance(raw, datetime):
        return raw
    s = str(raw).strip()
    # Try ISO 8601 with offset, then date-only, then a couple of fallbacks.
    for fmt in (
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            dt = datetime.strptime(s, fmt)
            return dt
        except ValueError:
            continue
    return None


def file_dates(path: Path) -> tuple[datetime | None, dict]:
    raw = path.read_bytes()
    m = FRONT_MATTER_RE.match(raw)
    if not m:
        return None, {}
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return None, {}
    if not isinstance(fm, dict):
        return None, {}
    return parse_date(fm), fm


def set_birthtime_and_mtime(path: Path, when: datetime) -> None:
    # Naive (no tz) for SetFile; treat as local-time wall clock.
    if when.tzinfo is not None:
        when = when.astimezone().replace(tzinfo=None)
    # SetFile expects "MM/DD/YYYY HH:MM:SS"
    setfile_str = when.strftime("%m/%d/%Y %H:%M:%S")
    subprocess.run(
        ["SetFile", "-d", setfile_str, "-m", setfile_str, str(path)],
        check=True,
        capture_output=True,
    )
    # Also set POSIX mtime/atime via utime (SetFile -m is the macOS-specific
    # modified date which Finder shows but some POSIX tools ignore; setting
    # both keeps everything in sync).
    ts = time.mktime(when.timetuple())
    import os
    os.utime(path, (ts, ts))


def main() -> int:
    candidates = sorted(REPO_ROOT.glob("*.md")) + sorted((REPO_ROOT / "pages").glob("*.md"))
    candidates = [p for p in candidates if p.is_file()]

    fixed = 0
    skipped = 0
    failed = 0

    for path in candidates:
        when, _fm = file_dates(path)
        if when is None:
            skipped += 1
            continue
        try:
            set_birthtime_and_mtime(path, when)
            fixed += 1
        except subprocess.CalledProcessError as exc:
            print(f"FAIL {path.name}: SetFile failed: {exc.stderr.decode().strip()}", file=sys.stderr)
            failed += 1
        except Exception as exc:
            print(f"FAIL {path.name}: {exc}", file=sys.stderr)
            failed += 1

    print(f"normalized: fixed={fixed} skipped={skipped} failed={failed} (of {len(candidates)})")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
