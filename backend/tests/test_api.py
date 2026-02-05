"""API統合テスト"""
from datetime import datetime

import httpx
import pytest
from app.main import app
from app.database import get_db


def fake_get_db():
    yield None


@pytest.mark.asyncio
async def test_get_score_success(monkeypatch):
    """正常系: スコア取得成功"""
    def fake_get_stock_score(stock_code, _db):
        return {
            "stock_code": stock_code,
            "stock_name": "トヨタ自動車",
            "total_score": 72.63,
            "rank": "B+",
            "value_score": 100.0,
            "growth_score": 50.0,
            "momentum_score": 70.51,
            "score_date": "2026-02-03",
            "details": {},
            "market_comparison": {
                "total_diff": 22.63,
                "value_diff": 50.0,
                "growth_diff": 0.0,
                "momentum_diff": 20.51,
            },
            "updated_at": datetime(2026, 2, 3, 7, 32, 16).isoformat(),
        }

    monkeypatch.setattr("app.routers.scores.get_stock_score", fake_get_stock_score)
    app.dependency_overrides.clear()
    app.dependency_overrides[get_db] = fake_get_db
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/score/7203")

    assert response.status_code == 200
    data = response.json()
    assert data["stock_code"] == "7203"
    assert 0 <= data["total_score"] <= 100


@pytest.mark.asyncio
async def test_get_score_not_found(monkeypatch):
    """異常系: 存在しない銘柄コード"""
    monkeypatch.setattr("app.routers.scores.get_stock_score", lambda *_: None)
    app.dependency_overrides.clear()
    app.dependency_overrides[get_db] = fake_get_db
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/score/9999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_score_invalid_code():
    """異常系: 無効な銘柄コード"""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/score/abcd")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_root_endpoint():
    """ルートエンドポイントが応答する"""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "ZenJP MVP API"


@pytest.mark.asyncio
async def test_health_endpoint():
    """ヘルスチェックが応答する"""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"