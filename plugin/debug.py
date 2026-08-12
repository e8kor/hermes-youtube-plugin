"""Central debug helper for the youtube plugin."""
from __future__ import annotations

import os
import sys

_enabled = bool(os.environ.get("YOUTUBE_DEBUG", ""))


def set_debug(value: bool) -> None:
    global _enabled
    _enabled = value


def is_debug() -> bool:
    return _enabled


def debug(*args) -> None:
    if not _enabled:
        return
    print(f"[youtube] {' '.join(str(a) for a in args)}", file=sys.stderr)
