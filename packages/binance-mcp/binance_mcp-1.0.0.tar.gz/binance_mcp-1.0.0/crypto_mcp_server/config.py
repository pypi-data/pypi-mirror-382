from pydantic_settings import BaseSettings
from typing import Literal, Optional
import secrets


class Settings(BaseSettings):
    # Binance API
    binance_api_key: str
    binance_api_secret: str

    # Trading Mode - AI should ask user before each session, but default to paper for safety
    trading_mode: Literal["paper", "live"] = "paper"  # Default, can be overridden per request

    # MCP Server
    mcp_server_host: str = "0.0.0.0"
    mcp_server_port: int = 8000
    mcp_auth_token: Optional[str] = None  # Auto-generated if not provided

    # Risk Management (Optional - if not set, AI trades without limits)
    max_trade_size_usd: Optional[float] = None  # None = unlimited
    max_daily_loss_usd: Optional[float] = None  # None = no daily loss limit
    max_position_size_usd: Optional[float] = None  # None = unlimited position size

    # Auto-detect account balance - always enabled
    auto_detect_balance: bool = True  # Always True - removed from config

    # Database
    database_url: str = "sqlite:///./trading.db"

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Auto-generate secure auth token if not provided
        if not self.mcp_auth_token:
            self.mcp_auth_token = secrets.token_urlsafe(48)  # 64 character base64 token


settings = Settings()
