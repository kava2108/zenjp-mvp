#!/usr/bin/env python
"""
株価データ取得スクリプト
yfinanceを使用して日本株の株価データを取得し、PostgreSQLに保存します。

対象銘柄：
- 7203: トヨタ自動車
- 6758: ソニーグループ
- 9984: ソフトバンクグループ

取得期間：直近45日間（営業日約30日分）
"""

import yfinance as yf
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import time
import sys

# 設定
STOCK_CODES = ['7203', '6758', '9984']
DATABASE_URL = os.getenv('DATABASE_URL')

# 直近45日を取得（営業日約30日分を確保）
END_DATE = datetime.now().date()
START_DATE = (datetime.now() - timedelta(days=45)).date()


def collect_stock_prices(stock_code: str, session) -> None:
    """
    指定された銘柄の株価データを取得してDBに保存
    
    Args:
        stock_code: 銘柄コード（例: '7203'）
        session: SQLAlchemyのSession
    
    Raises:
        Exception: データ取得またはDB操作に失敗した場合
    """
    print(f"\n[{stock_code}] データ取得開始...")
    
    # リトライ処理（最大3回）
    ticker_symbol = f"{stock_code}.T"
    hist = None
    
    for attempt in range(3):
        try:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(start=START_DATE, end=END_DATE)
            
            if hist is not None and len(hist) > 0:
                break
            
            if attempt < 2:
                wait_time = 2 ** attempt
                print(f"[{stock_code}] リトライ {attempt + 1}/3 ({wait_time}秒後)...")
                time.sleep(wait_time)
        except Exception as e:
            if attempt < 2:
                wait_time = 2 ** attempt
                print(f"[{stock_code}] エラー発生（{str(e)[:50]}...）")
                print(f"[{stock_code}] リトライ {attempt + 1}/3 ({wait_time}秒後)...")
                time.sleep(wait_time)
            else:
                print(f"[{stock_code}] ✗ データ取得失敗: {e}")
                return
    
    # データが取得できなかった場合
    if hist is None or len(hist) == 0:
        print(f"[{stock_code}] ✗ データが取得できませんでした")
        return
    
    # UPSERT処理でDBに保存
    try:
        count = 0
        for date, row in hist.iterrows():
            # 日付をdateオブジェクトに変換
            price_date = date.date()
            
            # データ型の変換
            open_price = float(row['Open'])
            high_price = float(row['High'])
            low_price = float(row['Low'])
            close_price = float(row['Close'])
            volume = int(row['Volume'])
            
            # UPSERT SQL（PostgreSQL）
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
            
            # パラメータをバインド
            params = {
                'stock_code': stock_code,
                'price_date': price_date,
                'open_price': open_price,
                'high_price': high_price,
                'low_price': low_price,
                'close_price': close_price,
                'volume': volume
            }
            
            # 実行
            session.execute(upsert_query, params)
            count += 1
        
        # コミット
        session.commit()
        print(f"[{stock_code}] ✓ {count}件のデータを保存しました")
        
    except Exception as e:
        session.rollback()
        print(f"[{stock_code}] ✗ DB保存失敗: {e}")
        raise


def main() -> None:
    """メイン処理"""
    
    print("=" * 50)
    print("株価データ取得を開始します")
    print(f"対象銘柄: {', '.join(STOCK_CODES)}")
    print(f"取得期間: {START_DATE} ～ {END_DATE}")
    print("=" * 50)
    
    # データベース接続
    if not DATABASE_URL:
        print("エラー: DATABASE_URLが設定されていません")
        sys.exit(1)
    
    try:
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # 各銘柄のデータを取得
        for stock_code in STOCK_CODES:
            try:
                collect_stock_prices(stock_code, session)
            except Exception as e:
                print(f"[{stock_code}] 処理中にエラーが発生しました: {e}")
                continue
        
        session.close()
        
    except Exception as e:
        print(f"データベース接続エラー: {e}")
        sys.exit(1)
    
    print("=" * 50)
    print("株価データ取得が完了しました")
    print("=" * 50)


if __name__ == "__main__":
    main()
