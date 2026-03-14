from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

import aiohttp

from config import load_config
from formatting import format_message
from rss_reader import fetch_rss_items, RssItem
from storage import SentStore
from telegram_client import TelegramClient


async def _send_start_backlog(
    *,
    items: list[RssItem],
    store: SentStore,
    tg: TelegramClient,
    session: aiohttp.ClientSession,
    chat_id: str,
    lookback_minutes: int,
    delay_seconds: int,
    include_summary: bool,
    summary_max_chars: int,
    disable_preview: bool,
) -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=lookback_minutes)
    backlog = [i for i in items if i.published_at >= cutoff]
    backlog.sort(key=lambda x: x.published_at)

    for item in backlog:
        if await store.has(item.item_id):
            continue
        await tg.send_message(
            session,
            chat_id=chat_id,
            text=format_message(item, include_summary, summary_max_chars),
            disable_preview=disable_preview,
        )
        await store.mark_sent(item.item_id)
        await asyncio.sleep(max(0, int(delay_seconds)))


async def _send_new_items(
    *,
    items: list[RssItem],
    store: SentStore,
    tg: TelegramClient,
    session: aiohttp.ClientSession,
    chat_id: str,
    include_summary: bool,
    summary_max_chars: int,
    disable_preview: bool,
) -> int:
    sent = 0
    for item in sorted(items, key=lambda x: x.published_at):
        if await store.has(item.item_id):
            continue
        await tg.send_message(
            session,
            chat_id=chat_id,
            text=format_message(item, include_summary, summary_max_chars),
            disable_preview=disable_preview,
        )
        await store.mark_sent(item.item_id)
        sent += 1
    return sent


async def amain() -> None:
    cfg = load_config()

    store = SentStore(cfg.db_path)
    await store.open()

    tg = TelegramClient(cfg.telegram_bot_token)

    try:
        async with aiohttp.ClientSession() as session:
            items = await fetch_rss_items(session, cfg.rss_url)
            await _send_start_backlog(
                items=items,
                store=store,
                tg=tg,
                session=session,
                chat_id=cfg.telegram_chat_id,
                lookback_minutes=cfg.start_lookback_minutes,
                delay_seconds=cfg.start_send_delay_seconds,
                include_summary=cfg.include_summary,
                summary_max_chars=cfg.summary_max_chars,
                disable_preview=cfg.telegram_disable_preview,
            )

            while True:
                await asyncio.sleep(max(5, int(cfg.poll_interval_seconds)))
                items = await fetch_rss_items(session, cfg.rss_url)
                await _send_new_items(
                    items=items,
                    store=store,
                    tg=tg,
                    session=session,
                    chat_id=cfg.telegram_chat_id,
                    include_summary=cfg.include_summary,
                    summary_max_chars=cfg.summary_max_chars,
                    disable_preview=cfg.telegram_disable_preview,
                )
    finally:
        await store.close()


def main() -> None:
    asyncio.run(amain())


if __name__ == "__main__":
    main()