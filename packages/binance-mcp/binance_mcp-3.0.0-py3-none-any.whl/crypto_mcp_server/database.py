from sqlalchemy import create_engine, Column, String, Float, DateTime, Enum, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from crypto_mcp_server.config import settings
import enum

Base = declarative_base()


class OrderSideDB(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderTypeDB(enum.Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    STOP_LOSS_LIMIT = "STOP_LOSS_LIMIT"


class OrderStatusDB(enum.Enum):
    NEW = "NEW"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class TradeLog(Base):
    __tablename__ = "trade_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String, unique=True, index=True)
    symbol = Column(String, index=True)
    side = Column(Enum(OrderSideDB))
    order_type = Column(Enum(OrderTypeDB))
    quantity = Column(Float)
    price = Column(Float, nullable=True)
    fill_price = Column(Float, nullable=True)
    status = Column(Enum(OrderStatusDB))
    timestamp = Column(DateTime, default=datetime.utcnow)
    commission = Column(Float, nullable=True)
    commission_asset = Column(String, nullable=True)
    trading_mode = Column(String)  # live (paper trading removed)

    # OCO tracking
    is_oco = Column(String, nullable=True)  # 'entry', 'exit', or None
    oco_order_list_id = Column(String, nullable=True)  # Links OCO orders together
    take_profit_price = Column(Float, nullable=True)
    stop_loss_price = Column(Float, nullable=True)

    # Additional tracking
    notes = Column(String, nullable=True)  # AI decision notes, strategy used, etc.


class ContextSnapshot(Base):
    __tablename__ = "context_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    context_type = Column(String, index=True)
    data = Column(String)  # JSON serialized
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class DailyPnL(Base):
    __tablename__ = "daily_pnl"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, unique=True, index=True)  # YYYY-MM-DD
    realized_pnl = Column(Float, default=0.0)
    unrealized_pnl = Column(Float, default=0.0)
    total_pnl = Column(Float, default=0.0)
    trade_count = Column(Integer, default=0)

    # Additional metrics
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    total_volume = Column(Float, default=0.0)


# Database setup
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
