"""youtube plugin — registration."""
from __future__ import annotations

import logging

from . import api, cli, schemas, slash, tools

logger = logging.getLogger(__name__)


def _on_session_start(session_id: str = "", **kwargs):
    """Observer hook — no injection. Logs a hint if YouTube access is missing."""
    try:
        if not api.has_access():
            logger.info(
                "youtube plugin: no YouTube scope in the Google token. "
                "Re-run google-workspace OAuth with youtube.readonly."
            )
    except Exception:
        pass


def register(ctx) -> None:
    ctx.register_tool(
        name="youtube_status", toolset="youtube",
        schema=schemas.YOUTUBE_STATUS, handler=tools.youtube_status,
        check_fn=api.has_access,
    )
    ctx.register_tool(
        name="youtube_subs", toolset="youtube",
        schema=schemas.YOUTUBE_SUBS, handler=tools.youtube_subs,
        check_fn=api.has_access,
    )
    ctx.register_tool(
        name="youtube_feed", toolset="youtube",
        schema=schemas.YOUTUBE_FEED, handler=tools.youtube_feed,
        check_fn=api.has_access,
    )

    ctx.register_command(
        "youtube",
        handler=lambda raw: slash._handle(raw, ctx=ctx),
        description="Manage YouTube subscriptions and feed.",
        args_hint="<status|subs|feed>",
    )

    ctx.register_cli_command(
        name="youtube",
        help="Manage YouTube subscriptions and feed (status, subs, feed)",
        setup_fn=cli._setup_argparse,
        handler_fn=None,
    )

    ctx.register_hook("on_session_start", _on_session_start)

    logger.info("youtube plugin registered (tools, /youtube, hermes youtube).")
