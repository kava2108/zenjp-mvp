# ZenJP MVP PHASE4 実装アクション詳細計画書 - Part 2: UI実装

**対象:** Day 10-12（UI実装）  
**期間:** 3日間、合計12時間  
**作成日:** 2026年2月12日

---

## Day 10: UI実装（基礎）- 3.5時間

### ステップ11: Next.js依存関係追加（20分）

#### アクション11-1: package.json更新

**コマンド:**
```bash
cd frontend
npm install framer-motion@10.16.16
```

**または手動編集:**
```json
// frontend/package.json の dependencies に追加
"framer-motion": "^10.16.16"
```

**確認:**
```bash
cat frontend/package.json | grep framer-motion
npm list framer-motion
```

---

### ステップ12: 型定義作成（45分）

#### アクション12-1: types.ts作成

**GitHub Copilotへの指示:**

```typescript
// ファイル名: frontend/src/lib/types.ts

// Copilotに以下を指示:
// バックエンドAPIのレスポンス型定義を作成してください
//
// export interface ScoreDetail {
//   per: number;
//   per_score: number;
//   pbr: number;
//   pbr_score: number;
//   dividend_yield: number;
//   dividend_score: number;
//   revenue_growth_rate: number;
//   rsi: number;
//   rsi_score: number;
//   volume_change_rate: number;
//   volume_change_score: number;
// }
//
// export interface MarketComparison {
//   total_diff: number;
//   value_diff: number;
//   growth_diff: number;
//   momentum_diff: number;
// }
//
// export interface ScoreData {
//   stock_code: string;
//   stock_name: string;
//   total_score: number;
//   rank: string;
//   value_score: number;
//   growth_score: number;
//   momentum_score: number;
//   score_date: string;
//   details: ScoreDetail;
//   market_comparison: MarketComparison;
//   updated_at: string;
// }
//
// export interface Stock {
//   code: string;
//   name: string;
// }
//
// export const STOCKS: Stock[] = [
//   { code: '7203', name: 'トヨタ自動車' },
//   { code: '6758', name: 'ソニーグループ' },
//   { code: '9984', name: 'ソフトバンクグループ' }
// ];
```

**確認:**
```bash
cat frontend/src/lib/types.ts
```

---

### ステップ13: APIクライアント実装（45分）

#### アクション13-1: api.ts作成

**GitHub Copilotへの指示:**

```typescript
// ファイル名: frontend/src/lib/api.ts

// Copilotに以下を指示:
// バックエンドAPIと通信するクライアントを実装してください
//
// import { ScoreData } from './types';
//
// const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
//
// export async function fetchScore(stockCode: string): Promise<ScoreData> {
//   const response = await fetch(`${API_BASE_URL}/api/score/${stockCode}`);
//   
//   if (!response.ok) {
//     if (response.status === 404) {
//       throw new Error(`銘柄コード ${stockCode} のスコアが見つかりません`);
//     } else if (response.status === 400) {
//       throw new Error(`無効な銘柄コードです: ${stockCode}`);
//     } else {
//       throw new Error(`APIエラー: ${response.status}`);
//     }
//   }
//   
//   const data: ScoreData = await response.json();
//   return data;
// }
//
// export function formatScore(score: number): string {
//   return score.toFixed(1);
// }
//
// export function formatDate(dateString: string): string {
//   const date = new Date(dateString);
//   return date.toLocaleDateString('ja-JP');
// }
//
// export function getRankColor(rank: string): string {
//   const colorMap: { [key: string]: string } = {
//     'A': 'text-green-600',
//     'B+': 'text-blue-600',
//     'B': 'text-blue-500',
//     'C+': 'text-yellow-600',
//     'C': 'text-yellow-500',
//     'D': 'text-red-600'
//   };
//   return colorMap[rank] || 'text-gray-600';
// }
```

**確認:**
```bash
cat frontend/src/lib/api.ts
```

---

### ステップ14: ホームページ実装（60分）

#### アクション14-1: layout.tsx更新

**GitHub Copilotへの指示:**

```typescript
// ファイル名: frontend/src/app/layout.tsx

// Copilotに以下を指示:
// Next.js 14 App Router用のルートレイアウトを作成してください
//
// import type { Metadata } from 'next';
// import './globals.css';
//
// export const metadata: Metadata = {
//   title: 'ZenJP MVP - 日本株スコアリングシステム',
//   description: 'Value/Growth/Momentumの3軸で日本株を評価',
// };
//
// export default function RootLayout({
//   children,
// }: {
//   children: React.ReactNode;
// }) {
//   return (
//     <html lang="ja">
//       <body className="bg-gray-50">
//         {children}
//       </body>
//     </html>
//   );
// }
```

---

#### アクション14-2: page.tsx実装（基本版）

**GitHub Copilotへの指示:**

```typescript
// ファイル名: frontend/src/app/page.tsx

// Copilotに以下を指示:
// ホームページを実装してください（基本版）
//
// 'use client';
//
// import { useState, useEffect } from 'react';
// import { STOCKS } from '@/lib/types';
// import type { ScoreData } from '@/lib/types';
// import { fetchScore } from '@/lib/api';
//
// export default function Home() {
//   const [selectedStock, setSelectedStock] = useState('7203');
//   const [scoreData, setScoreData] = useState<ScoreData | null>(null);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState<string | null>(null);
//
//   useEffect(() => {
//     loadScore(selectedStock);
//   }, [selectedStock]);
//
//   async function loadScore(stockCode: string) {
//     setLoading(true);
//     setError(null);
//     try {
//       const data = await fetchScore(stockCode);
//       setScoreData(data);
//     } catch (err) {
//       setError(err instanceof Error ? err.message : 'エラーが発生しました');
//     } finally {
//       setLoading(false);
//     }
//   }
//
//   return (
//     <div className="min-h-screen p-8">
//       <div className="max-w-4xl mx-auto">
//         <h1 className="text-4xl font-bold mb-8">ZenJP MVP</h1>
//         
//         {/* 銘柄セレクター（仮） */}
//         <div className="mb-8">
//           <select
//             value={selectedStock}
//             onChange={(e) => setSelectedStock(e.target.value)}
//             className="px-4 py-2 border rounded"
//           >
//             {STOCKS.map((stock) => (
//               <option key={stock.code} value={stock.code}>
//                 {stock.name} ({stock.code})
//               </option>
//             ))}
//           </select>
//         </div>
//
//         {/* ローディング */}
//         {loading && <div>読み込み中...</div>}
//
//         {/* エラー */}
//         {error && <div className="text-red-600">{error}</div>}
//
//         {/* スコアデータ（仮表示） */}
//         {scoreData && !loading && (
//           <div className="bg-white p-6 rounded-lg shadow">
//             <h2 className="text-2xl font-bold mb-4">
//               {scoreData.stock_name} ({scoreData.stock_code})
//             </h2>
//             <div className="text-6xl font-bold mb-4">
//               {scoreData.total_score.toFixed(1)}点
//             </div>
//             <div className="text-2xl mb-4">
//               ランク: {scoreData.rank}
//             </div>
//             <div className="grid grid-cols-3 gap-4">
//               <div>
//                 <div className="text-sm text-gray-600">Value</div>
//                 <div className="text-xl font-bold">{scoreData.value_score.toFixed(1)}</div>
//               </div>
//               <div>
//                 <div className="text-sm text-gray-600">Growth</div>
//                 <div className="text-xl font-bold">{scoreData.growth_score.toFixed(1)}</div>
//               </div>
//               <div>
//                 <div className="text-sm text-gray-600">Momentum</div>
//                 <div className="text-xl font-bold">{scoreData.momentum_score.toFixed(1)}</div>
//               </div>
//             </div>
//           </div>
//         )}
//       </div>
//     </div>
//   );
// }
```

---

### ステップ15: フロントエンド動作確認（30分）

#### アクション15-1: フロントエンド起動

**コマンド:**
```bash
docker-compose restart frontend
docker-compose logs frontend | tail -20
```

**期待されるログ:**
```
ready - started server on 0.0.0.0:3000
```

---

#### アクション15-2: ブラウザで確認

**ブラウザで確認:**
```
URL: http://localhost:3000

確認項目:
- ページが表示される
- タイトル「ZenJP MVP」が表示される
- 銘柄セレクターが表示される
- スコアが表示される
- 銘柄を切り替えるとスコアが変わる
```

---

### Day 10完了確認

```bash
# 1. ファイル存在確認
ls -l frontend/src/lib/types.ts
ls -l frontend/src/lib/api.ts
ls -l frontend/src/app/page.tsx

# 2. フロントエンド起動確認
curl http://localhost:3000

# 3. ブラウザで確認
open http://localhost:3000

echo "✅ Day 10 完了！"
```

---

## Day 11: UI実装（コンポーネント）- 3.5時間

### ステップ16: ScoreCardコンポーネント作成（60分）

#### アクション16-1: ScoreCard.tsx作成

**GitHub Copilotへの指示（プロンプト#7）:**

```typescript
// ファイル名: frontend/src/components/ScoreCard.tsx

// Copilotに以下を指示:
// 以下の要件で、Reactコンポーネント（TypeScript + Tailwind CSS）を実装してください:
//
// コンポーネント名: ScoreCard
// 要件:
// - 総合スコア（大きく表示）
// - ランク（A/B+/B/C+/C/D、色分け）
// - 市場平均との比較（+28.5点、色分け）
// - 更新日時（右下に小さく）
// デザイン: Apple風のクリーンで洗練されたデザイン
// レスポンシブ: モバイル・デスクトップ両対応
//
// import { ScoreData } from '@/lib/types';
// import { getRankColor, formatDate } from '@/lib/api';
//
// interface ScoreCardProps {
//   data: ScoreData;
// }
//
// export default function ScoreCard({ data }: ScoreCardProps) {
//   return (
//     <div className="bg-white rounded-2xl shadow-lg p-8 mb-6">
//       <h2 className="text-2xl font-bold mb-6 text-gray-800">
//         {data.stock_name} <span className="text-gray-500">({data.stock_code})</span>
//       </h2>
//
//       <div className="flex items-end justify-between mb-6">
//         <div>
//           <div className="text-6xl font-bold text-gray-900 mb-2">
//             {data.total_score.toFixed(1)}
//             <span className="text-3xl text-gray-500 ml-2">点</span>
//           </div>
//           <div className={`text-2xl font-semibold ${getRankColor(data.rank)}`}>
//             ランク: {data.rank}
//           </div>
//         </div>
//
//         <div className="text-right">
//           <div className="text-sm text-gray-600 mb-1">市場平均との差</div>
//           <div className={`text-3xl font-bold ${
//             data.market_comparison.total_diff >= 0 ? 'text-green-600' : 'text-red-600'
//           }`}>
//             {data.market_comparison.total_diff >= 0 ? '+' : ''}
//             {data.market_comparison.total_diff.toFixed(1)}
//           </div>
//         </div>
//       </div>
//
//       <div className="text-sm text-gray-500 text-right">
//         更新: {formatDate(data.updated_at)}
//       </div>
//     </div>
//   );
// }
```

**確認:**
```bash
cat frontend/src/components/ScoreCard.tsx
```

---

### ステップ17: CategoryBarコンポーネント作成（45分）

#### アクション17-1: CategoryBar.tsx作成

**GitHub Copilotへの指示:**

```typescript
// ファイル名: frontend/src/components/CategoryBar.tsx

// Copilotに以下を指示:
// Value/Growth/Momentumスコアを横棒グラフで表示するコンポーネントを作成してください
//
// import { ScoreData } from '@/lib/types';
//
// interface CategoryBarProps {
//   data: ScoreData;
// }
//
// export default function CategoryBar({ data }: CategoryBarProps) {
//   const categories = [
//     { name: 'Value', score: data.value_score, diff: data.market_comparison.value_diff, color: 'bg-blue-500' },
//     { name: 'Growth', score: data.growth_score, diff: data.market_comparison.growth_diff, color: 'bg-green-500' },
//     { name: 'Momentum', score: data.momentum_score, diff: data.market_comparison.momentum_diff, color: 'bg-purple-500' }
//   ];
//
//   return (
//     <div className="bg-white rounded-2xl shadow-lg p-8 mb-6">
//       <h3 className="text-xl font-bold mb-6 text-gray-800">カテゴリ別スコア</h3>
//       
//       <div className="space-y-6">
//         {categories.map((cat) => (
//           <div key={cat.name}>
//             <div className="flex justify-between mb-2">
//               <span className="font-semibold text-gray-700">{cat.name}</span>
//               <div className="flex items-center gap-3">
//                 <span className="text-xl font-bold text-gray-900">{cat.score.toFixed(1)}</span>
//                 <span className={`text-sm font-semibold ${cat.diff >= 0 ? 'text-green-600' : 'text-red-600'}`}>
//                   ({cat.diff >= 0 ? '+' : ''}{cat.diff.toFixed(1)})
//                 </span>
//               </div>
//             </div>
//             
//             <div className="relative h-8 bg-gray-200 rounded-full overflow-hidden">
//               <div className="absolute h-full w-0.5 bg-gray-400" style={{ left: '50%' }} />
//               <div className={`h-full ${cat.color} transition-all duration-500`} style={{ width: `${cat.score}%` }} />
//             </div>
//           </div>
//         ))}
//       </div>
//     </div>
//   );
// }
```

---

### ステップ18: DetailTableコンポーネント作成（45分）

#### アクション18-1: DetailTable.tsx作成

**GitHub Copilotへの指示:**

```typescript
// ファイル名: frontend/src/components/DetailTable.tsx

// Copilotに以下を指示:
// スコア詳細をテーブルで表示するコンポーネントを作成してください
//
// import { ScoreData } from '@/lib/types';
//
// interface DetailTableProps {
//   data: ScoreData;
// }
//
// export default function DetailTable({ data }: DetailTableProps) {
//   const details = data.details;
//
//   const rows = [
//     { label: 'PER（株価収益率）', value: `${details.per.toFixed(2)}倍`, score: details.per_score },
//     { label: 'PBR（株価純資産倍率）', value: `${details.pbr.toFixed(2)}倍`, score: details.pbr_score },
//     { label: '配当利回り', value: `${details.dividend_yield.toFixed(2)}%`, score: details.dividend_score },
//     { label: '売上成長率', value: `${details.revenue_growth_rate.toFixed(2)}%`, score: details.revenue_growth_rate },
//     { label: 'RSI（相対力指数）', value: details.rsi.toFixed(1), score: details.rsi_score },
//     { label: '出来高変化率', value: `${details.volume_change_rate.toFixed(1)}%`, score: details.volume_change_score }
//   ];
//
//   return (
//     <div className="bg-white rounded-2xl shadow-lg p-8">
//       <h3 className="text-xl font-bold mb-6 text-gray-800">詳細指標</h3>
//       
//       <div className="overflow-x-auto">
//         <table className="w-full">
//           <thead>
//             <tr className="border-b-2 border-gray-200">
//               <th className="text-left py-3 px-4 font-semibold text-gray-700">指標</th>
//               <th className="text-right py-3 px-4 font-semibold text-gray-700">値</th>
//               <th className="text-right py-3 px-4 font-semibold text-gray-700">スコア</th>
//             </tr>
//           </thead>
//           <tbody>
//             {rows.map((row, index) => (
//               <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
//                 <td className="py-3 px-4 text-gray-700">{row.label}</td>
//                 <td className="py-3 px-4 text-right font-semibold text-gray-900">{row.value}</td>
//                 <td className="py-3 px-4 text-right font-bold text-blue-600">{row.score.toFixed(1)}</td>
//               </tr>
//             ))}
//           </tbody>
//         </table>
//       </div>
//     </div>
//   );
// }
```

---

### ステップ19: StockSelectorコンポーネント作成（30分）

#### アクション19-1: StockSelector.tsx作成

**GitHub Copilotへの指示:**

```typescript
// ファイル名: frontend/src/components/StockSelector.tsx

// Copilotに以下を指示:
// 銘柄選択UIコンポーネントを作成してください
//
// import { STOCKS } from '@/lib/types';
//
// interface StockSelectorProps {
//   selectedCode: string;
//   onSelect: (code: string) => void;
// }
//
// export default function StockSelector({ selectedCode, onSelect }: StockSelectorProps) {
//   return (
//     <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
//       <h3 className="text-lg font-semibold mb-4 text-gray-800">銘柄選択</h3>
//       
//       <div className="flex flex-col sm:flex-row gap-3">
//         {STOCKS.map((stock) => (
//           <button
//             key={stock.code}
//             onClick={() => onSelect(stock.code)}
//             className={`flex-1 py-4 px-6 rounded-xl font-semibold transition-all ${
//               selectedCode === stock.code
//                 ? 'bg-blue-600 text-white shadow-md'
//                 : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
//             }`}
//           >
//             <div className="text-sm mb-1">{stock.code}</div>
//             <div className="text-base">{stock.name}</div>
//           </button>
//         ))}
//       </div>
//     </div>
//   );
// }
```

---

### ステップ20: page.tsx更新（30分）

#### アクション20-1: コンポーネント組み込み

**GitHub Copilotへの指示:**

```typescript
// frontend/src/app/page.tsx を更新

// Copilotに以下を指示:
// 作成した4つのコンポーネントを組み込んでください
//
// import ScoreCard from '@/components/ScoreCard';
// import CategoryBar from '@/components/CategoryBar';
// import DetailTable from '@/components/DetailTable';
// import StockSelector from '@/components/StockSelector';
//
// return (
//   <div className="min-h-screen bg-gray-50 p-4 sm:p-8">
//     <div className="max-w-6xl mx-auto">
//       <div className="mb-8">
//         <h1 className="text-4xl font-bold text-gray-900 mb-2">ZenJP MVP</h1>
//         <p className="text-gray-600">日本株スコアリングシステム</p>
//       </div>
//
//       <StockSelector selectedCode={selectedStock} onSelect={setSelectedStock} />
//
//       {loading && <div className="text-center py-12">読み込み中...</div>}
//       {error && <div className="bg-red-50 border border-red-200 rounded-xl p-6">{error}</div>}
//       
//       {scoreData && !loading && (
//         <div className="space-y-6">
//           <ScoreCard data={scoreData} />
//           <CategoryBar data={scoreData} />
//           <DetailTable data={scoreData} />
//         </div>
//       )}
//     </div>
//   </div>
// );
```

---

### Day 11完了確認

```bash
# 1. コンポーネント存在確認
ls -l frontend/src/components/*.tsx

# 2. ブラウザで確認
open http://localhost:3000

# 確認項目:
# - ScoreCardが表示される
# - CategoryBarが表示される（横棒グラフ）
# - DetailTableが表示される
# - StockSelectorが表示される
# - 銘柄切り替えが動作する

echo "✅ Day 11 完了！"
```

---

## Day 12: UI実装（完成）- 5時間

### ステップ21: レスポンシブ対応（40分）

#### アクション21-1: レスポンシブチェック

**Chrome DevToolsで確認:**
```
1. F12 → デバイスツールバー
2. 以下のサイズで確認:
   - iPhone SE (375px)
   - iPad (768px)
   - Desktop (1920px)
```

---

### ステップ22: スコアアニメーション追加（60分）🤖

#### アクション22-1: ScoreCard.tsxにアニメーション追加

**GitHub Copilotへの指示（プロンプト#8）:**

```typescript
// ScoreCard.tsx を更新

// Copilotに以下を指示:
// スコアがカウントアップするアニメーションを追加してください。
// 0から実際のスコアまで1.5秒でアニメーションし、Framer Motionを使用してください。
//
// import { motion, useMotionValue, useTransform, animate } from 'framer-motion';
// import { useEffect } from 'react';
//
// const scoreMotion = useMotionValue(0);
// const scoreDisplay = useTransform(scoreMotion, (latest) => latest.toFixed(1));
//
// useEffect(() => {
//   const controls = animate(scoreMotion, data.total_score, {
//     duration: 1.5,
//     ease: 'easeOut'
//   });
//   return controls.stop;
// }, [data.total_score]);
//
// <motion.div className="text-6xl font-bold text-gray-900 mb-2">
//   {scoreDisplay}
//   <span className="text-3xl text-gray-500 ml-2">点</span>
// </motion.div>
```

---

#### アクション22-2: CategoryBarにアニメーション追加

**GitHub Copilotへの指示:**

```typescript
// CategoryBar.tsx を更新

// 横棒グラフがアニメーションで伸びるようにしてください
//
// import { motion } from 'framer-motion';
//
// <motion.div 
//   className={`h-full ${cat.color}`}
//   initial={{ width: 0 }}
//   animate={{ width: `${cat.score}%` }}
//   transition={{ duration: 1, ease: 'easeOut', delay: index * 0.2 }}
// />
```

---

### ステップ23: エラーハンドリング強化（30分）

#### アクション23-1: ローディング・エラー表示改善

**GitHub Copilotへの指示:**

```typescript
// page.tsx を更新

// ローディング表示をスピナーに変更してください
//
// {loading && (
//   <div className="flex justify-center items-center py-12">
//     <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent"></div>
//   </div>
// )}
//
// エラー表示を改善してください
//
// {error && (
//   <div className="bg-red-50 border-2 border-red-200 rounded-xl p-6">
//     <div className="flex items-start">
//       <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
//         <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
//       </svg>
//       <div className="ml-3">
//         <h3 className="text-sm font-semibold text-red-800">エラーが発生しました</h3>
//         <div className="mt-2 text-sm text-red-700">{error}</div>
//         <button onClick={() => loadScore(selectedStock)} className="mt-3 text-sm font-semibold text-red-600">
//           再試行
//         </button>
//       </div>
//     </div>
//   </div>
// )}
```

---

### ステップ24: スクリーンショット取得（30分）

#### アクション24-1: スクリーンショット撮影

**手順:**
```bash
mkdir -p docs/screenshots
```

**ブラウザで撮影:**
```
1. トヨタ自動車を表示 → docs/screenshots/01_toyota_desktop.png
2. ソニーグループを表示 → docs/screenshots/02_sony_desktop.png
3. SBGを表示 → docs/screenshots/03_sbg_desktop.png
4. モバイル表示（iPhone 12 Pro）→ docs/screenshots/04_mobile.png
5. カテゴリバー → docs/screenshots/05_category_bar.png
6. 詳細テーブル → docs/screenshots/06_detail_table.png
```

---

### ステップ25: README更新（30分）

#### アクション25-1: README.md更新

**GitHub Copilotへの指示:**

```markdown
# README.md を更新

# スクリーンショットセクション追加
## スクリーンショット

### デスクトップ表示
![トヨタ自動車](docs/screenshots/01_toyota_desktop.png)

### モバイル表示
![モバイル](docs/screenshots/04_mobile.png)

## 使用方法

### セットアップ
```bash
git clone https://github.com/your-username/zenjp-mvp.git
cd zenjp-mvp
docker-compose up -d
```

### アクセス
- フロントエンド: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
```

---

### Day 12完了確認

```bash
# 1. アニメーション確認（ブラウザ）
# - スコアがカウントアップする
# - 横棒グラフが伸びる

# 2. レスポンシブ確認（DevTools）
# - 375px、768px、1920pxで正常表示

# 3. スクリーンショット確認
ls -l docs/screenshots/
# → 6枚以上

# 4. README確認
cat README.md

echo "✅ Day 12 完了！"
echo "🎉 PHASE4 完了！"
echo "🎊 ZenJP MVP 完成！"
```

---

## Day 10-12 完了報告

**所要時間:** 12時間  
**成果物:**
- ✅ Next.js基本構造完成
- ✅ TypeScript型定義
- ✅ APIクライアント
- ✅ 4つのコンポーネント（ScoreCard, CategoryBar, DetailTable, StockSelector）
- ✅ Framer Motionアニメーション
- ✅ レスポンシブ対応
- ✅ エラーハンドリング
- ✅ スクリーンショット6枚
- ✅ README更新

**次のステップ:** PHASE5（テスト・デモ準備）Day 13-14
