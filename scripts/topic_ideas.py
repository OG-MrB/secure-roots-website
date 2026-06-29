#!/usr/bin/env python3
"""
Secure Roots — Weekly Blog Topic Ideas

Pulls recent items from a configurable list of cybersecurity feeds, scores
them against the Secure Roots editorial focus with Claude, and opens (or
updates) a single weekly GitHub issue with five ranked topic candidates.

Each candidate includes a one-line hook, the angle for Secure Roots' SMB-
heavy audience, source links, and a ready-to-paste draft command.

Designed to run from .github/workflows/topic-ideas.yml on a weekly cron.

Required env:
    ANTHROPIC_API_KEY
    GITHUB_TOKEN  (provided automatically in GitHub Actions)
    GITHUB_REPOSITORY  (e.g. OG-MrB/secure-roots-website — auto-set by Actions)
"""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Any

import feedparser
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("topic-ideas")

CLAUDE_MODEL = "claude-opus-4-7"

FEEDS = [
    ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
    ("SANS NewsBites", "https://www.sans.org/newsletters/newsbites/feed.xml"),
    ("CISA Advisories", "https://www.cisa.gov/news-events/cybersecurity-advisories/all.xml"),
    ("CISA KEV", "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.xml"),
    ("Krebs on Security", "https://krebsonsecurity.com/feed/"),
    ("Bleeping Computer", "https://www.bleepingcomputer.com/feed/"),
    ("The Record", "https://therecord.media/feed/"),
]

LOOKBACK_DAYS = 7
MAX_ITEMS_PER_FEED = 12
TOTAL_CANDIDATES = 5

EDITORIAL_BRIEF = """\
Secure Roots is a cybersecurity consultancy that publishes for SMB and mid-market
leaders, IT directors, and CISOs at organizations under 5,000 employees. Posts
focus on:

- Cybercrime and threat awareness (the *why* behind a current threat, not just IOCs)
- Social engineering, BEC, deepfakes, sextortion
- Nation-state activity that affects ordinary businesses (supply chain, contractors)
- Ransomware, data extortion, and the criminal economy
- Practical, action-oriented guidance — what to do this week, with no new budget

Avoid: vendor product reviews, deeply technical exploit walkthroughs, breach
post-mortems where the lesson is too narrow for a general audience, and stories
that are pure politics.

Strong topic candidates have:
1. A current news hook in the past 7 days
2. A concrete action SMBs can take
3. Real numbers / named incidents we can cite
4. Stakes that resonate with non-technical executives
"""


def fetch_recent_items() -> list[dict[str, Any]]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)
    items: list[dict[str, Any]] = []
    for source_name, url in FEEDS:
        log.info("Fetching %s ...", source_name)
        try:
            parsed = feedparser.parse(url)
        except Exception as e:
            log.warning("Failed to parse %s: %s", source_name, e)
            continue
        for entry in parsed.entries[:MAX_ITEMS_PER_FEED]:
            published = entry.get("published_parsed") or entry.get("updated_parsed")
            if published:
                pub_dt = datetime(*published[:6], tzinfo=timezone.utc)
                if pub_dt < cutoff:
                    continue
                pub_iso = pub_dt.isoformat()
            else:
                pub_iso = ""
            summary = entry.get("summary", "") or entry.get("description", "")
            # Strip HTML aggressively
            import re as _re
            summary = _re.sub(r"<[^>]+>", " ", summary)
            summary = _re.sub(r"\s+", " ", summary).strip()
            items.append(
                {
                    "source": source_name,
                    "title": entry.get("title", "").strip(),
                    "link": entry.get("link", ""),
                    "published": pub_iso,
                    "summary": summary[:600],
                }
            )
    log.info("Collected %d recent items across %d feeds.", len(items), len(FEEDS))
    return items


def rank_candidates(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not items:
        return []
    try:
        from anthropic import Anthropic
    except ImportError:
        log.error("anthropic SDK not installed.")
        sys.exit(1)
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        log.error("ANTHROPIC_API_KEY is not set.")
        sys.exit(1)

    feed_payload = json.dumps(items, indent=2)
    user = (
        "Below is a JSON list of recent cybersecurity news items. Pick the "
        f"{TOTAL_CANDIDATES} strongest candidates for a Secure Roots blog post "
        "this week. For each, return a JSON object with:\n"
        "  topic: a short imperative phrase to feed into our drafting CLI\n"
        "  hook: one sentence that sets up why this matters\n"
        "  angle: 1-2 sentences on the Secure Roots take / SMB action lens\n"
        "  sources: array of source URLs you used (subset of the input links)\n\n"
        "Return ONLY a JSON array of those objects, no commentary, no fences.\n\n"
        f"News items:\n{feed_payload}"
    )

    client = Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=4000,
        system=[{"type": "text", "text": EDITORIAL_BRIEF, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": user}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text").strip()
    # Strip a possible code fence
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
        if text.endswith("```"):
            text = text[: -3]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        log.error("Could not parse Claude response as JSON. Raw output:\n%s", text)
        return []


def render_issue_body(candidates: list[dict[str, Any]]) -> str:
    if not candidates:
        return (
            "_No strong candidates surfaced this week. Either the feeds were "
            "quiet or the editorial filter was too strict. Re-run manually if "
            "you want to lower the bar._\n"
        )
    today = datetime.now().strftime("%Y-%m-%d")
    lines = [
        f"Auto-generated weekly topic ideas for the week of **{today}**.",
        "",
        "Pick one and paste the command into your terminal — the draft script "
        "will create a branch and open a PR with the post and a hero image.",
        "",
    ]
    for i, c in enumerate(candidates, 1):
        topic = (c.get("topic") or "").replace('"', "'")
        hook = c.get("hook", "")
        angle = c.get("angle", "")
        sources = c.get("sources", []) or []
        lines.append(f"### {i}. {topic}")
        lines.append("")
        if hook:
            lines.append(f"**Hook:** {hook}")
            lines.append("")
        if angle:
            lines.append(f"**Angle:** {angle}")
            lines.append("")
        if sources:
            lines.append("**Sources:**")
            for url in sources:
                lines.append(f"- {url}")
            lines.append("")
        lines.append("**Draft this post:**")
        lines.append("```")
        lines.append(f'scripts/draft_post.py "{topic}"')
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


def upsert_weekly_issue(body: str) -> None:
    repo = os.environ.get("GITHUB_REPOSITORY")
    token = os.environ.get("GITHUB_TOKEN")
    if not (repo and token):
        log.warning("GITHUB_REPOSITORY or GITHUB_TOKEN not set — printing issue body to stdout instead.")
        print(body)
        return

    today = datetime.now().strftime("%Y-%m-%d")
    title = f"Blog topic ideas — week of {today}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    # Look for an existing open issue from this week (same title prefix)
    list_resp = requests.get(
        f"https://api.github.com/repos/{repo}/issues",
        headers=headers,
        params={"state": "open", "labels": "blog-topics", "per_page": 10},
        timeout=30,
    )
    list_resp.raise_for_status()
    existing_id = None
    for issue in list_resp.json():
        if issue.get("title") == title:
            existing_id = issue["number"]
            break

    payload = {"title": title, "body": body, "labels": ["blog-topics"]}
    if existing_id:
        log.info("Updating existing issue #%s", existing_id)
        resp = requests.patch(
            f"https://api.github.com/repos/{repo}/issues/{existing_id}",
            headers=headers,
            json=payload,
            timeout=30,
        )
    else:
        log.info("Creating new issue: %s", title)
        resp = requests.post(
            f"https://api.github.com/repos/{repo}/issues",
            headers=headers,
            json=payload,
            timeout=30,
        )
    resp.raise_for_status()
    log.info("Issue URL: %s", resp.json().get("html_url"))


def main() -> None:
    items = fetch_recent_items()
    candidates = rank_candidates(items)
    body = render_issue_body(candidates)
    upsert_weekly_issue(body)


if __name__ == "__main__":
    main()
