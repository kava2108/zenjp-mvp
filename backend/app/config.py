from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str
    APP_ENV: str
    APP_DEBUG: bool

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    DATABASE_URL: str

    CORS_ORIGINS: str

    class Config:
        env_file = ".env"
        extra = 'ignore'  # 定義されていない環境変数を無視

settings = Settings()
