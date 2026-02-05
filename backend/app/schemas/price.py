"""
株価データスキーマ
"""
from pydantic import BaseModel, Field
from datetime import datetime, date
from decimal import Decimal
from typing import Optional


class StockPriceBase(BaseModel):
    """株価データ基本スキーマ"""
    stock_code: str = Field(..., max_length=4, description="銘柄コード")
    price_date: date = Field(..., description="株価日付")
    open_price: Optional[Decimal] = Field(None, description="始値")
    high_price: Optional[Decimal] = Field(None, description="高値")
    low_price: Optional[Decimal] = Field(None, description="安値")
    close_price: Decimal = Field(..., description="終値")
    volume: Optional[int] = Field(None, description="出来高")


class StockPriceCreate(StockPriceBase):
    """株価データ作成スキーマ"""
    pass


class StockPriceResponse(StockPriceBase):
    """株価データレスポンススキーマ"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
