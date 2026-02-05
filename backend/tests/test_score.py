"""スコア取得ロジックのユニットテスト"""
from datetime import datetime
from types import SimpleNamespace

from app.services.score_service import get_stock_score


class FakeResult:
    def __init__(self, row):
        self._row = row

    def fetchone(self):
        return self._row


class FakeSession:
    def __init__(self, row):
        self._row = row

    def execute(self, *_args, **_kwargs):
        return FakeResult(self._row)


class TestGetStockScore:
    def test_normal_score(self):
        """正常系: スコアが取得できる"""
        row = SimpleNamespace(
            stock_code="7203",
            stock_name="トヨタ自動車",
            total_score=72.63,
            rank="B+",
            value_score=100.0,
            growth_score=50.0,
            momentum_score=70.51,
            score_date="2026-02-03",
            details={"per": 1.15},
            created_at=datetime(2026, 2, 3, 7, 32, 16),
        )
        db = FakeSession(row)

        data = get_stock_score("7203", db)

        assert data["stock_code"] == "7203"
        assert data["stock_name"] == "トヨタ自動車"
        assert data["total_score"] == 72.63
        assert data["rank"] == "B+"
        assert data["market_comparison"]["total_diff"] == 22.63

    def test_details_json_string(self):
        """detailsがJSON文字列でも辞書に変換される"""
        row = SimpleNamespace(
            stock_code="7203",
            stock_name="トヨタ自動車",
            total_score=50.0,
            rank="B",
            value_score=50.0,
            growth_score=50.0,
            momentum_score=50.0,
            score_date="2026-02-03",
            details='{"per": 10.0}',
            created_at=datetime(2026, 2, 3, 7, 32, 16),
        )
        db = FakeSession(row)

        data = get_stock_score("7203", db)

        assert data["details"]["per"] == 10.0

    def test_missing_row_returns_none(self):
        """データが存在しない場合はNone"""
        db = FakeSession(None)
        assert get_stock_score("7203", db) is None