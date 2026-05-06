from __future__ import annotations

import networkx as nx

from app.schemas.common import SourceItem


class KnowledgeGraphService:
    def build(
        self,
        symbol: str,
        company_name: str | None,
        sources: list[SourceItem],
        fundamentals: dict,
    ) -> dict:
        graph = nx.DiGraph()
        company = company_name or symbol
        graph.add_node(symbol, label=company, category="stock")

        for metric, value in fundamentals.items():
            if metric == "symbol":
                continue
            graph.add_node(metric, label=metric, category="fundamental")
            graph.add_edge(symbol, metric, relation="has_metric", value=value)

        for idx, source in enumerate(sources[:8]):
            node_id = f"source_{idx}"
            graph.add_node(node_id, label=source.title, category=source.source_type)
            graph.add_edge(node_id, symbol, relation="impacts", weight=source.score)

        opportunities = []
        risks = []
        growth = float(fundamentals.get("revenue_growth", 0) or 0)
        debt = float(fundamentals.get("debt_to_asset", 0) or 0)
        if growth > 0.2:
            opportunities.append("营收增速较高，具备景气延续可能")
        if debt > 0.55:
            risks.append("资产负债率偏高，需关注融资与偿债压力")

        return {
            "nodes": [{"id": node, **attrs} for node, attrs in graph.nodes(data=True)],
            "edges": [{"source": a, "target": b, **attrs} for a, b, attrs in graph.edges(data=True)],
            "opportunities": opportunities,
            "risks": risks,
        }

