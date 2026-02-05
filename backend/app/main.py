from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import OperationalError
from app.routers import scores

app = FastAPI(
    title="ZenJP MVP API",
    version="1.0.0",
    description="日本株スコアリングシステムAPI"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost", "http://38.242.205.42:3000", "http://38.242.205.42:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター
app.include_router(scores.router)

# カスタム例外ハンドラー

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "バリデーションエラー",
            "detail": exc.errors()
        }
    )


@app.exception_handler(OperationalError)
async def database_exception_handler(request: Request, exc: OperationalError):
    return JSONResponse(
        status_code=503,
        content={
            "error": "データベース接続エラー",
            "detail": "データベースに接続できません"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "内部サーバーエラー",
            "detail": "予期しないエラーが発生しました"
        }
    )


@app.get("/")
async def root():
    return {
        "message": "ZenJP MVP API",
        "version": "1.0.0",
        "endpoints": ["/api/score/{stock_code}", "/health", "/docs"]
    }

@app.get("/health")
async def health():
    return {"status": "ok"}
