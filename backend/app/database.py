"""
データベース接続設定
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# データベースURL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://zenjp:password@db:5432/zenjp_mvp")

# SQLAlchemyエンジン作成
engine = create_engine(DATABASE_URL, echo=True)

# セッションローカル
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ベースクラス
Base = declarative_base()

# Dependency Injection用
def get_db():
    """
    データベースセッションを取得する依存性注入関数
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
