from __future__ import annotations

import aiohttp


class TelegramClient:
    def __init__(self, bot_token: str) -> None:
        self._base = f"https://api.telegram.org/bot{bot_token}"

    async def send_message(
        self,
        session: aiohttp.ClientSession,
        *,
        chat_id: str,
        text: str,
        disable_preview: bool,
    ) -> None:
        async with session.post(
            f"{self._base}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "disable_web_page_preview": disable_preview,
            },
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            if resp.status != 200:
                body = await resp.text()
                raise RuntimeError(f"Telegram sendMessage failed: {resp.status} {body}")
