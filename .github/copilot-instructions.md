# AI Agent Instructions for Secure Roots Website

This document provides essential context for AI agents working with the Secure Roots website codebase.

## Project Overview

- Jekyll-based static website for Secure Roots cybersecurity company
- Focus on cybersecurity insights, services, and blog content
- Built with security-first approach (CSP headers, secure forms)

## Architecture

### Key Components

- `_layouts/`: Templates defining page structure
  - `default.html`: Base template with navigation and security headers
  - `post.html`: Blog post template extending default
  - `home.html`: Landing page template

### Content Organization

- `_posts/`: Blog articles in Markdown format
  - Naming convention: `YYYY-MM-DD-title.md`
  - Required frontmatter: layout, title, date, categories
- `assets/`: Media and static files
  - `img/services/`: Service-specific icons
  - `img/social/`: Social media assets
  - `img/`: General images and logos

## Development Workflow

### Local Setup

```bash
bundle install  # Install dependencies
bundle exec jekyll serve  # Run development server
```

### Content Guidelines

1. Blog Posts
   - Place in `_posts/` with correct date prefix
   - Include required frontmatter (see example in `2025-10-05-example-post.md`)
   - Use markdown for content formatting

2. Security Features
   - CSP headers defined in `_layouts/default.html`
   - Form submissions handled via FormSubmit.co

## Common Patterns

1. Asset References
   ```liquid
   {{ site.baseurl }}/img/path/to/image.jpg
   ```

2. Page/Post URLs
   ```liquid
   {{ post.url | relative_url }}
   ```

3. Blog Pagination
   - Configured in `_config.yml` (5 posts per page)
   - Navigation handled in `blog/index.html`