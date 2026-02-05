"""
株式銘柄モデル
"""
from sqlalchemy import Column, String, TIMESTAMP, func
from app.database import Base


class Stock(Base):
    """
    銘柄マスタテーブル
    """
    __tablename__ = "stocks"

    stock_code = Column(String(4), primary_key=True, index=True)
    stock_name = Column(String(100), nullable=False)
    sector_name = Column(String(50))
    market = Column(String(20))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), 
                       onupdate=func.current_timestamp(), nullable=False)
