import math
import re
from decimal import Decimal, InvalidOperation


SUPPORTED_CURRENCIES = {"BRL", "USD", "EUR"}
TOKEN_PATTERN = re.compile(r"^tok_[A-Za-z0-9_-]{4,}$")


def _is_valid_token(token):
    if not isinstance(token, str):
        return False
    token = token.strip()
    return bool(TOKEN_PATTERN.fullmatch(token))


def _has_two_decimal_places_or_less(amount: float) -> bool:
    try:
        decimal_amount = Decimal(str(amount))
    except (InvalidOperation, ValueError):
        return False
    if not decimal_amount.is_finite():
        return False
    return decimal_amount.as_tuple().exponent >= -2


def validate_order(order_total, payment_token, currency="BRL"):
    """Validate checkout payload for critical payment path."""
    if not isinstance(currency, str):
        return False
    currency = currency.upper()
    if currency not in SUPPORTED_CURRENCIES:
        return False
    if isinstance(order_total, bool):
        return False
    if isinstance(order_total, int):
        if order_total <= 0:
            return False
    elif isinstance(order_total, float):
        if not math.isfinite(order_total):
            return False
        if order_total <= 0:
            return False
        if not _has_two_decimal_places_or_less(order_total):
            return False
    else:
        return False
    return _is_valid_token(payment_token)
