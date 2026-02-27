"""Order placement and response formatting."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any, Dict, Optional

from bot.client import BinanceClient

logger = logging.getLogger(__name__)

ORDER_PATH = "/fapi/v1/order"
TIF_REQUIRED_TYPES = {"LIMIT", "STOP", "TAKE_PROFIT"}


def _fmt(d: Decimal) -> str:
    return f"{d:f}"


def place_order(
    client: BinanceClient,
    *,
    symbol: str,
    side: str,
    order_type: str,
    quantity: Decimal,
    price: Optional[Decimal] = None,
    stop_price: Optional[Decimal] = None,
    time_in_force: str = "GTC",
) -> Dict[str, Any]:
    params: Dict[str, Any] = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": _fmt(quantity),
    }

    if price is not None:
        params["price"] = _fmt(price)
    if stop_price is not None:
        params["stopPrice"] = _fmt(stop_price)
    if order_type in TIF_REQUIRED_TYPES:
        params["timeInForce"] = time_in_force

    logger.info(
        "Placing %s %s order: %s %s @ %s (stop=%s)",
        side, order_type, quantity, symbol,
        price or "MARKET", stop_price or "N/A",
    )

    response = client.post(ORDER_PATH, params=params)

    logger.info(
        "Order response – orderId=%s status=%s executedQty=%s avgPrice=%s",
        response.get("orderId"),
        response.get("status"),
        response.get("executedQty"),
        response.get("avgPrice", "N/A"),
    )

    return response


def format_order_response(resp: Dict[str, Any]) -> str:
    lines = [
        "╔══════════════════════════════════════════╗",
        "║           ORDER RESPONSE                 ║",
        "╠══════════════════════════════════════════╣",
        f"  Order ID    : {resp.get('orderId', 'N/A')}",
        f"  Symbol      : {resp.get('symbol', 'N/A')}",
        f"  Side        : {resp.get('side', 'N/A')}",
        f"  Type        : {resp.get('type', 'N/A')}",
        f"  Status      : {resp.get('status', 'N/A')}",
        f"  Quantity    : {resp.get('origQty', 'N/A')}",
        f"  Executed    : {resp.get('executedQty', 'N/A')}",
        f"  Price       : {resp.get('price', 'N/A')}",
        f"  Avg Price   : {resp.get('avgPrice', 'N/A')}",
        f"  Stop Price  : {resp.get('stopPrice', 'N/A')}",
        f"  Time        : {resp.get('updateTime', 'N/A')}",
        "╚══════════════════════════════════════════╝",
    ]
    return "\n".join(lines)
