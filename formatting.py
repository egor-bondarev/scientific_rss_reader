from __future__ import annotations

from html import unescape
import re

from rss_reader import RssItem

_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(text: str) -> str:
    text = unescape(text or "")
    text = _TAG_RE.sub("", text)
    return re.sub(r"\s+", " ", text).strip()


def format_message(item: RssItem, include_summary: bool, summary_max_chars: int) -> str:
    parts = [item.title, item.link]

    if include_summary:
        summary = _strip_html(item.summary)
        if summary:
            if len(summary) > summary_max_chars:
                summary = summary[: summary_max_chars - 1].rstrip() + "…"
            parts.append("")
            parts.append(summary)

    return "\n".join(parts).strip()