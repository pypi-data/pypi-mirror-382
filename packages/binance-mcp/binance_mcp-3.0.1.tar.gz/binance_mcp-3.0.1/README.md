# Crypto MCP Trading Server

A Model Context Protocol (MCP) server for **LIVE cryptocurrency trading** via Binance.US, enabling AI-driven trading with real-time market data, comprehensive analytics, crypto news, and intelligent position management.

## Features

### Core Trading
- ✅ **MCP Protocol**: Standard stdio-based MCP communication
- 🔐 **Binance.US Integration**: Direct API connection for live trading
- 💹 **Advanced Order Types**: Market, Limit, Stop-Loss, OCO (One-Cancels-Other)
- 🎯 **Automatic TP/SL**: Set take-profit and stop-loss in one order
- 💰 **Smart Position Management**: Easy position closing with OCO cancellation
- 💾 **Local Database**: SQLite tracks all trades with full OCO linking

### Market Intelligence
- 📊 **Comprehensive Market Data**: Price, volume, liquidity metrics, volatility analysis
- 📈 **Technical Analysis**: RSI, MACD, SMA, EMA, Bollinger Bands with buy/sell signals
- 🕯️ **Advanced Candlestick Analysis**: Trend detection, support/resistance, pattern recognition
- 📰 **Crypto News**: CryptoPanic integration for market sentiment (24h delay)
- 📉 **Order Book Depth**: Real-time bid/ask analysis
- 🔍 **Symbol Details**: Trading rules, lot sizes, price filters

### Analysis & Intelligence
- 🧠 **AI-Powered Recommendations**: Comprehensive position analysis
- 📊 **Multi-Timeframe Analysis**: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w
- 🎯 **Technical Sentiment**: Aggregated buy/sell signals from all indicators
- 📈 **Trend Detection**: Identify UPTREND, DOWNTREND, SIDEWAYS markets
- 💧 **Liquidity Scoring**: Assess market depth and spread quality
- 🚀 **Live Trading Only**: All data from real Binance API (no paper mode)

## Architecture

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────┐
│             │  MCP    │                  │  REST   │             │
│  LLM Client │◄───────►│   MCP Server     │◄───────►│ Binance.US  │
│ (Claude/LM  │ stdio   │   (Python)       │   API   │   Exchange  │
│   Studio)   │Protocol │                  │         │             │
└─────────────┘         └──────────────────┘         └─────────────┘
                               │                  │
                               │                  │ News
                               │                  ▼
                               │           ┌──────────────┐
                               │           │ CryptoPanic  │
                               │           │     API      │
                               │           └──────────────┘
                               │
                               │ Logs All Trades
                               ▼
                        ┌─────────────┐
                        │   SQLite    │
                        │  Database   │
                        │ (trading.db)│
                        └─────────────┘
```

## Installation

### Prerequisites

- Python 3.8+
- Binance.US account with API keys
- pip package manager

### Quick Install

```bash
pip install binance-mcp
```

### Configuration

Add to your Claude Desktop or LM Studio configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "crypto-trading": {
      "command": "binance-mcp",
      "env": {
        "BINANCE_API_KEY": "your_api_key_here",
        "BINANCE_API_SECRET": "your_api_secret_here",
        "CRYPTOPANIC_API_KEY": "optional_news_api_key"
      }
    }
  }
}
```

**Note**: Get a free CryptoPanic API key at https://cryptopanic.com/developers/api/

## Available Tools

The AI has access to 14 powerful trading tools:

### Market Intelligence

**1. `get_market_data`** - Comprehensive market intelligence
   - Real-time price, volume, 24h stats
   - Liquidity metrics (bid/ask depth, spread analysis)
   - Volatility & volume trend analysis
   - Technical indicators (RSI, MACD, SMA, EMA, Bollinger Bands)
   - Automated buy/sell signals
   - Trading activity metrics

**2. `get_candlestick_data`** - Advanced timeframe analysis
   - OHLCV data for any timeframe (1m to 1w)
   - Trend detection (UPTREND, DOWNTREND, SIDEWAYS)
   - Support/resistance level calculation
   - Candle pattern analysis (BULLISH, BEARISH, DOJI)
   - Strength indicators (STRONG, MODERATE, WEAK)
   - Timeframe-specific technical indicators

**3. `get_crypto_news`** - Market sentiment & trending coins
   - Latest crypto news (24-hour delay)
   - Sentiment analysis
   - Trending cryptocurrencies
   - CryptoPanic integration

**4. `get_all_markets`** - All tradable cryptocurrency pairs

**5. `get_order_book`** - Live order book depth analysis

**6. `get_24h_ticker`** - 24-hour statistics for symbols

**7. `get_symbol_details`** - Trading rules, lot sizes, filters

**8. `get_fee_structure`** - Trading fees for symbols

### Account & Trading

**9. `get_account_balances`** - View your Binance account balances

**10. `place_order`** - Execute live trades
   - Market, Limit, Stop-Loss orders
   - Automatic OCO (One-Cancels-Other) for TP/SL
   - Supports both LONG and SHORT positions
   - Auto-formats quantity to exchange requirements

**11. `close_position`** - Smart position closing
   - Automatically sells full or partial balance
   - Cancels related OCO orders
   - Market execution for immediate fills

**12. `get_open_orders`** - See all active orders

**13. `cancel_order`** - Cancel open orders

**14. `analyze_position`** - AI analyzes when to sell
   - Current P&L calculation
   - Technical indicator analysis
   - Clear buy/hold/sell recommendations

### Trading History

**15. `get_trade_history`** - Recent trade history

## How It Works

### 1. Market Research with Intelligence
```
AI: "Analyze Bitcoin's market conditions"
→ Uses get_market_data("BTCUSDT")
→ Returns:
  💰 PRICE DATA:
    Current: $67,234.50 (+2.3%)
    24h Range: $65,100 - $68,500

  💧 LIQUIDITY:
    Liquidity Score: 87/100
    Spread: 0.02%

  🎯 TECHNICAL ANALYSIS:
    Overall Sentiment: BULLISH
    Buy Signals: 4 | Sell Signals: 1
    RSI: 58 [NEUTRAL]
    MACD: 120 [BUY]
    SMA_20 > SMA_50 [BUY]
```

### 2. Timeframe-Specific Analysis
```
AI: "Show me the 4-hour chart for Bitcoin"
→ Uses get_candlestick_data("BTCUSDT", timeframe="4h")
→ Returns:
  📈 TREND ANALYSIS:
    Trend: STRONG UPTREND
    Support: $66,100
    Resistance: $68,800

  🕯️ RECENT CANDLES:
    10/07 12:00 🟢 BULLISH (STRONG) | +1.8%
    10/07 08:00 🟢 BULLISH (MODERATE) | +0.5%
    10/07 04:00 🔴 BEARISH (WEAK) | -0.3%
```

### 3. Check Market News
```
AI: "What's the latest news on Bitcoin?"
→ Uses get_crypto_news(symbols=["BTC"])
→ Returns:
  📰 Crypto News (10 items):
  ⚠️ NOTE: News has 24-hour delay

  • Bitcoin ETF sees $200M inflow
    Source: CoinDesk | 🟢 Positive

  • Major institution adopts BTC
    Source: Bloomberg Crypto | 🟢 Positive
```

### 4. Place Trade with Auto TP/SL
```
AI: "Buy 0.01 BTC with take-profit at $70,000 and stop-loss at $65,000"
→ Uses place_order(
    symbol="BTCUSDT",
    side="BUY",
    order_type="MARKET",
    quantity=0.01,
    take_profit_price=70000,
    stop_loss_price=65000
  )
→ Returns:
  ✅ LIVE Order with OCO Exit Executed:
  ENTRY ORDER:
    Order ID: 12345
    BUY 0.01 BTCUSDT @ $67,234

  OCO EXIT ORDER:
    Take-Profit: $70,000
    Stop-Loss: $65,000
    Status: NEW
```

### 5. Close Position
```
AI: "Close my entire Bitcoin position"
→ Uses close_position(symbol="BTCUSDT")
→ Returns:
  ✅ Position Closed:
    Quantity Sold: 0.01 BTC
    Executed at: $68,500
    Status: FILLED
    OCO Order canceled.
```

## Order Types & Strategies

### Market Orders
- Execute immediately at current market price
- Best for quick entry/exit

### Limit Orders
- Execute at specific price or better
- Good for patient entries

### OCO Orders (One-Cancels-Other)
- Automatically place take-profit AND stop-loss
- When one executes, the other cancels
- Perfect for long and short positions

**Example LONG with OCO:**
```python
# Buy BTC, auto-exit at profit OR loss
place_order(
  symbol="BTCUSDT",
  side="BUY",
  order_type="MARKET",
  quantity=0.01,
  take_profit_price=70000,  # Exit at profit
  stop_loss_price=65000      # Exit at loss
)
```

**Example SHORT with OCO:**
```python
# Sell BTC short, auto-exit at profit OR loss
place_order(
  symbol="BTCUSDT",
  side="SELL",
  order_type="MARKET",
  quantity=0.01,
  take_profit_price=65000,   # Exit at profit (lower)
  stop_loss_price=70000       # Exit at loss (higher)
)
```

## Technical Indicators

### Supported Timeframes
- `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d`, `1w`

### Available Indicators

**RSI (Relative Strength Index)**
- 14-period RSI
- < 30: Oversold (BUY signal)
- > 70: Overbought (SELL signal)

**MACD (Moving Average Convergence Divergence)**
- 12/26/9 periods
- MACD > Signal: BUY
- MACD < Signal: SELL

**SMA (Simple Moving Average)**
- 20 and 50 periods
- SMA20 > SMA50: Golden Cross (BUY)
- SMA20 < SMA50: Death Cross (SELL)

**EMA (Exponential Moving Average)**
- 12 and 26 periods
- Used for MACD calculation

**Bollinger Bands**
- 20-period, 2 std dev
- Price < Lower Band: BUY
- Price > Upper Band: SELL

## Database Tracking

All trades are automatically logged to `trading.db` (SQLite):

### TradeLog Table
- Order ID, Symbol, Side, Type
- Quantity, Price, Fill Price
- Status, Timestamp
- **OCO Tracking**: Links entry/exit orders
- **TP/SL Prices**: Records target prices
- **Strategy Notes**: AI decision reasoning

### DailyPnL Table
- Daily profit/loss tracking
- Win/loss ratio
- Total volume
- Trade count

Each computer maintains its own local trade history with full OCO order linking.

## Position Analysis

The AI analyzes your positions and recommends when to sell based on:

### Technical Indicators
- **RSI** - Overbought (>70) suggests selling
- **MACD** - Bearish crossover suggests selling
- **Bollinger Bands** - Price above upper band suggests selling
- **Moving Averages** - Death cross suggests selling

### Profit/Loss Thresholds
- **>10% profit** - Consider taking profits
- **>5% loss** - Consider stop-loss
- **Multiple sell signals** - Strong recommendation to sell

### Recommendations Include
- Clear action: SELL, HOLD, or TAKE PROFITS
- Suggested take-profit levels
- Suggested stop-loss levels
- Current P&L calculation
- Technical indicator breakdown

## Security

- API keys stored in environment variables
- Never committed to version control
- MCP stdio protocol (no network exposure)
- Token-based authentication
- Request validation
- LOT_SIZE auto-formatting prevents order errors

## Example Conversation

```
User: "Find me a good crypto to buy right now"

AI: Let me analyze the market for you...
[Uses get_crypto_news() to check sentiment]
📰 Latest News: Bitcoin ETF inflows, bullish sentiment

[Uses get_all_markets() to see available coins]
[Uses get_market_data() for top coins with full analysis]

Market Intelligence Analysis:

BTCUSDT:
💰 Price: $67,234 (+2.3%)
💧 Liquidity: 87/100 (Excellent)
📈 Volatility: 3.2% (Moderate)
🎯 Sentiment: BULLISH (4 buy, 1 sell)

ETHUSD:
💰 Price: $3,456 (+4.1%)
💧 Liquidity: 82/100 (Good)
📈 Volatility: 4.8% (High)
🎯 Sentiment: STRONG BULLISH (5 buy, 0 sell)

Based on comprehensive analysis, Ethereum shows the strongest signals with 5/5 buy indicators and strong momentum. Would you like me to buy ETH with automatic take-profit and stop-loss?

User: "Yes, buy $1000 worth with 10% take-profit and 5% stop-loss"

AI: [Uses get_account_balances() to verify funds]
✅ Balance confirmed: $5,000 available

[Calculates: $1000 / $3456 = 0.289 ETH]

[Uses place_order() with OCO]
✅ Order Executed:

ENTRY: Bought 0.289 ETH @ $3,456 = $1,000
OCO EXIT SET:
  Take-Profit: $3,802 (+10%)
  Stop-Loss: $3,283 (-5%)

I'll monitor this position. The OCO order will automatically:
- Sell at $3,802 for 10% profit, OR
- Sell at $3,283 to limit loss to 5%

Use `analyze_position` anytime to check status!
```

## What's New in v3.0.0

### Major Features
- ✨ **Crypto News Integration** - CryptoPanic API for market sentiment
- 📊 **Enhanced Market Intelligence** - Comprehensive liquidity & volatility metrics
- 🕯️ **Advanced Candlestick Analysis** - Trend detection, support/resistance, patterns
- 🎯 **Smart Position Closing** - `close_position` tool with OCO cancellation
- 📈 **Consolidated Market Data** - All indicators in one comprehensive tool

### Improvements
- 🔧 **LOT_SIZE Auto-Formatting** - Prevents order rejection errors
- 💾 **Enhanced Database** - OCO tracking, TP/SL linking, strategy notes
- 🗑️ **Removed Friction** - Eliminated risk manager and paper trading mode

### Breaking Changes
- ❌ Risk management removed (trade freely)
- ❌ Paper trading removed (live-only)
- ✅ All risk decisions now AI-driven

## Development

### Project Structure

```
Crypto MCP/
├── crypto_mcp_server/
│   ├── server.py              # MCP server & tool handlers
│   ├── binance_client.py      # Binance.US + news integration
│   ├── database.py            # SQLAlchemy models with OCO tracking
│   ├── config.py              # Configuration
│   └── schemas.py             # Pydantic models
├── pyproject.toml             # Package configuration
└── README.md                  # This file
```

### Building from Source

```bash
# Clone repository
git clone https://github.com/yourusername/crypto-mcp.git
cd crypto-mcp

# Install in development mode
pip install -e .

# Build package
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

## Troubleshooting

**"Binance.US client failed to initialize"**
- Check API keys in configuration
- Ensure keys have trading permissions
- Verify API keys are for Binance.US (not Binance.com)

**"Filter failure: LOT_SIZE"**
- Fixed in v3.0.0! Quantities now auto-formatted
- Update to latest version: `pip install --upgrade binance-mcp`

**"Connection closed" error**
- Restart Claude Desktop or LM Studio
- Verify binance-mcp is installed: `pip show binance-mcp`
- Check configuration file path

**AI doesn't see tools**
- Restart client completely
- Verify MCP server is in config
- Check logs for server startup

**News not showing**
- Add `CRYPTOPANIC_API_KEY` to configuration
- Free key at https://cryptopanic.com/developers/api/
- Falls back to CoinGecko trending if no key

## License

MIT License

## Disclaimer

⚠️ **LIVE TRADING WITH REAL MONEY**

This software executes REAL trades on Binance.US with REAL money. Use at your own risk.

- Cryptocurrency trading is highly volatile
- You can lose your entire investment
- Past performance doesn't guarantee future results
- The authors are not responsible for financial losses
- News data has a 24-hour delay - not for time-sensitive decisions
- Always start with small amounts
- Never trade more than you can afford to lose

**This is not financial advice. Trade responsibly.**

## Support

For issues or questions:
1. Check this README
2. Review `trading.db` for trade history
3. Check server logs for errors
4. Verify Binance.US API status
5. Visit: https://pypi.org/project/binance-mcp/

## Links

- **PyPI**: https://pypi.org/project/binance-mcp/
- **Binance.US API**: https://docs.binance.us/
- **CryptoPanic API**: https://cryptopanic.com/developers/api/
- **MCP Protocol**: https://modelcontextprotocol.io/
