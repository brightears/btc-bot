"""Helpers for applying exchange filters (tick size, step size, notional)."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN, getcontext
from typing import Optional

getcontext().prec = 18


@dataclass
class SymbolFilters:
    tick_size: Optional[float]
    step_size: Optional[float]
    min_notional: Optional[float]


def _quantize(value: float, quantum: Optional[float]) -> float:
    if not quantum:
        return value
    quantized = Decimal(str(value)).quantize(Decimal(str(quantum)), rounding=ROUND_DOWN)
    return float(quantized)


def round_price(price: float, tick_size: Optional[float]) -> float:
    return _quantize(price, tick_size)


def round_quantity(quantity: float, step_size: Optional[float]) -> float:
    return _quantize(quantity, step_size)


def ensure_min_notional(price: float, quantity: float, min_notional: Optional[float]) -> float:
    if not min_notional:
        return quantity
    if price * quantity >= min_notional:
        return quantity
    adjusted_qty = min_notional / max(price, 1e-12)
    return adjusted_qty


def apply_filters(price: float, quantity: float, filters: SymbolFilters) -> tuple[float, float]:
    rounded_price = round_price(price, filters.tick_size)
    rounded_qty = round_quantity(quantity, filters.step_size)
    rounded_qty = ensure_min_notional(rounded_price, rounded_qty, filters.min_notional)
    rounded_qty = round_quantity(rounded_qty, filters.step_size)
    return rounded_price, rounded_qty
