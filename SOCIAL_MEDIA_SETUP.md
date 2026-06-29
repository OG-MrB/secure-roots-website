# Social Media Auto-Post Setup Guide

This guide walks you through setting up automated social media posting for Secure Roots blog articles. Once configured, any blog post pushed with `publish_social: true` in its front matter will automatically be shared to Twitter/X, LinkedIn, and Instagram.

---

## Step 1: Twitter / X Developer Account

1. Go to [developer.x.com](https://developer.x.com) and sign in with the **@secureroots_og** account
2. Click **Sign up for Free Account** (Free tier: 1,500 tweets/month — more than enough)
3. Describe your use case: *"Automated posting of cybersecurity blog articles from secureroots.io to our company Twitter account."*
4. Once approved, go to **Dashboard → Projects & Apps → Create App**
5. Name the app: `Secure Roots Blog Auto-Post`
6. Under **Keys and Tokens**, generate:
   - **API Key** (also called Consumer Key)
   - **API Key Secret** (Consumer Secret)
   - **Access Token**
   - **Access Token Secret**
7. Make sure Access Token permissions are set to **Read and Write**

**You'll need these 4 values for GitHub Secrets:**
| Secret Name | Value |
|---|---|
| `TWITTER_API_KEY` | Your API Key |
| `TWITTER_API_SECRET` | Your API Key Secret |
| `TWITTER_ACCESS_TOKEN` | Your Access Token |
| `TWITTER_ACCESS_TOKEN_SECRET` | Your Access Token Secret |

---

## Step 2: LinkedIn Developer App

1. Go to [linkedin.com/developers/apps](https://www.linkedin.com/developers/apps) and sign in with your LinkedIn account (must be admin of the Secure Roots company page)
2. Click **Create App**
3. Fill in:
   - **App name**: `Secure Roots Blog Auto-Post`
   - **LinkedIn Page**: Select "Secure Roots"
   - **App logo**: Upload the Secure Roots logo
   - **Legal agreement**: Check the box
4. After creation, go to the **Auth** tab
5. Under **OAuth 2.0 Scopes**, request:
   - `w_member_social` (post on behalf of the authenticated member)
   - `r_organization_social` (read company page)
   - `w_organization_social` (post to company page)
6. Go to the **Products** tab and request access to **Share on LinkedIn** and **Marketing Developer Platform**
7. To generate an Access Token:
   - Go to [linkedin.com/developers/tools/oauth](https://www.linkedin.com/developers/tools/oauth)
   - Select your app
   - Check the scopes listed above
   - Click **Request access token**
   - Copy the generated token

**Note:** LinkedIn access tokens expire after 60 days. You'll need to refresh periodically, or set up a token refresh mechanism. The setup guide will remind you when it's time.

**You'll need this value for GitHub Secrets:**
| Secret Name | Value |
|---|---|
| `LINKEDIN_ACCESS_TOKEN` | Your OAuth 2.0 Access Token |

---

## Step 3: Instagram / Meta Developer App

Instagram posting requires a Meta (Facebook) developer account and an Instagram Professional (Business or Creator) account.

### 3a. Prepare Your Instagram Account
1. Open Instagram → Settings → Account → Switch to Professional Account (if not already)
2. Choose **Business** account type
3. Connect to a Facebook Page (create one for Secure Roots if needed)

### 3b. Create Meta Developer App
1. Go to [developers.facebook.com](https://developers.facebook.com) and log in
2. Click **My Apps → Create App**
3. Select **Business** as the app type
4. Name: `Secure Roots Blog Auto-Post`
5. After creation, on the app dashboard, click **Add Product** → find **Instagram Graph API** → click **Set Up**

### 3c. Get Your Instagram Business Account ID
1. In the Meta App Dashboard, go to **Tools → Graph API Explorer**
2. Select your app from the dropdown
3. Generate a User Token with these permissions:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_read_engagement`
4. Run this query: `me/accounts` — this returns your Facebook Pages
5. From the response, copy the Page ID
6. Run: `{page_id}?fields=instagram_business_account` — this returns your Instagram Business Account ID
7. Copy the `instagram_business_account.id` value

### 3d. Generate a Long-Lived Token
1. In Graph API Explorer, your token is short-lived (1 hour)
2. Exchange it for a long-lived token (60 days) by running:
   ```
   GET https://graph.facebook.com/v21.0/oauth/access_token?
     grant_type=fb_exchange_token&
     client_id={app_id}&
     client_secret={app_secret}&
     fb_exchange_token={short_lived_token}
   ```
3. Copy the long-lived access token from the response

**You'll need these values for GitHub Secrets:**
| Secret Name | Value |
|---|---|
| `INSTAGRAM_ACCESS_TOKEN` | Your long-lived Page Access Token |
| `INSTAGRAM_ACCOUNT_ID` | Your Instagram Business Account ID |

---

## Step 4: Facebook Page

The Facebook publisher uses the same Meta app you set up for Instagram.

1. In Graph API Explorer, run `me/accounts` to list your Pages
2. Copy the **Page ID** for the Secure Roots page
3. Copy the **Page Access Token** from the response (this is different from your user access token)
4. Long-lived Page Access Tokens do **not** expire as long as the user token used to fetch them was long-lived

**You'll need:**
| Secret Name | Value |
|---|---|
| `FB_PAGE_ACCESS_TOKEN` | Page Access Token (long-lived) |
| `FB_PAGE_ID` | Numeric Page ID |

---

## Step 5: Threads

1. Threads uses its own Graph API surface at `graph.threads.net`
2. Go to [developers.facebook.com](https://developers.facebook.com) → your app → add the **Threads API** product
3. Generate a long-lived Threads access token following the [Threads docs](https://developers.facebook.com/docs/threads/getting-started)
4. Get your Threads user ID with `GET https://graph.threads.net/v1.0/me?fields=id&access_token={token}`

**You'll need:**
| Secret Name | Value |
|---|---|
| `THREADS_ACCESS_TOKEN` | Long-lived Threads access token |
| `THREADS_USER_ID` | Your Threads user ID |

---

## Step 6: Bluesky

1. Log in to [bsky.app](https://bsky.app) with the Secure Roots account
2. **Settings → Privacy and security → App passwords → Add app password**
3. Name it `Secure Roots Auto-Post`. Save the generated password (format: `xxxx-xxxx-xxxx-xxxx`)
4. The Bluesky publisher uses your handle (e.g. `secureroots.bsky.social`) and that app password — no API console needed

**You'll need:**
| Secret Name | Value |
|---|---|
| `BLUESKY_HANDLE` | e.g. `secureroots.bsky.social` |
| `BLUESKY_APP_PASSWORD` | The generated app password |

---

## Step 7: Mastodon

1. Pick or join an instance — `infosec.exchange` is a strong fit for cybersecurity content. `mastodon.social` works too
2. Log in → **Preferences → Development → New application**
3. Name: `Secure Roots Auto-Post`. Scopes: check `write:statuses` and `write:media` at minimum
4. Save, then copy the **Access Token** from the application's detail page

**You'll need:**
| Secret Name | Value |
|---|---|
| `MASTODON_INSTANCE_URL` | e.g. `https://infosec.exchange` |
| `MASTODON_ACCESS_TOKEN` | Application access token |

---

## Step 8: Drafting & Topic Pipeline (Anthropic + OpenAI)

The local drafting CLI and weekly topic-ideas workflow need two extra keys.

### Get the keys
- **Anthropic API key** — [console.anthropic.com](https://console.anthropic.com) → Settings → API Keys → Create Key. Starts with `sk-ant-...`. Add a small credit balance under Settings → Billing.
- **OpenAI API key** — [platform.openai.com](https://platform.openai.com) → API keys → Create new secret key. Starts with `sk-...`. `gpt-image-1` requires verifying your organization (Settings → General → Verify Organization, one-time photo-ID check).

### Local `.env` (drafting CLI)
The local script reads from `.env` in the repo root (already gitignored):

```
cat > .env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
EOF
```

### GitHub Secrets (topic-ideas workflow)
```
gh secret set ANTHROPIC_API_KEY --repo OG-MrB/secure-roots-website
gh secret set OPENAI_API_KEY --repo OG-MrB/secure-roots-website
```
(OpenAI is optional for the topic-ideas workflow but useful if we later add image generation in CI.)

---

## Step 9: Store Credentials in GitHub Secrets

Either via the web UI at [github.com/OG-MrB/secure-roots-website/settings/secrets/actions](https://github.com/OG-MrB/secure-roots-website/settings/secrets/actions), or with the `gh` CLI:

```
gh secret set <NAME> --repo OG-MrB/secure-roots-website
```

| Secret Name | Platform |
|---|---|
| `TWITTER_API_KEY` | Twitter/X |
| `TWITTER_API_SECRET` | Twitter/X |
| `TWITTER_ACCESS_TOKEN` | Twitter/X |
| `TWITTER_ACCESS_TOKEN_SECRET` | Twitter/X |
| `LINKEDIN_ACCESS_TOKEN` | LinkedIn |
| `INSTAGRAM_ACCESS_TOKEN` | Instagram |
| `INSTAGRAM_ACCOUNT_ID` | Instagram |
| `FB_PAGE_ACCESS_TOKEN` | Facebook |
| `FB_PAGE_ID` | Facebook |
| `THREADS_ACCESS_TOKEN` | Threads |
| `THREADS_USER_ID` | Threads |
| `BLUESKY_HANDLE` | Bluesky |
| `BLUESKY_APP_PASSWORD` | Bluesky |
| `MASTODON_INSTANCE_URL` | Mastodon |
| `MASTODON_ACCESS_TOKEN` | Mastodon |
| `ANTHROPIC_API_KEY` | Topic-ideas workflow |
| `OPENAI_API_KEY` | (Optional) Image gen in CI |

**Note:** `GITHUB_TOKEN` is automatically available in GitHub Actions — you don't need to create it.

---

## Step 10: Drafting workflow (day-to-day usage)

```
# Pick up Monday's auto-generated topic issue, then:
scripts/draft_post.py "AI-driven CEO impersonation"
scripts/draft_post.py "AI-driven CEO impersonation" --notes "Cite the Arup case"
scripts/draft_post.py --regenerate _posts/2026-05-01-ai-ceo-impersonation.md --image-only
```

What it does:
1. Drafts the post body with Claude (Opus 4.7), using your existing posts as a style anchor
2. Generates the hero image with `gpt-image-1`
3. Writes `_posts/YYYY-MM-DD-<slug>.md` with `publish_social: false`
4. Creates a `draft/<slug>` branch, commits, pushes, opens a PR

You review the PR. When ready to publish, flip `publish_social: true` and merge — the existing social workflow does the rest.

---

## Step 5: Test the Workflow

1. Edit any blog post in `_posts/` and add `publish_social: true` to the front matter
2. Push to `main`
3. Go to **Actions** tab in GitHub — you should see the "Post to Social Media" workflow running
4. Check each platform to verify the posts appeared
5. Check `data/posted_urls.json` in the repo — it should now contain the posted article's tracking data

---

## Maintenance

### Token Refresh Schedule
- **LinkedIn**: Access token expires every 60 days. Set a calendar reminder to refresh.
- **Instagram/Meta**: Long-lived token expires every 60 days. Refresh using the Graph API.
- **Twitter/X**: Access tokens don't expire unless revoked. No refresh needed.

### Refreshing LinkedIn Token
1. Go to [linkedin.com/developers/tools/oauth](https://www.linkedin.com/developers/tools/oauth)
2. Re-authorize and generate a new token
3. Update the `LINKEDIN_ACCESS_TOKEN` secret in GitHub

### Refreshing Instagram Token
Run this API call before the token expires:
```
GET https://graph.facebook.com/v21.0/oauth/access_token?
  grant_type=fb_exchange_token&
  client_id={app_id}&
  client_secret={app_secret}&
  fb_exchange_token={current_long_lived_token}
```
Update the `INSTAGRAM_ACCESS_TOKEN` secret in GitHub with the new token.

---

## Troubleshooting

| Issue | Solution |
|---|---|
| Workflow doesn't trigger | Make sure the push modified a file in `_posts/` |
| Twitter post fails | Verify API keys have Read+Write permissions |
| LinkedIn post fails | Check if access token expired (60-day limit) |
| Instagram post fails | Verify account is Professional/Business type and token has `instagram_content_publish` scope |
| Duplicate posts | Check `data/posted_urls.json` — the URL may already be tracked |
| Image upload fails | Ensure the image file exists at the path specified in the post's `image:` field |
