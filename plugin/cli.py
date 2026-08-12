"""CLI subcommand tree for ``hermes youtube``.

    CONNECT   status
    CONTENT   subs, feed
"""
from __future__ import annotations

from typing import Any, Dict

from . import api
from .debug import set_debug


def _print_subs(result: Dict[str, Any]) -> None:
    print(f"Subscriptions ({result['count']}):")
    for s in result["subscriptions"]:
        print(f"  {s['title']:<40} {s['channel_id']}")


def _print_feed(result: Dict[str, Any]) -> None:
    print(f"Feed (last {result['days']}d, {result['count']} videos):")
    for v in result["videos"]:
        print(f"  {v['channel']:<30} | {v['title'][:50]} | {v['published'][:10]}")


def _cmd_status(args) -> None:
    if getattr(args, "debug", False):
        set_debug(True)
    if not api.has_access():
        print("YouTube access not granted. Re-run google-workspace OAuth with youtube.readonly scope.")
        return
    try:
        me = api.my_channel()
        print(f"Channel: {me['title']}")
        print(f"  subscribers={me['subscribers']}  videos={me['videos']}  views={me['views']}")
    except api.YouTubeError as exc:
        print(f"Error: {exc}")


def _cmd_subs(args) -> None:
    if getattr(args, "debug", False):
        set_debug(True)
    try:
        _print_subs(api.subscriptions(max_results=getattr(args, "max", 50)))
    except api.YouTubeError as exc:
        print(f"Error: {exc}")


def _cmd_feed(args) -> None:
    if getattr(args, "debug", False):
        set_debug(True)
    try:
        _print_feed(api.feed(days=getattr(args, "days", 7),
                             max_results=getattr(args, "max", 30)))
    except api.YouTubeError as exc:
        print(f"Error: {exc}")


def _setup_argparse(subparser) -> None:
    subs = subparser.add_subparsers(dest="yt_cmd")

    p_st = subs.add_parser("status", help="Show channel + access status")
    p_st.add_argument("--debug", action="store_true")
    p_st.set_defaults(func=_cmd_status)

    p_subs = subs.add_parser("subs", help="List channel subscriptions")
    p_subs.add_argument("--max", type=int, default=50)
    p_subs.add_argument("--debug", action="store_true")
    p_subs.set_defaults(func=_cmd_subs)

    p_feed = subs.add_parser("feed", help="Show recent uploads from subscribed channels")
    p_feed.add_argument("--days", type=int, default=7)
    p_feed.add_argument("--max", type=int, default=30)
    p_feed.add_argument("--debug", action="store_true")
    p_feed.set_defaults(func=_cmd_feed)

    subparser.set_defaults(func=_cmd_status)
