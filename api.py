"""YouTube Data API layer for the youtube plugin.

Reuses the Hermes Google OAuth token (which now carries the youtube.readonly
scope). Provides read-only operations: the user's channel, subscriptions,
and recent uploads from subscribed channels (the "feed").

NOTE on write access: youtube.readonly is a non-restricted scope, so it was
accepted. The restricted write scopes (youtube.update / youtube / force-ssl)
require Google's verification process for the OAuth app, so this plugin is
read-only for now — it can list subscriptions and surface which channels to
prune, but cannot itself unsubscribe (that needs a write scope).

All functions return plain dicts and raise YouTubeError on failure; tool
handlers convert to JSON strings.
"""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

from .debug import debug

logger = logging.getLogger(__name__)


class YouTubeError(Exception):
    pass


def _home() -> str:
    return os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))


def _credentials():
    """Load the shared Google token."""
    from google.oauth2.credentials import Credentials
    token_path = os.path.join(_home(), "google_token.json")
    if not os.path.exists(token_path):
        raise YouTubeError(
            "No Google token found. Run the google-workspace setup / youtube OAuth first."
        )
    return Credentials.from_authorized_user_file(token_path)


def _service():
    """Build the YouTube Data API v3 service."""
    from googleapiclient.discovery import build
    try:
        return build("youtube", "v3", credentials=_credentials(), static_discovery=False)
    except Exception as exc:
        raise YouTubeError(f"Could not build YouTube client: {exc}")


def has_access() -> bool:
    """True if the Google token includes a YouTube scope."""
    import json
    try:
        tok = json.load(open(os.path.join(_home(), "google_token.json"), encoding="utf-8"))
        return any("youtube" in s for s in tok.get("scopes", []))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Channel / identity
# ---------------------------------------------------------------------------


def my_channel() -> Dict[str, Any]:
    yt = _service()
    r = yt.channels().list(part="snippet,statistics,contentDetails", mine=True).execute()
    items = r.get("items", [])
    if not items:
        raise YouTubeError("No channel found for this account.")
    ch = items[0]
    stats = ch.get("statistics", {})
    return {
        "title": ch.get("snippet", {}).get("title", ""),
        "id": ch.get("id", ""),
        "subscribers": stats.get("subscriberCount", "0"),
        "videos": stats.get("videoCount", "0"),
        "views": stats.get("viewCount", "0"),
        "uploads_playlist": ch.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads", ""),
    }


# ---------------------------------------------------------------------------
# Subscriptions
# ---------------------------------------------------------------------------


def subscriptions(max_results: int = 50) -> Dict[str, Any]:
    """List the user's channel subscriptions."""
    yt = _service()
    subs = []
    tok = None
    while len(subs) < max_results:
        r = yt.subscriptions().list(
            part="snippet", mine=True, maxResults=min(50, max_results - len(subs)),
            pageToken=tok,
        ).execute()
        for s in r.get("items", []):
            sn = s.get("snippet", {})
            subs.append({
                "channel_id": sn.get("resourceId", {}).get("channelId", ""),
                "title": sn.get("title", ""),
                "description": (sn.get("description", "") or "")[:80],
                "channel_url": f"https://www.youtube.com/channel/{sn.get('resourceId', {}).get('channelId','')}",
                "thumb": (sn.get("thumbnails", {}).get("default", {}) or {}).get("url", ""),
            })
        tok = r.get("nextPageToken")
        if not tok:
            break
    return {"count": len(subs), "subscriptions": subs}


# ---------------------------------------------------------------------------
# Feed: recent uploads from subscribed channels
# ---------------------------------------------------------------------------


def feed(days: int = 7, max_results: int = 30) -> Dict[str, Any]:
    """Return recent uploads from the user's subscribed channels.

    Approach: for each subscribed channel, get its uploads playlist's most
    recent video(s), and keep those published within *days*. This mirrors the
    YouTube Home feed (uploads from subscriptions) without a single "feed"
    endpoint.
    """
    from datetime import datetime, timedelta, timezone

    yt = _service()
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    subs_r = yt.subscriptions().list(part="snippet", mine=True, maxResults=50).execute()
    channel_ids = [
        s.get("snippet", {}).get("resourceId", {}).get("channelId", "")
        for s in subs_r.get("items", [])
    ]

    items = []
    for cid in channel_ids:
        try:
            # uploads playlist id for this channel
            ch = yt.channels().list(part="contentDetails", id=cid).execute()
            uploads = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
            pl = yt.playlistItems().list(
                part="snippet", playlistId=uploads, maxResults=5
            ).execute()
            for it in pl.get("items", []):
                sn = it.get("snippet", {})
                pub = sn.get("publishedAt", "")
                try:
                    pub_dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
                except Exception:
                    continue
                if pub_dt < cutoff:
                    continue
                vid_id = sn.get("resourceId", {}).get("videoId", "")
                if not vid_id:
                    continue
                items.append({
                    "video_id": vid_id,
                    "channel": sn.get("videoOwnerChannelTitle", sn.get("channelTitle", "")),
                    "title": sn.get("title", ""),
                    "published": pub,
                    "url": f"https://www.youtube.com/watch?v={vid_id}",
                })
                if len(items) >= max_results:
                    return {"count": len(items), "days": days, "videos": items}
        except Exception:
            continue

    items.sort(key=lambda v: v.get("published", ""), reverse=True)
    return {"count": len(items), "days": days, "videos": items}
