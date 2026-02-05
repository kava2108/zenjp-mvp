"""モデルと設定の軽量テスト"""
import importlib
import sys


def test_settings_load_with_env(monkeypatch):
    """Settingsが環境変数から読み込める"""
    monkeypatch.setenv("APP_NAME", "ZenJP")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("APP_DEBUG", "false")
    monkeypatch.setenv("POSTGRES_USER", "zenjp")
    monkeypatch.setenv("POSTGRES_PASSWORD", "password")
    monkeypatch.setenv("POSTGRES_HOST", "db")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    monkeypatch.setenv("POSTGRES_DB", "zenjp_mvp")
    monkeypatch.setenv("DATABASE_URL", "postgresql://zenjp:password@db:5432/zenjp_mvp")
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000")

    if "app.config" in sys.modules:
        del sys.modules["app.config"]
    config = importlib.import_module("app.config")

    assert config.settings.APP_NAME == "ZenJP"
    assert config.settings.APP_ENV == "test"


def test_sqlalchemy_models_importable():
    """SQLAlchemyモデルがインポートできる"""
    from app.models.score import DailyScore
    from app.models.stock import Stock

    assert DailyScore.__tablename__ == "daily_scores"
    assert Stock.__tablename__ == "stocks"