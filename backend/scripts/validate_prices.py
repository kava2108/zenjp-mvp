#!/usr/bin/env python
"""
株価データ品質チェックスクリプト

stock_pricesテーブルのデータ品質をチェックして、以下の項目を検証します：
1. 件数チェック - 各銘柄が20件以上あるか
2. NULL値チェック - 必須カラムがNULLでないか
3. 最新データ日付チェック - 最新データが本日以内か
4. 価格の妥当性チェック - High >= Close >= Low >= Open
5. 出来高の妥当性チェック - Volume > 0
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import sys
from datetime import datetime, timedelta

# 設定
DATABASE_URL = os.getenv('DATABASE_URL')
STOCK_CODES = ['7203', '6758', '9984']


def check_record_count(session) -> bool:
    """
    チェック1: 件数チェック
    
    各銘柄が20件以上のデータを持っているか確認
    """
    print("\n[チェック1] 件数確認")
    print("-" * 40)
    
    query = text("""
        SELECT stock_code, COUNT(*) as count 
        FROM stock_prices 
        GROUP BY stock_code 
        ORDER BY stock_code
    """)
    
    result = session.execute(query).fetchall()
    all_ok = True
    
    for row in result:
        stock_code, count = row
        status = "✓" if count >= 20 else "✗"
        print(f"  {status} [{stock_code}] {count}件")
        if count < 20:
            all_ok = False
    
    return all_ok


def check_null_values(session) -> bool:
    """
    チェック2: NULL値チェック
    
    必須カラム（close_price, volume）がNULLでないか確認
    """
    print("\n[チェック2] NULL値確認")
    print("-" * 40)
    
    queries = [
        ("close_price", text("SELECT COUNT(*) FROM stock_prices WHERE close_price IS NULL")),
        ("volume", text("SELECT COUNT(*) FROM stock_prices WHERE volume IS NULL")),
        ("open_price", text("SELECT COUNT(*) FROM stock_prices WHERE open_price IS NULL")),
        ("high_price", text("SELECT COUNT(*) FROM stock_prices WHERE high_price IS NULL")),
        ("low_price", text("SELECT COUNT(*) FROM stock_prices WHERE low_price IS NULL")),
    ]
    
    all_ok = True
    
    for col_name, query in queries:
        null_count = session.execute(query).scalar()
        status = "✓" if null_count == 0 else "✗"
        print(f"  {status} {col_name}: {null_count}件のNULL")
        if null_count > 0:
            all_ok = False
    
    return all_ok


def check_latest_date(session) -> bool:
    """
    チェック3: 最新データ日付チェック
    
    最新データが過去7日以内か確認
    """
    print("\n[チェック3] 最新データ日付確認")
    print("-" * 40)
    
    query = text("""
        SELECT stock_code, MAX(price_date) as latest_date
        FROM stock_prices
        GROUP BY stock_code
        ORDER BY stock_code
    """)
    
    result = session.execute(query).fetchall()
    threshold_date = datetime.now().date() - timedelta(days=7)
    all_ok = True
    
    for row in result:
        stock_code, latest_date = row
        days_ago = (datetime.now().date() - latest_date).days
        status = "✓" if latest_date >= threshold_date else "✗"
        print(f"  {status} [{stock_code}] {latest_date} ({days_ago}日前)")
        if latest_date < threshold_date:
            all_ok = False
    
    return all_ok


def check_price_validity(session) -> bool:
    """
    チェック4: 価格の妥当性チェック
    
    High >= Close, High >= Open, Close >= Low, Open >= Low の関係が成立しているか確認
    """
    print("\n[チェック4] 価格妥当性確認")
    print("-" * 40)
    
    # High >= Closeのチェック
    query1 = text("""
        SELECT COUNT(*) FROM stock_prices 
        WHERE high_price < close_price
    """)
    invalid_high_close = session.execute(query1).scalar()
    
    # High >= Openのチェック
    query2 = text("""
        SELECT COUNT(*) FROM stock_prices 
        WHERE high_price < open_price
    """)
    invalid_high_open = session.execute(query2).scalar()
    
    # Close >= Lowのチェック
    query3 = text("""
        SELECT COUNT(*) FROM stock_prices 
        WHERE close_price < low_price
    """)
    invalid_close_low = session.execute(query3).scalar()
    
    # Open >= Lowのチェック
    query4 = text("""
        SELECT COUNT(*) FROM stock_prices 
        WHERE open_price < low_price
    """)
    invalid_open_low = session.execute(query4).scalar()
    
    all_ok = True
    
    status1 = "✓" if invalid_high_close == 0 else "✗"
    print(f"  {status1} High >= Close: {invalid_high_close}件の異常")
    if invalid_high_close > 0:
        all_ok = False
    
    status2 = "✓" if invalid_high_open == 0 else "✗"
    print(f"  {status2} High >= Open: {invalid_high_open}件の異常")
    if invalid_high_open > 0:
        all_ok = False
    
    status3 = "✓" if invalid_close_low == 0 else "✗"
    print(f"  {status3} Close >= Low: {invalid_close_low}件の異常")
    if invalid_close_low > 0:
        all_ok = False
    
    status4 = "✓" if invalid_open_low == 0 else "✗"
    print(f"  {status4} Open >= Low: {invalid_open_low}件の異常")
    if invalid_open_low > 0:
        all_ok = False
    
    return all_ok


def check_volume_validity(session) -> bool:
    """
    チェック5: 出来高の妥当性チェック
    
    Volume > 0 か確認
    """
    print("\n[チェック5] 出来高妥当性確認")
    print("-" * 40)
    
    query = text("""
        SELECT COUNT(*) FROM stock_prices 
        WHERE volume <= 0
    """)
    
    invalid_volume = session.execute(query).scalar()
    status = "✓" if invalid_volume == 0 else "✗"
    print(f"  {status} Volume > 0: {invalid_volume}件の異常")
    
    return invalid_volume == 0


def check_price_range(session) -> bool:
    """
    チェック6: 価格の範囲チェック
    
    Close_priceが極端な値でないか確認
    """
    print("\n[チェック6] 価格範囲確認")
    print("-" * 40)
    
    all_ok = True
    
    for stock_code in STOCK_CODES:
        query = text("""
            SELECT 
                MIN(close_price) as min_price,
                MAX(close_price) as max_price,
                AVG(close_price) as avg_price
            FROM stock_prices
            WHERE stock_code = :stock_code
        """)
        
        result = session.execute(query, {'stock_code': stock_code}).fetchone()
        min_price, max_price, avg_price = result
        
        # 最高値と最低値の比が3倍以上なら警告
        ratio = max_price / min_price if min_price > 0 else 0
        status = "✓" if ratio < 3.0 else "⚠"
        print(f"  {status} [{stock_code}] 最小: {min_price:.2f}, 最大: {max_price:.2f}, 平均: {avg_price:.2f}, 比率: {ratio:.2f}")
    
    return all_ok


def main() -> None:
    """メイン処理"""
    
    print("=" * 50)
    print("株価データ品質チェック")
    print("=" * 50)
    
    # データベース接続
    if not DATABASE_URL:
        print("エラー: DATABASE_URLが設定されていません")
        sys.exit(1)
    
    try:
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # 各チェックを実行
        check1 = check_record_count(session)
        check2 = check_null_values(session)
        check3 = check_latest_date(session)
        check4 = check_price_validity(session)
        check5 = check_volume_validity(session)
        check6 = check_price_range(session)
        
        session.close()
        
        # 総合判定
        print("\n" + "=" * 50)
        print("チェック結果サマリー")
        print("=" * 50)
        
        checks = [
            ("件数確認", check1),
            ("NULL値確認", check2),
            ("最新データ日付確認", check3),
            ("価格妥当性確認", check4),
            ("出来高妥当性確認", check5),
            ("価格範囲確認", check6),
        ]
        
        all_passed = True
        for name, result in checks:
            status = "✓" if result else "✗"
            print(f"  {status} {name}")
            if not result:
                all_passed = False
        
        print("=" * 50)
        
        if all_passed:
            print("\n✅ すべてのチェックに合格しました！")
            sys.exit(0)
        else:
            print("\n⚠️ いくつかのチェックが失敗しました")
            sys.exit(1)
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
