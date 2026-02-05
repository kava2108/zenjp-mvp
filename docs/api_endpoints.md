# ZenJP MVP API 仕様書

**バージョン:** 1.0.0  
**作成日:** 2026年2月3日  
**ステータス:** MVP完成

---

## 📌 ベースURL

| 環境 | URL |
|------|-----|
| 開発環境 | `http://localhost:8000` |
| 本番環境 | `https://api.zenjp.com` （予定） |

---

## 🔌 API情報

- **タイトル:** ZenJP MVP API
- **説明:** 日本株スコアリングシステムAPI
- **バージョン:** 1.0.0
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc UI:** `http://localhost:8000/redoc`

---

## 📋 エンドポイント一覧

### 1️⃣ GET / - ルート情報

**説明:** API のルート情報を取得

**リクエスト:**
```bash
curl http://localhost:8000/
```

**レスポンス (200 OK):**
```json
{
  "message": "ZenJP MVP API",
  "version": "1.0.0",
  "endpoints": [
    "/api/score/{stock_code}",
    "/health",
    "/docs"
  ]
}
```

---

### 2️⃣ GET /health - ヘルスチェック

**説明:** API の稼働状態を確認

**リクエスト:**
```bash
curl http://localhost:8000/health
```

**レスポンス (200 OK):**
```json
{
  "status": "ok"
}
```

**ステータスコード:**
- `200 OK` - 正常に稼働中

---

### 3️⃣ GET /api/score/{stock_code} - スコア取得（⭐ メインエンドポイント）

**説明:** 指定された銘柄のスコアを取得

#### パラメータ

| パラメータ | 型 | 必須 | 説明 | 例 |
|-----------|-----|------|------|-----|
| `stock_code` | string | ✅ | 銘柄コード（4桁の数字） | `7203` |

#### バリデーション

- **形式:** 4桁の数字
- **許可値:** 0000-9999
- **推奨値:** 7203（トヨタ）, 6758（ソニー）, 9984（ソフトバンク）

#### リクエスト例

```bash
# トヨタ自動車
curl http://localhost:8000/api/score/7203

# ソニーグループ
curl http://localhost:8000/api/score/6758

# ソフトバンクグループ
curl http://localhost:8000/api/score/9984
```

#### レスポンス (200 OK)

```json
{
  "stock_code": "7203",
  "stock_name": "トヨタ自動車",
  "total_score": 72.63,
  "rank": "B+",
  "value_score": 100.0,
  "growth_score": 50.0,
  "momentum_score": 70.51,
  "score_date": "2026-02-03",
  "details": {
    "per": 1.15,
    "per_score": 100.0,
    "pbr": 0.27,
    "pbr_score": 100.0,
    "dividend_yield": 8.68,
    "dividend_score": 100.0,
    "revenue_growth_rate": null,
    "rsi": 62.19,
    "rsi_score": 94.63,
    "volume_change_rate": -0.72,
    "volume_change_score": null,
    "volume_score": 46.39
  },
  "market_comparison": {
    "total_diff": 22.63,
    "value_diff": 50.0,
    "growth_diff": 0.0,
    "momentum_diff": 20.51
  },
  "updated_at": "2026-02-03T07:32:16.611528"
}
```

#### レスポンスフィールド説明

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `stock_code` | string | 銘柄コード |
| `stock_name` | string | 銘柄名 |
| `total_score` | float | 総合スコア（0-100） |
| `rank` | string | ランク評価（S/A/B/C/D） |
| `value_score` | float | 割安性スコア |
| `growth_score` | float | 成長性スコア |
| `momentum_score` | float | 勢いスコア |
| `score_date` | date | スコア算出日 |
| `details` | object | 詳細指標 |
| `market_comparison` | object | 市場平均との比較 |
| `updated_at` | string | 更新日時（ISO 8601） |

#### スコア詳細フィールド

| フィールド | 説明 |
|-----------|------|
| `per` | PER（株価収益率） |
| `per_score` | PERスコア |
| `pbr` | PBR（株価純資産倍率） |
| `pbr_score` | PBRスコア |
| `dividend_yield` | 配当利回り（%） |
| `dividend_score` | 配当スコア |
| `revenue_growth_rate` | 売上成長率（%） |
| `rsi` | RSI（相対力指数） |
| `rsi_score` | RSIスコア |
| `volume_change_rate` | 出来高変化率（%） |
| `volume_change_score` | 出来高変化スコア |
| `volume_score` | 出来高スコア |

#### 市場比較フィールド

| フィールド | 説明 |
|-----------|------|
| `total_diff` | 総合スコア差分（銘柄スコア - 市場平均） |
| `value_diff` | 割安性スコア差分 |
| `growth_diff` | 成長性スコア差分 |
| `momentum_diff` | 勢いスコア差分 |

#### ステータスコード

| コード | 説明 | 例 |
|-------|------|-----|
| `200 OK` | 正常 | `{"stock_code": "7203", ...}` |
| `400 Bad Request` | 無効な銘柄コード | `{"detail": "無効な銘柄コードです: abc"}` |
| `404 Not Found` | スコアが見つからない | `{"detail": "銘柄コード 0000 のスコアが見つかりません"}` |
| `503 Service Unavailable` | データベース接続エラー | `{"error": "データベース接続エラー"}` |
| `500 Internal Server Error` | 内部サーバーエラー | `{"error": "内部サーバーエラー"}` |

#### エラーレスポンス例

**400 Bad Request（不正な銘柄コード）:**
```bash
curl http://localhost:8000/api/score/abc
```

```json
{
  "detail": "無効な銘柄コードです: abc"
}
```

**404 Not Found（スコアが見つからない）:**
```bash
curl http://localhost:8000/api/score/0000
```

```json
{
  "detail": "銘柄コード 0000 のスコアが見つかりません"
}
```

---

## 🎨 認可・認証

| 項目 | 状態 | 備考 |
|------|------|------|
| **認証** | なし | MVPフェーズ |
| **認可** | なし | オープンAPI |
| **レート制限** | なし | PHASE5で実装予定 |

---

## ⚡ パフォーマンス

### レスポンスタイム測定結果

| リクエスト | 平均時間 | 最小時間 | 最大時間 |
|-----------|---------|---------|---------|
| `/api/score/{code}` | ~10ms | 7ms | 39ms |
| `/` | ~5ms | - | - |
| `/health` | ~3ms | - | - |

**目標値:** < 500ms  
**実績:** 平均 10-15ms ✅ **目標達成**

---

## 🔄 レスポンスヘッダー

```
Content-Type: application/json
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, OPTIONS
Access-Control-Allow-Headers: Content-Type
X-Process-Time: 0.012s
```

---

## 📊 サンプルコード

### Python (requests)

```python
import requests

response = requests.get("http://localhost:8000/api/score/7203")
data = response.json()

print(f"銘柄: {data['stock_name']}")
print(f"スコア: {data['total_score']}")
print(f"ランク: {data['rank']}")
```

### JavaScript (fetch)

```javascript
const response = await fetch("http://localhost:8000/api/score/7203");
const data = await response.json();

console.log(`銘柄: ${data.stock_name}`);
console.log(`スコア: ${data.total_score}`);
console.log(`ランク: ${data.rank}`);
```

### cURL

```bash
# トヨタのスコア取得
curl http://localhost:8000/api/score/7203 | jq .

# すべての銘柄を取得
for code in 7203 6758 9984; do
  curl -s http://localhost:8000/api/score/$code | jq '.stock_name, .total_score'
done
```

---

## 🛠️ 開発環境構築

### 起動

```bash
cd /home/ubuntu/workspace/zenjp-mvp
docker-compose up -d
```

### Swagger UI確認

```
http://localhost:8000/docs
```

### ログ確認

```bash
docker-compose logs backend -f
```

---

## 📅 API仕様変更履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2026-02-03 | 1.0.0 | MVP完成版公開 |

---

## 📞 サポート情報

- **GitHub:** https://github.com/zenjp/mvp
- **Issues:** https://github.com/zenjp/mvp/issues
- **ドキュメント:** `/docs` ディレクトリ

---

**最終更新:** 2026年2月3日
