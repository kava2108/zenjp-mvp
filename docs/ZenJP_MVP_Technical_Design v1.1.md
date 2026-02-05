# ZenJP MVP 技術設計書（2週間版）

**Version:** 1.0.0  
**作成日:** 2026年2月1日  
**対象:** ZenJP MVP（3銘柄、3カテゴリスコア）  
**基準文書:** ZenJP MVP 要件定義書 v1.1.0

---

## 🎯 本ドキュメントの目的

この技術設計書は、ZenJP MVP（2週間版）の実装に必要な技術的詳細を定義します。

**対象読者:**
- バックエンド開発者
- フロントエンド開発者
- データエンジニア

**本ドキュメントで決定すること:**
- システムアーキテクチャ
- 技術スタック選定理由
- データベース設計（詳細）
- API設計（実装レベル）
- データパイプライン設計

---

## 目次

1. [システムアーキテクチャ](#1-システムアーキテクチャ)
2. [技術スタック](#2-技術スタック)
3. [データベース設計](#3-データベース設計)
4. [バックエンド設計](#4-バックエンド設計)
5. [フロントエンド設計](#5-フロントエンド設計)
6. [データパイプライン](#6-データパイプライン)
7. [デプロイ設計](#7-デプロイ設計)

---

## 1. システムアーキテクチャ

### 1.1 全体構成図

```
┌─────────────────────────────────────────────┐
│           Browser (User)                    │
└────────────────┬────────────────────────────┘
                 │ HTTP
                 ↓
┌─────────────────────────────────────────────┐
│      Frontend (Next.js 14)                  │
│      Port: 3000                             │
└────────────────┬────────────────────────────┘
                 │ REST API (JSON)
                 ↓
┌─────────────────────────────────────────────┐
│      Backend (FastAPI)                      │
│      Port: 8000                             │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐ │
│  │ Routers  │→│ Services │→│Repositories│ │
│  └──────────┘ └──────────┘ └────────────┘ │
└────────────────┬────────────────────────────┘
                 │ SQL
                 ↓
┌─────────────────────────────────────────────┐
│      PostgreSQL 14                          │
│      Port: 5432                             │
└─────────────────────────────────────────────┘
         ↑
         │ Python Scripts (手動実行)
         │
┌────────┴────────────────────────────────────┐
│   Data Collection Scripts                   │
│   - collect_prices.py                       │
│   - collect_financials.py                   │
│   - calculate_scores.py                     │
└─────────────────────────────────────────────┘
```

---

## 2. 技術スタック

### 2.1 バックエンド

#### FastAPI 0.104+
**選定理由:**
- 高速（Starlette + Pydantic）
- 自動OpenAPI生成
- 型安全
- 学習コスト低

#### SQLAlchemy 2.0+
**選定理由:**
- Python標準ORM
- 型安全
- マイグレーション対応

#### 依存パッケージ
```txt
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
yfinance==0.2.32
pandas==2.1.3
python-dotenv==1.0.0
```

### 2.2 フロントエンド

#### Next.js 14+
**選定理由:**
- App Router（最新）
- Server Components
- TypeScript完全対応

#### Tailwind CSS 3.4+
**選定理由:**
- 高速プロトタイピング
- 小さいバンドルサイズ

#### 依存パッケージ
```json
{
  "dependencies": {
    "next": "14.0.4",
    "react": "18.2.0",
    "typescript": "5.3.3",
    "tailwindcss": "3.4.0",
    "recharts": "2.10.3"
  }
}
```

### 2.3 データベース

#### PostgreSQL 14+
**選定理由:**
- 信頼性
- UPSERT対応
- JSON型サポート

---

## 3. データベース設計

### 3.1 テーブル定義

[詳細なSQLは要件定義書を参照]

**テーブル一覧:**
1. stocks (3件)
2. stock_prices (90件)
3. stock_financials (3件)
4. daily_scores (3件)

**合計:** 約15KB

---

## 4. バックエンド設計

### 4.1 ディレクトリ構造

```
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   └── services/
├── scripts/
└── requirements.txt
```

### 4.2 APIエンドポイント仕様

#### GET /api/score/{stock_code}

**レスポンス例:**
```json
{
  "status": "success",
  "data": {
    "stock_code": "7203",
    "stock_name": "トヨタ自動車",
    "date": "2026-02-01",
    "total_score": 78.5,
    "rank": "B+",
    "updated_at": "2026-02-01T06:15:23+09:00",
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

**updated_atの用途:**
- データがいつ計算されたかを明示
- デバッグ時に「最新データか」を即座に判断可能
- フロントエンドで「最終更新: 2月1日 6:15」と表示

**Pydanticスキーマ:**
```python
from datetime import datetime

class ScoreResponse(BaseModel):
    stock_code: str
    stock_name: str
    date: date
    total_score: float
    rank: str
    updated_at: datetime  # 追加
    market_comparison: MarketComparison
    category_scores: dict[str, CategoryScore]
    details: ScoreDetails
```

---

## 5. フロントエンド設計

### 5.1 ディレクトリ構造

```
frontend/
├── src/
│   ├── app/
│   │   ├── stocks/
│   │   │   └── [code]/
│   │   │       └── page.tsx
│   │   └── layout.tsx
│   ├── components/
│   │   ├── ScoreCard.tsx
│   │   ├── CategoryBar.tsx
│   │   └── DetailTable.tsx
│   ├── lib/
│   │   ├── api.ts
│   │   └── types.ts          # バックエンドと型を共有
│   └── styles/
└── package.json
```

### 5.2 型定義の共有化（重要）

**問題:**
バックエンド（Pydantic）とフロントエンド（TypeScript）で型定義が二重管理になり、不一致が発生しやすい。

**推奨解決策:**

#### 方法1: 手動同期（MVP推奨）
バックエンドのPydanticスキーマをTypeScriptに手動変換してコピペ。

**バックエンド（Python）:**
```python
# backend/app/schemas/score.py
class ScoreResponse(BaseModel):
    stock_code: str
    stock_name: str
    date: date
    total_score: float
    rank: str
    updated_at: datetime
```

**フロントエンド（TypeScript）:**
```typescript
// frontend/src/lib/types.ts
export interface ScoreResponse {
  stock_code: string;
  stock_name: string;
  date: string;          // ISO 8601形式
  total_score: number;
  rank: string;
  updated_at: string;    // ISO 8601形式
}
```

**同期ルール:**
1. バックエンドでスキーマ変更したら、必ずフロントエンドの型も更新
2. コメントで同期元を明記
3. Day 8-9（API実装時）に一度同期、その後は変更時のみ

#### 方法2: OpenAPI自動生成（将来的）
FastAPIの自動生成したOpenAPI仕様からTypeScript型を生成。

```bash
# openapi-typescript を使用
npx openapi-typescript http://localhost:8000/openapi.json -o src/lib/api-types.ts
```

**MVP期間中は方法1（手動）を推奨。**

### 5.3 Server Actions vs fetch

**現在の設計: fetch（推奨）**

```typescript
// lib/api.ts
export async function getScore(code: string) {
  const res = await fetch(`${API_URL}/api/score/${code}`);
  return res.json();
}
```

**理由:**
- バックエンド（FastAPI）とフロントエンド（Next.js）を完全分離
- APIが独立して動作（Postmanでもテスト可能）
- 将来的にモバイルアプリからも同じAPIを使用可能

**Server Actionsは使わない理由:**
- FastAPIとNext.jsを統合する手間がかかる
- MVP期間中は分離した方がシンプル
- デバッグが容易（ブラウザのNetwork タブで確認可能）

---

## 6. データパイプライン

### 6.1 スクリプト一覧

1. `collect_prices.py` - Yahoo Finance
2. `collect_financials.py` - EDINET
3. `calculate_scores.py` - スコア計算

---

## 7. デプロイ設計

### 7.1 ローカル開発環境（Docker Compose）

**重要: Day 1の最優先タスク**

MVPはローカル環境のみで動作させるため、`docker-compose.yml`で全環境を一発起動する。

#### docker-compose.yml（完全版）

```yaml
version: '3.8'

services:
  # PostgreSQL データベース
  db:
    image: postgres:14-alpine
    container_name: zenjp_db
    environment:
      POSTGRES_DB: zenjp_mvp
      POSTGRES_USER: zenjp
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U zenjp"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - zenjp-network

  # FastAPI バックエンド
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: zenjp_backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://zenjp:password@db:5432/zenjp_mvp
      DEBUG: "true"
      CORS_ORIGINS: '["http://localhost:3000"]'
    volumes:
      - ./backend:/app
      - backend_cache:/app/.cache
    depends_on:
      db:
        condition: service_healthy
    command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    networks:
      - zenjp-network

  # Next.js フロントエンド
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: zenjp_frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    depends_on:
      - backend
    command: npm run dev
    networks:
      - zenjp-network

volumes:
  postgres_data:
    driver: local
  backend_cache:
    driver: local

networks:
  zenjp-network:
    driver: bridge
```

#### backend/Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 依存パッケージのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# 開発環境用のホットリロード対応
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
```

#### frontend/Dockerfile

```dockerfile
FROM node:20-alpine

WORKDIR /app

# 依存パッケージのインストール
COPY package*.json ./
RUN npm ci

# アプリケーションコードのコピー
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
```

### 7.2 起動手順（Day 1で実行）

```bash
# 1. プロジェクトディレクトリ作成
mkdir zenjp-mvp
cd zenjp-mvp

# 2. ディレクトリ構造作成
mkdir -p backend/app frontend/src database

# 3. docker-compose.yml を作成
# （上記の内容をコピペ）

# 4. Dockerfileを作成
# backend/Dockerfile と frontend/Dockerfile を作成

# 5. 環境変数ファイル作成
cat > .env << 'EOF'
DATABASE_URL=postgresql://zenjp:password@db:5432/zenjp_mvp
DEBUG=true
CORS_ORIGINS=["http://localhost:3000"]
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

# 6. Docker起動
docker-compose up -d

# 7. 起動確認
docker-compose ps
# → db, backend, frontend が "Up" になっていればOK

# 8. ログ確認
docker-compose logs -f backend
docker-compose logs -f frontend

# 9. アクセス確認
# Backend: http://localhost:8000/docs（Swagger UI）
# Frontend: http://localhost:3000（Next.js）
# Database: localhost:5432（psqlで接続可能）
```

### 7.3 よくあるエラーと対処法

#### エラー1: `port 5432 already in use`

**原因:** ローカルにPostgreSQLが既にインストールされている

**対処法:**
```bash
# ローカルのPostgreSQLを停止
sudo systemctl stop postgresql  # Linuxの場合
brew services stop postgresql   # macOSの場合

# または、ポート番号を変更
# docker-compose.yml の ports を "5433:5432" に変更
```

#### エラー2: `backend | Error: No module named 'app'`

**原因:** backend/app/ ディレクトリが存在しない

**対処法:**
```bash
# バックエンドの基本構造を作成
mkdir -p backend/app
touch backend/app/__init__.py
touch backend/app/main.py
```

#### エラー3: `frontend | Module not found: Can't resolve 'next'`

**原因:** package.json が存在しない

**対処法:**
```bash
cd frontend
npm init -y
npm install next react react-dom typescript
```

### 7.4 開発環境の検証チェックリスト

Day 1の最後に以下を確認：

- [ ] `docker-compose ps` で3つのコンテナが "Up"
- [ ] http://localhost:8000/docs でSwagger UIが表示される
- [ ] http://localhost:8000/health で `{"status":"ok"}` が返る
- [ ] http://localhost:3000 でNext.jsのページが表示される
- [ ] `psql -h localhost -U zenjp -d zenjp_mvp` でDBに接続できる
- [ ] バックエンドのコード変更が即座に反映される（ホットリロード）
- [ ] フロントエンドのコード変更が即座に反映される（Fast Refresh）

**すべてチェックできたらDay 1完了！**

---

**実装準備完了**

次のステップ: Day 1 環境構築

---

## 付録: Gemini改善提案への対応

### 改善1: APIレスポンスへの「更新日時（updated_at）」追加 ✅

**提案内容:** スコアがいつ計算されたかを示すタイムスタンプをAPIレスポンスに含める。

**対応:** 
- `ScoreResponse`に`updated_at: datetime`を追加
- フロントエンドで「最終更新: 2月1日 6:15」と表示
- デバッグ時に最新データか即座に判断可能

**実装例:**
```python
# バックエンド
class ScoreResponse(BaseModel):
    updated_at: datetime  # 追加

# フロントエンド表示
<p>最終更新: {new Date(data.updated_at).toLocaleString('ja-JP')}</p>
```

---

### 改善2: Next.js Server Actions vs fetch の方針明確化 ✅

**提案内容:** バックエンド（FastAPI）とフロントエンド（Next.js）の連携方法を明確化。

**対応:**
- **MVP期間中は`fetch`を使用**（FastAPIとNext.jsを完全分離）
- Server Actionsは使わない（統合の手間を避ける）
- 型定義の手動同期ルールを明記

**理由:**
1. APIが独立して動作（Postmanでテスト可能）
2. デバッグが容易（Network タブで確認）
3. 将来的にモバイルアプリからも同じAPIを使用可能

**型共有化の推奨手順:**
1. バックエンドのPydanticスキーマを作成
2. TypeScriptの`interface`に手動変換
3. コメントで同期元を明記
4. API変更時は必ず型も更新

---

### 改善3: docker-compose.yml の詳細化 ✅

**提案内容:** Day 1で確実に環境構築できるよう、完全な`docker-compose.yml`を設計書に含める。

**対応:**
- 本番レベルの`docker-compose.yml`（healthcheck、networks含む）
- `Dockerfile`（backend/frontend）の完全版
- 起動手順の詳細ガイド
- よくあるエラーと対処法
- 検証チェックリスト

**Day 1の成功基準:**
```bash
✓ docker-compose ps で3コンテナが "Up"
✓ http://localhost:8000/docs でSwagger UI表示
✓ http://localhost:3000 でNext.js表示
✓ ホットリロードが動作
```

**これでDay 1の環境構築で詰まるリスクを最小化！**

---

## 変更履歴

| Version | 日付 | 変更内容 | 作成者 |
|---------|------|---------|--------|
| 1.0.0 | 2026-02-01 | 初版作成 | ZenJP Team |
| 1.1.0 | 2026-02-01 | Gemini改善提案を反映<br>- APIに`updated_at`追加<br>- 型共有化ルール明記<br>- docker-compose詳細化 | ZenJP Team |

---

**ZenJP MVP 技術設計書 v1.1.0 完成**

この設計書に基づき、Day 1から確実に実装を開始できます。
