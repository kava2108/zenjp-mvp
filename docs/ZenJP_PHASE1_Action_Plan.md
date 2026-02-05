# ZenJP MVP PHASE1 実装アクション詳細計画書

**対象フェーズ:** PHASE1 環境構築・データベース構築  
**期間:** Day 1-2（2日間、合計6時間）  
**担当:** 末告さん（指示・確認・承認）  
**実装:** GitHub Copilot（実行）  
**作成日:** 2026年2月3日

---

## 📋 目次

1. [PHASE1概要](#1-phase1概要)
2. [事前準備](#2-事前準備)
3. [Day 1: 環境構築](#3-day-1-環境構築)
4. [Day 2: データベース構築](#4-day-2-データベース構築)
5. [完了確認](#5-完了確認)
6. [トラブルシューティング](#6-トラブルシューティング)

---

## 1. PHASE1概要

### 1.1 達成目標

**Day 1終了時:**
- ✅ Docker環境が起動している（3コンテナ: db, backend, frontend）
- ✅ http://localhost:8000 でFastAPIにアクセスできる
- ✅ http://localhost:3000 でNext.jsにアクセスできる
- ✅ psqlでPostgreSQLに接続できる

**Day 2終了時:**
- ✅ 4つのテーブルが作成されている
- ✅ stocks テーブルに3銘柄が登録されている
- ✅ SQLAlchemyモデルとPydanticスキーマが同期している
- ✅ 型定義の不一致エラーがゼロ

### 1.2 成果物

```
zenjp-mvp/
├── docker-compose.yml
├── .env
├── .gitignore
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── stock.py
│   │   │   ├── price.py
│   │   │   ├── financial.py
│   │   │   └── score.py
│   │   └── schemas/
│   │       ├── __init__.py
│   │       ├── stock.py
│   │       ├── price.py
│   │       ├── financial.py
│   │       └── score.py
│   └── scripts/
│       └── seed_stocks.py
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── next.config.js
│   └── src/
│       └── app/
│           ├── layout.tsx
│           ├── page.tsx
│           └── globals.css
└── database/
    └── init.sql
```

---

## 2. 事前準備

### 2.1 必要なツール

以下がインストールされていることを確認してください：

```bash
# バージョン確認コマンド
docker --version          # Docker 20.10+
docker-compose --version  # Docker Compose 2.0+
git --version             # Git 2.30+
```

### 2.2 GitHub Copilotの準備

1. VS Code / Cursorを起動
2. GitHub Copilot拡張機能が有効になっていることを確認
3. 以下のファイルをCopilotに読み込ませる準備：
   - 要件定義書 v1.1.0
   - 技術設計書 v1.1.0
   - 実装計画書 v1.1.0（AI駆動型）

### 2.3 作業ディレクトリの決定

```bash
# 作業ディレクトリを決定（例: ホームディレクトリ直下）
cd ~
# または
cd ~/Projects
```

---

## 3. Day 1: 環境構築

**所要時間:** 3時間  
**目標:** Docker環境起動、3コンテナが"Up"状態

---

### ステップ1: プロジェクト初期化（15分）

#### アクション1-1: プロジェクトディレクトリ作成

**コマンド:**
```bash
mkdir zenjp-mvp
cd zenjp-mvp
```

**確認:**
```bash
pwd
# 出力例: /Users/your-name/zenjp-mvp
```

---

#### アクション1-2: Git初期化

**コマンド:**
```bash
git init
```

**確認:**
```bash
ls -la | grep .git
# 出力: drwxr-xr-x  .git
```

---

#### アクション1-3: .gitignore作成

**GitHub Copilotへの指示:**

```
# VS Code / Cursorで新規ファイル作成
# ファイル名: .gitignore

# Copilotに以下をコメントで指示
# Python、Node.js、Docker、環境変数ファイル用の.gitignoreを作成してください
```

**期待される内容:**
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/

# Node.js
node_modules/
.next/
out/
*.log

# Docker
*.pid

# Environment
.env
.env.local

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Database
*.db
*.sqlite
```

**確認コマンド:**
```bash
cat .gitignore
```

---

### ステップ2: ディレクトリ構造作成（10分）

#### アクション2-1: ディレクトリ作成

**コマンド:**
```bash
mkdir -p backend/app/{models,schemas,routers,services}
mkdir -p backend/scripts
mkdir -p frontend/src/app
mkdir -p database
```

**確認:**
```bash
tree -L 3
# または
find . -type d -not -path '*/\.*'
```

**期待される出力:**
```
.
├── backend
│   ├── app
│   │   ├── models
│   │   ├── schemas
│   │   ├── routers
│   │   └── services
│   └── scripts
├── database
└── frontend
    └── src
        └── app
```

---

#### アクション2-2: __init__.py作成

**コマンド:**
```bash
touch backend/app/__init__.py
touch backend/app/models/__init__.py
touch backend/app/schemas/__init__.py
touch backend/app/routers/__init__.py
touch backend/app/services/__init__.py
```

**確認:**
```bash
find backend -name "__init__.py"
# 5個のファイルが表示されればOK
```

---

### ステップ3: Docker Compose設定（45分）

#### アクション3-1: docker-compose.yml作成

**GitHub Copilotへの指示:**

```yaml
# ファイル名: docker-compose.yml

# Copilotに以下を指示（コメントで記述）
# ZenJP MVP用のdocker-compose.ymlを作成してください
# サービス:
# 1. db: PostgreSQL 14-alpine
#    - コンテナ名: zenjp_db
#    - ポート: 5432
#    - 環境変数: POSTGRES_DB=zenjp_mvp, POSTGRES_USER=zenjp, POSTGRES_PASSWORD=password
#    - ボリューム: postgres_data, ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
#    - healthcheck: pg_isready -U zenjp
# 2. backend: FastAPI
#    - コンテナ名: zenjp_backend
#    - ポート: 8000
#    - 環境変数: DATABASE_URL=postgresql://zenjp:password@db:5432/zenjp_mvp
#    - ボリューム: ./backend:/app
#    - depends_on: db (healthcheck)
#    - command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# 3. frontend: Next.js
#    - コンテナ名: zenjp_frontend
#    - ポート: 3000
#    - 環境変数: NEXT_PUBLIC_API_URL=http://localhost:8000
#    - ボリューム: ./frontend:/app, /app/node_modules
#    - depends_on: backend
#    - command: npm run dev
# ネットワーク: zenjp-network (bridge)
# ボリューム: postgres_data, backend_cache
```

**手動確認項目:**
- [ ] version: '3.8' が記載されている
- [ ] 3つのサービス（db, backend, frontend）が定義されている
- [ ] healthcheckが設定されている
- [ ] networksが設定されている

**確認コマンド:**
```bash
docker-compose config
# エラーが出なければOK
```

---

#### アクション3-2: .env作成

**コマンド:**
```bash
cat > .env << 'EOF'
# Application
APP_NAME=ZenJP MVP
DEBUG=true

# Database
DATABASE_URL=postgresql://zenjp:password@db:5432/zenjp_mvp
POSTGRES_DB=zenjp_mvp
POSTGRES_USER=zenjp
POSTGRES_PASSWORD=password

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Scoring Constants (初期値、Day 6-7で調整)
PER_BASELINE=15.0
PBR_PERFECT_THRESHOLD=1.0
DIVIDEND_MULTIPLIER=20.0
GROWTH_PERFECT_THRESHOLD=20.0
RSI_IDEAL_MIN=40.0
RSI_IDEAL_MAX=70.0

# Market Average
MARKET_AVERAGE_TOTAL=50.0
MARKET_AVERAGE_VALUE=50.0
MARKET_AVERAGE_GROWTH=50.0
MARKET_AVERAGE_MOMENTUM=50.0
EOF
```

**確認:**
```bash
cat .env
```

---

### ステップ4: バックエンドDockerfile（30分）

#### アクション4-1: requirements.txt作成

**GitHub Copilotへの指示:**

```python
# ファイル名: backend/requirements.txt

# Copilotに以下を指示
# ZenJP MVP バックエンド用のPython依存関係を記述してください
# 必要なパッケージ:
# - fastapi==0.104.1
# - uvicorn[standard]==0.24.0
# - sqlalchemy==2.0.23
# - psycopg2-binary==2.9.9
# - pydantic==2.5.0
# - pydantic-settings==2.1.0
# - python-dotenv==1.0.0
# - yfinance==0.2.32
# - pandas==2.1.3
# - numpy==1.26.2
# - alembic==1.13.0
```

**確認:**
```bash
cat backend/requirements.txt
wc -l backend/requirements.txt
# 11行以上あればOK
```

---

#### アクション4-2: Dockerfile作成

**GitHub Copilotへの指示:**

```dockerfile
# ファイル名: backend/Dockerfile

# Copilotに以下を指示
# Python 3.11-slim ベースのDockerfileを作成してください
# 手順:
# 1. FROM python:3.11-slim
# 2. WORKDIR /app
# 3. requirements.txtをコピーしてpip install
# 4. アプリケーションコードをコピー
# 5. ENV PYTHONUNBUFFERED=1
# 6. EXPOSE 8000
# 7. CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
```

**確認:**
```bash
cat backend/Dockerfile
```

---

### ステップ5: フロントエンドDockerfile（30分）

#### アクション5-1: package.json作成

**GitHub Copilotへの指示:**

```json
// ファイル名: frontend/package.json

// Copilotに以下を指示
// ZenJP MVP フロントエンド用のpackage.jsonを作成してください
// name: "zenjp-frontend"
// version: "1.0.0"
// scripts:
//   - dev: "next dev"
//   - build: "next build"
//   - start: "next start"
// dependencies:
//   - next: "14.0.4"
//   - react: "18.2.0"
//   - react-dom: "18.2.0"
//   - typescript: "5.3.3"
//   - tailwindcss: "3.4.0"
//   - recharts: "2.10.3"
// devDependencies:
//   - @types/node: "20.10.0"
//   - @types/react: "18.2.42"
```

**確認:**
```bash
cat frontend/package.json
```

---

#### アクション5-2: tsconfig.json作成

**GitHub Copilotへの指示:**

```json
// ファイル名: frontend/tsconfig.json

// Copilotに以下を指示
// Next.js 14 App Router用のtsconfig.jsonを作成してください
// compilerOptions:
//   - target: "ES2020"
//   - lib: ["dom", "dom.iterable", "esnext"]
//   - allowJs: true
//   - skipLibCheck: true
//   - strict: true
//   - noEmit: true
//   - esModuleInterop: true
//   - module: "esnext"
//   - moduleResolution: "bundler"
//   - resolveJsonModule: true
//   - isolatedModules: true
//   - jsx: "preserve"
//   - incremental: true
//   - paths: {"@/*": ["./src/*"]}
// include: ["next-env.d.ts", "**/*.ts", "**/*.tsx"]
// exclude: ["node_modules"]
```

---

#### アクション5-3: Dockerfile作成

**GitHub Copilotへの指示:**

```dockerfile
# ファイル名: frontend/Dockerfile

# Copilotに以下を指示
# Node.js 20-alpine ベースのDockerfileを作成してください
# 手順:
# 1. FROM node:20-alpine
# 2. WORKDIR /app
# 3. package*.jsonをコピーしてnpm ci
# 4. アプリケーションコードをコピー
# 5. EXPOSE 3000
# 6. CMD ["npm", "run", "dev"]
```

---

### ステップ6: 最小限のアプリケーションコード（30分）

#### アクション6-1: backend/app/main.py作成

**GitHub Copilotへの指示:**

```python
# ファイル名: backend/app/main.py

# Copilotに以下を指示
# ZenJP MVP用のFastAPIアプリケーションを作成してください
# 要件:
# - FastAPIインスタンス作成（title="ZenJP MVP API", version="1.0.0"）
# - CORS設定（allow_origins=["http://localhost:3000"]）
# - ルートエンドポイント GET "/" → {"message": "ZenJP MVP API", "version": "1.0.0"}
# - ヘルスチェック GET "/health" → {"status": "ok"}
```

**確認コマンド:**
```bash
cat backend/app/main.py
python3 -m py_compile backend/app/main.py
# エラーが出なければOK
```

---

#### アクション6-2: frontend/src/app/layout.tsx作成

**GitHub Copilotへの指示:**

```typescript
// ファイル名: frontend/src/app/layout.tsx

// Copilotに以下を指示
// Next.js 14 App Router用のルートレイアウトを作成してください
// 要件:
// - export default function RootLayout
// - HTML lang="ja"
// - メタデータ: title="ZenJP MVP", description="日本株スコアリングシステム"
```

---

#### アクション6-3: frontend/src/app/page.tsx作成

**GitHub Copilotへの指示:**

```typescript
// ファイル名: frontend/src/app/page.tsx

// Copilotに以下を指示
// Next.js 14用のホームページを作成してください
// 要件:
// - export default function Home
// - h1: "ZenJP MVP"
// - p: "日本株スコアリングシステム（開発中）"
// - Tailwind CSSを使用
```

---

#### アクション6-4: frontend/src/app/globals.css作成

**コマンド:**
```bash
cat > frontend/src/app/globals.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;
EOF
```

---

#### アクション6-5: next.config.js作成

**GitHub Copilotへの指示:**

```javascript
// ファイル名: frontend/next.config.js

// Copilotに以下を指示
// Next.js 14用のnext.config.jsを作成してください
// 最小限の設定のみ
```

---

#### アクション6-6: tailwind.config.ts作成

**GitHub Copilotへの指示:**

```typescript
// ファイル名: frontend/tailwind.config.ts

// Copilotに以下を指示
// Tailwind CSS用の設定ファイルを作成してください
// content: ['./src/**/*.{js,ts,jsx,tsx,mdx}']
```

---

### ステップ7: Docker起動テスト（30分）

#### アクション7-1: Docker起動

**コマンド:**
```bash
# Docker起動
docker-compose up -d
```

**期待される出力:**
```
Creating network "zenjp-mvp_zenjp-network" ... done
Creating volume "zenjp-mvp_postgres_data" ... done
Creating zenjp_db ... done
Creating zenjp_backend ... done
Creating zenjp_frontend ... done
```

---

#### アクション7-2: コンテナ状態確認

**コマンド:**
```bash
docker-compose ps
```

**期待される出力:**
```
Name                 State    Ports
-----------------------------------------------
zenjp_db           Up       0.0.0.0:5432->5432/tcp
zenjp_backend      Up       0.0.0.0:8000->8000/tcp
zenjp_frontend     Up       0.0.0.0:3000->3000/tcp
```

**確認項目:**
- [ ] 3つのコンテナすべてが "Up" 状態
- [ ] ポートマッピングが正しい

---

#### アクション7-3: ログ確認

**コマンド:**
```bash
# バックエンドログ
docker-compose logs backend | tail -20

# フロントエンドログ
docker-compose logs frontend | tail -20
```

**期待されるキーワード:**
- Backend: `Uvicorn running on http://0.0.0.0:8000`
- Frontend: `ready - started server on 0.0.0.0:3000`

---

#### アクション7-4: APIアクセステスト

**コマンド:**
```bash
# ルートエンドポイント
curl http://localhost:8000/

# ヘルスチェック
curl http://localhost:8000/health

# Swagger UI
open http://localhost:8000/docs
# Windows: start http://localhost:8000/docs
# Linux: xdg-open http://localhost:8000/docs
```

**期待されるレスポンス:**
```json
// GET /
{"message":"ZenJP MVP API","version":"1.0.0"}

// GET /health
{"status":"ok"}
```

---

#### アクション7-5: フロントエンドアクセステスト

**コマンド:**
```bash
open http://localhost:3000
# Windows: start http://localhost:3000
# Linux: xdg-open http://localhost:3000
```

**期待される表示:**
- ページタイトル: "ZenJP MVP"
- テキスト: "日本株スコアリングシステム（開発中）"

---

#### アクション7-6: PostgreSQL接続テスト

**コマンド:**
```bash
# psqlで接続
docker-compose exec db psql -U zenjp -d zenjp_mvp

# または
psql -h localhost -U zenjp -d zenjp_mvp
# パスワード: password
```

**期待されるプロンプト:**
```
zenjp_mvp=#
```

**確認クエリ:**
```sql
SELECT version();
\q
```

---

### ステップ8: README作成（10分）

#### アクション8-1: README.md作成

**GitHub Copilotへの指示:**

```markdown
# ファイル名: README.md

# Copilotに以下を指示
# ZenJP MVP用のREADME.mdを作成してください
# セクション:
# 1. プロジェクト概要
# 2. セットアップ手順（docker-compose up -d）
# 3. アクセスURL（Backend: http://localhost:8000、Frontend: http://localhost:3000）
# 4. 開発コマンド（ログ確認、停止、再起動）
```

---

### Day 1完了確認

#### チェックリスト

```bash
# 以下のコマンドを順に実行して、すべてOKならDay 1完了

# 1. コンテナ確認
docker-compose ps
# → 3コンテナすべてUp

# 2. API確認
curl http://localhost:8000/health
# → {"status":"ok"}

# 3. フロントエンド確認
curl http://localhost:3000
# → HTML が返ってくる

# 4. DB確認
docker-compose exec db psql -U zenjp -d zenjp_mvp -c "SELECT 1;"
# → 1

# すべてOKなら
echo "✅ Day 1 完了！"
```

---

## 4. Day 2: データベース構築

**所要時間:** 3時間  
**目標:** 4テーブル作成、3銘柄登録、型同期完了

---

### ステップ9: database/init.sql作成（45分）

#### アクション9-1: init.sql作成

**GitHub Copilotへの指示:**

```sql
-- ファイル名: database/init.sql

-- Copilotに以下を指示
-- ZenJP MVP用のデータベース初期化SQLを作成してください
-- 
-- テーブル1: stocks（銘柄マスタ）
-- カラム:
--   - stock_code VARCHAR(4) PRIMARY KEY
--   - stock_name VARCHAR(100) NOT NULL
--   - sector_name VARCHAR(50)
--   - market VARCHAR(20)
--   - created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
--   - updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
--
-- テーブル2: stock_prices（株価データ）
-- カラム:
--   - id SERIAL PRIMARY KEY
--   - stock_code VARCHAR(4) NOT NULL
--   - price_date DATE NOT NULL
--   - open_price NUMERIC(10,2)
--   - high_price NUMERIC(10,2)
--   - low_price NUMERIC(10,2)
--   - close_price NUMERIC(10,2) NOT NULL
--   - volume BIGINT
--   - created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
--   - updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- 制約:
--   - FOREIGN KEY (stock_code) REFERENCES stocks(stock_code)
--   - UNIQUE (stock_code, price_date) -- 冪等性保証
-- インデックス:
--   - CREATE INDEX idx_prices_stock_date ON stock_prices(stock_code, price_date DESC);
--
-- テーブル3: stock_financials（財務データ）
-- カラム:
--   - id SERIAL PRIMARY KEY
--   - stock_code VARCHAR(4) NOT NULL
--   - fiscal_period DATE NOT NULL
--   - revenue BIGINT
--   - eps NUMERIC(10,2)
--   - bps NUMERIC(10,2)
--   - dividend NUMERIC(10,2)
--   - created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
--   - updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- 制約:
--   - FOREIGN KEY (stock_code) REFERENCES stocks(stock_code)
--   - UNIQUE (stock_code, fiscal_period)
-- インデックス:
--   - CREATE INDEX idx_financials_stock ON stock_financials(stock_code, fiscal_period DESC);
--
-- テーブル4: daily_scores（日次スコア）
-- カラム:
--   - id SERIAL PRIMARY KEY
--   - stock_code VARCHAR(4) NOT NULL
--   - score_date DATE NOT NULL
--   - total_score NUMERIC(5,2) NOT NULL
--   - rank VARCHAR(2) NOT NULL
--   - value_score NUMERIC(5,2)
--   - growth_score NUMERIC(5,2)
--   - momentum_score NUMERIC(5,2)
--   - details JSONB
--   - created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- 制約:
--   - FOREIGN KEY (stock_code) REFERENCES stocks(stock_code)
--   - UNIQUE (stock_code, score_date)
--   - CHECK (total_score >= 0 AND total_score <= 100)
-- インデックス:
--   - CREATE INDEX idx_scores_stock_date ON daily_scores(stock_code, score_date DESC);
--   - CREATE INDEX idx_scores_date ON daily_scores(score_date DESC);
--
-- 初期データ投入:
-- INSERT INTO stocks (stock_code, stock_name, sector_name, market) VALUES
-- ('7203', 'トヨタ自動車', '輸送用機器', 'プライム'),
-- ('6758', 'ソニーグループ', '電気機器', 'プライム'),
-- ('9984', 'ソフトバンクグループ', '情報・通信業', 'プライム');
```

**確認:**
```bash
cat database/init.sql
wc -l database/init.sql
# 100行程度あればOK
```

---

#### アクション9-2: データベース再起動

**コマンド:**
```bash
# コンテナを停止
docker-compose down

# ボリュームを削除（初期化するため）
docker volume rm zenjp-mvp_postgres_data

# 再起動
docker-compose up -d

# ログでinit.sqlが実行されたか確認
docker-compose logs db | grep "init.sql"
```

---

#### アクション9-3: テーブル作成確認

**コマンド:**
```bash
docker-compose exec db psql -U zenjp -d zenjp_mvp
```

**SQLコマンド:**
```sql
-- テーブル一覧
\dt

-- 期待される出力:
--  public | stocks           | table | zenjp
--  public | stock_prices     | table | zenjp
--  public | stock_financials | table | zenjp
--  public | daily_scores     | table | zenjp

-- 初期データ確認
SELECT * FROM stocks;

-- 期待される出力:
--  7203 | トヨタ自動車
--  6758 | ソニーグループ
--  9984 | ソフトバンクグループ

-- 終了
\q
```

---

### ステップ10: SQLAlchemyモデル作成（60分）

#### アクション10-1: backend/app/database.py作成

**GitHub Copilotへの指示:**

```python
# ファイル名: backend/app/database.py

# Copilotに以下を指示
# SQLAlchemyのデータベース接続設定を作成してください
# 要件:
# - create_engine(DATABASE_URL) を使用
# - SessionLocal = sessionmaker()
# - Base = declarative_base()
# - get_db() 関数（Dependency Injection用）
# - DATABASE_URLは環境変数から取得（os.getenv("DATABASE_URL")）
```

**確認:**
```bash
cat backend/app/database.py
python3 -m py_compile backend/app/database.py
```

---

#### アクション10-2: backend/app/models/stock.py作成

**GitHub Copilotへの指示:**

```python
# ファイル名: backend/app/models/stock.py

# Copilotに以下を指示（プロンプト例2参照）
# このテーブル定義をSQLAlchemyモデルに変換してください:
# 
# CREATE TABLE stocks (
#     stock_code VARCHAR(4) PRIMARY KEY,
#     stock_name VARCHAR(100) NOT NULL,
#     sector_name VARCHAR(50),
#     market VARCHAR(20),
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );
#
# クラス名: Stock
# from app.database import Base を使用
# server_default と onupdate を適切に設定
```

**確認:**
```bash
cat backend/app/models/stock.py
python3 -c "from backend.app.models.stock import Stock; print('OK')"
```

---

#### アクション10-3: backend/app/models/price.py作成

**GitHub Copilotへの指示:**

```python
# ファイル名: backend/app/models/price.py

# Copilotに以下を指示
# stock_prices テーブルのSQLAlchemyモデルを作成してください
# クラス名: StockPrice
# リレーション: stock = relationship("Stock", back_populates="prices")
# UniqueConstraint: (stock_code, price_date)
```

---

#### アクション10-4: backend/app/models/financial.py作成

**GitHub Copilotへの指示:**

```python
# ファイル名: backend/app/models/financial.py

# Copilotに以下を指示
# stock_financials テーブルのSQLAlchemyモデルを作成してください
# クラス名: StockFinancial
# リレーション: stock = relationship("Stock", back_populates="financials")
# UniqueConstraint: (stock_code, fiscal_period)
```

---

#### アクション10-5: backend/app/models/score.py作成

**GitHub Copilotへの指示:**

```python
# ファイル名: backend/app/models/score.py

# Copilotに以下を指示
# daily_scores テーブルのSQLAlchemyモデルを作成してください
# クラス名: DailyScore
# リレーション: stock = relationship("Stock", back_populates="scores")
# UniqueConstraint: (stock_code, score_date)
# CheckConstraint: total_score BETWEEN 0 AND 100
# details カラムは JSONB型（from sqlalchemy.dialects.postgresql import JSONB）
```

---

### ステップ11: Pydanticスキーマ作成（60分）

**🤖 AI活用のポイント:**

SQLAlchemyモデルができたら、Copilotに「このモデルをPydanticスキーマに変換して」と指示するだけで自動生成できます。

---

#### アクション11-1: backend/app/schemas/stock.py作成

**GitHub Copilotへの指示:**

```python
# ファイル名: backend/app/schemas/stock.py

# Copilotに以下を指示（プロンプト例2参照）
# backend/app/models/stock.py のStockモデルをPydanticスキーマに変換してください
# 
# 必要なスキーマ:
# 1. StockBase: 基本フィールド（stock_code, stock_name, sector_name, market）
# 2. StockCreate: 作成用（StockBaseを継承）
# 3. StockResponse: レスポンス用（StockBase + created_at, updated_at）
#    - Config: from_attributes = True
# 
# from pydantic import BaseModel, Field
# from datetime import datetime
```

**確認:**
```bash
cat backend/app/schemas/stock.py
python3 -m py_compile backend/app/schemas/stock.py
```

---

#### アクション11-2: backend/app/schemas/price.py作成

**GitHub Copilotへの指示:**

```python
# ファイル名: backend/app/schemas/price.py

# Copilotに以下を指示
# backend/app/models/price.py のStockPriceモデルをPydanticスキーマに変換してください
# スキーマ:
# 1. StockPriceBase
# 2. StockPriceCreate
# 3. StockPriceResponse
```

---

#### アクション11-3: backend/app/schemas/financial.py作成

**GitHub Copilotへの指示:**

```python
# ファイル名: backend/app/schemas/financial.py

# Copilotに以下を指示
# backend/app/models/financial.py のStockFinancialモデルをPydanticスキーマに変換してください
# スキーマ:
# 1. StockFinancialBase
# 2. StockFinancialCreate
# 3. StockFinancialResponse
```

---

#### アクション11-4: backend/app/schemas/score.py作成

**GitHub Copilotへの指示:**

```python
# ファイル名: backend/app/schemas/score.py

# Copilotに以下を指示
# backend/app/models/score.py のDailyScoreモデルをPydanticスキーマに変換してください
# スキーマ:
# 1. DailyScoreBase
# 2. DailyScoreCreate
# 3. DailyScoreResponse
# details: dict | None = None（JSONBフィールド）
```

---

### ステップ12: 動作確認（15分）

#### アクション12-1: Pythonインタラクティブシェルでテスト

**コマンド:**
```bash
docker-compose exec backend python
```

**Pythonコード:**
```python
# モデルのインポートテスト
from app.models.stock import Stock
from app.models.price import StockPrice
from app.models.financial import StockFinancial
from app.models.score import DailyScore

# スキーマのインポートテスト
from app.schemas.stock import StockResponse
from app.schemas.price import StockPriceResponse
from app.schemas.financial import StockFinancialResponse
from app.schemas.score import DailyScoreResponse

# データベース接続テスト
from app.database import engine, SessionLocal
from sqlalchemy import text

db = SessionLocal()
result = db.execute(text("SELECT * FROM stocks"))
for row in result:
    print(row)

db.close()

# Ctrl+D で終了
```

**期待される出力:**
```
(7203, 'トヨタ自動車', '輸送用機器', 'プライム', ...)
(6758, 'ソニーグループ', '電気機器', 'プライム', ...)
(9984, 'ソフトバンクグループ', '情報・通信業', 'プライム', ...)
```

---

### Day 2完了確認

#### チェックリスト

```bash
# 1. テーブル確認
docker-compose exec db psql -U zenjp -d zenjp_mvp -c "\dt"
# → 4テーブル

# 2. 初期データ確認
docker-compose exec db psql -U zenjp -d zenjp_mvp -c "SELECT COUNT(*) FROM stocks;"
# → 3

# 3. モデル確認
docker-compose exec backend python -c "from app.models.stock import Stock; print('OK')"
# → OK

# 4. スキーマ確認
docker-compose exec backend python -c "from app.schemas.stock import StockResponse; print('OK')"
# → OK

# すべてOKなら
echo "✅ Day 2 完了！"
```

---

## 5. 完了確認

### PHASE1完了チェックリスト

```bash
# 最終確認スクリプト
cat > check_phase1.sh << 'EOF'
#!/bin/bash

echo "=== ZenJP MVP PHASE1 完了確認 ==="
echo ""

# 1. Docker確認
echo "1. Docker コンテナ確認"
docker-compose ps | grep -q "Up" && echo "✅ Docker起動OK" || echo "❌ Docker起動NG"
echo ""

# 2. API確認
echo "2. API確認"
curl -s http://localhost:8000/health | grep -q "ok" && echo "✅ API動作OK" || echo "❌ API動作NG"
echo ""

# 3. Frontend確認
echo "3. Frontend確認"
curl -s http://localhost:3000 | grep -q "ZenJP" && echo "✅ Frontend動作OK" || echo "❌ Frontend動作NG"
echo ""

# 4. Database確認
echo "4. Database確認"
docker-compose exec -T db psql -U zenjp -d zenjp_mvp -c "SELECT COUNT(*) FROM stocks;" | grep -q "3" && echo "✅ Database OK" || echo "❌ Database NG"
echo ""

# 5. モデル確認
echo "5. SQLAlchemyモデル確認"
docker-compose exec -T backend python -c "from app.models.stock import Stock; print('OK')" 2>&1 | grep -q "OK" && echo "✅ Models OK" || echo "❌ Models NG"
echo ""

# 6. スキーマ確認
echo "6. Pydanticスキーマ確認"
docker-compose exec -T backend python -c "from app.schemas.stock import StockResponse; print('OK')" 2>&1 | grep -q "OK" && echo "✅ Schemas OK" || echo "❌ Schemas NG"
echo ""

echo "=== 確認完了 ==="
EOF

chmod +x check_phase1.sh
./check_phase1.sh
```

---

### 完了報告フォーマット

```markdown
## PHASE1完了報告

**実施日:** 2026年X月X日  
**担当:** 末告さん  
**所要時間:** X時間

### 成果物

- ✅ docker-compose.yml
- ✅ backend/Dockerfile
- ✅ frontend/Dockerfile
- ✅ database/init.sql
- ✅ 4つのSQLAlchemyモデル
- ✅ 4つのPydanticスキーマ

### 動作確認

- ✅ Docker 3コンテナ起動
- ✅ API動作確認
- ✅ Frontend動作確認
- ✅ Database接続確認
- ✅ 型定義同期確認

### 次のステップ

PHASE2（データ取得）の準備完了
```

---

## 6. トラブルシューティング

### 問題1: `port 5432 already in use`

**原因:** ローカルにPostgreSQLが既にインストールされている

**解決策:**
```bash
# ローカルPostgreSQLを停止
sudo systemctl stop postgresql  # Linux
brew services stop postgresql   # macOS

# または docker-compose.yml のポート変更
# ports を "5433:5432" に変更
```

---

### 問題2: `backend | Error: No module named 'app'`

**原因:** backend/app/__init__.py が存在しない

**解決策:**
```bash
touch backend/app/__init__.py
docker-compose restart backend
```

---

### 問題3: `frontend | Module not found: Can't resolve 'next'`

**原因:** package.json が正しくない、またはnode_modules未インストール

**解決策:**
```bash
# コンテナ内でnpm install実行
docker-compose exec frontend npm install

# または再ビルド
docker-compose down
docker-compose build frontend
docker-compose up -d
```

---

### 問題4: `database | init.sql: syntax error`

**原因:** SQLの構文エラー

**解決策:**
```bash
# init.sqlを確認
cat database/init.sql

# エラー箇所を修正後、DBを再初期化
docker-compose down
docker volume rm zenjp-mvp_postgres_data
docker-compose up -d
```

---

### 問題5: 型定義の不一致

**原因:** SQLAlchemyとPydanticの型が一致していない

**解決策:**

```python
# Copilotに再変換を依頼
# 「このSQLAlchemyモデルをPydanticスキーマに再変換してください。
#  型定義を完全に一致させてください」
```

---

## 付録A: コマンドクイックリファレンス

### Docker操作

```bash
# 起動
docker-compose up -d

# 停止
docker-compose down

# 再起動
docker-compose restart

# ログ確認
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db

# ビルド
docker-compose build

# クリーンビルド
docker-compose build --no-cache

# ボリューム削除
docker volume rm zenjp-mvp_postgres_data
```

---

### Database操作

```bash
# psql接続
docker-compose exec db psql -U zenjp -d zenjp_mvp

# SQLファイル実行
docker-compose exec -T db psql -U zenjp -d zenjp_mvp < database/init.sql

# クエリ実行
docker-compose exec db psql -U zenjp -d zenjp_mvp -c "SELECT * FROM stocks;"
```

---

### Backend操作

```bash
# Pythonシェル
docker-compose exec backend python

# モジュールインポートテスト
docker-compose exec backend python -c "from app.models.stock import Stock"

# requirements.txtインストール
docker-compose exec backend pip install -r requirements.txt
```

---

### Frontend操作

```bash
# npm install
docker-compose exec frontend npm install

# パッケージ追加
docker-compose exec frontend npm install パッケージ名
```

---

## 付録B: GitHub Copilotプロンプトテンプレート

### SQL生成

```
PostgreSQL用のCREATE TABLE文を生成してください。
テーブル名: [テーブル名]
カラム:
- [カラム名] [型] [制約]
- ...
制約:
- FOREIGN KEY ...
- UNIQUE ...
インデックス:
- CREATE INDEX ...
```

---

### SQLAlchemy→Pydantic変換

```
このSQLAlchemyモデルをPydanticスキーマに変換してください:

[SQLAlchemyモデルのコード]

必要なスキーマ:
1. [モデル名]Base
2. [モデル名]Create
3. [モデル名]Response (Config: from_attributes = True)
```

---

### Dockerfile生成

```
[言語/フレームワーク]用のDockerfileを作成してください。
ベースイメージ: [イメージ名]
手順:
1. WORKDIR設定
2. 依存関係インストール
3. アプリケーションコピー
4. ポート公開
5. 起動コマンド
```

---

## 変更履歴

| Version | 日付 | 変更内容 | 作成者 |
|---------|------|---------|--------|
| 1.0.0 | 2026-02-03 | 初版作成 | ZenJP Team |

---

**ZenJP MVP PHASE1 実装アクション詳細計画書 完成**

**次のステップ:** Day 1 ステップ1から実装開始！
