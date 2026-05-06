from __future__ import annotations

from datetime import datetime
from urllib.parse import urlparse

import httpx

from app.schemas.common import SourceItem
from app.services.search.base import BaseSearchProvider


def classify_source(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if host.endswith(".gov.cn") or "gov.cn" in host or "csrc" in host:
        return "policy"
    if any(token in host for token in ["cninfo", "sse.com", "szse.cn", "company", "investor"]):
        return "official"
    if any(token in host for token in ["stcn", "cs.com", "eastmoney", "10jqka", "caixin", "yicai"]):
        return "news"
    return "social"


class MockSearchProvider(BaseSearchProvider):
    provider = "mock"

    async def search(self, query: str, max_results: int = 8) -> list[SourceItem]:
        items = [
            SourceItem(
                title=f"Mock policy insight for {query}",
                url="https://www.gov.cn/mock-policy",
                snippet="Mock policy source demonstrating ranking behaviour.",
                source_type="policy",
                published_at=datetime.utcnow(),
                score=0.95,
            ),
            SourceItem(
                title=f"Mock company filing for {query}",
                url="https://www.cninfo.com.cn/mock-filing",
                snippet="Mock official disclosure for testing source attribution.",
                source_type="official",
                published_at=datetime.utcnow(),
                score=0.90,
            ),
        ]
        return self.rank(items[:max_results])


class BochaSearchProvider(BaseSearchProvider):
    provider = "bocha"

    def __init__(self, api_key: str, base_url: str, timeout: int):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout

    async def search(self, query: str, max_results: int = 8) -> list[SourceItem]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"query": query, "count": max_results},
            )
            response.raise_for_status()
            data = response.json()
        items = []
        for row in data.get("data", data.get("results", [])):
            url = row.get("url") or row.get("link") or ""
            items.append(
                SourceItem(
                    title=row.get("title", ""),
                    url=url,
                    snippet=row.get("snippet", row.get("summary", "")),
                    source_type=classify_source(url),
                    score=float(row.get("score", 0.5)),
                )
            )
        return self.rank(items[:max_results])


class GoogleSearchProvider(BaseSearchProvider):
    provider = "google"

    def __init__(self, api_key: str, cx: str, timeout: int):
        self.api_key = api_key
        self.cx = cx
        self.timeout = timeout

    async def search(self, query: str, max_results: int = 8) -> list[SourceItem]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                "https://www.googleapis.com/customsearch/v1",
                params={"key": self.api_key, "cx": self.cx, "q": query, "num": max_results},
            )
            response.raise_for_status()
            data = response.json()
        items = []
        for row in data.get("items", []):
            url = row.get("link", "")
            items.append(
                SourceItem(
                    title=row.get("title", ""),
                    url=url,
                    snippet=row.get("snippet", ""),
                    source_type=classify_source(url),
                    score=0.6,
                )
            )
        return self.rank(items[:max_results])

