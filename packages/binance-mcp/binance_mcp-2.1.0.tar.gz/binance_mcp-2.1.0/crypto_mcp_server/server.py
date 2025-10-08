#!/usr/bin/env python
"""
MCP Server for Crypto Trading via Binance.US
Uses the MCP protocol for communication with Claude Desktop and LM Studio
"""

import asyncio
import logging
from typing import Any, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from crypto_mcp_server.config import settings
from crypto_mcp_server.binance_client import BinanceUSClient
from crypto_mcp_server.risk_manager import RiskManager
from crypto_mcp_server.schemas import OrderSide, OrderType

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize components
binance_client = BinanceUSClient()
risk_manager = RiskManager()

# Create MCP server
app = Server("binance-mcp")

logger.info("🚀 Binance MCP Server starting - LIVE TRADING MODE")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="get_market_data",
            description="Get current market data for a cryptocurrency symbol (price, volume, 24h change)",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Trading pair symbol (e.g., BTCUSD, ETHUSD)"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_account_balances",
            description="Get current account balances for all assets",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_all_markets",
            description="Get all tradable cryptocurrency pairs/markets on Binance",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_candlestick_data",
            description="Get OHLCV candlestick data for technical analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Trading pair symbol"
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "Timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w)",
                        "default": "1h"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of candlesticks to retrieve",
                        "default": 100
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_order_book",
            description="Get current order book depth (bids and asks)",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Trading pair symbol"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Depth limit",
                        "default": 100
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_24h_ticker",
            description="Get 24-hour ticker statistics for symbols",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbols": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of symbols (optional, gets all if not specified)"
                    }
                }
            }
        ),
        Tool(
            name="get_technical_indicators",
            description="Calculate technical indicators (RSI, MACD, SMA, EMA, Bollinger Bands)",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Trading pair symbol"
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "Timeframe for calculations",
                        "default": "1h"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="place_order",
            description="Place a LIVE trading order on Binance with automatic risk management. Supports: MARKET, LIMIT, STOP_LOSS orders. Can automatically set take-profit and stop-loss for both LONG and SHORT positions using OCO orders. ALWAYS show account balance BEFORE placing orders!",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Trading pair symbol (e.g., BTCUSDT, DOGEUSDT)"
                    },
                    "side": {
                        "type": "string",
                        "enum": ["BUY", "SELL"],
                        "description": "Order side - BUY to open long/close short, SELL to open short/close long"
                    },
                    "order_type": {
                        "type": "string",
                        "enum": ["MARKET", "LIMIT", "STOP_LOSS", "STOP_LOSS_LIMIT"],
                        "description": "Order type - use MARKET for instant execution, LIMIT for specific price"
                    },
                    "quantity": {
                        "type": "number",
                        "description": "Order quantity in base asset (e.g., 0.01 BTC, 100 DOGE)"
                    },
                    "price": {
                        "type": "number",
                        "description": "Limit price (required for LIMIT orders)"
                    },
                    "stop_price": {
                        "type": "number",
                        "description": "Stop trigger price (for STOP_LOSS orders)"
                    },
                    "take_profit_price": {
                        "type": "number",
                        "description": "Take-profit target price. When provided with stop_loss_price, automatically creates OCO exit order. For LONG: set higher than entry. For SHORT: set lower than entry."
                    },
                    "stop_loss_price": {
                        "type": "number",
                        "description": "Stop-loss protection price. When provided with take_profit_price, automatically creates OCO exit order. For LONG: set lower than entry. For SHORT: set higher than entry."
                    },
                    "stop_limit_price": {
                        "type": "number",
                        "description": "Stop-limit price (optional, defaults to stop_loss_price if not specified)"
                    }
                },
                "required": ["symbol", "side", "order_type", "quantity"]
            }
        ),
        Tool(
            name="get_open_orders",
            description="Get all open (active) orders for a symbol or all symbols",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Trading pair symbol (optional, gets all if not specified)"
                    }
                }
            }
        ),
        Tool(
            name="cancel_order",
            description="Cancel an open order",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Trading pair symbol"
                    },
                    "order_id": {
                        "type": "string",
                        "description": "Order ID to cancel"
                    }
                },
                "required": ["symbol", "order_id"]
            }
        ),
        Tool(
            name="analyze_position",
            description="Analyze current market conditions and provide sell/exit recommendations for a position based on technical indicators",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Trading pair symbol"
                    },
                    "entry_price": {
                        "type": "number",
                        "description": "Entry price of the position"
                    },
                    "quantity": {
                        "type": "number",
                        "description": "Position quantity"
                    }
                },
                "required": ["symbol", "entry_price", "quantity"]
            }
        ),
        Tool(
            name="get_trade_history",
            description="Get recent trade history",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Trading pair symbol (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of trades to retrieve",
                        "default": 50
                    }
                }
            }
        ),
        Tool(
            name="get_fee_structure",
            description="Get trading fee structure for symbols",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbols": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of symbols (optional)"
                    }
                }
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""

    try:
        if name == "get_market_data":
            symbol = arguments["symbol"]

            # ALWAYS use live Binance data for market queries
            market_data = await binance_client.get_market_data(symbol)
            result = f"Market Data for {symbol}:\n"
            result += f"Price: ${market_data.price:,.2f}\n"
            result += f"24h Change: {market_data.price_change_percent_24h:+.2f}%\n"
            result += f"24h Volume: ${market_data.volume_24h:,.2f}\n"
            result += f"24h High: ${market_data.high_24h:,.2f}\n"
            result += f"24h Low: ${market_data.low_24h:,.2f}\n"
            result += f"Bid: ${market_data.bid:,.2f}\n"
            result += f"Ask: ${market_data.ask:,.2f}"

            return [TextContent(type="text", text=result)]

        elif name == "get_account_balances":
            # Get live account balances from Binance
            balances = await binance_client.get_account_balances()

            result = "Account Balances:\n\n"
            for balance in balances:
                result += f"{balance.asset}: {balance.total:.8f} (Free: {balance.free:.8f}, Locked: {balance.locked:.8f})\n"

            return [TextContent(type="text", text=result)]

        elif name == "get_all_markets":
            # ALWAYS use live Binance data
            markets_ctx = await binance_client.get_all_markets()
            result = f"All Markets (Total: {markets_ctx.total_count}):\n\n"
            for market in markets_ctx.markets[:50]:  # Limit to first 50
                price_str = f"${market.price:,.2f}" if market.price else "N/A"
                result += f"{market.symbol} ({market.base_asset}/{market.quote_asset}): {price_str}\n"
            if markets_ctx.total_count > 50:
                result += f"\n... and {markets_ctx.total_count - 50} more markets"

            return [TextContent(type="text", text=result)]

        elif name == "get_candlestick_data":
            symbol = arguments["symbol"]
            timeframe = arguments.get("timeframe", "1h")
            limit = arguments.get("limit", 100)

            # ALWAYS use live Binance data
            candle_ctx = await binance_client.get_candlestick_data(symbol, timeframe, limit)
            result = f"Candlestick Data for {symbol} ({timeframe}, last {len(candle_ctx.candlesticks)} candles):\n\n"
            # Show last 10 candles
            for candle in candle_ctx.candlesticks[-10:]:
                result += f"{candle.open_time.strftime('%Y-%m-%d %H:%M')} | "
                result += f"O: {candle.open:.2f} H: {candle.high:.2f} L: {candle.low:.2f} C: {candle.close:.2f} V: {candle.volume:.2f}\n"

            return [TextContent(type="text", text=result)]

        elif name == "get_order_book":
            symbol = arguments["symbol"]
            limit = arguments.get("limit", 100)

            # ALWAYS use live Binance data
            order_book = await binance_client.get_order_book_depth(symbol, limit)
            result = f"Order Book for {symbol}:\n\n"
            result += "TOP BIDS:\n"
            for bid in order_book.bids[:10]:
                result += f"  ${bid.price:.2f} - {bid.quantity:.8f}\n"
            result += "\nTOP ASKS:\n"
            for ask in order_book.asks[:10]:
                result += f"  ${ask.price:.2f} - {ask.quantity:.8f}\n"

            return [TextContent(type="text", text=result)]

        elif name == "get_24h_ticker":
            symbols = arguments.get("symbols")

            # ALWAYS use live Binance data
            ticker_ctx = await binance_client.get_24h_tickers(symbols)
            result = "24h Ticker Statistics:\n\n"
            for ticker in ticker_ctx.tickers[:20]:  # Limit to 20
                result += f"{ticker.symbol}: ${ticker.last_price:,.2f} ({ticker.price_change_percent:+.2f}%) "
                result += f"Vol: {ticker.volume:,.2f}\n"

            return [TextContent(type="text", text=result)]

        elif name == "get_technical_indicators":
            symbol = arguments["symbol"]
            timeframe = arguments.get("timeframe", "1h")

            # ALWAYS use live Binance data
            indicators_ctx = await binance_client.calculate_technical_indicators(symbol, timeframe)
            result = f"Technical Indicators for {symbol} ({timeframe}):\n\n"
            for indicator in indicators_ctx.indicators:
                signal_str = f" [{indicator.signal}]" if indicator.signal else ""
                result += f"{indicator.name}: {indicator.value:.2f}{signal_str}\n"

            return [TextContent(type="text", text=result)]

        elif name == "place_order":
            symbol = arguments["symbol"]
            side = OrderSide[arguments["side"]]
            order_type = OrderType[arguments["order_type"]]
            quantity = float(arguments["quantity"])
            price = arguments.get("price")
            stop_price = arguments.get("stop_price")
            take_profit_price = arguments.get("take_profit_price")
            stop_loss_price = arguments.get("stop_loss_price")
            stop_limit_price = arguments.get("stop_limit_price")

            logger.info(f"🎯 Placing LIVE order on Binance: {side.value} {quantity} {symbol}")
            if take_profit_price and stop_loss_price:
                logger.info(f"   With auto TP/SL: TP=${take_profit_price:.4f} SL=${stop_loss_price:.4f}")

            # Check circuit breaker
            should_halt, halt_reason = await risk_manager.check_circuit_breaker()
            if should_halt:
                return [TextContent(type="text", text=f"❌ Trading halted: {halt_reason}")]

            # Get current price for risk validation
            current_price = await binance_client.get_current_price(symbol)

            # Get account balances BEFORE placing order
            balances = await binance_client.get_account_balances()
            portfolio_value = sum(b.total * current_price for b in balances)  # Simplified

            # Risk validation
            from crypto_mcp_server.schemas import TradeOrderAction
            action = TradeOrderAction(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
                stop_price=stop_price
            )

            valid, error = await risk_manager.validate_trade(action, current_price, portfolio_value)
            if not valid:
                return [TextContent(type="text", text=f"❌ Order rejected: {error}")]

            # Place LIVE order on Binance (with optional OCO)
            order_result = await binance_client.place_order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
                stop_price=stop_price,
                take_profit_price=take_profit_price,
                stop_loss_price=stop_loss_price,
                stop_limit_price=stop_limit_price
            )

            # Check if OCO was created
            is_oco = isinstance(order_result, dict) and 'oco_order' in order_result

            # Log to local database
            from crypto_mcp_server.database import SessionLocal, TradeLog, OrderSideDB, OrderTypeDB, OrderStatusDB
            db = SessionLocal()
            try:
                if is_oco:
                    # Log entry order
                    entry_order = order_result['entry_order']
                    trade_log = TradeLog(
                        order_id=str(entry_order.get("orderId")),
                        symbol=symbol,
                        side=OrderSideDB[side.value],
                        order_type=OrderTypeDB[order_type.value],
                        quantity=quantity,
                        price=price,
                        fill_price=float(entry_order.get("price", 0)) if entry_order.get("price") else None,
                        status=OrderStatusDB[entry_order.get("status", "NEW")],
                        trading_mode="live"
                    )
                    db.add(trade_log)
                else:
                    # Log single order
                    trade_log = TradeLog(
                        order_id=str(order_result.get("orderId")),
                        symbol=symbol,
                        side=OrderSideDB[side.value],
                        order_type=OrderTypeDB[order_type.value],
                        quantity=quantity,
                        price=price,
                        fill_price=float(order_result.get("price", 0)) if order_result.get("price") else None,
                        status=OrderStatusDB[order_result.get("status", "NEW")],
                        trading_mode="live"
                    )
                    db.add(trade_log)
                db.commit()
            except Exception as e:
                logger.error(f"Error logging trade to database: {e}")
                db.rollback()
            finally:
                db.close()

            # Format response
            if is_oco:
                entry_order = order_result['entry_order']
                oco_order = order_result['oco_order']
                result = f"✅ LIVE Order with OCO Exit Executed on Binance:\n\n"
                result += f"ENTRY ORDER:\n"
                result += f"  Order ID: {entry_order.get('orderId')}\n"
                result += f"  Status: {entry_order.get('status')}\n"
                result += f"  {side.value} {quantity} {symbol} @ ${current_price:,.4f}\n\n"
                result += f"OCO EXIT ORDER:\n"
                result += f"  OCO Order ID: {oco_order.get('orderListId')}\n"
                result += f"  Take-Profit: ${take_profit_price:,.4f}\n"
                result += f"  Stop-Loss: ${stop_loss_price:,.4f}\n"
                result += f"  Status: {oco_order.get('listOrderStatus')}"
            else:
                result = f"✅ LIVE Order Executed on Binance:\n"
                result += f"Order ID: {order_result.get('orderId')}\n"
                result += f"Status: {order_result.get('status')}\n"
                result += f"Symbol: {symbol}\n"
                result += f"Side: {side.value}\n"
                result += f"Quantity: {quantity}\n"
                result += f"Price: ${current_price:,.2f}"

            return [TextContent(type="text", text=result)]

        elif name == "get_trade_history":
            symbol = arguments.get("symbol")
            limit = arguments.get("limit", 50)

            # Get live trade history from Binance
            trades = await binance_client.get_recent_trades(symbol=symbol, limit=limit)

            result = "Trade History:\n\n"
            for trade in trades:
                result += f"{trade.timestamp.strftime('%Y-%m-%d %H:%M')} | "
                result += f"{trade.symbol} {trade.side.value} {trade.quantity:.8f} @ ${trade.price:.2f}\n"

            return [TextContent(type="text", text=result)]

        elif name == "get_fee_structure":
            symbols = arguments.get("symbols")

            # ALWAYS use live Binance data
            fee_ctx = await binance_client.get_fee_structure(symbols)
            result = "Trading Fees:\n\n"
            for fee_info in fee_ctx.fees[:20]:
                result += f"{fee_info.symbol}: Maker {fee_info.maker_fee*100:.3f}% / Taker {fee_info.taker_fee*100:.3f}%\n"

            return [TextContent(type="text", text=result)]

        elif name == "get_open_orders":
            symbol = arguments.get("symbol")

            # Get all open orders from Binance
            if symbol:
                # Get orders for specific symbol
                try:
                    orders = binance_client.client.get_open_orders(symbol=symbol)
                except Exception as e:
                    orders = []
            else:
                # Get all open orders
                try:
                    orders = binance_client.client.get_open_orders()
                except Exception as e:
                    orders = []

            if not orders:
                return [TextContent(type="text", text="No open orders found.")]

            result = f"Open Orders ({len(orders)}):\n\n"
            for order in orders:
                result += f"Order ID: {order['orderId']}\n"
                result += f"Symbol: {order['symbol']}\n"
                result += f"Side: {order['side']}\n"
                result += f"Type: {order['type']}\n"
                result += f"Price: ${float(order['price']):,.2f}\n"
                result += f"Quantity: {float(order['origQty']):.8f}\n"
                result += f"Filled: {float(order['executedQty']):.8f}\n"
                result += f"Status: {order['status']}\n"
                result += f"---\n"

            return [TextContent(type="text", text=result)]

        elif name == "cancel_order":
            symbol = arguments["symbol"]
            order_id = arguments["order_id"]

            logger.info(f"Canceling order {order_id} for {symbol}")

            # Cancel order on Binance
            result_data = await binance_client.cancel_order(symbol, order_id)

            result = f"✅ Order Canceled:\n"
            result += f"Order ID: {result_data.get('orderId')}\n"
            result += f"Symbol: {result_data.get('symbol')}\n"
            result += f"Status: {result_data.get('status')}"

            return [TextContent(type="text", text=result)]

        elif name == "analyze_position":
            symbol = arguments["symbol"]
            entry_price = float(arguments["entry_price"])
            quantity = float(arguments["quantity"])

            # Get current market data
            market_data = await binance_client.get_market_data(symbol)
            current_price = market_data.price

            # Calculate P&L
            pnl = (current_price - entry_price) * quantity
            pnl_percent = ((current_price - entry_price) / entry_price) * 100

            # Get technical indicators
            indicators_ctx = await binance_client.calculate_technical_indicators(symbol, "1h")

            # Analyze indicators for sell signals
            sell_signals = []
            hold_signals = []

            for indicator in indicators_ctx.indicators:
                if indicator.signal == "SELL":
                    sell_signals.append(f"{indicator.name} showing SELL signal")
                elif indicator.signal == "BUY" or indicator.signal == "NEUTRAL":
                    hold_signals.append(f"{indicator.name}: {indicator.signal}")

            # Build recommendation
            result = f"Position Analysis for {symbol}:\n\n"
            result += f"Entry Price: ${entry_price:,.2f}\n"
            result += f"Current Price: ${current_price:,.2f}\n"
            result += f"Quantity: {quantity:.8f}\n"
            result += f"P&L: ${pnl:,.2f} ({pnl_percent:+.2f}%)\n\n"

            result += "Technical Indicators:\n"
            for indicator in indicators_ctx.indicators:
                signal_str = f" [{indicator.signal}]" if indicator.signal else ""
                result += f"  {indicator.name}: {indicator.value:.2f}{signal_str}\n"

            result += "\n📊 Recommendation:\n"
            if len(sell_signals) >= 2:
                result += "🔴 CONSIDER SELLING - Multiple indicators showing sell signals\n"
                result += f"Sell signals: {', '.join(sell_signals)}\n"
                # Suggest take-profit level
                take_profit = current_price * 1.02  # 2% above current
                stop_loss = current_price * 0.98    # 2% below current
                result += f"\nSuggested Take-Profit: ${take_profit:,.2f}\n"
                result += f"Suggested Stop-Loss: ${stop_loss:,.2f}"
            elif pnl_percent > 10:
                result += "🟡 CONSIDER TAKING PROFITS - Position up >10%\n"
                result += f"Consider selling partial position to lock in gains"
            elif pnl_percent < -5:
                result += "🟠 CONSIDER STOP-LOSS - Position down >5%\n"
                stop_loss = current_price * 0.98
                result += f"Suggested Stop-Loss: ${stop_loss:,.2f}"
            else:
                result += "🟢 HOLD - No strong sell signals detected\n"
                result += "Monitor position and set stop-loss if not already set"

            return [TextContent(type="text", text=result)]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def async_main():
    """Async main entry point for MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def main():
    """Synchronous entry point for CLI"""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
