#!/usr/bin/env python3
"""
Secure Roots — Automated Social Media Posting Script

Reads Jekyll blog posts, extracts metadata, and publishes to
Twitter/X, LinkedIn, and Instagram when `publish_social: true`
is set in the post's front matter.

Usage:
    python post_to_social.py <file_with_changed_posts>
"""

import json
import os
import re
import sys
import time
import logging
from datetime import datetime
from pathlib import Path

import yaml
import requests
from slugify import slugify

# Optional imports — gracefully handle if not posting to a platform
try:
    import tweepy
    HAS_TWEEPY = True
except ImportError:
    HAS_TWEEPY = False

try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SITE_URL = os.environ.get("SITE_URL", "https://secureroots.io")
REPO_ROOT = Path(__file__).resolve().parent.parent
TRACKING_FILE = REPO_ROOT / "data" / "posted_urls.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("social-poster")


# ---------------------------------------------------------------------------
# Front Matter Parser
# ---------------------------------------------------------------------------
class FrontMatterParser:
    """Extract YAML front matter and body from a Jekyll markdown file."""

    @staticmethod
    def parse(filepath: str) -> dict:
        path = REPO_ROOT / filepath
        if not path.exists():
            raise FileNotFoundError(f"Post file not found: {path}")

        text = path.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", text, re.DOTALL)
        if not match:
            raise ValueError(f"No valid front matter in {filepath}")

        meta = yaml.safe_load(match.group(1))
        body = match.group(2).strip()

        # Build the blog URL from the permalink pattern
        date = meta.get("date")
        if hasattr(date, "strftime"):
            year = date.strftime("%Y")
            month = date.strftime("%m")
            day = date.strftime("%d")
        else:
            # Parse date string
            date_str = str(date).split()[0]
            parts = date_str.split("-")
            year, month, day = parts[0], parts[1], parts[2]

        title_slug = slugify(meta.get("title", "untitled"))
        blog_url = f"{SITE_URL}/blog/{year}/{month}/{day}/{title_slug}/"

        # Get first ~30 words of body as fallback excerpt
        words = re.sub(r"[#*\[\]()>]", "", body).split()
        excerpt = " ".join(words[:30])
        if len(words) > 30:
            excerpt += "..."

        return {
            "title": meta.get("title", ""),
            "description": meta.get("description", excerpt),
            "image": meta.get("image", ""),
            "categories": meta.get("categories", []),
            "publish_social": meta.get("publish_social", False),
            "date": str(date),
            "blog_url": blog_url,
            "image_path": str(REPO_ROOT / meta.get("image", "").lstrip("/")),
            "excerpt": excerpt,
        }


# ---------------------------------------------------------------------------
# Post Tracker (prevents duplicate posts)
# ---------------------------------------------------------------------------
class PostTracker:
    """Track which articles have been posted to which platforms."""

    def __init__(self):
        self.data = self._load()

    def _load(self) -> dict:
        if TRACKING_FILE.exists():
            return json.loads(TRACKING_FILE.read_text(encoding="utf-8"))
        return {"posted_articles": []}

    def save(self):
        TRACKING_FILE.parent.mkdir(parents=True, exist_ok=True)
        TRACKING_FILE.write_text(
            json.dumps(self.data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def has_been_posted(self, blog_url: str, platform: str) -> bool:
        for article in self.data["posted_articles"]:
            if article["blog_url"] == blog_url:
                return platform in article.get("platforms", {})
        return False

    def mark_posted(self, blog_url: str, title: str, platform: str, post_id: str):
        # Find or create the article entry
        entry = None
        for article in self.data["posted_articles"]:
            if article["blog_url"] == blog_url:
                entry = article
                break

        if entry is None:
            entry = {
                "blog_url": blog_url,
                "title": title,
                "platforms": {},
            }
            self.data["posted_articles"].append(entry)

        entry["platforms"][platform] = {
            "id": post_id,
            "published_at": datetime.utcnow().isoformat() + "Z",
        }
        self.save()


# ---------------------------------------------------------------------------
# Twitter/X Publisher
# ---------------------------------------------------------------------------
class TwitterPublisher:
    """Post to Twitter/X using API v2 via tweepy."""

    def __init__(self):
        self.api_key = os.environ.get("TWITTER_API_KEY")
        self.api_secret = os.environ.get("TWITTER_API_SECRET")
        self.access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

    def is_configured(self) -> bool:
        return all([self.api_key, self.api_secret, self.access_token, self.access_token_secret])

    def publish(self, meta: dict) -> str | None:
        if not HAS_TWEEPY:
            log.warning("tweepy not installed — skipping Twitter")
            return None
        if not self.is_configured():
            log.warning("Twitter credentials not configured — skipping")
            return None

        # Build tweet text (280 char limit)
        title = meta["title"]
        url = meta["blog_url"]
        hashtags = "#CyberSecurity #InfoSec"

        # URLs count as 23 chars on Twitter
        available = 280 - 23 - len(hashtags) - 4  # spaces + newlines
        if len(title) > available:
            title = title[: available - 3] + "..."

        tweet_text = f"{title}\n\n{url}\n\n{hashtags}"

        # Authenticate
        auth = tweepy.OAuth1UserHandler(
            self.api_key, self.api_secret,
            self.access_token, self.access_token_secret,
        )
        api_v1 = tweepy.API(auth)
        client = tweepy.Client(
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
        )

        # Upload image via v1.1 (media upload not in v2 yet)
        media_id = None
        image_path = meta.get("image_path", "")
        if image_path and os.path.exists(image_path):
            try:
                media = api_v1.media_upload(filename=image_path)
                media_id = media.media_id
                log.info(f"Twitter: Image uploaded (media_id={media_id})")
            except Exception as e:
                log.warning(f"Twitter: Image upload failed: {e}")

        # Post tweet
        kwargs = {"text": tweet_text}
        if media_id:
            kwargs["media_ids"] = [media_id]

        response = client.create_tweet(**kwargs)
        tweet_id = str(response.data["id"])
        log.info(f"Twitter: Posted tweet {tweet_id}")
        return tweet_id


# ---------------------------------------------------------------------------
# LinkedIn Publisher
# ---------------------------------------------------------------------------
class LinkedInPublisher:
    """Post to LinkedIn company page using the REST API."""

    API_BASE = "https://api.linkedin.com/v2"

    def __init__(self):
        self.access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN")

    def is_configured(self) -> bool:
        return bool(self.access_token)

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }

    def _get_org_id(self) -> str | None:
        """Get the organization URN for the Secure Roots company page."""
        resp = requests.get(
            f"{self.API_BASE}/organizationAcls?q=roleAssignee",
            headers=self._headers(),
        )
        if resp.status_code != 200:
            log.warning(f"LinkedIn: Failed to get org ID: {resp.text}")
            return None
        elements = resp.json().get("elements", [])
        if elements:
            return elements[0].get("organization")
        return None

    def _upload_image(self, org_urn: str, image_path: str) -> str | None:
        """Upload an image and return the asset URN."""
        # Step 1: Register upload
        register_body = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": org_urn,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent",
                    }
                ],
            }
        }
        resp = requests.post(
            f"{self.API_BASE}/assets?action=registerUpload",
            headers=self._headers(),
            json=register_body,
        )
        if resp.status_code not in (200, 201):
            log.warning(f"LinkedIn: Image register failed: {resp.text}")
            return None

        upload_url = resp.json()["value"]["uploadMechanism"][
            "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
        ]["uploadUrl"]
        asset = resp.json()["value"]["asset"]

        # Step 2: Upload the image binary
        with open(image_path, "rb") as f:
            upload_resp = requests.put(
                upload_url,
                headers={"Authorization": f"Bearer {self.access_token}"},
                data=f,
            )
        if upload_resp.status_code not in (200, 201):
            log.warning(f"LinkedIn: Image upload failed: {upload_resp.status_code}")
            return None

        log.info(f"LinkedIn: Image uploaded ({asset})")
        return asset

    def publish(self, meta: dict) -> str | None:
        if not self.is_configured():
            log.warning("LinkedIn credentials not configured — skipping")
            return None

        org_urn = self._get_org_id()
        if not org_urn:
            log.warning("LinkedIn: Could not determine organization — skipping")
            return None

        # Build post text
        categories = meta.get("categories", [])
        hashtags = " ".join(f"#{slugify(c, separator='')}" for c in categories)
        hashtags += " #CyberSecurity #InfoSec"

        text = (
            f"{meta['title']}\n\n"
            f"{meta['description']}\n\n"
            f"Read the full article: {meta['blog_url']}\n\n"
            f"{hashtags}"
        )

        # Upload image if available
        image_asset = None
        image_path = meta.get("image_path", "")
        if image_path and os.path.exists(image_path):
            image_asset = self._upload_image(org_urn, image_path)

        # Build share payload
        share_body = {
            "author": org_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "ARTICLE" if not image_asset else "IMAGE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }

        if image_asset:
            share_body["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                {
                    "status": "READY",
                    "originalUrl": meta["blog_url"],
                    "media": image_asset,
                    "title": {"text": meta["title"]},
                    "description": {"text": meta["description"][:200]},
                }
            ]
        else:
            share_body["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                {
                    "status": "READY",
                    "originalUrl": meta["blog_url"],
                    "title": {"text": meta["title"]},
                    "description": {"text": meta["description"][:200]},
                }
            ]

        resp = requests.post(
            f"{self.API_BASE}/ugcPosts",
            headers=self._headers(),
            json=share_body,
        )

        if resp.status_code in (200, 201):
            post_id = resp.json().get("id", "unknown")
            log.info(f"LinkedIn: Posted ({post_id})")
            return str(post_id)
        else:
            log.error(f"LinkedIn: Post failed ({resp.status_code}): {resp.text}")
            return None


# ---------------------------------------------------------------------------
# Instagram Publisher
# ---------------------------------------------------------------------------
class InstagramPublisher:
    """Post to Instagram using the Meta Graph API."""

    GRAPH_URL = "https://graph.facebook.com/v21.0"

    def __init__(self):
        self.access_token = os.environ.get("INSTAGRAM_ACCESS_TOKEN")
        self.account_id = os.environ.get("INSTAGRAM_ACCOUNT_ID")

    def is_configured(self) -> bool:
        return bool(self.access_token and self.account_id)

    def publish(self, meta: dict) -> str | None:
        if not self.is_configured():
            log.warning("Instagram credentials not configured — skipping")
            return None

        # Instagram requires a publicly accessible image URL
        # Use the live site URL for the image
        image_rel = meta.get("image", "")
        if not image_rel:
            log.warning("Instagram: No image specified — skipping (image required)")
            return None

        image_url = f"{SITE_URL}{image_rel}"

        # Build caption
        categories = meta.get("categories", [])
        hashtags = " ".join(f"#{slugify(c, separator='')}" for c in categories)
        hashtags += " #CyberSecurity #InfoSec #SecureRoots #ThreatIntelligence"

        caption = (
            f"{meta['title']}\n\n"
            f"{meta['description']}\n\n"
            f"Read the full article at secureroots.io (link in bio)\n\n"
            f"{hashtags}"
        )

        # Step 1: Create media container
        container_resp = requests.post(
            f"{self.GRAPH_URL}/{self.account_id}/media",
            params={
                "image_url": image_url,
                "caption": caption,
                "access_token": self.access_token,
            },
        )

        if container_resp.status_code != 200:
            log.error(f"Instagram: Container creation failed: {container_resp.text}")
            return None

        container_id = container_resp.json().get("id")
        log.info(f"Instagram: Media container created ({container_id})")

        # Step 2: Wait for container to be ready (Instagram processes async)
        time.sleep(5)

        # Step 3: Publish the container
        publish_resp = requests.post(
            f"{self.GRAPH_URL}/{self.account_id}/media_publish",
            params={
                "creation_id": container_id,
                "access_token": self.access_token,
            },
        )

        if publish_resp.status_code != 200:
            log.error(f"Instagram: Publish failed: {publish_resp.text}")
            return None

        post_id = publish_resp.json().get("id")
        log.info(f"Instagram: Published ({post_id})")
        return str(post_id)


# ---------------------------------------------------------------------------
# Facebook Page Publisher
# ---------------------------------------------------------------------------
class FacebookPublisher:
    """Post to a Facebook Page using the Graph API (uses the same Meta app as Instagram)."""

    GRAPH_URL = "https://graph.facebook.com/v21.0"

    def __init__(self):
        self.access_token = os.environ.get("FB_PAGE_ACCESS_TOKEN")
        self.page_id = os.environ.get("FB_PAGE_ID")

    def is_configured(self) -> bool:
        return bool(self.access_token and self.page_id)

    def publish(self, meta: dict) -> str | None:
        if not self.is_configured():
            log.warning("Facebook credentials not configured — skipping")
            return None

        categories = meta.get("categories", [])
        hashtags = " ".join(f"#{slugify(c, separator='')}" for c in categories)
        hashtags += " #CyberSecurity #InfoSec"

        message = (
            f"{meta['title']}\n\n"
            f"{meta['description']}\n\n"
            f"Read the full article: {meta['blog_url']}\n\n"
            f"{hashtags}"
        )

        # Prefer a photo post when we have an image; otherwise a link post.
        image_rel = meta.get("image", "")
        if image_rel:
            image_url = f"{SITE_URL}{image_rel}"
            resp = requests.post(
                f"{self.GRAPH_URL}/{self.page_id}/photos",
                params={
                    "url": image_url,
                    "caption": message,
                    "access_token": self.access_token,
                },
                timeout=60,
            )
        else:
            resp = requests.post(
                f"{self.GRAPH_URL}/{self.page_id}/feed",
                params={
                    "message": message,
                    "link": meta["blog_url"],
                    "access_token": self.access_token,
                },
                timeout=60,
            )

        if resp.status_code in (200, 201):
            post_id = resp.json().get("id") or resp.json().get("post_id") or "unknown"
            log.info(f"Facebook: Posted ({post_id})")
            return str(post_id)
        log.error(f"Facebook: Post failed ({resp.status_code}): {resp.text}")
        return None


# ---------------------------------------------------------------------------
# Threads Publisher
# ---------------------------------------------------------------------------
class ThreadsPublisher:
    """Post to Threads via the Meta Threads Graph API."""

    GRAPH_URL = "https://graph.threads.net/v1.0"

    def __init__(self):
        self.access_token = os.environ.get("THREADS_ACCESS_TOKEN")
        self.user_id = os.environ.get("THREADS_USER_ID")

    def is_configured(self) -> bool:
        return bool(self.access_token and self.user_id)

    def publish(self, meta: dict) -> str | None:
        if not self.is_configured():
            log.warning("Threads credentials not configured — skipping")
            return None

        # Threads posts are capped at 500 chars.
        title = meta["title"]
        url = meta["blog_url"]
        suffix = f"\n\n{url}\n\n#CyberSecurity #InfoSec"
        body_room = 500 - len(suffix) - len(title) - 2
        description = meta.get("description", "")
        if body_room > 40 and description:
            if len(description) > body_room:
                description = description[: body_room - 3] + "..."
            text = f"{title}\n\n{description}{suffix}"
        else:
            text = f"{title}{suffix}"

        # Step 1: create the media container
        params = {
            "media_type": "TEXT",
            "text": text,
            "access_token": self.access_token,
        }
        image_rel = meta.get("image", "")
        if image_rel:
            params["media_type"] = "IMAGE"
            params["image_url"] = f"{SITE_URL}{image_rel}"

        create_resp = requests.post(
            f"{self.GRAPH_URL}/{self.user_id}/threads",
            params=params,
            timeout=60,
        )
        if create_resp.status_code != 200:
            log.error(f"Threads: Container creation failed: {create_resp.text}")
            return None
        container_id = create_resp.json().get("id")
        log.info(f"Threads: Container created ({container_id})")

        time.sleep(3)  # Threads needs a moment before publish

        publish_resp = requests.post(
            f"{self.GRAPH_URL}/{self.user_id}/threads_publish",
            params={
                "creation_id": container_id,
                "access_token": self.access_token,
            },
            timeout=60,
        )
        if publish_resp.status_code != 200:
            log.error(f"Threads: Publish failed: {publish_resp.text}")
            return None
        post_id = publish_resp.json().get("id")
        log.info(f"Threads: Published ({post_id})")
        return str(post_id)


# ---------------------------------------------------------------------------
# Bluesky Publisher
# ---------------------------------------------------------------------------
class BlueskyPublisher:
    """Post to Bluesky using the AT Protocol HTTP API."""

    PDS_URL = "https://bsky.social"

    def __init__(self):
        self.handle = os.environ.get("BLUESKY_HANDLE")
        self.app_password = os.environ.get("BLUESKY_APP_PASSWORD")

    def is_configured(self) -> bool:
        return bool(self.handle and self.app_password)

    def _login(self) -> dict | None:
        resp = requests.post(
            f"{self.PDS_URL}/xrpc/com.atproto.server.createSession",
            json={"identifier": self.handle, "password": self.app_password},
            timeout=30,
        )
        if resp.status_code != 200:
            log.error(f"Bluesky: Login failed: {resp.text}")
            return None
        return resp.json()

    def _upload_image(self, jwt: str, image_path: str) -> dict | None:
        with open(image_path, "rb") as f:
            data = f.read()
        # Bluesky requires images <= 1MB. Downscale if needed.
        if len(data) > 950_000 and HAS_PILLOW:
            try:
                from io import BytesIO
                img = Image.open(image_path).convert("RGB")
                buf = BytesIO()
                img.thumbnail((1600, 1600))
                img.save(buf, format="JPEG", quality=82)
                data = buf.getvalue()
                content_type = "image/jpeg"
            except Exception as e:
                log.warning(f"Bluesky: image downscale failed: {e}")
                content_type = "image/png"
        else:
            content_type = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"

        resp = requests.post(
            f"{self.PDS_URL}/xrpc/com.atproto.repo.uploadBlob",
            headers={"Authorization": f"Bearer {jwt}", "Content-Type": content_type},
            data=data,
            timeout=60,
        )
        if resp.status_code != 200:
            log.error(f"Bluesky: image upload failed: {resp.text}")
            return None
        return resp.json().get("blob")

    def publish(self, meta: dict) -> str | None:
        if not self.is_configured():
            log.warning("Bluesky credentials not configured — skipping")
            return None

        session = self._login()
        if not session:
            return None
        jwt = session["accessJwt"]
        did = session["did"]

        # 300-char limit (graphemes; we approximate with chars).
        title = meta["title"]
        url = meta["blog_url"]
        suffix = f"\n\n{url}"
        budget = 300 - len(suffix)
        if len(title) > budget:
            title = title[: budget - 3] + "..."
        text = f"{title}{suffix}"

        # Build a facet so the URL renders as a clickable link.
        link_start = text.encode("utf-8").find(url.encode("utf-8"))
        link_end = link_start + len(url.encode("utf-8"))
        facets = [
            {
                "index": {"byteStart": link_start, "byteEnd": link_end},
                "features": [{"$type": "app.bsky.richtext.facet#link", "uri": url}],
            }
        ] if link_start >= 0 else []

        record: dict = {
            "$type": "app.bsky.feed.post",
            "text": text,
            "createdAt": datetime.utcnow().isoformat() + "Z",
            "facets": facets,
        }

        image_path = meta.get("image_path", "")
        if image_path and os.path.exists(image_path):
            blob = self._upload_image(jwt, image_path)
            if blob:
                record["embed"] = {
                    "$type": "app.bsky.embed.images",
                    "images": [{"alt": meta.get("description", title)[:300], "image": blob}],
                }

        resp = requests.post(
            f"{self.PDS_URL}/xrpc/com.atproto.repo.createRecord",
            headers={"Authorization": f"Bearer {jwt}"},
            json={
                "repo": did,
                "collection": "app.bsky.feed.post",
                "record": record,
            },
            timeout=60,
        )
        if resp.status_code != 200:
            log.error(f"Bluesky: Post failed: {resp.text}")
            return None
        uri = resp.json().get("uri", "unknown")
        log.info(f"Bluesky: Posted ({uri})")
        return uri


# ---------------------------------------------------------------------------
# Mastodon Publisher
# ---------------------------------------------------------------------------
class MastodonPublisher:
    """Post to a Mastodon instance via the standard REST API."""

    def __init__(self):
        self.instance_url = (os.environ.get("MASTODON_INSTANCE_URL") or "").rstrip("/")
        self.access_token = os.environ.get("MASTODON_ACCESS_TOKEN")

    def is_configured(self) -> bool:
        return bool(self.instance_url and self.access_token)

    def _headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}

    def _upload_media(self, image_path: str, alt_text: str) -> str | None:
        with open(image_path, "rb") as f:
            files = {"file": f}
            data = {"description": alt_text[:1500]}
            resp = requests.post(
                f"{self.instance_url}/api/v2/media",
                headers=self._headers(),
                files=files,
                data=data,
                timeout=60,
            )
        if resp.status_code not in (200, 202):
            log.error(f"Mastodon: media upload failed: {resp.text}")
            return None
        return resp.json().get("id")

    def publish(self, meta: dict) -> str | None:
        if not self.is_configured():
            log.warning("Mastodon credentials not configured — skipping")
            return None

        categories = meta.get("categories", [])
        hashtags = " ".join(f"#{slugify(c, separator='')}" for c in categories)
        hashtags += " #CyberSecurity #InfoSec"
        # 500-char limit on most instances.
        body = f"{meta['title']}\n\n{meta['description']}\n\n{meta['blog_url']}\n\n{hashtags}"
        if len(body) > 500:
            # Drop description first, then truncate as a last resort.
            body = f"{meta['title']}\n\n{meta['blog_url']}\n\n{hashtags}"
            if len(body) > 500:
                body = body[:497] + "..."

        media_ids: list[str] = []
        image_path = meta.get("image_path", "")
        if image_path and os.path.exists(image_path):
            media_id = self._upload_media(image_path, meta.get("description", meta["title"]))
            if media_id:
                media_ids.append(media_id)

        payload = {"status": body, "visibility": "public"}
        if media_ids:
            payload["media_ids[]"] = media_ids

        resp = requests.post(
            f"{self.instance_url}/api/v1/statuses",
            headers=self._headers(),
            data=payload,
            timeout=60,
        )
        if resp.status_code in (200, 201):
            post_id = resp.json().get("id", "unknown")
            log.info(f"Mastodon: Posted ({post_id})")
            return str(post_id)
        log.error(f"Mastodon: Post failed ({resp.status_code}): {resp.text}")
        return None


# ---------------------------------------------------------------------------
# Main Orchestration
# ---------------------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        log.error("Usage: post_to_social.py <file_with_changed_posts>")
        sys.exit(1)

    changed_file = sys.argv[1]
    if not os.path.exists(changed_file):
        log.error(f"Changed posts file not found: {changed_file}")
        sys.exit(1)

    # Read list of changed post files
    with open(changed_file) as f:
        changed_posts = [line.strip() for line in f if line.strip()]

    if not changed_posts:
        log.info("No changed posts to process.")
        return

    tracker = PostTracker()
    parser = FrontMatterParser()

    # Initialize publishers
    twitter = TwitterPublisher()
    linkedin = LinkedInPublisher()
    instagram = InstagramPublisher()
    facebook = FacebookPublisher()
    threads = ThreadsPublisher()
    bluesky = BlueskyPublisher()
    mastodon = MastodonPublisher()

    extras = [
        ("facebook", facebook),
        ("threads", threads),
        ("bluesky", bluesky),
        ("mastodon", mastodon),
    ]

    results = {"processed": 0, "posted": 0, "skipped": 0, "errors": 0}

    for post_file in changed_posts:
        log.info(f"\n{'='*60}")
        log.info(f"Processing: {post_file}")
        results["processed"] += 1

        try:
            meta = parser.parse(post_file)
        except Exception as e:
            log.error(f"Failed to parse {post_file}: {e}")
            results["errors"] += 1
            continue

        # Check QC gate
        if not meta.get("publish_social"):
            log.info(f"Skipping (publish_social is not true): {meta['title']}")
            results["skipped"] += 1
            continue

        blog_url = meta["blog_url"]
        title = meta["title"]
        log.info(f"Title: {title}")
        log.info(f"URL: {blog_url}")

        posted_any = False

        # --- Twitter ---
        if not tracker.has_been_posted(blog_url, "twitter"):
            try:
                tweet_id = twitter.publish(meta)
                if tweet_id:
                    tracker.mark_posted(blog_url, title, "twitter", tweet_id)
                    posted_any = True
            except Exception as e:
                log.error(f"Twitter error: {e}")
                results["errors"] += 1
        else:
            log.info("Twitter: Already posted — skipping")

        time.sleep(2)  # Brief pause between platforms

        # --- LinkedIn ---
        if not tracker.has_been_posted(blog_url, "linkedin"):
            try:
                li_id = linkedin.publish(meta)
                if li_id:
                    tracker.mark_posted(blog_url, title, "linkedin", li_id)
                    posted_any = True
            except Exception as e:
                log.error(f"LinkedIn error: {e}")
                results["errors"] += 1
        else:
            log.info("LinkedIn: Already posted — skipping")

        time.sleep(2)

        # --- Instagram ---
        if not tracker.has_been_posted(blog_url, "instagram"):
            try:
                ig_id = instagram.publish(meta)
                if ig_id:
                    tracker.mark_posted(blog_url, title, "instagram", ig_id)
                    posted_any = True
            except Exception as e:
                log.error(f"Instagram error: {e}")
                results["errors"] += 1
        else:
            log.info("Instagram: Already posted — skipping")

        # --- Facebook / Threads / Bluesky / Mastodon ---
        for platform_name, publisher in extras:
            time.sleep(2)
            if tracker.has_been_posted(blog_url, platform_name):
                log.info(f"{platform_name.title()}: Already posted — skipping")
                continue
            try:
                pid = publisher.publish(meta)
                if pid:
                    tracker.mark_posted(blog_url, title, platform_name, pid)
                    posted_any = True
            except Exception as e:
                log.error(f"{platform_name.title()} error: {e}")
                results["errors"] += 1

        if posted_any:
            results["posted"] += 1

    # Summary
    log.info(f"\n{'='*60}")
    log.info("SUMMARY")
    log.info(f"  Processed: {results['processed']}")
    log.info(f"  Posted:    {results['posted']}")
    log.info(f"  Skipped:   {results['skipped']}")
    log.info(f"  Errors:    {results['errors']}")

    if results["errors"] > 0:
        log.warning("Some posts had errors — check logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
