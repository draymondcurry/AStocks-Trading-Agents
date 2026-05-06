import httpx
import pytest
from httpx import ASGITransport

from app.main import create_app
from app.tui.app import AStockTUI, format_memory, format_signals, format_sources
from app.tui.client import BackendClient


@pytest.mark.asyncio
async def test_backend_client_against_local_app():
    app = create_app()
    transport = ASGITransport(app=app)
    client = BackendClient("http://testserver", transport=transport)

    health = await client.health()
    providers = await client.provider_status()
    bootstrap = await client.bootstrap()
    analysis = await client.analyze({"symbol": "000001", "company_name": "平安银行"})

    assert health["status"] == "ok"
    assert "llm" in providers
    assert bootstrap["risk_profiles"]
    assert analysis["symbol"] == "000001"


def test_format_helpers():
    assert "暂无来源" not in format_sources(
        [{"title": "t", "url": "https://a.com", "snippet": "s", "source_type": "news"}]
    )
    assert "bullish" in format_signals(
        [{"name": "policy", "direction": "bullish", "score": 0.9, "reason": "催化"}]
    )
    assert "短期记忆" in format_memory({"short_term": [], "long_term": []})


@pytest.mark.asyncio
async def test_tui_smoke():
    app = create_app()
    transport = ASGITransport(app=app)
    backend = BackendClient("http://testserver", transport=transport)
    tui = AStockTUI(backend)

    async with tui.run_test(size=(140, 40)) as pilot:
        await pilot.pause()
        assert tui.query_one("#status-line").renderable
        await tui.run_search()
        await pilot.pause()
        await tui.run_market()
        await pilot.pause()
        assert "A-Share Alpha Terminal" in tui.title
