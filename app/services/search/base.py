from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas.common import SourceItem


SOURCE_PRIORITY = {
    "policy": 4,
    "official": 3,
    "news": 2,
    "social": 1,
}


class BaseSearchProvider(ABC):
    provider: str

    @abstractmethod
    async def search(self, query: str, max_results: int = 8) -> list[SourceItem]:
        raise NotImplementedError

    def rank(self, items: list[SourceItem]) -> list[SourceItem]:
        return sorted(
            items,
            key=lambda item: (SOURCE_PRIORITY.get(item.source_type, 0), item.score),
            reverse=True,
        )

