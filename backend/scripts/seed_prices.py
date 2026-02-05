#!/usr/bin/env python
"""
テスト用 株価データ投入スクリプト

yfinanceのレート制限に対応するため、テスト用のダミーデータをDBに投入します。
実運用時はcollect_prices.pyで本物のデータを取得します。

対象銘柄：
- 7203: トヨタ自動車
- 6758: ソニーグループ
- 9984: ソフトバンクグループ

取得期間：直近45営業日分のダミーデータ
"""

from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import sys
import random

# 設定
STOCK_CODES = ['7203', '6758', '9984']
DATABASE_URL = os.getenv('DATABASE_URL')

# ダミーデータの基準値（実際の相場に近い値に設定）
# 注: 株価は「円」単位で記載
BASE_PRICES = {
    '7203': 2850.0,   # トヨタ自動車（円）
    '6758': 1350.0,   # ソニーグループ（円）- 修正: 13500→1350
    '9984': 720.0     # ソフトバンクグループ（円）- 修正: 7200→720
}

# 直近45営業日を生成（営業日のみ）
def get_business_dates(num_days=45):
    """営業日のリストを生成（土日と祝日を除外）"""
    dates = []
    current_date = datetime.now().date()
    
    while len(dates) < num_days:
        # 土日を除外
        if current_date.weekday() < 5:  # 0-4: 月-金
            dates.append(current_date)
        current_date -= timedelta(days=1)
    
    dates.reverse()  # 古い順に
    return dates


def generate_price_data(stock_code, base_price, dates):
    """
    ダミーデータを生成
    
    Args:
        stock_code: 銘柄コード
        base_price: 基準株価
        dates: 日付リスト
    
    Returns:
        辞書のリスト
    """
    data = []
    current_price = base_price
    
    for date in dates:
        # ランダムに±3%の変動
        daily_change = random.uniform(-0.03, 0.03)
        current_price = current_price * (1 + daily_change)
        
        # 日中の価格範囲を決定
        day_high = current_price * random.uniform(1.00, 1.02)
        day_low = current_price * random.uniform(0.98, 1.00)
        
        # Open価格を日中の範囲内で決定
        open_price = random.uniform(day_low, day_high)
        
        # Close価格を日中の範囲内で決定
        close_price = random.uniform(day_low, day_high)
        
        # 正式な高値・安値
        high_price = day_high
        low_price = day_low
        
        # 出来高を生成（銘柄によって異なる）
        if stock_code == '7203':
            volume = random.randint(10000000, 20000000)
        elif stock_code == '6758':
            volume = random.randint(20000000, 40000000)
        else:  # 9984
            volume = random.randint(30000000, 50000000)
        
        data.append({
            'stock_code': stock_code,
            'price_date': date,
            'open_price': round(open_price, 2),
            'high_price': round(high_price, 2),
            'low_price': round(low_price, 2),
            'close_price': round(close_price, 2),
            'volume': volume
        })
    
    return data


def seed_stock_prices(session) -> None:
    """
    ダミーデータをDBに投入
    
    Args:
        session: SQLAlchemyのSession
    """
    try:
        # 営業日リストを取得
        dates = get_business_dates(num_days=45)
        print(f"生成期間: {dates[0]} ～ {dates[-1]} ({len(dates)}営業日)")
        
        # 各銘柄のデータを生成・投入
        for stock_code in STOCK_CODES:
            print(f"\n[{stock_code}] ダミーデータ投入開始...")
            
            base_price = BASE_PRICES[stock_code]
            price_data = generate_price_data(stock_code, base_price, dates)
            
            # UPSERT処理でDBに保存
            count = 0
            for row in price_data:
                upsert_query = text("""
                    INSERT INTO stock_prices 
                    (stock_code, price_date, open_price, high_price, low_price, close_price, volume, created_at, updated_at)
                    VALUES (:stock_code, :price_date, :open_price, :high_price, :low_price, :close_price, :volume, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    ON CONFLICT (stock_code, price_date)
                    DO UPDATE SET
                        open_price = EXCLUDED.open_price,
                        high_price = EXCLUDED.high_price,
                        low_price = EXCLUDED.low_price,
                        close_price = EXCLUDED.close_price,
                        volume = EXCLUDED.volume,
                        updated_at = CURRENT_TIMESTAMP
                """)
                
                session.execute(upsert_query, row)
                count += 1
            
            session.commit()
            print(f"[{stock_code}] ✓ {count}件のダミーデータを投入しました")
        
    except Exception as e:
        session.rollback()
        print(f"エラーが発生しました: {e}")
        raise


def main() -> None:
    """メイン処理"""
    
    print("=" * 50)
    print("テスト用 株価データ投入スクリプト")
    print("=" * 50)
    
    # データベース接続
    if not DATABASE_URL:
        print("エラー: DATABASE_URLが設定されていません")
        sys.exit(1)
    
    try:
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # ダミーデータを投入
        seed_stock_prices(session)
        
        session.close()
        
    except Exception as e:
        print(f"データベース接続エラー: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("ダミーデータ投入が完了しました")
    print("=" * 50)


if __name__ == "__main__":
    main()
