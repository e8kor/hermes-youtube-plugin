"""In-session slash command handler for ``/youtube``."""
from __future__ import annotations

from typing import Optional

from . import tools


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
        return tools.youtube_subs({"max_results": max_n})

    if sub == "feed":
        days = 7
        max_n = 30
        for i in range(1, len(argv)):
            if argv[i] == "--days" and i + 1 < len(argv):
                days = int(argv[i + 1])
            elif argv[i] == "--max" and i + 1 < len(argv):
                max_n = int(argv[i + 1])
        return tools.youtube_feed({"days": days, "max_results": max_n})

    return _HELP
