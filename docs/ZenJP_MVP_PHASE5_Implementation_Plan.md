# ZenJP MVP PHASE5 実装アクション詳細計画書

**Version:** 1.0.0  
**作成日:** 2026年2月4日  
**対象期間:** 2026年2月13日(金) 〜 2026年2月15日(日) = Day 10-12  
**総所要時間:** 12時間（Day 10: 3.5h / Day 11: 3.5h / Day 12: 5h）  
**基準文書:** ZenJP MVP 実装計画書 v1.1.0

---

## 📋 目次

1. [PHASE5概要](#1-phase5概要)
2. [前提条件・準備](#2-前提条件準備)
3. [Day 10: UI基礎実装](#3-day-10-ui基礎実装)
4. [Day 11: UIコンポーネント実装](#4-day-11-uiコンポーネント実装)
5. [Day 12: UI完成・洗練化](#5-day-12-ui完成洗練化)
6. [検証・品質基準](#6-検証品質基準)
7. [トラブルシューティング](#7-トラブルシューティング)

---

## 1. PHASE5概要

### 1.1 目的

FastAPIバックエンドと連携するNext.js + TypeScript + Tailwind CSSフロントエンドを実装し、3銘柄のスコアを視覚的に表示する。

### 1.2 成果物

| 成果物 | 説明 |
|-------|------|
| `frontend/` ディレクトリ | Next.js 14プロジェクト全体 |
| `src/components/ScoreCard.tsx` | スコア表示カード（アニメーション付き） |
| `src/components/CategoryBar.tsx` | カテゴリ別スコアバー |
| `src/components/DetailTable.tsx` | 詳細データテーブル |
| `src/app/page.tsx` | メインページ |
| `src/types/score.ts` | TypeScript型定義 |

### 1.3 技術スタック

- **フレームワーク:** Next.js 14 (App Router)
- **言語:** TypeScript 5.x
- **スタイリング:** Tailwind CSS 3.x
- **アニメーション:** Framer Motion
- **API通信:** fetch API
- **状態管理:** React useState/useEffect

### 1.4 AI活用戦略

| タスク | 従来時間 | AI活用後 | 削減率 | AI活用方法 |
|--------|---------|---------|--------|-----------|
| Next.jsプロジェクト初期化 | 30分 | 20分 | -33% | ベストプラクティス設定生成 |
| TypeScript型定義 | 40分 | 15分 | -63% | Python型から自動変換 |
| ScoreCard実装 | 60分 | 30分 | -50% | Tailwindコンポーネント生成 |
| CategoryBar実装 | 50分 | 25分 | -50% | 同上 |
| DetailTable実装 | 45分 | 25分 | -44% | 同上 |
| レスポンシブ対応 | 40分 | 15分 | -63% | 一括最適化 |
| アニメーション追加 | 新規 | 30分 | - | Framer Motion実装 |

---

## 2. 前提条件・準備

### 2.1 完了している必要があるPhase

- ✅ **Phase 1-2:** 環境構築・DB完了
- ✅ **Phase 3:** データ取得完了（90件株価 + 3件財務）
- ✅ **Phase 4:** API実装完了（`GET /api/score/{stock_code}`が稼働）

### 2.2 事前確認コマンド

```bash
# APIが稼働しているか確認
curl http://localhost:8000/api/score/7203 | jq

# 期待されるレスポンス例
{
  "stock_code": "7203",
  "stock_name": "トヨタ自動車",
  "total_score": 78.5,
  "rank": "B+",
  "value_score": 62.3,
  "growth_score": 71.2,
  "momentum_score": 85.8,
  "market_avg_diff": 28.5,
  "score_date": "2026-01-31"
}
```

### 2.3 必要なツール

```bash
# Node.js 18.x以上
node --version  # v18.x 以上

# npm 9.x以上
npm --version   # v9.x 以上

# Claude/Cursor/GitHub Copilot（いずれか1つ以上）
# - プロンプト例は本ドキュメントに記載
```

### 2.4 ディレクトリ構成（予定）

```
zenjp-mvp/
├── backend/           # (既存)
│   ├── app/
│   └── ...
├── frontend/          # (新規作成)
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx          # メインページ
│   │   │   ├── layout.tsx        # レイアウト
│   │   │   └── globals.css       # グローバルCSS
│   │   ├── components/
│   │   │   ├── ScoreCard.tsx     # スコアカード
│   │   │   ├── CategoryBar.tsx   # カテゴリバー
│   │   │   └── DetailTable.tsx   # 詳細テーブル
│   │   └── types/
│   │       └── score.ts          # 型定義
│   ├── public/                   # 静的ファイル
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── next.config.js
└── docker-compose.yml # (既存)
```

---

## 3. Day 10: UI基礎実装

**日時:** 2026年2月13日(金)  
**所要時間:** 3.5時間  
**目標:** Next.jsプロジェクト初期化、型定義、基本ページ構築

---

### タスク 10.1: Next.jsプロジェクト初期化（20分）

#### 手順

```bash
# プロジェクトディレクトリに移動
cd ~/zenjp-mvp

# Next.jsプロジェクト作成
npx create-next-app@latest frontend --typescript --tailwind --app --use-npm

# プロンプトへの回答例:
# ✔ Would you like to use ESLint? … Yes
# ✔ Would you like to use `src/` directory? … Yes
# ✔ Would you like to use App Router? … Yes
# ✔ Would you like to customize the default import alias? … No
```

#### AI活用プロンプト例

```
【プロンプト: Next.js設定最適化】
以下の要件に基づいて、Next.js 14のベストプラクティス設定を生成してください:

要件:
- TypeScript厳格モード
- Tailwind CSS最適化
- 絶対パス import設定（@/で始まる）
- 本番環境でのソースマップ無効化
- API呼び出し先: http://localhost:8000

生成ファイル:
1. next.config.js
2. tsconfig.json（compilerOptions最適化）
3. .env.local（環境変数設定）
```

#### 検証

```bash
cd frontend
npm run dev
# ブラウザで http://localhost:3000 を開き、デフォルトページが表示されることを確認
```

#### 成果物

- `frontend/` ディレクトリ
- `package.json`
- `next.config.js`
- `tsconfig.json`

---

### タスク 10.2: TypeScript型定義作成（15分）

#### 手順

```bash
cd frontend/src
mkdir types
touch types/score.ts
```

#### AI活用プロンプト例

```
【プロンプト: Python型定義からTypeScript型定義への変換】
以下のPydanticスキーマをTypeScript型定義に変換してください:

from pydantic import BaseModel
from datetime import date

class ScoreResponse(BaseModel):
    stock_code: str
    stock_name: str
    total_score: float
    rank: str
    value_score: float
    growth_score: float
    momentum_score: float
    market_avg_diff: float
    score_date: date

要件:
- エクスポート可能なinterfaceとして定義
- date型はstring型に変換（ISO 8601形式）
- すべてのフィールドを必須とする
- ランク型を 'A+' | 'A' | 'B+' | 'B' | 'C+' | 'C' | 'D' のユニオン型で定義
```

#### 期待される出力（`src/types/score.ts`）

```typescript
export type Rank = 'A+' | 'A' | 'B+' | 'B' | 'C+' | 'C' | 'D';

export interface ScoreResponse {
  stock_code: string;
  stock_name: string;
  total_score: number;
  rank: Rank;
  value_score: number;
  growth_score: number;
  momentum_score: number;
  market_avg_diff: number;
  score_date: string; // ISO 8601形式
}
```

#### 検証

```bash
# TypeScript型エラーがないことを確認
npm run build
```

#### 成果物

- `src/types/score.ts`

---

### タスク 10.3: API通信関数作成（25分）

#### 手順

```bash
mkdir src/lib
touch src/lib/api.ts
```

#### 実装内容（`src/lib/api.ts`）

```typescript
import { ScoreResponse } from '@/types/score';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchScore(stockCode: string): Promise<ScoreResponse> {
  const response = await fetch(`${API_BASE_URL}/api/score/${stockCode}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    cache: 'no-store', // 常に最新データを取得
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

export async function fetchMultipleScores(
  stockCodes: string[]
): Promise<ScoreResponse[]> {
  const promises = stockCodes.map(code => fetchScore(code));
  return Promise.all(promises);
}
```

#### 環境変数設定（`.env.local`）

```bash
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### 検証

```bash
# 開発サーバー再起動
npm run dev

# ブラウザコンソールでテスト
# F12 > Console > 以下を実行
# import { fetchScore } from '@/lib/api';
# await fetchScore('7203');
```

#### 成果物

- `src/lib/api.ts`
- `.env.local`

---

### タスク 10.4: グローバルCSS設定（15分）

#### 実装内容（`src/app/globals.css`）

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;
    --radius: 0.5rem;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground font-sans antialiased;
  }
}

@layer utilities {
  .text-balance {
    text-wrap: balance;
  }
}
```

#### Tailwind設定（`tailwind.config.ts`）

```typescript
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
    },
  },
  plugins: [],
}
export default config
```

#### 検証

```bash
npm run dev
# ブラウザで色が適用されていることを確認
```

#### 成果物

- `src/app/globals.css`（更新）
- `tailwind.config.ts`（更新）

---

### タスク 10.5: 基本レイアウト構築（30分）

#### 実装内容（`src/app/layout.tsx`）

```typescript
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'ZenJP - 日本株スコアリングシステム',
  description: '日本株をValue/Growth/Momentumの3軸で評価',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body className={inter.className}>
        <div className="min-h-screen bg-gray-50">
          <header className="bg-white shadow-sm">
            <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
              <h1 className="text-2xl font-bold text-gray-900">ZenJP</h1>
              <p className="text-sm text-gray-600">日本株スコアリングシステム MVP</p>
            </div>
          </header>
          <main>{children}</main>
          <footer className="bg-white border-t mt-12">
            <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
              <p className="text-center text-sm text-gray-500">
                © 2026 ZenJP. All rights reserved.
              </p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  )
}
```

#### 検証

```bash
npm run dev
# http://localhost:3000 でヘッダー・フッターが表示されることを確認
```

#### 成果物

- `src/app/layout.tsx`（更新）

---

### タスク 10.6: メインページ骨組み作成（30分）

#### 実装内容（`src/app/page.tsx`）

```typescript
'use client';

import { useEffect, useState } from 'react';
import { ScoreResponse } from '@/types/score';
import { fetchMultipleScores } from '@/lib/api';

const TARGET_STOCKS = ['7203', '6758', '9984']; // トヨタ、ソニー、ソフトバンク

export default function Home() {
  const [scores, setScores] = useState<ScoreResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadScores() {
      try {
        setLoading(true);
        const data = await fetchMultipleScores(TARGET_STOCKS);
        setScores(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : '不明なエラー');
      } finally {
        setLoading(false);
      }
    }

    loadScores();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]"></div>
          <p className="mt-2 text-gray-600">データを読み込み中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">エラー: {error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900">スコアダッシュボード</h2>
        <p className="mt-2 text-gray-600">
          更新日: {scores[0]?.score_date || 'N/A'}
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {scores.map((score) => (
          <div
            key={score.stock_code}
            className="bg-white rounded-lg shadow p-6"
          >
            <h3 className="text-xl font-semibold">{score.stock_name}</h3>
            <p className="text-gray-500">({score.stock_code})</p>
            <div className="mt-4">
              <p className="text-4xl font-bold">{score.total_score.toFixed(1)}</p>
              <p className="text-gray-600">総合スコア</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

#### 検証

```bash
npm run dev
# http://localhost:3000 で3銘柄の基本情報が表示されることを確認
```

#### 成果物

- `src/app/page.tsx`（実装完了）

---

### タスク 10.7: Day 10完了確認（15分）

#### チェックリスト

- [ ] Next.jsプロジェクトが正常に起動する
- [ ] TypeScript型定義が正しく作成されている
- [ ] API通信関数が動作する
- [ ] 3銘柄のデータが取得・表示される
- [ ] ヘッダー・フッターが表示される
- [ ] レスポンシブデザインの基礎が機能する

#### 検証コマンド

```bash
# ビルドエラーがないことを確認
cd frontend
npm run build

# 型チェック
npx tsc --noEmit

# 開発サーバー起動
npm run dev
```

#### 完了基準

- すべてのチェックリストがクリア
- ビルドエラーなし
- ブラウザで3銘柄が表示される

---

## 4. Day 11: UIコンポーネント実装

**日時:** 2026年2月14日(土)  
**所要時間:** 3.5時間  
**目標:** ScoreCard、CategoryBar、DetailTableコンポーネント実装

---

### タスク 11.1: ScoreCardコンポーネント実装（30分）

#### 手順

```bash
cd frontend/src/components
touch ScoreCard.tsx
```

#### AI活用プロンプト例

```
【プロンプト: ScoreCard実装】
以下の要件で、Reactコンポーネント（TypeScript + Tailwind CSS）を実装してください:

コンポーネント名: ScoreCard
Props型定義:
interface ScoreCardProps {
  score: ScoreResponse;
}

要件:
1. 総合スコアを大きく表示（例: 78.5点）
2. ランクを色分けして表示
   - A+/A: 緑系（bg-green-100, text-green-800）
   - B+/B: 青系（bg-blue-100, text-blue-800）
   - C+/C: 黄色系（bg-yellow-100, text-yellow-800）
   - D: 赤系（bg-red-100, text-red-800）
3. 市場平均との差分を表示（+28.5点など）
   - プラスは緑、マイナスは赤
4. 銘柄名と銘柄コードを上部に表示
5. 更新日時を右下に小さく表示

デザインテイスト: Apple風のクリーンで洗練されたデザイン
レスポンシブ: モバイル・デスクトップ両対応
```

#### 期待される実装（`src/components/ScoreCard.tsx`）

```typescript
import { ScoreResponse, Rank } from '@/types/score';

interface ScoreCardProps {
  score: ScoreResponse;
}

function getRankColor(rank: Rank): string {
  const colorMap: Record<Rank, string> = {
    'A+': 'bg-green-100 text-green-800',
    'A': 'bg-green-100 text-green-800',
    'B+': 'bg-blue-100 text-blue-800',
    'B': 'bg-blue-100 text-blue-800',
    'C+': 'bg-yellow-100 text-yellow-800',
    'C': 'bg-yellow-100 text-yellow-800',
    'D': 'bg-red-100 text-red-800',
  };
  return colorMap[rank];
}

export default function ScoreCard({ score }: ScoreCardProps) {
  const isPositiveDiff = score.market_avg_diff > 0;

  return (
    <div className="bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow duration-300 p-6 relative">
      {/* ヘッダー */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-xl font-bold text-gray-900">{score.stock_name}</h3>
          <p className="text-sm text-gray-500">({score.stock_code})</p>
        </div>
        <span
          className={`px-3 py-1 rounded-full text-sm font-semibold ${getRankColor(
            score.rank
          )}`}
        >
          {score.rank}
        </span>
      </div>

      {/* 総合スコア */}
      <div className="text-center my-6">
        <p className="text-5xl font-bold text-gray-900">
          {score.total_score.toFixed(1)}
        </p>
        <p className="text-sm text-gray-600 mt-1">総合スコア</p>
      </div>

      {/* 市場平均との差分 */}
      <div className="flex items-center justify-center gap-2">
        <span className="text-sm text-gray-600">市場平均</span>
        <span
          className={`text-lg font-semibold ${
            isPositiveDiff ? 'text-green-600' : 'text-red-600'
          }`}
        >
          {isPositiveDiff ? '+' : ''}
          {score.market_avg_diff.toFixed(1)}
        </span>
      </div>

      {/* 更新日時 */}
      <div className="absolute bottom-4 right-4">
        <p className="text-xs text-gray-400">{score.score_date}</p>
      </div>
    </div>
  );
}
```

#### 検証

```bash
# src/app/page.tsx で ScoreCard を import して表示
npm run dev
```

#### 成果物

- `src/components/ScoreCard.tsx`

---

### タスク 11.2: CategoryBarコンポーネント実装（25分）

#### 手順

```bash
touch src/components/CategoryBar.tsx
```

#### AI活用プロンプト例

```
【プロンプト: CategoryBar実装】
以下の要件で、Reactコンポーネント（TypeScript + Tailwind CSS）を実装してください:

コンポーネント名: CategoryBar
Props型定義:
interface CategoryBarProps {
  label: string;
  score: number;
  color: 'value' | 'growth' | 'momentum';
}

要件:
1. ラベル（Value/Growth/Momentum）を左に表示
2. スコア（0-100点）をプログレスバーで表示
3. 色分け:
   - value: 青系（bg-blue-500）
   - growth: 緑系（bg-green-500）
   - momentum: 紫系（bg-purple-500）
4. スコア数値を右端に表示
5. バーの幅はスコアに応じて0-100%
6. アニメーション: バーが左から右に伸びる（transition）

レスポンシブ: モバイル・デスクトップ両対応
```

#### 期待される実装（`src/components/CategoryBar.tsx`）

```typescript
interface CategoryBarProps {
  label: string;
  score: number;
  color: 'value' | 'growth' | 'momentum';
}

function getColorClass(color: CategoryBarProps['color']): string {
  const colorMap = {
    value: 'bg-blue-500',
    growth: 'bg-green-500',
    momentum: 'bg-purple-500',
  };
  return colorMap[color];
}

export default function CategoryBar({ label, score, color }: CategoryBarProps) {
  return (
    <div className="mb-4">
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm font-medium text-gray-700">{label}</span>
        <span className="text-sm font-semibold text-gray-900">
          {score.toFixed(1)}
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
        <div
          className={`h-full ${getColorClass(color)} transition-all duration-1000 ease-out`}
          style={{ width: `${score}%` }}
        ></div>
      </div>
    </div>
  );
}
```

#### 検証

```bash
npm run dev
# ブラウザで3つのバーが表示されることを確認
```

#### 成果物

- `src/components/CategoryBar.tsx`

---

### タスク 11.3: DetailTableコンポーネント実装（25分）

#### 手順

```bash
touch src/components/DetailTable.tsx
```

#### AI活用プロンプト例

```
【プロンプト: DetailTable実装】
以下の要件で、Reactコンポーネント（TypeScript + Tailwind CSS）を実装してください:

コンポーネント名: DetailTable
Props型定義:
interface DetailTableProps {
  score: ScoreResponse;
}

要件:
1. スコア詳細をテーブル形式で表示:
   - 総合スコア
   - Valueスコア
   - Growthスコア
   - Momentumスコア
   - ランク
   - 市場平均との差分
2. 2カラムレイアウト（項目名 | 値）
3. ストライプ背景（zebra stripes）
4. 数値は小数点第1位まで表示
5. 市場平均差分はプラス/マイナスで色分け

デザインテイスト: シンプルで読みやすいテーブル
レスポンシブ: モバイル・デスクトップ両対応
```

#### 期待される実装（`src/components/DetailTable.tsx`）

```typescript
import { ScoreResponse } from '@/types/score';

interface DetailTableProps {
  score: ScoreResponse;
}

export default function DetailTable({ score }: DetailTableProps) {
  const isPositiveDiff = score.market_avg_diff > 0;

  const rows = [
    { label: '総合スコア', value: score.total_score.toFixed(1) },
    { label: 'Valueスコア', value: score.value_score.toFixed(1) },
    { label: 'Growthスコア', value: score.growth_score.toFixed(1) },
    { label: 'Momentumスコア', value: score.momentum_score.toFixed(1) },
    { label: 'ランク', value: score.rank },
    {
      label: '市場平均差分',
      value: `${isPositiveDiff ? '+' : ''}${score.market_avg_diff.toFixed(1)}`,
      valueClass: isPositiveDiff ? 'text-green-600' : 'text-red-600',
    },
  ];

  return (
    <div className="overflow-hidden rounded-lg border border-gray-200">
      <table className="min-w-full divide-y divide-gray-200">
        <tbody className="divide-y divide-gray-200 bg-white">
          {rows.map((row, index) => (
            <tr key={row.label} className={index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
              <td className="px-6 py-3 text-sm font-medium text-gray-900">
                {row.label}
              </td>
              <td
                className={`px-6 py-3 text-sm font-semibold text-right ${
                  row.valueClass || 'text-gray-900'
                }`}
              >
                {row.value}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

#### 検証

```bash
npm run dev
# 詳細テーブルが正しく表示されることを確認
```

#### 成果物

- `src/components/DetailTable.tsx`

---

### タスク 11.4: メインページへのコンポーネント統合（30分）

#### 実装内容（`src/app/page.tsx`を更新）

```typescript
'use client';

import { useEffect, useState } from 'react';
import { ScoreResponse } from '@/types/score';
import { fetchMultipleScores } from '@/lib/api';
import ScoreCard from '@/components/ScoreCard';
import CategoryBar from '@/components/CategoryBar';
import DetailTable from '@/components/DetailTable';

const TARGET_STOCKS = ['7203', '6758', '9984'];

export default function Home() {
  const [scores, setScores] = useState<ScoreResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedStock, setSelectedStock] = useState<ScoreResponse | null>(null);

  useEffect(() => {
    async function loadScores() {
      try {
        setLoading(true);
        const data = await fetchMultipleScores(TARGET_STOCKS);
        setScores(data);
        if (data.length > 0) {
          setSelectedStock(data[0]);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : '不明なエラー');
      } finally {
        setLoading(false);
      }
    }

    loadScores();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent"></div>
          <p className="mt-2 text-gray-600">データを読み込み中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">エラー: {error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900">スコアダッシュボード</h2>
        <p className="mt-2 text-gray-600">
          更新日: {scores[0]?.score_date || 'N/A'}
        </p>
      </div>

      {/* スコアカード一覧 */}
      <div className="grid grid-cols-1 gap-6 mb-8 lg:grid-cols-3">
        {scores.map((score) => (
          <div key={score.stock_code} onClick={() => setSelectedStock(score)} className="cursor-pointer">
            <ScoreCard score={score} />
          </div>
        ))}
      </div>

      {/* 選択された銘柄の詳細 */}
      {selectedStock && (
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="text-2xl font-bold mb-6">
            {selectedStock.stock_name} 詳細
          </h3>

          {/* カテゴリバー */}
          <div className="mb-8">
            <h4 className="text-lg font-semibold mb-4">カテゴリ別スコア</h4>
            <CategoryBar label="Value" score={selectedStock.value_score} color="value" />
            <CategoryBar label="Growth" score={selectedStock.growth_score} color="growth" />
            <CategoryBar label="Momentum" score={selectedStock.momentum_score} color="momentum" />
          </div>

          {/* 詳細テーブル */}
          <div>
            <h4 className="text-lg font-semibold mb-4">スコア詳細</h4>
            <DetailTable score={selectedStock} />
          </div>
        </div>
      )}
    </div>
  );
}
```

#### 検証

```bash
npm run dev
# - 3銘柄のカードが表示される
# - カードをクリックすると詳細が表示される
# - カテゴリバーが色分けされている
# - 詳細テーブルが正しく表示される
```

#### 成果物

- `src/app/page.tsx`（更新）

---

### タスク 11.5: レスポンシブ対応確認（15分）

#### AI活用プロンプト例

```
【プロンプト: レスポンシブ最適化】
以下のNext.jsページコンポーネントをレスポンシブ対応に最適化してください:

現在の実装:
- grid-cols-1 lg:grid-cols-3（カード一覧）
- px-4 sm:px-6 lg:px-8（パディング）

追加要件:
1. モバイル（<640px）: 1カラム、パディング小
2. タブレット（640px-1024px）: 2カラム、パディング中
3. デスクトップ（>1024px）: 3カラム、パディング大
4. スコアカードのフォントサイズもレスポンシブ化
5. 詳細テーブルのスクロール対応（モバイル）

最適化してください。
```

#### 検証コマンド

```bash
# ブラウザのDevToolsでレスポンシブモード確認
# 320px, 768px, 1440px の各幅で確認
```

#### 成果物

- レスポンシブ対応完了

---

### タスク 11.6: Day 11完了確認（30分）

#### チェックリスト

- [ ] ScoreCardコンポーネントが正しく動作する
- [ ] CategoryBarコンポーネントが正しく動作する
- [ ] DetailTableコンポーネントが正しく動作する
- [ ] 3銘柄すべてのデータが表示される
- [ ] クリックで詳細表示が切り替わる
- [ ] レスポンシブデザインが機能する

#### 検証コマンド

```bash
npm run build
npm run dev
```

#### 完了基準

- すべてのコンポーネントが表示される
- インタラクションが正常動作する
- モバイル・デスクトップで表示が崩れない

---

## 5. Day 12: UI完成・洗練化

**日時:** 2026年2月15日(日)  
**所要時間:** 5時間  
**目標:** アニメーション追加、ホバーエフェクト、最終調整、スクリーンショット取得

---

### タスク 12.1: Framer Motionインストール（10分）

#### 手順

```bash
cd frontend
npm install framer-motion
```

#### 検証

```bash
npm list framer-motion
# framer-motion@x.x.x と表示されることを確認
```

#### 成果物

- `package.json`に`framer-motion`が追加

---

### タスク 12.2: ScoreCardにカウントアップアニメーション追加（30分）

#### AI活用プロンプト例

```
【プロンプト: スコアアニメーション追加】
ScoreCardコンポーネントに、スコアがカウントアップするアニメーションを追加してください:

要件:
1. Framer Motionを使用
2. スコアが0から実際の値まで1.5秒でカウントアップ
3. イージング: easeOut
4. コンポーネントがマウント時に1回だけ実行
5. useMotionValueとuseTransformを使用

現在のコード:
<p className="text-5xl font-bold text-gray-900">
  {score.total_score.toFixed(1)}
</p>

これを動的にカウントアップするように改修してください。
```

#### 期待される実装（`src/components/ScoreCard.tsx`を更新）

```typescript
import { ScoreResponse, Rank } from '@/types/score';
import { motion, useMotionValue, useTransform, animate } from 'framer-motion';
import { useEffect } from 'react';

interface ScoreCardProps {
  score: ScoreResponse;
}

function getRankColor(rank: Rank): string {
  const colorMap: Record<Rank, string> = {
    'A+': 'bg-green-100 text-green-800',
    'A': 'bg-green-100 text-green-800',
    'B+': 'bg-blue-100 text-blue-800',
    'B': 'bg-blue-100 text-blue-800',
    'C+': 'bg-yellow-100 text-yellow-800',
    'C': 'bg-yellow-100 text-yellow-800',
    'D': 'bg-red-100 text-red-800',
  };
  return colorMap[rank];
}

export default function ScoreCard({ score }: ScoreCardProps) {
  const isPositiveDiff = score.market_avg_diff > 0;
  const count = useMotionValue(0);
  const rounded = useTransform(count, (latest) => Math.round(latest * 10) / 10);

  useEffect(() => {
    const controls = animate(count, score.total_score, {
      duration: 1.5,
      ease: 'easeOut',
    });

    return controls.stop;
  }, [count, score.total_score]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow duration-300 p-6 relative"
    >
      {/* ヘッダー */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-xl font-bold text-gray-900">{score.stock_name}</h3>
          <p className="text-sm text-gray-500">({score.stock_code})</p>
        </div>
        <span
          className={`px-3 py-1 rounded-full text-sm font-semibold ${getRankColor(
            score.rank
          )}`}
        >
          {score.rank}
        </span>
      </div>

      {/* 総合スコア（アニメーション） */}
      <div className="text-center my-6">
        <motion.p className="text-5xl font-bold text-gray-900">
          {rounded}
        </motion.p>
        <p className="text-sm text-gray-600 mt-1">総合スコア</p>
      </div>

      {/* 市場平均との差分 */}
      <div className="flex items-center justify-center gap-2">
        <span className="text-sm text-gray-600">市場平均</span>
        <span
          className={`text-lg font-semibold ${
            isPositiveDiff ? 'text-green-600' : 'text-red-600'
          }`}
        >
          {isPositiveDiff ? '+' : ''}
          {score.market_avg_diff.toFixed(1)}
        </span>
      </div>

      {/* 更新日時 */}
      <div className="absolute bottom-4 right-4">
        <p className="text-xs text-gray-400">{score.score_date}</p>
      </div>
    </motion.div>
  );
}
```

#### 検証

```bash
npm run dev
# ページ読み込み時にスコアがカウントアップすることを確認
```

#### 成果物

- `src/components/ScoreCard.tsx`（アニメーション追加）

---

### タスク 12.3: CategoryBarにプログレスアニメーション追加（20分）

#### 実装内容（`src/components/CategoryBar.tsx`を更新）

```typescript
import { motion } from 'framer-motion';

interface CategoryBarProps {
  label: string;
  score: number;
  color: 'value' | 'growth' | 'momentum';
}

function getColorClass(color: CategoryBarProps['color']): string {
  const colorMap = {
    value: 'bg-blue-500',
    growth: 'bg-green-500',
    momentum: 'bg-purple-500',
  };
  return colorMap[color];
}

export default function CategoryBar({ label, score, color }: CategoryBarProps) {
  return (
    <div className="mb-4">
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm font-medium text-gray-700">{label}</span>
        <span className="text-sm font-semibold text-gray-900">
          {score.toFixed(1)}
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 1.2, ease: 'easeOut', delay: 0.3 }}
          className={`h-full ${getColorClass(color)}`}
        ></motion.div>
      </div>
    </div>
  );
}
```

#### 検証

```bash
npm run dev
# バーが左から右にアニメーションすることを確認
```

#### 成果物

- `src/components/CategoryBar.tsx`（アニメーション追加）

---

### タスク 12.4: ホバーエフェクト追加（20分）

#### 実装内容（各コンポーネントに追加）

##### ScoreCard

```typescript
// className に追加
className="... hover:scale-105 transition-transform duration-200"
```

##### DetailTable

```typescript
// tr に追加
className="... hover:bg-gray-100 transition-colors duration-150"
```

#### 検証

```bash
npm run dev
# マウスホバー時にエフェクトが適用されることを確認
```

#### 成果物

- 各コンポーネントにホバーエフェクト追加

---

### タスク 12.5: ローディングアニメーション改善（15分）

#### 実装内容（`src/app/page.tsx`を更新）

```typescript
if (loading) {
  return (
    <div className="flex items-center justify-center min-h-[400px]">
      <div className="text-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          className="inline-block h-12 w-12 rounded-full border-4 border-solid border-gray-300 border-t-blue-600"
        ></motion.div>
        <p className="mt-4 text-gray-600 font-medium">データを読み込み中...</p>
      </div>
    </div>
  );
}
```

#### 検証

```bash
# ネットワークを遅延させて確認
npm run dev
```

#### 成果物

- ローディングアニメーション改善

---

### タスク 12.6: エラーハンドリング改善（15分）

#### 実装内容（`src/app/page.tsx`を更新）

```typescript
if (error) {
  return (
    <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-red-50 border-2 border-red-200 rounded-lg p-6 text-center"
      >
        <div className="text-red-600 mb-2">
          <svg
            className="w-12 h-12 mx-auto"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-red-800 mb-2">エラーが発生しました</h3>
        <p className="text-red-700">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
        >
          再読み込み
        </button>
      </motion.div>
    </div>
  );
}
```

#### 検証

```bash
# APIを停止してエラー表示を確認
docker-compose stop backend
npm run dev
```

#### 成果物

- エラーハンドリング改善

---

### タスク 12.7: アクセシビリティ改善（20分）

#### 実装内容

##### セマンティックHTML追加

```typescript
// ScoreCard.tsx
<article role="article" aria-label={`${score.stock_name}のスコアカード`}>
  {/* 既存コンテンツ */}
</article>

// CategoryBar.tsx
<div role="progressbar" aria-valuenow={score} aria-valuemin={0} aria-valuemax={100}>
  {/* 既存コンテンツ */}
</div>
```

##### キーボードナビゲーション対応

```typescript
// page.tsx のカードクリック部分
<div
  key={score.stock_code}
  onClick={() => setSelectedStock(score)}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      setSelectedStock(score);
    }
  }}
  tabIndex={0}
  className="cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-xl"
>
  <ScoreCard score={score} />
</div>
```

#### 検証

```bash
# Tabキーで要素間を移動できることを確認
# Enterキーで詳細表示が切り替わることを確認
```

#### 成果物

- アクセシビリティ改善

---

### タスク 12.8: パフォーマンス最適化（30分）

#### 実装内容

##### 画像最適化（もし使用している場合）

```typescript
import Image from 'next/image';

// <img> を <Image> に置き換え
```

##### メモ化

```typescript
import { memo } from 'react';

// ScoreCard.tsx
export default memo(ScoreCard);

// CategoryBar.tsx
export default memo(CategoryBar);

// DetailTable.tsx
export default memo(DetailTable);
```

##### 動的インポート（必要に応じて）

```typescript
import dynamic from 'next/dynamic';

const DetailTable = dynamic(() => import('@/components/DetailTable'), {
  loading: () => <p>読み込み中...</p>,
});
```

#### 検証

```bash
# Lighthouseでパフォーマンススコア確認
npm run build
npm start
# Chrome DevTools > Lighthouse > Generate report
```

#### 成果物

- パフォーマンス最適化完了

---

### タスク 12.9: スクリーンショット取得（10分）

#### 手順

```bash
mkdir -p docs/screenshots
```

#### 取得するスクリーンショット

1. **デスクトップ表示（全体）**
   - 解像度: 1920x1080
   - ファイル名: `desktop-overview.png`

2. **モバイル表示**
   - 解像度: 375x812 (iPhone X)
   - ファイル名: `mobile-overview.png`

3. **スコアカード詳細**
   - ファイル名: `scorecard-detail.png`

4. **カテゴリバーアニメーション**
   - ファイル名: `category-bars.png`

5. **詳細テーブル**
   - ファイル名: `detail-table.png`

#### 検証

```bash
ls -lh docs/screenshots/
# 5つのPNGファイルが存在することを確認
```

#### 成果物

- `docs/screenshots/` に5つのスクリーンショット

---

### タスク 12.10: 最終動作確認（40分）

#### チェックリスト

##### 機能確認

- [ ] 3銘柄のスコアカードが表示される
- [ ] スコアがカウントアップアニメーションする
- [ ] カテゴリバーが左から右にアニメーションする
- [ ] カードクリックで詳細が表示される
- [ ] 詳細テーブルが正しく表示される
- [ ] ローディング表示が機能する
- [ ] エラー表示が機能する

##### デザイン確認

- [ ] Apple風のクリーンなデザイン
- [ ] ホバーエフェクトが動作する
- [ ] ランクの色分けが正しい
- [ ] 市場平均差分の色分けが正しい

##### レスポンシブ確認

- [ ] モバイル（375px）で表示が崩れない
- [ ] タブレット（768px）で表示が崩れない
- [ ] デスクトップ（1920px）で表示が崩れない

##### パフォーマンス確認

- [ ] 初回読み込み < 3秒
- [ ] インタラクション遅延なし
- [ ] アニメーションがスムーズ

##### アクセシビリティ確認

- [ ] Tabキーでナビゲーション可能
- [ ] Enterキーで詳細表示切り替え可能
- [ ] スクリーンリーダー対応（aria-label等）

#### 検証コマンド

```bash
# ビルド確認
npm run build

# 本番モード起動
npm start

# Lighthouse監査
# Chrome DevTools > Lighthouse > Generate report
# 目標: Performance 90+, Accessibility 90+
```

#### 完了基準

- すべてのチェックリストがクリア
- Lighthouseスコア: Performance 90+, Accessibility 90+

---

### タスク 12.11: README作成（30分）

#### 実装内容（`frontend/README.md`）

```markdown
# ZenJP Frontend

日本株スコアリングシステムのフロントエンドアプリケーション

## 技術スタック

- Next.js 14 (App Router)
- TypeScript 5.x
- Tailwind CSS 3.x
- Framer Motion

## 開発環境セットアップ

### 前提条件

- Node.js 18.x以上
- npm 9.x以上
- バックエンドAPI稼働中（http://localhost:8000）

### インストール

```bash
cd frontend
npm install
```

### 環境変数設定

`.env.local`を作成:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 開発サーバー起動

```bash
npm run dev
```

ブラウザで http://localhost:3000 を開く

### ビルド

```bash
npm run build
npm start
```

## プロジェクト構成

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx          # メインページ
│   │   ├── layout.tsx        # レイアウト
│   │   └── globals.css       # グローバルCSS
│   ├── components/
│   │   ├── ScoreCard.tsx     # スコアカード
│   │   ├── CategoryBar.tsx   # カテゴリバー
│   │   └── DetailTable.tsx   # 詳細テーブル
│   ├── lib/
│   │   └── api.ts            # API通信関数
│   └── types/
│       └── score.ts          # 型定義
├── public/                   # 静的ファイル
└── docs/                     # ドキュメント
    └── screenshots/          # スクリーンショット
```

## 主要機能

### スコアカード

- 総合スコア表示（カウントアップアニメーション）
- ランク表示（A+〜D、色分け）
- 市場平均との差分表示

### カテゴリバー

- Value/Growth/Momentumスコア表示
- プログレスバーアニメーション

### 詳細テーブル

- スコア詳細一覧
- ストライプ背景
- 数値の色分け

## パフォーマンス

- 初回読み込み: < 3秒
- Lighthouseスコア: 90+
- アニメーション: 60fps

## ライセンス

MIT
```

#### 成果物

- `frontend/README.md`

---

### タスク 12.12: Git commit & tag（30分）

#### 手順

```bash
cd ~/zenjp-mvp/frontend

# ステージング
git add .

# コミット
git commit -m "feat(frontend): PHASE5 UI実装完了

- Next.js 14プロジェクト構築
- TypeScript型定義作成
- ScoreCard/CategoryBar/DetailTableコンポーネント実装
- Framer Motionアニメーション追加
- レスポンシブデザイン対応
- アクセシビリティ改善
- パフォーマンス最適化
- README作成
"

# タグ
git tag -a v1.0.0-phase5 -m "PHASE5: UI実装完了"

# プッシュ（リモートリポジトリがある場合）
git push origin main
git push origin v1.0.0-phase5
```

#### 検証

```bash
git log --oneline -n 5
git tag -l
```

#### 成果物

- Gitコミット & タグ

---

### タスク 12.13: Day 12完了確認（30分）

#### 最終チェックリスト

##### 機能

- [ ] すべてのアニメーションが動作する
- [ ] すべてのインタラクションが動作する
- [ ] エラーハンドリングが適切

##### デザイン

- [ ] Apple風のクリーンなデザイン
- [ ] 色分けが適切
- [ ] ホバーエフェクトが適切

##### レスポンシブ

- [ ] モバイル・タブレット・デスクトップで表示が崩れない

##### パフォーマンス

- [ ] Lighthouseスコア 90+

##### ドキュメント

- [ ] README完成
- [ ] スクリーンショット取得
- [ ] Gitコミット完了

#### 検証コマンド

```bash
# 最終ビルド
cd frontend
npm run build

# 本番モード起動
npm start

# 全機能確認
# http://localhost:3000 で全機能をテスト
```

#### 完了基準

- すべてのチェックリストがクリア
- デモ可能な状態

---

## 6. 検証・品質基準

### 6.1 機能要件

| 要件 | 検証方法 | 合格基準 |
|------|---------|---------|
| 3銘柄表示 | 目視確認 | 3銘柄すべて表示 |
| スコア表示 | 目視確認 | 小数点第1位まで |
| ランク表示 | 目視確認 | 色分け正確 |
| アニメーション | 目視確認 | スムーズに動作 |
| レスポンシブ | DevTools | 3サイズで崩れなし |

### 6.2 非機能要件

| 要件 | 測定方法 | 合格基準 |
|------|---------|---------|
| 初回読み込み時間 | Lighthouse | < 3秒 |
| API応答時間 | DevTools Network | < 500ms |
| パフォーマンススコア | Lighthouse | 90+ |
| アクセシビリティスコア | Lighthouse | 90+ |
| エラー率 | Console | 0件 |

### 6.3 コード品質

| 項目 | ツール | 合格基準 |
|------|--------|---------|
| TypeScript型エラー | `tsc --noEmit` | 0件 |
| ビルドエラー | `npm run build` | 0件 |
| ESLintエラー | `npm run lint` | 0件（警告は許容） |

---

## 7. トラブルシューティング

### 7.1 よくある問題

#### 問題1: APIに接続できない

**症状:**
```
API Error: Failed to fetch
```

**原因:**
- バックエンドが起動していない
- CORSエラー

**解決策:**
```bash
# バックエンド起動確認
docker-compose ps

# バックエンド再起動
docker-compose restart backend

# CORSエラーの場合はbackend/app/main.pyを確認
# origins = ["http://localhost:3000"] が設定されているか確認
```

---

#### 問題2: アニメーションが動作しない

**症状:**
スコアがカウントアップしない

**原因:**
- Framer Motionのインストール漏れ
- useEffect依存配列の問題

**解決策:**
```bash
# Framer Motionインストール確認
npm list framer-motion

# 再インストール
npm install framer-motion

# useEffect依存配列を確認
# [count, score.total_score] が正しく設定されているか
```

---

#### 問題3: レスポンシブが崩れる

**症状:**
モバイルで表示が崩れる

**原因:**
- Tailwindのブレークポイント誤設定
- 固定幅の使用

**解決策:**
```typescript
// 誤: 固定幅
<div className="w-500">

// 正: レスポンシブ幅
<div className="w-full lg:w-1/3">
```

---

#### 問題4: TypeScript型エラー

**症状:**
```
Type 'string' is not assignable to type 'Rank'
```

**原因:**
- API応答とTypeScript型定義の不一致

**解決策:**
```typescript
// src/types/score.ts のRank型を確認
export type Rank = 'A+' | 'A' | 'B+' | 'B' | 'C+' | 'C' | 'D';

// API応答が正しいか確認
console.log(score.rank); // "B+"など

// 型アサーションを使用（最終手段）
rank: score.rank as Rank
```

---

#### 問題5: ビルドエラー

**症状:**
```
Error: Cannot find module '@/components/ScoreCard'
```

**原因:**
- tsconfig.jsonのpaths設定漏れ

**解決策:**
```json
// tsconfig.json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

---

### 7.2 パフォーマンス問題

#### 問題: Lighthouseスコアが低い

**チェック項目:**

1. **画像最適化**
   - Next.js Imageコンポーネント使用
   - WebP形式への変換

2. **コード分割**
   - 動的インポート使用
   - 不要なライブラリ削除

3. **キャッシュ設定**
   - API応答のキャッシュ
   - 静的アセットのキャッシュ

4. **バンドルサイズ削減**
   ```bash
   npm run build
   # チャンクサイズを確認
   ```

---

## 付録A: AI活用プロンプトクイックリファレンス

### プロンプト一覧

| タスク | プロンプトID | 用途 |
|--------|------------|------|
| Next.js設定 | #P1 | next.config.js生成 |
| 型変換 | #P2 | Python→TypeScript |
| コンポーネント生成 | #P3 | ScoreCard実装 |
| コンポーネント生成 | #P4 | CategoryBar実装 |
| コンポーネント生成 | #P5 | DetailTable実装 |
| アニメーション | #P6 | Framer Motion実装 |
| レスポンシブ最適化 | #P7 | 一括最適化 |

---

## 付録B: 完成イメージ

### デスクトップ表示

```
┌─────────────────────────────────────────────────────────────────┐
│ ZenJP                                                           │
│ 日本株スコアリングシステム MVP                                    │
├─────────────────────────────────────────────────────────────────┤
│ スコアダッシュボード                                             │
│ 更新日: 2026-01-31                                              │
│                                                                 │
│ ┌─────────┐  ┌─────────┐  ┌─────────┐                        │
│ │トヨタ    │  │ソニー    │  │ソフトバンク│                        │
│ │(7203)   │  │(6758)   │  │(9984)   │                        │
│ │  B+     │  │  A      │  │  B      │                        │
│ │         │  │         │  │         │                        │
│ │  78.5   │  │  92.3   │  │  71.2   │                        │
│ │ 総合スコア│  │ 総合スコア│  │ 総合スコア│                        │
│ │         │  │         │  │         │                        │
│ │市場平均  │  │市場平均  │  │市場平均  │                        │
│ │ +28.5   │  │ +42.3   │  │ +21.2   │                        │
│ └─────────┘  └─────────┘  └─────────┘                        │
│                                                                 │
│ トヨタ自動車 詳細                                                │
│ ┌─────────────────────────────────────────────┐                │
│ │ カテゴリ別スコア                               │                │
│ │ Value    ████████████░░░░░░░░  62.3          │                │
│ │ Growth   ██████████████░░░░░░  71.2          │                │
│ │ Momentum █████████████████░░░  85.8          │                │
│ │                                              │                │
│ │ スコア詳細                                    │                │
│ │ ┌────────────┬────────┐                    │                │
│ │ │総合スコア    │ 78.5   │                    │                │
│ │ │Valueスコア  │ 62.3   │                    │                │
│ │ │Growthスコア │ 71.2   │                    │                │
│ │ │Momentumスコア│ 85.8  │                    │                │
│ │ │ランク       │ B+     │                    │                │
│ │ │市場平均差分  │ +28.5  │                    │                │
│ │ └────────────┴────────┘                    │                │
│ └─────────────────────────────────────────────┘                │
├─────────────────────────────────────────────────────────────────┤
│ © 2026 ZenJP. All rights reserved.                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 変更履歴

| Version | 日付 | 変更内容 | 作成者 |
|---------|------|---------|--------|
| 1.0.0 | 2026-02-04 | PHASE5詳細計画書作成 | ZenJP Team |

---

**ZenJP MVP PHASE5 実装アクション詳細計画書 完成**

**次のアクション:** Day 10 タスク 10.1 開始！
