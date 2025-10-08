from typing import Dict, List, Optional
from datetime import datetime
from crypto_mcp_server.schemas import (
    Balance, Position, Trade, MarketDataContext,
    OrderSide, OrderType, OrderStatus, MCPContextMetadata
)
import uuid
import logging

logger = logging.getLogger(__name__)


class PaperTradingEngine:
    """Mock trading engine for paper trading"""

    def __init__(self, starting_balance_usd: float = 10000.0):
        self.balances: Dict[str, Balance] = {
            "USD": Balance(asset="USD", free=starting_balance_usd, locked=0.0, total=starting_balance_usd)
        }
        self.open_orders: Dict[str, Dict] = {}
        self.filled_orders: List[Trade] = []
        self.order_counter = 0
        self.position_cost_basis: Dict[str, float] = {}  # Track average entry price per asset

    async def get_balance(self, asset: str) -> Optional[Balance]:
        """Get balance for a specific asset"""
        return self.balances.get(asset)

    async def get_all_balances(self) -> List[Balance]:
        """Get all non-zero balances"""
        return [b for b in self.balances.values() if b.total > 0]

    async def place_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: float,
        price: Optional[float] = None,
        current_price: float = None
    ) -> Dict:
        """Simulate order placement"""
        self.order_counter += 1
        order_id = f"PAPER_{self.order_counter}_{uuid.uuid4().hex[:8]}"

        # Extract base and quote assets (e.g., BTCUSD -> BTC, USD)
        # Assuming USD is always the quote currency for simplicity
        base_asset = symbol.replace("USD", "")
        quote_asset = "USD"

        # Determine execution price
        if order_type == OrderType.MARKET:
            execution_price = current_price if current_price else price
        else:
            execution_price = price

        if execution_price is None:
            raise ValueError("Execution price cannot be determined")

        # For limit orders, don't execute immediately - store as open order
        if order_type in [OrderType.LIMIT, OrderType.STOP_LOSS, OrderType.STOP_LOSS_LIMIT]:
            self.open_orders[order_id] = {
                "orderId": order_id,
                "symbol": symbol,
                "status": "NEW",
                "side": side.value,
                "type": order_type.value,
                "quantity": quantity,
                "price": execution_price,
                "stop_price": None
            }
            return self.open_orders[order_id]

        # Calculate trade value for market orders
        trade_value = quantity * execution_price

        # Check if we have sufficient balance
        if side == OrderSide.BUY:
            # Need USD to buy
            usd_balance = self.balances.get(quote_asset)
            if not usd_balance or usd_balance.free < trade_value:
                error_msg = f"Insufficient balance: Required {trade_value}, Available {usd_balance.free if usd_balance else 0}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # Deduct USD
            usd_balance.free -= trade_value
            usd_balance.total -= trade_value

            # Add base asset
            if base_asset not in self.balances:
                self.balances[base_asset] = Balance(asset=base_asset, free=0.0, locked=0.0, total=0.0)
                self.position_cost_basis[base_asset] = 0.0

            # Update cost basis (weighted average)
            old_quantity = self.balances[base_asset].total
            old_cost = self.position_cost_basis.get(base_asset, 0.0)
            self.position_cost_basis[base_asset] = ((old_quantity * old_cost) + (quantity * execution_price)) / (old_quantity + quantity) if (old_quantity + quantity) > 0 else execution_price

            self.balances[base_asset].free += quantity
            self.balances[base_asset].total += quantity

        elif side == OrderSide.SELL:
            # Need base asset to sell
            base_balance = self.balances.get(base_asset)
            if not base_balance or base_balance.free < quantity:
                error_msg = f"Insufficient balance: Required {quantity} {base_asset}, Available {base_balance.free if base_balance else 0}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # Deduct base asset
            base_balance.free -= quantity
            base_balance.total -= quantity

            # Add USD
            if quote_asset not in self.balances:
                self.balances[quote_asset] = Balance(asset=quote_asset, free=0.0, locked=0.0, total=0.0)
            self.balances[quote_asset].free += trade_value
            self.balances[quote_asset].total += trade_value

        # Record trade
        trade = Trade(
            id=order_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=execution_price,
            fill_price=execution_price,
            status=OrderStatus.FILLED,
            timestamp=datetime.utcnow(),
            commission=0.0,
            commission_asset=quote_asset
        )
        self.filled_orders.append(trade)

        logger.info(f"Paper trade executed: {side.value} {quantity} {symbol} @ {execution_price}")

        return {
            "orderId": order_id,
            "symbol": symbol,
            "status": "FILLED",
            "side": side.value,
            "type": order_type.value,
            "executedQty": str(quantity),
            "cummulativeQuoteQty": str(trade_value),
            "price": str(execution_price),
            "fills": [{
                "price": str(execution_price),
                "qty": str(quantity),
                "commission": "0",
                "commissionAsset": quote_asset
            }]
        }

    async def cancel_order(self, order_id: str) -> Dict:
        """Simulate order cancellation"""
        if order_id in self.open_orders:
            order = self.open_orders.pop(order_id)
            return {
                "orderId": order_id,
                "status": "CANCELED"
            }
        else:
            raise ValueError(f"Order {order_id} not found")

    async def get_recent_trades(self, limit: int = 50) -> List[Trade]:
        """Get recent paper trades"""
        return self.filled_orders[-limit:]

    async def get_positions(self, prices: Dict[str, float]) -> List[Position]:
        """Calculate current positions with P&L"""
        positions = []

        for asset, balance in self.balances.items():
            if asset != "USD" and balance.total > 0:
                symbol = f"{asset}USD"
                current_price = prices.get(symbol, 0.0)
                entry_price = self.position_cost_basis.get(asset, 0.0)

                # Calculate P&L
                unrealized_pnl = (current_price - entry_price) * balance.total
                unrealized_pnl_percent = ((current_price - entry_price) / entry_price * 100) if entry_price > 0 else 0.0

                positions.append(Position(
                    symbol=symbol,
                    quantity=balance.total,
                    entry_price=entry_price,
                    current_price=current_price,
                    unrealized_pnl=unrealized_pnl,
                    unrealized_pnl_percent=unrealized_pnl_percent
                ))

        return positions

    async def get_portfolio_value(self, prices: Dict[str, float]) -> float:
        """Calculate total portfolio value in USD"""
        total_value = 0.0

        for asset, balance in self.balances.items():
            if asset == "USD":
                total_value += balance.total
            else:
                symbol = f"{asset}USD"
                price = prices.get(symbol, 0.0)
                total_value += balance.total * price

        return total_value
