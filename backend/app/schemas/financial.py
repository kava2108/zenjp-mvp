"""
財務データスキーマ
"""
from pydantic import BaseModel, Field
from datetime import datetime, date
from decimal import Decimal
from typing import Optional


class StockFinancialBase(BaseModel):
    """財務データ基本スキーマ"""
    stock_code: str = Field(..., max_length=4, description="銘柄コード")
    fiscal_period: date = Field(..., description="会計期間")
    revenue: Optional[int] = Field(None, description="売上高")
    eps: Optional[Decimal] = Field(None, description="EPS（1株当たり利益）")
    bps: Optional[Decimal] = Field(None, description="BPS（1株当たり純資産）")
    dividend: Optional[Decimal] = Field(None, description="配当金")


class StockFinancialCreate(StockFinancialBase):
    """財務データ作成スキーマ"""
    pass


class StockFinancialResponse(StockFinancialBase):
    """財務データレスポンススキーマ"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
