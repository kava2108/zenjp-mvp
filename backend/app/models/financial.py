"""
財務データモデル
"""
from sqlalchemy import Column, Integer, String, Date, Numeric, BigInteger, TIMESTAMP, ForeignKey, UniqueConstraint, Index, func
from app.database import Base


class StockFinancial(Base):
    """
    財務データテーブル
    """
    __tablename__ = "stock_financials"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(4), ForeignKey("stocks.stock_code"), nullable=False)
    fiscal_period = Column(Date, nullable=False)
    revenue = Column(BigInteger)
    eps = Column(Numeric(10, 2))
    bps = Column(Numeric(10, 2))
    dividend = Column(Numeric(10, 2))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), 
                       onupdate=func.current_timestamp(), nullable=False)

    __table_args__ = (
        UniqueConstraint('stock_code', 'fiscal_period', name='uq_stock_fiscal_period'),
        Index('idx_financials_stock', 'stock_code', 'fiscal_period'),
    )
