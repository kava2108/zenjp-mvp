# ZenJP MVP PHASE1 実装アクション詳細計画書（環境構築・DB）

対象フェーズ: Phase 1: 環境構築・DB (Day 1-2)  
前提: すべての実作業は GitHub Copilot に依頼し、あなたは「指示・確認・承認」のみを行う。

---

## 0. 前提条件・ゴール

**ゴール:**

- Docker + Docker Compose で以下3コンテナが `docker compose up` で起動する状態
  - **backend**: FastAPI + SQLAlchemy + Poetry or pip 管理
  - **db**: PostgreSQL 14+
  - **(optional) adminer or pgadmin**: 簡易DB確認用
- DB スキーマ（`stocks`, `stock_prices`, `stock_financials`, `daily_scores`, `market_average_scores`）が `init.sql` で自動作成される状態
- FastAPI プロジェクトの最小スケルトンが起動確認済み（`/health` など）

---

## 1. リポジトリ初期化

**1-1. Git リポジトリ作成**

- **Copilotへの指示内容:**
  - プロジェクトルートを作成し、Git 初期化コマンドを README に記載させる

- **想定コマンド:**
  ```bash
  mkdir zenjp-mvp
  cd zenjp-mvp
  git init