#!/usr/bin/env python3
"""
Secure Roots — Staggered posting selector.

Prints the path of the single NEWEST blog post that:
  - has `publish_social: true` in its front matter, AND
  - has not yet been recorded in data/posted_urls.json

Prints nothing (and exits 0) when there is nothing left to post, so the
daily scheduled workflow naturally stops after the backlog is drained.

The blog_url is constructed identically to post_to_social.py so the
dedup keys match exactly.

Usage:
    python scripts/select_next_post.py
"""

import json
import os
import re
import sys
from pathlib import Path

import yaml

SITE_URL = os.environ.get("SITE_URL", "https://secureroots.io")
REPO_ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO_ROOT / "_posts"
TRACKING_FILE = REPO_ROOT / "data" / "posted_urls.json"


def parse_front_matter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return None
    return yaml.safe_load(match.group(1)) or {}


def blog_url_for(path: Path) -> str:
    # Match Jekyll's permalink, which is built from the FILENAME slug
    # (YYYY-MM-DD-<slug>.md), the same way post_to_social.py builds it.
    fm = re.match(r"(\d{4})-(\d{2})-(\d{2})-(.+)", path.stem)
    if not fm:
        return ""
    year, month, day, slug = fm.groups()
    return f"{SITE_URL}/blog/{year}/{month}/{day}/{slug}/"


def posted_urls() -> set[str]:
    if not TRACKING_FILE.exists():
        return set()
    data = json.loads(TRACKING_FILE.read_text(encoding="utf-8"))
    return {a["blog_url"] for a in data.get("posted_articles", [])}


def main() -> None:
    already = posted_urls()
    candidates = []  # (date_str, path)

    for path in sorted(POSTS_DIR.glob("*.md")):
        meta = parse_front_matter(path)
        if not meta or meta.get("publish_social") is not True:
            continue
        if blog_url_for(path) in already:
            continue
        candidates.append((str(meta.get("date")).split()[0], path))

    if not candidates:
        return  # nothing left — print nothing, exit 0

    # Newest first — promote the most recent unposted article each day
    candidates.sort(key=lambda c: c[0], reverse=True)
    chosen = candidates[0][1]
    # Print path relative to repo root (what post_to_social.py expects)
    print(chosen.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
