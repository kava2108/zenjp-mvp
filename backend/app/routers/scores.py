from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.score import ScoreResponse
from app.services.score_service import get_stock_score


router = APIRouter(
    prefix="/api",
    tags=["scores"]
)


@router.get("/score/{stock_code}", response_model=ScoreResponse)
def get_score(stock_code: str, db: Session = Depends(get_db)):
    """
    指定された銘柄のスコアを取得
    
    Args:
        stock_code: 銘柄コード（7203, 6758, 9984）
    
    Returns:
        ScoreResponse: スコアデータ
    
    Raises:
        HTTPException 404: 銘柄が見つからない
        HTTPException 400: 無効な銘柄コード
    """
    
    # 銘柄コードのバリデーション（4桁の数字）
    if not stock_code.isdigit() or len(stock_code) != 4:
        raise HTTPException(
            status_code=400,
            detail=f"無効な銘柄コードです: {stock_code}"
        )
    
    # スコア取得
    score_data = get_stock_score(stock_code, db)
    
    if not score_data:
        raise HTTPException(
            status_code=404,
            detail=f"銘柄コード {stock_code} のスコアが見つかりません"
        )
    
    return score_data
