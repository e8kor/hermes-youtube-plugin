"""Plain-text table rendering for chat/CLI output.

These plugins' slash commands and CLI subcommands currently return raw JSON
strings from the tool handlers (e.g. ``{"success": true, "accounts": [...]}``).
For a human reading the terminal, a fixed-width aligned table is far easier to
scan. This module renders a list of row-dicts into an aligned monospace table,
with no third-party dependency.

Usage::

    from . import tables
    rows = [{"id": "pub_1", "title": "Hello", "status": "draft"}, ...]
    return tables.render(rows, columns=[
        ("ID", "id"),
        ("Title", "title"),
        ("Status", "status"),
    ])

Column spec is a list of ``(header, key)`` tuples. A key may be a callable
``lambda row: ...`` for derived/composed values. Columns render in the given
order. Long cell values are truncated to the column width (the last column is
NOT truncated so titles/messages don't get chopped mid-way).
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple, Union

# A column is (header, key) where key is a dict key, dotted path, or callable.
Column = Tuple[str, Union[str, Callable[[Dict[str, Any]], Any]]]


def _cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (list, tuple)):
        return ", ".join(str(v) for v in value)
    return str(value)


def _get(row: Dict[str, Any], key: Union[str, Callable[[Dict[str, Any]], Any]]) -> Any:
    if callable(key):
        return key(row)
    if "." in key:
        cur: Any = row
        for part in key.split("."):
            if isinstance(cur, dict):
                cur = cur.get(part)
            else:
                return None
        return cur
    return row.get(key)


def render(rows: Sequence[Dict[str, Any]], columns: List[Column],
           title: Optional[str] = None, empty: str = "(none)") -> str:
    """Render ``rows`` as an aligned table.

    Columns are sized to the widest cell (min 3, capped so the table doesn't
    blow out on huge strings). The last column is not truncated. If ``rows``
    is empty, ``empty`` is returned (under ``title`` if given).
    """
    rows = list(rows or [])
    headers = [h for h, _ in columns]

    # Precompute cell strings for width sizing.
    cells = {idx: [_cell(_get(r, key)) for r in rows] for idx, (h, key) in enumerate(columns)}

    # Column widths: max(header len, widest cell len), capped at 40, last col uncapped.
    widths: List[int] = []
    for idx, h in enumerate(headers):
        maxlen = len(h)
        cap = 40 if idx < len(columns) - 1 else 10 ** 6
        for c in cells[idx]:
            maxlen = max(maxlen, len(c))
        widths.append(min(maxlen, cap) if idx < len(columns) - 1 else maxlen)

    def fmt_row(vals: List[str]) -> str:
        parts = []
        for i, v in enumerate(vals):
            if i < len(widths) - 1:
                parts.append(v[:widths[i]].ljust(widths[i]))
            else:
                parts.append(v)
        return "  ".join(parts).rstrip()

    line = "  ".join(h.ljust(widths[i]) for i, h in enumerate(headers)).rstrip()
    sep = "  ".join("-" * widths[i] for i in range(len(widths)))

    out = []
    if title:
        out.append(title)
    out.append(line)
    out.append(sep)
    if not rows:
        return (title + "\n" if title else "") + empty
    for r in rows:
        out.append(fmt_row([_cell(_get(r, key)) for _, key in columns]))
    return "\n".join(out)


def render_pairs(pairs: Iterable[Tuple[str, Any]], title: Optional[str] = None) -> str:
    """Render a single-record key/value layout (for ``show``/detail output)."""
    items = [(k, _cell(v)) for k, v in pairs]
    if not items:
        return title or "(no data)"
    w = max(len(k) for k, _ in items)
    out = []
    if title:
        out.append(title)
    for k, v in items:
        out.append(f"{k.ljust(w)} : {v}")
    return "\n".join(out)
