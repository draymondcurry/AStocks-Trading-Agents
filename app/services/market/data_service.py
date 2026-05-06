from __future__ import annotations

from typing import Any

import pandas as pd

try:
    import akshare as ak
except Exception:  # pragma: no cover
    ak = None


class MarketDataService:
    def __init__(self, enable_mocks: bool = True):
        self.enable_mocks = enable_mocks

    def _mock_kline(self, symbol: str, period: str) -> list[dict[str, Any]]:
        frame = pd.DataFrame(
            [
                {"timestamp": "2026-05-01", "open": 10.2, "close": 10.8, "high": 10.9, "low": 10.1, "volume": 120000},
                {"timestamp": "2026-05-02", "open": 10.8, "close": 11.1, "high": 11.3, "low": 10.7, "volume": 168000},
                {"timestamp": "2026-05-03", "open": 11.1, "close": 10.95, "high": 11.2, "low": 10.8, "volume": 142000},
            ]
        )
        return [{"symbol": symbol, "period": period, **row} for row in frame.to_dict(orient="records")]

    def _mock_fundamentals(self, symbol: str) -> dict[str, Any]:
        return {
            "symbol": symbol,
            "pe_ttm": 18.5,
            "pb": 3.1,
            "roe": 0.156,
            "revenue_growth": 0.24,
            "net_profit_growth": 0.31,
            "debt_to_asset": 0.41,
        }

    def get_kline(
        self,
        symbol: str,
        period: str,
        start_date: str | None = None,
        end_date: str | None = None,
        adjust: str = "",
    ) -> list[dict[str, Any]]:
        if self.enable_mocks or ak is None:
            return self._mock_kline(symbol, period)

        if period == "daily":
            frame = ak.stock_zh_a_hist(
                symbol=symbol,
                start_date=start_date or "20250101",
                end_date=end_date or "20261231",
                adjust=adjust,
            )
        else:
            frame = ak.stock_zh_a_hist_min_em(
                symbol=symbol,
                period=period.replace("min", ""),
                adjust=adjust,
            )
        frame = frame.rename(
            columns={
                frame.columns[0]: "timestamp",
                frame.columns[1]: "open",
                frame.columns[2]: "close",
                frame.columns[3]: "high",
                frame.columns[4]: "low",
                frame.columns[5]: "volume",
            }
        )
        return [{"symbol": symbol, "period": period, **row} for row in frame.to_dict(orient="records")]

    def get_fundamentals(self, symbol: str) -> dict[str, Any]:
        if self.enable_mocks or ak is None:
            return self._mock_fundamentals(symbol)
        frame = ak.stock_individual_info_em(symbol=symbol)
        metrics = {}
        for _, row in frame.iterrows():
            metrics[str(row["item"])] = row["value"]
        metrics["symbol"] = symbol
        return metrics
