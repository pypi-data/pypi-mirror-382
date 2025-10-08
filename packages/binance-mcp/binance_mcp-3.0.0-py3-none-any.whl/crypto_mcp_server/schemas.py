from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    STOP_LOSS_LIMIT = "STOP_LOSS_LIMIT"
    TAKE_PROFIT = "TAKE_PROFIT"
    TAKE_PROFIT_LIMIT = "TAKE_PROFIT_LIMIT"


class OrderStatus(str, Enum):
    NEW = "NEW"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


# MCP Protocol Schemas

class MCPContextMetadata(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    namespace: str
    version: str = "1.0"


class MarketDataContext(BaseModel):
    symbol: str
    price: float
    bid: float
    ask: float
    volume_24h: float
    high_24h: float
    low_24h: float
    price_change_24h: float
    price_change_percent_24h: float
    metadata: MCPContextMetadata


class Balance(BaseModel):
    asset: str
    free: float
    locked: float
    total: float
    usd_value: Optional[float] = None


class Position(BaseModel):
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    unrealized_pnl_percent: float


class AccountStateContext(BaseModel):
    balances: List[Balance]
    positions: List[Position]
    total_portfolio_value_usd: float
    metadata: MCPContextMetadata


class Trade(BaseModel):
    id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: float
    fill_price: Optional[float] = None
    status: OrderStatus
    timestamp: datetime
    commission: Optional[float] = None
    commission_asset: Optional[str] = None


class TradeHistoryContext(BaseModel):
    trades: List[Trade]
    metadata: MCPContextMetadata


# New Enhanced Context Types

class CoinInfo(BaseModel):
    """Information about a tradable coin/pair"""
    symbol: str
    base_asset: str  # e.g., BTC
    quote_asset: str  # e.g., USD
    status: str  # TRADING, BREAK, etc.
    price: Optional[float] = None
    volume_24h: Optional[float] = None
    is_margin_trading_allowed: bool = False
    is_spot_trading_allowed: bool = True


class AllMarketsContext(BaseModel):
    """All tradable coins on Binance"""
    markets: List[CoinInfo]
    total_count: int
    metadata: MCPContextMetadata


class FeeInfo(BaseModel):
    """Fee structure for a symbol"""
    symbol: str
    maker_fee: float  # Fee for maker orders (%)
    taker_fee: float  # Fee for taker orders (%)
    spot_trading_fee: Optional[float] = None
    margin_trading_fee: Optional[float] = None


class FeeStructureContext(BaseModel):
    """Trading fees"""
    fees: List[FeeInfo]
    metadata: MCPContextMetadata


class Candlestick(BaseModel):
    """OHLCV candlestick data"""
    open_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    close_time: datetime
    quote_volume: float
    trades_count: int


class CandlestickContext(BaseModel):
    """Historical candlestick data for charting"""
    symbol: str
    timeframe: str  # 1m, 5m, 15m, 1h, 4h, 1d, etc.
    candlesticks: List[Candlestick]
    metadata: MCPContextMetadata


class OrderBookLevel(BaseModel):
    """Order book price level"""
    price: float
    quantity: float


class OrderBookContext(BaseModel):
    """Current order book depth"""
    symbol: str
    bids: List[OrderBookLevel]  # Buy orders
    asks: List[OrderBookLevel]  # Sell orders
    metadata: MCPContextMetadata


class Ticker24h(BaseModel):
    """24-hour ticker statistics"""
    symbol: str
    price_change: float
    price_change_percent: float
    weighted_avg_price: float
    prev_close_price: float
    last_price: float
    bid_price: float
    ask_price: float
    open_price: float
    high_price: float
    low_price: float
    volume: float
    quote_volume: float
    open_time: datetime
    close_time: datetime
    first_trade_id: Optional[int] = None
    last_trade_id: Optional[int] = None
    trade_count: int


class Ticker24hContext(BaseModel):
    """24-hour statistics for symbols"""
    tickers: List[Ticker24h]
    metadata: MCPContextMetadata


class TechnicalIndicator(BaseModel):
    """Technical indicator value"""
    name: str  # RSI, MACD, BB, SMA, EMA, etc.
    value: float
    signal: Optional[str] = None  # BUY, SELL, NEUTRAL
    timestamp: datetime


class TechnicalIndicatorsContext(BaseModel):
    """Technical analysis indicators"""
    symbol: str
    timeframe: str
    indicators: List[TechnicalIndicator]
    metadata: MCPContextMetadata


class MCPContext(BaseModel):
    context_type: Literal["market_data", "account_state", "trade_history"]
    data: Dict[str, Any]
    metadata: MCPContextMetadata


# MCP Actions

class TradeOrderAction(BaseModel):
    action_type: Literal["trade_order"] = "trade_order"
    symbol: str = Field(..., description="Trading pair, e.g., BTCUSD")
    side: OrderSide
    order_type: OrderType = OrderType.MARKET
    quantity: float = Field(..., gt=0, description="Amount to trade")
    price: Optional[float] = Field(None, description="Limit price (required for LIMIT orders)")
    stop_price: Optional[float] = Field(None, description="Stop price for stop orders")
    time_in_force: Optional[str] = Field("GTC", description="GTC, IOC, FOK")


class CancelOrderAction(BaseModel):
    action_type: Literal["cancel_order"] = "cancel_order"
    symbol: str
    order_id: str


class MCPAction(BaseModel):
    action_id: str = Field(default_factory=lambda: f"action_{datetime.utcnow().timestamp()}")
    action: TradeOrderAction | CancelOrderAction
    metadata: Dict[str, Any] = Field(default_factory=dict)


# MCP Action Results

class ActionResult(BaseModel):
    action_id: str
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TradeExecutionResult(BaseModel):
    order_id: str
    symbol: str
    side: OrderSide
    status: OrderStatus
    filled_quantity: float
    average_fill_price: Optional[float] = None
    commission: Optional[float] = None
    commission_asset: Optional[str] = None


# MCP Request/Response

class MCPContextRequest(BaseModel):
    context_types: List[str] = Field(..., description="""
        Available context types:
        - market_data: Current price, bid/ask, volume
        - account_state: Balances, positions, portfolio value
        - trade_history: Past trades and orders
        - all_markets: All tradable coins/pairs on Binance
        - fee_structure: Trading fees per symbol
        - candlestick_data: OHLCV data for technical analysis
        - order_book: Current buy/sell orders depth
        - ticker_24h: 24h statistics for symbols
        - technical_indicators: RSI, MACD, Bollinger Bands, etc.
    """)
    symbols: Optional[List[str]] = Field(None, description="Optional list of symbols to filter")
    timeframe: Optional[str] = Field(None, description="Timeframe for candlestick data: 1m, 5m, 15m, 1h, 4h, 1d, 1w")
    limit: Optional[int] = Field(100, description="Number of data points to return")


class MCPContextResponse(BaseModel):
    contexts: List[MCPContext]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MCPActionRequest(BaseModel):
    actions: List[MCPAction]
    auth_token: str = Field(..., description="Authorization token")
    trading_mode: Optional[Literal["paper", "live"]] = Field(
        default=None,
        description="Trading mode for this session: 'paper' (simulated) or 'live' (real money). AI should ask user before setting."
    )


class MCPActionResponse(BaseModel):
    results: List[ActionResult]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
