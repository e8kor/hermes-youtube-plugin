"""Tool schemas — what the LLM sees for the youtube plugin."""

YOUTUBE_STATUS = {
    "name": "youtube_status",
    "description": (
        "Show the youtube plugin status: the connected channel and whether YouTube "
        "API access is available. Use when the user asks about YouTube plugin health."
    ),
    "parameters": {"type": "object", "properties": {}},
}

YOUTUBE_SUBS = {
    "name": "youtube_subs",
    "description": (
        "List the user's YouTube channel subscriptions. Use when the user wants to "
        "see what channels they follow, review subscriptions, or decide which to prune. "
        "Optionally limit the count."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "max_results": {
                "type": "integer",
                "description": "Max subscriptions to return (default 50).",
            },
        },
    },
}

YOUTUBE_FEED = {
    "name": "youtube_feed",
    "description": (
        "Show the user's YouTube feed: recent uploads from subscribed channels within "
        "a time window. Use when the user wants to catch up on what channels they "
        "follow have posted recently, or review their feed."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "days": {
                "type": "integer",
                "description": "How far back to look for uploads (default 7 days).",
            },
            "max_results": {
                "type": "integer",
                "description": "Max videos to return (default 30).",
            },
        },
    },
}
