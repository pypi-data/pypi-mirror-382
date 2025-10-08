from typing import Optional
from datetime import datetime, date
from crypto_mcp_server.config import settings
from crypto_mcp_server.database import DailyPnL, SessionLocal
from crypto_mcp_server.schemas import OrderSide, TradeOrderAction
import logging

logger = logging.getLogger(__name__)


class RiskManager:
    """Risk management and validation for trades"""

    def __init__(self):
        self.max_trade_size_usd = settings.max_trade_size_usd
        self.max_daily_loss_usd = settings.max_daily_loss_usd
        self.max_position_size_usd = settings.max_position_size_usd

    async def validate_trade(
        self,
        action: TradeOrderAction,
        current_price: float,
        current_portfolio_value: float
    ) -> tuple[bool, Optional[str]]:
        """
        Validate a trade against risk parameters (if limits are set)
        Returns (is_valid, error_message)

        If risk limits are None, AI can trade freely (no restrictions)
        """

        # Calculate trade value
        trade_value_usd = action.quantity * current_price

        # Check max trade size (only if limit is set)
        if self.max_trade_size_usd is not None and trade_value_usd > self.max_trade_size_usd:
            error = f"Trade size ${trade_value_usd:.2f} exceeds max of ${self.max_trade_size_usd:.2f}"
            logger.warning(error)
            return False, error

        # Check max position size (only if limit is set)
        if self.max_position_size_usd is not None and trade_value_usd > self.max_position_size_usd:
            error = f"Position size ${trade_value_usd:.2f} exceeds max of ${self.max_position_size_usd:.2f}"
            logger.warning(error)
            return False, error

        # Check daily loss limit (only if limit is set)
        if self.max_daily_loss_usd is not None:
            today = date.today().isoformat()
            daily_loss = await self.get_daily_pnl(today)

            if daily_loss and daily_loss < -self.max_daily_loss_usd:
                error = f"Daily loss ${abs(daily_loss):.2f} exceeds max of ${self.max_daily_loss_usd:.2f}"
                logger.warning(error)
                return False, error

        # Validate sufficient portfolio value for position (only if not unlimited)
        if self.max_position_size_usd is not None:
            if trade_value_usd > current_portfolio_value * 0.5:  # Max 50% of portfolio per trade
                error = f"Trade size ${trade_value_usd:.2f} is too large relative to portfolio ${current_portfolio_value:.2f}"
                logger.warning(error)
                return False, error

        # All checks passed
        logger.info(f"Trade validated: ${trade_value_usd:.2f} (limits: size={self.max_trade_size_usd}, daily_loss={self.max_daily_loss_usd})")
        return True, None

    async def get_daily_pnl(self, date_str: str) -> Optional[float]:
        """Get total P&L for a specific date"""
        db = SessionLocal()
        try:
            record = db.query(DailyPnL).filter(DailyPnL.date == date_str).first()
            if record:
                return record.total_pnl
            return 0.0
        finally:
            db.close()

    async def update_daily_pnl(self, realized_pnl: float):
        """Update daily P&L after a trade"""
        db = SessionLocal()
        try:
            today = date.today().isoformat()
            record = db.query(DailyPnL).filter(DailyPnL.date == today).first()

            if record:
                record.realized_pnl += realized_pnl
                record.total_pnl = record.realized_pnl + record.unrealized_pnl
                record.trade_count += 1
            else:
                record = DailyPnL(
                    date=today,
                    realized_pnl=realized_pnl,
                    unrealized_pnl=0.0,
                    total_pnl=realized_pnl,
                    trade_count=1
                )
                db.add(record)

            db.commit()
            logger.info(f"Updated daily P&L for {today}: ${realized_pnl:.2f}")
        finally:
            db.close()

    async def check_circuit_breaker(self) -> tuple[bool, Optional[str]]:
        """
        Check if circuit breaker should trigger (halt all trading)
        Returns (should_halt, reason)

        Only triggers if max_daily_loss_usd is set
        """
        if self.max_daily_loss_usd is None:
            # No daily loss limit = no circuit breaker
            return False, None

        today = date.today().isoformat()
        daily_pnl = await self.get_daily_pnl(today)

        if daily_pnl and daily_pnl < -self.max_daily_loss_usd:
            return True, f"Circuit breaker triggered: Daily loss ${abs(daily_pnl):.2f} exceeds limit"

        return False, None

    def validate_order_parameters(self, action: TradeOrderAction) -> tuple[bool, Optional[str]]:
        """Validate basic order parameters"""

        # Check symbol
        if not action.symbol or action.symbol.strip() == "":
            return False, "Symbol is required"

        # Check quantity
        if action.quantity <= 0:
            return False, "Quantity must be positive"

        # Check price for limit orders
        if action.order_type.value in ["LIMIT", "STOP_LOSS_LIMIT"] and action.price is None:
            return False, f"Price required for {action.order_type.value} orders"

        # Check stop price for stop orders
        if "STOP" in action.order_type.value and action.stop_price is None:
            return False, f"Stop price required for {action.order_type.value} orders"

        # Validate price values
        if action.price is not None and action.price <= 0:
            return False, "Price must be positive"

        if action.stop_price is not None and action.stop_price <= 0:
            return False, "Stop price must be positive"

        return True, None
