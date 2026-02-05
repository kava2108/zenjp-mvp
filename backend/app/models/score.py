"""
日次スコアモデル
"""
from sqlalchemy import Column, Integer, String, Date, Numeric, TIMESTAMP, ForeignKey, UniqueConstraint, Index, CheckConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base


class DailyScore(Base):
    """
    日次スコアテーブル
    """
    __tablename__ = "daily_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(4), ForeignKey("stocks.stock_code"), nullable=False)
    score_date = Column(Date, nullable=False)
    total_score = Column(Numeric(5, 2), nullable=False)
    rank = Column(String(2), nullable=False)
    value_score = Column(Numeric(5, 2))
    growth_score = Column(Numeric(5, 2))
    momentum_score = Column(Numeric(5, 2))
    details = Column(JSONB)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)

    __table_args__ = (
        UniqueConstraint('stock_code', 'score_date', name='uq_stock_score_date'),
        CheckConstraint('total_score >= 0 AND total_score <= 100', name='chk_total_score_range'),
        Index('idx_scores_stock_date', 'stock_code', 'score_date'),
        Index('idx_scores_date', 'score_date'),
    )
