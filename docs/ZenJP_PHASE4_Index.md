# ZenJP MVP PHASE4 実装アクション詳細計画書 - 統合版

**対象フェーズ:** PHASE4 API・UI実装  
**期間:** Day 8-12（5日間、合計19.5時間）  
**作成日:** 2026年2月10日

---

## 📋 ドキュメント構成

PHASE4の詳細実装ガイドは、以下の2つのパートに分割されています：

### Part 1: API実装（Day 8-9）
**ファイル:** `ZenJP_PHASE4_Part1_API.md`  
**期間:** 2日間、7時間  
**内容:**
- Day 8: API実装（基礎）- 3.5時間
  - FastAPI基本構造構築
  - スキーマ定義
  - サービス層実装
  - ルーター実装
  - API動作確認
- Day 9: API実装（完成）- 3.5時間
  - エラーハンドリング強化
  - レスポンスタイム測定
  - AIセキュリティ監査
  - APIドキュメント整備
  - Postmanコレクション作成

### Part 2: UI実装（Day 10-12）
**ファイル:** `ZenJP_PHASE4_Part2_UI.md`  
**期間:** 3日間、12時間  
**内容:**
- Day 10: UI実装（基礎）- 3.5時間
  - Next.js依存関係追加
  - TypeScript型定義
  - APIクライアント実装
  - ホームページ実装
- Day 11: UI実装（コンポーネント）- 3.5時間
  - ScoreCardコンポーネント
  - CategoryBarコンポーネント
  - DetailTableコンポーネント
  - StockSelectorコンポーネント
- Day 12: UI実装（完成）- 5時間
  - レスポンシブ対応
  - Framer Motionアニメーション
  - エラーハンドリング強化
  - スクリーンショット取得
  - README更新

---

## 🎯 PHASE4の全体像

### 達成目標

**API実装（Day 8-9）:**
- ✅ FastAPI基本構造完成
- ✅ GET /api/score/{stock_code} エンドポイント実装
- ✅ エラーハンドリング実装
- ✅ CORSミドルウェア設定
- ✅ Swagger UIドキュメント
- ✅ セキュリティ監査（AI活用）

**UI実装（Day 10-12）:**
- ✅ Next.js 14基本構造完成
- ✅ TypeScript型定義完成
- ✅ 4つのコンポーネント完成
- ✅ Framer Motionアニメーション
- ✅ レスポンシブ対応完了
- ✅ MVP完成

### 使用するAIプロンプト

- **プロンプト#6**: セキュリティ監査（Day 9）
- **プロンプト#7**: UIコンポーネント生成（Day 11）
- **プロンプト#8**: アニメーション追加（Day 12）

---

## 📂 成果物一覧

### バックエンド（API）
```
backend/app/
├── main.py                    # FastAPIメインアプリ（CORS設定）
├── routers/
│   └── scores.py              # スコアAPIエンドポイント
├── services/
│   └── score_service.py       # スコア取得サービス
└── schemas/
    └── score.py               # スコアレスポンススキーマ
```

### フロントエンド（UI）
```
frontend/src/
├── app/
│   ├── layout.tsx             # ルートレイアウト
│   ├── page.tsx               # ホームページ
│   └── globals.css            # グローバルスタイル
├── components/
│   ├── ScoreCard.tsx          # スコアカード
│   ├── CategoryBar.tsx        # カテゴリバー
│   ├── DetailTable.tsx        # 詳細テーブル
│   └── StockSelector.tsx      # 銘柄セレクター
└── lib/
    ├── types.ts               # 型定義
    └── api.ts                 # APIクライアント
```

### ドキュメント
```
docs/
├── api_endpoints.md                        # API仕様書
├── api_security_review.md                  # セキュリティ監査結果
├── ZenJP_MVP_API.postman_collection.json   # Postmanコレクション
└── screenshots/                            # スクリーンショット（6枚）
    ├── 01_toyota_desktop.png
    ├── 02_sony_desktop.png
    ├── 03_sbg_desktop.png
    ├── 04_mobile.png
    ├── 05_category_bar.png
    └── 06_detail_table.png
```

---

## 🚀 実装の流れ

### Week 1: API実装
```
Day 8 (月曜)
└─ FastAPI基本構造
   └─ スキーマ定義
      └─ サービス層
         └─ ルーター
            └─ 動作確認 ✓

Day 9 (火曜)
└─ エラーハンドリング
   └─ パフォーマンステスト
      └─ セキュリティ監査（AI）
         └─ ドキュメント整備
            └─ Postman ✓
```

### Week 2: UI実装
```
Day 10 (水曜)
└─ Next.js設定
   └─ 型定義
      └─ APIクライアント
         └─ ホームページ基本版 ✓

Day 11 (木曜)
└─ ScoreCard
   └─ CategoryBar
      └─ DetailTable
         └─ StockSelector
            └─ 統合 ✓

Day 12 (金曜)
└─ レスポンシブ
   └─ アニメーション
      └─ エラーハンドリング
         └─ スクリーンショット
            └─ README
               └─ MVP完成！ 🎉
```

---

## ✅ 完了確認チェックリスト

### API完了確認
```bash
# 1. エンドポイント動作確認
curl http://localhost:8000/api/score/7203

# 2. Swagger UI確認
open http://localhost:8000/docs

# 3. 3銘柄すべて確認
for code in 7203 6758 9984; do
  curl -s http://localhost:8000/api/score/$code | jq '.stock_name, .total_score'
done
```

### UI完了確認
```bash
# 1. フロントエンド起動確認
curl http://localhost:3000

# 2. コンポーネント存在確認
ls frontend/src/components/*.tsx

# 3. ブラウザ確認
open http://localhost:3000

# 確認項目:
# - ScoreCard表示
# - CategoryBar表示（横棒グラフ）
# - DetailTable表示
# - StockSelector表示
# - 銘柄切り替え動作
# - アニメーション動作
# - モバイル表示OK
```

### 最終確認
```bash
# スクリーンショット確認
ls -l docs/screenshots/
# → 6枚以上

# README確認
cat README.md
# → スクリーンショット、使用方法が記載

# Lighthouse確認（Chrome DevTools）
# → Performance 90以上
# → Accessibility 90以上
```

---

## 🎊 PHASE4完了！

**開発期間:** 5日間（Day 8-12）  
**総時間:** 19.5時間

**完成したもの:**
- ✅ 完全に動作するWebアプリケーション
- ✅ FastAPI（バックエンド）
- ✅ Next.js（フロントエンド）
- ✅ 3銘柄のスコア表示
- ✅ レスポンシブUI
- ✅ スムーズなアニメーション
- ✅ 完全なドキュメント

**次のステップ:**
- PHASE5: Day 13-14でテスト・デモ準備
- 統合テスト
- デモ台本作成
- MVP最終確認

---

## 📖 参考資料

### 関連ドキュメント
- [PHASE1: 環境構築・DB](ZenJP_PHASE1_Action_Plan.md)
- [PHASE2: データ取得](ZenJP_PHASE2_Action_Plan.md)
- [PHASE3: スコア計算](ZenJP_PHASE3_Action_Plan.md)
- [PHASE4 Part1: API実装](ZenJP_PHASE4_Part1_API.md)
- [PHASE4 Part2: UI実装](ZenJP_PHASE4_Part2_UI.md)

### 技術スタック
- **バックエンド:** FastAPI, PostgreSQL, SQLAlchemy, Pydantic
- **フロントエンド:** Next.js 14, React 18, TypeScript, Tailwind CSS, Framer Motion
- **開発環境:** Docker, Docker Compose

---

**お疲れ様でした！MVP完成です！** 🎉
