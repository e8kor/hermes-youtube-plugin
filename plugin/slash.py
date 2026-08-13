"""In-session slash command handler for ``/youtube``."""
from __future__ import annotations

import json
from typing import Optional

from . import tables, tools


def _as_dict(json_str: str) -> dict:
    try:
        return json.loads(json_str)
    except Exception:
        return {}


def _render_subs(subs_json: str) -> str:
    data = _as_dict(subs_json)
    subs = data.get("subscriptions") or []
    if not subs:
        return "No subscriptions."
    rows = [{
        "title": s.get("title", ""),
        "channel_id": s.get("channel_id", ""),
    } for s in subs]
    return tables.render(rows, columns=[
        ("Title", "title"), ("Channel ID", "channel_id"),
    ], title=f"Subscriptions ({data.get('count', len(subs))}):")


def _render_feed(feed_json: str) -> str:
    data = _as_dict(feed_json)
    vids = data.get("videos") or []
    if not vids:
        return "No videos in the feed."
    rows = [{
        "channel": v.get("channel", ""),
        "title": v.get("title", ""),
        "published": v.get("published", ""),
    } for v in vids]
    return tables.render(rows, columns=[
        ("Channel", "channel"), ("Title", "title"), ("Published", "published"),
    ], title=f"Feed (last {data.get('days', '')}d, {data.get('count', len(vids))} videos):")


_HELP = """\
/youtube — YouTube subscriptions & feed manager

CONNECT
  status                     Show connected channel + access status

CONTENT
  subs [--max N]             List your channel subscriptions
  feed [--days N] [--max N]  Recent uploads from channels you follow
"""


def _handle(raw_args: str, ctx=None) -> Optional[str]:
    argv = raw_args.strip().split()
    if not argv or argv[0] in {"help", "-h", "--help"}:
        return _HELP

    sub = argv[0]

    if sub == "status":
        return tools.youtube_status({})

    if sub == "subs":
        max_n = 50
        for i in range(1, len(argv)):
            if argv[i] == "--max" and i + 1 < len(argv):
                max_n = int(argv[i + 1])
        return _render_subs(tools.youtube_subs({"max_results": max_n}))

    if sub == "feed":
        days = 7
        max_n = 30
        for i in range(1, len(argv)):
            if argv[i] == "--days" and i + 1 < len(argv):
                days = int(argv[i + 1])
            elif argv[i] == "--max" and i + 1 < len(argv):
                max_n = int(argv[i + 1])
        return _render_feed(tools.youtube_feed({"days": days, "max_results": max_n}))

    return _HELP
