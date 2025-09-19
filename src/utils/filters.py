import math
from decimal import Decimal, ROUND_DOWN, ROUND_UP
from typing import Dict, Any


def round_to_tick_size(price: float, tick_size: float, round_up: bool = False) -> float:
    tick_decimal = Decimal(str(tick_size))
    price_decimal = Decimal(str(price))

    if round_up:
        return float((price_decimal / tick_decimal).quantize(Decimal('1'), rounding=ROUND_UP) * tick_decimal)
    else:
        return float((price_decimal / tick_decimal).quantize(Decimal('1'), rounding=ROUND_DOWN) * tick_decimal)


def round_to_step_size(quantity: float, step_size: float) -> float:
    step_decimal = Decimal(str(step_size))
    qty_decimal = Decimal(str(quantity))

    return float((qty_decimal / step_decimal).quantize(Decimal('1'), rounding=ROUND_DOWN) * step_decimal)


def apply_exchange_filters(
    symbol: str,
    price: float,
    quantity: float,
    market_info: Dict[str, Any],
    side: str = "buy"
) -> tuple[float, float]:
    limits = market_info.get('limits', {})
    precision = market_info.get('precision', {})

    tick_size = precision.get('price', 0.01)
    step_size = precision.get('amount', 0.00001)

    min_cost = limits.get('cost', {}).get('min', 10)
    min_amount = limits.get('amount', {}).get('min', 0.00001)
    max_amount = limits.get('amount', {}).get('max', float('inf'))

    filtered_price = round_to_tick_size(price, tick_size, round_up=(side == "buy"))

    filtered_qty = round_to_step_size(quantity, step_size)

    filtered_qty = max(filtered_qty, min_amount)
    filtered_qty = min(filtered_qty, max_amount)

    notional = filtered_price * filtered_qty
    if notional < min_cost:
        filtered_qty = round_to_step_size(min_cost / filtered_price, step_size)

    return filtered_price, filtered_qty


def validate_order_params(
    symbol: str,
    price: float,
    quantity: float,
    market_info: Dict[str, Any]
) -> bool:
    try:
        filtered_price, filtered_qty = apply_exchange_filters(
            symbol, price, quantity, market_info
        )

        limits = market_info.get('limits', {})
        min_cost = limits.get('cost', {}).get('min', 10)

        notional = filtered_price * filtered_qty
        return notional >= min_cost

    except Exception:
        return False