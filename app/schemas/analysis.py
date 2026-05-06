from pydantic import BaseModel, Field

from app.schemas.common import AgentInsight, SourceItem


class StockPickRequest(BaseModel):
    symbol: str
    company_name: str | None = None
    query: str = "请分析该标的的投资价值、催化剂、风险与交易信号"
    llm_provider: str | None = None
    search_provider: str | None = None
    timeframe: str = "swing"
    risk_profile: str = "balanced"
    include_minutes: bool = True


class KnowledgeGraphPayload(BaseModel):
    nodes: list[dict] = Field(default_factory=list)
    edges: list[dict] = Field(default_factory=list)


class StockPickResponse(BaseModel):
    symbol: str
    company_name: str | None = None
    summary: str
    recommendation: str
    confidence: float
    alpha_signals: list[dict]
    risks: list[str]
    opportunities: list[str]
    sources: list[SourceItem]
    agent_insights: list[AgentInsight]
    knowledge_graph: KnowledgeGraphPayload

