"""Input validators for order parameters."""

from __future__ import annotations

import logging
from decimal import Decimal, InvalidOperation
from typing import Optional

logger = logging.getLogger(__name__)

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {
    "MARKET", "LIMIT", "STOP", "STOP_MARKET",
    "TAKE_PROFIT", "TAKE_PROFIT_MARKET",
}
PRICE_REQUIRED_TYPES = {"LIMIT", "STOP", "TAKE_PROFIT"}
STOP_REQUIRED_TYPES = {"STOP", "STOP_MARKET", "TAKE_PROFIT", "TAKE_PROFIT_MARKET"}


def validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not symbol or not symbol.isalpha():
        raise ValueError(f"Invalid symbol '{symbol}'. Must be alphabetic (e.g. BTCUSDT).")
    if len(symbol) < 5:
        raise ValueError(f"Symbol '{symbol}' looks too short. Expected something like BTCUSDT.")
    logger.debug("Validated symbol: %s", symbol)
    return symbol


def validate_side(side: str) -> str:
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(f"Invalid side '{side}'. Must be one of {VALID_SIDES}.")
    return side


def validate_order_type(order_type: str) -> str:
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. Supported: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )
    return order_type


def validate_quantity(quantity: str | float) -> Decimal:
    try:
        qty = Decimal(str(quantity))
    except (InvalidOperation, ValueError):
        raise ValueError(f"Invalid quantity '{quantity}'. Must be a positive number.")
    if qty <= 0:
        raise ValueError(f"Quantity must be > 0, got {qty}.")
    return qty


def validate_price(price: Optional[str | float], order_type: str) -> Optional[Decimal]:
    if price is None:
        if order_type in PRICE_REQUIRED_TYPES:
            raise ValueError(f"Price is required for {order_type} orders.")
        return None
    try:
        p = Decimal(str(price))
    except (InvalidOperation, ValueError):
        raise ValueError(f"Invalid price '{price}'. Must be a positive number.")
    if p <= 0:
        raise ValueError(f"Price must be > 0, got {p}.")
    return p


def validate_stop_price(stop_price: Optional[str | float], order_type: str) -> Optional[Decimal]:
    if stop_price is None:
        if order_type in STOP_REQUIRED_TYPES:
            raise ValueError(f"Stop price is required for {order_type} orders.")
        return None
    try:
        sp = Decimal(str(stop_price))
    except (InvalidOperation, ValueError):
        raise ValueError(f"Invalid stop price '{stop_price}'. Must be a positive number.")
    if sp <= 0:
        raise ValueError(f"Stop price must be > 0, got {sp}.")
    return sp
