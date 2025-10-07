# Crypto MCP Trading Server

A Model Context Protocol (MCP)-compliant server for crypto trading via Binance.US, enabling LLM-driven trading with built-in risk management and paper trading support.

## Features

- ✅ **MCP Protocol Compliance**: Standard `/mcp/contexts` and `/mcp/actions` endpoints
- 🔐 **Secure Authentication**: Auto-generated 64-character token on startup
- 📊 **Complete Market Visibility**: AI can see ALL tradable coins on Binance
- 💹 **Comprehensive Market Data**: Real-time prices, order books, candlesticks, 24h tickers
- 📈 **Technical Analysis**: RSI, MACD, SMA, EMA, Bollinger Bands on all timeframes
- 💰 **Fee Structure Access**: See maker/taker fees for every trading pair
- 🤖 **Trade Execution**: Support for MARKET, LIMIT, STOP orders via Binance.US API
- 🛡️ **Optional Risk Management**: Set limits or let AI trade freely
- 📝 **Paper Trading**: Full mock trading mode for testing strategies without risk
- 💾 **Database Logging**: SQLite database for trade logs and context snapshots
- 📈 **Portfolio Tracking**: Real-time balance and position monitoring

## Architecture

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────┐
│             │  MCP    │                  │  REST   │             │
│  LLM Client │◄───────►│   MCP Server     │◄───────►│ Binance.US  │
│             │Protocol │  (FastAPI)       │   API   │   Exchange  │
└─────────────┘         └──────────────────┘         └─────────────┘
                               │
                               │ Logs
                               ▼
                        ┌─────────────┐
                        │   SQLite    │
                        │  Database   │
                        └─────────────┘
```

## Installation

### Prerequisites

- Python 3.8+
- Binance.US account with API keys (for live trading)
- pip package manager

### Option 1: Install from Source (Development)

1. **Clone or download the project**

```bash
git clone <repository-url>
cd "Crypto MCP"
```

2. **Install package in editable mode**

```bash
pip install -e .
```

Or install with development dependencies for testing:

```bash
pip install -e ".[dev]"
```

3. **Configure environment variables**

Copy the example environment file and edit it:

```bash
cp .env.example .env
```

Edit the `.env` file and replace placeholder values:

```bash
# REQUIRED: Add your Binance.US API keys
BINANCE_API_KEY=your_real_api_key_here
BINANCE_API_SECRET=your_real_api_secret_here

# Set trading mode (paper or live)
TRADING_MODE=paper

# OPTIONAL: Risk limits (omit for unlimited AI trading)
# MAX_TRADE_SIZE_USD=1000
# MAX_DAILY_LOSS_USD=500
# MAX_POSITION_SIZE_USD=5000
```

> 🔐 **No auth token needed!** A secure 64-character token is auto-generated on startup.

### Option 2: Install for Claude Desktop

1. **Install the package**

```bash
pip install binance-mcp
```

2. **Configure Claude Desktop**

Add to your Claude Desktop configuration file:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**Minimal Configuration (AI Asks Trading Mode):**
```json
{
  "mcpServers": {
    "crypto-trading": {
      "command": "binance-mcp",
      "env": {
        "BINANCE_API_KEY": "your_binance_api_key_here",
        "BINANCE_API_SECRET": "your_binance_api_secret_here"
      }
    }
  }
}
```

**With Daily Loss Limit (Safety Net for Live Trading):**
```json
{
  "mcpServers": {
    "crypto-trading": {
      "command": "binance-mcp",
      "env": {
        "BINANCE_API_KEY": "your_binance_api_key_here",
        "BINANCE_API_SECRET": "your_binance_api_secret_here",
        "MAX_DAILY_LOSS_USD": "500.0"
      }
    }
  }
}
```

> 🤖 **AI asks trading mode**: The AI will ask you "Do you want paper or live trading?" before each session
> 🔐 **Auth token auto-generated**: Secure 64-character token created on startup
> ✅ **Auto-detect balance**: Always enabled, no configuration needed

> 💡 **See [claude_desktop_config_examples.md](claude_desktop_config_examples.md) for more configuration examples**

3. **Restart Claude Desktop**

The MCP server will automatically start when Claude Desktop launches.

See [INSTALL.md](INSTALL.md) for detailed installation instructions.

## Usage

### Starting the Server

**If installed as package:**

```bash
binance-mcp
```

**If running from source:**

```bash
python -m crypto_mcp_server.server
```

The server will start on `http://localhost:8000`

### Running the Example Client

```bash
# Run trading workflow example
python llm_client_example.py

# Run monitoring loop
python llm_client_example.py 2
```

### API Endpoints

#### Health Check
```bash
GET /health
```

#### Get Contexts (Market Data, Account State, Trade History)
```bash
POST /mcp/contexts
Authorization: Bearer <your_token>

# Get market data for specific symbols
{
  "context_types": ["market_data"],
  "symbols": ["BTCUSD", "ETHUSD"]
}

# Discover ALL tradable coins
{
  "context_types": ["all_markets"]
}

# Get trading fees
{
  "context_types": ["fee_structure"],
  "symbols": ["BTCUSD", "ETHUSD"]  # Optional: all symbols if omitted
}

# Get candlestick data for technical analysis
{
  "context_types": ["candlestick_data"],
  "symbols": ["BTCUSD"],
  "timeframe": "1h",  # Optional: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w
  "limit": 100        # Optional: number of candles (default 100)
}

# Get order book depth
{
  "context_types": ["order_book"],
  "symbols": ["BTCUSD"],
  "limit": 100  # Optional: depth levels (default 100)
}

# Get 24h ticker statistics
{
  "context_types": ["ticker_24h"],
  "symbols": ["BTCUSD", "ETHUSD"]  # Optional: all tickers if omitted
}

# Get technical indicators
{
  "context_types": ["technical_indicators"],
  "symbols": ["BTCUSD"],
  "timeframe": "1h"  # Optional: default 1h
}

# Get multiple context types at once
{
  "context_types": ["market_data", "account_state", "technical_indicators"],
  "symbols": ["BTCUSD"],
  "timeframe": "1h"
}
```

#### Execute Actions (Trade Orders, Cancellations)
```bash
POST /mcp/actions
Authorization: Bearer <your_token>

{
  "actions": [
    {
      "action_id": "action_123",
      "action": {
        "action_type": "trade_order",
        "symbol": "BTCUSD",
        "side": "BUY",
        "order_type": "MARKET",
        "quantity": 0.01
      }
    }
  ],
  "auth_token": "<your_token>"
}
```

## MCP Protocol Schema

### Context Types

The AI has access to the following context types for complete market visibility:

1. **market_data**: Current market information for specific symbols
   - Real-time price, bid/ask spread
   - 24h volume, high, low
   - Price change and percentage

2. **all_markets**: Discover ALL tradable coins on Binance
   - List of every trading pair available
   - Base/quote assets for each pair
   - Trading status (TRADING, HALT, etc.)
   - Current price and 24h volume for all pairs
   - Margin/spot trading capabilities

3. **fee_structure**: Trading fees for all symbols
   - Maker fee percentage
   - Taker fee percentage
   - Per-symbol fee information

4. **candlestick_data**: OHLCV data for technical analysis
   - Open, High, Low, Close, Volume
   - Multiple timeframes: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w
   - Historical data up to 1000 candles
   - Quote volume and trade counts

5. **order_book**: Real-time order book depth
   - Bid orders (buy side)
   - Ask orders (sell side)
   - Price levels and quantities
   - Up to 5000 levels of depth

6. **ticker_24h**: 24-hour statistics for symbols
   - Price change and percentage
   - Weighted average price
   - Previous close, open, high, low
   - Current bid/ask prices
   - 24h volume and quote volume
   - Number of trades

7. **technical_indicators**: Calculated indicators for any symbol/timeframe
   - **RSI** (Relative Strength Index): Oversold/overbought signals
   - **MACD** (Moving Average Convergence Divergence): Trend momentum
   - **SMA** (Simple Moving Average): 20 and 50 period
   - **EMA** (Exponential Moving Average): 12 and 26 period
   - **Bollinger Bands**: Upper, middle, lower bands
   - Buy/Sell/Neutral signals for each indicator

8. **account_state**: Account balances and positions
   - Asset balances (free, locked, total)
   - Portfolio value in USD
   - Open positions with P&L

9. **trade_history**: Historical trades
   - Past orders, fills, commissions
   - Trade timestamps and prices

### Action Types

1. **trade_order**: Execute a trade
   - Required: symbol, side, quantity
   - Optional: price, stop_price, order_type

2. **cancel_order**: Cancel an existing order
   - Required: symbol, order_id

## Risk Management

The server includes **optional** risk controls - you decide what limits to set:

### Optional Limits (Can be omitted for AI full control)
- **Max Trade Size**: Limit per individual trade (omit for unlimited)
- **Max Position Size**: Maximum position value (omit for unlimited)
- **Daily Loss Limit**: Maximum loss allowed per day (omit for unlimited)
- **Circuit Breaker**: Only triggers if daily loss limit is set

### AI Trading Modes

**🤖 AI Full Control (No Limits):**
- Omit all `MAX_*` environment variables
- AI uses entire available balance
- No restrictions on trade size or frequency
- **Use with:** Paper trading or if you trust the AI completely

**⚖️ AI with Daily Loss Limit Only:**
- Set only `MAX_DAILY_LOSS_USD`
- AI trades freely until daily loss limit hit
- Circuit breaker stops trading for the day
- **Use with:** Live trading when you want safety net

**🛡️ Conservative Mode (All Limits):**
- Set all `MAX_TRADE_SIZE_USD`, `MAX_DAILY_LOSS_USD`, `MAX_POSITION_SIZE_USD`
- Maximum protection with strict controls
- **Use with:** Live trading for beginners

> See [claude_desktop_config_examples.md](claude_desktop_config_examples.md) for detailed configuration examples

## Paper Trading vs Live Trading

### Paper Trading (Default)
- No real money involved
- Mock execution engine
- Starting balance: $10,000 USD
- Perfect for testing strategies

### Live Trading
- Real orders on Binance.US
- Requires valid API keys
- Real money at risk
- Set `TRADING_MODE=live` in `.env`

**⚠️ WARNING**: Always test thoroughly in paper mode before switching to live!

## Database

The server maintains a SQLite database (`trading.db`) with:

- **trade_logs**: All executed trades
- **context_snapshots**: Historical context data
- **daily_pnl**: Daily profit/loss tracking

## Security

- API keys stored in environment variables (never committed)
- Token-based authentication for MCP endpoints
- Request validation and authorization
- No direct key access for LLM clients

## Development

### Project Structure

```
Crypto MCP/
├── crypto_mcp_server/          # Main package
│   ├── __init__.py            # Package init
│   ├── server.py              # Entry point
│   ├── mcp_server.py          # FastAPI server
│   ├── schemas.py             # Pydantic models
│   ├── binance_client.py      # Binance.US integration
│   ├── paper_trading.py       # Mock trading engine
│   ├── risk_manager.py        # Risk controls
│   ├── database.py            # SQLAlchemy models
│   └── config.py              # Configuration
├── tests/                     # Test suite
│   ├── conftest.py           # Test fixtures
│   ├── test_mcp_server.py    # API tests
│   ├── test_paper_trading.py # Trading engine tests
│   ├── test_risk_manager.py  # Risk tests
│   ├── test_database.py      # Database tests
│   ├── test_integration.py   # E2E tests
│   └── README.md             # Test documentation
├── setup.py                   # Package setup (legacy)
├── pyproject.toml            # Package configuration
├── pytest.ini                # Pytest configuration
├── MANIFEST.in               # Package manifest
├── requirements.txt          # Dependencies
├── .env.example              # Example environment
├── INSTALL.md                # Installation guide
├── claude_desktop_config.json # Claude Desktop config example
└── README.md                 # This file
```

### Adding New Features

1. **New Context Types**: Add to `schemas.py` and implement in `mcp_server.py`
2. **New Actions**: Define in `schemas.py`, implement handler in `mcp_server.py`
3. **Risk Rules**: Extend `risk_manager.py` validation logic
4. **Trading Strategies**: Implement in LLM client logic

## Testing

### Running Tests

The project includes a comprehensive test suite with 64+ tests covering:
- API endpoints and authentication
- Paper trading engine
- Risk management
- Database operations
- End-to-end workflows

**Run all tests:**

```bash
pytest
```

**Run with verbose output:**

```bash
pytest -v
```

**Run with coverage report:**

```bash
pytest --cov=crypto_mcp_server --cov-report=html
```

**Run specific test file:**

```bash
pytest tests/test_mcp_server.py
```

See [tests/README.md](tests/README.md) for detailed testing documentation.

### Manual Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test context retrieval
curl -X POST http://localhost:8000/mcp/contexts \
  -H "Authorization: Bearer mcp_secure_token_12345" \
  -H "Content-Type: application/json" \
  -d '{"context_types": ["market_data"], "symbols": ["BTCUSD"]}'
```

## Troubleshooting

### "Failed to initialize Binance client"
- Expected when using placeholder API keys
- Switch to live mode and add real keys, or continue with paper trading

### "Invalid authorization token"
- Ensure `MCP_AUTH_TOKEN` matches in `.env` and client
- Check Authorization header format: `Bearer <token>`

### "Circuit breaker triggered"
- Daily loss limit exceeded
- Reset by clearing `daily_pnl` table or waiting for next day
- Adjust `MAX_DAILY_LOSS_USD` in `.env`

### Connection errors
- Ensure server is running on correct port
- Check firewall settings
- Verify network connectivity to Binance.US (for live mode)

## License

MIT License - see LICENSE file for details

## Disclaimer

This software is for educational purposes. Trading cryptocurrencies involves significant risk. Always test thoroughly in paper trading mode before risking real capital. The authors are not responsible for any financial losses.

## Support

For issues or questions:
1. Check this README
2. Review logs in console output
3. Examine `trading.db` for trade history
4. Open an issue on GitHub (if applicable)

## What the AI Can See and Do

### Complete Market Visibility ✅

The AI has **full access** to all Binance market data:

- ✅ **Every tradable coin/pair** on Binance (use `all_markets` context)
- ✅ **Real-time prices** for all symbols
- ✅ **Trading fees** (maker/taker) for every pair
- ✅ **Order book depth** up to 5000 levels
- ✅ **Historical candlesticks** (OHLCV) on all timeframes
- ✅ **24h ticker statistics** (volume, price change, etc.)
- ✅ **Technical indicators** (RSI, MACD, SMA, EMA, Bollinger Bands)

### Timeframes Supported ⏰

The AI can analyze any symbol on these timeframes:
- `1m` - 1 minute
- `5m` - 5 minutes
- `15m` - 15 minutes
- `30m` - 30 minutes
- `1h` - 1 hour (default)
- `4h` - 4 hours
- `1d` - 1 day
- `1w` - 1 week

### Technical Indicators 📊

The AI can request calculated indicators for any symbol/timeframe:

1. **RSI (Relative Strength Index)**
   - 14-period RSI
   - Buy signal when < 30 (oversold)
   - Sell signal when > 70 (overbought)

2. **MACD (Moving Average Convergence Divergence)**
   - 12/26/9 period MACD
   - Buy signal when MACD > signal line
   - Sell signal when MACD < signal line

3. **SMA (Simple Moving Average)**
   - 20-period and 50-period SMA
   - Buy signal when SMA20 > SMA50 (golden cross)
   - Sell signal when SMA20 < SMA50 (death cross)

4. **EMA (Exponential Moving Average)**
   - 12-period and 26-period EMA
   - Used for MACD calculation

5. **Bollinger Bands**
   - 20-period, 2 standard deviations
   - Upper, middle (SMA20), and lower bands
   - Buy signal when price < lower band
   - Sell signal when price > upper band

### Trading Capabilities 💰

The AI can execute:
- **MARKET orders** - Instant execution at current price
- **LIMIT orders** - Execute at specific price or better
- **STOP orders** - Trigger at stop price
- **Order cancellations** - Cancel pending orders

### Discovery Workflow Example 🔍

```
1. AI: "What coins can I trade?"
   → Request context_type: "all_markets"
   → See all 300+ trading pairs

2. AI: "What are the fees for BTCUSD?"
   → Request context_type: "fee_structure" with symbol "BTCUSD"
   → See maker/taker fees (typically 0.1%)

3. AI: "Show me BTC price history"
   → Request context_type: "candlestick_data" with symbol "BTCUSD", timeframe "1h"
   → Get 100 hourly candles

4. AI: "What do the indicators say about BTC?"
   → Request context_type: "technical_indicators" with symbol "BTCUSD"
   → Get RSI, MACD, SMA, EMA, Bollinger Bands with buy/sell signals

5. AI: "Buy 0.01 BTC"
   → Execute action: trade_order with symbol "BTCUSD", side "BUY", quantity 0.01
   → Order executed
```

### AI Trading Modes 🤖

**Paper Trading (Safe)**
- All context data uses mock/realistic values
- No real API calls to Binance
- Perfect for testing and strategy development

**Live Trading (Real Money)**
- All context data from real Binance API
- Real-time prices, order books, fees
- Real money at risk - use with caution!

> 💡 **The AI will ask you**: "Do you want paper or live trading?" before each session

## Roadmap

- [ ] Margin/futures trading support for shorts
- [ ] WebSocket streaming for real-time market data
- [ ] Advanced order types (trailing stop, OCO)
- [ ] Multi-exchange support
- [ ] Backtesting framework
- [ ] Performance analytics dashboard
- [ ] Telegram/Discord notifications
- [ ] Strategy templates library
