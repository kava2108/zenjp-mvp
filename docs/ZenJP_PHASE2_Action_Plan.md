# ZenJP MVP PHASE2 実装アクション詳細計画書

**対象フェーズ:** PHASE2 データ取得（株価・財務データ）  
**期間:** Day 3-5（3日間、合計10時間）  
**担当:** 末告さん（指示・確認・承認）  
**実装:** GitHub Copilot（実行）  
**作成日:** 2026年2月5日

---

## 📋 目次

1. [PHASE2概要](#1-phase2概要)
2. [事前準備](#2-事前準備)
3. [Day 3: 株価データ取得（実装）](#3-day-3-株価データ取得実装)
4. [Day 4: 株価データ取得（完成）](#4-day-4-株価データ取得完成)
5. [Day 5: 財務データ取得](#5-day-5-財務データ取得)
6. [完了確認](#6-完了確認)
7. [トラブルシューティング](#7-トラブルシューティング)
8. [付録](#8-付録)

---

## 1. PHASE2概要

### 1.1 達成目標

**Day 3終了時:**
- ✅ yfinanceライブラリが正常動作
- ✅ `collect_prices.py` スクリプト完成
- ✅ トヨタ自動車（7203）の株価30日分取得成功
- ✅ UPSERT処理が動作（冪等性保証）

**Day 4終了時:**
- ✅ 3銘柄すべての株価データ取得（約90件）
- ✅ データ品質チェック完了
- ✅ 異常値検知ロジック実装（Gemini提案）
- ✅ 冪等性テスト完了

**Day 5終了時:**
- ✅ 3銘柄の財務データ投入（3件）
- ✅ EPS、BPS、配当すべて入力済み
- ✅ PER/PBR試算で整合性確認完了

### 1.2 成果物

```
zenjp-mvp/
├── backend/
│   ├── requirements.txt           # yfinance追加済み
│   └── scripts/
│       ├── collect_prices.py      # 株価取得（UPSERT、リトライ処理）
│       ├── validate_prices.py     # データ品質チェック
│       ├── detect_anomalies.py    # 異常値検知（AI生成）
│       ├── visualize_prices.py    # 簡易可視化
│       └── seed_financials.py     # 財務データ投入
└── docs/
    ├── data_collection_guide.md   # 運用手順書
    ├── financial_data_sources.md  # データソース記録
    └── quarterly_update.md         # 四半期更新手順
```

### 1.3 データ概要

| テーブル | 件数 | 内容 |
|---------|------|------|
| stock_prices | 約90件 | 3銘柄 × 30営業日 |
| stock_financials | 3件 | EPS、BPS、配当、売上高 |

---

## 2. 事前準備

### 2.1 PHASE1完了確認

**必須チェック:**

```bash
# プロジェクトディレクトリに移動
cd ~/zenjp-mvp

# Docker起動確認
docker-compose ps

# 期待される出力:
# zenjp_db       Up    0.0.0.0:5432->5432/tcp
# zenjp_backend  Up    0.0.0.0:8000->8000/tcp
# zenjp_frontend Up    0.0.0.0:3000->3000/tcp
```

**データベース確認:**

```bash
# テーブル確認
docker-compose exec db psql -U zenjp -d zenjp_mvp -c "\dt"

# 期待される出力: 4テーブル
#  stocks, stock_prices, stock_financials, daily_scores

# 銘柄マスタ確認
docker-compose exec db psql -U zenjp -d zenjp_mvp -c "SELECT * FROM stocks;"

# 期待される出力: 3件（7203, 6758, 9984）
```

**すべてOKならPHASE2開始可能**

### 2.2 Git作業ブランチ作成（推奨）

```bash
# 現在の状態をコミット
git add .
git commit -m "PHASE1完了: 環境構築・DB構築完了"

# PHASE2用ブランチ作成
git checkout -b phase2-data-collection
```

---

## 3. Day 3: 株価データ取得（実装）

**所要時間:** 3.5時間  
**目標:** yfinance動作確認 → collect_prices.py完成 → 1銘柄テスト成功

---

### ステップ1: yfinance動作確認（20分）

#### アクション1-1: yfinanceインストール確認

**コマンド:**
```bash
# requirements.txtを確認
cat backend/requirements.txt | grep yfinance
```

**期待される出力:**
```
yfinance==0.2.32
```

**もし含まれていない場合:**
```bash
# requirements.txtに追加
echo "yfinance==0.2.32" >> backend/requirements.txt

# コンテナ内でインストール
docker-compose exec backend pip install yfinance==0.2.32
```

**確認:**
```bash
docker-compose exec backend pip list | grep yfinance
# yfinance  0.2.32
```

---

#### アクション1-2: yfinance動作テスト

**Pythonインタラクティブシェルで確認:**

```bash
# Pythonシェル起動
docker-compose exec backend python
```

**テストコード（Python内で実行）:**
```python
import yfinance as yf
from datetime import datetime, timedelta

print("yfinanceインポート成功")

# トヨタ自動車のティッカー取得
ticker = yf.Ticker("7203.T")
print(f"ティッカー作成成功: {ticker.ticker}")

# 直近5日分のデータ取得テスト
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

hist = ticker.history(start=start_date, end=end_date)

print(f"\n取得件数: {len(hist)}件")
print("\n最新データ:")
print(hist.tail(3))

# 終了
exit()
```

**期待される出力:**
```
yfinanceインポート成功
ティッカー作成成功: 7203.T

取得件数: 5件

最新データ:
                  Open    High     Low   Close     Volume
Date                                                      
2026-02-03  2850.0  2880.0  2840.0  2870.0  12345678
2026-02-04  2870.0  2895.0  2860.0  2890.0  13456789
2026-02-05  2890.0  2910.0  2880.0  2900.0  14567890
```

**確認項目:**
- [ ] エラーが出ない
- [ ] DataFrameが返ってくる
- [ ] Open, High, Low, Close, Volumeカラムがある
- [ ] 日付インデックスがある

---

### ステップ2: collect_prices.py作成（90分）

#### アクション2-1: スクリプトファイル作成

**GitHub Copilotへの指示:**

```python
# ファイル名: backend/scripts/collect_prices.py

# Copilotに以下を指示:
# yfinanceを使って日本株の株価データを取得し、PostgreSQLに保存するスクリプトを作成してください
#
# === 基本仕様 ===
# 1. 対象銘柄
#    STOCK_CODES = ['7203', '6758', '9984']
#    yfinanceに渡す際は "{code}.T" 形式
#
# 2. 取得期間
#    直近45日（datetime.now() - timedelta(days=45)）
#    ※営業日約30日分を確保
#
# 3. データベース接続
#    DATABASE_URL = os.getenv("DATABASE_URL")
#    SQLAlchemyのcreate_engine、Session使用
#
# 4. UPSERT処理（冪等性保証）
#    INSERT INTO stock_prices (...) VALUES (...)
#    ON CONFLICT (stock_code, price_date)
#    DO UPDATE SET
#        open_price = EXCLUDED.open_price,
#        high_price = EXCLUDED.high_price,
#        low_price = EXCLUDED.low_price,
#        close_price = EXCLUDED.close_price,
#        volume = EXCLUDED.volume,
#        updated_at = CURRENT_TIMESTAMP
#
# 5. エラーハンドリング
#    - ネットワークエラー時: 3回リトライ（エクスポネンシャルバックオフ）
#    - データが空の場合: スキップして次の銘柄へ
#    - 各銘柄ごとにtry-exceptで処理
#    - エラー時はsession.rollback()
#
# 6. ログ出力
#    print("=" * 50)
#    print("株価データ取得を開始します")
#    print(f"対象銘柄: {', '.join(STOCK_CODES)}")
#    print("=" * 50)
#    ...
#    print(f"[{stock_code}] データ取得開始...")
#    print(f"[{stock_code}] ✓ {count}件のデータを保存しました")
#    ...
#    print("=" * 50)
#    print("株価データ取得が完了しました")
#    print("=" * 50)
#
# === 関数構成 ===
# def collect_stock_prices(stock_code: str, session) -> None:
#     """
#     指定された銘柄の株価データを取得してDBに保存
#     
#     Args:
#         stock_code: 銘柄コード（例: '7203'）
#         session: SQLAlchemyのSession
#     """
#     # 実装
#
# def main() -> None:
#     """メイン処理"""
#     # 実装
#
# if __name__ == "__main__":
#     main()
#
# === インポート ===
# import yfinance as yf
# from datetime import datetime, timedelta
# from sqlalchemy import create_engine, text
# from sqlalchemy.orm import sessionmaker
# import os
# import time
# import sys
#
# === 実装のポイント ===
# - yf.Ticker(f"{stock_code}.T") でティッカー取得
# - ticker.history(start=start_date, end=end_date) でデータ取得
# - df.iterrows() でDataFrameをループ
# - date.date() でdateオブジェクトに変換
# - float(), int() で型変換
# - session.execute(text(query), params) でUPSERT
# - session.commit() でコミット
#
# === リトライ処理の実装例 ===
# for attempt in range(3):
#     try:
#         hist = ticker.history(start=start_date, end=end_date)
#         break
#     except Exception as e:
#         if attempt < 2:
#             wait_time = 2 ** attempt
#             print(f"  リトライ {attempt + 1}/3 ({wait_time}秒後)")
#             time.sleep(wait_time)
#         else:
#             print(f"[{stock_code}] ✗ データ取得失敗: {e}")
#             return
```

**作成後の確認:**
```bash
# ファイルが作成されたか確認
ls -l backend/scripts/collect_prices.py

# 構文チェック
docker-compose exec backend python -m py_compile scripts/collect_prices.py
echo $?  # 0ならOK
```

---

#### アクション2-2: スクリプト実行権限付与

```bash
chmod +x backend/scripts/collect_prices.py
```

---

### ステップ3: テスト実行（30分）

#### アクション3-1: 全銘柄でデータ取得

**実行コマンド:**
```bash
docker-compose exec backend python scripts/collect_prices.py
```

**期待される出力:**
```
==================================================
株価データ取得を開始します
対象銘柄: 7203, 6758, 9984
==================================================

[7203] データ取得開始...
[7203] ✓ 30件のデータを保存しました

[6758] データ取得開始...
[6758] ✓ 30件のデータを保存しました

[9984] データ取得開始...
[9984] ✓ 30件のデータを保存しました

==================================================
株価データ取得が完了しました
==================================================
```

**確認項目:**
- [ ] 3銘柄すべてで「✓ XX件のデータを保存しました」と表示
- [ ] エラーが出ていない
- [ ] 処理時間が10秒以内

---

#### アクション3-2: データベース確認

**件数確認:**
```bash
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT stock_code, COUNT(*) as count
   FROM stock_prices 
   GROUP BY stock_code 
   ORDER BY stock_code;"
```

**期待される出力:**
```
 stock_code | count 
------------+-------
 6758       |    30
 7203       |    30
 9984       |    30
(3 rows)
```

**データ内容確認:**
```bash
# 最新10件を表示
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT stock_code, price_date, close_price, volume 
   FROM stock_prices 
   ORDER BY price_date DESC, stock_code 
   LIMIT 10;"
```

**期待される出力例:**
```
 stock_code | price_date | close_price |  volume  
------------+------------+-------------+----------
 6758       | 2026-02-05 |    13500.00 | 23456789
 7203       | 2026-02-05 |     2900.00 | 14567890
 9984       | 2026-02-05 |     7200.00 | 34567891
 6758       | 2026-02-04 |    13400.00 | 22345678
 7203       | 2026-02-04 |     2890.00 | 13456789
 9984       | 2026-02-04 |     7150.00 | 33456780
...
```

**確認項目:**
- [ ] 約90件のデータがある
- [ ] close_price、volumeにNULLがない
- [ ] 日付が新しい順に並んでいる

---

#### アクション3-3: 冪等性テスト

**再実行:**
```bash
# もう一度同じスクリプトを実行
docker-compose exec backend python scripts/collect_prices.py
```

**データ件数再確認:**
```bash
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT stock_code, COUNT(*) FROM stock_prices GROUP BY stock_code;"
```

**期待される結果:**
- 件数が変わらない（約90件のまま）
- エラーが出ない

**重複確認:**
```bash
# 重複データがないか確認
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT stock_code, price_date, COUNT(*) 
   FROM stock_prices 
   GROUP BY stock_code, price_date 
   HAVING COUNT(*) > 1;"
```

**期待される出力:**
```
 stock_code | price_date | count 
------------+------------+-------
(0 rows)
```

**0行 = 重複なし = UPSERT成功！**

---

### ステップ4: ドキュメント作成（30分）

#### アクション4-1: スクリプト使用方法をREADMEに追加

**GitHub Copilotへの指示:**

```markdown
# ファイル名: backend/scripts/README.md（新規作成）

# Copilotに以下を指示:
# データ収集スクリプトの使用方法を記載したREADMEを作成してください
#
# ## セクション構成
#
# ### 1. 概要
# - 株価データ取得スクリプトの説明
# - 対象銘柄: 7203（トヨタ）、6758（ソニー）、9984（SBG）
#
# ### 2. 必要な環境変数
# ```
# DATABASE_URL=postgresql://zenjp:password@db:5432/zenjp_mvp
# ```
#
# ### 3. 実行方法
# ```bash
# # 全銘柄のデータ取得
# docker-compose exec backend python scripts/collect_prices.py
#
# # データ確認
# docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
#   "SELECT stock_code, COUNT(*) FROM stock_prices GROUP BY stock_code;"
# ```
#
# ### 4. 実行結果の確認方法
# - 件数確認
# - 最新データ確認
# - NULL値確認
#
# ### 5. トラブルシューティング
# - yfinanceがインストールされていない
#   → pip install yfinance==0.2.32
# - データが取得できない
#   → ティッカーシンボル確認（.T付きか）
# - 重複エラーが発生する
#   → UNIQUE制約確認
#
# ### 6. 定期実行（将来）
# - cron設定例
# ```
# # 毎日18:00に実行（市場終了後）
# 0 18 * * * cd /path/to/zenjp-mvp && docker-compose exec -T backend python scripts/collect_prices.py
# ```
```

**確認:**
```bash
cat backend/scripts/README.md
```

---

### Day 3完了確認

#### チェックリスト

```bash
# 1. スクリプト存在確認
ls -la backend/scripts/collect_prices.py

# 2. 構文チェック
docker-compose exec backend python -m py_compile scripts/collect_prices.py

# 3. データ件数確認
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT COUNT(*) FROM stock_prices;"
# → 約90件

# 4. 銘柄別件数確認
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT stock_code, COUNT(*) FROM stock_prices GROUP BY stock_code;"
# → 各銘柄30件程度

# 5. 冪等性確認
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT stock_code, price_date, COUNT(*) 
   FROM stock_prices 
   GROUP BY stock_code, price_date 
   HAVING COUNT(*) > 1;"
# → 0 rows

# すべてOKなら
echo "✅ Day 3 完了！"
```

**成果物:**
- ✅ collect_prices.py（約150行）
- ✅ backend/scripts/README.md
- ✅ stock_pricesテーブルに約90件

---

## 4. Day 4: 株価データ取得（完成）

**所要時間:** 3.5時間  
**目標:** データ品質チェック、異常値検知、可視化スクリプト作成

---

### ステップ5: データ品質チェックスクリプト作成（45分）

#### アクション5-1: validate_prices.py作成

**GitHub Copilotへの指示:**

```python
# ファイル名: backend/scripts/validate_prices.py

# Copilotに以下を指示:
# stock_pricesテーブルのデータ品質をチェックするスクリプトを作成してください
#
# === チェック項目 ===
# 1. 件数チェック
#    - 各銘柄が20件以上あるか
#    SELECT stock_code, COUNT(*) FROM stock_prices GROUP BY stock_code
#
# 2. NULL値チェック
#    - close_price, volumeがNULLでないか
#    SELECT COUNT(*) FROM stock_prices 
#    WHERE close_price IS NULL OR volume IS NULL
#
# 3. 最新データ日付チェック
#    - 最新データが直近3営業日以内か
#    SELECT stock_code, MAX(price_date) FROM stock_prices GROUP BY stock_code
#
# 4. 価格範囲チェック
#    - close_price > 0
#    - volume >= 0
#    SELECT stock_code, COUNT(*) FROM stock_prices 
#    WHERE close_price <= 0 OR volume < 0 GROUP BY stock_code
#
# === 出力形式 ===
# ==================================================
# データ品質チェック
# ==================================================
#
# ■ データ件数:
#   ✓ 7203: 30件
#   ✓ 6758: 30件
#   ✓ 9984: 30件
#
# ■ NULL値:
#   ✓ NULL値なし
#
# ■ 最新データ日付:
#   7203: 2026-02-05
#   6758: 2026-02-05
#   9984: 2026-02-05
#
# ■ 価格範囲:
#   ✓ すべての価格が正常範囲
#
# ==================================================
# チェック完了: すべて正常
# ==================================================
#
# === 実装 ===
# - print_section()関数で見出し表示
# - check_count()関数で件数チェック
# - check_nulls()関数でNULLチェック
# - check_latest_date()関数で最新日付チェック
# - check_price_range()関数で価格範囲チェック
# - main()関数で全チェック実行
```

**確認:**
```bash
cat backend/scripts/validate_prices.py
docker-compose exec backend python -m py_compile scripts/validate_prices.py
```

---

#### アクション5-2: データ品質チェック実行

**コマンド:**
```bash
docker-compose exec backend python scripts/validate_prices.py
```

**期待される出力:**
```
==================================================
データ品質チェック
==================================================

■ データ件数:
  ✓ 7203: 30件
  ✓ 6758: 30件
  ✓ 9984: 30件

■ NULL値:
  ✓ NULL値なし

■ 最新データ日付:
  7203: 2026-02-05
  6758: 2026-02-05
  9984: 2026-02-05

■ 価格範囲:
  ✓ すべての価格が正常範囲

==================================================
チェック完了: すべて正常
==================================================
```

---

### ステップ6: 異常値検知ロジック実装（60分）🤖

**🔥 AI活用ポイント（Gemini提案・プロンプト#3）:**

異常値検知を追加することで、Day 6のスコア計算時のバグを事前に防ぎます。

#### アクション6-1: detect_anomalies.py作成

**GitHub Copilotへの指示（プロンプト#3）:**

```python
# ファイル名: backend/scripts/detect_anomalies.py

# Copilotに以下を指示:
# 株価データに混入しがちな異常値を検知するPython関数を書いてください:
#
# === 検知対象 ===
# 1. 株価が前日比で±50%以上変動（株式分割未調整の可能性）
# 2. 出来高が0（データ欠損）
# 3. 株価が0または負の値
# 4. 営業日でない日のデータ（土日のデータ）
#
# === 関数シグネチャ ===
# def detect_price_anomalies(stock_code: str, session) -> list[dict]:
#     """
#     異常値を検知して返す
#     
#     Args:
#         stock_code: 銘柄コード
#         session: SQLAlchemyのSession
#     
#     Returns:
#         [
#             {
#                 "date": "2026-01-28",
#                 "type": "large_change",
#                 "detail": "前日比+55%",
#                 "close_price": 2850.0,
#                 "prev_close": 1840.0
#             },
#             {
#                 "date": "2026-02-01",
#                 "type": "zero_volume",
#                 "detail": "出来高が0",
#                 "volume": 0
#             },
#             ...
#         ]
#     """
#
# === 実装のポイント ===
# - stock_pricesから日付順にデータ取得（ORDER BY price_date ASC）
# - 前日の終値と比較して変化率計算
#   change_pct = (today_close - prev_close) / prev_close * 100
# - abs(change_pct) > 50 なら異常
# - datetime.weekday()で土日判定（5=土曜、6=日曜）
# - 異常を検知したら辞書に追加
#
# === メイン処理 ===
# def main():
#     print("=" * 50)
#     print("異常値検知")
#     print("=" * 50)
#     
#     for stock_code in ['7203', '6758', '9984']:
#         print(f"\n[{stock_code}] チェック中...")
#         anomalies = detect_price_anomalies(stock_code, session)
#         
#         if not anomalies:
#             print(f"  ✓ 異常値なし")
#         else:
#             print(f"  ✗ 異常検出:")
#             for a in anomalies:
#                 print(f"    - {a['date']}: {a['detail']}")
#     
#     print("\n" + "=" * 50)
#     print("チェック完了")
#     print("=" * 50)
```

**確認:**
```bash
cat backend/scripts/detect_anomalies.py
docker-compose exec backend python -m py_compile scripts/detect_anomalies.py
```

---

#### アクション6-2: 異常値検知実行

**コマンド:**
```bash
docker-compose exec backend python scripts/detect_anomalies.py
```

**期待される出力（異常なしの場合）:**
```
==================================================
異常値検知
==================================================

[7203] チェック中...
  ✓ 異常値なし

[6758] チェック中...
  ✓ 異常値なし

[9984] チェック中...
  ✓ 異常値なし

==================================================
チェック完了: 異常値は検出されませんでした
==================================================
```

**もし異常が検出された場合:**
```
[7203] チェック中...
  ✗ 異常検出:
    - 2026-01-28: 前日比+55% (close: 2850.0, prev: 1840.0)
    - 2026-02-01: 出来高が0

→ この場合、該当データを確認:
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT * FROM stock_prices WHERE stock_code='7203' AND price_date='2026-01-28';"

→ 株式分割の場合はデータ削除して再取得
```

---

### ステップ7: 簡易可視化スクリプト作成（60分）

#### アクション7-1: visualize_prices.py作成

**GitHub Copilotへの指示:**

```python
# ファイル名: backend/scripts/visualize_prices.py

# Copilotに以下を指示:
# 株価データをテキストで可視化するスクリプトを作成してください
#
# === 機能 ===
# 1. pandasでデータ取得
#    query = """
#    SELECT stock_code, price_date, close_price, volume
#    FROM stock_prices
#    WHERE price_date >= CURRENT_DATE - INTERVAL '30 days'
#    ORDER BY stock_code, price_date DESC
#    """
#
# 2. 銘柄ごとに統計情報を表示
#    - 件数
#    - 最新株価
#    - 最高値
#    - 最低値
#    - 平均値
#    - 出来高平均
#
# === 出力形式 ===
# ==================================================
# 株価データサマリー（直近30日）
# ==================================================
#
# ■ 7203（トヨタ自動車）
#   件数    : 30件
#   最新    : 2,900.00円
#   最高    : 2,950.00円
#   最低    : 2,750.00円
#   平均    : 2,850.50円
#   出来高  : 14,567,890株（平均）
#
# ■ 6758（ソニーグループ）
#   件数    : 30件
#   最新    : 13,500.00円
#   最高    : 13,800.00円
#   最低    : 13,200.00円
#   平均    : 13,450.25円
#   出来高  : 23,456,789株（平均）
#
# ■ 9984（ソフトバンクグループ）
#   件数    : 30件
#   最新    : 7,200.00円
#   最高    : 7,350.00円
#   最低    : 7,050.00円
#   平均    : 7,175.50円
#   出来高  : 34,567,891株（平均）
#
# ==================================================
#
# === 実装 ===
# import pandas as pd
# from sqlalchemy import create_engine
# import os
#
# def get_summary(stock_code, df):
#     stock_df = df[df['stock_code'] == stock_code]
#     return {
#         'count': len(stock_df),
#         'latest': stock_df.iloc[0]['close_price'],
#         'max': stock_df['close_price'].max(),
#         'min': stock_df['close_price'].min(),
#         'mean': stock_df['close_price'].mean(),
#         'avg_volume': stock_df['volume'].mean()
#     }
```

**確認:**
```bash
cat backend/scripts/visualize_prices.py
docker-compose exec backend python -m py_compile scripts/visualize_prices.py
```

---

#### アクション7-2: 可視化実行

**コマンド:**
```bash
docker-compose exec backend python scripts/visualize_prices.py
```

**期待される出力:**
```
==================================================
株価データサマリー（直近30日）
==================================================

■ 7203（トヨタ自動車）
  件数    : 30件
  最新    : 2,900.00円
  最高    : 2,950.00円
  最低    : 2,750.00円
  平均    : 2,850.50円
  出来高  : 14,567,890株（平均）

■ 6758（ソニーグループ）
  件数    : 30件
  最新    : 13,500.00円
  最高    : 13,800.00円
  最低    : 13,200.00円
  平均    : 13,450.25円
  出来高  : 23,456,789株（平均）

■ 9984（ソフトバンクグループ）
  件数    : 30件
  最新    : 7,200.00円
  最高    : 7,350.00円
  最低    : 7,050.00円
  平均    : 7,175.50円
  出来高  : 34,567,891株（平均）

==================================================
```

---

### ステップ8: ドキュメント整備（35分）

#### アクション8-1: 運用手順書作成

**GitHub Copilotへの指示:**

```markdown
# ファイル名: docs/data_collection_guide.md（新規作成）

# Copilotに以下を指示:
# データ取得の運用手順書を作成してください
#
# === セクション構成 ===
#
# ## 1. 日次運用
# ### 実行タイミング
# - 市場終了後（15:30以降）
# - 推奨時刻: 18:00
#
# ### 実行手順
# ```bash
# cd ~/zenjp-mvp
# docker-compose exec backend python scripts/collect_prices.py
# docker-compose exec backend python scripts/validate_prices.py
# docker-compose exec backend python scripts/detect_anomalies.py
# ```
#
# ## 2. データ確認手順
# ### 件数確認
# ```bash
# docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
#   "SELECT stock_code, COUNT(*) FROM stock_prices GROUP BY stock_code;"
# ```
#
# ### 最新データ確認
# ```bash
# docker-compose exec backend python scripts/visualize_prices.py
# ```
#
# ## 3. トラブル対応
# ### データ取得失敗時
# - ネットワーク確認
# - yfinanceのステータス確認
# - 1時間後に再実行
#
# ### 異常値検出時
# - Yahoo Financeで株式分割を確認
# - 分割があれば該当データを削除して再取得:
# ```sql
# DELETE FROM stock_prices WHERE stock_code = '7203' AND price_date = '2026-01-28';
# ```
# - 再実行: docker-compose exec backend python scripts/collect_prices.py
#
# ## 4. データ再取得手順
# ### 特定銘柄のデータを削除して再取得
# ```bash
# # データ削除
# docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
#   "DELETE FROM stock_prices WHERE stock_code = '7203';"
#
# # 再取得
# docker-compose exec backend python scripts/collect_prices.py
# ```
#
# ### 全データ再取得
# ```bash
# # 全削除
# docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
#   "TRUNCATE TABLE stock_prices;"
#
# # 再取得
# docker-compose exec backend python scripts/collect_prices.py
# ```
```

**確認:**
```bash
cat docs/data_collection_guide.md
```

---

### Day 4完了確認

#### チェックリスト

```bash
# 1. スクリプト存在確認
ls -l backend/scripts/validate_prices.py
ls -l backend/scripts/detect_anomalies.py
ls -l backend/scripts/visualize_prices.py

# 2. データ品質チェック
docker-compose exec backend python scripts/validate_prices.py
# → すべて✓

# 3. 異常値検知
docker-compose exec backend python scripts/detect_anomalies.py
# → 異常値なし

# 4. 可視化
docker-compose exec backend python scripts/visualize_prices.py
# → 統計情報表示

# 5. NULL値確認
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT COUNT(*) FROM stock_prices WHERE close_price IS NULL;"
# → 0

# すべてOKなら
echo "✅ Day 4 完了！"
```

**成果物:**
- ✅ validate_prices.py
- ✅ detect_anomalies.py（AI生成）
- ✅ visualize_prices.py
- ✅ docs/data_collection_guide.md

---

## 5. Day 5: 財務データ取得

**所要時間:** 3時間  
**目標:** 3銘柄の財務データ投入完了、整合性確認

---

### ステップ9: データソース調査（30分）

#### アクション9-1: Yahoo Financeで財務データ確認

**ブラウザで各銘柄を確認:**

```
トヨタ自動車（7203）:
https://finance.yahoo.com/quote/7203.T/key-statistics

確認項目:
- EPS (Earnings Per Share / 1株当たり利益)
- BPS (Book Value Per Share / 1株当たり純資産)
- 配当 (Dividend / 年間配当金)
- 売上高 (Revenue)
```

#### アクション9-2: データ収集メモ作成

**ファイル作成:**
```bash
cat > backend/scripts/financial_data_memo.md << 'EOF'
# 財務データ収集メモ

## データ取得日
2026年2月7日

## トヨタ自動車（7203）
ソース: https://finance.yahoo.com/quote/7203.T
決算期: 2026年3月期

- EPS: 186.67円
- BPS: 1250.50円
- 配当: 280.0円
- 売上高（当期）: 35,000,000百万円
- 売上高（前期）: 33,500,000百万円
- 売上成長率: 4.48%

## ソニーグループ（6758）
ソース: https://finance.yahoo.com/quote/6758.T
決算期: 2026年3月期

- EPS: 850.25円
- BPS: 3200.00円
- 配当: 60.0円
- 売上高（当期）: 12,000,000百万円
- 売上高（前期）: 11,200,000百万円
- 売上成長率: 7.14%

## ソフトバンクグループ（9984）
ソース: https://finance.yahoo.com/quote/9984.T
決算期: 2026年3月期

- EPS: 420.50円
- BPS: 5800.00円
- 配当: 86.0円
- 売上高（当期）: 6,500,000百万円
- 売上高（前期）: 6,100,000百万円
- 売上成長率: 6.56%
EOF
```

**確認:**
```bash
cat backend/scripts/financial_data_memo.md
```

---

### ステップ10: seed_financials.py作成（60分）

#### アクション10-1: スクリプト作成

**GitHub Copilotへの指示:**

```python
# ファイル名: backend/scripts/seed_financials.py

# Copilotに以下を指示:
# 手動で収集した財務データをstock_financialsテーブルに投入するスクリプトを作成してください
#
# === データ定義 ===
# from datetime import date
#
# FINANCIAL_DATA = [
#     {
#         "stock_code": "7203",
#         "fiscal_period": date(2026, 3, 31),
#         "revenue": 35000000,  # 百万円
#         "eps": 186.67,
#         "bps": 1250.50,
#         "dividend": 280.0
#     },
#     {
#         "stock_code": "6758",
#         "fiscal_period": date(2026, 3, 31),
#         "revenue": 12000000,
#         "eps": 850.25,
#         "bps": 3200.00,
#         "dividend": 60.0
#     },
#     {
#         "stock_code": "9984",
#         "fiscal_period": date(2026, 3, 31),
#         "revenue": 6500000,
#         "eps": 420.50,
#         "bps": 5800.00,
#         "dividend": 86.0
#     }
# ]
#
# === 要件 ===
# 1. UPSERT処理
#    INSERT INTO stock_financials (...)
#    VALUES (...)
#    ON CONFLICT (stock_code, fiscal_period)
#    DO UPDATE SET
#        revenue = EXCLUDED.revenue,
#        eps = EXCLUDED.eps,
#        bps = EXCLUDED.bps,
#        dividend = EXCLUDED.dividend,
#        updated_at = CURRENT_TIMESTAMP
#
# 2. DATABASE_URLを環境変数から取得
# 3. 各銘柄ごとにINSERT実行
# 4. 成功/失敗をログ出力
# 5. トランザクション管理（commit/rollback）
#
# === 出力形式 ===
# ==================================================
# 財務データ投入
# ==================================================
#
# ✓ 7203: データ投入完了
# ✓ 6758: データ投入完了
# ✓ 9984: データ投入完了
#
# ==================================================
# 財務データ投入完了
# ==================================================
#
# === インポート ===
# from datetime import date
# from sqlalchemy import create_engine, text
# from sqlalchemy.orm import sessionmaker
# import os
```

**確認:**
```bash
cat backend/scripts/seed_financials.py
docker-compose exec backend python -m py_compile scripts/seed_financials.py
```

---

### ステップ11: データ投入実行（20分）

#### アクション11-1: 財務データ投入

**コマンド:**
```bash
docker-compose exec backend python scripts/seed_financials.py
```

**期待される出力:**
```
==================================================
財務データ投入
==================================================

✓ 7203: データ投入完了
✓ 6758: データ投入完了
✓ 9984: データ投入完了

==================================================
財務データ投入完了
==================================================
```

---

#### アクション11-2: データ確認

**件数確認:**
```bash
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT COUNT(*) FROM stock_financials;"
```

**期待される出力:**
```
 count 
-------
     3
(1 row)
```

**データ内容確認:**
```bash
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT stock_code, revenue, eps, bps, dividend 
   FROM stock_financials 
   ORDER BY stock_code;"
```

**期待される出力:**
```
 stock_code |  revenue  |  eps   |   bps   | dividend 
------------+-----------+--------+---------+----------
 6758       | 12000000  | 850.25 | 3200.00 |    60.00
 7203       | 35000000  | 186.67 | 1250.50 |   280.00
 9984       |  6500000  | 420.50 | 5800.00 |    86.00
(3 rows)
```

**確認項目:**
- [ ] 3件のデータがある
- [ ] すべてのカラムにNULLがない
- [ ] 数値が正しい

---

### ステップ12: データ整合性確認（30分）

#### アクション12-1: PER/PBR試算

**SQLクエリで確認:**

```bash
docker-compose exec db psql -U zenjp -d zenjp_mvp
```

**SQL:**
```sql
-- PER/PBR/配当利回り試算
SELECT 
    s.stock_code,
    s.stock_name,
    p.close_price AS "最新株価",
    f.eps AS "EPS",
    f.bps AS "BPS",
    f.dividend AS "配当",
    ROUND(p.close_price / f.eps, 2) AS "PER",
    ROUND(p.close_price / f.bps, 2) AS "PBR",
    ROUND((f.dividend / p.close_price) * 100, 2) AS "配当利回り(%)"
FROM stocks s
JOIN stock_financials f ON s.stock_code = f.stock_code
JOIN (
    SELECT DISTINCT ON (stock_code) 
        stock_code, 
        close_price 
    FROM stock_prices 
    ORDER BY stock_code, price_date DESC
) p ON s.stock_code = p.stock_code
ORDER BY s.stock_code;

-- 終了
\q
```

**期待される出力例:**
```
 stock_code |    stock_name    | 最新株価 |  EPS   |   BPS   | 配当 |  PER  | PBR  | 配当利回り(%)
------------+------------------+----------+--------+---------+------+-------+------+-------------
 6758       | ソニーグループ   | 13500.00 | 850.25 | 3200.00 | 60.0 | 15.88 | 4.22 |        0.44
 7203       | トヨタ自動車     |  2900.00 | 186.67 | 1250.50 |280.0 | 15.53 | 2.32 |        9.66
 9984       | SBG              |  7200.00 | 420.50 | 5800.00 | 86.0 | 17.12 | 1.24 |        1.19
(3 rows)
```

**確認項目:**
- [ ] PERが5-50倍の範囲内（日本株の妥当な範囲）
- [ ] PBRが0.5-5倍の範囲内
- [ ] 配当利回りが0-10%の範囲内
- [ ] すべて正の値

---

#### アクション12-2: NULL値・異常値確認

**NULL値確認:**
```bash
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT COUNT(*) 
   FROM stock_financials 
   WHERE eps IS NULL OR bps IS NULL OR dividend IS NULL;"
```

**期待される出力:**
```
 count 
-------
     0
```

**負の値確認:**
```bash
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT stock_code, eps, bps, dividend 
   FROM stock_financials 
   WHERE eps <= 0 OR bps <= 0 OR dividend < 0;"
```

**期待される出力:**
```
 stock_code | eps | bps | dividend 
------------+-----+-----+----------
(0 rows)
```

---

### ステップ13: ドキュメント作成（40分）

#### アクション13-1: データソース記録

**ファイル作成:**
```bash
cat > docs/financial_data_sources.md << 'EOF'
# 財務データソース一覧

## データ取得日
2026年2月7日

## データソース

### 主要ソース
- Yahoo Finance: https://finance.yahoo.com/
- 各社IRページ

## 取得データ詳細

### 7203 トヨタ自動車
- **ソース:** Yahoo Finance (https://finance.yahoo.com/quote/7203.T)
- **決算期:** 2026年3月期
- **売上高（当期）:** 35,000,000百万円
- **売上高（前期）:** 33,500,000百万円
- **EPS:** 186.67円
- **BPS:** 1250.50円
- **配当:** 280.0円
- **取得日:** 2026年2月7日

### 6758 ソニーグループ
- **ソース:** Yahoo Finance (https://finance.yahoo.com/quote/6758.T)
- **決算期:** 2026年3月期
- **売上高（当期）:** 12,000,000百万円
- **売上高（前期）:** 11,200,000百万円
- **EPS:** 850.25円
- **BPS:** 3200.00円
- **配当:** 60.0円
- **取得日:** 2026年2月7日

### 9984 ソフトバンクグループ
- **ソース:** Yahoo Finance (https://finance.yahoo.com/quote/9984.T)
- **決算期:** 2026年3月期
- **売上高（当期）:** 6,500,000百万円
- **売上高（前期）:** 6,100,000百万円
- **EPS:** 420.50円
- **BPS:** 5800.00円
- **配当:** 86.0円
- **取得日:** 2026年2月7日

## 次回更新予定

### 更新タイミング
各社の決算発表後（四半期ごと）:
- 第1四半期: 2026年5月
- 第2四半期: 2026年8月
- 第3四半期: 2026年11月
- 第4四半期: 2027年2月

### 更新対象データ
- EPS
- BPS
- 配当
- 売上高（当期・前期）

## 注意事項

### 株式分割対応
株式分割があった場合、EPS・BPS・配当を調整する必要があります。

例: 1:2 分割の場合
- EPS: 186.67円 → 93.34円
- BPS: 1250.50円 → 625.25円
- 配当: 280.0円 → 140.0円

### データ整合性チェック
財務データ更新後は必ずPER/PBRを試算して妥当性を確認してください。

```bash
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT stock_code, 
          ROUND(close_price / eps, 2) AS per,
          ROUND(close_price / bps, 2) AS pbr
   FROM stock_financials f
   JOIN (SELECT DISTINCT ON (stock_code) stock_code, close_price 
         FROM stock_prices ORDER BY stock_code, price_date DESC) p
   ON f.stock_code = p.stock_code;"
```
EOF
```

**確認:**
```bash
cat docs/financial_data_sources.md
```

---

#### アクション13-2: 四半期更新手順書作成

**ファイル作成:**
```bash
cat > docs/quarterly_update.md << 'EOF'
# 四半期財務データ更新手順

## 更新タイミング

各社の決算発表後（3ヶ月ごと）:
- **トヨタ自動車:** 2月、5月、8月、11月
- **ソニーグループ:** 2月、5月、8月、11月
- **ソフトバンクグループ:** 2月、5月、8月、11月

## 更新手順

### 1. 最新財務データ取得

各社のIRページまたはYahoo Financeから取得:
- EPS (Earnings Per Share / 1株当たり利益)
- BPS (Book Value Per Share / 1株当たり純資産)
- 配当 (Dividend / 年間配当金)
- 売上高 (Revenue / 当期・前期)

### 2. seed_financials.py更新

```python
# backend/scripts/seed_financials.py

FINANCIAL_DATA = [
    {
        "stock_code": "7203",
        "fiscal_period": date(2026, 6, 30),  # 期を更新
        "revenue": 36000000,      # 新しい値
        "eps": 195.50,            # 新しい値
        "bps": 1280.00,           # 新しい値
        "dividend": 290.0         # 新しい値
    },
    {
        "stock_code": "6758",
        "fiscal_period": date(2026, 6, 30),
        "revenue": 12500000,
        "eps": 870.00,
        "bps": 3250.00,
        "dividend": 65.0
    },
    {
        "stock_code": "9984",
        "fiscal_period": date(2026, 6, 30),
        "revenue": 6700000,
        "eps": 435.00,
        "bps": 5900.00,
        "dividend": 88.0
    }
]
```

### 3. データ投入

```bash
docker-compose exec backend python scripts/seed_financials.py
```

### 4. データ確認

```bash
# 件数確認
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT COUNT(*) FROM stock_financials;"

# 最新データ確認
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT * FROM stock_financials ORDER BY fiscal_period DESC LIMIT 3;"
```

### 5. 整合性確認

```bash
# PER/PBR試算
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT stock_code, 
          ROUND(close_price / eps, 2) AS per,
          ROUND(close_price / bps, 2) AS pbr
   FROM stock_financials f
   JOIN (SELECT DISTINCT ON (stock_code) stock_code, close_price 
         FROM stock_prices ORDER BY stock_code, price_date DESC) p
   ON f.stock_code = p.stock_code;"
```

**妥当性の目安:**
- PER: 5-50倍
- PBR: 0.5-5倍

### 6. データソース記録更新

```bash
# docs/financial_data_sources.md を更新
# - 取得日
# - 各銘柄のデータ
```

## トラブルシューティング

### データが取得できない場合
- Yahoo Financeで確認
- 各社IRページで決算短信を確認
- EDINETで有価証券報告書を確認

### PER/PBRが異常値の場合
- EPSの単位を確認（円建てか）
- 株式分割の有無を確認
- 前期との比較で急変がないか確認
EOF
```

**確認:**
```bash
cat docs/quarterly_update.md
```

---

### Day 5完了確認

#### チェックリスト

```bash
# 1. 財務データ件数確認
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT COUNT(*) FROM stock_financials;"
# → 3

# 2. NULL値確認
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT COUNT(*) FROM stock_financials 
   WHERE eps IS NULL OR bps IS NULL OR dividend IS NULL;"
# → 0

# 3. データ表示
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT stock_code, eps, bps, dividend FROM stock_financials 
   ORDER BY stock_code;"
# → 3銘柄すべて表示

# 4. PER試算（妥当性確認）
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT stock_code, 
          ROUND(2900.0 / eps, 2) AS per 
   FROM stock_financials 
   WHERE stock_code = '7203';"
# → PERが10-20程度

# すべてOKなら
echo "✅ Day 5 完了！"
```

**成果物:**
- ✅ seed_financials.py
- ✅ backend/scripts/financial_data_memo.md
- ✅ docs/financial_data_sources.md
- ✅ docs/quarterly_update.md
- ✅ stock_financialsテーブルに3件

---

## 6. 完了確認

### PHASE2完了チェックリスト

**最終確認スクリプト作成:**

```bash
cat > check_phase2.sh << 'EOF'
#!/bin/bash

echo "=== ZenJP MVP PHASE2 完了確認 ==="
echo ""

# 1. 株価データ確認
echo "1. 株価データ確認"
PRICE_COUNT=$(docker-compose exec -T db psql -U zenjp -d zenjp_mvp -t -c \
  "SELECT COUNT(*) FROM stock_prices;")
echo "  件数: $PRICE_COUNT"
if [ $PRICE_COUNT -ge 80 ]; then
    echo "  ✅ 株価データOK（90件程度期待）"
else
    echo "  ❌ 株価データ不足（80件未満）"
fi
echo ""

# 2. 財務データ確認
echo "2. 財務データ確認"
FIN_COUNT=$(docker-compose exec -T db psql -U zenjp -d zenjp_mvp -t -c \
  "SELECT COUNT(*) FROM stock_financials;")
echo "  件数: $FIN_COUNT"
if [ $FIN_COUNT -eq 3 ]; then
    echo "  ✅ 財務データOK"
else
    echo "  ❌ 財務データNG（3件期待）"
fi
echo ""

# 3. NULL値確認
echo "3. NULL値確認"
PRICE_NULL=$(docker-compose exec -T db psql -U zenjp -d zenjp_mvp -t -c \
  "SELECT COUNT(*) FROM stock_prices WHERE close_price IS NULL;")
FIN_NULL=$(docker-compose exec -T db psql -U zenjp -d zenjp_mvp -t -c \
  "SELECT COUNT(*) FROM stock_financials WHERE eps IS NULL;")
if [ $PRICE_NULL -eq 0 ] && [ $FIN_NULL -eq 0 ]; then
    echo "  ✅ NULL値なし"
else
    echo "  ❌ NULL値あり（株価: $PRICE_NULL, 財務: $FIN_NULL）"
fi
echo ""

# 4. スクリプト確認
echo "4. スクリプト確認"
for script in collect_prices.py validate_prices.py detect_anomalies.py seed_financials.py; do
    if [ -f "backend/scripts/$script" ]; then
        echo "  ✅ $script"
    else
        echo "  ❌ $script なし"
    fi
done
echo ""

# 5. ドキュメント確認
echo "5. ドキュメント確認"
for doc in data_collection_guide.md financial_data_sources.md quarterly_update.md; do
    if [ -f "docs/$doc" ]; then
        echo "  ✅ $doc"
    else
        echo "  ❌ $doc なし"
    fi
done
echo ""

echo "=== 確認完了 ==="
EOF

chmod +x check_phase2.sh
```

**実行:**
```bash
./check_phase2.sh
```

**期待される出力:**
```
=== ZenJP MVP PHASE2 完了確認 ===

1. 株価データ確認
  件数:       90
  ✅ 株価データOK（90件程度期待）

2. 財務データ確認
  件数:        3
  ✅ 財務データOK

3. NULL値確認
  ✅ NULL値なし

4. スクリプト確認
  ✅ collect_prices.py
  ✅ validate_prices.py
  ✅ detect_anomalies.py
  ✅ seed_financials.py

5. ドキュメント確認
  ✅ data_collection_guide.md
  ✅ financial_data_sources.md
  ✅ quarterly_update.md

=== 確認完了 ===
```

---

### 完了報告フォーマット

```markdown
## PHASE2完了報告

**実施日:** 2026年2月5-7日  
**担当:** 末告さん  
**所要時間:** 10時間

### 成果物

#### データ
- ✅ stock_prices: 90件（7203:30, 6758:30, 9984:30）
- ✅ stock_financials: 3件（全銘柄）

#### スクリプト
- ✅ collect_prices.py（株価取得・UPSERT・リトライ）
- ✅ validate_prices.py（品質チェック）
- ✅ detect_anomalies.py（異常値検知・AI生成）
- ✅ visualize_prices.py（簡易可視化）
- ✅ seed_financials.py（財務データ投入）

#### ドキュメント
- ✅ backend/scripts/README.md
- ✅ docs/data_collection_guide.md
- ✅ docs/financial_data_sources.md
- ✅ docs/quarterly_update.md

### 動作確認

- ✅ 冪等性テスト成功（2回実行でデータ重複なし）
- ✅ 異常値検知: 異常なし
- ✅ データ品質チェック: すべてOK
- ✅ PER/PBR試算: 正常範囲内

### AI活用実績

- ✅ プロンプト#3使用（異常値検知ロジック）
- ✅ エラーハンドリング自動生成
- ✅ UPSERT処理自動生成

### 次のステップ

PHASE3（スコア計算）の準備完了
- Day 6-7でスコア計算ロジック実装予定
- 取得済みデータを使用してValue/Growth/Momentumスコア算出
```

---

## 7. トラブルシューティング

### 問題1: yfinanceでデータが取得できない

**症状:**
```
[7203] ✗ データ取得失敗: ...
```

**原因:**
1. ティッカーシンボルが間違っている
2. ネットワーク接続の問題
3. Yahoo Finance側のAPI制限

**解決策:**

```python
# 1. ティッカーシンボル確認
ticker = yf.Ticker("7203.T")  # ✅ 正しい（.T付き）
ticker = yf.Ticker("7203")    # ❌ 間違い

# 2. 期間を短くしてテスト
hist = ticker.history(period="5d")  # 5日間のみ
print(len(hist))

# 3. リトライ処理が動作しているか確認
# ログに「リトライ 1/3」と表示されるか
```

---

### 問題2: データが0件

**症状:**
```sql
SELECT COUNT(*) FROM stock_prices;
-- 0件
```

**原因:**
- 取得期間が短すぎる
- 営業日がない期間を指定

**解決策:**

```python
# collect_prices.py の取得期間を確認
end_date = datetime.now()
start_date = end_date - timedelta(days=45)  # ✅ 45日（営業日約30日）
start_date = end_date - timedelta(days=7)   # ❌ 7日（短すぎる）
```

---

### 問題3: UPSERT時にエラー

**エラーメッセージ:**
```
ERROR: duplicate key value violates unique constraint "uq_prices_stock_date"
```

**原因:**
ON CONFLICT句が正しくない、またはUNIQUE制約がない

**解決策:**

```sql
-- 1. UNIQUE制約確認
\d stock_prices

-- UNIQUE制約がない場合は追加
ALTER TABLE stock_prices 
ADD CONSTRAINT uq_prices_stock_date UNIQUE (stock_code, price_date);

-- 2. 重複データ削除
DELETE FROM stock_prices a USING stock_prices b
WHERE a.id > b.id 
  AND a.stock_code = b.stock_code 
  AND a.price_date = b.price_date;

-- 3. スクリプト再実行
```

---

### 問題4: 財務データのNULL

**症状:**
```sql
SELECT * FROM stock_financials WHERE eps IS NULL;
-- 何件か返ってくる
```

**原因:**
Yahoo Financeでデータが取得できなかった

**解決策:**

```bash
# 各社IRページから手動で取得
# トヨタ: https://global.toyota/jp/ir/
# ソニー: https://www.sony.com/ja/SonyInfo/IR/
# SBG: https://group.softbank/ir

# 決算短信PDFから以下を抽出:
# - 1株当たり当期純利益（EPS）
# - 1株当たり純資産（BPS）
# - 1株当たり配当金

# seed_financials.pyのデータを更新して再実行
```

---

### 問題5: 異常値が検出される

**症状:**
```
[7203] ✗ 異常検出:
  - 2026-01-28: 前日比+55% (close: 2850.0, prev: 1840.0)
```

**原因:**
株式分割が実施されたがデータが未調整

**対処法:**

```bash
# 1. Yahoo Financeで株式分割を確認
# https://finance.yahoo.com/quote/7203.T/history

# 2. 分割日のデータを確認
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT * FROM stock_prices 
   WHERE stock_code='7203' 
     AND price_date BETWEEN '2026-01-27' AND '2026-01-29';"

# 3. 該当銘柄のデータを削除
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "DELETE FROM stock_prices WHERE stock_code='7203';"

# 4. データ再取得
docker-compose exec backend python scripts/collect_prices.py
```

---

## 8. 付録

### 付録A: yfinance APIリファレンス

**基本的な使い方:**

```python
import yfinance as yf
from datetime import datetime, timedelta

# ティッカー作成
ticker = yf.Ticker("7203.T")

# 履歴データ取得
hist = ticker.history(
    start=datetime(2026, 1, 1),
    end=datetime(2026, 2, 1),
    interval='1d'  # 1日足
)

# DataFrameで返される
# カラム: Open, High, Low, Close, Volume
print(hist.head())
```

**エラーハンドリング:**

```python
try:
    hist = ticker.history(start=start_date, end=end_date)
    if hist.empty:
        print("データが取得できませんでした")
        return
except Exception as e:
    print(f"エラー: {e}")
    return
```

---

### 付録B: SQL UPSERTパターン

**基本パターン:**

```sql
INSERT INTO table_name (col1, col2, col3)
VALUES (val1, val2, val3)
ON CONFLICT (unique_column)
DO UPDATE SET
    col2 = EXCLUDED.col2,
    col3 = EXCLUDED.col3,
    updated_at = CURRENT_TIMESTAMP;
```

**複合ユニークキー:**

```sql
INSERT INTO stock_prices (stock_code, price_date, close_price, volume)
VALUES ('7203', '2026-02-07', 2850.0, 12345678)
ON CONFLICT (stock_code, price_date)  -- 複合キー
DO UPDATE SET
    close_price = EXCLUDED.close_price,
    volume = EXCLUDED.volume,
    updated_at = CURRENT_TIMESTAMP;
```

---

### 付録C: データ品質チェックSQL

**件数チェック:**
```sql
SELECT stock_code, COUNT(*) 
FROM stock_prices 
GROUP BY stock_code;
```

**NULL値チェック:**
```sql
SELECT COUNT(*) 
FROM stock_prices 
WHERE close_price IS NULL OR volume IS NULL;
```

**日付範囲チェック:**
```sql
SELECT 
    stock_code,
    MIN(price_date) AS oldest,
    MAX(price_date) AS latest,
    COUNT(*) AS count
FROM stock_prices
GROUP BY stock_code;
```

**価格統計:**
```sql
SELECT 
    stock_code,
    MIN(close_price) AS min_price,
    MAX(close_price) AS max_price,
    ROUND(AVG(close_price), 2) AS avg_price
FROM stock_prices
GROUP BY stock_code;
```

---

### 付録D: GitHub Copilotプロンプトテンプレート

**yfinanceデータ取得:**
```
yfinanceを使って日本株の株価データを取得するPython関数を書いてください。

要件:
- ティッカーシンボル: {stock_code}.T
- 取得期間: startからendまで（datetime）
- ticker.history(start=start, end=end)
- 戻り値: pandas DataFrame（Date, Open, High, Low, Close, Volume）
- エラーハンドリング: データが空の場合はNoneを返す
```

**UPSERT処理:**
```
PostgreSQLのINSERT ... ON CONFLICT ... DO UPDATEを使ったUPSERT処理を実装してください。

テーブル: stock_prices
UNIQUE制約: (stock_code, price_date)
更新対象: open_price, high_price, low_price, close_price, volume, updated_at

SQLAlchemyのtext()を使用してください。
```

---

## 変更履歴

| Version | 日付 | 変更内容 | 作成者 |
|---------|------|---------|--------|
| 1.0.0 | 2026-02-05 | 初版作成 | ZenJP Team |

---

**ZenJP MVP PHASE2 実装アクション詳細計画書 完成**

**次のステップ:** Day 3 ステップ1から実装開始！
