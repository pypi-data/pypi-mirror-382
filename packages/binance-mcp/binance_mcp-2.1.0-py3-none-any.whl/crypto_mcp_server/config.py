from pydantic_settings import BaseSettings
from typing import Literal, Optional
import secrets


class Settings(BaseSettings):
    # Binance API
    binance_api_key: str
    binance_api_secret: str

    # Risk Management (Optional - if not set, trades without limits)
    max_trade_size_usd: Optional[float] = None  # None = unlimited
    max_daily_loss_usd: Optional[float] = None  # None = no daily loss limit
    max_position_size_usd: Optional[float] = None  # None = unlimited position size

    # Database (stores all trades locally on each computer)
    database_url: str = "sqlite:///./trading.db"

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False



settings = Settings()
