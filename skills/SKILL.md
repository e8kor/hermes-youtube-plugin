---
name: youtube-subscriptions
description: "Manage YouTube subs and feed via the youtube plugin."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [YouTube, Subscriptions, Feed, Media, Plugin]
    related_skills: [google-workspace, youtube-content]
---

# YouTube Subscriptions & Feed

Manage your YouTube subscriptions and feed through the `youtube` Hermes plugin.

> **Prefer the plugin.** The `youtube` plugin (tools `youtube_status`/
> `youtube_subs`/`youtube_feed`, the `/youtube` slash command, and the
> `hermes youtube` CLI) implements the workflow. Use its tools; this skill
> documents how and the constraints.

## When to Use

- "What channels do I follow on YouTube?"
- "Show my YouTube feed / recent uploads from my subscriptions."
- "Which subscriptions should I prune / unsubscribe from?"
- "Check my YouTube channel status."

## Setup (one-time)

1. **Add the YouTube scope to your Google OAuth token.** The token at
   `~/.hermes/google_token.json` must include `youtube.readonly`. This is a
   **non-restricted** scope, so it's accepted without app verification. Add it
   to `google-workspace`'s `setup.py` SCOPES and re-run the OAuth flow
   (auth-url → approve → paste code). Only `youtube.readonly`; the write
   scopes are restricted and will be rejected (400 invalid_scope).
2. **Enable the YouTube Data API v3** in the Google Cloud project:
   https://console.cloud.google.com/apis/library/youtube.googleapis.com
   (403 "API has not been used" until enabled).

## Usage

```
hermes youtube status                     # connected channel + counts
hermes youtube subs --max 100             # list channel subscriptions
hermes youtube feed --days 7 --max 30     # recent uploads from subs
```

Chat: `/youtube status`, `/youtube subs`, `/youtube feed --days 7`.
Agent tools: `youtube_status`, `youtube_subs`, `youtube_feed`.

## Feed semantics

There is no single "home feed" REST endpoint. The plugin approximates it by:
for each subscribed channel, get its uploads playlist's most recent videos and
keep those published within the window. This mirrors "recent uploads from
channels I follow" well.

## Constraint: read-only (no unsubscribe yet)

- The write scopes (`youtube.update` / `youtube` / `force-ssl`) are
  **restricted scopes** requiring Google's OAuth app verification process.
  A consumer/testing-mode app gets `400 invalid_scope` for them.
- So the plugin can **list** subscriptions and surface which channels to prune,
  but the actual unsubscribe must happen in the YouTube web UI, or after the
  OAuth app passes Google verification.

## Pitfalls

- **403 "API has not been used in project"** = the YouTube Data API isn't
  enabled in the Cloud console (not an auth problem). Enable it once.
- **`400 invalid_scope` on youtube.update** = restricted scope; drop it and use
  only `youtube.readonly`.
- **Google token missing the YouTube scope** → tools hidden (clean `check_fn`
  gate on `has_access()`); re-run OAuth.
- **`youtube-content` skill is different** — that one summarizes a *specific*
  video's transcript; this plugin manages your *subscriptions/feed*.
- **New slash commands take effect next session** — `/youtube` needs a restart.

## Verification

```bash
hermes youtube status            # shows connected channel (or scope-needed msg)
hermes plugins list              # youtube enabled?
```

## Data

Reads live from the API; no persistent store. Token is the shared
`~/.hermes/google_token.json`.
