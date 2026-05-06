from __future__ import annotations

import asyncio
import json
from textwrap import shorten
from typing import Any

from rich.json import JSON
from rich.markdown import Markdown
from rich.panel import Panel
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Checkbox, Footer, Header, Input, Label, RichLog, Select, Static, TabPane, TabbedContent, TextArea

from app.tui.client import BackendClient


def format_sources(sources: list[dict[str, Any]]) -> str:
    if not sources:
        return "暂无来源"
    lines = []
    for index, source in enumerate(sources, start=1):
        lines.append(
            f"{index}. [{source.get('source_type', 'unknown')}] {source.get('title', '')}\n"
            f"   {source.get('url', '')}\n"
            f"   {source.get('snippet', '')}"
        )
    return "\n\n".join(lines)


def format_signals(signals: list[dict[str, Any]]) -> str:
    if not signals:
        return "暂无信号"
    return "\n".join(
        f"- {item.get('name', '')} | {item.get('direction', '')} | {item.get('score', 0):.2f} | {item.get('reason', '')}"
        for item in signals
    )


def format_memory(payload: dict[str, Any]) -> str:
    lines = ["短期记忆:"]
    short_term = payload.get("short_term", [])
    long_term = payload.get("long_term", [])
    if short_term:
        lines.extend(f"- {item.get('content', '')}" for item in short_term)
    else:
        lines.append("- 暂无")
    lines.extend(["", "长期记忆:"])
    if long_term:
        lines.extend(
            f"- {item.get('content', '')} (score={item.get('score', 0)})"
            for item in long_term
        )
    else:
        lines.append("- 暂无")
    return "\n".join(lines)


class AStockTUI(App[None]):
    CSS_PATH = "styles.tcss"
    TITLE = "A-Share Alpha Terminal"
    SUB_TITLE = "Claude Code style research console"
    BINDINGS = [
        ("q", "quit", "退出"),
        ("ctrl+r", "refresh_meta", "刷新"),
        ("ctrl+a", "run_analysis", "分析"),
        ("ctrl+s", "run_search", "检索"),
        ("ctrl+m", "run_market", "行情"),
        ("ctrl+k", "recall_memory", "回忆"),
    ]

    def __init__(self, backend_client: BackendClient, session_id: str = "terminal-default"):
        super().__init__()
        self.backend = backend_client
        self.session_id = session_id
        self.bootstrap_data: dict[str, Any] = {}
        self.provider_data: dict[str, Any] = {}

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Container(id="root"):
            with Vertical(id="sidebar"):
                yield Static("A-Share Alpha", classes="panel-title")
                yield Label("证券代码", classes="block-label")
                yield Input(value="000001", id="symbol-input", placeholder="例如 000001")
                yield Label("公司名称", classes="block-label")
                yield Input(value="平安银行", id="company-input", placeholder="可选")
                yield Label("分析任务", classes="block-label")
                yield TextArea(
                    "请分析该标的的投资价值、催化剂、风险与交易信号",
                    id="query-input",
                )
                yield Label("LLM Provider", classes="block-label")
                yield Select([("mock", "mock")], id="llm-select", allow_blank=False)
                yield Label("Search Provider", classes="block-label")
                yield Select([("mock", "mock")], id="search-select", allow_blank=False)
                yield Label("交易周期", classes="block-label")
                yield Select([("swing", "swing")], id="timeframe-select", allow_blank=False)
                yield Label("风险偏好", classes="block-label")
                yield Select([("balanced", "balanced")], id="risk-select", allow_blank=False)
                yield Checkbox("包含分时数据", value=True, id="minutes-checkbox")
                with Horizontal(classes="action-row"):
                    yield Button("分析", id="analyze-button", variant="primary")
                    yield Button("检索", id="search-button")
                with Horizontal(classes="action-row"):
                    yield Button("行情", id="market-button")
                    yield Button("记忆", id="remember-button")
                yield Button("回忆", id="recall-button")
            with Vertical(id="stream-panel"):
                yield Static("Execution Stream", classes="panel-title")
                yield RichLog(id="event-log", wrap=True, markup=True, highlight=True)
            with Vertical(id="detail-panel"):
                yield Static("Inspector", classes="panel-title")
                with TabbedContent(id="detail-tabs"):
                    with TabPane("摘要", id="summary-tab"):
                        yield Static("等待分析结果", id="summary-view", classes="detail-view")
                    with TabPane("信号", id="signals-tab"):
                        yield Static("等待信号结果", id="signals-view", classes="detail-view")
                    with TabPane("来源", id="sources-tab"):
                        yield Static("等待检索结果", id="sources-view", classes="detail-view")
                    with TabPane("行情", id="market-tab"):
                        yield Static("等待行情结果", id="market-view", classes="detail-view")
                    with TabPane("记忆", id="memory-tab"):
                        yield Static("等待记忆结果", id="memory-view", classes="detail-view")
                    with TabPane("图谱", id="graph-tab"):
                        yield Static("等待知识图谱", id="graph-view", classes="detail-view")
            with Vertical(id="status-panel"):
                yield Static("Status", classes="panel-title")
                yield Static("初始化中", id="status-line")
        yield Footer()

    async def on_mount(self) -> None:
        await self.refresh_meta()

    def _set_status(self, text: str) -> None:
        self.query_one("#status-line", Static).update(text)

    def _log(self, title: str, content: str, color: str) -> None:
        self.query_one("#event-log", RichLog).write(
            Panel(content, title=title, border_style=color)
        )

    def _set_detail(self, selector: str, renderable: Any) -> None:
        self.query_one(selector, Static).update(renderable)

    def _activate_tab(self, tab_id: str) -> None:
        self.query_one("#detail-tabs", TabbedContent).active = tab_id

    def _collect_analysis_payload(self) -> dict[str, Any]:
        return {
            "symbol": self.query_one("#symbol-input", Input).value.strip(),
            "company_name": self.query_one("#company-input", Input).value.strip() or None,
            "query": self.query_one("#query-input", TextArea).text.strip(),
            "llm_provider": self.query_one("#llm-select", Select).value,
            "search_provider": self.query_one("#search-select", Select).value,
            "timeframe": self.query_one("#timeframe-select", Select).value,
            "risk_profile": self.query_one("#risk-select", Select).value,
            "include_minutes": self.query_one("#minutes-checkbox", Checkbox).value,
        }

    def _populate_selects(self) -> None:
        llm_select = self.query_one("#llm-select", Select)
        search_select = self.query_one("#search-select", Select)
        timeframe_select = self.query_one("#timeframe-select", Select)
        risk_select = self.query_one("#risk-select", Select)

        llm_select.set_options(
            [(item, item) for item in self.provider_data["llm"]["available"]]
        )
        search_select.set_options(
            [(item, item) for item in self.provider_data["search"]["available"]]
        )
        timeframe_select.set_options(
            [(item, item) for item in self.bootstrap_data["supported_timeframes"]]
        )
        risk_select.set_options(
            [(item, item) for item in self.bootstrap_data["risk_profiles"]]
        )
        llm_select.value = self.bootstrap_data["default_llm_provider"]
        search_select.value = self.bootstrap_data["default_search_provider"]
        timeframe_select.value = self.bootstrap_data["supported_timeframes"][1]
        risk_select.value = self.bootstrap_data["risk_profiles"][1]

    async def refresh_meta(self) -> None:
        try:
            health, providers, bootstrap = await asyncio.gather(
                self.backend.health(),
                self.backend.provider_status(),
                self.backend.bootstrap(),
            )
        except Exception as exc:
            self._set_status(f"后端连接失败: {exc}")
            self._log("backend.error", str(exc), "red")
            return

        self.provider_data = providers
        self.bootstrap_data = bootstrap
        self._populate_selects()
        self._set_status(
            f"backend={health['status']} | llm={providers['llm']['default']} | "
            f"search={providers['search']['default']} | mock={providers['mock_enabled']}"
        )
        self._log(
            "bootstrap",
            json.dumps(
                {"providers": providers, "bootstrap": bootstrap},
                ensure_ascii=False,
                indent=2,
            ),
            "cyan",
        )

    async def run_analysis(self) -> None:
        payload = self._collect_analysis_payload()
        self._set_status("正在执行多智能体分析")
        self._log("analysis.request", json.dumps(payload, ensure_ascii=False, indent=2), "yellow")
        result = await self.backend.analyze(payload)
        self._log(
            "analysis.response",
            shorten(result["summary"], width=400, placeholder="..."),
            "green",
        )
        self._set_detail("#summary-view", Markdown(result["summary"]))
        self._set_detail("#signals-view", Markdown(format_signals(result["alpha_signals"])))
        self._set_detail("#sources-view", Markdown(format_sources(result["sources"])))
        self._set_detail("#graph-view", JSON.from_data(result["knowledge_graph"]))
        self._activate_tab("summary-tab")
        self._set_status(
            f"建议={result['recommendation']} | 置信度={result['confidence']:.2f}"
        )

    async def run_search(self) -> None:
        symbol = self.query_one("#symbol-input", Input).value.strip()
        company = self.query_one("#company-input", Input).value.strip()
        payload = {
            "query": f"{company or symbol} A股 政策 公告 新闻",
            "max_results": 8,
            "provider": self.query_one("#search-select", Select).value,
        }
        self._log("search.request", json.dumps(payload, ensure_ascii=False, indent=2), "blue")
        result = await self.backend.search(payload)
        self._set_detail("#sources-view", Markdown(format_sources(result["items"])))
        self._activate_tab("sources-tab")
        self._set_status(f"{result['provider']} 返回 {len(result['items'])} 条来源")

    async def run_market(self) -> None:
        symbol = self.query_one("#symbol-input", Input).value.strip()
        period = "5min" if self.query_one("#minutes-checkbox", Checkbox).value else "daily"
        kline, fundamentals = await asyncio.gather(
            self.backend.kline(symbol, period),
            self.backend.fundamentals(symbol),
        )
        payload = {"kline": kline["items"][-5:], "fundamentals": fundamentals["metrics"]}
        self._set_detail("#market-view", JSON.from_data(payload))
        self._activate_tab("market-tab")
        self._set_status(f"{symbol} 行情已刷新 | period={period}")

    async def remember(self) -> None:
        payload = {
            "session_id": self.session_id,
            "namespace": "tui",
            "content": self.query_one("#query-input", TextArea).text.strip(),
            "importance": 0.75,
        }
        await self.backend.remember(payload)
        self._set_detail("#memory-view", Markdown("已写入短期与长期记忆。"))
        self._activate_tab("memory-tab")
        self._set_status("记忆写入完成")

    async def recall_memory(self) -> None:
        payload = {
            "session_id": self.session_id,
            "namespace": "tui",
            "query": self.query_one("#query-input", TextArea).text.strip(),
            "limit": 5,
        }
        result = await self.backend.recall(payload)
        self._log("memory.recall", json.dumps(result, ensure_ascii=False, indent=2), "magenta")
        self._set_detail("#memory-view", Markdown(format_memory(result)))
        self._activate_tab("memory-tab")
        self._set_status("记忆回忆完成")

    async def action_refresh_meta(self) -> None:
        await self.refresh_meta()

    async def action_run_analysis(self) -> None:
        await self.run_analysis()

    async def action_run_search(self) -> None:
        await self.run_search()

    async def action_run_market(self) -> None:
        await self.run_market()

    async def action_recall_memory(self) -> None:
        await self.recall_memory()

    @on(Button.Pressed, "#analyze-button")
    async def on_analyze_pressed(self) -> None:
        await self.run_analysis()

    @on(Button.Pressed, "#search-button")
    async def on_search_pressed(self) -> None:
        await self.run_search()

    @on(Button.Pressed, "#market-button")
    async def on_market_pressed(self) -> None:
        await self.run_market()

    @on(Button.Pressed, "#remember-button")
    async def on_remember_pressed(self) -> None:
        await self.remember()

    @on(Button.Pressed, "#recall-button")
    async def on_recall_pressed(self) -> None:
        await self.recall_memory()
