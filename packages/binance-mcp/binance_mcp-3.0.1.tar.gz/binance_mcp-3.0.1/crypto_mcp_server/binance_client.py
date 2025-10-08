from binance.client import Client
from binance.exceptions import BinanceAPIException
from typing import Dict, List, Optional
from crypto_mcp_server.config import settings
from crypto_mcp_server.schemas import (
    MarketDataContext, Balance, Position, Trade,
    OrderSide, OrderType, OrderStatus, MCPContextMetadata,
    CoinInfo, AllMarketsContext, FeeInfo, FeeStructureContext,
    Candlestick, CandlestickContext, OrderBookLevel, OrderBookContext,
    Ticker24h, Ticker24hContext, TechnicalIndicator, TechnicalIndicatorsContext
)
import logging
from datetime import datetime
import aiohttp
import asyncio

logger = logging.getLogger(__name__)


class BinanceUSClient:
    def __init__(self):
        self.api_key = settings.binance_api_key
        self.api_secret = settings.binance_api_secret

        # Initialize Binance.US client
        try:
            self.client = Client(
                self.api_key,
                self.api_secret,
                tld='us'  # Binance.US specific
            )
            logger.info("Binance.US client initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Binance client (placeholder keys expected): {e}")
            self.client = None

    async def get_market_data(self, symbol: str) -> MarketDataContext:
        """Fetch current market data for a symbol"""
        try:
            # Get ticker data
            ticker = self.client.get_ticker(symbol=symbol)

            # Get order book for bid/ask
            depth = self.client.get_order_book(symbol=symbol, limit=5)

            return MarketDataContext(
                symbol=symbol,
                price=float(ticker['lastPrice']),
                bid=float(depth['bids'][0][0]) if depth['bids'] else float(ticker['lastPrice']),
                ask=float(depth['asks'][0][0]) if depth['asks'] else float(ticker['lastPrice']),
                volume_24h=float(ticker['volume']),
                high_24h=float(ticker['highPrice']),
                low_24h=float(ticker['lowPrice']),
                price_change_24h=float(ticker['priceChange']),
                price_change_percent_24h=float(ticker['priceChangePercent']),
                metadata=MCPContextMetadata(
                    namespace="binance.market_data",
                    timestamp=datetime.utcnow()
                )
            )
        except Exception as e:
            logger.error(f"Error fetching market data for {symbol}: {e}")
            raise

    async def get_account_balances(self) -> List[Balance]:
        """Fetch account balances"""
        try:
            account = self.client.get_account()
            balances = []

            for balance in account['balances']:
                free = float(balance['free'])
                locked = float(balance['locked'])
                total = free + locked

                # Only include non-zero balances
                if total > 0:
                    balances.append(Balance(
                        asset=balance['asset'],
                        free=free,
                        locked=locked,
                        total=total
                    ))

            return balances
        except Exception as e:
            logger.error(f"Error fetching account balances: {e}")
            raise

    async def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            raise

    def _format_quantity(self, symbol: str, quantity: float) -> str:
        """Format quantity according to symbol's LOT_SIZE filter"""
        try:
            info = self.client.get_symbol_info(symbol)

            # Extract filters
            lot_size_filter = None
            min_notional_filter = None

            for filter_item in info['filters']:
                if filter_item['filterType'] == 'LOT_SIZE':
                    lot_size_filter = filter_item
                elif filter_item['filterType'] == 'MIN_NOTIONAL':
                    min_notional_filter = filter_item

            if not lot_size_filter:
                logger.warning(f"No LOT_SIZE filter found for {symbol}, using quantity as-is")
                return f"{quantity:.8f}".rstrip('0').rstrip('.')

            step_size = float(lot_size_filter['stepSize'])
            min_qty = float(lot_size_filter['minQty'])
            max_qty = float(lot_size_filter['maxQty'])

            # Calculate precision from step_size
            step_str = f"{step_size:.8f}".rstrip('0')
            if '.' in step_str:
                precision = len(step_str.split('.')[-1])
            else:
                precision = 0

            # Round down to step_size precision
            formatted_qty = quantity - (quantity % step_size)
            formatted_qty = round(formatted_qty, precision)

            # Validate bounds
            if formatted_qty < min_qty:
                raise ValueError(f"Quantity {formatted_qty} below minimum {min_qty} for {symbol}")
            if formatted_qty > max_qty:
                raise ValueError(f"Quantity {formatted_qty} above maximum {max_qty} for {symbol}")

            # Format as string to avoid scientific notation
            qty_str = f"{formatted_qty:.{precision}f}".rstrip('0').rstrip('.')

            # Validate MIN_NOTIONAL if filter exists
            if min_notional_filter:
                min_notional = float(min_notional_filter.get('minNotional', 0))
                # Get current price to check notional value
                ticker = self.client.get_symbol_ticker(symbol=symbol)
                current_price = float(ticker['price'])
                notional_value = formatted_qty * current_price

                if notional_value < min_notional:
                    raise ValueError(
                        f"Order value ${notional_value:.2f} below minimum ${min_notional:.2f} for {symbol}. "
                        f"Increase quantity or trade a different amount."
                    )

            return qty_str

        except Exception as e:
            logger.error(f"Error formatting quantity for {symbol}: {e}")
            raise

    async def place_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        take_profit_price: Optional[float] = None,
        stop_loss_price: Optional[float] = None,
        stop_limit_price: Optional[float] = None,
        time_in_force: str = "GTC"
    ) -> Dict:
        """
        Place an order on Binance.US with optional stop-loss and take-profit.

        This unified method handles:
        - Market orders (instant execution)
        - Limit orders (execute at specific price)
        - Stop-loss orders (risk management)
        - OCO orders (automatic stop-loss + take-profit for longs/shorts)

        Args:
            symbol: Trading pair (e.g., "BTCUSDT")
            side: BUY or SELL
            order_type: MARKET, LIMIT, STOP_LOSS, or STOP_LOSS_LIMIT
            quantity: Amount to trade
            price: Limit price (required for LIMIT orders)
            stop_price: Stop trigger price (for stop orders)
            take_profit_price: Take-profit price (creates OCO if stop_loss_price also provided)
            stop_loss_price: Stop-loss price (creates OCO if take_profit_price also provided)
            stop_limit_price: Stop limit price (for STOP_LOSS_LIMIT orders)
            time_in_force: GTC (default), IOC, or FOK

        Returns:
            Order result with order ID(s)

        Examples:
            # Market order (instant buy/sell)
            await place_order(symbol="BTCUSDT", side=OrderSide.BUY,
                            order_type=OrderType.MARKET, quantity=0.01)

            # Limit order (buy at specific price)
            await place_order(symbol="BTCUSDT", side=OrderSide.BUY,
                            order_type=OrderType.LIMIT, quantity=0.01, price=45000)

            # Long position with auto TP/SL (buy entry with OCO exit)
            await place_order(symbol="BTCUSDT", side=OrderSide.BUY,
                            order_type=OrderType.MARKET, quantity=0.01,
                            take_profit_price=50000, stop_loss_price=44000)

            # Short position with auto TP/SL (sell entry with OCO exit)
            await place_order(symbol="BTCUSDT", side=OrderSide.SELL,
                            order_type=OrderType.MARKET, quantity=0.01,
                            take_profit_price=44000, stop_loss_price=50000)
        """
        try:
            # Format quantity according to LOT_SIZE filter
            formatted_quantity = self._format_quantity(symbol, quantity)

            # If both TP and SL provided, create entry order + OCO exit
            if take_profit_price is not None and stop_loss_price is not None:
                # Place entry order first
                entry_params = {
                    'symbol': symbol,
                    'side': side.value,
                    'type': order_type.value,
                    'quantity': formatted_quantity
                }

                if order_type == OrderType.LIMIT:
                    if price is None:
                        raise ValueError("Price required for LIMIT orders")
                    entry_params['price'] = price
                    entry_params['timeInForce'] = time_in_force

                entry_result = self.client.create_order(**entry_params)
                logger.info(f"Entry order placed: {entry_result}")

                # Determine OCO side (opposite of entry)
                oco_side = OrderSide.SELL if side == OrderSide.BUY else OrderSide.BUY

                # Create OCO exit order
                oco_params = {
                    'symbol': symbol,
                    'side': oco_side.value,
                    'quantity': formatted_quantity,
                    'price': take_profit_price,
                    'stopPrice': stop_loss_price,
                    'stopLimitPrice': stop_limit_price or stop_loss_price,
                    'stopLimitTimeInForce': time_in_force
                }

                oco_result = self.client.create_oco_order(**oco_params)
                logger.info(f"OCO exit order placed: {oco_result}")

                return {
                    'entry_order': entry_result,
                    'oco_order': oco_result,
                    'strategy': 'entry_with_oco_exit'
                }

            # Standard single order (no OCO)
            params = {
                'symbol': symbol,
                'side': side.value,
                'type': order_type.value,
                'quantity': formatted_quantity
            }

            if order_type == OrderType.LIMIT:
                if price is None:
                    raise ValueError("Price required for LIMIT orders")
                params['price'] = price
                params['timeInForce'] = time_in_force

            if order_type in [OrderType.STOP_LOSS, OrderType.STOP_LOSS_LIMIT]:
                if stop_price is None:
                    raise ValueError("Stop price required for stop orders")
                params['stopPrice'] = stop_price
                if order_type == OrderType.STOP_LOSS_LIMIT:
                    params['price'] = price
                    params['timeInForce'] = time_in_force

            # Execute single order
            order_result = self.client.create_order(**params)
            logger.info(f"Order placed: {order_result}")
            return order_result

        except BinanceAPIException as e:
            logger.error(f"Binance API error placing order: {e}")
            raise
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            raise

    async def cancel_order(self, symbol: str, order_id: str) -> Dict:
        """Cancel an existing order"""
        try:
            result = self.client.cancel_order(symbol=symbol, orderId=order_id)
            logger.info(f"Order canceled: {result}")
            return result
        except Exception as e:
            logger.error(f"Error canceling order {order_id}: {e}")
            raise

    async def get_order_status(self, symbol: str, order_id: str) -> Dict:
        """Get order status"""
        try:
            return self.client.get_order(symbol=symbol, orderId=order_id)
        except Exception as e:
            logger.error(f"Error fetching order status: {e}")
            raise

    async def get_recent_trades(self, symbol: Optional[str] = None, limit: int = 50) -> List[Trade]:
        """Get recent trade history"""
        try:
            if symbol:
                trades_data = self.client.get_my_trades(symbol=symbol, limit=limit)
            else:
                # Get trades for all symbols (not directly supported, need to iterate)
                # For now, return empty if no symbol specified
                trades_data = []

            trades = []
            for trade in trades_data:
                trades.append(Trade(
                    id=str(trade['id']),
                    symbol=trade['symbol'],
                    side=OrderSide.BUY if trade['isBuyer'] else OrderSide.SELL,
                    order_type=OrderType.MARKET,  # Simplified
                    quantity=float(trade['qty']),
                    price=float(trade['price']),
                    fill_price=float(trade['price']),
                    status=OrderStatus.FILLED,
                    timestamp=datetime.fromtimestamp(trade['time'] / 1000),
                    commission=float(trade['commission']),
                    commission_asset=trade['commissionAsset']
                ))

            return trades
        except Exception as e:
            logger.error(f"Error fetching trade history: {e}")
            raise

    def test_connectivity(self) -> bool:
        """Test API connectivity"""
        try:
            if self.client is None:
                return False
            self.client.ping()
            return True
        except Exception as e:
            logger.error(f"Connectivity test failed: {e}")
            return False

    async def get_all_markets(self) -> AllMarketsContext:
        """Get all tradable coins/pairs on Binance"""
        try:
            # Get exchange info with all trading pairs
            exchange_info = self.client.get_exchange_info()

            # Get all 24h ticker data for current prices
            tickers = self.client.get_ticker()
            ticker_map = {t['symbol']: t for t in tickers}

            markets = []
            for symbol_info in exchange_info['symbols']:
                symbol = symbol_info['symbol']
                ticker = ticker_map.get(symbol, {})

                markets.append(CoinInfo(
                    symbol=symbol,
                    base_asset=symbol_info['baseAsset'],
                    quote_asset=symbol_info['quoteAsset'],
                    status=symbol_info['status'],
                    price=float(ticker.get('lastPrice', 0)) if ticker else None,
                    volume_24h=float(ticker.get('volume', 0)) if ticker else None,
                    is_margin_trading_allowed=symbol_info.get('isMarginTradingAllowed', False),
                    is_spot_trading_allowed=symbol_info.get('isSpotTradingAllowed', True)
                ))

            return AllMarketsContext(
                markets=markets,
                total_count=len(markets),
                metadata=MCPContextMetadata(
                    namespace="binance.all_markets",
                    timestamp=datetime.utcnow()
                )
            )
        except Exception as e:
            logger.error(f"Error fetching all markets: {e}")
            raise

    async def get_fee_structure(self, symbols: Optional[List[str]] = None) -> FeeStructureContext:
        """Get trading fee structure for symbols"""
        try:
            # Get trade fee information
            fees_data = self.client.get_trade_fee()

            fees = []
            for fee_info in fees_data['tradeFee']:
                symbol = fee_info['symbol']

                # Filter by symbols if provided
                if symbols and symbol not in symbols:
                    continue

                fees.append(FeeInfo(
                    symbol=symbol,
                    maker_fee=float(fee_info.get('maker', 0)),
                    taker_fee=float(fee_info.get('taker', 0))
                ))

            return FeeStructureContext(
                fees=fees,
                metadata=MCPContextMetadata(
                    namespace="binance.fee_structure",
                    timestamp=datetime.utcnow()
                )
            )
        except Exception as e:
            logger.error(f"Error fetching fee structure: {e}")
            raise

    async def get_candlestick_data(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 100
    ) -> CandlestickContext:
        """Get OHLCV candlestick data for technical analysis"""
        try:
            # Map common timeframes to Binance intervals
            interval_map = {
                "1m": Client.KLINE_INTERVAL_1MINUTE,
                "5m": Client.KLINE_INTERVAL_5MINUTE,
                "15m": Client.KLINE_INTERVAL_15MINUTE,
                "30m": Client.KLINE_INTERVAL_30MINUTE,
                "1h": Client.KLINE_INTERVAL_1HOUR,
                "4h": Client.KLINE_INTERVAL_4HOUR,
                "1d": Client.KLINE_INTERVAL_1DAY,
                "1w": Client.KLINE_INTERVAL_1WEEK,
            }

            interval = interval_map.get(timeframe, Client.KLINE_INTERVAL_1HOUR)
            klines = self.client.get_klines(symbol=symbol, interval=interval, limit=limit)

            candlesticks = []
            for kline in klines:
                candlesticks.append(Candlestick(
                    open_time=datetime.fromtimestamp(kline[0] / 1000),
                    open=float(kline[1]),
                    high=float(kline[2]),
                    low=float(kline[3]),
                    close=float(kline[4]),
                    volume=float(kline[5]),
                    close_time=datetime.fromtimestamp(kline[6] / 1000),
                    quote_volume=float(kline[7]),
                    trades_count=int(kline[8])
                ))

            return CandlestickContext(
                symbol=symbol,
                timeframe=timeframe,
                candlesticks=candlesticks,
                metadata=MCPContextMetadata(
                    namespace="binance.candlestick_data",
                    timestamp=datetime.utcnow()
                )
            )
        except Exception as e:
            logger.error(f"Error fetching candlestick data for {symbol}: {e}")
            raise

    async def get_order_book_depth(self, symbol: str, limit: int = 100) -> OrderBookContext:
        """Get current order book depth"""
        try:
            depth = self.client.get_order_book(symbol=symbol, limit=limit)

            bids = [OrderBookLevel(price=float(b[0]), quantity=float(b[1])) for b in depth['bids']]
            asks = [OrderBookLevel(price=float(a[0]), quantity=float(a[1])) for a in depth['asks']]

            return OrderBookContext(
                symbol=symbol,
                bids=bids,
                asks=asks,
                metadata=MCPContextMetadata(
                    namespace="binance.order_book",
                    timestamp=datetime.utcnow()
                )
            )
        except Exception as e:
            logger.error(f"Error fetching order book for {symbol}: {e}")
            raise

    async def get_24h_tickers(self, symbols: Optional[List[str]] = None) -> Ticker24hContext:
        """Get 24-hour ticker statistics for symbols"""
        try:
            if symbols:
                # Get tickers for specific symbols
                tickers_data = []
                for symbol in symbols:
                    ticker = self.client.get_ticker(symbol=symbol)
                    tickers_data.append(ticker)
            else:
                # Get all tickers
                tickers_data = self.client.get_ticker()

            tickers = []
            for ticker in tickers_data:
                tickers.append(Ticker24h(
                    symbol=ticker['symbol'],
                    price_change=float(ticker['priceChange']),
                    price_change_percent=float(ticker['priceChangePercent']),
                    weighted_avg_price=float(ticker['weightedAvgPrice']),
                    prev_close_price=float(ticker['prevClosePrice']),
                    last_price=float(ticker['lastPrice']),
                    bid_price=float(ticker['bidPrice']),
                    ask_price=float(ticker['askPrice']),
                    open_price=float(ticker['openPrice']),
                    high_price=float(ticker['highPrice']),
                    low_price=float(ticker['lowPrice']),
                    volume=float(ticker['volume']),
                    quote_volume=float(ticker['quoteVolume']),
                    open_time=datetime.fromtimestamp(ticker['openTime'] / 1000),
                    close_time=datetime.fromtimestamp(ticker['closeTime'] / 1000),
                    first_trade_id=ticker.get('firstId'),
                    last_trade_id=ticker.get('lastId'),
                    trade_count=int(ticker['count'])
                ))

            return Ticker24hContext(
                tickers=tickers,
                metadata=MCPContextMetadata(
                    namespace="binance.ticker_24h",
                    timestamp=datetime.utcnow()
                )
            )
        except Exception as e:
            logger.error(f"Error fetching 24h tickers: {e}")
            raise

    async def calculate_technical_indicators(
        self,
        symbol: str,
        timeframe: str = "1h"
    ) -> TechnicalIndicatorsContext:
        """Calculate technical indicators (RSI, MACD, SMA, EMA, Bollinger Bands)"""
        try:
            # Get candlestick data for calculations
            candlestick_ctx = await self.get_candlestick_data(symbol, timeframe, limit=200)
            closes = [c.close for c in candlestick_ctx.candlesticks]

            if len(closes) < 50:
                raise ValueError("Insufficient data for technical indicators")

            indicators = []

            # RSI (14 period)
            rsi = self._calculate_rsi(closes, period=14)
            rsi_signal = "BUY" if rsi < 30 else "SELL" if rsi > 70 else "NEUTRAL"
            indicators.append(TechnicalIndicator(
                name="RSI",
                value=rsi,
                signal=rsi_signal,
                timestamp=datetime.utcnow()
            ))

            # SMA (Simple Moving Average - 20, 50)
            sma_20 = sum(closes[-20:]) / 20
            sma_50 = sum(closes[-50:]) / 50
            sma_signal = "BUY" if sma_20 > sma_50 else "SELL"
            indicators.append(TechnicalIndicator(
                name="SMA_20",
                value=sma_20,
                signal=sma_signal,
                timestamp=datetime.utcnow()
            ))
            indicators.append(TechnicalIndicator(
                name="SMA_50",
                value=sma_50,
                signal=None,
                timestamp=datetime.utcnow()
            ))

            # EMA (Exponential Moving Average - 12, 26)
            ema_12 = self._calculate_ema(closes, period=12)
            ema_26 = self._calculate_ema(closes, period=26)
            indicators.append(TechnicalIndicator(
                name="EMA_12",
                value=ema_12,
                signal=None,
                timestamp=datetime.utcnow()
            ))
            indicators.append(TechnicalIndicator(
                name="EMA_26",
                value=ema_26,
                signal=None,
                timestamp=datetime.utcnow()
            ))

            # MACD
            macd = ema_12 - ema_26
            macd_signal_line = self._calculate_ema([macd], period=9)
            macd_signal = "BUY" if macd > macd_signal_line else "SELL"
            indicators.append(TechnicalIndicator(
                name="MACD",
                value=macd,
                signal=macd_signal,
                timestamp=datetime.utcnow()
            ))

            # Bollinger Bands (20 period, 2 std dev)
            bb_middle = sma_20
            std_dev = (sum((x - bb_middle) ** 2 for x in closes[-20:]) / 20) ** 0.5
            bb_upper = bb_middle + (2 * std_dev)
            bb_lower = bb_middle - (2 * std_dev)
            current_price = closes[-1]
            bb_signal = "SELL" if current_price > bb_upper else "BUY" if current_price < bb_lower else "NEUTRAL"

            indicators.append(TechnicalIndicator(
                name="BB_UPPER",
                value=bb_upper,
                signal=None,
                timestamp=datetime.utcnow()
            ))
            indicators.append(TechnicalIndicator(
                name="BB_MIDDLE",
                value=bb_middle,
                signal=bb_signal,
                timestamp=datetime.utcnow()
            ))
            indicators.append(TechnicalIndicator(
                name="BB_LOWER",
                value=bb_lower,
                signal=None,
                timestamp=datetime.utcnow()
            ))

            return TechnicalIndicatorsContext(
                symbol=symbol,
                timeframe=timeframe,
                indicators=indicators,
                metadata=MCPContextMetadata(
                    namespace="binance.technical_indicators",
                    timestamp=datetime.utcnow()
                )
            )
        except Exception as e:
            logger.error(f"Error calculating technical indicators for {symbol}: {e}")
            raise

    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return 50.0  # Neutral if insufficient data

        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return sum(prices) / len(prices)  # Fallback to SMA

        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period  # Start with SMA

        for price in prices[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))

        return ema

    async def get_crypto_news(self, symbols: Optional[List[str]] = None, limit: int = 20) -> Dict:
        """
        Fetch crypto news from multiple sources.
        Supports CryptoPanic API (if key provided) and free alternatives.
        """
        news_items = []

        # Try CryptoPanic API first (best for crypto-specific news)
        if settings.cryptopanic_api_key:
            try:
                async with aiohttp.ClientSession() as session:
                    # Build currency filter
                    currencies = ','.join(symbols) if symbols else 'BTC,ETH'
                    url = f"https://cryptopanic.com/api/v1/posts/"
                    params = {
                        'auth_token': settings.cryptopanic_api_key,
                        'currencies': currencies,
                        'kind': 'news',
                        'filter': 'important'
                    }
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            for post in data.get('results', [])[:limit]:
                                news_items.append({
                                    'title': post.get('title'),
                                    'url': post.get('url'),
                                    'source': post.get('source', {}).get('title', 'Unknown'),
                                    'published_at': post.get('published_at'),
                                    'sentiment': post.get('votes', {}).get('positive', 0) - post.get('votes', {}).get('negative', 0),
                                    'currencies': [c['code'] for c in post.get('currencies', [])]
                                })
            except Exception as e:
                logger.warning(f"CryptoPanic API error: {e}")

        # Fallback: Use free CoinGecko trending coins as "news"
        if not news_items:
            try:
                async with aiohttp.ClientSession() as session:
                    url = "https://api.coingecko.com/api/v3/search/trending"
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            for coin in data.get('coins', [])[:10]:
                                item = coin.get('item', {})
                                news_items.append({
                                    'title': f"🔥 Trending: {item.get('name')} ({item.get('symbol', '').upper()})",
                                    'url': f"https://www.coingecko.com/en/coins/{item.get('id')}",
                                    'source': 'CoinGecko Trending',
                                    'published_at': datetime.utcnow().isoformat(),
                                    'sentiment': item.get('market_cap_rank', 0),
                                    'currencies': [item.get('symbol', '').upper()],
                                    'market_cap_rank': item.get('market_cap_rank')
                                })
            except Exception as e:
                logger.warning(f"CoinGecko trending error: {e}")

        return {
            'news': news_items,
            'total_count': len(news_items),
            'timestamp': datetime.utcnow()
        }

    async def get_enhanced_market_data(self, symbol: str) -> Dict:
        """
        Get comprehensive market data with additional intelligence metrics.
        Includes: price, volume, liquidity, volatility, market depth analysis.
        """
        try:
            # Get basic market data
            basic_data = await self.get_market_data(symbol)

            # Get 24h ticker for additional metrics
            ticker = self.client.get_ticker(symbol=symbol)

            # Get order book for liquidity analysis
            order_book = await self.get_order_book_depth(symbol, limit=100)

            # Calculate liquidity metrics
            total_bid_volume = sum(bid.quantity for bid in order_book.bids[:20])
            total_ask_volume = sum(ask.quantity for ask in order_book.asks[:20])
            bid_ask_spread = order_book.asks[0].price - order_book.bids[0].price
            spread_percentage = (bid_ask_spread / order_book.bids[0].price) * 100

            # Get recent candles for volatility
            candles = await self.get_candlestick_data(symbol, timeframe="1h", limit=24)
            prices = [c.close for c in candles.candlesticks]
            avg_price = sum(prices) / len(prices)
            volatility = (max(prices) - min(prices)) / avg_price * 100

            # Calculate volume trend
            volumes = [c.volume for c in candles.candlesticks]
            avg_volume = sum(volumes) / len(volumes)
            current_volume = volumes[-1]
            volume_trend = ((current_volume - avg_volume) / avg_volume) * 100

            # Get technical indicators
            indicators = await self.calculate_technical_indicators(symbol, timeframe="1h")

            # Determine market sentiment from indicators
            buy_signals = sum(1 for ind in indicators.indicators if ind.signal == "BUY")
            sell_signals = sum(1 for ind in indicators.indicators if ind.signal == "SELL")
            sentiment = "BULLISH" if buy_signals > sell_signals else "BEARISH" if sell_signals > buy_signals else "NEUTRAL"

            return {
                'symbol': symbol,
                'basic_data': {
                    'price': basic_data.price,
                    'bid': basic_data.bid,
                    'ask': basic_data.ask,
                    'volume_24h': basic_data.volume_24h,
                    'high_24h': basic_data.high_24h,
                    'low_24h': basic_data.low_24h,
                    'price_change_24h': basic_data.price_change_24h,
                    'price_change_percent_24h': basic_data.price_change_percent_24h
                },
                'liquidity_metrics': {
                    'bid_volume_top20': total_bid_volume,
                    'ask_volume_top20': total_ask_volume,
                    'bid_ask_spread': bid_ask_spread,
                    'spread_percentage': spread_percentage,
                    'liquidity_score': min(100, (total_bid_volume + total_ask_volume) / 1000)  # Simplified score
                },
                'volatility_metrics': {
                    'volatility_24h_percent': volatility,
                    'volume_trend_percent': volume_trend,
                    'avg_volume_24h': avg_volume,
                    'current_volume': current_volume
                },
                'technical_sentiment': {
                    'sentiment': sentiment,
                    'buy_signals': buy_signals,
                    'sell_signals': sell_signals,
                    'indicators': [{'name': ind.name, 'value': ind.value, 'signal': ind.signal} for ind in indicators.indicators]
                },
                'trading_activity': {
                    'trade_count_24h': int(ticker.get('count', 0)),
                    'quote_volume_24h': float(ticker.get('quoteVolume', 0))
                },
                'timestamp': datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error getting enhanced market data for {symbol}: {e}")
            raise

    async def get_symbol_info_detailed(self, symbol: str) -> Dict:
        """
        Get detailed exchange information for a specific symbol.
        Includes all trading rules, filters, and constraints.
        """
        try:
            info = self.client.get_symbol_info(symbol)

            # Parse all filters into readable format
            filters_parsed = {}
            for filter_item in info.get('filters', []):
                filter_type = filter_item['filterType']
                filters_parsed[filter_type] = {k: v for k, v in filter_item.items() if k != 'filterType'}

            return {
                'symbol': info['symbol'],
                'status': info['status'],
                'base_asset': info['baseAsset'],
                'quote_asset': info['quoteAsset'],
                'order_types': info.get('orderTypes', []),
                'is_spot_trading_allowed': info.get('isSpotTradingAllowed', True),
                'is_margin_trading_allowed': info.get('isMarginTradingAllowed', False),
                'permissions': info.get('permissions', []),
                'filters': filters_parsed,
                'base_asset_precision': info.get('baseAssetPrecision'),
                'quote_asset_precision': info.get('quotePrecision'),
                'timestamp': datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error getting symbol info for {symbol}: {e}")
            raise

    async def convert_dust_to_bnb(self, assets: Optional[List[str]] = None) -> Dict:
        """
        Convert small balances (dust) to BNB using Binance's dust conversion feature.

        Args:
            assets: List of asset symbols to convert (e.g., ['BTC', 'ETH']).
                   If None, will attempt to convert all dust balances.

        Returns:
            Dict with conversion results and details
        """
        try:
            # If no assets specified, get all dust balances
            if assets is None:
                balances = await self.get_account_balances()
                # Get current prices to calculate notional values
                dust_threshold_usd = 10  # Typical dust threshold

                dust_assets = []
                for balance in balances:
                    if balance.asset in ['BNB', 'USDT', 'USDC', 'BUSD']:
                        continue  # Skip stablecoins and BNB

                    # Try to get price in USDT
                    try:
                        symbol = f"{balance.asset}USDT"
                        price = await self.get_current_price(symbol)
                        notional = balance.free * price

                        if 0 < notional < dust_threshold_usd:
                            dust_assets.append(balance.asset)
                    except:
                        # If can't get price, include if balance is very small
                        if 0 < balance.free < 1:
                            dust_assets.append(balance.asset)

                assets = dust_assets

            if not assets:
                return {
                    'success': True,
                    'message': 'No dust balances found to convert',
                    'converted_assets': [],
                    'bnb_received': 0
                }

            # Convert dust using Binance API
            result = self.client.transfer_dust(asset=assets)

            logger.info(f"Dust conversion completed: {result}")

            return {
                'success': True,
                'message': f"Successfully converted {len(assets)} dust positions to BNB",
                'converted_assets': assets,
                'transfer_result': result.get('transferResult', []),
                'total_transferred': result.get('totalTransfered', 0),
                'total_service_charge': result.get('totalServiceCharge', 0)
            }

        except Exception as e:
            logger.error(f"Error converting dust: {e}")
            return {
                'success': False,
                'message': f"Failed to convert dust: {str(e)}",
                'converted_assets': [],
                'error': str(e)
            }

    async def get_dust_balances(self) -> Dict:
        """
        Identify all dust balances (positions too small to sell normally).

        Returns:
            Dict with dust balances and total USD value
        """
        try:
            balances = await self.get_account_balances()
            dust_positions = []
            total_dust_value_usd = 0
            dust_threshold_usd = 10

            for balance in balances:
                if balance.asset in ['BNB', 'USDT', 'USDC', 'BUSD']:
                    continue

                try:
                    # Try to get value in USDT
                    symbol = f"{balance.asset}USDT"
                    price = await self.get_current_price(symbol)
                    notional = balance.free * price

                    # Check if below dust threshold
                    if 0 < notional < dust_threshold_usd:
                        dust_positions.append({
                            'asset': balance.asset,
                            'quantity': balance.free,
                            'locked': balance.locked,
                            'price_usdt': price,
                            'value_usdt': notional,
                            'can_convert': True
                        })
                        total_dust_value_usd += notional

                except Exception as symbol_error:
                    # Asset might not have USDT pair or other issue
                    if balance.free > 0:
                        dust_positions.append({
                            'asset': balance.asset,
                            'quantity': balance.free,
                            'locked': balance.locked,
                            'price_usdt': None,
                            'value_usdt': None,
                            'can_convert': True,
                            'note': 'Price unavailable'
                        })

            return {
                'dust_positions': dust_positions,
                'total_count': len(dust_positions),
                'total_value_usdt': total_dust_value_usd,
                'dust_threshold_usdt': dust_threshold_usd,
                'recommendation': 'Convert to BNB using convert_dust_to_bnb()' if dust_positions else 'No dust found',
                'timestamp': datetime.utcnow()
            }

        except Exception as e:
            logger.error(f"Error getting dust balances: {e}")
            raise

    async def get_enhanced_candlestick_data(self, symbol: str, timeframe: str = "1h", limit: int = 100) -> Dict:
        """
        Get comprehensive candlestick analysis with technical indicators for each timeframe.
        Includes: OHLCV data, technical analysis, volatility, volume analysis, and trend signals.
        """
        try:
            # Get candlestick data
            candle_ctx = await self.get_candlestick_data(symbol, timeframe, limit)
            candles = candle_ctx.candlesticks

            if len(candles) < 20:
                raise ValueError(f"Insufficient candles for analysis (got {len(candles)}, need at least 20)")

            # Extract price and volume data
            closes = [c.close for c in candles]
            highs = [c.high for c in candles]
            lows = [c.low for c in candles]
            volumes = [c.volume for c in candles]

            # Calculate technical indicators for the timeframe
            indicators = await self.calculate_technical_indicators(symbol, timeframe)

            # Calculate volatility metrics
            avg_price = sum(closes) / len(closes)
            volatility = (max(closes) - min(closes)) / avg_price * 100

            # Calculate volume trend
            avg_volume = sum(volumes) / len(volumes)
            recent_avg_volume = sum(volumes[-5:]) / 5
            volume_trend = ((recent_avg_volume - avg_volume) / avg_volume) * 100

            # Identify price trend
            sma_20 = sum(closes[-20:]) / 20
            sma_50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else sma_20
            current_price = closes[-1]

            if current_price > sma_20 > sma_50:
                trend = "STRONG UPTREND"
            elif current_price > sma_20:
                trend = "UPTREND"
            elif current_price < sma_20 < sma_50:
                trend = "STRONG DOWNTREND"
            elif current_price < sma_20:
                trend = "DOWNTREND"
            else:
                trend = "SIDEWAYS"

            # Calculate support/resistance levels
            recent_highs = sorted(highs[-20:], reverse=True)[:3]
            recent_lows = sorted(lows[-20:])[:3]
            resistance_level = sum(recent_highs) / len(recent_highs)
            support_level = sum(recent_lows) / len(recent_lows)

            # Analyze recent candles for patterns
            recent_candles_analysis = []
            for candle in candles[-10:]:
                body_size = abs(candle.close - candle.open)
                candle_range = candle.high - candle.low
                body_percentage = (body_size / candle_range * 100) if candle_range > 0 else 0

                candle_type = "BULLISH" if candle.close > candle.open else "BEARISH" if candle.close < candle.open else "DOJI"
                strength = "STRONG" if body_percentage > 70 else "WEAK" if body_percentage < 30 else "MODERATE"

                recent_candles_analysis.append({
                    'time': candle.open_time,
                    'open': candle.open,
                    'high': candle.high,
                    'low': candle.low,
                    'close': candle.close,
                    'volume': candle.volume,
                    'type': candle_type,
                    'strength': strength,
                    'body_percentage': body_percentage,
                    'price_change_percent': ((candle.close - candle.open) / candle.open * 100) if candle.open > 0 else 0
                })

            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'total_candles': len(candles),
                'price_summary': {
                    'current': current_price,
                    'highest': max(closes),
                    'lowest': min(closes),
                    'average': avg_price,
                    'price_change_percent': ((current_price - closes[0]) / closes[0] * 100) if closes[0] > 0 else 0
                },
                'trend_analysis': {
                    'trend': trend,
                    'sma_20': sma_20,
                    'sma_50': sma_50,
                    'support_level': support_level,
                    'resistance_level': resistance_level
                },
                'volatility_metrics': {
                    'volatility_percent': volatility,
                    'volume_trend_percent': volume_trend,
                    'avg_volume': avg_volume,
                    'recent_avg_volume': recent_avg_volume
                },
                'technical_indicators': [
                    {'name': ind.name, 'value': ind.value, 'signal': ind.signal}
                    for ind in indicators.indicators
                ],
                'recent_candles': recent_candles_analysis,
                'timestamp': datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error getting enhanced candlestick data for {symbol}: {e}")
            raise
