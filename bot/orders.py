from dataclasses import dataclass

from .client import BinanceFuturesTestnetClient


@dataclass
class OrderRequest:
    symbol: str
    side: str
    order_type: str
    quantity: str
    price: str | None = None


class OrderService:
    """Application layer for placing and formatting orders."""

    def __init__(self, client: BinanceFuturesTestnetClient) -> None:
        self.client = client

    def place_order(self, request: OrderRequest) -> dict:
        return self.client.place_order(
            symbol=request.symbol,
            side=request.side,
            order_type=request.order_type,
            quantity=request.quantity,
            price=request.price,
        )

    @staticmethod
    def format_summary(request: OrderRequest) -> str:
        details = [
            f"symbol={request.symbol}",
            f"side={request.side}",
            f"type={request.order_type}",
            f"quantity={request.quantity}",
        ]
        if request.price is not None:
            details.append(f"price={request.price}")
        return "Order Request Summary: " + ", ".join(details)

    @staticmethod
    def format_response(response: dict) -> str:
        order_id = response.get("orderId", "N/A")
        status = response.get("status", "N/A")
        executed_qty = response.get("executedQty", "N/A")
        avg_price = response.get("avgPrice", "N/A")
        return (
            "Order Response Details: "
            f"orderId={order_id}, status={status}, "
            f"executedQty={executed_qty}, avgPrice={avg_price}"
        )
