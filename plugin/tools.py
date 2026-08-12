"""Tool handlers — the code that runs when the LLM calls youtube tools.

All handlers return JSON strings and never raise.
"""
from __future__ import annotations

import json
from typing import Any, Dict

from . import api


def _ok(**kw) -> str:
    return json.dumps({"success": True, **kw}, ensure_ascii=False)


def _err(message: str, **kw) -> str:
    return json.dumps({"success": False, "error": message, **kw}, ensure_ascii=False)


def youtube_status(args: dict, **kwargs) -> str:
    if not api.has_access():
        return _err(
            "YouTube access not granted. The Google token lacks a YouTube scope. "
            "Re-run the google-workspace OAuth flow with youtube.readonly."
        )
    try:
        me = api.my_channel()
        return _ok(channel=me)
    except Exception as exc:
        return _err(str(exc))


def youtube_subs(args: dict, **kwargs) -> str:
    try:
        result = api.subscriptions(max_results=int(args.get("max_results", 50)))
        return _ok(**result)
    except Exception as exc:
        return _err(str(exc))


def youtube_feed(args: dict, **kwargs) -> str:
    try:
        result = api.feed(days=int(args.get("days", 7)),
                          max_results=int(args.get("max_results", 30)))
        return _ok(**result)
    except Exception as exc:
        return _err(str(exc))
