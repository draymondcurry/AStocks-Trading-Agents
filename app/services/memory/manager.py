from __future__ import annotations

from app.core.settings import Settings
from app.services.llm.base import BaseLLMClient
from app.services.memory.store import MemoryStore


class MemoryManager:
    def __init__(self, store: MemoryStore, llm: BaseLLMClient, settings: Settings):
        self.store = store
        self.llm = llm
        self.settings = settings

    async def remember(self, session_id: str, namespace: str, content: str, importance: float) -> None:
        embedding = await self.llm.embed(content)
        await self.store.remember_short_term(
            session_id,
            namespace,
            content,
            importance,
            self.settings.short_memory_ttl_minutes,
        )
        await self.store.remember_long_term(session_id, namespace, content, embedding, importance)

    async def recall(self, session_id: str, namespace: str, query: str, limit: int) -> dict:
        embedding = await self.llm.embed(query)
        short_term = await self.store.recall_short_term(session_id, namespace, limit)
        long_term = await self.store.recall_long_term(
            session_id,
            namespace,
            embedding,
            min(limit, self.settings.long_memory_top_k),
        )
        return {"short_term": short_term, "long_term": long_term}

