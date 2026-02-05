# ZenJP MVP PHASE4 実装アクション詳細計画書 - Part 1: API実装

**対象:** Day 8-9（API実装）  
**期間:** 2日間、合計7時間  
**作成日:** 2026年2月10日

---

## Day 8: API実装（基礎）- 3.5時間

### ステップ1: FastAPI基本構造構築（30分）

#### アクション1-1: main.py更新

**GitHub Copilotへの指示:**

```python
# ファイル名: backend/app/main.py

# Copilotに以下を指示:
# 既存のmain.pyを更新して、ルーターとCORSミドルウェアを追加してください
#
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.routers import scores
#
# app = FastAPI(
#     title="ZenJP MVP API",
#     version="1.0.0",
#     description="日本株スコアリングシステムAPI"
# )
#
# # CORSミドルウェア
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # ルーター
# app.include_router(scores.router)
#
# @app.get("/")
# def root():
#     return {
#         "message": "ZenJP MVP API",
#         "version": "1.0.0",
#         "endpoints": ["/api/score/{stock_code}", "/health", "/docs"]
#     }
#
# @app.get("/health")
# def health():
#     return {"status": "ok"}
```

**確認コマンド:**
```bash
cat backend/app/main.py
docker-compose exec backend python -m py_compile app/main.py
```

---

### ステップ2: スキーマ定義（30分）

#### アクション2-1: score.py（スキーマ）作成

**GitHub Copilotへの指示:**

```python
# ファイル名: backend/app/schemas/score.py

# Copilotに以下を指示:
# スコアAPIのレスポンススキーマを作成してください
#
# from pydantic import BaseModel, Field
# from datetime import date
#
# class ScoreDetail(BaseModel):
#     """スコア詳細"""
#     per: float = Field(..., description="PER（株価収益率）")
#     per_score: float = Field(..., description="PERスコア")
#     pbr: float = Field(..., description="PBR（株価純資産倍率）")
#     pbr_score: float = Field(..., description="PBRスコア")
#     dividend_yield: float = Field(..., description="配当利回り（%）")
#     dividend_score: float = Field(..., description="配当スコア")
#     revenue_growth_rate: float = Field(..., description="売上成長率（%）")
#     rsi: float = Field(..., description="RSI（相対力指数）")
#     rsi_score: float = Field(..., description="RSIスコア")
#     volume_change_rate: float = Field(..., description="出来高変化率（%）")
#     volume_change_score: float = Field(..., description="出来高変化スコア")
#
#     class Config:
#         from_attributes = True
#
# class MarketComparison(BaseModel):
#     """市場平均との比較"""
#     total_diff: float = Field(..., description="総合スコア差分")
#     value_diff: float = Field(..., description="Valueスコア差分")
#     growth_diff: float = Field(..., description="Growthスコア差分")
#     momentum_diff: float = Field(..., description="Momentumスコア差分")
#
# class ScoreResponse(BaseModel):
#     """スコアAPIレスポンス"""
#     stock_code: str = Field(..., description="銘柄コード")
#     stock_name: str = Field(..., description="銘柄名")
#     total_score: float = Field(..., description="総合スコア")
#     rank: str = Field(..., description="ランク（A/B+/B/C+/C/D）")
#     value_score: float = Field(..., description="Valueスコア")
#     growth_score: float = Field(..., description="Growthスコア")
#     momentum_score: float = Field(..., description="Momentumスコア")
#     score_date: date = Field(..., description="スコア算出日")
#     details: ScoreDetail = Field(..., description="スコア詳細")
#     market_comparison: MarketComparison = Field(..., description="市場平均との比較")
#     updated_at: str = Field(..., description="更新日時")
#
#     class Config:
#         from_attributes = True
#         json_schema_extra = {
#             "example": {
#                 "stock_code": "7203",
#                 "stock_name": "トヨタ自動車",
#                 "total_score": 75.5,
#                 "rank": "B+",
#                 "value_score": 78.2,
#                 "growth_score": 65.5,
#                 "momentum_score": 78.3,
#                 "score_date": "2026-02-09",
#                 "details": {
#                     "per": 15.53,
#                     "per_score": 49.2,
#                     "pbr": 2.32,
#                     "pbr_score": 54.0,
#                     "dividend_yield": 9.66,
#                     "dividend_score": 100.0,
#                     "revenue_growth_rate": 4.48,
#                     "rsi": 55.3,
#                     "rsi_score": 100.0,
#                     "volume_change_rate": 12.5,
#                     "volume_change_score": 70.6
#                 },
#                 "market_comparison": {
#                     "total_diff": 25.5,
#                     "value_diff": 28.2,
#                     "growth_diff": 15.5,
#                     "momentum_diff": 28.3
#                 },
#                 "updated_at": "2026-02-09T10:30:00"
#             }
#         }
```

**確認コマンド:**
```bash
cat backend/app/schemas/score.py
docker-compose exec backend python -m py_compile app/schemas/score.py
```

---

### ステップ3: サービス層実装（45分）

#### アクション3-1: score_service.py作成

**GitHub Copilotへの指示:**

```python
# ファイル名: backend/app/services/score_service.py

# Copilotに以下を指示:
# スコアデータを取得するサービス層を実装してください
#
# from sqlalchemy.orm import Session
# from sqlalchemy import text
# from datetime import datetime
# import json
#
# MARKET_AVERAGE = {
#     "total": 50.0,
#     "value": 50.0,
#     "growth": 50.0,
#     "momentum": 50.0
# }
#
# def get_stock_score(stock_code: str, db: Session) -> dict | None:
#     """
#     指定された銘柄のスコアを取得
#     
#     Args:
#         stock_code: 銘柄コード（例: '7203'）
#         db: SQLAlchemyのSession
#     
#     Returns:
#         スコアデータの辞書、存在しない場合はNone
#     """
#     
#     query = text("""
#         SELECT 
#             s.stock_code,
#             s.stock_name,
#             ds.total_score,
#             ds.rank,
#             ds.value_score,
#             ds.growth_score,
#             ds.momentum_score,
#             ds.score_date,
#             ds.details,
#             ds.created_at
#         FROM daily_scores ds
#         JOIN stocks s ON ds.stock_code = s.stock_code
#         WHERE ds.stock_code = :stock_code
#         ORDER BY ds.score_date DESC
#         LIMIT 1
#     """)
#     
#     result = db.execute(query, {"stock_code": stock_code}).fetchone()
#     
#     if not result:
#         return None
#     
#     # 市場平均との比較を計算
#     market_comparison = {
#         'total_diff': round(result.total_score - MARKET_AVERAGE['total'], 2),
#         'value_diff': round(result.value_score - MARKET_AVERAGE['value'], 2),
#         'growth_diff': round(result.growth_score - MARKET_AVERAGE['growth'], 2),
#         'momentum_diff': round(result.momentum_score - MARKET_AVERAGE['momentum'], 2)
#     }
#     
#     return {
#         'stock_code': result.stock_code,
#         'stock_name': result.stock_name,
#         'total_score': float(result.total_score),
#         'rank': result.rank,
#         'value_score': float(result.value_score),
#         'growth_score': float(result.growth_score),
#         'momentum_score': float(result.momentum_score),
#         'score_date': result.score_date,
#         'details': result.details,
#         'market_comparison': market_comparison,
#         'updated_at': result.created_at.isoformat()
#     }
```

**確認コマンド:**
```bash
cat backend/app/services/score_service.py
docker-compose exec backend python -m py_compile app/services/score_service.py
```

---

### ステップ4: ルーター実装（45分）

#### アクション4-1: scores.py（ルーター）作成

**GitHub Copilotへの指示:**

```python
# ファイル名: backend/app/routers/scores.py

# Copilotに以下を指示:
# スコアAPIのエンドポイントを実装してください
#
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app.database import get_db
# from app.schemas.score import ScoreResponse
# from app.services.score_service import get_stock_score
#
# router = APIRouter(
#     prefix="/api",
#     tags=["scores"]
# )
#
# @router.get("/score/{stock_code}", response_model=ScoreResponse)
# def get_score(stock_code: str, db: Session = Depends(get_db)):
#     """
#     指定された銘柄のスコアを取得
#     
#     Args:
#         stock_code: 銘柄コード（7203, 6758, 9984）
#     
#     Returns:
#         ScoreResponse: スコアデータ
#     
#     Raises:
#         HTTPException 404: 銘柄が見つからない
#         HTTPException 400: 無効な銘柄コード
#     """
#     
#     # 銘柄コードのバリデーション（4桁の数字）
#     if not stock_code.isdigit() or len(stock_code) != 4:
#         raise HTTPException(
#             status_code=400,
#             detail=f"無効な銘柄コードです: {stock_code}"
#         )
#     
#     # スコア取得
#     score_data = get_stock_score(stock_code, db)
#     
#     if not score_data:
#         raise HTTPException(
#             status_code=404,
#             detail=f"銘柄コード {stock_code} のスコアが見つかりません"
#         )
#     
#     return score_data
```

**確認コマンド:**
```bash
cat backend/app/routers/scores.py
docker-compose exec backend python -m py_compile app/routers/scores.py
```

---

### ステップ5: API動作確認（30分）

#### アクション5-1: バックエンド再起動

**コマンド:**
```bash
docker-compose restart backend
docker-compose logs backend | tail -20
```

**期待されるログ:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

---

#### アクション5-2: cURLでテスト

**コマンド:**
```bash
# ルートエンドポイント
curl http://localhost:8000/

# スコアエンドポイント（トヨタ）
curl http://localhost:8000/api/score/7203

# 存在しない銘柄
curl http://localhost:8000/api/score/0000

# 無効な銘柄コード
curl http://localhost:8000/api/score/abc
```

---

#### アクション5-3: Swagger UI確認

**ブラウザで確認:**
```
URL: http://localhost:8000/docs

確認項目:
- GET /api/score/{stock_code} が表示される
- Try it out で 7203 を入力
- Execute をクリック
- レスポンスが200 OKで返ってくる
```

---

### Day 8完了確認

```bash
# 1. ファイル存在確認
ls -l backend/app/main.py
ls -l backend/app/schemas/score.py
ls -l backend/app/services/score_service.py
ls -l backend/app/routers/scores.py

# 2. API動作確認
curl http://localhost:8000/api/score/7203 | jq .

# 3. 3銘柄すべてで確認
for code in 7203 6758 9984; do
  echo "=== $code ==="
  curl -s http://localhost:8000/api/score/$code | jq '.stock_name, .total_score'
done

echo "✅ Day 8 完了！"
```

---

## Day 9: API実装（完成）- 3.5時間

### ステップ6: エラーハンドリング強化（45分）

#### アクション6-1: カスタム例外ハンドラー追加

**GitHub Copilotへの指示:**

```python
# backend/app/main.py に追加

# Copilotに以下を指示:
# カスタム例外ハンドラーを追加してください
#
# from fastapi import Request
# from fastapi.responses import JSONResponse
# from fastapi.exceptions import RequestValidationError
# from sqlalchemy.exc import OperationalError
#
# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     return JSONResponse(
#         status_code=400,
#         content={
#             "error": "バリデーションエラー",
#             "detail": exc.errors()
#         }
#     )
#
# @app.exception_handler(OperationalError)
# async def database_exception_handler(request: Request, exc: OperationalError):
#     return JSONResponse(
#         status_code=503,
#         content={
#             "error": "データベース接続エラー",
#             "detail": "データベースに接続できません"
#         }
#     )
#
# @app.exception_handler(Exception)
# async def general_exception_handler(request: Request, exc: Exception):
#     return JSONResponse(
#         status_code=500,
#         content={
#             "error": "内部サーバーエラー",
#             "detail": "予期しないエラーが発生しました"
#         }
#     )
```

**テスト:**
```bash
# バリデーションエラー
curl http://localhost:8000/api/score/abc

# 存在しない銘柄
curl http://localhost:8000/api/score/0000
```

---

### ステップ7: レスポンスタイム測定（30分）

#### アクション7-1: パフォーマンステスト

**コマンド:**
```bash
# 10回実行して平均レスポンスタイムを測定
for i in {1..10}; do
  time curl -s http://localhost:8000/api/score/7203 > /dev/null
done
```

**期待される結果:**
- レスポンスタイム: <500ms（平均）

---

### ステップ8: AIセキュリティ監査（30分）🤖

#### アクション8-1: セキュリティ監査実施

**Claude/ChatGPTに以下のプロンプトを入力:**

```
このFastAPIエンドポイントに対して、セキュリティレビューしてください:

[backend/app/routers/scores.py の内容を貼り付け]

チェック項目:
1. SQLインジェクション脆弱性
2. N+1クエリ問題
3. レート制限の必要性
4. エラーハンドリングの妥当性
5. 認証・認可の必要性
6. CORS設定の妥当性
7. 入力バリデーションの妥当性

推奨される改善点があれば教えてください。
```

**AIの回答を記録:**
```bash
cat > docs/api_security_review.md << 'EOF'
# API セキュリティレビュー

## 監査実施日
2026年2月11日

## 指摘事項

[AIの回答をここに貼り付け]

## 対応状況

1. [指摘事項1]: [対応内容]
2. [指摘事項2]: [対応内容]
EOF
```

---

### ステップ9: APIドキュメント整備（45分）

#### アクション9-1: api_endpoints.md作成

**GitHub Copilotへの指示:**

```markdown
# ファイル名: docs/api_endpoints.md

# Copilotに以下を指示:
# API仕様書を作成してください
#
# # ZenJP MVP API 仕様書
#
# ## ベースURL
# - 開発環境: http://localhost:8000
#
# ## エンドポイント一覧
#
# ### GET /api/score/{stock_code}
# 指定された銘柄のスコアを取得
#
# **パラメータ:**
# - stock_code (string, required): 銘柄コード（4桁の数字）
#
# **レスポンス（200 OK）:**
# ```json
# {
#   "stock_code": "7203",
#   "stock_name": "トヨタ自動車",
#   "total_score": 75.5,
#   "rank": "B+",
#   ...
# }
# ```
#
# **エラーレスポンス:**
# - 400 Bad Request: 無効な銘柄コード
# - 404 Not Found: 銘柄が見つからない
# - 503 Service Unavailable: データベース接続エラー
```

---

### ステップ10: Postmanコレクション作成（30分）

#### アクション10-1: Postmanでテスト

**手順:**

1. Postmanを起動
2. 新しいコレクション作成: "ZenJP MVP API"
3. リクエスト追加:
   - GET /
   - GET /health
   - GET /api/score/7203
   - GET /api/score/6758
   - GET /api/score/9984
   - GET /api/score/0000（404テスト）
   - GET /api/score/abc（400テスト）
4. コレクションをエクスポート: `docs/ZenJP_MVP_API.postman_collection.json`

---

### Day 9完了確認

```bash
# 1. エラーハンドリング確認
curl http://localhost:8000/api/score/abc

# 2. レスポンスタイム確認
time curl -s http://localhost:8000/api/score/7203 > /dev/null

# 3. ドキュメント確認
cat docs/api_endpoints.md
cat docs/api_security_review.md

# 4. Swagger UI確認
open http://localhost:8000/docs

echo "✅ Day 9 完了！"
```

---

## トラブルシューティング

### 問題1: CORSエラー

**症状:**
```
Access to fetch has been blocked by CORS policy
```

**解決策:**
```python
# backend/app/main.py を確認
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # ← 確認
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 問題2: APIレスポンスが404

**症状:**
```
curl http://localhost:8000/api/score/7203
404 Not Found
```

**解決策:**
```python
# backend/app/main.py を確認
from app.routers import scores
app.include_router(scores.router)

# バックエンド再起動
docker-compose restart backend
```

---

## Day 8-9 完了報告

**所要時間:** 7時間  
**成果物:**
- ✅ FastAPI基本構造完成
- ✅ GET /api/score/{stock_code} エンドポイント
- ✅ エラーハンドリング実装
- ✅ CORS設定完了
- ✅ Swagger UIドキュメント
- ✅ セキュリティ監査実施（AI）
- ✅ API仕様書作成
- ✅ Postmanコレクション作成

**次のステップ:** Day 10-12（UI実装）
