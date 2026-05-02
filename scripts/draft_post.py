#!/usr/bin/env python3
"""
Secure Roots — Blog Post Draft Generator

Drafts a Jekyll post (markdown + hero image) for a given topic, then opens
a pull request against main. The post is committed with publish_social: false
so it stays out of the social pipeline until you flip the flag at merge time.

Usage:
    scripts/draft_post.py "topic phrase"
    scripts/draft_post.py "topic phrase" --notes "extra context or a URL"
    scripts/draft_post.py "topic phrase" --notes-file path/to/notes.md
    scripts/draft_post.py --regenerate _posts/2026-05-01-foo.md [--image-only|--body-only]

Required env (loads from .env in repo root if present):
    ANTHROPIC_API_KEY
    OPENAI_API_KEY

Requires: gh CLI authed (gh auth login) for PR creation.
"""

from __future__ import annotations

import argparse
import base64
import logging
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml
from slugify import slugify

REPO_ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO_ROOT / "_posts"
IMG_DIR = REPO_ROOT / "img"
ENV_FILE = REPO_ROOT / ".env"

CLAUDE_MODEL = "claude-opus-4-7"
IMAGE_MODEL = "gpt-image-1"
IMAGE_SIZE = "1536x1024"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("draft_post")


def load_dotenv() -> None:
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def run(cmd: list[str], check: bool = True, capture: bool = False, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess:
    log.info("$ %s", " ".join(cmd))
    return subprocess.run(cmd, check=check, cwd=cwd, capture_output=capture, text=True)


def load_style_corpus() -> str:
    """Concatenate existing posts so the model can mirror voice and structure."""
    files = sorted(POSTS_DIR.glob("*.md"))
    chunks = []
    for f in files:
        chunks.append(f"<post filename=\"{f.name}\">\n{f.read_text()}\n</post>")
    return "\n\n".join(chunks)


STYLE_INSTRUCTIONS = """\
You are drafting a blog post for Secure Roots (secureroots.io), a cybersecurity
consultancy. The post will be committed to a Jekyll site under _posts/.

Match the voice and structure of the reference posts EXACTLY:

- Title: hook + colon + clarifier (e.g. "The Cavalry Isn't Coming: Your Wartime
  Cybersecurity Checklist"). Punchy, declarative, sometimes provocative. Avoid
  clickbait.
- Open with a 2-4 paragraph dramatic hook. Short sentences. Stakes first.
- Use `---` horizontal rules between major sections.
- Use `## Section header` for top-level sections (mix of sentence case and
  title case is OK, follow what reads strongest).
- Bullet lists for concrete action items. Bold for emphasis on key terms.
- Cite real numbers, real incidents, and named threat actors when relevant.
- Voice: direct, urgent, confident, professional. No hedging. No filler.
- Em-dashes are welcome. Avoid emojis.
- Length: 1500-2500 words.
- ALWAYS include a "What Secure Roots Is Doing" or equivalent CTA section near
  the end, followed by a clear contact link: [Contact Secure Roots →](/contact/)

Front matter REQUIREMENTS — emit exactly this YAML block at the top:

---
layout: post
title: "<the title>"
date: <YYYY-MM-DD HH:MM:SS -0700>
categories: [Cybercrime & Threat Awareness]
image: /img/<slug>.png
description: "<150-220 char SEO-friendly meta description>"
publish_social: false
---

The image filename must be /img/<slug>.png where <slug> matches the post's
slug. publish_social MUST be false (the human reviews and flips it on merge).

OUTPUT RULES:
- Output ONLY the markdown file contents (front matter + body).
- Do NOT wrap in code fences.
- Do NOT include any commentary before or after.
- Do NOT include placeholders like [INSERT X] — write the real post.
"""


def call_claude(system: str, user: str, max_tokens: int = 8000) -> str:
    """Call Claude Messages API and return the text."""
    try:
        from anthropic import Anthropic
    except ImportError:
        log.error("anthropic SDK not installed. Run: pip install -r scripts/requirements.txt")
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        log.error("ANTHROPIC_API_KEY not set (check .env in repo root)")
        sys.exit(1)

    client = Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=max_tokens,
        system=[
            {"type": "text", "text": system, "cache_control": {"type": "ephemeral"}},
        ],
        messages=[{"role": "user", "content": user}],
    )
    return "".join(block.text for block in resp.content if block.type == "text").strip()


def draft_body(topic: str, notes: str | None) -> str:
    style_corpus = load_style_corpus()
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S -0700")

    system = (
        STYLE_INSTRUCTIONS
        + "\n\n## Reference posts (for voice and structure only — do not copy content)\n\n"
        + style_corpus
    )
    user_parts = [
        f"Topic: {topic}",
        f"Today's date: {today} (use this in the front matter date field)",
    ]
    if notes:
        user_parts.append(f"\nAdditional context / notes:\n{notes}")
    user_parts.append("\nDraft the post now. Output only the markdown file contents.")

    raw = call_claude(system, "\n".join(user_parts))
    return strip_code_fences(raw)


def strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        # remove opening fence (with or without language tag)
        text = re.sub(r"^```[a-zA-Z]*\n", "", text)
        if text.endswith("```"):
            text = text[: -3].rstrip()
    return text.strip()


def parse_front_matter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", text, re.DOTALL)
    if not m:
        raise ValueError("Drafted post is missing YAML front matter.")
    return yaml.safe_load(m.group(1)), m.group(2)


IMAGE_PROMPT_TEMPLATE = """\
Editorial hero illustration for a cybersecurity blog post titled "{title}".
Subject: {subject}
Style: cinematic, dramatic lighting, photoreal with subtle illustrated elements,
dark teal and amber palette, sense of tension and urgency. Professional,
suitable for a corporate security publication. No text, no logos, no watermarks,
no readable letters or numbers. 16:9 framing.
"""


def generate_hero_image(title: str, description: str, slug: str) -> Path:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        log.error("OPENAI_API_KEY not set (check .env in repo root)")
        sys.exit(1)

    try:
        from openai import OpenAI
    except ImportError:
        log.error("openai SDK not installed. Run: pip install -r scripts/requirements.txt")
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    prompt = IMAGE_PROMPT_TEMPLATE.format(title=title, subject=description)
    log.info("Generating hero image with %s ...", IMAGE_MODEL)
    resp = client.images.generate(
        model=IMAGE_MODEL,
        prompt=prompt,
        size=IMAGE_SIZE,
        n=1,
    )
    b64 = resp.data[0].b64_json
    image_bytes = base64.b64decode(b64)

    IMG_DIR.mkdir(exist_ok=True)
    out_path = IMG_DIR / f"{slug}.png"
    out_path.write_bytes(image_bytes)
    log.info("Saved hero image: %s", out_path)
    return out_path


def write_post(post_text: str, slug: str, date_obj: datetime) -> Path:
    POSTS_DIR.mkdir(exist_ok=True)
    filename = f"{date_obj.strftime('%Y-%m-%d')}-{slug}.md"
    out_path = POSTS_DIR / filename
    out_path.write_text(post_text, encoding="utf-8")
    log.info("Saved post: %s", out_path)
    return out_path


def open_pull_request(branch: str, post_path: Path, image_path: Path, title: str) -> None:
    # Branch off current main
    run(["git", "checkout", "-b", branch])
    run(["git", "add", str(post_path.relative_to(REPO_ROOT)), str(image_path.relative_to(REPO_ROOT))])
    commit_msg = f"Draft: {title}\n\nGenerated by scripts/draft_post.py — review and flip publish_social: true to publish."
    run(["git", "commit", "-m", commit_msg])
    run(["git", "push", "-u", "origin", branch])

    pr_body = f"""\
## Drafted post — needs review

**File:** `{post_path.relative_to(REPO_ROOT)}`
**Image:** `{image_path.relative_to(REPO_ROOT)}`

### Reviewer checklist
- [ ] Read the post end-to-end. Tighten or rewrite anything that feels off-voice.
- [ ] Verify all named incidents, numbers, and CVEs are accurate.
- [ ] Look at `{image_path.relative_to(REPO_ROOT)}` — regenerate if it doesn't fit (`scripts/draft_post.py --regenerate {post_path.relative_to(REPO_ROOT)} --image-only`).
- [ ] Confirm the `description:` reads well for SEO and link previews.
- [ ] Flip `publish_social: true` in the front matter when ready to publish.
- [ ] Merge. The social workflow will then push to all configured platforms.
"""

    run([
        "gh", "pr", "create",
        "--base", "main",
        "--head", branch,
        "--title", f"Draft: {title}",
        "--body", pr_body,
        "--label", "blog-draft",
    ], check=False)  # label may not exist yet — don't fail the whole run


def cmd_new(args: argparse.Namespace) -> None:
    notes = args.notes
    if args.notes_file:
        notes_path = Path(args.notes_file).expanduser()
        notes = (notes or "") + "\n\n" + notes_path.read_text()

    log.info("Drafting body for topic: %s", args.topic)
    raw = draft_body(args.topic, notes)
    meta, _body = parse_front_matter(raw)

    title = meta["title"]
    description = meta.get("description", "")
    date_field = meta.get("date")
    if isinstance(date_field, datetime):
        date_obj = date_field
    else:
        date_obj = datetime.strptime(str(date_field).split()[0], "%Y-%m-%d")
    slug = slugify(title)

    # Make sure the front matter image path matches the slug we'll save under
    expected_img = f"/img/{slug}.png"
    raw = re.sub(r"^image:.*$", f"image: {expected_img}", raw, count=1, flags=re.MULTILINE)

    post_path = write_post(raw, slug, date_obj)
    image_path = generate_hero_image(title, description, slug)

    branch = f"draft/{slug}"
    open_pull_request(branch, post_path, image_path, title)
    # Return to main so the working tree isn't left on the draft branch
    run(["git", "checkout", "main"], check=False)
    log.info("Done. PR opened on branch %s.", branch)


def cmd_regenerate(args: argparse.Namespace) -> None:
    post_path = (REPO_ROOT / args.post_path).resolve() if not Path(args.post_path).is_absolute() else Path(args.post_path)
    if not post_path.exists():
        log.error("Post not found: %s", post_path)
        sys.exit(1)
    text = post_path.read_text()
    meta, _body = parse_front_matter(text)
    title = meta["title"]
    description = meta.get("description", "")
    slug = slugify(title)

    if not args.body_only:
        generate_hero_image(title, description, slug)

    if not args.image_only:
        log.info("Regenerating body for: %s", title)
        new_text = draft_body(title, args.notes)
        # Force the slug-aligned image path
        new_text = re.sub(r"^image:.*$", f"image: /img/{slug}.png", new_text, count=1, flags=re.MULTILINE)
        post_path.write_text(new_text, encoding="utf-8")
        log.info("Rewrote: %s", post_path)


def main() -> None:
    load_dotenv()
    p = argparse.ArgumentParser(description="Draft a Secure Roots blog post and open a PR.")
    sub = p.add_subparsers(dest="cmd")

    # default subcommand: new (also accepts a positional topic at the top level)
    p.add_argument("topic", nargs="?", help="Topic phrase for the post")
    p.add_argument("--notes", help="Inline notes / extra context for the draft")
    p.add_argument("--notes-file", help="Path to a file containing notes")

    p.add_argument("--regenerate", metavar="POST_PATH", help="Regenerate body and/or image for an existing post file")
    p.add_argument("--image-only", action="store_true", help="With --regenerate: only regen the hero image")
    p.add_argument("--body-only", action="store_true", help="With --regenerate: only regen the body")

    args = p.parse_args()

    if args.regenerate:
        ns = argparse.Namespace(
            post_path=args.regenerate,
            image_only=args.image_only,
            body_only=args.body_only,
            notes=args.notes,
        )
        cmd_regenerate(ns)
        return

    if not args.topic:
        p.error("topic is required (or pass --regenerate <path>)")
    cmd_new(args)


if __name__ == "__main__":
    main()
