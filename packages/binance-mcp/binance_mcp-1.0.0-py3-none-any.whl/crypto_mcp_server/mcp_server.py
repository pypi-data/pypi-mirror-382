from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import json

from crypto_mcp_server.config import settings
from crypto_mcp_server.schemas import (
    MCPContextRequest, MCPContextResponse, MCPActionRequest, MCPActionResponse,
    MCPContext, MCPContextMetadata, ActionResult, TradeExecutionResult,
    MarketDataContext, AccountStateContext, TradeHistoryContext,
    TradeOrderAction, CancelOrderAction, OrderStatus, OrderSide,
    AllMarketsContext, FeeStructureContext, CandlestickContext, OrderBookContext,
    Ticker24hContext, TechnicalIndicatorsContext, CoinInfo, FeeInfo, Candlestick,
    OrderBookLevel, Ticker24h, TechnicalIndicator
)
from crypto_mcp_server.binance_client import BinanceUSClient
from crypto_mcp_server.paper_trading import PaperTradingEngine
from crypto_mcp_server.risk_manager import RiskManager
from crypto_mcp_server.database import TradeLog, ContextSnapshot, SessionLocal, OrderSideDB, OrderTypeDB, OrderStatusDB

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Crypto MCP Trading Server",
    description="Model Context Protocol server for crypto trading via Binance.US",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
binance_client = BinanceUSClient()
paper_engine = PaperTradingEngine()
risk_manager = RiskManager()

# Log the auto-generated auth token on startup
logger.info("=" * 80)
logger.info("🔐 MCP SERVER AUTHENTICATION TOKEN")
logger.info("=" * 80)
logger.info(f"Auth Token: {settings.mcp_auth_token}")
logger.info("=" * 80)
logger.info("⚠️  IMPORTANT: Save this token to authenticate with the MCP server!")
logger.info("=" * 80)


def verify_auth_token(authorization: Optional[str] = Header(None)) -> bool:
    """Verify MCP authorization token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    # Extract token (support "Bearer <token>" format)
    token = authorization.replace("Bearer ", "").strip()

    if token != settings.mcp_auth_token:
        raise HTTPException(status_code=403, detail="Invalid authorization token")

    return True


@app.get("/")
async def root():
    """Root endpoint"""
    risk_info = {
        "max_trade_size_usd": settings.max_trade_size_usd or "unlimited",
        "max_daily_loss_usd": settings.max_daily_loss_usd or "unlimited",
        "max_position_size_usd": settings.max_position_size_usd or "unlimited"
    }

    return {
        "service": "Crypto MCP Trading Server",
        "version": "1.0.0",
        "status": "running",
        "trading_mode": settings.trading_mode,
        "risk_limits": risk_info,
        "auto_detect_balance": settings.auto_detect_balance
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    connectivity = binance_client.test_connectivity() if settings.trading_mode == "live" else True

    return {
        "status": "healthy",
        "trading_mode": settings.trading_mode,
        "binance_connectivity": connectivity,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/mcp/contexts", response_model=MCPContextResponse)
async def get_contexts(
    request: MCPContextRequest,
    authorized: bool = Depends(verify_auth_token)
):
    """
    MCP endpoint to retrieve contexts (market data, account state, trade history)
    """
    contexts = []

    try:
        for context_type in request.context_types:
            if context_type == "market_data":
                # Get market data for requested symbols
                if not request.symbols:
                    raise HTTPException(status_code=400, detail="Symbols required for market_data context")

                for symbol in request.symbols:
                    if settings.trading_mode == "live":
                        market_data = await binance_client.get_market_data(symbol)
                    else:
                        # Mock data for paper trading
                        market_data = MarketDataContext(
                            symbol=symbol,
                            price=50000.0,
                            bid=49990.0,
                            ask=50010.0,
                            volume_24h=1000000.0,
                            high_24h=51000.0,
                            low_24h=49000.0,
                            price_change_24h=500.0,
                            price_change_percent_24h=1.0,
                            metadata=MCPContextMetadata(
                                namespace="paper.market_data",
                                timestamp=datetime.utcnow()
                            )
                        )

                    contexts.append(MCPContext(
                        context_type="market_data",
                        data=market_data.model_dump(),
                        metadata=market_data.metadata
                    ))

                    # Store snapshot
                    await store_context_snapshot("market_data", market_data.model_dump())

            elif context_type == "account_state":
                # Get account state
                if settings.trading_mode == "live":
                    balances = await binance_client.get_account_balances()
                    # Calculate positions and portfolio value
                    portfolio_value = sum(b.total * 1.0 for b in balances)  # Simplified
                else:
                    balances = await paper_engine.get_all_balances()
                    # Get current prices for portfolio calculation
                    prices = {"BTCUSD": 50000.0}  # Mock
                    portfolio_value = await paper_engine.get_portfolio_value(prices)
                    positions = await paper_engine.get_positions(prices)

                account_state = AccountStateContext(
                    balances=balances,
                    positions=positions if settings.trading_mode == "paper" else [],
                    total_portfolio_value_usd=portfolio_value,
                    metadata=MCPContextMetadata(
                        namespace=f"{settings.trading_mode}.account_state",
                        timestamp=datetime.utcnow()
                    )
                )

                contexts.append(MCPContext(
                    context_type="account_state",
                    data=account_state.model_dump(),
                    metadata=account_state.metadata
                ))

                await store_context_snapshot("account_state", account_state.model_dump())

            elif context_type == "trade_history":
                # Get trade history
                if settings.trading_mode == "live":
                    symbol = request.symbols[0] if request.symbols else None
                    trades = await binance_client.get_recent_trades(symbol=symbol)
                else:
                    trades = await paper_engine.get_recent_trades()

                trade_history = TradeHistoryContext(
                    trades=trades,
                    metadata=MCPContextMetadata(
                        namespace=f"{settings.trading_mode}.trade_history",
                        timestamp=datetime.utcnow()
                    )
                )

                contexts.append(MCPContext(
                    context_type="trade_history",
                    data=trade_history.model_dump(),
                    metadata=trade_history.metadata
                ))

                await store_context_snapshot("trade_history", trade_history.model_dump())

            elif context_type == "all_markets":
                # Get all tradable coins/pairs
                if settings.trading_mode == "live":
                    all_markets = await binance_client.get_all_markets()
                else:
                    # Mock data for paper trading
                    all_markets = AllMarketsContext(
                        markets=[
                            CoinInfo(
                                symbol="BTCUSD",
                                base_asset="BTC",
                                quote_asset="USD",
                                status="TRADING",
                                price=50000.0,
                                volume_24h=1000000.0,
                                is_spot_trading_allowed=True
                            ),
                            CoinInfo(
                                symbol="ETHUSD",
                                base_asset="ETH",
                                quote_asset="USD",
                                status="TRADING",
                                price=3000.0,
                                volume_24h=500000.0,
                                is_spot_trading_allowed=True
                            )
                        ],
                        total_count=2,
                        metadata=MCPContextMetadata(
                            namespace="paper.all_markets",
                            timestamp=datetime.utcnow()
                        )
                    )

                contexts.append(MCPContext(
                    context_type="all_markets",
                    data=all_markets.model_dump(),
                    metadata=all_markets.metadata
                ))

                await store_context_snapshot("all_markets", all_markets.model_dump())

            elif context_type == "fee_structure":
                # Get trading fees
                if settings.trading_mode == "live":
                    fee_structure = await binance_client.get_fee_structure(request.symbols)
                else:
                    # Mock fee data
                    symbols = request.symbols or ["BTCUSD", "ETHUSD"]
                    fee_structure = FeeStructureContext(
                        fees=[
                            FeeInfo(symbol=sym, maker_fee=0.001, taker_fee=0.001)
                            for sym in symbols
                        ],
                        metadata=MCPContextMetadata(
                            namespace="paper.fee_structure",
                            timestamp=datetime.utcnow()
                        )
                    )

                contexts.append(MCPContext(
                    context_type="fee_structure",
                    data=fee_structure.model_dump(),
                    metadata=fee_structure.metadata
                ))

                await store_context_snapshot("fee_structure", fee_structure.model_dump())

            elif context_type == "candlestick_data":
                # Get OHLCV candlestick data
                if not request.symbols:
                    raise HTTPException(status_code=400, detail="Symbols required for candlestick_data context")

                for symbol in request.symbols:
                    timeframe = request.timeframe or "1h"
                    limit = request.limit or 100

                    if settings.trading_mode == "live":
                        candlestick_data = await binance_client.get_candlestick_data(symbol, timeframe, limit)
                    else:
                        # Mock candlestick data
                        base_price = 50000.0
                        candlesticks = []
                        for i in range(limit):
                            candlesticks.append(Candlestick(
                                open_time=datetime.utcnow(),
                                open=base_price + (i * 10),
                                high=base_price + (i * 10) + 100,
                                low=base_price + (i * 10) - 100,
                                close=base_price + (i * 10) + 50,
                                volume=1000.0,
                                close_time=datetime.utcnow(),
                                quote_volume=50000000.0,
                                trades_count=1000
                            ))

                        candlestick_data = CandlestickContext(
                            symbol=symbol,
                            timeframe=timeframe,
                            candlesticks=candlesticks,
                            metadata=MCPContextMetadata(
                                namespace="paper.candlestick_data",
                                timestamp=datetime.utcnow()
                            )
                        )

                    contexts.append(MCPContext(
                        context_type="candlestick_data",
                        data=candlestick_data.model_dump(),
                        metadata=candlestick_data.metadata
                    ))

                    await store_context_snapshot("candlestick_data", candlestick_data.model_dump())

            elif context_type == "order_book":
                # Get order book depth
                if not request.symbols:
                    raise HTTPException(status_code=400, detail="Symbols required for order_book context")

                for symbol in request.symbols:
                    limit = request.limit or 100

                    if settings.trading_mode == "live":
                        order_book = await binance_client.get_order_book_depth(symbol, limit)
                    else:
                        # Mock order book
                        base_price = 50000.0
                        order_book = OrderBookContext(
                            symbol=symbol,
                            bids=[
                                OrderBookLevel(price=base_price - (i * 10), quantity=0.5 + (i * 0.1))
                                for i in range(1, min(limit, 20))
                            ],
                            asks=[
                                OrderBookLevel(price=base_price + (i * 10), quantity=0.5 + (i * 0.1))
                                for i in range(1, min(limit, 20))
                            ],
                            metadata=MCPContextMetadata(
                                namespace="paper.order_book",
                                timestamp=datetime.utcnow()
                            )
                        )

                    contexts.append(MCPContext(
                        context_type="order_book",
                        data=order_book.model_dump(),
                        metadata=order_book.metadata
                    ))

                    await store_context_snapshot("order_book", order_book.model_dump())

            elif context_type == "ticker_24h":
                # Get 24h ticker statistics
                if settings.trading_mode == "live":
                    ticker_24h = await binance_client.get_24h_tickers(request.symbols)
                else:
                    # Mock ticker data
                    symbols = request.symbols or ["BTCUSD", "ETHUSD"]
                    ticker_24h = Ticker24hContext(
                        tickers=[
                            Ticker24h(
                                symbol=sym,
                                price_change=500.0,
                                price_change_percent=1.0,
                                weighted_avg_price=50000.0,
                                prev_close_price=49500.0,
                                last_price=50000.0,
                                bid_price=49990.0,
                                ask_price=50010.0,
                                open_price=49500.0,
                                high_price=51000.0,
                                low_price=49000.0,
                                volume=1000000.0,
                                quote_volume=50000000000.0,
                                open_time=datetime.utcnow(),
                                close_time=datetime.utcnow(),
                                trade_count=100000
                            )
                            for sym in symbols
                        ],
                        metadata=MCPContextMetadata(
                            namespace="paper.ticker_24h",
                            timestamp=datetime.utcnow()
                        )
                    )

                contexts.append(MCPContext(
                    context_type="ticker_24h",
                    data=ticker_24h.model_dump(),
                    metadata=ticker_24h.metadata
                ))

                await store_context_snapshot("ticker_24h", ticker_24h.model_dump())

            elif context_type == "technical_indicators":
                # Get technical indicators
                if not request.symbols:
                    raise HTTPException(status_code=400, detail="Symbols required for technical_indicators context")

                for symbol in request.symbols:
                    timeframe = request.timeframe or "1h"

                    if settings.trading_mode == "live":
                        indicators = await binance_client.calculate_technical_indicators(symbol, timeframe)
                    else:
                        # Mock technical indicators
                        indicators = TechnicalIndicatorsContext(
                            symbol=symbol,
                            timeframe=timeframe,
                            indicators=[
                                TechnicalIndicator(name="RSI", value=55.0, signal="NEUTRAL", timestamp=datetime.utcnow()),
                                TechnicalIndicator(name="SMA_20", value=50000.0, signal="BUY", timestamp=datetime.utcnow()),
                                TechnicalIndicator(name="SMA_50", value=49500.0, signal=None, timestamp=datetime.utcnow()),
                                TechnicalIndicator(name="EMA_12", value=50100.0, signal=None, timestamp=datetime.utcnow()),
                                TechnicalIndicator(name="EMA_26", value=49900.0, signal=None, timestamp=datetime.utcnow()),
                                TechnicalIndicator(name="MACD", value=200.0, signal="BUY", timestamp=datetime.utcnow()),
                                TechnicalIndicator(name="BB_UPPER", value=51000.0, signal=None, timestamp=datetime.utcnow()),
                                TechnicalIndicator(name="BB_MIDDLE", value=50000.0, signal="NEUTRAL", timestamp=datetime.utcnow()),
                                TechnicalIndicator(name="BB_LOWER", value=49000.0, signal=None, timestamp=datetime.utcnow()),
                            ],
                            metadata=MCPContextMetadata(
                                namespace="paper.technical_indicators",
                                timestamp=datetime.utcnow()
                            )
                        )

                    contexts.append(MCPContext(
                        context_type="technical_indicators",
                        data=indicators.model_dump(),
                        metadata=indicators.metadata
                    ))

                    await store_context_snapshot("technical_indicators", indicators.model_dump())

        return MCPContextResponse(contexts=contexts)

    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Error retrieving contexts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/actions", response_model=MCPActionResponse)
async def execute_actions(
    request: MCPActionRequest,
    authorized: bool = Depends(verify_auth_token)
):
    """
    MCP endpoint to execute actions (trade orders, cancellations)
    Trading mode can be specified per request - AI should ask user which mode to use
    """
    # Verify auth token from request body as well
    if request.auth_token != settings.mcp_auth_token:
        raise HTTPException(status_code=403, detail="Invalid auth token in request")

    # Use trading mode from request, fallback to config default (paper for safety)
    trading_mode = request.trading_mode or settings.trading_mode
    logger.info(f"🎯 Trading session starting in {trading_mode.upper()} mode")

    # Check circuit breaker
    should_halt, halt_reason = await risk_manager.check_circuit_breaker()
    if should_halt:
        logger.error(f"Trading halted: {halt_reason}")
        raise HTTPException(status_code=403, detail=halt_reason)

    results = []

    for mcp_action in request.actions:
        try:
            action = mcp_action.action

            if isinstance(action, TradeOrderAction):
                result = await execute_trade_order(action, trading_mode)
                results.append(ActionResult(
                    action_id=mcp_action.action_id,
                    success=result.get("status") in ["FILLED", "NEW"],
                    message=f"Order {result.get('status')}",
                    data=result
                ))

            elif isinstance(action, CancelOrderAction):
                result = await cancel_order(action, trading_mode)
                results.append(ActionResult(
                    action_id=mcp_action.action_id,
                    success=True,
                    message="Order canceled",
                    data=result
                ))

        except Exception as e:
            logger.error(f"Error executing action {mcp_action.action_id}: {e}")
            results.append(ActionResult(
                action_id=mcp_action.action_id,
                success=False,
                message="Execution failed",
                error=str(e)
            ))

    return MCPActionResponse(results=results)


async def execute_trade_order(action: TradeOrderAction, trading_mode: str) -> Dict:
    """Execute a trade order using specified trading mode"""

    # Validate order parameters
    valid, error = risk_manager.validate_order_parameters(action)
    if not valid:
        raise ValueError(error)

    # Get current price based on trading mode
    if trading_mode == "live":
        current_price = await binance_client.get_current_price(action.symbol)
    else:
        current_price = 50000.0  # Mock price for paper trading

    # Get portfolio value for risk check
    if trading_mode == "paper":
        prices = {action.symbol: current_price}
        portfolio_value = await paper_engine.get_portfolio_value(prices)
    else:
        portfolio_value = 10000.0  # Simplified

    # Risk validation
    valid, error = await risk_manager.validate_trade(action, current_price, portfolio_value)
    if not valid:
        raise ValueError(error)

    # Execute order based on trading mode
    if trading_mode == "live":
        result = await binance_client.place_order(
            symbol=action.symbol,
            side=action.side,
            order_type=action.order_type,
            quantity=action.quantity,
            price=action.price,
            stop_price=action.stop_price,
            time_in_force=action.time_in_force
        )
    else:
        result = await paper_engine.place_order(
            symbol=action.symbol,
            side=action.side,
            order_type=action.order_type,
            quantity=action.quantity,
            price=action.price,
            current_price=current_price
        )

    # Log trade to database with trading mode
    await log_trade(action, result, trading_mode)

    # Update daily P&L (simplified - would need better calculation)
    if result.get("status") == "FILLED":
        # Calculate P&L (simplified)
        pnl = 0.0  # Would need proper calculation based on entry/exit
        await risk_manager.update_daily_pnl(pnl)

    return result


async def cancel_order(action: CancelOrderAction, trading_mode: str) -> Dict:
    """Cancel an order using specified trading mode"""
    if trading_mode == "live":
        result = await binance_client.cancel_order(action.symbol, action.order_id)
    else:
        result = await paper_engine.cancel_order(action.order_id)

    return result


async def log_trade(action: TradeOrderAction, result: Dict, trading_mode: str):
    """Log trade to database with trading mode"""
    db = SessionLocal()
    try:
        trade_log = TradeLog(
            order_id=str(result.get("orderId")),
            symbol=action.symbol,
            side=OrderSideDB[action.side.value],
            order_type=OrderTypeDB[action.order_type.value],
            quantity=action.quantity,
            price=action.price,
            fill_price=float(result.get("price", 0)) if result.get("price") else None,
            status=OrderStatusDB[result.get("status", "NEW")],
            trading_mode=trading_mode
        )
        db.add(trade_log)
        db.commit()
        logger.info(f"Trade logged: {trade_log.order_id} ({trading_mode} mode)")
    except Exception as e:
        logger.error(f"Error logging trade: {e}")
        db.rollback()
    finally:
        db.close()


async def store_context_snapshot(context_type: str, data: Dict):
    """Store context snapshot to database"""
    db = SessionLocal()
    try:
        snapshot = ContextSnapshot(
            context_type=context_type,
            data=json.dumps(data)
        )
        db.add(snapshot)
        db.commit()
    except Exception as e:
        logger.error(f"Error storing context snapshot: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.mcp_server_host,
        port=settings.mcp_server_port,
        log_level=settings.log_level.lower()
    )
