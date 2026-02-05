from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import json


MARKET_AVERAGE = {
    "total": 50.0,
    "value": 50.0,
    "growth": 50.0,
    "momentum": 50.0
}


def get_stock_score(stock_code: str, db: Session) -> dict | None:
    """
    指定された銘柄のスコアを取得
    
    Args:
        stock_code: 銘柄コード（例: '7203'）
        db: SQLAlchemyのSession
    
    Returns:
        スコアデータの辞書、存在しない場合はNone
    """
    
    query = text("""
        SELECT 
            s.stock_code,
            s.stock_name,
            ds.total_score,
            ds.rank,
            ds.value_score,
            ds.growth_score,
            ds.momentum_score,
            ds.score_date,
            ds.details,
            ds.created_at
        FROM daily_scores ds
        JOIN stocks s ON ds.stock_code = s.stock_code
        WHERE ds.stock_code = :stock_code
        ORDER BY ds.score_date DESC
        LIMIT 1
    """)
    
    result = db.execute(query, {"stock_code": stock_code}).fetchone()
    
    if not result:
        return None
    
    # details を辞書に変換（JSON文字列の場合）
    details_data = result.details
    if isinstance(details_data, str):
        details_data = json.loads(details_data)
    elif details_data is None:
        details_data = {}
    
    # 市場平均との比較を計算
    market_comparison = {
        'total_diff': round(float(result.total_score) - MARKET_AVERAGE['total'], 2),
        'value_diff': round(float(result.value_score or 0) - MARKET_AVERAGE['value'], 2),
        'growth_diff': round(float(result.growth_score or 0) - MARKET_AVERAGE['growth'], 2),
        'momentum_diff': round(float(result.momentum_score or 0) - MARKET_AVERAGE['momentum'], 2)
    }
    
    return {
        'stock_code': result.stock_code,
        'stock_name': result.stock_name,
        'total_score': float(result.total_score),
        'rank': result.rank,
        'value_score': float(result.value_score or 0),
        'growth_score': float(result.growth_score or 0),
        'momentum_score': float(result.momentum_score or 0),
        'score_date': result.score_date,
        'details': details_data,
        'market_comparison': market_comparison,
        'updated_at': result.created_at.isoformat()
    }
