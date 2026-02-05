# ZenJP MVP 要件定義書（2週間版）

**Version:** 1.1.0  
**作成日:** 2026年2月1日  
**最終更新:** 2026年2月1日（Gemini改善提案反映）  
**開発期間:** 2週間（14日間）  
**目的:** 最小機能でスコアリングの価値を検証

---

## 目次

1. [プロジェクト概要](#1-プロジェクト概要)
2. [MVP の範囲](#2-mvp-の範囲)
3. [機能要件](#3-機能要件)
4. [非機能要件](#4-非機能要件)
5. [技術スタック](#5-技術スタック)
6. [データ要件](#6-データ要件)
7. [画面要件](#7-画面要件)
8. [開発スケジュール](#8-開発スケジュール)
9. [成功基準](#9-成功基準)
10. [制約事項](#10-制約事項)

---

## 1. プロジェクト概要

### 1.1 背景

日本株市場には総合的なスコアリングサービスが存在しない。ZenJPは日本株に特化した独自のスコアリングシステムを提供するサービスである。

### 1.2 MVP の目的

**2週間で最小限の機能を実装し、以下を検証する：**

1. **スコアリングロジックの妥当性**
   - 計算したスコアが実際の株価パフォーマンスと相関するか
   - 投資家にとって有用な指標となるか

2. **技術的実現可能性**
   - データ取得の安定性
   - スコア計算の処理速度
   - システム全体の動作確認

3. **ユーザー価値の検証**
   - 実際の投資家からのフィードバック取得
   - UI/UXの方向性確認

### 1.3 MVP のスコープ

**作るもの：**
- 3銘柄のスコア計算システム（トヨタ、ソニー、ソフトバンク）
- 簡易スコア表示Web画面（1ページ）
- スコア取得API（1エンドポイント）

**作らないもの：**
- 全銘柄対応（3,800銘柄）
- 複雑な補正ロジック（TDnet、PBR改善等）
- ユーザー認証
- 有料プラン機能
- スクリーニング機能
- ランキング機能
- アラート機能

### 1.4 ターゲットユーザー

- **プライマリ**: 個人投資家（経験者）
- **セカンダリ**: フィンテック企業、投資情報サイト運営者

---

## 2. MVP の範囲

### 2.1 対象銘柄（3銘柄のみ）

| 銘柄コード | 銘柄名 | 選定理由 |
|-----------|--------|---------|
| 7203 | トヨタ自動車 | 時価総額1位、安定企業 |
| 6758 | ソニーグループ | 成長企業、グローバル展開 |
| 9984 | ソフトバンクグループ | ハイリスク・ハイリターン |

**なぜ3銘柄か：**
- 異なる特性を持つ銘柄でスコアの妥当性を検証
- データ取得・処理の負荷を最小化
- 2週間で確実に完成させる

### 2.2 スコアカテゴリ（3カテゴリのみ）

| カテゴリ | ウェイト | 含む指標 |
|---------|---------|---------|
| **Value（割安性）** | 40% | PER、PBR、配当利回り |
| **Growth（成長性）** | 30% | 売上高成長率（YoY） |
| **Momentum（モメンタム）** | 30% | RSI、出来高変化率 |

**除外するカテゴリ：**
- Financial（財務健全性） → フルバージョンで実装
- Analyst（アナリスト評価） → フルバージョンで実装

### 2.3 市場平均スコア（ベンチマーク）

スコアの相対的な価値を示すため、市場平均スコアを定義する。

**市場平均スコアの定義：**
- 総合スコア: **50点**（中立）
- Value: **50点**
- Growth: **50点**
- Momentum: **50点**

**用途：**
- フロントエンドでの比較表示（「市場平均：50点」）
- スコアの相対的な強さを視覚化
- 投資家への説得力向上

**実装方法：**
```python
# constants.py
MARKET_AVERAGE_SCORES = {
    "total": 50.0,
    "value": 50.0,
    "growth": 50.0,
    "momentum": 50.0
}
```

**UI表示例：**
```
総合スコア: 78.5点 (市場平均: 50.0点)
  → +28.5点 (市場平均を上回る)
```

### 2.4 機能範囲

#### 実装する機能

| 機能 | 優先度 | 説明 |
|------|--------|------|
| 株価データ取得 | 必須 | Yahoo Financeから日次OHLCV取得 |
| 財務データ取得（簡易） | 必須 | EDINETから最新期の売上高のみ |
| スコア計算 | 必須 | Value/Growth/Momentumの3カテゴリ |
| スコア表示API | 必須 | `/api/score/{stock_code}` |
| スコア表示画面 | 必須 | 1ページのシンプルUI |

#### 実装しない機能

- ユーザー登録・ログイン
- データベース複雑なリレーション
- リアルタイム更新
- TDnet連携
- 株式分割調整（簡易版のみ）
- レート制限
- キャッシング（Redis）
- 監視・ログ基盤

---

## 3. 機能要件

### 3.1 データ取得機能

**データ取得の基本方針:**
- **冪等性の保証**: 同じスクリプトを何度実行してもデータが重複しない
- **エラー時の継続**: 一部の銘柄でエラーが出ても他の銘柄は処理継続
- **ログの充実**: どのデータが取得できて、どれができなかったかを記録

### 3.2 スコア計算ロジックの調整方針

**重要: Day 6-7で定数の微調整を実施**

本要件定義書に記載されているスコア計算式の定数（例: PER基準15倍、PBR閾値1.0等）は、**理論的な初期値**です。

**Day 6-7のスコア実装時に、以下の作業を1-2時間確保してください:**

1. **期待スコアの設定**
   ```
   トヨタ（7203）: 総合スコア 70-80点（ランクB+前後）
     → 安定企業、Value高め、Growth中程度
   
   ソニー（6758）: 総合スコア 75-85点（ランクB+〜A）
     → 成長企業、Growth高め、Momentum良好
   
   SBG（9984）: 総合スコア 55-70点（ランクC+〜B）
     → ハイリスク、Value低め、Momentum変動大
   ```

2. **定数の微調整プロセス**
   ```python
   # 1. 実データで初回計算
   トヨタのPER = 12.5倍
   初期PER_Score = 100 - (12.5 / 15) * 50 = 58.3点
   
   # 2. 期待値と比較
   期待: Value 75-80点
   実測: Value 58.3点 → 低すぎる
   
   # 3. 定数を調整
   # PER基準を20倍に変更
   調整後PER_Score = 100 - (12.5 / 20) * 50 = 68.8点
   → まだ低い
   
   # PER基準を25倍に変更
   調整後PER_Score = 100 - (12.5 / 25) * 50 = 75.0点
   → OK！
   ```

3. **調整対象の定数一覧**
   
   | 定数名 | 初期値 | 調整範囲 | 影響 |
   |-------|--------|---------|------|
   | PER基準値 | 15倍 | 15-30倍 | Value高すぎ/低すぎ |
   | PBR閾値（満点） | 1.0倍 | 0.8-1.2倍 | Value高すぎ/低すぎ |
   | 配当利回り係数 | 20 | 15-25 | Value高すぎ/低すぎ |
   | 成長率20%（満点） | 20% | 15-25% | Growth高すぎ/低すぎ |
   | RSI理想ゾーン | 40-70 | 35-75 | Momentum高すぎ/低すぎ |

4. **調整後の記録**
   ```python
   # constants.py に記録
   # 最終調整値（2026-02-07時点）
   SCORING_CONSTANTS = {
       "per_baseline": 22.0,      # 初期15.0 → 調整
       "pbr_perfect_threshold": 1.0,  # 調整なし
       "dividend_multiplier": 18.0,   # 初期20.0 → 調整
       "growth_perfect_threshold": 18.0,  # 初期20.0 → 調整
       "rsi_ideal_min": 40,       # 調整なし
       "rsi_ideal_max": 70,       # 調整なし
   }
   ```

**調整の目標:**
- デモ時に「なるほど、このスコアは納得感がある」と思わせる
- 3銘柄の特性（安定/成長/ハイリスク）がスコアに反映される
- 極端なスコア（0点や100点ばかり）にならない

**調整時の注意:**
- 1つの定数を変えると全銘柄に影響するため、バランスを見る
- 調整履歴を残す（後で理由を説明できるように）
- 調整後は3銘柄すべてで再計算して確認

---

### 3.3 データ取得機能（詳細）

#### FR-D01: 株価データ取得

**概要:**  
Yahoo Finance APIから対象3銘柄の株価データを取得する。

**入力:**
- 銘柄コード（7203, 6758, 9984）
- 取得期間（直近30営業日）

**処理:**
1. Yahoo Finance APIを呼び出し
2. 日次OHLCV（始値、高値、安値、終値、出来高）を取得
3. データベースに保存（UPSERT方式）

**出力:**
- stock_prices テーブルに登録

**冪等性の保証（重要）:**

同じスクリプトを何度実行しても、データの整合性が保たれるように、PostgreSQLの`ON CONFLICT`句を使用してUPSERT処理を実装する。

```python
def save_stock_price(stock_code, price_date, close_price, volume):
    """
    株価データを保存（UPSERT）
    
    同じstock_codeとprice_dateのデータが存在する場合は更新、
    存在しない場合は新規挿入を行う。
    """
    query = """
    INSERT INTO stock_prices (stock_code, price_date, close_price, volume)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (stock_code, price_date)
    DO UPDATE SET
        close_price = EXCLUDED.close_price,
        volume = EXCLUDED.volume,
        updated_at = CURRENT_TIMESTAMP
    """
    execute(query, (stock_code, price_date, close_price, volume))
```

**実装例（yfinance使用）:**

```python
import yfinance as yf
from datetime import datetime, timedelta

def collect_stock_prices(stock_code):
    """
    指定銘柄の株価データを取得してDBに保存
    """
    # Yahoo Financeでは日本株は「XXXX.T」形式
    ticker = yf.Ticker(f"{stock_code}.T")
    
    # 直近30営業日分を取得
    end_date = datetime.now()
    start_date = end_date - timedelta(days=45)  # 余裕を持って45日
    
    hist = ticker.history(start=start_date, end=end_date)
    
    for date, row in hist.iterrows():
        save_stock_price(
            stock_code=stock_code,
            price_date=date.date(),
            close_price=row['Close'],
            volume=row['Volume']
        )
    
    print(f"{stock_code}: {len(hist)}件のデータを保存（UPSERT）")

# 実行例
for code in ['7203', '6758', '9984']:
    collect_stock_prices(code)
```

**例外処理:**
- API呼び出し失敗時は3回リトライ
- 3回失敗した場合はログ記録して処理スキップ
- ネットワークエラー時は60秒待機してリトライ

**更新頻度:**
- 手動実行（Pythonスクリプト）
- 何度実行しても安全（冪等性保証）

**メリット:**
- データ修正が容易（再実行するだけ）
- テスト時に何度でもやり直せる
- データの不整合が発生しない

---

#### FR-D02: 財務データ取得（簡易版）

**概要:**  
EDINETから対象3銘柄の最新期売上高を取得する。

**入力:**
- 銘柄コード（7203, 6758, 9984）

**処理:**
1. EDINET APIで最新有価証券報告書を検索
2. 売上高（当期・前期）を抽出
3. データベースに保存

**出力:**
- stock_financials テーブルに登録（売上高のみ）

**例外処理:**
- データ取得失敗時はログ記録
- 売上成長率は計算不可として扱う

**更新頻度:**
- 手動実行（Pythonスクリプト）

---

### 3.2 スコア計算機能

#### FR-S01: Valueスコア計算

**概要:**  
PER、PBR、配当利回りから割安性スコアを算出する。

**入力:**
- 株価（終値）
- EPS（1株当たり利益）
- BPS（1株当たり純資産）
- 年間配当

**計算式:**

```python
# PERスコア（業種平均15倍を基準）
PER = 株価 / EPS
PER_Score = max(0, 100 - (PER / 15) * 50)

# PBRスコア
PBR = 株価 / BPS
if PBR < 1.0:
    PBR_Score = 100
elif PBR < 1.5:
    PBR_Score = 80 - (PBR - 1.0) * 40
else:
    PBR_Score = max(0, 60 - (PBR - 1.5) * 20)

# 配当利回りスコア
配当利回り = (年間配当 / 株価) * 100
配当利回りScore = min(100, 配当利回り * 20)

# Value総合スコア
Value_Score = (PER_Score * 0.4 + PBR_Score * 0.3 + 配当利回りScore * 0.3)
```

**出力:**
- Value_Score（0-100）

**制約:**
- EPSが負の場合、PER_Score = 0
- 配当なしの場合、配当利回りScore = 0

---

#### FR-S02: Growthスコア計算

**概要:**  
売上高成長率から成長性スコアを算出する。

**入力:**
- 当期売上高
- 前期売上高

**計算式:**

```python
# 売上高成長率（YoY）の計算
def calculate_revenue_growth(current_revenue, previous_revenue):
    """
    売上高成長率を計算
    
    Returns:
        float: 成長率（%）または None（計算不可の場合）
    """
    # 例外処理: 前期データがない場合
    if previous_revenue is None or previous_revenue == 0:
        return None
    
    # 例外処理: 当期データがない場合
    if current_revenue is None:
        return None
    
    return ((current_revenue - previous_revenue) / previous_revenue) * 100

# Growthスコアの計算
def calculate_growth_score(revenue_growth):
    """
    売上成長率からGrowthスコアを算出
    
    Args:
        revenue_growth: 売上成長率（%）または None
    
    Returns:
        float: Growthスコア（0-100）
    """
    # 例外処理: 成長率が計算できない場合は中立スコア
    if revenue_growth is None:
        return 50.0  # 市場平均と同じ（中立）
    
    # 通常の計算
    if revenue_growth >= 20:
        return 100.0
    elif revenue_growth >= 10:
        return 80.0 + (revenue_growth - 10) * 2.0
    elif revenue_growth >= 0:
        return 50.0 + revenue_growth * 3.0
    else:
        return max(0.0, 50.0 + revenue_growth * 2.5)
```

**例外ケースとスコア:**

| ケース | 売上成長率 | Growthスコア | 理由 |
|-------|-----------|-------------|------|
| 通常（成長） | +15% | 90.0点 | 正常計算 |
| 通常（横ばい） | 0% | 50.0点 | 市場平均 |
| 通常（減収） | -5% | 37.5点 | 減点 |
| **前期データなし** | None | **50.0点** | 判断不可のため中立 |
| **当期データなし** | None | **50.0点** | 判断不可のため中立 |
| **前期売上=0** | None | **50.0点** | 計算不可のため中立 |

**出力:**
- Growth_Score（0-100）

**制約:**
- 前期売上高が0の場合、Growth_Score = 50（中立）
- データ欠損時もエラーではなく中立スコアを返す
- スコア計算が必ず完了することを保証

**データ欠損への対応方針:**
1. **データがない = 悪い ではない**
2. **データがない = 判断できない = 中立（50点）**
3. **エラーで止めずに処理を継続**

この方針により：
- 3銘柄以外への拡張が容易
- テスト時のトラブルが減少
- 実運用時の安定性が向上

**ログ出力例:**
```python
if revenue_growth is None:
    logger.warning(
        f"[{stock_code}] 売上成長率が計算できません。"
        f"中立スコア（50点）を採用します。"
    )
    return 50.0
```
- 前期売上高が取得できない場合、Growth_Score = 50（中立）
- 当期売上高が取得できない場合、Growth_Score = 50（中立）

**例外処理:**
```python
def calculate_growth_score(current_revenue, previous_revenue):
    """
    売上成長率スコアを計算
    
    Returns:
        float: Growthスコア（0-100）
    """
    # データ欠損時は中立値を返す
    if current_revenue is None or previous_revenue is None:
        return 50.0
    
    if previous_revenue == 0:
        return 50.0
    
    growth_rate = ((current_revenue - previous_revenue) / previous_revenue) * 100
    
    if growth_rate >= 20:
        return 100.0
    elif growth_rate >= 10:
        return 80.0 + (growth_rate - 10) * 2
    elif growth_rate >= 0:
        return 50.0 + growth_rate * 3
    else:
        return max(0.0, 50.0 + growth_rate * 2.5)
```

**重要:** データ欠損時に例外を発生させず、必ず数値（50.0）を返すことで、他のカテゴリスコアの計算を継続できるようにする。

---

#### FR-S03: Momentumスコア計算

**概要:**  
RSIと出来高変化率からモメンタムスコアを算出する。

**入力:**
- 過去30日の株価データ
- 過去30日の出来高データ

**計算式:**

```python
# RSI（14日）
上昇幅平均 = 過去14日の上昇幅の平均
下落幅平均 = 過去14日の下落幅の平均
RSI = 上昇幅平均 / (上昇幅平均 + 下落幅平均) * 100

# RSIスコア
if 40 <= RSI <= 70:
    RSI_Score = 100
elif RSI < 40:
    RSI_Score = 70 + (40 - RSI) * 0.75
else:  # RSI > 70
    RSI_Score = max(0, 100 - (RSI - 70) * 2)

# 出来高変化率
出来高変化率 = (直近出来高 / 20日平均出来高 - 1) * 100

if 出来高変化率 >= 50:
    Volume_Score = 90
elif 出来高変化率 >= 0:
    Volume_Score = 50 + 出来高変化率 * 0.8
else:
    Volume_Score = max(20, 50 + 出来高変化率 * 0.6)

# Momentum総合スコア
Momentum_Score = (RSI_Score * 0.6 + Volume_Score * 0.4)
```

**出力:**
- Momentum_Score（0-100）

---

#### FR-S04: 総合スコア計算

**概要:**  
3カテゴリスコアから総合スコアを算出する。

**入力:**
- Value_Score
- Growth_Score
- Momentum_Score

**計算式:**

```python
総合スコア = (
    Value_Score * 0.4 +
    Growth_Score * 0.3 +
    Momentum_Score * 0.3
)

# ランク判定
if 総合スコア >= 80:
    ランク = "A"
elif 総合スコア >= 70:
    ランク = "B+"
elif 総合スコア >= 60:
    ランク = "B"
elif 総合スコア >= 50:
    ランク = "C+"
elif 総合スコア >= 40:
    ランク = "C"
else:
    ランク = "D"
```

**出力:**
- 総合スコア（0-100）
- ランク（A/B+/B/C+/C/D）

---

### 3.3 API機能

#### FR-A01: スコア取得API

**エンドポイント:**
```
GET /api/score/{stock_code}
```

**パスパラメータ:**
- `stock_code`: 証券コード（7203/6758/9984のみ）

**レスポンス（成功時）:**
```json
{
  "status": "success",
  "data": {
    "stock_code": "7203",
    "stock_name": "トヨタ自動車",
    "date": "2026-02-01",
    "total_score": 78.5,
    "rank": "B+",
    "market_comparison": {
      "market_average": 50.0,
      "vs_market": "+28.5",
      "percentile": 85
    },
    "category_scores": {
      "value": {
        "score": 82.3,
        "weight": 0.4,
        "vs_market": "+32.3"
      },
      "growth": {
        "score": 65.8,
        "weight": 0.3,
        "vs_market": "+15.8"
      },
      "momentum": {
        "score": 80.1,
        "weight": 0.3,
        "vs_market": "+30.1"
      }
    },
    "market_comparison": {
      "total_score_diff": 26.5,
      "market_avg_total_score": 52.0,
      "percentile": 100,
      "comment": "市場平均を大きく上回る"
    },
    "details": {
      "per": 12.5,
      "pbr": 1.15,
      "dividend_yield": 2.8,
      "revenue_growth_yoy": 8.5,
      "rsi": 55.3,
      "volume_change": 12.5
    }
  },
  "meta": {
    "timestamp": "2026-02-01T12:00:00+09:00"
  }
}
```

**market_comparison フィールドの説明:**
- `total_score_diff`: 市場平均との差分（+26.5 = 78.5 - 52.0）
- `market_avg_total_score`: 市場平均スコア（MVP期間中は3銘柄の平均）
- `percentile`: 3銘柄中の順位を百分率で表示（100% = 1位）
- `comment`: 自動生成コメント
  - +20以上: "市場平均を大きく上回る"
  - +10〜+20: "市場平均を上回る"
  - -10〜+10: "市場平均並み"
  - -20〜-10: "市場平均を下回る"
  - -20未満: "市場平均を大きく下回る"

**レスポンス（エラー時）:**
```json
{
  "status": "error",
  "error": {
    "code": "INVALID_STOCK_CODE",
    "message": "対象外の銘柄コードです。現在は7203/6758/9984のみ対応しています。"
  }
}
```

**ステータスコード:**
- 200: 成功
- 400: 無効なパラメータ
- 404: 銘柄が見つからない
- 500: サーバーエラー

---

### 3.4 画面機能

#### FR-U01: スコア表示画面

**URL:**
```
/stocks/{stock_code}
```

**画面構成:**

```
┌─────────────────────────────────────┐
│ ZenJP MVP                          │
├─────────────────────────────────────┤
│                                     │
│  銘柄選択: [▼ 7203 - トヨタ自動車]  │
│                                     │
│  ┌─────────────────────────────┐  │
│  │ 総合スコア                    │  │
│  │   78.5 点                    │  │
│  │   ランク: B+                 │  │
│  │                              │  │
│  │   市場平均: 52.0点           │  │
│  │   差分: +26.5点 ⬆️           │  │
│  │   市場平均を大きく上回る      │  │
│  └─────────────────────────────┘  │
│                                     │
│  ┌─────────────────────────────┐  │
│  │ カテゴリ別スコア              │  │
│  │                              │  │
│  │ Value     ████████░ 82.3    │  │
│  │ (平均52)   ↑+30.3           │  │
│  │                              │  │
│  │ Growth    ██████░░░ 65.8    │  │
│  │ (平均48)   ↑+17.8           │  │
│  │                              │  │
│  │ Momentum  ████████░ 80.1    │  │
│  │ (平均55)   ↑+25.1           │  │
│  └─────────────────────────────┘  │
│                                     │
│  ┌─────────────────────────────┐  │
│  │ 詳細指標                      │  │
│  │                              │  │
│  │ PER:        12.5倍           │  │
│  │ PBR:         1.15倍          │  │
│  │ 配当利回り:   2.8%            │  │
│  │ 売上成長率:   8.5%            │  │
│  │ RSI:        55.3             │  │
│  │ 出来高変化: +12.5%            │  │
│  └─────────────────────────────┘  │
│                                     │
│  更新日時: 2026-02-01 12:00        │
│  対象銘柄: 3銘柄                   │
│                                     │
└─────────────────────────────────────┘
```

**機能:**
- 銘柄選択（ドロップダウン: 7203/6758/9984）
- 総合スコアとランクの表示
- **市場平均との比較表示**（差分、コメント）
- カテゴリ別スコアのバーチャート
- **各カテゴリの市場平均との差分**
- 詳細指標の数値表示
- 最終更新日時の表示
- 対象銘柄数の表示（3銘柄と明記）

**非機能:**
- レスポンシブデザイン（スマホ対応は後回し）
- アニメーション（静的表示のみ）
- リアルタイム更新（手動リロード）

---

## 4. 非機能要件

### 4.1 性能要件

| 項目 | 要件 |
|------|------|
| API応答時間 | 500ms以内 |
| 画面表示速度 | 2秒以内（初回読み込み） |
| スコア計算時間 | 1銘柄あたり100ms以内 |
| 同時接続数 | 10ユーザー（MVP期間中） |

### 4.2 可用性要件

| 項目 | 要件 |
|------|------|
| 稼働時間 | 営業時間（9:00-15:00）のみ保証 |
| ダウンタイム | 許容（MVP期間中） |
| データバックアップ | 不要（再取得可能） |

### 4.3 セキュリティ要件

| 項目 | 要件 |
|------|------|
| 認証 | 不要（全データ公開） |
| HTTPS | 不要（HTTP許可） |
| SQL Injection対策 | ORM使用（SQLAlchemy） |
| XSS対策 | エスケープ処理 |

### 4.4 保守性要件

| 項目 | 要件 |
|------|------|
| ログ出力 | 標準出力のみ |
| エラーハンドリング | try-exceptで最低限対応 |
| コードコメント | 主要関数のみ |
| テストコード | 不要（手動テスト） |

---

## 5. 技術スタック

### 5.1 バックエンド

| 技術 | バージョン | 用途 |
|------|-----------|------|
| Python | 3.11+ | 言語 |
| FastAPI | 0.104+ | APIフレームワーク |
| SQLAlchemy | 2.0+ | ORM |
| PostgreSQL | 14+ | データベース |
| yfinance | 最新 | Yahoo Finance API |
| pandas | 最新 | データ処理 |

### 5.2 フロントエンド

| 技術 | バージョン | 用途 |
|------|-----------|------|
| Next.js | 14+ | フレームワーク |
| TypeScript | 5.0+ | 言語 |
| Tailwind CSS | 3.4+ | スタイリング |
| Recharts | 最新 | チャート表示 |

### 5.3 インフラ

| 技術 | 用途 |
|------|------|
| Docker | ローカル開発環境 |
| Docker Compose | 複数コンテナ管理 |

---

## 6. データ要件

### 6.1 データベーススキーマ（簡易版）

#### stocks テーブル
```sql
CREATE TABLE stocks (
    stock_code VARCHAR(4) PRIMARY KEY,
    stock_name VARCHAR(100) NOT NULL,
    sector_name VARCHAR(50),
    market VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### stock_prices テーブル
```sql
CREATE TABLE stock_prices (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(4) NOT NULL,
    price_date DATE NOT NULL,
    close_price NUMERIC(10,2) NOT NULL,
    volume BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code, price_date)
);
```

#### stock_financials テーブル（簡易版）
```sql
CREATE TABLE stock_financials (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(4) NOT NULL,
    fiscal_period DATE NOT NULL,
    revenue BIGINT,  -- 売上高のみ
    eps NUMERIC(10,2),
    bps NUMERIC(10,2),
    dividend NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code, fiscal_period)
);
```

#### daily_scores テーブル（簡易版）
```sql
CREATE TABLE daily_scores (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(4) NOT NULL,
    score_date DATE NOT NULL,
    total_score NUMERIC(5,2) NOT NULL,
    rank VARCHAR(2) NOT NULL,
    value_score NUMERIC(5,2),
    growth_score NUMERIC(5,2),
    momentum_score NUMERIC(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code, score_date)
);
```

#### market_average_scores テーブル（市場平均）
```sql
CREATE TABLE market_average_scores (
    id SERIAL PRIMARY KEY,
    score_date DATE NOT NULL UNIQUE,
    avg_total_score NUMERIC(5,2) NOT NULL DEFAULT 50.0,
    avg_value_score NUMERIC(5,2) NOT NULL DEFAULT 50.0,
    avg_growth_score NUMERIC(5,2) NOT NULL DEFAULT 50.0,
    avg_momentum_score NUMERIC(5,2) NOT NULL DEFAULT 50.0,
    sample_size INTEGER NOT NULL DEFAULT 3,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**用途:**
- 個別銘柄スコアとの相対比較
- UI上で「市場平均: 52点」として表示
- MVP期間中は3銘柄の平均値を市場平均として使用

### 6.2 初期データ

#### 銘柄マスタ
```sql
INSERT INTO stocks (stock_code, stock_name, sector_name, market) VALUES
('7203', 'トヨタ自動車', '輸送用機器', 'プライム'),
('6758', 'ソニーグループ', '電気機器', 'プライム'),
('9984', 'ソフトバンクグループ', '情報・通信業', 'プライム');
```

### 6.3 データ更新方針

| データ種別 | 更新方法 | 頻度 |
|-----------|---------|------|
| 株価データ | Pythonスクリプト手動実行 | 必要時 |
| 財務データ | Pythonスクリプト手動実行 | 初回のみ |
| スコアデータ | Pythonスクリプト手動実行 | 必要時 |

---

## 7. 画面要件

### 7.1 画面一覧

| 画面ID | 画面名 | URL | 優先度 |
|--------|--------|-----|--------|
| SC-01 | スコア表示画面 | `/stocks/{stock_code}` | 必須 |
| SC-02 | トップページ | `/` | 必須 |

### 7.2 SC-01: スコア表示画面

#### レイアウト

**ヘッダー**
- ロゴ（ZenJP MVP）
- 説明文（1行）

**メインコンテンツ**
1. 銘柄選択ドロップダウン
2. 総合スコアカード
3. カテゴリ別スコアバー
4. 詳細指標テーブル
5. 更新日時

**フッター**
- 免責事項（1行）

#### カラーパレット

```css
/* スコアランクの色分け */
A:   #22c55e (緑)
B+:  #84cc16 (ライムグリーン)
B:   #eab308 (黄)
C+:  #f97316 (オレンジ)
C:   #ef4444 (赤)
D:   #991b1b (ダークレッド)
```

---

## 8. 開発スケジュール

### 8.1 全体スケジュール（14日間）

| Day | タスク | 成果物 | 担当 |
|-----|--------|--------|------|
| 1 | 環境構築 | Docker環境、PostgreSQL | Backend |
| 2 | DBスキーマ作成 | テーブル作成SQL | Backend |
| 3 | 株価データ取得実装 | data_collector.py | Backend |
| 4 | 株価データ取得テスト | 3銘柄のデータ | Backend |
| 5 | 財務データ取得実装 | financial_collector.py | Backend |
| 6 | スコア計算実装（Value） | score_calculator.py | Backend |
| 7 | スコア計算実装（Growth/Momentum） | score_calculator.py | Backend |
| 8 | API実装 | /api/score/{code} | Backend |
| 9 | API動作確認 | Postmanテスト | Backend |
| 10 | フロント環境構築 | Next.jsプロジェクト | Frontend |
| 11 | スコア表示画面実装 | /stocks/[code] | Frontend |
| 12 | UI調整・デザイン | CSS調整 | Frontend |
| 13 | 統合テスト | E2Eテスト | All |
| 14 | デモ準備・ドキュメント | README、スクショ | All |

### 8.2 Day 1-2: 環境構築・DB設計

**タスク:**
- [ ] Dockerfileとdocker-compose.yml作成
- [ ] PostgreSQL起動確認
- [ ] FastAPIプロジェクト初期化
- [ ] SQLAlchemyモデル定義
- [ ] テーブル作成スクリプト実行
- [ ] 初期データ投入

**成果物:**
- 動作するDockerコンテナ
- 3銘柄が登録されたDB

### 8.3 Day 3-4: 株価データ取得

**タスク:**
- [ ] yfinance を使った株価取得関数実装
- [ ] stock_pricesテーブルへの保存処理
- [ ] 30日分のデータ取得・保存
- [ ] エラーハンドリング実装

**成果物:**
- `scripts/collect_prices.py`
- 3銘柄 × 30日分のデータ

### 8.4 Day 5: 財務データ取得

**タスク:**
- [ ] 手動で財務データ収集（EDINET）
- [ ] stock_financialsテーブルに投入
- [ ] EPS、BPS、配当データの確認

**成果物:**
- 3銘柄の財務データ

### 8.5 Day 6-7: スコア計算実装

**タスク:**
- [ ] Value スコア計算関数
- [ ] Growth スコア計算関数
- [ ] Momentum スコア計算関数
- [ ] 総合スコア計算関数
- [ ] daily_scoresテーブルへ保存
- [ ] 市場平均スコアの計算・保存
- [ ] **スコア定数の微調整（1-2時間確保）**

**成果物:**
- `services/score_calculator.py`
- 3銘柄のスコアデータ

**重要: スコア定数の調整**

計算式内の定数（業種平均PER=15、PBR基準値等）は仮の値です。実装後に以下の期待値と照らし合わせて微調整してください：

**期待されるスコア傾向:**
```python
# トヨタ自動車（7203）- 安定企業
期待スコア = {
    "total": 70-80,  # B+前後
    "value": 75-85,  # Value高（配当あり、PBR低め）
    "growth": 60-70, # Growth中（安定成長）
    "momentum": 65-75 # Momentum中
}

# ソニーグループ（6758）- 成長企業
期待スコア = {
    "total": 75-85,  # B+〜A
    "value": 60-70,  # Value中
    "growth": 80-90, # Growth高（高成長）
    "momentum": 70-80 # Momentum高
}

# ソフトバンクグループ（9984）- ハイリスク
期待スコア = {
    "total": 55-65,  # C+〜B
    "value": 40-50,  # Value低（PBR高い）
    "growth": 70-80, # Growth高（投資先成長）
    "momentum": 50-70 # Momentum変動大
}
```

**調整時の手順:**
1. 3銘柄のスコアを計算
2. 期待値と比較
3. ずれが大きい場合、定数を調整
   - PER基準値（現在15）を12-18の範囲で調整
   - PBRの閾値（現在1.0/1.5）を微調整
   - 配当利回りの倍率を調整
4. 再計算して確認
5. 3銘柄が期待範囲内に収まることを確認

**調整例:**
```python
# 調整前: PER基準値15
PER_Score = max(0, 100 - (PER / 15) * 50)

# トヨタのPERが12でスコアが高すぎる場合
# → 基準値を13に下げる
PER_Score = max(0, 100 - (PER / 13) * 50)
```

**時間配分:**
- Day 6午前: Value実装
- Day 6午後: Growth実装
- Day 7午前: Momentum実装
- Day 7午後: 総合スコア実装 + **定数調整（1-2時間）**

### 8.6 Day 8-9: API実装

**タスク:**
- [ ] FastAPI エンドポイント実装
- [ ] Pydanticスキーマ定義
- [ ] データベースクエリ実装
- [ ] レスポンス整形
- [ ] エラーハンドリング
- [ ] Postmanでテスト

**成果物:**
- `routers/scores.py`
- 動作確認済みAPI

### 8.7 Day 10-12: フロントエンド実装

**タスク:**
- [ ] Next.jsプロジェクト作成
- [ ] スコア表示ページ実装
- [ ] APIクライアント実装
- [ ] バーチャート実装
- [ ] Tailwind CSSでスタイリング
- [ ] レスポンシブ対応（基本のみ）

**成果物:**
- `/stocks/[code]` ページ
- 動作確認済みUI

### 8.8 Day 13-14: テスト・デモ準備

**タスク:**
- [ ] 3銘柄すべてで動作確認
- [ ] スコアの妥当性チェック
- [ ] UIのバグ修正
- [ ] README作成
- [ ] デモ用スクリーンショット作成
- [ ] プレゼン資料作成

**成果物:**
- 完成版MVP
- デモ環境
- ドキュメント

---

## 9. 成功基準

### 9.1 必須要件（Must Have）

- [ ] 3銘柄のスコアが正常に計算される
- [ ] APIが正常にレスポンスを返す
- [ ] Web画面でスコアが表示される
- [ ] スコアが0-100の範囲内である
- [ ] ランク判定が正しく動作する

### 9.2 期待要件（Should Have）

- [ ] スコアが実際の株価パフォーマンスと相関している
- [ ] UIが直感的で分かりやすい
- [ ] 計算ロジックが透明で説明可能
- [ ] エラーが発生しない（3銘柄の範囲内）

### 9.3 検証方法

#### 定量的検証

| 検証項目 | 目標値 | 測定方法 |
|---------|--------|---------|
| API応答時間 | 500ms以内 | Postmanで計測 |
| スコア計算時間 | 100ms以内 | Pythonタイマーで計測 |
| エラー発生率 | 0% | 100回実行してエラーなし |

#### 定性的検証

1. **スコアの妥当性**
   - トヨタ（安定） → Value高、Growth中、Momentum中
   - ソニー（成長） → Value中、Growth高、Momentum高
   - SBG（ハイリスク） → Value低、Growth高、Momentum変動

2. **UI/UX**
   - 投資家3名にデモして理解度チェック
   - 「何を表しているか分かるか」質問
   - 改善点をヒアリング

---

## 10. 制約事項

### 10.1 技術的制約

- **対象銘柄数**: 3銘柄のみ（7203/6758/9984）
- **データ更新**: 手動実行（自動化なし）
- **スコア履歴**: 保存のみ（グラフ化なし）
- **認証**: なし（誰でもアクセス可能）
- **本番環境**: なし（ローカル実行のみ）

### 10.2 スコープ外

以下はMVP期間中は実装しない：

- 全銘柄対応（3,800銘柄）
- 複雑な補正ロジック（TDnet、PBR改善）
- ユーザー登録・認証
- ウォッチリスト機能
- アラート機能
- スクリーニング機能
- ランキング機能
- レート制限
- キャッシング
- ログ基盤
- 監視基盤
- CI/CD
- 本番デプロイ

### 10.3 既知の制限

1. **データ鮮度**
   - 手動更新のため、最新データでない可能性あり

2. **精度**
   - 簡易版のため、詳細な財務分析は未実装

3. **パフォーマンス**
   - 3銘柄のみのため、スケーラビリティ未検証

4. **セキュリティ**
   - 認証なしのため、本番環境では使用不可

---

## 付録A: Gemini指摘事項への対応

### A.1 市場平均スコアの保持

**指摘内容:**  
3銘柄それぞれの単体スコアだけでは「日本株全体の中でどうなのか」が見えにくい。

**対応策:**
1. `market_average_scores` テーブルを新設
2. 3銘柄の平均値を市場平均として計算・保存
3. APIレスポンスに `market_comparison` フィールドを追加
4. UI上で「市場平均: 52点」「差分: +26.5点」と表示

**効果:**
- スコアの相対的な強さが瞬時に伝わる
- 投資家にとっての価値が明確になる
- デモ時の説得力が大幅に向上

### A.2 データ取得の冪等性確保

**指摘内容:**  
手動実行スクリプトで同じ日に2回実行するとデータが重複する恐れがある。

**対応策:**
1. PostgreSQLの `ON CONFLICT` 句を使用したUPSERT処理
2. `UNIQUE(stock_code, price_date)` 制約を活用
3. 既存データは更新、新規データは挿入

**効果:**
- データの修正や再取得が何度でも安全
- Day 4のテスト工数が削減
- データの不整合が発生しない

**実装コード:**
```sql
INSERT INTO stock_prices (stock_code, price_date, close_price, volume)
VALUES (%s, %s, %s, %s)
ON CONFLICT (stock_code, price_date)
DO UPDATE SET
    close_price = EXCLUDED.close_price,
    volume = EXCLUDED.volume,
    updated_at = CURRENT_TIMESTAMP
```

### A.3 Growthスコアの例外処理具体化

**指摘内容:**  
EDINETからのデータ取得で決算期の違いやデータ欠損が必ず発生する。

**対応策:**
1. データ欠損時は `50点（中立）` を返す
2. 例外を発生させず、必ず数値を返す
3. 他のカテゴリスコアの計算を継続

**効果:**
- エラーで処理が止まることを防ぐ
- 3銘柄以外のテストへの移行が容易
- システムの堅牢性が向上

**実装コード:**
```python
def calculate_growth_score(current_revenue, previous_revenue):
    # データ欠損時は中立値を返す
    if current_revenue is None or previous_revenue is None:
        return 50.0
    
    if previous_revenue == 0:
        return 50.0
    
    # ... 通常の計算
```

### A.4 スコア定数の微調整時間確保

**指摘内容:**  
計算式の定数が「仮」の値の場合、期待するランクになるよう調整する時間が必要。

**対応策:**
1. Day 7午後に1-2時間の調整時間を確保
2. 期待スコア範囲を明記（トヨタ: B+、ソニー: A、SBG: C+）
3. 調整手順とサンプルコードを追加

**効果:**
- デモの説得力が一層向上
- スコアの妥当性を事前検証
- 投資家へのフィードバックが的確

**期待スコア:**
```
トヨタ: 70-80点（B+）安定企業らしいバランス
ソニー: 75-85点（A）成長性の高さ
SBG: 55-65点（C+）ハイリスク・ハイリターン
```

---

## 付録B: データソース

### A.1 株価データ

**ソース:** Yahoo Finance  
**取得方法:** yfinance ライブラリ  
**取得データ:**
- 日付
- 始値、高値、安値、終値
- 出来高

**サンプルコード:**
```python
import yfinance as yf

# トヨタ自動車の株価取得
ticker = yf.Ticker("7203.T")
hist = ticker.history(period="1mo")
```

### A.2 財務データ

**ソース:** EDINET API または 手動収集  
**取得データ:**
- 売上高（当期・前期）
- EPS（1株当たり利益）
- BPS（1株当たり純資産）
- 年間配当

**MVPでは手動収集を許容**

---

## 付録B: 参考資料

### B.1 類似サービス

- **米国株**: Seeking Alpha、Zacks Rank
- **日本株**: 株探、バフェット・コード（スコアリングなし）

### B.2 技術参考

- FastAPI公式: https://fastapi.tiangolo.com/
- Next.js公式: https://nextjs.org/
- yfinance: https://github.com/ranaroussi/yfinance

---

## 変更履歴

| Version | 日付 | 変更内容 | 作成者 |
|---------|------|---------|--------|
| 1.0.0 | 2026-02-01 | 初版作成 | ZenJP Team |
| 1.1.0 | 2026-02-01 | Gemini改善提案を反映<br>- 市場平均スコア（50点）の追加<br>- データ取得の冪等性を明記<br>- Growthスコア例外処理の具体化<br>- スコア定数調整プロセスの追加 | ZenJP Team |

**v1.1.0 の主な変更:**
1. **市場平均スコアの追加**
   - 全カテゴリで50点を市場平均と定義
   - APIレスポンスに市場平均との比較を追加
   - UI画面に市場平均との差分表示を追加

2. **データ取得の冪等性保証**
   - UPSERT処理の実装方法を明記
   - PostgreSQLの `ON CONFLICT` 句を使用
   - サンプルコード追加

3. **Growthスコアの例外処理明確化**
   - データ欠損時は50点（中立）を返す
   - 例外処理の実装コード追加
   - 処理継続の重要性を明記

4. **スコア定数の調整時間確保**
   - Day 6-7に1-2時間の調整時間を追加
   - 期待スコア範囲を明記
   - 調整手順とサンプルを追加

---

## 付録: Gemini改善提案への対応

### 改善提案1: 市場平均スコアの保持 ✅

**提案内容:** スコアの相対的価値を示すため、市場平均スコアを定義する。

**対応:** 2.3節に追加。全カテゴリで50点を市場平均と定義し、APIとUIに反映。

---

### 改善提案2: データ取得の冪等性確保 ✅

**提案内容:** 同じスクリプトを複数回実行してもデータが重複しないようUPSERT処理を実装。

**対応:** FR-D01に冪等性保証を明記。PostgreSQLの `ON CONFLICT ... DO UPDATE` を使用。

---

### 改善提案3: Growthスコア例外処理の具体化 ✅

**提案内容:** データ欠損時のスコアを明確に定義し、エラーで止まらないようにする。

**対応:** FR-S02に詳細化。データ欠損時は中立スコア（50点）を返す仕様に変更。

---

### 確認事項への回答: スコア計算式の検証状態 ✅

**質問:** 計算式は実データで検証済みか？

**回答:** v1.0.0時点では理論値。Day 6-7で実データによる調整時間（1-2時間）を確保。

**調整方針:** 期待スコア（トヨタ70-80点、ソニー75-85点、SBG55-70点）に合わせて定数を微調整。

---

## 承認

| 役割 | 氏名 | 承認日 | 署名 |
|------|------|--------|------|
| プロダクトオーナー | | | |
| 技術リード | | | |
| デザイナー | | | |

---

**この要件定義書（v1.1.0）に基づき、2週間でZenJP MVPを完成させます。**

**次のステップ:** 技術設計書の作成
