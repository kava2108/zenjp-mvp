#!/usr/bin/env python
"""
異常値検知スクリプト

統計的な手法を使って株価データから異常値を検知します。
以下の異常を検出：
1. Z-scoreを使った価格異常値検知
2. 日次変動率の異常値検知
3. 出来高の異常値検知
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import sys
import statistics

# 設定
DATABASE_URL = os.getenv('DATABASE_URL')
STOCK_CODES = ['7203', '6758', '9984']

# 異常値判定の閾値（Z-score）
Z_SCORE_THRESHOLD = 2.5

# 日次変動率の異常値判定閾値（%）
PRICE_CHANGE_THRESHOLD = 10.0

# 出来高の異常値判定閾値（Z-score）
VOLUME_Z_SCORE_THRESHOLD = 2.0


def calculate_z_score(values, value):
    """
    Z-scoreを計算
    
    Z = (X - 平均) / 標準偏差
    """
    if len(values) < 2:
        return 0.0
    
    mean = statistics.mean(values)
    stdev = statistics.stdev(values)
    
    if stdev == 0:
        return 0.0
    
    return abs((value - mean) / stdev)


def detect_price_anomalies(session, stock_code) -> list:
    """
    価格異常値を検知
    
    Args:
        session: SQLAlchemyセッション
        stock_code: 銘柄コード
    
    Returns:
        異常値レコードのリスト
    """
    # Close_priceのデータを取得
    query = text("""
        SELECT price_date, close_price FROM stock_prices
        WHERE stock_code = :stock_code
        ORDER BY price_date
    """)
    
    rows = session.execute(query, {'stock_code': stock_code}).fetchall()
    
    if len(rows) < 3:
        return []
    
    # Close_priceのリストを作成
    close_prices = [float(row[1]) for row in rows]
    dates = [row[0] for row in rows]
    
    # Z-scoreを計算
    anomalies = []
    
    for i, (date, close_price) in enumerate(zip(dates, close_prices)):
        z_score = calculate_z_score(close_prices, close_price)
        
        if z_score > Z_SCORE_THRESHOLD:
            anomalies.append({
                'type': '価格異常',
                'date': date,
                'close_price': close_price,
                'z_score': z_score
            })
    
    return anomalies


def detect_price_change_anomalies(session, stock_code) -> list:
    """
    日次変動率の異常値を検知
    
    Args:
        session: SQLAlchemyセッション
        stock_code: 銘柄コード
    
    Returns:
        異常値レコードのリスト
    """
    query = text("""
        SELECT price_date, close_price FROM stock_prices
        WHERE stock_code = :stock_code
        ORDER BY price_date
    """)
    
    rows = session.execute(query, {'stock_code': stock_code}).fetchall()
    
    if len(rows) < 2:
        return []
    
    anomalies = []
    
    for i in range(1, len(rows)):
        date = rows[i][0]
        close_price = float(rows[i][1])
        prev_close_price = float(rows[i-1][1])
        
        if prev_close_price == 0:
            continue
        
        # 日次変動率を計算
        price_change_pct = abs((close_price - prev_close_price) / prev_close_price * 100)
        
        if price_change_pct > PRICE_CHANGE_THRESHOLD:
            anomalies.append({
                'type': '変動率異常',
                'date': date,
                'close_price': close_price,
                'prev_close_price': prev_close_price,
                'change_pct': price_change_pct
            })
    
    return anomalies


def detect_volume_anomalies(session, stock_code) -> list:
    """
    出来高の異常値を検知
    
    Args:
        session: SQLAlchemyセッション
        stock_code: 銘柄コード
    
    Returns:
        異常値レコードのリスト
    """
    query = text("""
        SELECT price_date, volume FROM stock_prices
        WHERE stock_code = :stock_code
        ORDER BY price_date
    """)
    
    rows = session.execute(query, {'stock_code': stock_code}).fetchall()
    
    if len(rows) < 3:
        return []
    
    # Volumeのリストを作成
    volumes = [int(row[1]) for row in rows]
    dates = [row[0] for row in rows]
    
    # Z-scoreを計算
    anomalies = []
    
    for date, volume in zip(dates, volumes):
        z_score = calculate_z_score(volumes, volume)
        
        if z_score > VOLUME_Z_SCORE_THRESHOLD:
            anomalies.append({
                'type': '出来高異常',
                'date': date,
                'volume': volume,
                'z_score': z_score
            })
    
    return anomalies


def format_anomaly_report(stock_code, anomalies) -> str:
    """異常値レポートをフォーマット"""
    
    if not anomalies:
        return f"  {stock_code}: 異常値なし"
    
    report = f"  {stock_code}: {len(anomalies)}件の異常を検知\n"
    
    for anomaly in anomalies:
        if anomaly['type'] == '価格異常':
            report += (f"    - {anomaly['date']}: "
                      f"Close={anomaly['close_price']:.2f}, "
                      f"Z-score={anomaly['z_score']:.2f}\n")
        
        elif anomaly['type'] == '変動率異常':
            report += (f"    - {anomaly['date']}: "
                      f"変動率={anomaly['change_pct']:.2f}%, "
                      f"Close={anomaly['close_price']:.2f}\n")
        
        elif anomaly['type'] == '出来高異常':
            report += (f"    - {anomaly['date']}: "
                      f"Volume={anomaly['volume']:,}, "
                      f"Z-score={anomaly['z_score']:.2f}\n")
    
    return report


def main() -> None:
    """メイン処理"""
    
    print("=" * 50)
    print("異常値検知分析")
    print("=" * 50)
    
    # データベース接続
    if not DATABASE_URL:
        print("エラー: DATABASE_URLが設定されていません")
        sys.exit(1)
    
    try:
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # 各銘柄の異常値を検知
        all_anomalies = {}
        
        for stock_code in STOCK_CODES:
            anomalies = []
            
            # 各種異常値を検知
            anomalies.extend(detect_price_anomalies(session, stock_code))
            anomalies.extend(detect_price_change_anomalies(session, stock_code))
            anomalies.extend(detect_volume_anomalies(session, stock_code))
            
            # 日付でソート
            anomalies.sort(key=lambda x: x['date'])
            
            all_anomalies[stock_code] = anomalies
        
        session.close()
        
        # レポート出力
        print("\n[異常値検知結果]\n")
        
        total_anomalies = 0
        
        for stock_code in STOCK_CODES:
            anomalies = all_anomalies[stock_code]
            report = format_anomaly_report(stock_code, anomalies)
            print(report)
            total_anomalies += len(anomalies)
        
        print("\n" + "=" * 50)
        print(f"合計異常値数: {total_anomalies}件")
        print("=" * 50)
        
        if total_anomalies > 0:
            print("\n⚠️ 異常値が検知されました")
            print("\n検知ルール：")
            print(f"  - 価格Z-score > {Z_SCORE_THRESHOLD}")
            print(f"  - 日次変動率 > {PRICE_CHANGE_THRESHOLD}%")
            print(f"  - 出来高Z-score > {VOLUME_Z_SCORE_THRESHOLD}")
        else:
            print("\n✅ 異常値は検知されませんでした")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
