from pydantic_settings import BaseSettings
from typing import Literal, Optional
import secrets


class Settings(BaseSettings):
    # Binance API
    binance_api_key: str
    binance_api_secret: str

    # News API (optional - for crypto news)
    cryptopanic_api_key: Optional[str] = None
    newsapi_key: Optional[str] = None

    # Database (stores all trades locally on each computer)
    database_url: str = "sqlite:///./trading.db"

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False



settings = Settings()
