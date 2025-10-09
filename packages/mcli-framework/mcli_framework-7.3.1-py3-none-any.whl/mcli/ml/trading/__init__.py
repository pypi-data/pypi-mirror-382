"""Trading module for portfolio management and trade execution"""

from mcli.ml.trading.models import (
    # Enums
    OrderStatus,
    OrderType,
    OrderSide,
    PositionSide,
    PortfolioType,
    RiskLevel,
    # Database models
    TradingAccount,
    Portfolio,
    Position,
    TradingOrder,
    PortfolioPerformanceSnapshot,
    TradingSignal,
    # Pydantic models
    TradingAccountCreate,
    PortfolioCreate,
    OrderCreate,
    PositionResponse,
    OrderResponse,
    PortfolioResponse,
    TradingSignalResponse,
)
from mcli.ml.trading.trading_service import TradingService
from mcli.ml.trading.alpaca_client import AlpacaTradingClient
from mcli.ml.trading.risk_management import RiskManager
from mcli.ml.trading.paper_trading import PaperTradingEngine

__all__ = [
    # Enums
    "OrderStatus",
    "OrderType",
    "OrderSide",
    "PositionSide",
    "PortfolioType",
    "RiskLevel",
    # Database models
    "TradingAccount",
    "Portfolio",
    "Position",
    "TradingOrder",
    "PortfolioPerformanceSnapshot",
    "TradingSignal",
    # Pydantic models
    "TradingAccountCreate",
    "PortfolioCreate",
    "OrderCreate",
    "PositionResponse",
    "OrderResponse",
    "PortfolioResponse",
    "TradingSignalResponse",
    # Services
    "TradingService",
    "AlpacaTradingClient",
    "RiskManager",
    "PaperTradingEngine",
]
