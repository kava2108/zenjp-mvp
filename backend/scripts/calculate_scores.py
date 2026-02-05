"""
スコア計算メインスクリプト
ZenJP MVP - PHASE3

このスクリプトは以下を実行します:
1. DBから株価・財務データを取得
2. 3銘柄のスコアを計算
3. daily_scoresテーブルに保存
"""

import sys
import os
from datetime import datetime, date
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pandas as pd

# app モジュールへのパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.config import settings
from scripts.score_calculator import calculate_stock_score


def get_db_engine():
    """データベース接続エンジンを取得"""
    database_url = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    return create_engine(database_url)


def get_latest_prices(engine, stock_code: str, limit: int = 45) -> pd.DataFrame:
    """
    最新の株価データを取得
    
    Args:
        engine: SQLAlchemy engine
        stock_code: 銘柄コード
        limit: 取得件数
    
    Returns:
        DataFrame (price_date降順)
    """
    query = text("""
        SELECT price_date as date, close_price as close, volume
        FROM stock_prices
        WHERE stock_code = :stock_code
        ORDER BY price_date DESC
        LIMIT :limit
    """)
    
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={'stock_code': stock_code, 'limit': limit})
    
    return df


def get_stock_financial(engine, stock_code: str) -> dict:
    """
    財務データを取得（最新と1年前）
    
    Args:
        engine: SQLAlchemy engine
        stock_code: 銘柄コード
    
    Returns:
        財務データ辞書（最新のEPS/BPS/配当と、計算された成長率を含む）
    """
    # 最新の財務データを取得
    query_latest = text("""
        SELECT eps, bps, dividend, revenue, fiscal_period
        FROM stock_financials
        WHERE stock_code = :stock_code
        ORDER BY fiscal_period DESC
        LIMIT 1
    """)
    
    with engine.connect() as conn:
        result_latest = conn.execute(query_latest, {'stock_code': stock_code}).fetchone()
    
    if not result_latest:
        return None
    
    latest_eps, latest_bps, latest_dividend, latest_revenue, latest_period = result_latest
    
    # 1年前のデータを取得（成長率計算用）
    query_prev = text("""
        SELECT revenue, fiscal_period
        FROM stock_financials
        WHERE stock_code = :stock_code AND fiscal_period < :latest_period
        ORDER BY fiscal_period DESC
        LIMIT 1
    """)
    
    with engine.connect() as conn:
        result_prev = conn.execute(query_prev, {
            'stock_code': stock_code,
            'latest_period': latest_period
        }).fetchone()
    
    # 成長率を計算
    growth_rate = None
    if result_prev and result_prev[0] and latest_revenue:
        prev_revenue = result_prev[0]
        # 成長率 = (今年の売上 - 去年の売上) / 去年の売上 × 100
        growth_rate = ((latest_revenue - prev_revenue) / prev_revenue) * 100.0
    
    return {
        'eps': float(latest_eps) if latest_eps else 0.0,
        'bps': float(latest_bps) if latest_bps else 0.0,
        'dividend': float(latest_dividend) if latest_dividend else 0.0,
        'revenue': float(latest_revenue) if latest_revenue else 0.0,
        'growth_rate': growth_rate  # 計算された成長率（%）またはNone
    }


def get_stock_sector(engine, stock_code: str) -> str:
    """
    銘柄の業種を取得
    
    Args:
        engine: SQLAlchemy engine
        stock_code: 銘柄コード
    
    Returns:
        業種名（または None）
    """
    query = text("""
        SELECT sector_name
        FROM stocks
        WHERE stock_code = :stock_code
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query, {'stock_code': stock_code}).fetchone()
    
    return result[0] if result and result[0] else None


def get_current_price(engine, stock_code: str) -> float:
    """
    最新の株価を取得
    
    Args:
        engine: SQLAlchemy engine
        stock_code: 銘柄コード
    
    Returns:
        最新株価
    """
    query = text("""
        SELECT close_price
        FROM stock_prices
        WHERE stock_code = :stock_code
        ORDER BY price_date DESC
        LIMIT 1
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query, {'stock_code': stock_code}).fetchone()
    
    return float(result[0]) if result else 0.0


def save_daily_score(engine, score_data: dict, calculation_date: date):
    """
    daily_scoresテーブルにスコアを保存
    
    Args:
        engine: SQLAlchemy engine
        score_data: スコアデータ辞書
        calculation_date: 計算日
    """
    import json
    
    # 詳細情報をJSON形式で作成
    details = {
        'per': score_data['per'],
        'pbr': score_data['pbr'],
        'dividend_yield': score_data['dividend_yield'],
        'per_score': score_data['per_score'],
        'pbr_score': score_data['pbr_score'],
        'dividend_score': score_data['dividend_score'],
        'rsi': score_data['rsi'],
        'rsi_score': score_data['rsi_score'],
        'volume_change_rate': score_data['volume_change_rate'],
        'volume_score': score_data['volume_score']
    }
    
    # 既存データを削除（同じ日付・銘柄コード）
    delete_query = text("""
        DELETE FROM daily_scores
        WHERE stock_code = :stock_code AND score_date = :date
    """)
    
    # 新しいデータを挿入
    insert_query = text("""
        INSERT INTO daily_scores (
            stock_code, score_date, total_score, rank,
            value_score, growth_score, momentum_score,
            details,
            created_at
        ) VALUES (
            :stock_code, :date, :total_score, :rank,
            :value_score, :growth_score, :momentum_score,
            CAST(:details AS jsonb),
            NOW()
        )
    """)
    
    with engine.begin() as conn:
        # 既存削除
        conn.execute(delete_query, {
            'stock_code': score_data['stock_code'],
            'date': calculation_date
        })
        
        # 新規挿入
        conn.execute(insert_query, {
            'stock_code': score_data['stock_code'],
            'date': calculation_date,
            'total_score': score_data['total_score'],
            'rank': score_data['rank'],
            'value_score': score_data['value_score'],
            'growth_score': score_data['growth_score'],
            'momentum_score': score_data['momentum_score'],
            'details': json.dumps(details)
        })


def calculate_all_scores(calculation_date: date = None):
    """
    全銘柄のスコアを計算してDBに保存
    
    Args:
        calculation_date: 計算日（Noneの場合は今日）
    """
    if calculation_date is None:
        calculation_date = date.today()
    
    print(f"=== ZenJP スコア計算開始 ===")
    print(f"計算日: {calculation_date}")
    print()
    
    # DB接続
    engine = get_db_engine()
    
    # 対象銘柄（MVP版）
    # 成長率は財務データから自動計算される
    stock_codes = ['7203', '6758', '9984']
    
    results = []
    
    for stock_code in stock_codes:
        print(f"[{stock_code}] スコア計算中...")
        
        try:
            # データ取得
            financial = get_stock_financial(engine, stock_code)
            if not financial:
                print(f"  ⚠️ 財務データが見つかりません")
                continue
            
            current_price = get_current_price(engine, stock_code)
            if current_price == 0:
                print(f"  ⚠️ 株価データが見つかりません")
                continue
            
            prices_df = get_latest_prices(engine, stock_code)
            if len(prices_df) < 30:
                print(f"  ⚠️ 株価データが不足しています（{len(prices_df)}件）")
                continue
            
            # 業種情報を取得
            sector_name = get_stock_sector(engine, stock_code)
            
            # スコア計算（成長率は財務データから自動取得、業種別の重みを適用）
            growth_rate = financial['growth_rate']  # DBから計算された成長率
            score_data = calculate_stock_score(
                stock_code=stock_code,
                current_price=current_price,
                eps=financial['eps'],
                bps=financial['bps'],
                dividend=financial['dividend'],
                prices_df=prices_df,
                growth_rate=growth_rate,  # 計算された成長率（またはNone）
                sector_name=sector_name   # 業種別の重みを適用
            )
            
            # DB保存
            save_daily_score(engine, score_data, calculation_date)
            
            results.append(score_data)
            
            # 結果表示
            print(f"  ✅ 完了")
            print(f"     総合スコア: {score_data['total_score']}点 ({score_data['rank']})")
            print(f"     Value: {score_data['value_score']}点 | Growth: {score_data['growth_score']}点 | Momentum: {score_data['momentum_score']}点")
            print(f"     PER: {score_data['per']} | PBR: {score_data['pbr']} | 配当利回り: {score_data['dividend_yield']}%")
            if growth_rate is not None:
                print(f"     売上成長率: {growth_rate:.2f}%（財務データから計算）")
            else:
                print(f"     売上成長率: データ不足により固定値を使用")
            if sector_name:
                print(f"     業種: {sector_name}（業種別の重みを適用）")
            print(f"     RSI: {score_data['rsi']} | 出来高変化: {score_data['volume_change_rate']}%")
            print()
            
        except Exception as e:
            print(f"  ❌ エラー: {str(e)}")
            import traceback
            traceback.print_exc()
            print()
            continue
    
    # サマリー表示
    print("=== スコア計算完了 ===")
    print(f"成功: {len(results)}件 / {len(stock_codes)}件")
    
    if results:
        print("\n【ランキング】")
        sorted_results = sorted(results, key=lambda x: x['total_score'], reverse=True)
        for i, result in enumerate(sorted_results, 1):
            print(f"{i}位: {result['stock_code']} - {result['total_score']}点 ({result['rank']})")
    
    return results


if __name__ == '__main__':
    # 引数で日付を指定可能（YYYY-MM-DD形式）
    if len(sys.argv) > 1:
        calc_date = datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
    else:
        calc_date = None
    
    calculate_all_scores(calc_date)
