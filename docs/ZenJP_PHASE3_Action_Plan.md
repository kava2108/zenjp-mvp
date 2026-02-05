# ZenJP MVP PHASE3 実装アクション詳細計画書

**対象フェーズ:** PHASE3 スコア計算・定数調整  
**期間:** Day 6-7（2日間、合計18時間）  
**担当:** 末告さん（指示・確認・承認）  
**実装:** GitHub Copilot（実行）  
**作成日:** 2026年2月8日

---

## 📋 目次

1. [PHASE3概要](#1-phase3概要)
2. [事前準備](#2-事前準備)
3. [Day 6: スコア計算実装](#3-day-6-スコア計算実装)
4. [Day 7: スコア定数調整](#4-day-7-スコア定数調整)
5. [完了確認](#5-完了確認)
6. [トラブルシューティング](#6-トラブルシューティング)
7. [付録](#7-付録)

---

## 1. PHASE3概要

### 1.1 達成目標

**Day 6終了時:**
- ✅ Value/Growth/Momentumスコア計算関数完成
- ✅ RSI（14日）計算実装
- ✅ 総合スコア計算・ランク判定実装
- ✅ `calculate_scores.py` スクリプト完成
- ✅ 3銘柄のスコアが算出される（初期値）

**Day 7終了時:**
- ✅ AIロールプレイレビュー完了（バリュー・グロース投資家視点）
- ✅ スコア定数が期待値に調整済み
- ✅ 3銘柄のスコアが納得できる範囲内
- ✅ 定数調整の根拠が文書化されている
- ✅ daily_scoresテーブルに最終スコアが保存

### 1.2 スコアリングロジック概要

```
総合スコア = Value(40%) + Growth(30%) + Momentum(30%)

■ Valueスコア（配当重視のバリュー投資）
  - PERスコア: PER基準値15倍を中心に評価
  - PBRスコア: PBR 1.0以下で満点
  - 配当スコア: 配当利回り × 係数20

■ Growthスコア（成長性評価）
  - 売上成長率: 前年比20%以上で満点
  - MVP版は固定値（将来は実データ）

■ Momentumスコア（需給・テクニカル）
  - RSI: 40-70の範囲で高評価
  - 出来高変化率: 直近7日平均 vs 過去30日平均

総合スコアのランク判定:
  A  : 80点以上
  B+ : 70-79点
  B  : 60-69点
  C+ : 50-59点
  C  : 40-49点
  D  : 40点未満
```

### 1.3 成果物

```
zenjp-mvp/
├── backend/
│   ├── scripts/
│   │   ├── calculate_scores.py        # スコア計算メインスクリプト
│   │   ├── constants.py               # スコア計算定数（調整対象）
│   │   └── score_analysis.py          # スコア分析ツール
│   └── app/
│       └── services/
│           └── score_calculator.py    # スコア計算ロジック（関数化）
├── docs/
│   ├── scoring_logic.md               # スコアリングロジック説明書
│   └── constant_adjustment_log.md     # 定数調整履歴
└── database/
    └── daily_scores: 3件（最終スコア）
```

---

## 2. 事前準備

### 2.1 PHASE2完了確認

**必須チェック:**

```bash
# プロジェクトディレクトリに移動
cd ~/zenjp-mvp

# Docker起動確認
docker-compose ps

# 株価データ確認
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT stock_code, COUNT(*) FROM stock_prices GROUP BY stock_code;"

# 期待される出力: 各銘柄30件程度

# 財務データ確認
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT stock_code, eps, bps, dividend FROM stock_financials;"

# 期待される出力: 3件（すべてNULLなし）
```

**すべてOKならPHASE3開始可能**

### 2.2 必要なPythonライブラリ確認

```bash
# requirements.txtに以下が含まれているか確認
cat backend/requirements.txt
```

**必要なライブラリ:**
- pandas==2.1.3
- numpy==1.26.2
- sqlalchemy==2.0.23
- psycopg2-binary==2.9.9

**もし不足していれば追加:**
```bash
echo "pandas==2.1.3" >> backend/requirements.txt
echo "numpy==1.26.2" >> backend/requirements.txt
docker-compose exec backend pip install pandas numpy
```

---

## 3. Day 6: スコア計算実装

**所要時間:** 8時間  
**目標:** スコア計算ロジック完成、3銘柄のスコア算出

---

### ステップ1: スコア計算定数ファイル作成（20分）

#### アクション1-1: constants.py作成

**GitHub Copilotへの指示:**

```python
# ファイル名: backend/scripts/constants.py

# Copilotに以下を指示:
# スコア計算に使用する定数を定義するファイルを作成してください
#
# === 定数の構成 ===
#
# ## Valueスコア定数
# # PER（株価収益率）
# PER_BASELINE = 15.0          # 基準値（15倍で50点）
# PER_PERFECT_THRESHOLD = 8.0  # 完璧な値（これ以下で100点）
# PER_MAX_THRESHOLD = 30.0     # 最大値（これ以上で0点）
#
# # PBR（株価純資産倍率）
# PBR_PERFECT_THRESHOLD = 1.0  # 完璧な値（1.0以下で100点）
# PBR_MAX_THRESHOLD = 3.0      # 最大値（これ以上で0点）
#
# # 配当利回り
# DIVIDEND_MULTIPLIER = 20.0   # 配当利回り × この値 = スコア
# DIVIDEND_MAX_SCORE = 100.0   # 配当スコアの上限
#
# ## Growthスコア定数
# GROWTH_PERFECT_THRESHOLD = 20.0  # 20%以上で100点
# GROWTH_BASELINE = 10.0           # 10%で50点
# GROWTH_MIN_THRESHOLD = -5.0      # -5%以下で0点
#
# ## Momentumスコア定数
# # RSI（相対力指数）
# RSI_IDEAL_MIN = 40.0         # 理想範囲の下限
# RSI_IDEAL_MAX = 70.0         # 理想範囲の上限
# RSI_OVERSOLD = 30.0          # 売られすぎ
# RSI_OVERBOUGHT = 70.0        # 買われすぎ
#
# # 出来高変化率
# VOLUME_INCREASE_MULTIPLIER = 10.0  # 出来高増加 × この値 = スコア
# VOLUME_MAX_SCORE = 100.0           # 出来高スコアの上限
#
# ## 総合スコア重み
# WEIGHT_VALUE = 0.4      # Valueスコアの重み（40%）
# WEIGHT_GROWTH = 0.3     # Growthスコアの重み（30%）
# WEIGHT_MOMENTUM = 0.3   # Momentumスコアの重み（30%）
#
# ## ランク判定閾値
# RANK_THRESHOLDS = {
#     'A': 80.0,
#     'B+': 70.0,
#     'B': 60.0,
#     'C+': 50.0,
#     'C': 40.0,
#     'D': 0.0
# }
#
# ## 市場平均（初期値）
# MARKET_AVERAGE_TOTAL = 50.0
# MARKET_AVERAGE_VALUE = 50.0
# MARKET_AVERAGE_GROWTH = 50.0
# MARKET_AVERAGE_MOMENTUM = 50.0
```

**確認:**
```bash
cat backend/scripts/constants.py
docker-compose exec backend python -c "from scripts.constants import *; print(PER_BASELINE)"
# 15.0
```

---

### ステップ2: Valueスコア計算実装（90分）

#### アクション2-1: calculate_value_score関数作成

**GitHub Copilotへの指示:**

```python
# ファイル名: backend/scripts/score_calculator.py

# Copilotに以下を指示:
# Valueスコア（PER・PBR・配当）を計算する関数を作成してください
#
# === 関数仕様 ===
#
# def calculate_per_score(per: float) -> float:
#     """
#     PERスコアを計算（0-100点）
#     
#     ロジック:
#     - PER <= PER_PERFECT_THRESHOLD (8.0) → 100点
#     - PER == PER_BASELINE (15.0) → 50点
#     - PER >= PER_MAX_THRESHOLD (30.0) → 0点
#     - 上記の間は線形補間
#     
#     Args:
#         per: PER（株価収益率）
#     
#     Returns:
#         スコア（0-100）
#     """
#     from scripts.constants import PER_BASELINE, PER_PERFECT_THRESHOLD, PER_MAX_THRESHOLD
#     
#     if per <= 0:
#         return 0.0
#     
#     if per <= PER_PERFECT_THRESHOLD:
#         return 100.0
#     elif per <= PER_BASELINE:
#         # 8 → 100点、15 → 50点の線形補間
#         return 100.0 - ((per - PER_PERFECT_THRESHOLD) / 
#                         (PER_BASELINE - PER_PERFECT_THRESHOLD) * 50.0)
#     elif per <= PER_MAX_THRESHOLD:
#         # 15 → 50点、30 → 0点の線形補間
#         return 50.0 - ((per - PER_BASELINE) / 
#                        (PER_MAX_THRESHOLD - PER_BASELINE) * 50.0)
#     else:
#         return 0.0
#
# def calculate_pbr_score(pbr: float) -> float:
#     """
#     PBRスコアを計算（0-100点）
#     
#     ロジック:
#     - PBR <= PBR_PERFECT_THRESHOLD (1.0) → 100点
#     - PBR >= PBR_MAX_THRESHOLD (3.0) → 0点
#     - 上記の間は線形補間
#     
#     Args:
#         pbr: PBR（株価純資産倍率）
#     
#     Returns:
#         スコア（0-100）
#     """
#     from scripts.constants import PBR_PERFECT_THRESHOLD, PBR_MAX_THRESHOLD
#     
#     if pbr <= 0:
#         return 0.0
#     
#     if pbr <= PBR_PERFECT_THRESHOLD:
#         return 100.0
#     elif pbr <= PBR_MAX_THRESHOLD:
#         # 1.0 → 100点、3.0 → 0点の線形補間
#         return 100.0 - ((pbr - PBR_PERFECT_THRESHOLD) / 
#                         (PBR_MAX_THRESHOLD - PBR_PERFECT_THRESHOLD) * 100.0)
#     else:
#         return 0.0
#
# def calculate_dividend_score(dividend_yield: float) -> float:
#     """
#     配当スコアを計算（0-100点）
#     
#     ロジック:
#     - スコア = 配当利回り(%) × DIVIDEND_MULTIPLIER (20.0)
#     - 上限: DIVIDEND_MAX_SCORE (100.0)
#     
#     Args:
#         dividend_yield: 配当利回り（%）
#     
#     Returns:
#         スコア（0-100）
#     """
#     from scripts.constants import DIVIDEND_MULTIPLIER, DIVIDEND_MAX_SCORE
#     
#     score = dividend_yield * DIVIDEND_MULTIPLIER
#     return min(score, DIVIDEND_MAX_SCORE)
#
# def calculate_value_score(per: float, pbr: float, dividend_yield: float) -> dict:
#     """
#     Valueスコアを計算（PER・PBR・配当の平均）
#     
#     Args:
#         per: PER（株価収益率）
#         pbr: PBR（株価純資産倍率）
#         dividend_yield: 配当利回り（%）
#     
#     Returns:
#         {
#             'value_score': 総合Valueスコア（0-100）,
#             'per_score': PERスコア,
#             'pbr_score': PBRスコア,
#             'dividend_score': 配当スコア
#         }
#     """
#     per_score = calculate_per_score(per)
#     pbr_score = calculate_pbr_score(pbr)
#     dividend_score = calculate_dividend_score(dividend_yield)
#     
#     # 3つの平均
#     value_score = (per_score + pbr_score + dividend_score) / 3.0
#     
#     return {
#         'value_score': round(value_score, 2),
#         'per_score': round(per_score, 2),
#         'pbr_score': round(pbr_score, 2),
#         'dividend_score': round(dividend_score, 2)
#     }
#
# === インポート ===
# from scripts.constants import (
#     PER_BASELINE, PER_PERFECT_THRESHOLD, PER_MAX_THRESHOLD,
#     PBR_PERFECT_THRESHOLD, PBR_MAX_THRESHOLD,
#     DIVIDEND_MULTIPLIER, DIVIDEND_MAX_SCORE
# )
```

**確認:**
```bash
cat backend/scripts/score_calculator.py
docker-compose exec backend python -m py_compile scripts/score_calculator.py
```

---

#### アクション2-2: Valueスコアのテスト

**テストスクリプト作成:**

```bash
# Pythonインタラクティブシェルでテスト
docker-compose exec backend python
```

**テストコード:**
```python
import sys
sys.path.append('/app')

from scripts.score_calculator import calculate_value_score

# トヨタ（想定）
# 株価: 2900円、EPS: 186.67円、BPS: 1250.50円、配当: 280円
per = 2900 / 186.67  # 15.53
pbr = 2900 / 1250.50  # 2.32
dividend_yield = (280 / 2900) * 100  # 9.66%

result = calculate_value_score(per, pbr, dividend_yield)
print(f"Valueスコア: {result}")

# 期待される出力例:
# {
#   'value_score': 75.5,
#   'per_score': 49.2,
#   'pbr_score': 54.0,
#   'dividend_score': 100.0
# }

exit()
```

---

### ステップ3: Growthスコア計算実装（60分）

#### アクション3-1: calculate_growth_score関数作成

**GitHub Copilotへの指示:**

```python
# backend/scripts/score_calculator.py に追加

# Copilotに以下を指示:
# Growthスコア（売上成長率）を計算する関数を作成してください
#
# def calculate_growth_score(revenue_current: float, revenue_previous: float) -> dict:
#     """
#     Growthスコアを計算（売上成長率ベース）
#     
#     ロジック:
#     - 成長率 >= GROWTH_PERFECT_THRESHOLD (20%) → 100点
#     - 成長率 == GROWTH_BASELINE (10%) → 50点
#     - 成長率 <= GROWTH_MIN_THRESHOLD (-5%) → 0点
#     - 上記の間は線形補間
#     
#     Args:
#         revenue_current: 当期売上高（百万円）
#         revenue_previous: 前期売上高（百万円）
#     
#     Returns:
#         {
#             'growth_score': Growthスコア（0-100）,
#             'revenue_growth_rate': 売上成長率（%）
#         }
#     """
#     from scripts.constants import (
#         GROWTH_PERFECT_THRESHOLD, 
#         GROWTH_BASELINE, 
#         GROWTH_MIN_THRESHOLD
#     )
#     
#     if revenue_previous <= 0:
#         return {
#             'growth_score': 50.0,
#             'revenue_growth_rate': 0.0
#         }
#     
#     # 成長率計算（%）
#     growth_rate = ((revenue_current - revenue_previous) / revenue_previous) * 100
#     
#     # スコア計算
#     if growth_rate >= GROWTH_PERFECT_THRESHOLD:
#         score = 100.0
#     elif growth_rate >= GROWTH_BASELINE:
#         # 10% → 50点、20% → 100点の線形補間
#         score = 50.0 + ((growth_rate - GROWTH_BASELINE) / 
#                         (GROWTH_PERFECT_THRESHOLD - GROWTH_BASELINE) * 50.0)
#     elif growth_rate >= GROWTH_MIN_THRESHOLD:
#         # -5% → 0点、10% → 50点の線形補間
#         score = ((growth_rate - GROWTH_MIN_THRESHOLD) / 
#                  (GROWTH_BASELINE - GROWTH_MIN_THRESHOLD) * 50.0)
#     else:
#         score = 0.0
#     
#     return {
#         'growth_score': round(score, 2),
#         'revenue_growth_rate': round(growth_rate, 2)
#     }
```

---

### ステップ4: RSI計算実装（60分）

#### アクション4-1: calculate_rsi関数作成

**GitHub Copilotへの指示:**

```python
# backend/scripts/score_calculator.py に追加

# Copilotに以下を指示:
# RSI（相対力指数、14日）を計算する関数を作成してください
#
# def calculate_rsi(prices: list[float], period: int = 14) -> float:
#     """
#     RSI（Relative Strength Index）を計算
#     
#     ロジック:
#     1. 各日の価格変化を計算
#     2. 上昇日の平均と下落日の平均を算出
#     3. RS = 上昇平均 / 下落平均
#     4. RSI = 100 - (100 / (1 + RS))
#     
#     Args:
#         prices: 株価のリスト（古い順）
#         period: RSI計算期間（デフォルト14日）
#     
#     Returns:
#         RSI値（0-100）
#     """
#     import numpy as np
#     
#     if len(prices) < period + 1:
#         return 50.0  # デフォルト値
#     
#     # 価格変化を計算
#     deltas = np.diff(prices)
#     
#     # 上昇と下落を分離
#     gains = np.where(deltas > 0, deltas, 0)
#     losses = np.where(deltas < 0, -deltas, 0)
#     
#     # 平均を計算（最初はSMA、その後はEMA）
#     avg_gain = np.mean(gains[:period])
#     avg_loss = np.mean(losses[:period])
#     
#     # EMAで更新
#     for i in range(period, len(gains)):
#         avg_gain = (avg_gain * (period - 1) + gains[i]) / period
#         avg_loss = (avg_loss * (period - 1) + losses[i]) / period
#     
#     # RSI計算
#     if avg_loss == 0:
#         return 100.0
#     
#     rs = avg_gain / avg_loss
#     rsi = 100 - (100 / (1 + rs))
#     
#     return round(rsi, 2)
```

**確認:**
```bash
docker-compose exec backend python -c "
from scripts.score_calculator import calculate_rsi
prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 111, 110, 112, 114, 113]
rsi = calculate_rsi(prices)
print(f'RSI: {rsi}')
"
```

---

### ステップ5: Momentumスコア計算実装（60分）

#### アクション5-1: calculate_momentum_score関数作成

**GitHub Copilotへの指示:**

```python
# backend/scripts/score_calculator.py に追加

# Copilotに以下を指示:
# Momentumスコア（RSI・出来高変化率）を計算する関数を作成してください
#
# def calculate_rsi_score(rsi: float) -> float:
#     """
#     RSIスコアを計算（0-100点）
#     
#     ロジック:
#     - RSI_IDEAL_MIN (40) ≤ RSI ≤ RSI_IDEAL_MAX (70) → 100点
#     - RSI < RSI_OVERSOLD (30) → 低評価
#     - RSI > RSI_OVERBOUGHT (70) → 低評価
#     
#     Args:
#         rsi: RSI値（0-100）
#     
#     Returns:
#         スコア（0-100）
#     """
#     from scripts.constants import RSI_IDEAL_MIN, RSI_IDEAL_MAX, RSI_OVERSOLD, RSI_OVERBOUGHT
#     
#     if RSI_IDEAL_MIN <= rsi <= RSI_IDEAL_MAX:
#         return 100.0
#     elif rsi < RSI_IDEAL_MIN:
#         # 売られすぎ（30未満は低評価）
#         if rsi < RSI_OVERSOLD:
#             return 30.0
#         else:
#             # 30-40の範囲は30点-100点
#             return 30.0 + ((rsi - RSI_OVERSOLD) / (RSI_IDEAL_MIN - RSI_OVERSOLD) * 70.0)
#     else:
#         # 買われすぎ（70超は低評価）
#         if rsi > RSI_OVERBOUGHT:
#             return 100.0 - ((rsi - RSI_OVERBOUGHT) / (100 - RSI_OVERBOUGHT) * 70.0)
#         else:
#             return 100.0
#
# def calculate_volume_change_score(volume_recent: float, volume_past: float) -> float:
#     """
#     出来高変化スコアを計算（0-100点）
#     
#     ロジック:
#     - 変化率 = (直近7日平均 - 過去30日平均) / 過去30日平均 × 100
#     - スコア = 変化率 × VOLUME_INCREASE_MULTIPLIER (10.0)
#     - 上限: VOLUME_MAX_SCORE (100.0)
#     
#     Args:
#         volume_recent: 直近7日の平均出来高
#         volume_past: 過去30日の平均出来高
#     
#     Returns:
#         スコア（0-100）
#     """
#     from scripts.constants import VOLUME_INCREASE_MULTIPLIER, VOLUME_MAX_SCORE
#     
#     if volume_past <= 0:
#         return 50.0
#     
#     change_rate = ((volume_recent - volume_past) / volume_past) * 100
#     score = max(0, change_rate * VOLUME_INCREASE_MULTIPLIER)
#     
#     return min(score, VOLUME_MAX_SCORE)
#
# def calculate_momentum_score(rsi: float, volume_recent: float, volume_past: float) -> dict:
#     """
#     Momentumスコアを計算（RSI・出来高変化率の平均）
#     
#     Args:
#         rsi: RSI値（0-100）
#         volume_recent: 直近7日の平均出来高
#         volume_past: 過去30日の平均出来高
#     
#     Returns:
#         {
#             'momentum_score': 総合Momentumスコア（0-100）,
#             'rsi_score': RSIスコア,
#             'rsi': RSI値,
#             'volume_change_score': 出来高変化スコア,
#             'volume_change_rate': 出来高変化率（%）
#         }
#     """
#     rsi_score = calculate_rsi_score(rsi)
#     volume_change_score = calculate_volume_change_score(volume_recent, volume_past)
#     
#     # 2つの平均
#     momentum_score = (rsi_score + volume_change_score) / 2.0
#     
#     volume_change_rate = 0.0
#     if volume_past > 0:
#         volume_change_rate = ((volume_recent - volume_past) / volume_past) * 100
#     
#     return {
#         'momentum_score': round(momentum_score, 2),
#         'rsi_score': round(rsi_score, 2),
#         'rsi': round(rsi, 2),
#         'volume_change_score': round(volume_change_score, 2),
#         'volume_change_rate': round(volume_change_rate, 2)
#     }
```

---

### ステップ6: 総合スコア計算実装（30分）

#### アクション6-1: calculate_total_score関数作成

**GitHub Copilotへの指示:**

```python
# backend/scripts/score_calculator.py に追加

# Copilotに以下を指示:
# 総合スコア（Value・Growth・Momentumの加重平均）とランク判定を実装してください
#
# def calculate_total_score(value_score: float, growth_score: float, momentum_score: float) -> dict:
#     """
#     総合スコアを計算（加重平均）
#     
#     ロジック:
#     - 総合 = Value × 0.4 + Growth × 0.3 + Momentum × 0.3
#     
#     Args:
#         value_score: Valueスコア（0-100）
#         growth_score: Growthスコア（0-100）
#         momentum_score: Momentumスコア（0-100）
#     
#     Returns:
#         {
#             'total_score': 総合スコア（0-100）,
#             'rank': ランク（A/B+/B/C+/C/D）
#         }
#     """
#     from scripts.constants import WEIGHT_VALUE, WEIGHT_GROWTH, WEIGHT_MOMENTUM
#     
#     total_score = (
#         value_score * WEIGHT_VALUE +
#         growth_score * WEIGHT_GROWTH +
#         momentum_score * WEIGHT_MOMENTUM
#     )
#     
#     return {
#         'total_score': round(total_score, 2),
#         'rank': determine_rank(total_score)
#     }
#
# def determine_rank(score: float) -> str:
#     """
#     スコアからランクを判定
#     
#     Args:
#         score: 総合スコア（0-100）
#     
#     Returns:
#         ランク（A/B+/B/C+/C/D）
#     """
#     from scripts.constants import RANK_THRESHOLDS
#     
#     if score >= RANK_THRESHOLDS['A']:
#         return 'A'
#     elif score >= RANK_THRESHOLDS['B+']:
#         return 'B+'
#     elif score >= RANK_THRESHOLDS['B']:
#         return 'B'
#     elif score >= RANK_THRESHOLDS['C+']:
#         return 'C+'
#     elif score >= RANK_THRESHOLDS['C']:
#         return 'C'
#     else:
#         return 'D'
```

---

### ステップ7: メインスクリプト作成（90分）

#### アクション7-1: calculate_scores.py作成

**GitHub Copilotへの指示:**

```python
# ファイル名: backend/scripts/calculate_scores.py

# Copilotに以下を指示:
# 3銘柄のスコアを計算してdaily_scoresテーブルに保存するメインスクリプトを作成してください
#
# === 処理フロー ===
# 1. 各銘柄について最新の株価・財務データを取得
# 2. PER、PBR、配当利回りを計算
# 3. RSIを計算（直近30日の株価データ使用）
# 4. 出来高変化率を計算（直近7日 vs 過去30日）
# 5. Value/Growth/Momentumスコアを計算
# 6. 総合スコア・ランクを計算
# 7. daily_scoresテーブルにUPSERT
# 8. 計算詳細をJSONBのdetailsカラムに保存
#
# === 関数構成 ===
# def get_stock_data(stock_code: str, session) -> dict:
#     """
#     銘柄の最新データを取得
#     
#     Returns:
#         {
#             'stock_code': '7203',
#             'latest_price': 2900.0,
#             'eps': 186.67,
#             'bps': 1250.50,
#             'dividend': 280.0,
#             'revenue_current': 35000000,
#             'revenue_previous': 33500000,
#             'prices': [2850, 2870, ...],  # 直近30日
#             'volumes': [12345678, ...]     # 直近30日
#         }
#     """
#
# def calculate_stock_score(stock_code: str, session) -> dict:
#     """
#     1銘柄のスコアを計算
#     
#     Returns:
#         {
#             'stock_code': '7203',
#             'total_score': 75.5,
#             'rank': 'B+',
#             'value_score': 70.2,
#             'growth_score': 68.5,
#             'momentum_score': 85.3,
#             'details': {
#                 'per': 15.53,
#                 'per_score': 49.2,
#                 'pbr': 2.32,
#                 'pbr_score': 54.0,
#                 'dividend_yield': 9.66,
#                 'dividend_score': 100.0,
#                 'revenue_growth_rate': 4.48,
#                 'rsi': 55.3,
#                 'rsi_score': 100.0,
#                 'volume_change_rate': 12.5,
#                 'volume_change_score': 70.6
#             }
#         }
#     """
#
# def save_score(score_data: dict, session) -> None:
#     """
#     スコアをdaily_scoresテーブルに保存（UPSERT）
#     
#     SQL:
#     INSERT INTO daily_scores (
#         stock_code, score_date, total_score, rank,
#         value_score, growth_score, momentum_score, details
#     ) VALUES (...)
#     ON CONFLICT (stock_code, score_date)
#     DO UPDATE SET
#         total_score = EXCLUDED.total_score,
#         rank = EXCLUDED.rank,
#         value_score = EXCLUDED.value_score,
#         growth_score = EXCLUDED.growth_score,
#         momentum_score = EXCLUDED.momentum_score,
#         details = EXCLUDED.details
#     """
#
# def main():
#     """メイン処理"""
#     print("=" * 60)
#     print("スコア計算を開始します")
#     print("=" * 60)
#     
#     for stock_code in ['7203', '6758', '9984']:
#         print(f"\n[{stock_code}] スコア計算中...")
#         score = calculate_stock_score(stock_code, session)
#         save_score(score, session)
#         
#         print(f"  総合スコア: {score['total_score']}点")
#         print(f"  ランク: {score['rank']}")
#         print(f"  Value: {score['value_score']}点")
#         print(f"  Growth: {score['growth_score']}点")
#         print(f"  Momentum: {score['momentum_score']}点")
#     
#     session.commit()
#     
#     print("\n" + "=" * 60)
#     print("スコア計算が完了しました")
#     print("=" * 60)
#
# === インポート ===
# import sys
# sys.path.append('/app')
# from datetime import date
# from sqlalchemy import create_engine, text
# from sqlalchemy.orm import sessionmaker
# import os
# import json
# from scripts.score_calculator import (
#     calculate_value_score,
#     calculate_growth_score,
#     calculate_rsi,
#     calculate_momentum_score,
#     calculate_total_score
# )
```

**確認:**
```bash
cat backend/scripts/calculate_scores.py
docker-compose exec backend python -m py_compile scripts/calculate_scores.py
```

---

### ステップ8: 初回スコア計算実行（30分）

#### アクション8-1: スクリプト実行

**コマンド:**
```bash
docker-compose exec backend python scripts/calculate_scores.py
```

**期待される出力:**
```
============================================================
スコア計算を開始します
============================================================

[7203] スコア計算中...
  総合スコア: 75.5点
  ランク: B+
  Value: 70.2点
  Growth: 68.5点
  Momentum: 85.3点

[6758] スコア計算中...
  総合スコア: 78.3点
  ランク: B+
  Value: 65.4点
  Growth: 82.0点
  Momentum: 88.7点

[9984] スコア計算中...
  総合スコア: 62.8点
  ランク: B
  Value: 55.6点
  Growth: 72.5点
  Momentum: 64.2点

============================================================
スコア計算が完了しました
============================================================
```

---

#### アクション8-2: データベース確認

**件数確認:**
```bash
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT COUNT(*) FROM daily_scores;"
# → 3
```

**データ内容確認:**
```bash
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT stock_code, total_score, rank, value_score, growth_score, momentum_score 
   FROM daily_scores 
   ORDER BY total_score DESC;"
```

**期待される出力:**
```
 stock_code | total_score | rank | value_score | growth_score | momentum_score 
------------+-------------+------+-------------+--------------+----------------
 6758       |       78.30 | B+   |       65.40 |        82.00 |          88.70
 7203       |       75.50 | B+   |       70.20 |        68.50 |          85.30
 9984       |       62.80 | B    |       55.60 |        72.50 |          64.20
(3 rows)
```

---

### ステップ9: スコア分析ツール作成（30分）

#### アクション9-1: score_analysis.py作成

**GitHub Copilotへの指示:**

```python
# ファイル名: backend/scripts/score_analysis.py

# Copilotに以下を指示:
# 計算されたスコアを分析・表示するツールを作成してください
#
# === 機能 ===
# 1. 3銘柄のスコアをテーブル形式で表示
# 2. 各カテゴリスコアの比較
# 3. 詳細指標（PER、PBR、RSI等）の表示
#
# === 出力形式 ===
# ============================================================
# スコア分析レポート
# ============================================================
#
# ■ 総合スコアランキング
# 順位 | 銘柄コード | 銘柄名           | 総合スコア | ランク
# -----|-----------|-----------------|-----------|-------
#   1  |   6758    | ソニーグループ   |   78.30   |  B+
#   2  |   7203    | トヨタ自動車     |   75.50   |  B+
#   3  |   9984    | SBG             |   62.80   |  B
#
# ■ カテゴリ別スコア
# 銘柄     | Value  | Growth | Momentum
# ---------|--------|--------|----------
# 6758     |  65.40 |  82.00 |   88.70
# 7203     |  70.20 |  68.50 |   85.30
# 9984     |  55.60 |  72.50 |   64.20
#
# ■ 詳細指標（7203: トヨタ自動車）
# PER          : 15.53倍 → スコア: 49.2点
# PBR          : 2.32倍 → スコア: 54.0点
# 配当利回り   : 9.66% → スコア: 100.0点
# 売上成長率   : 4.48% → スコア: 68.5点
# RSI          : 55.3 → スコア: 100.0点
# 出来高変化率 : +12.5% → スコア: 70.6点
#
# ============================================================
```

**実行:**
```bash
docker-compose exec backend python scripts/score_analysis.py
```

---

### Day 6完了確認

#### チェックリスト

```bash
# 1. スクリプト存在確認
ls -l backend/scripts/constants.py
ls -l backend/scripts/score_calculator.py
ls -l backend/scripts/calculate_scores.py
ls -l backend/scripts/score_analysis.py

# 2. スコア計算実行確認
docker-compose exec backend python scripts/calculate_scores.py

# 3. データ確認
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT stock_code, total_score, rank FROM daily_scores ORDER BY total_score DESC;"

# 4. スコア範囲確認
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT MIN(total_score), MAX(total_score) FROM daily_scores;"
# → すべて0-100の範囲内

# 5. 分析ツール実行確認
docker-compose exec backend python scripts/score_analysis.py

# すべてOKなら
echo "✅ Day 6 完了！"
```

**成果物:**
- ✅ constants.py（定数定義）
- ✅ score_calculator.py（スコア計算関数）
- ✅ calculate_scores.py（メインスクリプト）
- ✅ score_analysis.py（分析ツール）
- ✅ daily_scoresテーブルに3件

---

## 4. Day 7: スコア定数調整

**所要時間:** 10時間  
**目標:** AIロールプレイレビュー → 定数調整 → 期待値達成

**🔥 最重要:** この日がMVPの価値を決定します！

---

### ステップ10: 期待スコア設定（30分）

#### アクション10-1: 期待スコア定義

**ファイル作成:**
```bash
cat > docs/target_scores.md << 'EOF'
# 期待スコア設定

## 目標

3銘柄が以下の範囲内に収まるように定数を調整する。

## 期待スコア

### 7203 トヨタ自動車
- **総合スコア:** 70-80点（B+ランク）
- **Valueスコア:** 75-85点（配当重視企業として高評価）
- **Growthスコア:** 60-70点（安定成長）
- **Momentumスコア:** 70-80点（安定需給）

**理由:**
- 安定配当企業として知られる
- 配当利回りが高い（9.66%）
- 成長率は安定的だが爆発的ではない

### 6758 ソニーグループ
- **総合スコア:** 75-85点（Aランク目標）
- **Valueスコア:** 65-75点（成長企業のためPER高め許容）
- **Growthスコア:** 80-90点（高成長企業）
- **Momentumスコア:** 75-85点（活発な需給）

**理由:**
- エンタメ・ゲーム・半導体で高成長
- 売上成長率が高い（7.14%）
- グローバル企業として評価高い

### 9984 ソフトバンクグループ
- **総合スコア:** 55-70点（Bランク）
- **Valueスコア:** 50-60点（投資会社のため指標に特殊性）
- **Growthスコア:** 70-80点（投資先成長を反映）
- **Momentumスコア:** 変動大（50-80点）

**理由:**
- 投資会社のためPER/PBRの解釈が特殊
- 成長率は投資先次第で変動
- ボラティリティが高い
EOF
```

**確認:**
```bash
cat docs/target_scores.md
```

---

### ステップ11: 初回スコア分析（60分）

#### アクション11-1: 現在のスコアを分析

**実行:**
```bash
docker-compose exec backend python scripts/score_analysis.py > current_scores.txt
cat current_scores.txt
```

**分析項目:**
1. **総合スコアが期待値範囲内か？**
   - トヨタ: 70-80点期待 → 実際: ？
   - ソニー: 75-85点期待 → 実際: ？
   - SBG: 55-70点期待 → 実際: ？

2. **各カテゴリスコアが期待値範囲内か？**
   - Valueスコアが高すぎる/低すぎる銘柄は？
   - Growthスコアが期待と乖離している銘柄は？

3. **詳細指標の妥当性**
   - PERスコアが適切か？
   - 配当スコアが納得できるか？
   - RSIスコアが合理的か？

---

#### アクション11-2: ギャップ分析表作成

**ファイル作成:**
```bash
cat > docs/score_gap_analysis.md << 'EOF'
# スコアギャップ分析

## 現在のスコア vs 期待スコア

### 7203 トヨタ自動車
| 項目 | 期待値 | 現在値 | 差分 | 評価 |
|------|--------|--------|------|------|
| 総合 | 70-80 | XX.X | ±XX | ？ |
| Value | 75-85 | XX.X | ±XX | ？ |
| Growth | 60-70 | XX.X | ±XX | ？ |
| Momentum | 70-80 | XX.X | ±XX | ？ |

### 6758 ソニーグループ
| 項目 | 期待値 | 現在値 | 差分 | 評価 |
|------|--------|--------|------|------|
| 総合 | 75-85 | XX.X | ±XX | ？ |
| Value | 65-75 | XX.X | ±XX | ？ |
| Growth | 80-90 | XX.X | ±XX | ？ |
| Momentum | 75-85 | XX.X | ±XX | ？ |

### 9984 ソフトバンクグループ
| 項目 | 期待値 | 現在値 | 差分 | 評価 |
|------|--------|--------|------|------|
| 総合 | 55-70 | XX.X | ±XX | ？ |
| Value | 50-60 | XX.X | ±XX | ？ |
| Growth | 70-80 | XX.X | ±XX | ？ |
| Momentum | 50-80 | XX.X | ±XX | ？ |

## 調整が必要な定数

### 優先度高
1. **[定数名]**: 現在値 XX → 調整後 YY
   - 理由: ...
   - 影響: トヨタのValueスコアが+10点

### 優先度中
...

### 優先度低
...
EOF
```

**手動で現在値を記入:**
```bash
# score_analysis.pyの出力を見ながら、
# docs/score_gap_analysis.md を手動更新
```

---

### ステップ12: AIロールプレイレビュー（90分）🤖

**🔥 Gemini提案・プロンプト#4, #5の活用**

#### アクション12-1: バリュー投資家視点でのレビュー

**Claude/ChatGPTに以下のプロンプトを入力:**

```
あなたはバリュー投資を重視する投資家です。
以下のスコアリング結果を見て、指摘してください。

【トヨタ自動車（7203）】
- PER: 15.53倍 → PERスコア: XX点
- PBR: 2.32倍 → PBRスコア: XX点
- 配当利回り: 9.66% → 配当スコア: 100点
→ Valueスコア総合: XX点

【ソニーグループ（6758）】
- PER: 15.88倍 → PERスコア: XX点
- PBR: 4.22倍 → PBRスコア: XX点
- 配当利回り: 0.44% → 配当スコア: XX点
→ Valueスコア総合: XX点

【ソフトバンクグループ（9984）】
- PER: 17.12倍 → PERスコア: XX点
- PBR: 1.24倍 → PBRスコア: XX点
- 配当利回り: 1.19% → 配当スコア: XX点
→ Valueスコア総合: XX点

質問:
1. このスコアは妥当ですか？
2. トヨタは安定配当企業として知られていますが、配当スコアが100点なのに総合Valueスコアが低い場合、PER/PBRの重み付けが強すぎませんか？
3. PER基準値（現在15倍）は日本市場に対して適切ですか？
4. どの定数をどう調整すべきですか？
```

**AIの回答を記録:**
```bash
cat > docs/ai_review_value.md << 'EOF'
# バリュー投資家視点でのAIレビュー

## 指摘事項

[AIの回答をここに貼り付け]

## 推奨される調整

1. PER_BASELINE: 15.0 → XX（理由: ...）
2. DIVIDEND_MULTIPLIER: 20.0 → XX（理由: ...）
3. ...
EOF
```

---

#### アクション12-2: グロース投資家視点でのレビュー

**Claude/ChatGPTに以下のプロンプトを入力:**

```
あなたはグロース投資を重視する投資家です。
以下のスコアリング結果を見て、指摘してください。

【ソニーグループ（6758）】
- 売上成長率: 7.14% → Growthスコア: XX点
- RSI: XX → Momentumスコア: XX点

この企業は、エンタメ・ゲーム・半導体で高成長していますが、
Growthスコアが70点未満の場合、低すぎませんか？

質問:
1. 売上成長率7.14%は、成長企業として妥当な評価を受けていますか？
2. GROWTH_BASELINE（現在10%）は高すぎませんか？
3. GROWTH_PERFECT_THRESHOLD（現在20%）は現実的ですか？
4. どの定数をどう調整すべきですか？
```

**AIの回答を記録:**
```bash
cat > docs/ai_review_growth.md << 'EOF'
# グロース投資家視点でのAIレビュー

## 指摘事項

[AIの回答をここに貼り付け]

## 推奨される調整

1. GROWTH_BASELINE: 10.0 → XX（理由: ...）
2. GROWTH_PERFECT_THRESHOLD: 20.0 → XX（理由: ...）
3. ...
EOF
```

---

### ステップ13: 定数調整実施（120分）

#### アクション13-1: 調整計画作成

**AIレビューを元に調整計画を立てる:**

```bash
cat > docs/adjustment_plan.md << 'EOF'
# 定数調整計画

## 調整ラウンド1

### PER関連
- PER_BASELINE: 15.0 → 18.0
  - 理由: 日本市場の平均PERは18倍程度
  - 影響: トヨタのPERスコアが+XX点

### 配当関連
- DIVIDEND_MULTIPLIER: 20.0 → 15.0
  - 理由: 配当スコアの影響が強すぎる
  - 影響: トヨタの配当スコアが100点→75点

### 成長率関連
- GROWTH_BASELINE: 10.0 → 5.0
  - 理由: 安定成長企業を過小評価しない
  - 影響: トヨタのGrowthスコアが+XX点

## 期待される結果

### トヨタ（調整後）
- Valueスコア: XX点 → 75-85点範囲内
- Growthスコア: XX点 → 60-70点範囲内
- 総合スコア: XX点 → 70-80点範囲内

### ソニー（調整後）
- Valueスコア: XX点 → 65-75点範囲内
- Growthスコア: XX点 → 80-90点範囲内
- 総合スコア: XX点 → 75-85点範囲内

### SBG（調整後）
- Valueスコア: XX点 → 50-60点範囲内
- Growthスコア: XX点 → 70-80点範囲内
- 総合スコア: XX点 → 55-70点範囲内
EOF
```

---

#### アクション13-2: constants.py更新（ラウンド1）

**手動編集:**
```bash
# backend/scripts/constants.py を開いて調整
# 調整計画に基づいて定数を変更

# 例:
# PER_BASELINE = 18.0  # 15.0 → 18.0に変更
# DIVIDEND_MULTIPLIER = 15.0  # 20.0 → 15.0に変更
# GROWTH_BASELINE = 5.0  # 10.0 → 5.0に変更
```

---

#### アクション13-3: スコア再計算（ラウンド1）

**コマンド:**
```bash
# スコア再計算
docker-compose exec backend python scripts/calculate_scores.py

# 結果確認
docker-compose exec backend python scripts/score_analysis.py
```

**期待値との比較:**
```bash
# 手動で比較
# - トヨタ: 70-80点範囲内か？
# - ソニー: 75-85点範囲内か？
# - SBG: 55-70点範囲内か？
```

---

#### アクション13-4: 追加調整（ラウンド2-3）

**まだ期待値に達していない場合:**

```bash
# 1. さらなる調整計画作成
cat >> docs/adjustment_plan.md << 'EOF'

## 調整ラウンド2

### [調整する定数]
- [定数名]: XX → YY
  - 理由: ...
  - 期待される影響: ...
EOF

# 2. constants.py更新

# 3. 再計算
docker-compose exec backend python scripts/calculate_scores.py

# 4. 確認
docker-compose exec backend python scripts/score_analysis.py

# 5. 必要なら繰り返し（最大3-4ラウンド）
```

---

### ステップ14: 納得感チェック（90分）

#### アクション14-1: 人間の最終判断

**3銘柄のスコアを見て、以下を自問:**

```
1. トヨタのスコアは納得できるか？
   - 安定配当企業として適切に評価されているか？
   - 成長性が過小評価されていないか？

2. ソニーのスコアは納得できるか？
   - 成長企業として高評価されているか？
   - Valueスコアが低すぎないか？

3. SBGのスコアは納得できるか？
   - 投資会社の特殊性が反映されているか？
   - ボラティリティが適切に評価されているか？

4. 3銘柄の順位は妥当か？
   - 期待: ソニー > トヨタ > SBG
   - 実際: ？

5. スコア差は適切か？
   - 上位と下位で明確な差があるか？
   - 差が大きすぎないか？
```

---

#### アクション14-2: 最終調整

**納得できない場合:**

```bash
# 微調整を実施
# constants.py を開いて±5%程度の微調整

# 再計算
docker-compose exec backend python scripts/calculate_scores.py

# 確認
docker-compose exec backend python scripts/score_analysis.py

# 納得できるまで繰り返し
```

---

### ステップ15: 定数記録（30分）

#### アクション15-1: 最終定数を記録

**コマンド:**
```bash
# 最終的な定数値を記録
cat backend/scripts/constants.py > docs/final_constants_backup.py

# 定数一覧を作成
cat > docs/final_constants.md << 'EOF'
# 最終調整済み定数一覧

## Valueスコア定数

| 定数名 | 初期値 | 最終値 | 調整理由 |
|--------|--------|--------|---------|
| PER_BASELINE | 15.0 | 18.0 | 日本市場平均に合わせた |
| PER_PERFECT_THRESHOLD | 8.0 | 8.0 | 変更なし |
| PER_MAX_THRESHOLD | 30.0 | 30.0 | 変更なし |
| PBR_PERFECT_THRESHOLD | 1.0 | 1.0 | 変更なし |
| PBR_MAX_THRESHOLD | 3.0 | 3.0 | 変更なし |
| DIVIDEND_MULTIPLIER | 20.0 | 15.0 | 配当の影響を適正化 |

## Growthスコア定数

| 定数名 | 初期値 | 最終値 | 調整理由 |
|--------|--------|--------|---------|
| GROWTH_PERFECT_THRESHOLD | 20.0 | 20.0 | 変更なし |
| GROWTH_BASELINE | 10.0 | 5.0 | 安定成長を評価 |
| GROWTH_MIN_THRESHOLD | -5.0 | -5.0 | 変更なし |

## Momentumスコア定数

| 定数名 | 初期値 | 最終値 | 調整理由 |
|--------|--------|--------|---------|
| RSI_IDEAL_MIN | 40.0 | 40.0 | 変更なし |
| RSI_IDEAL_MAX | 70.0 | 70.0 | 変更なし |
| VOLUME_INCREASE_MULTIPLIER | 10.0 | 10.0 | 変更なし |

## 総合スコア重み

| 定数名 | 初期値 | 最終値 | 調整理由 |
|--------|--------|--------|---------|
| WEIGHT_VALUE | 0.4 | 0.4 | 変更なし |
| WEIGHT_GROWTH | 0.3 | 0.3 | 変更なし |
| WEIGHT_MOMENTUM | 0.3 | 0.3 | 変更なし |
EOF
```

---

### ステップ16: 調整履歴文書化（45分）

#### アクション16-1: 調整履歴作成

**GitHub Copilotへの指示:**

```markdown
# ファイル名: docs/constant_adjustment_log.md

# Copilotに以下を指示:
# 定数調整の履歴を記録するドキュメントを作成してください
#
# セクション:
# 1. 調整の目的
# 2. 初期スコア（調整前）
# 3. 調整プロセス
#    - ラウンド1: PER_BASELINE調整
#    - ラウンド2: DIVIDEND_MULTIPLIER調整
#    - ラウンド3: GROWTH_BASELINE調整
# 4. 最終スコア（調整後）
# 5. 調整の妥当性評価
# 6. AIレビューのサマリー
# 7. 今後の改善点
```

**手動で詳細を記入:**
```bash
# docs/constant_adjustment_log.md を開いて、
# 調整の詳細、スコアの変化、判断理由等を記入
```

---

### ステップ17: 最終確認（45分）

#### アクション17-1: 最終スコア確認

**コマンド:**
```bash
# 最終スコアを表示
docker-compose exec backend python scripts/score_analysis.py

# データベースに保存されているか確認
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT stock_code, total_score, rank, value_score, growth_score, momentum_score 
   FROM daily_scores 
   ORDER BY total_score DESC;"
```

**期待される出力:**
```
 stock_code | total_score | rank | value_score | growth_score | momentum_score 
------------+-------------+------+-------------+--------------+----------------
 6758       |       78.30 | B+   |       68.50 |        85.00 |          82.70
 7203       |       75.50 | B+   |       78.20 |        65.50 |          78.30
 9984       |       62.80 | B    |       58.60 |        75.50 |          60.20
```

**確認項目:**
- [ ] ソニーが1位
- [ ] トヨタが2位
- [ ] SBGが3位
- [ ] すべて期待値範囲内
- [ ] ランクが適切（A/B+/B）

---

#### アクション17-2: バックアップ

**コマンド:**
```bash
# データベースバックアップ
docker-compose exec db pg_dump -U zenjp zenjp_mvp > backup_phase3_$(date +%Y%m%d).sql

# スクリプトバックアップ
tar -czf scripts_phase3_$(date +%Y%m%d).tar.gz backend/scripts/

# ドキュメントバックアップ
tar -czf docs_phase3_$(date +%Y%m%d).tar.gz docs/

echo "✅ バックアップ完了"
```

---

### Day 7完了確認

#### チェックリスト

```bash
# 1. 期待スコア範囲内確認
docker-compose exec db psql -U zenjp -d zenjp_mvp -c \
  "SELECT stock_code, total_score FROM daily_scores;"
# トヨタ: 70-80点
# ソニー: 75-85点
# SBG: 55-70点

# 2. 定数記録確認
cat docs/final_constants.md

# 3. 調整履歴確認
cat docs/constant_adjustment_log.md

# 4. AIレビュー記録確認
cat docs/ai_review_value.md
cat docs/ai_review_growth.md

# 5. バックアップ確認
ls -lh backup_phase3_*.sql
ls -lh scripts_phase3_*.tar.gz
ls -lh docs_phase3_*.tar.gz

# すべてOKなら
echo "✅ Day 7 完了！"
echo "🎉 PHASE3 完了！"
```

**成果物:**
- ✅ 最終調整済みconstants.py
- ✅ docs/target_scores.md（期待スコア）
- ✅ docs/score_gap_analysis.md（ギャップ分析）
- ✅ docs/ai_review_value.md（AIレビュー・バリュー）
- ✅ docs/ai_review_growth.md（AIレビュー・グロース）
- ✅ docs/adjustment_plan.md（調整計画）
- ✅ docs/final_constants.md（最終定数一覧）
- ✅ docs/constant_adjustment_log.md（調整履歴）
- ✅ daily_scoresテーブルに最終スコア保存

---

## 5. 完了確認

### PHASE3完了チェックリスト

**最終確認スクリプト作成:**

```bash
cat > check_phase3.sh << 'EOF'
#!/bin/bash

echo "=== ZenJP MVP PHASE3 完了確認 ==="
echo ""

# 1. スコアデータ確認
echo "1. スコアデータ確認"
SCORE_COUNT=$(docker-compose exec -T db psql -U zenjp -d zenjp_mvp -t -c \
  "SELECT COUNT(*) FROM daily_scores;")
echo "  件数: $SCORE_COUNT"
if [ $SCORE_COUNT -eq 3 ]; then
    echo "  ✅ スコアデータOK"
else
    echo "  ❌ スコアデータNG（3件期待）"
fi
echo ""

# 2. スコア範囲確認
echo "2. スコア範囲確認"
docker-compose exec -T db psql -U zenjp -d zenjp_mvp -c \
  "SELECT stock_code, total_score, rank FROM daily_scores ORDER BY total_score DESC;"
echo ""

# 3. 期待値範囲内確認
echo "3. 期待値範囲内確認"
TOYOTA=$(docker-compose exec -T db psql -U zenjp -d zenjp_mvp -t -c \
  "SELECT total_score FROM daily_scores WHERE stock_code='7203';" | tr -d ' ')
SONY=$(docker-compose exec -T db psql -U zenjp -d zenjp_mvp -t -c \
  "SELECT total_score FROM daily_scores WHERE stock_code='6758';" | tr -d ' ')
SBG=$(docker-compose exec -T db psql -U zenjp -d zenjp_mvp -t -c \
  "SELECT total_score FROM daily_scores WHERE stock_code='9984';" | tr -d ' ')

echo "  トヨタ: $TOYOTA 点（期待: 70-80点）"
echo "  ソニー: $SONY 点（期待: 75-85点）"
echo "  SBG: $SBG 点（期待: 55-70点）"
echo ""

# 4. ドキュメント確認
echo "4. ドキュメント確認"
for doc in target_scores.md final_constants.md constant_adjustment_log.md; do
    if [ -f "docs/$doc" ]; then
        echo "  ✅ $doc"
    else
        echo "  ❌ $doc なし"
    fi
done
echo ""

# 5. スクリプト確認
echo "5. スクリプト確認"
for script in constants.py score_calculator.py calculate_scores.py score_analysis.py; do
    if [ -f "backend/scripts/$script" ]; then
        echo "  ✅ $script"
    else
        echo "  ❌ $script なし"
    fi
done
echo ""

echo "=== 確認完了 ==="
EOF

chmod +x check_phase3.sh
./check_phase3.sh
```

---

### 完了報告フォーマット

```markdown
## PHASE3完了報告

**実施日:** 2026年2月8-9日  
**担当:** 末告さん  
**所要時間:** 18時間

### 成果物

#### スクリプト
- ✅ constants.py（定数定義）
- ✅ score_calculator.py（計算関数）
- ✅ calculate_scores.py（メインスクリプト）
- ✅ score_analysis.py（分析ツール）

#### データ
- ✅ daily_scores: 3件（最終スコア保存）

#### ドキュメント
- ✅ target_scores.md（期待スコア）
- ✅ score_gap_analysis.md（ギャップ分析）
- ✅ ai_review_value.md（AIレビュー）
- ✅ ai_review_growth.md（AIレビュー）
- ✅ adjustment_plan.md（調整計画）
- ✅ final_constants.md（最終定数）
- ✅ constant_adjustment_log.md（調整履歴）

### 最終スコア

| 銘柄 | 総合 | Value | Growth | Momentum | ランク |
|------|------|-------|--------|----------|--------|
| ソニー | 78.3 | 68.5 | 85.0 | 82.7 | B+ |
| トヨタ | 75.5 | 78.2 | 65.5 | 78.3 | B+ |
| SBG | 62.8 | 58.6 | 75.5 | 60.2 | B |

### AI活用実績

- ✅ プロンプト#4使用（バリュー投資家レビュー）
- ✅ プロンプト#5使用（グロース投資家レビュー）
- ✅ 定数調整の根拠強化
- ✅ スコアの妥当性検証

### 次のステップ

PHASE4（API・UI実装）の準備完了
- Day 8-9でFastAPI実装予定
- 算出済みスコアをAPIで公開
```

---

## 6. トラブルシューティング

### 問題1: スコアが0-100の範囲外

**症状:**
```sql
SELECT * FROM daily_scores WHERE total_score > 100 OR total_score < 0;
-- 何件か返ってくる
```

**原因:**
計算ロジックのバグ

**解決策:**
```python
# score_calculator.py の各関数で上限・下限チェック

def calculate_per_score(per: float) -> float:
    score = ...
    return max(0.0, min(100.0, score))  # 0-100に制限
```

---

### 問題2: すべての銘柄が同じスコア

**症状:**
すべての銘柄が50点前後

**原因:**
定数が初期値のまま、または計算ロジックが単純すぎる

**解決策:**
```python
# constants.py を確認
# 各定数が適切に設定されているか

# score_calculator.py を確認
# 計算ロジックが正しく実装されているか
```

---

### 問題3: RSIが計算できない

**症状:**
```
ValueError: not enough values to unpack
```

**原因:**
株価データが不足（14日未満）

**解決策:**
```python
# calculate_rsi() にデフォルト値を設定

def calculate_rsi(prices: list[float], period: int = 14) -> float:
    if len(prices) < period + 1:
        return 50.0  # デフォルト値を返す
    # ... 計算処理
```

---

### 問題4: 配当スコアが異常に高い

**症状:**
配当スコアが常に100点

**原因:**
DIVIDEND_MULTIPLIERが大きすぎる

**解決策:**
```python
# constants.py を調整
DIVIDEND_MULTIPLIER = 15.0  # 20.0 → 15.0に下げる
```

---

### 問題5: AIレビューで納得できる回答が得られない

**原因:**
プロンプトが不十分、またはAIに十分な情報を与えていない

**解決策:**
```
プロンプトに以下を追加:

【追加情報】
- 日本株の平均PER: 15-18倍
- 配当利回り平均: 2-3%
- 成長率（優良企業）: 5-10%

【制約条件】
- スコアは0-100点
- 総合スコアは加重平均（Value 40%, Growth 30%, Momentum 30%）

この情報を踏まえて、再度評価してください。
```

---

## 7. 付録

### 付録A: スコアリングロジック詳細

**PERスコア計算式:**
```
PER <= 8.0: 100点
PER == 15.0: 50点
PER >= 30.0: 0点

8.0 < PER <= 15.0:
  score = 100 - ((PER - 8) / (15 - 8)) * 50

15.0 < PER <= 30.0:
  score = 50 - ((PER - 15) / (30 - 15)) * 50
```

**PBRスコア計算式:**
```
PBR <= 1.0: 100点
PBR >= 3.0: 0点

1.0 < PBR <= 3.0:
  score = 100 - ((PBR - 1.0) / (3.0 - 1.0)) * 100
```

**配当スコア計算式:**
```
score = 配当利回り(%) × DIVIDEND_MULTIPLIER
score = min(score, 100.0)
```

**RSI計算式:**
```
1. 価格変化 = 今日の終値 - 昨日の終値
2. 上昇平均 = 上昇日の変化の14日平均
3. 下落平均 = 下落日の変化の14日平均
4. RS = 上昇平均 / 下落平均
5. RSI = 100 - (100 / (1 + RS))
```

---

### 付録B: 期待スコア設定の考え方

**トヨタ（安定配当企業）:**
- 配当利回りが高い（9.66%） → Valueスコア高め
- 成長率は安定的（4.48%） → Growthスコア中程度
- 大型株で需給安定 → Momentumスコア中～高

**ソニー（成長企業）:**
- PERが高め（15.88倍） → Valueスコアやや低め
- 成長率が高い（7.14%） → Growthスコア高め
- グローバル企業 → Momentumスコア高め

**SBG（投資会社）:**
- PER/PBRの解釈が特殊 → Valueスコア低め
- 投資先次第 → Growthスコア変動
- ボラティリティ高い → Momentumスコア変動大

---

### 付録C: 定数調整のベストプラクティス

**調整の原則:**
1. **一度に1つの定数のみ変更**
   - 複数同時変更は影響が不明確

2. **±20%以内の調整**
   - 大きく変更しすぎない

3. **AIレビューを活用**
   - 客観的な視点を取り入れる

4. **最低3銘柄でテスト**
   - 1銘柄だけで判断しない

5. **調整履歴を記録**
   - なぜその値にしたか記録

**調整の順序:**
1. Valueスコア定数（PER、PBR、配当）
2. Growthスコア定数（成長率）
3. Momentumスコア定数（RSI、出来高）
4. 総合スコア重み（最後に微調整）

---

### 付録D: GitHubCopilotプロンプトテンプレート

**スコア計算関数:**
```
[カテゴリ]スコアを計算する関数を書いてください。

要件:
- 入力: [指標名]（例: PER）
- 出力: スコア（0-100点）
- ロジック:
  - [閾値1] 以下: 100点
  - [閾値2]: 50点
  - [閾値3] 以上: 0点
  - 上記の間は線形補間

実装してください。
```

---

## 変更履歴

| Version | 日付 | 変更内容 | 作成者 |
|---------|------|---------|--------|
| 1.0.0 | 2026-02-08 | 初版作成 | ZenJP Team |

---

**ZenJP MVP PHASE3 実装アクション詳細計画書 完成**

**次のステップ:** Day 6 ステップ1から実装開始！
