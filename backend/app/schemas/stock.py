"""
株式銘柄スキーマ
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class StockBase(BaseModel):
    """株式銘柄基本スキーマ"""
    stock_code: str = Field(..., max_length=4, description="銘柄コード（4桁）")
    stock_name: str = Field(..., max_length=100, description="銘柄名")
    sector_name: Optional[str] = Field(None, max_length=50, description="業種名")
    market: Optional[str] = Field(None, max_length=20, description="市場区分")


class StockCreate(StockBase):
    """株式銘柄作成スキーマ"""
    pass


class StockResponse(StockBase):
    """株式銘柄レスポンススキーマ"""
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
