"""
スコア分析ツール
ZenJP MVP - PHASE3 Day 7

計算されたスコアを分析・表示するツール
"""

import sys
import os
from sqlalchemy import create_engine, text
import pandas as pd

# app モジュールへのパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.config import settings


def get_db_engine():
    """データベース接続エンジンを取得"""
    database_url = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    return create_engine(database_url)


def get_stock_names():
    """銘柄名を取得"""
    return {
        '7203': 'トヨタ自動車',
        '9984': 'ソフトバンクグループ',
        '6758': 'ソニーグループ'
    }


def analyze_scores():
    """スコアを分析して表示"""
    engine = get_db_engine()
    stock_names = get_stock_names()
    
    # スコアデータ取得
    query = text("""
        SELECT 
            stock_code, 
            score_date,
            total_score, 
            rank,
            value_score, 
            growth_score, 
            momentum_score,
            details
        FROM daily_scores
        ORDER BY total_score DESC
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query)
        rows = result.fetchall()
    
    if not rows:
        print("❌ スコアデータが見つかりません")
        return
    
    print("=" * 80)
    print("スコア分析レポート")
    print("=" * 80)
    print()
    
    # 総合スコアランキング
    print("■ 総合スコアランキング")
    print("-" * 80)
    print(f"{'順位':<4} | {'銘柄コード':<8} | {'銘柄名':<20} | {'総合スコア':<10} | {'ランク':<6}")
    print("-" * 80)
    
    for i, row in enumerate(rows, 1):
        stock_code = row[0]
        total_score = float(row[2])
        rank = row[3]
        stock_name = stock_names.get(stock_code, '不明')
        
        print(f"{i:<4} | {stock_code:<8} | {stock_name:<20} | {total_score:<10.2f} | {rank:<6}")
    
    print()
    
    # カテゴリ別スコア
    print("■ カテゴリ別スコア")
    print("-" * 80)
    print(f"{'銘柄':<10} | {'Value':<8} | {'Growth':<8} | {'Momentum':<10}")
    print("-" * 80)
    
    for row in rows:
        stock_code = row[0]
        value_score = float(row[4])
        growth_score = float(row[5])
        momentum_score = float(row[6])
        
        print(f"{stock_code:<10} | {value_score:<8.2f} | {growth_score:<8.2f} | {momentum_score:<10.2f}")
    
    print()
    
    # 詳細指標
    print("■ 詳細指標")
    print("-" * 80)
    
    for row in rows:
        stock_code = row[0]
        stock_name = stock_names.get(stock_code, '不明')
        details = row[7] if row[7] else {}
        
        print(f"\n【{stock_code}: {stock_name}】")
        
        if details:
            per = details.get('per', 0)
            pbr = details.get('pbr', 0)
            dividend_yield = details.get('dividend_yield', 0)
            per_score = details.get('per_score', 0)
            pbr_score = details.get('pbr_score', 0)
            dividend_score = details.get('dividend_score', 0)
            rsi = details.get('rsi', 0)
            rsi_score = details.get('rsi_score', 0)
            volume_change = details.get('volume_change_rate', 0)
            volume_score = details.get('volume_score', 0)
            
            print(f"  PER          : {per:.2f}倍 → スコア: {per_score:.1f}点")
            print(f"  PBR          : {pbr:.2f}倍 → スコア: {pbr_score:.1f}点")
            print(f"  配当利回り   : {dividend_yield:.2f}% → スコア: {dividend_score:.1f}点")
            print(f"  RSI          : {rsi:.2f} → スコア: {rsi_score:.1f}点")
            print(f"  出来高変化率 : {volume_change:+.2f}% → スコア: {volume_score:.1f}点")
        else:
            print("  詳細情報なし")
    
    print()
    print("=" * 80)


if __name__ == '__main__':
    analyze_scores()
