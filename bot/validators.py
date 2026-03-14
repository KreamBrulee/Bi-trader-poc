from decimal import Decimal, InvalidOperation

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


class ValidationError(ValueError):
    """Raised when CLI input is invalid."""


def _to_positive_decimal(raw_value: str, field_name: str) -> Decimal:
    try:
        parsed = Decimal(str(raw_value))
    except (InvalidOperation, ValueError) as exc:
        raise ValidationError(f"{field_name} must be a valid number.") from exc

    if parsed <= 0:
        raise ValidationError(f"{field_name} must be greater than 0.")

    return parsed


def validate_order_input(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None,
) -> dict:
    symbol = symbol.strip().upper()
    side = side.strip().upper()
    order_type = order_type.strip().upper()

    if not symbol or not symbol.isalnum():
        raise ValidationError("symbol must be non-empty and alphanumeric (e.g. BTCUSDT).")

    if side not in VALID_SIDES:
        raise ValidationError("side must be BUY or SELL.")

    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError("order type must be MARKET or LIMIT.")

    validated_quantity = _to_positive_decimal(quantity, "quantity")

    validated_price = None
    if order_type == "LIMIT":
        if price is None:
            raise ValidationError("price is required for LIMIT orders.")
        validated_price = _to_positive_decimal(price, "price")
    elif price is not None:
        raise ValidationError("price must not be provided for MARKET orders.")

    return {
        "symbol": symbol,
        "side": side,
        "order_type": order_type,
        "quantity": str(validated_quantity),
        "price": str(validated_price) if validated_price is not None else None,
    }
