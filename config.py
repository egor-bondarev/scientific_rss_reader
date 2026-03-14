from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def _env_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_int(value: str | None, default: int) -> int:
    if value is None or not value.strip():
        return default
    return int(value)


@dataclass(frozen=True)
class Config:
    rss_url: str
    telegram_bot_token: str
    telegram_chat_id: str
    start_lookback_minutes: int
    start_send_delay_seconds: int
    poll_interval_seconds: int
    db_path: Path
    include_summary: bool
    summary_max_chars: int
    telegram_disable_preview: bool


def load_config() -> Config:
    load_dotenv()

    rss_url = os.getenv("RSS_URL", "https://www.nature.com/subjects/scientific-community.rss").strip()
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()

    if not token:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN in .env")
    if not chat_id:
        raise RuntimeError("Missing TELEGRAM_CHAT_ID in .env (e.g., @your_channel)")

    return Config(
        rss_url=rss_url,
        telegram_bot_token=token,
        telegram_chat_id=chat_id,
        start_lookback_minutes=_env_int(os.getenv("START_LOOKBACK_MINUTES"), 60),
        start_send_delay_seconds=_env_int(os.getenv("START_SEND_DELAY_SECONDS"), 5),
        poll_interval_seconds=_env_int(os.getenv("POLL_INTERVAL_SECONDS"), 60),
        db_path=Path(os.getenv("DB_PATH", "./sent_items.sqlite3")).expanduser().resolve(),
        include_summary=_env_bool(os.getenv("INCLUDE_SUMMARY"), False),
        summary_max_chars=_env_int(os.getenv("SUMMARY_MAX_CHARS"), 500),
        telegram_disable_preview=_env_bool(os.getenv("TELEGRAM_DISABLE_PREVIEW"), False),
    )