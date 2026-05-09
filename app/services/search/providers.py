from __future__ import annotations

from datetime import datetime
from typing import Any
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


def safe_float(value: Any, default: float = 0.5) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def extract_search_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    data = payload.get("data")
    candidates: Any = None

    if isinstance(data, dict):
        web_pages = data.get("webPages")
        if isinstance(web_pages, dict):
            candidates = web_pages.get("value")
        candidates = candidates or data.get("results") or data.get("items")
    elif isinstance(data, list):
        candidates = data

    candidates = candidates or payload.get("results") or payload.get("items") or []
    if isinstance(candidates, dict):
        candidates = candidates.get("value") or candidates.get("items") or []
    if not isinstance(candidates, list):
        return []

    return [row for row in candidates if isinstance(row, dict)]


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
        for row in extract_search_rows(data):
            url = row.get("url") or row.get("link") or row.get("displayUrl") or ""
            title = row.get("title") or row.get("name") or ""
            snippet = row.get("snippet") or row.get("summary") or row.get("description") or ""
            items.append(
                SourceItem(
                    title=title,
                    url=url,
                    snippet=snippet,
                    source_type=classify_source(url),
                    published_at=parse_datetime(row.get("datePublished") or row.get("dateLastCrawled")),
                    score=safe_float(row.get("score"), 0.5),
                    metadata={
                        "provider": self.provider,
                        "site_name": row.get("siteName"),
                        "display_url": row.get("displayUrl"),
                    },
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
