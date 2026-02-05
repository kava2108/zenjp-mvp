"""
日次スコアスキーマ
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Dict, Any


class DailyScoreBase(BaseModel):
    """日次スコア基本スキーマ"""
    stock_code: str = Field(..., max_length=4, description="銘柄コード")
    score_date: date = Field(..., description="スコア算出日")
    total_score: Decimal = Field(..., ge=0, le=100, description="総合スコア（0-100）")
    rank: str = Field(..., max_length=2, description="ランク（S, A, B, C, D）")
    value_score: Optional[Decimal] = Field(None, description="割安性スコア")
    growth_score: Optional[Decimal] = Field(None, description="成長性スコア")
    momentum_score: Optional[Decimal] = Field(None, description="勢いスコア")
    details: Optional[Dict[str, Any]] = Field(None, description="詳細情報（JSON）")

    @field_validator('rank')
    @classmethod
    def validate_rank(cls, v: str) -> str:
        """ランクのバリデーション"""
        allowed_ranks = ['S', 'A', 'B', 'C', 'D']
        if v not in allowed_ranks:
            raise ValueError(f'ランクは {", ".join(allowed_ranks)} のいずれかである必要があります')
        return v


class DailyScoreCreate(DailyScoreBase):
    """日次スコア作成スキーマ"""
    pass


class DailyScoreResponse(DailyScoreBase):
    """日次スコアレスポンススキーマ"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ScoreDetail(BaseModel):
    """スコア詳細"""
    per: float | None = Field(None, description="PER（株価収益率）")
    per_score: float | None = Field(None, description="PERスコア")
    pbr: float | None = Field(None, description="PBR（株価純資産倍率）")
    pbr_score: float | None = Field(None, description="PBRスコア")
    dividend_yield: float | None = Field(None, description="配当利回り（%）")
    dividend_score: float | None = Field(None, description="配当スコア")
    revenue_growth_rate: float | None = Field(None, description="売上成長率（%）")
    rsi: float | None = Field(None, description="RSI（相対力指数）")
    rsi_score: float | None = Field(None, description="RSIスコア")
    volume_change_rate: float | None = Field(None, description="出来高変化率（%）")
    volume_change_score: float | None = Field(None, description="出来高変化スコア")
    volume_score: float | None = Field(None, description="出来高スコア")

    class Config:
        from_attributes = True


class MarketComparison(BaseModel):
    """市場平均との比較"""
    total_diff: float = Field(..., description="総合スコア差分")
    value_diff: float = Field(..., description="Valueスコア差分")
    growth_diff: float = Field(..., description="Growthスコア差分")
    momentum_diff: float = Field(..., description="Momentumスコア差分")


class ScoreResponse(BaseModel):
    """スコアAPIレスポンス"""
    stock_code: str = Field(..., description="銘柄コード")
    stock_name: str = Field(..., description="銘柄名")
    total_score: float = Field(..., description="総合スコア")
    rank: str = Field(..., description="ランク（A/B+/B/C+/C/D）")
    value_score: float = Field(..., description="Valueスコア")
    growth_score: float = Field(..., description="Growthスコア")
    momentum_score: float = Field(..., description="Momentumスコア")
    score_date: date = Field(..., description="スコア算出日")
    details: ScoreDetail = Field(..., description="スコア詳細")
    market_comparison: MarketComparison = Field(..., description="市場平均との比較")
    updated_at: str = Field(..., description="更新日時")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "stock_code": "7203",
                "stock_name": "トヨタ自動車",
                "total_score": 75.5,
                "rank": "B+",
                "value_score": 78.2,
                "growth_score": 65.5,
                "momentum_score": 78.3,
                "score_date": "2026-02-09",
                "details": {
                    "per": 15.53,
                    "per_score": 49.2,
                    "pbr": 2.32,
                    "pbr_score": 54.0,
                    "dividend_yield": 9.66,
                    "dividend_score": 100.0,
                    "revenue_growth_rate": 4.48,
                    "rsi": 55.3,
                    "rsi_score": 100.0,
                    "volume_change_rate": 12.5,
                    "volume_change_score": 70.6
                },
                "market_comparison": {
                    "total_diff": 25.5,
                    "value_diff": 28.2,
                    "growth_diff": 15.5,
                    "momentum_diff": 28.3
                },
                "updated_at": "2026-02-09T10:30:00"
            }
        }