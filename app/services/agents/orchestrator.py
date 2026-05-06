from __future__ import annotations

import asyncio
import json
from statistics import mean

from app.schemas.common import AgentInsight, AlphaSignal, SourceItem
from app.services.kg.graph_service import KnowledgeGraphService
from app.services.llm.base import BaseLLMClient
from app.services.market.data_service import MarketDataService
from app.services.search.base import BaseSearchProvider


class AgentOrchestrator:
    def __init__(
        self,
        llm: BaseLLMClient,
        search_provider: BaseSearchProvider,
        market_service: MarketDataService,
        graph_service: KnowledgeGraphService,
    ):
        self.llm = llm
        self.search_provider = search_provider
        self.market_service = market_service
        self.graph_service = graph_service

    async def _run_agent(
        self,
        agent_name: str,
        symbol: str,
        query: str,
        fundamentals: dict,
        sources: list[SourceItem],
    ) -> AgentInsight:
        prompt = f"""
你是{agent_name}智能体。请围绕A股标的 {symbol} 输出 JSON：
{{
  "summary": "...",
  "score": 0-1,
  "signals": [{{"name":"", "direction":"bullish/bearish/neutral", "score":0-1, "reason":""}}]
}}

基本面：{json.dumps(fundamentals, ensure_ascii=False)}
资讯：{json.dumps([item.model_dump(mode='json') for item in sources[:5]], ensure_ascii=False)}
任务：{query}
"""
        raw = await self.llm.generate(prompt, system_prompt="You are an A-share multi-agent analyst.")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {
                "summary": raw[:300],
                "score": 0.55,
                "signals": [{"name": agent_name, "direction": "neutral", "score": 0.55, "reason": "Fallback parse"}],
            }
        signals = [AlphaSignal(**signal) for signal in payload.get("signals", [])]
        return AgentInsight(
            agent=agent_name,
            summary=payload.get("summary", ""),
            score=float(payload.get("score", 0.5)),
            signals=signals,
            sources=sources[:3],
        )

    async def analyze(
        self,
        symbol: str,
        company_name: str | None,
        query: str,
        include_minutes: bool,
    ) -> dict:
        search_query = f"{company_name or symbol} A股 政策 公司 公告 新闻 情绪"
        sources = await self.search_provider.search(search_query, max_results=8)
        fundamentals = self.market_service.get_fundamentals(symbol)
        daily_kline = self.market_service.get_kline(symbol, "daily")
        minute_kline = self.market_service.get_kline(symbol, "5min") if include_minutes else []

        tasks = [
            self._run_agent("policy_agent", symbol, query, fundamentals, sources),
            self._run_agent("market_agent", symbol, query, fundamentals, sources),
            self._run_agent("sentiment_agent", symbol, query, fundamentals, sources),
            self._run_agent("risk_agent", symbol, query, fundamentals, sources),
        ]
        insights = await asyncio.gather(*tasks)

        kg = self.graph_service.build(symbol, company_name, sources, fundamentals)
        all_signals = [signal.model_dump() for insight in insights for signal in insight.signals]
        confidence = round(mean(insight.score for insight in insights), 4)
        recommendation = "hold"
        bullish = sum(1 for signal in all_signals if signal["direction"] == "bullish")
        bearish = sum(1 for signal in all_signals if signal["direction"] == "bearish")
        if bullish > bearish:
            recommendation = "buy"
        elif bearish > bullish:
            recommendation = "reduce"

        summary_payload = {
            "symbol": symbol,
            "company_name": company_name,
            "fundamentals": fundamentals,
            "daily_kline": daily_kline[-3:],
            "minute_kline": minute_kline[-3:],
            "agent_insights": [insight.model_dump(mode="json") for insight in insights],
            "sources": [source.model_dump(mode="json") for source in sources],
            "knowledge_graph": kg,
        }
        summary_prompt = (
            "请根据以下多智能体分析结果，输出一段中文摘要，并明确给出投资建议、核心阿尔法、风险。"
            f"{json.dumps(summary_payload, ensure_ascii=False)}"
        )
        summary = await self.llm.generate(summary_prompt, system_prompt="You are a chief investment officer.")

        return {
            "symbol": symbol,
            "company_name": company_name,
            "summary": summary,
            "recommendation": recommendation,
            "confidence": confidence,
            "alpha_signals": all_signals,
            "risks": kg["risks"] or ["需持续跟踪政策、业绩与情绪变化"],
            "opportunities": kg["opportunities"] or ["若催化兑现，可关注趋势延续"],
            "sources": sources,
            "agent_insights": insights,
            "knowledge_graph": {"nodes": kg["nodes"], "edges": kg["edges"]},
        }

