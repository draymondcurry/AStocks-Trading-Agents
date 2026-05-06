from __future__ import annotations

import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

import aiosqlite


def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    numerator = sum(x * y for x, y in zip(vector_a, vector_b))
    left = math.sqrt(sum(x * x for x in vector_a))
    right = math.sqrt(sum(y * y for y in vector_b))
    if left == 0 or right == 0:
        return 0.0
    return numerator / (left * right)


class MemoryStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection: aiosqlite.Connection | None = None

    async def initialize(self) -> None:
        db_parent = Path(self.db_path).expanduser().parent
        if str(db_parent) not in ("", "."):
            db_parent.mkdir(parents=True, exist_ok=True)
        self.connection = await aiosqlite.connect(self.db_path)
        await self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS short_term_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                namespace TEXT NOT NULL,
                content TEXT NOT NULL,
                importance REAL NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS long_term_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                namespace TEXT NOT NULL,
                content TEXT NOT NULL,
                embedding TEXT NOT NULL,
                importance REAL NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        await self.connection.commit()

    async def close(self) -> None:
        if self.connection:
            await self.connection.close()

    async def remember_short_term(
        self,
        session_id: str,
        namespace: str,
        content: str,
        importance: float,
        ttl_minutes: int,
    ) -> None:
        assert self.connection is not None
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=ttl_minutes)
        await self.connection.execute(
            """
            INSERT INTO short_term_memory(session_id, namespace, content, importance, expires_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                namespace,
                content,
                importance,
                expires_at.isoformat(),
                now.isoformat(),
            ),
        )
        await self.connection.commit()

    async def remember_long_term(
        self,
        session_id: str,
        namespace: str,
        content: str,
        embedding: list[float],
        importance: float,
    ) -> None:
        assert self.connection is not None
        await self.connection.execute(
            """
            INSERT INTO long_term_memory(session_id, namespace, content, embedding, importance, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                namespace,
                content,
                json.dumps(embedding),
                importance,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        await self.connection.commit()

    async def recall_short_term(self, session_id: str, namespace: str, limit: int) -> list[dict]:
        assert self.connection is not None
        now = datetime.now(timezone.utc).isoformat()
        await self.connection.execute(
            "DELETE FROM short_term_memory WHERE expires_at < ?",
            (now,),
        )
        await self.connection.commit()
        cursor = await self.connection.execute(
            """
            SELECT content, importance, created_at
            FROM short_term_memory
            WHERE session_id = ? AND namespace = ?
            ORDER BY importance DESC, created_at DESC
            LIMIT ?
            """,
            (session_id, namespace, limit),
        )
        rows = await cursor.fetchall()
        return [{"content": row[0], "importance": row[1], "created_at": row[2]} for row in rows]

    async def recall_long_term(
        self,
        session_id: str,
        namespace: str,
        embedding: list[float],
        limit: int,
    ) -> list[dict]:
        assert self.connection is not None
        cursor = await self.connection.execute(
            """
            SELECT content, embedding, importance, created_at
            FROM long_term_memory
            WHERE session_id = ? AND namespace = ?
            """,
            (session_id, namespace),
        )
        rows = await cursor.fetchall()
        scored = []
        for content, raw_embedding, importance, created_at in rows:
            score = cosine_similarity(embedding, json.loads(raw_embedding)) * 0.8 + importance * 0.2
            scored.append(
                {
                    "content": content,
                    "score": round(score, 4),
                    "importance": importance,
                    "created_at": created_at,
                }
            )
        return sorted(scored, key=lambda item: item["score"], reverse=True)[:limit]
