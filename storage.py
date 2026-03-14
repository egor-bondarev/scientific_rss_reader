from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import aiosqlite


class SentStore:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._conn: aiosqlite.Connection | None = None

    async def open(self) -> None:
        self._conn = await aiosqlite.connect(str(self._db_path))
        await self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sent_items (
                item_id TEXT PRIMARY KEY,
                sent_at TEXT NOT NULL
            )
            """
        )
        await self._conn.commit()

    async def close(self) -> None:
        if self._conn is not None:
            await self._conn.close()

    async def has(self, item_id: str) -> bool:
        assert self._conn is not None
        async with self._conn.execute(
            "SELECT 1 FROM sent_items WHERE item_id = ? LIMIT 1",
            (item_id,),
        ) as cur:
            row = await cur.fetchone()
            return row is not None

    async def mark_sent(self, item_id: str) -> None:
        assert self._conn is not None
        sent_at = datetime.now(timezone.utc).isoformat()
        await self._conn.execute(
            "INSERT OR IGNORE INTO sent_items (item_id, sent_at) VALUES (?, ?)",
            (item_id, sent_at),
        )
        await self._conn.commit()