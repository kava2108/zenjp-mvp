#!/usr/bin/env python
"""
簡易可視化スクリプト

株価データの統計情報をテキスト形式で出力します。
また、CSVファイルにエクスポートして外部ツール（Excel等）で
グラフ化することも可能です。

出力内容：
1. 各銘柄の統計情報（平均、最高、最低など）
2. 日別の変動統計
3. CSVファイルへのエクスポート
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import sys
import csv
from datetime import datetime
import statistics

# 設定
DATABASE_URL = os.getenv('DATABASE_URL')
STOCK_CODES = ['7203', '6758', '9984']
STOCK_NAMES = {
    '7203': 'トヨタ自動車',
    '6758': 'ソニーグループ',
    '9984': 'ソフトバンクグループ'
}

# 出力ファイル
OUTPUT_DIR = '/tmp/zenjp_reports'
CSV_FILE = f'{OUTPUT_DIR}/stock_prices.csv'


def ensure_output_dir():
    """出力ディレクトリを作成"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_price_statistics(session, stock_code):
    """
    株価の統計情報を取得
    
    Args:
        session: SQLAlchemyセッション
        stock_code: 銘柄コード
    
    Returns:
        統計情報の辞書
    """
    query = text("""
        SELECT 
            COUNT(*) as count,
            MIN(close_price) as min_price,
            MAX(close_price) as max_price,
            AVG(close_price) as avg_price,
            MIN(volume) as min_volume,
            MAX(volume) as max_volume,
            AVG(volume) as avg_volume
        FROM stock_prices
        WHERE stock_code = :stock_code
    """)
    
    result = session.execute(query, {'stock_code': stock_code}).fetchone()
    
    if not result:
        return None
    
    count, min_price, max_price, avg_price, min_volume, max_volume, avg_volume = result
    
    return {
        'count': int(count),
        'min_price': float(min_price),
        'max_price': float(max_price),
        'avg_price': float(avg_price),
        'min_volume': int(min_volume),
        'max_volume': int(max_volume),
        'avg_volume': float(avg_volume),
    }


def get_daily_changes(session, stock_code):
    """
    日次変動率を計算
    
    Args:
        session: SQLAlchemyセッション
        stock_code: 銘柄コード
    
    Returns:
        変動率のリスト
    """
    query = text("""
        SELECT close_price FROM stock_prices
        WHERE stock_code = :stock_code
        ORDER BY price_date
    """)
    
    rows = session.execute(query, {'stock_code': stock_code}).fetchall()
    
    changes = []
    
    for i in range(1, len(rows)):
        prev_price = float(rows[i-1][0])
        curr_price = float(rows[i][0])
        
        if prev_price > 0:
            change_pct = ((curr_price - prev_price) / prev_price) * 100
            changes.append(change_pct)
    
    return changes


def print_statistics(stock_code, stats, changes):
    """統計情報をコンソール出力"""
    
    print(f"\n[{stock_code}] {STOCK_NAMES.get(stock_code, '不明')}")
    print("-" * 50)
    
    print(f"  データ件数: {stats['count']}件")
    print(f"\n  【価格統計 (Close)】")
    print(f"    最小値: {stats['min_price']:>10,.2f}円")
    print(f"    最大値: {stats['max_price']:>10,.2f}円")
    print(f"    平均値: {stats['avg_price']:>10,.2f}円")
    print(f"    レンジ: {stats['max_price'] - stats['min_price']:>10,.2f}円")
    
    if changes:
        print(f"\n  【日次変動率統計】")
        avg_change = statistics.mean(changes)
        min_change = min(changes)
        max_change = max(changes)
        stdev_change = statistics.stdev(changes) if len(changes) > 1 else 0
        
        print(f"    平均変動率: {avg_change:>10.2f}%")
        print(f"    最小変動率: {min_change:>10.2f}%")
        print(f"    最大変動率: {max_change:>10.2f}%")
        print(f"    標準偏差: {stdev_change:>10.2f}%")
    
    print(f"\n  【出来高統計】")
    print(f"    最小出来高: {stats['min_volume']:>15,}株")
    print(f"    最大出来高: {stats['max_volume']:>15,}株")
    print(f"    平均出来高: {stats['avg_volume']:>15,.0f}株")


def export_to_csv(session):
    """
    すべての株価データをCSVファイルにエクスポート
    """
    query = text("""
        SELECT 
            stock_code,
            price_date,
            open_price,
            high_price,
            low_price,
            close_price,
            volume
        FROM stock_prices
        ORDER BY price_date DESC, stock_code
    """)
    
    rows = session.execute(query).fetchall()
    
    # CSVファイルに書き込み
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # ヘッダー行
        writer.writerow([
            '銘柄コード',
            '銘柄名',
            '日付',
            '始値',
            '高値',
            '安値',
            '終値',
            '出来高'
        ])
        
        # データ行
        for row in rows:
            stock_code, price_date, open_price, high_price, low_price, close_price, volume = row
            stock_name = STOCK_NAMES.get(stock_code, '不明')
            
            writer.writerow([
                stock_code,
                stock_name,
                price_date,
                f'{float(open_price):.2f}',
                f'{float(high_price):.2f}',
                f'{float(low_price):.2f}',
                f'{float(close_price):.2f}',
                int(volume)
            ])
    
    print(f"\n✓ CSVファイルを出力しました: {CSV_FILE}")


def main() -> None:
    """メイン処理"""
    
    print("=" * 50)
    print("株価データ簡易可視化")
    print("=" * 50)
    
    # データベース接続
    if not DATABASE_URL:
        print("エラー: DATABASE_URLが設定されていません")
        sys.exit(1)
    
    try:
        # 出力ディレクトリを作成
        ensure_output_dir()
        
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # 各銘柄の統計情報を取得・表示
        for stock_code in STOCK_CODES:
            stats = get_price_statistics(session, stock_code)
            changes = get_daily_changes(session, stock_code)
            
            if stats:
                print_statistics(stock_code, stats, changes)
        
        # CSVファイルにエクスポート
        export_to_csv(session)
        
        session.close()
        
        print("\n" + "=" * 50)
        print("可視化が完了しました")
        print("=" * 50)
        print("\n出力ファイル：")
        print(f"  - {CSV_FILE}")
        print("\nExcelやGoogleシートに取り込んでグラフ化できます")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
