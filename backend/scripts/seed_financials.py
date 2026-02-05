#!/usr/bin/env python
"""
財務データ投入スクリプト

3銘柄の財務データ（EPS、BPS、配当、売上高）をDBに投入します。
このデータはスコア計算時に使用されます（PER、PBR計算等）。

投入データ：
- 7203（トヨタ自動車）
- 6758（ソニーグループ）
- 9984（ソフトバンクグループ）
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import sys
from datetime import datetime

# 設定
DATABASE_URL = os.getenv('DATABASE_URL')

# 財務データ（過去3年分）
# fiscal_period: 会計年度末
# 注: EPS/BPS/配当は「円」単位、売上は「百万円」単位で記載
# 成長率を計算するため、複数年のデータを用意
FINANCIAL_DATA = {
    '7203': {
        'stock_name': 'トヨタ自動車',
        'years': [
            {
                'fiscal_period': '2023-12-31',
                'eps': 280.50,            # 1株当たり利益（円）
                'bps': 1215.30,           # 1株当たり純資産（円）
                'dividend': 28.0,         # 配当金（円）
                'revenue': 37150000.0     # 売上高（百万円）
            },
            {
                'fiscal_period': '2022-12-31',
                'eps': 265.80,
                'bps': 1180.50,
                'dividend': 26.0,
                'revenue': 35400000.0     # 成長率: 4.9%
            },
            {
                'fiscal_period': '2021-12-31',
                'eps': 248.20,
                'bps': 1145.00,
                'dividend': 24.0,
                'revenue': 33800000.0     # 成長率: 4.7%
            }
        ]
    },
    '6758': {
        'stock_name': 'ソニーグループ',
        'years': [
            {
                'fiscal_period': '2023-12-31',
                'eps': 121.08,            # 1株当たり利益（円）
                'bps': 605.02,            # 1株当たり純資産（円）
                'dividend': 16.0,         # 配当金（円）
                'revenue': 27080000.0     # 売上高（百万円）
            },
            {
                'fiscal_period': '2022-12-31',
                'eps': 105.30,
                'bps': 580.10,
                'dividend': 14.0,
                'revenue': 24200000.0     # 成長率: 11.9%
            },
            {
                'fiscal_period': '2021-12-31',
                'eps': 92.50,
                'bps': 545.80,
                'dividend': 12.0,
                'revenue': 21650000.0     # 成長率: 11.8%
            }
        ]
    },
    '9984': {
        'stock_name': 'ソフトバンクグループ',
        'years': [
            {
                'fiscal_period': '2023-12-31',
                'eps': 30.54,             # 1株当たり利益（円）
                'bps': 312.08,            # 1株当たり純資産（円）
                'dividend': 7.0,          # 配当金（円）
                'revenue': 5400000.0      # 売上高（百万円）
            },
            {
                'fiscal_period': '2022-12-31',
                'eps': 26.80,
                'bps': 295.50,
                'dividend': 6.5,
                'revenue': 4850000.0      # 成長率: 11.3%
            },
            {
                'fiscal_period': '2021-12-31',
                'eps': 23.10,
                'bps': 278.20,
                'dividend': 6.0,
                'revenue': 4350000.0      # 成長率: 11.5%
            }
        ]
    }
}


def seed_financial_data(session) -> None:
    """
    財務データをDBに投入（複数年対応）
    
    Args:
        session: SQLAlchemyのSession
    """
    try:
        count = 0
        
        for stock_code, data in FINANCIAL_DATA.items():
            print(f"\n[{stock_code}] {data['stock_name']} 財務データ投入中...")
            
            # UPSERT処理でDBに保存
            upsert_query = text("""
                INSERT INTO stock_financials 
                (stock_code, fiscal_period, eps, bps, dividend, revenue, created_at, updated_at)
                VALUES (:stock_code, :fiscal_period, :eps, :bps, :dividend, :revenue, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT (stock_code, fiscal_period)
                DO UPDATE SET
                    eps = EXCLUDED.eps,
                    bps = EXCLUDED.bps,
                    dividend = EXCLUDED.dividend,
                    revenue = EXCLUDED.revenue,
                    updated_at = CURRENT_TIMESTAMP
            """)
            
            # 複数年のデータを投入
            for year_data in data['years']:
                params = {
                    'stock_code': stock_code,
                    'fiscal_period': year_data['fiscal_period'],
                    'eps': year_data['eps'],
                    'bps': year_data['bps'],
                    'dividend': year_data['dividend'],
                    'revenue': year_data['revenue']
                }
                
                session.execute(upsert_query, params)
                count += 1
                
                print(f"  ✓ {year_data['fiscal_period']} データ投入")
                print(f"    - EPS: {year_data['eps']:>10.2f}円, BPS: {year_data['bps']:>10.2f}円")
                print(f"    - 配当: {year_data['dividend']:>10.2f}円, 売上: {year_data['revenue']:>15.0f}百万円")
            
            session.commit()
        
        print(f"\n  ✓ 合計 {count}件の財務データを投入しました")
        
    except Exception as e:
        session.rollback()
        print(f"エラーが発生しました: {e}")
        raise


def verify_financial_data(session) -> None:
    """
    投入した財務データを検証
    
    Args:
        session: SQLAlchemyのSession
    """
    print("\n" + "=" * 50)
    print("投入データの検証")
    print("=" * 50)
    
    query = text("""
        SELECT 
            s.stock_code,
            s.stock_name,
            f.fiscal_period,
            f.eps,
            f.bps,
            f.dividend,
            f.revenue
        FROM stocks s
        LEFT JOIN stock_financials f ON s.stock_code = f.stock_code
        ORDER BY s.stock_code, f.fiscal_period DESC
    """)
    
    rows = session.execute(query).fetchall()
    
    print("\n【銘柄マスタと財務データの紐付け確認】\n")
    
    for row in rows:
        stock_code, stock_name, fiscal_period, eps, bps, dividend, revenue = row
        
        if eps is None:
            status = "✗ 財務データなし"
        else:
            status = "✓ データ完全"
        
        print(f"{status} [{stock_code}] {stock_name}")
        
        if eps is not None:
            print(f"     会計期間: {fiscal_period}")
            print(f"     EPS: {eps:.2f}円, BPS: {bps:.2f}円")
            print(f"     配当: {dividend:.2f}円, 売上: {revenue:.0f}百万円")
        print()


def calculate_valuations(session) -> None:
    """
    PER/PBRを試算して整合性を確認
    
    Args:
        session: SQLAlchemyのSession
    """
    print("=" * 50)
    print("バリュエーション試算（整合性確認）")
    print("=" * 50)
    
    query = text("""
        SELECT 
            s.stock_code,
            s.stock_name,
            AVG(sp.close_price) as avg_price,
            f.eps,
            f.bps,
            f.dividend
        FROM stocks s
        LEFT JOIN stock_prices sp ON s.stock_code = sp.stock_code
        LEFT JOIN stock_financials f ON s.stock_code = f.stock_code
        GROUP BY s.stock_code, s.stock_name, f.eps, f.bps, f.dividend
        ORDER BY s.stock_code
    """)
    
    rows = session.execute(query).fetchall()
    
    print("\n【PER（株価収益率）と PBR（株価純資産倍率）の試算】\n")
    
    for row in rows:
        stock_code, stock_name, avg_price, eps, bps, dividend = row
        
        print(f"[{stock_code}] {stock_name}")
        print(f"  平均株価: {avg_price:.2f}円")
        
        if eps is None or bps is None:
            print(f"  ※ 財務データが不足しているため計算不可\n")
            continue
        
        # PER計算（株価 ÷ EPS）
        if eps > 0:
            per = avg_price / eps
            print(f"  PER: {per:.2f}倍 (株価÷EPS)")
        else:
            print(f"  PER: 計算不可（EPS={eps}）")
        
        # PBR計算（株価 ÷ BPS）
        if bps > 0:
            pbr = avg_price / bps
            print(f"  PBR: {pbr:.2f}倍 (株価÷BPS)")
        else:
            print(f"  PBR: 計算不可（BPS={bps}）")
        
        # 配当利回り
        if dividend and dividend > 0:
            dividend_yield = (dividend / avg_price) * 100
            print(f"  配当利回り: {dividend_yield:.2f}% (配当÷株価)")
        else:
            print(f"  配当利回り: 計算不可（配当={dividend}）")
        
        print()


def main() -> None:
    """メイン処理"""
    
    print("=" * 50)
    print("財務データ投入スクリプト")
    print("=" * 50)
    
    # データベース接続
    if not DATABASE_URL:
        print("エラー: DATABASE_URLが設定されていません")
        sys.exit(1)
    
    try:
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # 財務データを投入
        seed_financial_data(session)
        
        # 投入データを検証
        verify_financial_data(session)
        
        # バリュエーション試算
        calculate_valuations(session)
        
        session.close()
        
        print("=" * 50)
        print("財務データ投入が完了しました")
        print("=" * 50)
        
    except Exception as e:
        print(f"データベース接続エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
