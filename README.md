# Hermes YouTube Plugin

Manage your **YouTube subscriptions and feed** from [Hermes Agent](https://github.com/e8kor/hermes-agent)
— list subscriptions, show recent uploads, and identify channels to prune. Uses the official
YouTube Data API v3 (read-only) via your existing Google OAuth.

- **Status** — connected channel, subscriber/video counts.
- **Subscriptions** — list channels you follow.
- **Feed** — recent uploads from subscribed channels.

## Install (community)

Requires [Hermes Agent](https://github.com/e8kor/hermes-agent), Python 3.9+, and a Google OAuth
token that includes the `youtube.readonly` scope. Enable the **YouTube Data API v3** in your
Google Cloud project first.

```bash
git clone https://github.com/e8kor/hermes-youtube-plugin.git
cd hermes-youtube-plugin
./install.sh                      # copies plugin + installs deps (google-api-python-client)
hermes plugins enable youtube     # takes effect next session
```

## Package layout

```
hermes-youtube-plugin/
├── install.sh        # one-shot installer
├── requirements.txt  # pip deps
├── plugin/           # the plugin source (→ ~/.hermes/plugins/youtube)
├── skills/           # bundled SKILL.md guidance
└── LICENSE           # MIT
```

## License

MIT — see [LICENSE](LICENSE).

---

# YouTube Plugin

Manage your YouTube subscriptions and feed. Uses the official YouTube Data
API via your existing Google OAuth (needs the `youtube.readonly` scope).

## Features

- **Status** — your connected channel, subscriber/video counts.
- **Subscriptions** — list the channels you follow, so you can review and
  decide which to prune.
- **Feed** — recent uploads from subscribed channels within a time window
  (your "feed" via the API).

## Setup

1. Ensure the Google OAuth token includes `youtube.readonly`:
   - Re-run the google-workspace OAuth flow (its `setup.py` now lists the
     YouTube scope), OR add it and re-authorize.
2. Enable the **YouTube Data API v3** in your Google Cloud project:
   https://console.cloud.google.com/apis/library/youtube.googleapis.com

## Usage

### Chat tools

`youtube_status`, `youtube_subs`, `youtube_feed`.

### Slash command

```
/youtube status
/youtube subs [--max N]
/youtube feed [--days N] [--max N]
```

### CLI

```
hermes youtube status
hermes youtube subs --max 100
hermes youtube feed --days 7
```

## Read-only limitation (important)

This plugin is **read-only** by design right now. The write scopes needed to
actually unsubscribe (`youtube.update` / `youtube`) are **restricted scopes**
that require Google's OAuth app verification process. Until that's done, the
plugin can list your subscriptions and surface which channels to prune, but
the actual unsubscribe must be done in the YouTube web UI (or after the app
passes verification).

## Data

No persistent store needed — this plugin reads live from the API. The token
is the shared `~/.hermes/google_token.json`.

## Debugging

`YOUTUBE_DEBUG=1` (or `--debug`) prints `[youtube]` trace to stderr.
