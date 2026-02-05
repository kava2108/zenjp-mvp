"""エッジケーステスト"""
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


def test_missing_details_defaults_to_empty_dict():
    """detailsがNoneでも空辞書になる"""
    row = SimpleNamespace(
        stock_code="7203",
        stock_name="トヨタ自動車",
        total_score=50.0,
        rank="B",
        value_score=50.0,
        growth_score=50.0,
        momentum_score=50.0,
        score_date="2026-02-03",
        details=None,
        created_at=datetime(2026, 2, 3, 7, 32, 16),
    )
    db = FakeSession(row)

    data = get_stock_score("7203", db)

    assert data["details"] == {}


def test_null_category_scores_default_to_zero():
    """カテゴリスコアがNULLでも0に補正される"""
    row = SimpleNamespace(
        stock_code="7203",
        stock_name="トヨタ自動車",
        total_score=10.0,
        rank="D",
        value_score=None,
        growth_score=None,
        momentum_score=None,
        score_date="2026-02-03",
        details={},
        created_at=datetime(2026, 2, 3, 7, 32, 16),
    )
    db = FakeSession(row)

    data = get_stock_score("7203", db)

    assert data["value_score"] == 0
    assert data["growth_score"] == 0
    assert data["momentum_score"] == 0