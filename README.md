# ZenJP MVP - 日本株スコアリングシステム

Value/Growth/Momentumの3軸で日本株を評価するフルスタックWebアプリケーションです。

**PHASE6完了**: 統合テスト、品質監査、スコアリングエンジン改善が完了しました。

## 概要

このシステムは日本株をPER、PBR、配当利回り、売上成長率、RSI、出来高変化率などの指標で**総合的にスコアリング**します。

### 特徴

- ✅ **データドリブン評価**: 成長率は財務データから自動計算
- ✅ **業種別重み付け**: 輸送用機器・電気機器・情報通信業で異なる重み
- ✅ **現実的なPER評価**: 10-15-25点の3段階評価
- ✅ **高速API**: 平均応答時間 26ms
- ✅ **包括的テスト**: 12個の後端テスト（90%カバレッジ）+ 2個のE2Eテスト
- ✅ **セキュリティ検証**: Bandit/npm audit で0件の脆弱性

### 技術スタック

- **Backend**: FastAPI 1.0.0 + PostgreSQL 14 + SQLAlchemy
- **Frontend**: Next.js 16.1.6 + React 19.2.3 + TypeScript + Tailwind CSS + Framer Motion 11.0.3
- **Testing**: pytest 9.0.2 + pytest-cov 7.0.0 + Playwright 1.58.1
- **Infrastructure**: Docker Compose

## セットアップ

### 前提条件

- Docker & Docker Compose
- Git

### インストール手順

1. **リポジトリのクローン**

```bash
git clone <repository-url>
cd zenjp-mvp
```

2. **Docker Composeで起動**

```bash
docker-compose up -d
```

3. **データのシード（初回のみ）**

```bash
# バックエンドコンテナに入る
docker-compose exec -T backend bash

# 財務データの投入（複数年対応）
python scripts/seed_financials.py

# 株価データの投入
python scripts/seed_prices.py

# スコア計算（成長率は財務データから自動計算）
python scripts/calculate_scores.py
```

4. **テストの実行（オプション）**

```bash
# バックエンドテスト（90%カバレッジ）
python -m pytest tests/ -v --cov=app --cov-report=html

# フロントエンドE2Eテスト（Playwrightコンテナで実行）
docker run --rm --network zenjp-mvp_zenjp-network \
  -e E2E_BASE_URL=http://38.242.205.42:3000 \
  mcr.microsoft.com/playwright:v1.58.1-jammy \
  npx playwright test
```

### アクセス方法

- **フロントエンド**: http://localhost:3000
- **バックエンドAPI**: http://localhost:8000
- **API仕様**: http://localhost:8000/docs

## 使用方法

### Webインターフェース

1. ブラウザで http://localhost:3000 にアクセス
2. トップページで3つの銘柄ボタンから選択:
   - **7203** トヨタ自動車
   - **6758** ソニーグループ
   - **9984** ソフトバンクグループ
3. スコア、ランク、市場平均との比較が表示されます
4. カテゴリ別スコア（Value/Growth/Momentum）が横棒グラフで表示されます
5. 詳細指標（PER、PBR、配当、RSI等）がテーブルで表示されます

### API仕様

詳細は [docs/api_endpoints.md](docs/api_endpoints.md) をご覧ください。

#### GET /api/score/{stock_code}

指定した銘柄コードのスコア情報を取得します。

**リクエスト例:**

```bash
curl http://localhost:8000/api/score/7203
```

**レスポンス例:**

```json
{
  "stock_code": "7203",
  "stock_name": "トヨタ自動車",
  "total_score": 72.63,
  "value_score": 55.0,
  "growth_score": 85.0,
  "momentum_score": 78.0,
  "rank": "A",
  "market_comparison": {
    "total_diff": 7.3,
    "value_diff": -5.2,
    "growth_diff": 15.8,
    "momentum_diff": 12.1
  },
  "details": {
    "per_score": 65.0,
    "pbr_score": 45.0,
    "dividend_yield_score": 55.0,
    "revenue_growth_rate_score": 80.0,
    "profit_growth_rate_score": 90.0,
    "rsi_score": 72.0,
    "volume_change_score": 84.0
  },
  "updated_at": "2025-01-15T12:00:00"
}
```

## スコアリングロジック

### 3つの評価軸

1. **Value スコア** (企業の価値評価)
   - PER（株価収益率）: 10以下で100点、25以上で0点
   - PBR（株価純資産倍率）: 1.0以下で100点、3.0以上で0点
   - 配当利回り: × 12の係数で計算

2. **Growth スコア** (企業の成長性)
   - 売上成長率: 財務データの前年比から自動計算
   - 15%以上で100点、-5%以下で0点

3. **Momentum スコア** (市場の勢い)
   - RSI（相対力指数）: 理想範囲40-70で高評価
   - 出来高変化率: 短期/長期平均の乖離度を評価

### 業種別の重み付け

総合スコア = Value×重み + Growth×重み + Momentum×重み

| 業種 | Value | Growth | Momentum |
|------|-------|--------|----------|
| 輸送用機器（トヨタ） | 40% | 30% | 30% |
| 電気機器（ソニー） | 30% | 45% | 25% |
| 情報・通信業（ソフトバンク） | 25% | 50% | 25% |

### ランク定義

| ランク | 点数 | 説明 |
|--------|------|------|
| A | 75+ | 非常に優良企業 |
| B+ | 70+ | 優良企業 |
| B | 60+ | 良好企業 |
| C+ | 50+ | 平均付近 |
| C | 40+ | 平均以下 |
| D | 0+ | 割高企業 |

### 市場平均

- **定義**: 50点 = スコア評価の中立点
- **注記**: MVP版は3銘柄サンプルのため、日経225など多数サンプルでの計算が望ましい
- **実測平均**: 3銘柄の平均スコア = 63.27点

## 実装済みの機能

### PHASE6 成果物

✅ **統合テスト** (Test Report)
- バックエンドテスト: 12個 (90%カバレッジ)
  - スコア計算: 3個テスト
  - APIエンドポイント: 5個テスト
  - エッジケース: 2個テスト
  - モデル/設定: 2個テスト
- フロントエンドE2E: 2個テスト (Playwright)

✅ **品質監査**
- セキュリティ監査 (Bandit): **0件の脆弱性**
- npm監査 (npm audit): **0件の脆弱性**
- パフォーマンス監査 (Locust): 平均 26ms, p95 30ms, p99 290ms

✅ **スコアリング改善**
- 複数年財務データ (3年分) で成長率を自動計算
- 業種別スコア重み付けを実装
- PER計算ロジックを改善 (10-15-25の3段階)
- 市場平均の定義を明確化

## プロジェクト構成

```
zenjp-mvp/
├── backend/              # FastAPI バックエンド
│   ├── app/
│   │   ├── api/v1/      # API エンドポイント
│   │   ├── core/        # 設定・ユーティリティ
│   │   ├── db/          # データベースモデル
│   │   ├── models/      # SQLAlchemy モデル
│   │   ├── schemas/     # Pydantic スキーマ
│   │   ├── services/    # ビジネスロジック
│   │   └── routers/     # FastAPI ルーター
│   └── scripts/         # データ処理スクリプト
├── frontend/            # Next.js フロントエンド
│   ├── app/            # Next.js App Router
│   ├── src/
│   │   ├── components/ # React コンポーネント
│   │   └── lib/        # ユーティリティ・型定義
│   └── public/         # 静的ファイル
├── db/                  # データベース初期化SQL
├── docs/                # ドキュメント
│   └── screenshots/     # UI スクリーンショット
└── docker-compose.yml   # Docker Compose設定
```

## 開発

### バックエンド開発

```bash
# バックエンドコンテナに入る
docker-compose exec backend bash

# スコア再計算
python scripts/calculate_scores.py

# 異常値検出
python scripts/detect_anomalies.py
```

### フロントエンド開発

```bash
# フロントエンドコンテナに入る
docker-compose exec frontend sh

# 依存関係のインストール
npm install

# ビルド
npm run build
```

### テスト

APIテストは [Postman Collection](docs/ZenJP_MVP_API.postman_collection.json) を使用できます。

## ドキュメント

### 要件定義 & 技術設計
- [要件定義書](docs/ZenJP_MVP_Requirements_v1.1.md) - プロジェクト要件定義
- [技術設計書](docs/ZenJP_MVP_Technical_Design%20v1.1.md) - 技術設計仕様
- [実装設計書](docs/ZenJP_MVP_Implementation_Plan_1.md) - 実装計画書

### API & 技術仕様
- [API Endpoints](docs/api_endpoints.md) - 完全なAPI仕様

### セキュリティ & 品質
- [Security Audit](docs/security-audit.md) - セキュリティ監査結果（PHASE6）
- [Performance Audit](docs/performance-audit.md) - パフォーマンス監査結果（PHASE6）
- [Test Report](docs/test-report.md) - テスト実行レポート（PHASE6）
- [API Security Review](docs/api_security_review.md) - セキュリティレビュー

### 実装アクション詳細計画書
- [PHASE1 Action Plan](docs/ZenJP_PHASE1_Action_Plan.md)
- [PHASE2 Action Plan](docs/ZenJP_PHASE2_Action_Plan.md)
- [PHASE3 Action Plan](docs/ZenJP_PHASE3_Action_Plan.md)
- [PHASE4 Action Plan](docs/ZenJP_PHASE4_Index.md)
  - [PHASE4 API Design](docs/ZenJP_PHASE4_Part1_API.md)
  - [PHASE4 UI Design](docs/ZenJP_PHASE4_Part2_UI.md)
- [PHASE5 Implementation Plan](docs/ZenJP_MVP_PHASE5_Implementation_Plan.md)
- [PHASE6 Implementation Plan](docs/ZenJP_MVP_PHASE6_Implementation_Plan.md)

### その他
- [Constant Adjustment Log](docs/constant_adjustment_log.md) - スコア計算定数の調整履歴
- [Postman Collection](docs/ZenJP_MVP_API.postman_collection.json) - APIテスト用

## パフォーマンス & セキュリティ

### パフォーマンス指標（PHASE6）
- **API Response Time**: 平均 26ms（目標500ms以下）
  - p95: 30ms
  - p99: 290ms
- **Frontend Initial Load**: ~2秒
- **Animation Duration**: 1.5秒（スコアカウントアップ）
- **Load Test**: Locust 124リクエスト、0件のエラー

### セキュリティ状況
- **Bandit Security Scan**: **0件の脆弱性**
  - SQLインジェクション対策: SQLAlchemy ORM使用
  - XSS対策: React自動エスケープ
- **npm Audit**: **0件の脆弱性**
  - 432個の依存関係すべて安全
- **入力値検証**: Pydantic + FastAPI
- **CORS設定**: localhost:3000のみ許可
- **エラーハンドリング**: 3層構造（Validation/DB/General）

詳細は [docs/security-audit.md](docs/security-audit.md) をご覧ください。

## ライセンス

MIT License

## 作者

ZenJP Development Team
