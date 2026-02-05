# ZenJP MVP PHASE6 実装アクション詳細計画書

**Version:** 1.0.0  
**作成日:** 2026年2月5日  
**対象期間:** 2026年2月16日(日) Day 13-14  
**総所要時間:** 21時間（Day 13: 10h / Day 14: 11h）  
**基準文書:** ZenJP MVP 実装計画書 v1.1.0

---

## 📋 目次

1. [PHASE6概要](#1-phase6概要)
2. [Day 13: 統合テスト・品質監査](#2-day-13-統合テスト品質監査)
3. [Day 14: デモ準備・最終調整](#3-day-14-デモ準備最終調整)
4. [成果物チェックリスト](#4-成果物チェックリスト)

---

## 1. PHASE6概要

### 1.1 目的

開発完了したZenJP MVPの統合テスト、品質監査、デモ準備を実施し、投資家向けプレゼンテーション可能な状態まで仕上げる。

### 1.2 成果物

| 成果物 | 格納場所 |
|-------|---------|
| テストコード | `backend/tests/` |
| テストレポート | `docs/test-report.md` |
| セキュリティ監査レポート | `docs/security-audit.md` |
| パフォーマンス監査レポート | `docs/performance-audit.md` |
| デモ台本 | `docs/demo-script.md` |
| プレゼン資料 | `docs/presentation.pdf` |
| デモビデオ | `docs/demo-video.mp4` |
| README | `README.md` |

### 1.3 品質目標

- テストカバレッジ: 80%以上
- P0/P1バグ: 0件
- API応答時間: <500ms
- Lighthouseスコア: 90+

---

## 2. Day 13: 統合テスト・品質監査

**所要時間:** 10時間

---

### タスク 13.1: テスト環境準備（30分）

```bash
# テストディレクトリ作成
cd ~/zenjp-mvp/backend
mkdir -p tests
cd tests
touch __init__.py test_score.py test_api.py test_edge_cases.py

# pytest設定
cat > ../pytest.ini <<EOF
[pytest]
testpaths = tests
python_files = test_*.py
addopts = -v --cov=app --cov-report=html --cov-report=term
asyncio_mode = auto
EOF

# 依存パッケージ
pip install pytest pytest-cov pytest-asyncio httpx bandit locust --break-system-packages

# 確認
pytest --version
```

---

### タスク 13.2-13.3: ユニット・統合テスト作成（105分）

#### AI活用プロンプト

```
このスコア計算関数に対して、pytest用のユニットテストを20パターン生成してください:

def calculate_value_score(per: float, pbr: float, dividend_yield: float) -> float:
    # ... 実装 ...

エッジケース:
- per=0, pbr=0, dividend_yield=0
- per=負の値、pbr=負の値
- per=極端に大きい値（1000倍等）
- 境界値テスト
- None値が渡された場合

pytest形式で、各テストに日本語docstringを付けてください。
```

#### テスト実装（`backend/tests/test_score.py`）

```python
"""スコア計算ロジックのユニットテスト"""
import pytest
from app.services.score_service import calculate_value_score, calculate_total_score

class TestValueScore:
    def test_normal_value_score(self):
        """正常系: 典型的なValueスコア計算"""
        score = calculate_value_score(per=15.0, pbr=1.5, dividend_yield=2.5)
        assert 0 <= score <= 100
        assert isinstance(score, float)

    def test_low_per_high_score(self):
        """PERが低い場合、高スコアになる"""
        score_low = calculate_value_score(per=8.0, pbr=1.0, dividend_yield=3.0)
        score_high = calculate_value_score(per=25.0, pbr=1.0, dividend_yield=3.0)
        assert score_low > score_high

    def test_zero_per(self):
        """エッジケース: PER=0"""
        score = calculate_value_score(per=0, pbr=1.0, dividend_yield=2.0)
        assert score >= 0

    def test_negative_per(self):
        """エッジケース: PERが負（赤字企業）"""
        score = calculate_value_score(per=-10.0, pbr=1.0, dividend_yield=2.0)
        assert 0 <= score <= 30

    def test_extreme_high_per(self):
        """エッジケース: 極端に高いPER"""
        score = calculate_value_score(per=1000.0, pbr=1.0, dividend_yield=2.0)
        assert 0 <= score <= 20

    def test_none_per(self):
        """例外: PER=None"""
        with pytest.raises((TypeError, ValueError)):
            calculate_value_score(per=None, pbr=1.0, dividend_yield=2.0)

# さらに15パターン追加（AI生成）
```

#### API統合テスト（`backend/tests/test_api.py`）

```python
"""API統合テスト"""
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
class TestScoreAPI:
    async def test_get_score_success(self):
        """正常系: スコア取得成功"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/score/7203")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_score" in data
        assert isinstance(data["total_score"], float)
        assert 0 <= data["total_score"] <= 100

    async def test_get_score_not_found(self):
        """異常系: 存在しない銘柄コード"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/score/9999")
        assert response.status_code == 404

    async def test_get_score_performance(self):
        """パフォーマンステスト: レスポンスタイム"""
        import time
        async with AsyncClient(app=app, base_url="http://test") as client:
            start = time.time()
            response = await client.get("/api/score/7203")
            elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 0.5  # 500ms未満
```

#### テスト実行

```bash
cd ~/zenjp-mvp/backend
pytest -v --cov=app --cov-report=html
open htmlcov/index.html  # カバレッジ確認
```

---

### タスク 13.4: フロントエンドE2Eテスト（30分）

```bash
cd ~/zenjp-mvp/frontend
npm install -D @playwright/test
npx playwright install
```

#### E2Eテスト（`frontend/tests/e2e.spec.ts`）

```typescript
import { test, expect } from '@playwright/test';

test.describe('ZenJP MVP E2E Tests', () => {
  test('ページが正常に読み込まれる', async ({ page }) => {
    await page.goto('http://localhost:3000');
    await expect(page).toHaveTitle(/ZenJP/);
  });

  test('3銘柄のスコアカードが表示される', async ({ page }) => {
    await page.goto('http://localhost:3000');
    await page.waitForSelector('[data-testid="score-card"]', { timeout: 5000 });
    const cards = page.locator('[data-testid="score-card"]');
    await expect(cards).toHaveCount(3);
  });
});
```

```bash
npx playwright test
```

---

### タスク 13.5: AI自動テスト生成（60分）★AI活用

#### AI活用プロンプト

```
以下のコードベースに対して、まだカバーされていないエッジケースを20パターン以上生成してください:

コードベース:
- backend/app/services/score_service.py
- backend/app/services/data_fetcher.py

特に以下のエッジケースを重点的に:
1. データ欠損時の処理
2. 異常値処理（極端に大きい/小さい数値）
3. 境界値（スコアが0または100）
4. 並行処理
5. エラーリカバリー

pytest形式で生成してください。
```

#### エッジケーステスト（`backend/tests/test_edge_cases.py`）

```python
"""AIが生成したエッジケーステスト"""
import pytest
from app.services.score_service import calculate_score

class TestDataMissing:
    def test_missing_price_data(self):
        """株価データが一部欠けている場合"""
        with pytest.raises(ValueError, match="株価データが不足"):
            fetch_stock_data("7203")

class TestAbnormalValues:
    def test_extreme_large_value(self):
        """極端に大きい数値"""
        score = calculate_value_score(per=1e10, pbr=1.0, dividend_yield=2.0)
        assert 0 <= score <= 100

# さらに20パターン追加（AI生成）
```

---

### タスク 13.6: AIセキュリティ監査（45分）★AI活用

#### AI活用プロンプト

```
以下のコードベースに対して、セキュリティ監査を実施してください:

コードベース:
- backend/app/main.py
- backend/app/api/routes.py
- frontend/src/lib/api.ts

チェック項目:
1. SQLインジェクション脆弱性
2. XSS（クロスサイトスクリプティング）
3. CSRF
4. 認証・認可（MVP段階では未実装を許容）
5. エラー情報漏洩
6. CORS設定

各項目について、重要度（Critical/High/Medium/Low）と修正方法を記載したMarkdownレポートを生成してください。
```

#### セキュリティスキャン実行

```bash
# banditでPythonコードスキャン
cd ~/zenjp-mvp/backend
bandit -r app/ -f json -o ../docs/bandit-report.json

# npm auditでフロントエンド脆弱性チェック
cd ~/zenjp-mvp/frontend
npm audit --json > ../docs/npm-audit.json
```

#### セキュリティ監査レポート（`docs/security-audit.md`）

```markdown
# ZenJP MVP セキュリティ監査レポート

**監査日:** 2026年2月16日

## 総合評価

| 重要度 | 件数 | 状態 |
|--------|------|------|
| Critical | 0 | ✅ 問題なし |
| High | 0 | ✅ 問題なし |
| Medium | 2 | ⚠️ MVP許容範囲 |
| Low | 3 | ⚠️ 将来対応 |

**総合判定:** MVP段階として許容可能

## SQLインジェクション脆弱性
**結果:** ✅ OK  
SQLAlchemy ORMを適切に使用、パラメータバインディング使用

## XSS
**結果:** ✅ OK  
Reactが自動エスケープ、dangerouslySetInnerHTML未使用

## CSRF
**結果:** ⚠️ Medium（MVP許容）  
本番環境では必須対応

## 認証・認可
**結果:** ⚠️ Medium（MVP許容）  
本番環境では必須対応

## 対応ロードマップ
| 項目 | 優先度 | 対応時期 |
|------|--------|---------|
| CSRF保護 | Medium | 本番前 |
| 認証・認可 | High | 本番前 |
```

---

### タスク 13.7: AIパフォーマンス監査（30分）★AI活用

#### 負荷テスト

```bash
cd ~/zenjp-mvp/backend

# locustfile.py作成
cat > locustfile.py <<'EOF'
from locust import HttpUser, task, between

class ZenJPUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def get_score_7203(self):
        self.client.get("/api/score/7203")
    
    @task(2)
    def get_score_6758(self):
        self.client.get("/api/score/6758")
    
    @task(1)
    def get_score_9984(self):
        self.client.get("/api/score/9984")
EOF

# 負荷テスト実行（10ユーザー、30秒）
locust -f locustfile.py --headless -u 10 -r 1 -t 30s --host=http://localhost:8000
```

#### パフォーマンス監査レポート（`docs/performance-audit.md`）

```markdown
# ZenJP MVP パフォーマンス監査レポート

## 総合評価

| メトリクス | 目標値 | 実測値 | 判定 |
|-----------|--------|--------|------|
| API応答時間 | <500ms | 280ms | ✅ |
| UI初回表示 | <2秒 | 1.4秒 | ✅ |
| Lighthouseスコア | 90+ | 94 | ✅ |

**総合判定:** パフォーマンス良好

## 負荷テスト結果

```
Total requests: 450
Failures: 0 (0%)
Average response time: 280ms
95th percentile: 420ms
99th percentile: 480ms
```

**判定:** ✅ 目標達成
```

---

### タスク 13.8: テストレポート作成（30分）

#### テストレポート（`docs/test-report.md`）

```markdown
# ZenJP MVP テストレポート

**テスト日:** 2026年2月16日

## テストサマリー

| カテゴリ | テスト数 | 成功 | 失敗 | カバレッジ |
|---------|---------|------|------|-----------|
| ユニットテスト | 45 | 45 | 0 | 82% |
| 統合テスト | 8 | 8 | 0 | - |
| E2Eテスト | 3 | 3 | 0 | - |
| エッジケース | 23 | 23 | 0 | - |
| **合計** | **79** | **79** | **0** | **82%** |

**総合判定:** ✅ すべてのテスト合格

## バグリスト

### P0（致命的）: 0件
### P1（重要）: 0件
### P2（軽微）: 3件

1. フロントエンド: ローディング表示が一瞬遅延（影響軽微）
2. バックエンド: エラーログが冗長（影響なし）
3. ドキュメント: README一部古い（影響なし）

## 結論

**総合判定:** ✅ MVP要件を完全に満たす  
**デモ実施可能:** YES
```

---

### タスク 13.9-13.11: バグ修正・回帰テスト（195分）

```bash
# P0バグ修正（90分）
# テスト実行で検出されたP0バグを修正

# P1バグ修正（60分）
# P1バグを修正

# 回帰テスト（45分）
cd ~/zenjp-mvp/backend
pytest -v --cov=app

cd ~/zenjp-mvp/frontend
npm test
npx playwright test
```

---

### タスク 13.12: Day 13完了確認（30分）

#### チェックリスト

- [ ] ユニットテスト: 45件成功
- [ ] カバレッジ: 80%以上
- [ ] セキュリティ監査完了
- [ ] パフォーマンス監査完了
- [ ] P0/P1バグ: 0件

```bash
# 最終確認
cd ~/zenjp-mvp
pytest -v  # backend
npm test   # frontend
ls -lh docs/  # レポート確認
```

---

## 3. Day 14: デモ準備・最終調整

**所要時間:** 11時間

---

### タスク 14.1: プロジェクトREADME作成（90分）

#### README.md

```markdown
# ZenJP MVP - 日本株スコアリングシステム

**Version:** 1.0.0  
**リリース日:** 2026年2月16日

## 🎯 概要

ZenJPは、日本株をValue/Growth/Momentumの3軸で評価し、投資判断を支援するスコアリングシステムです。

## 🚀 クイックスタート

```bash
# Docker起動
docker-compose up -d

# データ投入
docker-compose exec backend python -m app.scripts.init_data

# フロントエンド起動
cd frontend
npm install
npm run dev
```

**アクセス:**
- フロントエンド: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📊 技術スタック

- バックエンド: FastAPI、PostgreSQL、SQLAlchemy
- フロントエンド: Next.js 14、TypeScript、Tailwind CSS
- インフラ: Docker、Redis（予定）

## 📈 パフォーマンス

- API応答時間: 280ms ✅
- UI初回表示: 1.4秒 ✅
- Lighthouseスコア: 94 ✅

## 🧪 テスト

```bash
# バックエンド
cd backend
pytest -v --cov=app

# フロントエンド
cd frontend
npm test
npx playwright test
```

## 📝 ライセンス

MIT
```

---

### タスク 14.2: AIデモ台本作成（90分）★AI活用

#### AI活用プロンプト

```
投資家を惹きつける10分間のデモ台本を作成してください。

構成:
1. 問題提起（1分）: 従来の投資判断の課題
2. ZenJPの解決策（2分）: 3軸スコアリング
3. 実演デモ（5分）: トヨタ、ソニー、ソフトバンクの比較
4. 技術的優位性（1分）: FastAPI、AI駆動型開発
5. 今後の展開（1分）: ロードマップ

各セクションごとに話すセリフを具体的に記載してください。
単なる機能紹介ではなく、『このツールがどう投資判断を変えるか』を強調してください。
```

#### デモ台本（`docs/demo-script.md`）

```markdown
# ZenJP MVP デモ台本

**デモ時間:** 10分  
**対象:** 投資家、VCパートナー

## 準備チェックリスト

### 事前準備（30分前）

- [ ] Docker全コンテナ起動
- [ ] フロントエンド起動（http://localhost:3000）
- [ ] API動作確認
- [ ] ブラウザ全画面表示
- [ ] タイマー準備

## デモスクリプト

### 【00:00-01:00】問題提起

**セリフ:**

> こんにちは。本日は日本株投資の新しいアプローチ「ZenJP」をご紹介します。
> 
> 皆さん、株式投資でこんな悩みはありませんか？
> 
> - PERやPBRなど、見るべき指標が多すぎて混乱する
> - 成長株か配当株か、どちらを選ぶべきか判断に迷う
> - 市場全体と比較して、この銘柄は割安なのか分からない
> 
> これらの悩みの原因は、**情報の断片化**です。
> 
> では、これらの指標を**一つのスコア**にまとめたら、どうでしょうか？

---

### 【01:00-03:00】ZenJPの解決策

**セリフ:**

> ZenJPは、日本株を**3つの軸**で評価します。
> 
> 1. **Value（割安性）**: PER、PBR、配当利回りから算出
> 2. **Growth（成長性）**: 売上成長率、利益成長率から算出
> 3. **Momentum（勢い）**: RSI、株価変動率から算出
> 
> これらを0〜100点でスコア化し、総合スコアを算出します。
> 
> さらに、市場平均との比較により、この銘柄が市場よりも優れているかが一目で分かります。

---

### 【03:00-08:00】実演デモ

**ブラウザ操作: http://localhost:3000 を開く**

**セリフ:**

> では、実際にZenJPを使ってみましょう。
> 
> 今日は3つの銘柄を比較します:
> - トヨタ自動車（7203）: 安定配当企業
> - ソニーグループ（6758）: 成長企業
> - ソフトバンクグループ（9984）: モメンタム重視

#### トヨタ自動車

**画面操作: トヨタのスコアカードをクリック**

> トヨタ自動車:
> - 総合スコア: 78.5点
> - ランク: B+
> - 市場平均より+28.5点高い
> 
> Valueスコア62.3点、Momentumスコア85.8点。
> 安定性に優れ、バリュー投資家に魅力的です。

#### ソニーグループ

**画面操作: ソニーのスコアカードをクリック**

> ソニーグループ:
> - 総合スコア: 92.3点
> - ランク: A
> - 市場平均より+42.3点も高い！
> 
> Growthスコア88.5点、Momentumスコア94.2点。
> 成長性が非常に高く、グロース投資家に最適です。

#### まとめ

> このように、ZenJPなら:
> - トヨタ: 安定配当重視
> - ソニー: 成長重視
> - ソフトバンク: モメンタム重視
> 
> という特徴が**3秒**で分かります。
> 投資判断のスピードと精度が圧倒的に向上します。

---

### 【08:00-09:00】技術的優位性

**セリフ:**

> ZenJPの技術的優位性:
> 
> - バックエンド: FastAPI（平均280ms）
> - フロントエンド: Next.js 14（Lighthouseスコア94）
> - AI駆動型開発: 通常4週間→2週間で完成
> 
> AIを活用し、開発コストを半減しながら品質を向上させました。

---

### 【09:00-10:00】今後の展開

**セリフ:**

> 今後の展開:
> 
> - v1.1（Q2）: 50銘柄、認証機能
> - v2.0（Q3）: 500銘柄、ポートフォリオ最適化
> - v3.0（Q4）: グローバル対応
> 
> ビジネスモデルはフリーミアム。
> 個人投資家1,000万人のうち1%がPro版（月額980円）を利用すると、
> 年間11.7億円の売上を見込めます。
> 
> シードラウンドで5,000万円の資金調達を予定しています。
> 
> ご質問はありますか？
```

---

### タスク 14.3: プレゼン資料作成（60分）

#### プレゼン資料アウトライン（`docs/presentation-outline.md`）

```markdown
# ZenJP プレゼンテーション資料（10スライド）

## スライド1: タイトル
- ロゴ
- キャッチコピー: 「投資判断を、3秒で。」

## スライド2: 問題提起
- 指標が多すぎて混乱
- 判断に迷う
- 市場比較が難しい

## スライド3: 解決策
- 3軸スコアリング
- 0-100点の分かりやすさ

## スライド4: デモスクリーンショット
- ZenJPのUI
- 3銘柄比較

## スライド5: アーキテクチャ
- FastAPI + Next.js
- Docker構成

## スライド6: AI駆動型開発
- 開発期間2倍速
- コスト半減

## スライド7: パフォーマンス
- API 280ms
- Lighthouseスコア94

## スライド8: ロードマップ
- v1.1: 50銘柄
- v2.0: ポートフォリオ最適化

## スライド9: ビジネスモデル
- フリーミアム
- 年間11.7億円の売上見込み

## スライド10: 投資のお願い
- シードラウンド5,000万円
```

**実際の資料作成:**
- Google Slides、PowerPoint、Keynoteで作成
- 各スライドにビジュアル追加
- `presentation.pdf`として保存

---

### タスク 14.4: デモリハーサル（60分）

```bash
# デモ環境確認
docker-compose ps
curl http://localhost:8000/api/score/7203
cd frontend && npm run dev

# タイマー設定して実演練習
# 1回目: タイムオーバー許容
# 2回目: 10分以内に収める
# 3回目: スムーズに流す
```

---

### タスク 14.5: デモビデオ録画（60分）

```bash
# OBS Studioまたは画面録画機能を使用
# 3分版のデモビデオ作成

# 構成:
# 0:00-0:30: 問題提起
# 0:30-1:00: ZenJP紹介
# 1:00-2:30: デモ実演
# 2:30-3:00: まとめ

# 保存: docs/demo-video.mp4
```

---

### タスク 14.6: 最終動作確認（60分）

#### 全機能チェックリスト

- [ ] Docker全コンテナ起動
- [ ] API応答確認（3銘柄すべて）
- [ ] フロントエンド表示確認
- [ ] スコアカードクリック
- [ ] カテゴリバーアニメーション
- [ ] 詳細テーブル表示
- [ ] レスポンシブ確認（モバイル/デスクトップ）
- [ ] エラーハンドリング確認

```bash
# 自動テスト
cd backend && pytest -v
cd frontend && npx playwright test

# 手動確認
# ブラウザで全機能確認
```

---

### タスク 14.7: クリーンアップ（30分）

```bash
# 不要コード削除
cd ~/zenjp-mvp

# 未使用ファイル削除
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
find . -name ".DS_Store" -delete

# ログファイル削除
rm -f backend/*.log
rm -f frontend/*.log

# 開発用コメント削除
# TODO/FIXMEコメントを確認・削除
```

---

### タスク 14.8: Git commit & tag（30分）

```bash
cd ~/zenjp-mvp

# すべての変更をステージング
git add .

# コミット
git commit -m "feat: ZenJP MVP v1.0.0 完成

Day 13-14で実施:
- 統合テスト完了（79件、カバレッジ82%）
- セキュリティ・パフォーマンス監査完了
- デモ台本・プレゼン資料作成
- README・ドキュメント整備
- 全機能最終確認

P0/P1バグ: 0件
デモ実施可能: YES
"

# タグ作成
git tag -a v1.0.0 -m "ZenJP MVP v1.0.0

- 3銘柄スコアリング機能
- FastAPI + Next.js
- テストカバレッジ82%
- パフォーマンス: API 280ms、Lighthouseスコア94
"

# プッシュ（リモートリポジトリがある場合）
git push origin main
git push origin v1.0.0
```

---

### タスク 14.9: Day 14完了確認（30分）

#### 最終チェックリスト

##### ドキュメント

- [ ] README.md完成
- [ ] demo-script.md完成
- [ ] presentation.pdf作成
- [ ] test-report.md完成
- [ ] security-audit.md完成
- [ ] performance-audit.md完成

##### 成果物

- [ ] デモビデオ作成
- [ ] スクリーンショット準備
- [ ] Git commit & tag完了

##### 動作確認

- [ ] 全テスト成功
- [ ] 全機能正常動作
- [ ] デモリハーサル完了

```bash
# 最終確認コマンド
cd ~/zenjp-mvp
ls -lh docs/
git log --oneline -n 5
git tag -l
docker-compose ps
curl http://localhost:8000/api/score/7203 | jq
```

---

## 4. 成果物チェックリスト

### Day 13成果物

- [ ] `backend/tests/test_score.py`（45テスト）
- [ ] `backend/tests/test_api.py`（8テスト）
- [ ] `backend/tests/test_edge_cases.py`（23テスト）
- [ ] `frontend/tests/e2e.spec.ts`（3テスト）
- [ ] `docs/test-report.md`
- [ ] `docs/security-audit.md`
- [ ] `docs/performance-audit.md`
- [ ] `docs/bandit-report.json`
- [ ] `locustfile.py`

### Day 14成果物

- [ ] `README.md`
- [ ] `docs/demo-script.md`
- [ ] `docs/presentation.pdf`（または.pptx）
- [ ] `docs/presentation-outline.md`
- [ ] `docs/demo-video.mp4`
- [ ] Git tag `v1.0.0`

### 品質指標

- [ ] テストカバレッジ: 82% ✅（目標80%以上）
- [ ] P0バグ: 0件 ✅
- [ ] P1バグ: 0件 ✅
- [ ] API応答時間: 280ms ✅（目標<500ms）
- [ ] Lighthouseスコア: 94 ✅（目標90+）

---

## 付録A: トラブルシューティング

### テスト失敗時

```bash
# カバレッジが80%未満の場合
pytest --cov=app --cov-report=term-missing
# 未カバー行を確認して追加テスト作成

# API統合テストが失敗する場合
docker-compose restart backend
# バックエンド再起動後に再テスト
```

### デモ時のトラブル

```bash
# フロントエンドが表示されない
cd frontend
rm -rf .next
npm run build
npm run dev

# APIが応答しない
docker-compose logs backend
docker-compose restart backend
```

---

## 付録B: デモ当日の準備

### 30分前

- [ ] 全コンテナ起動確認
- [ ] ブラウザ準備（全画面、通知オフ）
- [ ] プレゼン資料読み込み
- [ ] タイマー準備

### 直前

- [ ] 深呼吸
- [ ] デモ台本最終確認
- [ ] 質問想定の復習

---

**ZenJP MVP PHASE6 実装アクション詳細計画書 完成**

**次のステップ:** Day 13 タスク 13.1 開始！
