"""
株価データモデル
"""
from sqlalchemy import Column, Integer, String, Date, Numeric, BigInteger, TIMESTAMP, ForeignKey, UniqueConstraint, Index, func
from app.database import Base


class StockPrice(Base):
    """
    株価データテーブル
    """
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(4), ForeignKey("stocks.stock_code"), nullable=False)
    price_date = Column(Date, nullable=False)
    open_price = Column(Numeric(10, 2))
    high_price = Column(Numeric(10, 2))
    low_price = Column(Numeric(10, 2))
    close_price = Column(Numeric(10, 2), nullable=False)
    volume = Column(BigInteger)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), 
                       onupdate=func.current_timestamp(), nullable=False)

    __table_args__ = (
        UniqueConstraint('stock_code', 'price_date', name='uq_stock_price_date'),
        Index('idx_prices_stock_date', 'stock_code', 'price_date'),
    )
