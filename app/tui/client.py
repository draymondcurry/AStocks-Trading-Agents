from __future__ import annotations

from typing import Any

import httpx


class BackendClient:
    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.transport = transport

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            transport=self.transport,
        ) as client:
            response = await client.request(method, path, **kwargs)
            response.raise_for_status()
            return response.json()

    async def health(self) -> dict[str, Any]:
        return await self._request("GET", "/api/v1/health")

    async def provider_status(self) -> dict[str, Any]:
        return await self._request("GET", "/api/v1/providers/status")

    async def bootstrap(self) -> dict[str, Any]:
        return await self._request("GET", "/api/v1/frontend/bootstrap")

    async def analyze(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._request("POST", "/api/v1/analysis/stock-pick", json=payload)

    async def search(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._request("POST", "/api/v1/search/query", json=payload)

    async def kline(self, symbol: str, period: str) -> dict[str, Any]:
        return await self._request(
            "GET",
            "/api/v1/market/kline",
            params={"symbol": symbol, "period": period},
        )

    async def fundamentals(self, symbol: str) -> dict[str, Any]:
        return await self._request(
            "GET",
            "/api/v1/market/fundamentals",
            params={"symbol": symbol},
        )

    async def remember(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._request("POST", "/api/v1/memory/remember", json=payload)

    async def recall(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._request("POST", "/api/v1/memory/recall", json=payload)

