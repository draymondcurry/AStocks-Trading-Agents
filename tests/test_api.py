def test_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_provider_status(client):
    response = client.get("/api/v1/providers/status")
    assert response.status_code == 200
    data = response.json()
    assert "mock" in data["llm"]["available"]
    assert "mock" in data["search"]["available"]
    assert data["llm"]["default"] == "mock"


def test_frontend_bootstrap(client):
    response = client.get("/api/v1/frontend/bootstrap")
    assert response.status_code == 200
    data = response.json()
    assert data["market_periods"]


def test_search_query(client):
    response = client.post(
        "/api/v1/search/query",
        json={"query": "新能源", "max_results": 5},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "mock"
    assert all(item["url"] for item in data["items"])


def test_market_endpoints(client):
    kline = client.get(
        "/api/v1/market/kline",
        params={"symbol": "000001", "period": "daily"},
    )
    assert kline.status_code == 200
    assert len(kline.json()["items"]) >= 1

    fundamentals = client.get(
        "/api/v1/market/fundamentals",
        params={"symbol": "000001"},
    )
    assert fundamentals.status_code == 200
    assert fundamentals.json()["metrics"]["symbol"] == "000001"


def test_memory_flow(client):
    stored = client.post(
        "/api/v1/memory/remember",
        json={"session_id": "s1", "content": "关注机器人板块政策催化", "importance": 0.9},
    )
    assert stored.status_code == 200

    recalled = client.post(
        "/api/v1/memory/recall",
        json={"session_id": "s1", "query": "机器人政策", "limit": 3},
    )
    assert recalled.status_code == 200
    data = recalled.json()
    assert data["short_term"]
    assert data["long_term"]


def test_stock_pick(client):
    response = client.post(
        "/api/v1/analysis/stock-pick",
        json={"symbol": "000001", "company_name": "平安银行"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "000001"
    assert data["agent_insights"]
    assert data["knowledge_graph"]["nodes"]
    assert data["sources"]

