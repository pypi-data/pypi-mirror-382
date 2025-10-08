# Crypto MCP Trading Server

A Model Context Protocol (MCP) server for **LIVE cryptocurrency trading** via Binance.US, enabling AI-driven trading with real-time market data, technical analysis, and intelligent position management.

## Features

- ✅ **MCP Protocol**: Standard stdio-based MCP communication
- 🔐 **Binance.US Integration**: Direct API connection for live trading
- 📊 **Complete Market Data**: Real-time prices, order books, candlesticks, 24h tickers
- 📈 **Technical Analysis**: RSI, MACD, SMA, EMA, Bollinger Bands on all timeframes
- 💹 **Advanced Order Types**: Market, Limit, Stop-Loss, Take-Profit orders
- 🎯 **Position Analysis**: AI analyzes when to sell based on market conditions
- 💰 **Account Management**: Real-time balance checking before every trade
- 📋 **Order Management**: View open orders, cancel orders, track positions
- 🛡️ **Risk Management**: Optional trade size and loss limits
- 💾 **Local Database**: SQLite database tracks all trades on each computer
- 🚀 **Live Trading Only**: All data from real Binance API (no mock/paper mode)

## Architecture

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────┐
│             │  MCP    │                  │  REST   │             │
│  LLM Client │◄───────►│   MCP Server     │◄───────►│ Binance.US  │
│ (Claude/LM  │ stdio   │   (Python)       │   API   │   Exchange  │
│   Studio)   │Protocol │                  │         │             │
└─────────────┘         └──────────────────┘         └─────────────┘
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

### Setup

1. **Install the package**

```bash
pip install -e .
```

2. **Configure environment variables**

Create a `.env` file:

```bash
# REQUIRED: Your Binance.US API credentials
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here

# OPTIONAL: Risk limits (omit for unlimited trading)
# MAX_TRADE_SIZE_USD=1000
# MAX_DAILY_LOSS_USD=500
# MAX_POSITION_SIZE_USD=5000
```

### Claude Desktop Configuration

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "crypto-trading": {
      "command": "C:\\Users\\YOUR_USERNAME\\AppData\\Local\\Packages\\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\\LocalCache\\local-packages\\Python311\\Scripts\\binance-mcp.exe",
      "env": {
        "BINANCE_API_KEY": "your_api_key_here",
        "BINANCE_API_SECRET": "your_api_secret_here"
      }
    }
  }
}
```

### LM Studio Configuration

Same configuration works for LM Studio - just add to your LM Studio MCP settings.

## Available Tools

The AI has access to 13 powerful trading tools:

### Market Data Tools

1. **`get_market_data`** - Real-time price, volume, 24h change
2. **`get_all_markets`** - All tradable cryptocurrency pairs
3. **`get_candlestick_data`** - OHLCV data for technical analysis
4. **`get_order_book`** - Live order book depth
5. **`get_24h_ticker`** - 24-hour statistics
6. **`get_technical_indicators`** - RSI, MACD, SMA, EMA, Bollinger Bands
7. **`get_fee_structure`** - Trading fees for symbols

### Account & Trading Tools

8. **`get_account_balances`** - View your Binance account balances
9. **`get_open_orders`** - See all active orders
10. **`get_trade_history`** - Recent trade history
11. **`place_order`** - Execute live trades (Market, Limit, Stop-Loss, Take-Profit)
12. **`cancel_order`** - Cancel open orders
13. **`analyze_position`** - AI analyzes when to sell your position

## How It Works

### 1. Market Research
```
AI: "Show me the current price of Bitcoin"
→ Uses get_market_data("BTCUSD")
→ Returns: $67,234.50, +2.3%, Volume: $1.2B
```

### 2. Technical Analysis
```
AI: "What do the indicators say about BTC?"
→ Uses get_technical_indicators("BTCUSD", "1h")
→ Returns: RSI: 58 [NEUTRAL], MACD: 120 [BUY], SMA_20 > SMA_50 [BUY]
```

### 3. Account Check
```
AI: "Check my balance before trading"
→ Uses get_account_balances()
→ Returns: USD: 5,000.00, BTC: 0.05, ETH: 2.3
```

### 4. Place Trade
```
AI: "Buy 0.01 BTC at market price"
→ Uses place_order(symbol="BTCUSD", side="BUY", order_type="MARKET", quantity=0.01)
→ Order executed and logged to database
```

### 5. Position Analysis
```
AI: "When should I sell my BTC position?"
→ Uses analyze_position(symbol="BTCUSD", entry_price=65000, quantity=0.01)
→ Returns:
  P&L: +$22.34 (+3.4%)
  RSI: 72 [SELL]
  MACD: -50 [SELL]
  🔴 CONSIDER SELLING - Multiple indicators showing sell signals
  Suggested Take-Profit: $67,800
  Suggested Stop-Loss: $65,900
```

### 6. Set Stop-Loss
```
AI: "Set a stop-loss at $65,000"
→ Uses place_order(symbol="BTCUSD", side="SELL", order_type="STOP_LOSS", quantity=0.01, stop_price=65000)
→ Stop-loss order placed
```

## Order Types Supported

### Market Orders
- Execute immediately at current market price
- Best for quick entry/exit

### Limit Orders
- Execute at specific price or better
- Good for patient entries

### Stop-Loss Orders
- Automatically sell if price drops to stop price
- Protects against losses

### Stop-Loss Limit Orders
- Stop-loss with a limit price
- More control over execution price

### Take-Profit Orders
- Automatically sell when target price reached
- Locks in profits

### Take-Profit Limit Orders
- Take-profit with a limit price
- Ensures minimum profit level

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

## Risk Management

Optional risk controls (can be omitted for full AI control):

- **Max Trade Size**: Limit individual trade size
- **Max Daily Loss**: Circuit breaker stops trading after daily loss limit
- **Max Position Size**: Limit total position value

Set in `.env` file or omit for unlimited trading.

## Database

All trades are automatically logged to `trading.db` (SQLite):

- **Order ID** - Binance order reference
- **Symbol** - Trading pair
- **Side** - BUY or SELL
- **Type** - Order type (MARKET, LIMIT, etc.)
- **Quantity** - Amount traded
- **Price** - Execution price
- **Status** - Order status
- **Timestamp** - When trade occurred

Each computer maintains its own local trade history.

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

## Security

- API keys stored in environment variables
- Never committed to version control
- MCP stdio protocol (no network exposure)
- Token-based authentication
- Request validation

## Example Conversation

```
User: "Check my balance and find me a good coin to buy"

AI: Let me check your account balance first.
[Uses get_account_balances()]
Your balance: USD: $5,000.00

Now let me analyze some promising cryptocurrencies...
[Uses get_all_markets() to see available coins]
[Uses get_technical_indicators() for top coins]

Based on technical analysis:
- BTCUSD: RSI 45 [NEUTRAL], MACD [BUY], Price: $67,234
- ETHUSD: RSI 38 [BUY], MACD [BUY], Price: $3,456
- SOLUSD: RSI 52 [NEUTRAL], MACD [NEUTRAL], Price: $142

Ethereum (ETH) shows strong buy signals. Would you like me to:
1. Buy $1,000 worth of ETH?
2. Set a stop-loss at 5% below entry?

User: "Yes, buy ETH and set the stop-loss"

AI: [Uses place_order() for market buy]
✅ Bought 0.289 ETH at $3,456 = $1,000

[Uses place_order() for stop-loss]
✅ Stop-loss set at $3,283 (5% below entry)

I'll monitor this position and let you know when to sell based on market conditions.
```

## Development

### Project Structure

```
Crypto MCP/
├── crypto_mcp_server/
│   ├── server.py              # MCP server entry point
│   ├── binance_client.py      # Binance.US integration
│   ├── risk_manager.py        # Risk controls
│   ├── database.py            # SQLAlchemy models
│   ├── config.py              # Configuration
│   └── schemas.py             # Pydantic models
├── pyproject.toml             # Package configuration
├── .env.example               # Example environment
└── README.md                  # This file
```

## Troubleshooting

**"Binance.US client failed to initialize"**
- Check API keys in `.env` file
- Ensure keys have trading permissions
- Verify API keys are for Binance.US (not Binance.com)

**"Connection closed" error**
- Restart LM Studio or Claude Desktop
- Verify binance-mcp.exe path is correct
- Check Python is in PATH

**"Circuit breaker triggered"**
- Daily loss limit exceeded
- Wait until next day or adjust MAX_DAILY_LOSS_USD

**AI doesn't see tools**
- Restart LM Studio/Claude Desktop completely
- Verify MCP server is in config
- Check logs for server startup

## License

MIT License

## Disclaimer

⚠️ **LIVE TRADING WITH REAL MONEY**

This software executes REAL trades on Binance.US with REAL money. Use at your own risk.

- Cryptocurrency trading is highly volatile
- You can lose your entire investment
- Past performance doesn't guarantee future results
- The authors are not responsible for financial losses
- Always start with small amounts
- Never trade more than you can afford to lose

**This is not financial advice. Trade responsibly.**

## Support

For issues or questions:
1. Check this README
2. Review `trading.db` for trade history
3. Check server logs for errors
4. Verify Binance.US API status
