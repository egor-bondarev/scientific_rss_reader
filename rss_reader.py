from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import aiohttp
import feedparser


@dataclass(frozen=True)
class RssItem:
    item_id: str
    title: str
    link: str
    published_at: datetime
    summary: str


def _to_datetime(entry: dict) -> Optional[datetime]:
    ts = entry.get("published_parsed") or entry.get("updated_parsed")
    if not ts:
        return None
    return datetime(*ts[:6], tzinfo=timezone.utc)


def _make_item_id(entry: dict) -> str:
    return (
        entry.get("id")
        or entry.get("guid")
        or entry.get("link")
        or f"{entry.get('title','').strip()}::{entry.get('published','')}"
    )


async def fetch_rss_items(session: aiohttp.ClientSession, rss_url: str) -> list[RssItem]:
    headers = {"User-Agent": "rss2tg-demo/0.1 (+https://example.local)"}
    async with session.get(rss_url, headers=headers, timeout=aiohttp.ClientTimeout(total=20)) as resp:
        resp.raise_for_status()
        content = await resp.text()

    parsed = feedparser.parse(content)
    items: list[RssItem] = []

    for e in parsed.entries:
        dt = _to_datetime(e)
        if dt is None:
            continue

        title = (e.get("title") or "").strip()
        link = (e.get("link") or "").strip()
        summary = (e.get("summary") or e.get("description") or "").strip()
        item_id = _make_item_id(e).strip()

        if not title or not link or not item_id:
            continue

        items.append(RssItem(item_id=item_id, title=title, link=link, published_at=dt, summary=summary))

    return items