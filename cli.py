import argparse
import logging
import os
import sys

from bot.client import BinanceAPIError, BinanceClientError, BinanceFuturesTestnetClient
from bot.logging_config import setup_logging
from bot.orders import OrderRequest, OrderService
from bot.validators import ValidationError, validate_order_input


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Place MARKET/LIMIT orders on Binance Futures Testnet (USDT-M)."
    )
    parser.add_argument("--symbol", required=True, help="Trading pair symbol, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, help="BUY or SELL")
    parser.add_argument("--order-type", required=True, help="MARKET or LIMIT")
    parser.add_argument("--quantity", required=True, help="Order quantity")
    parser.add_argument("--price", help="Required for LIMIT orders")

    parser.add_argument(
        "--api-key",
        default=os.getenv("BINANCE_API_KEY"),
        help="Binance API key (or set BINANCE_API_KEY)",
    )
    parser.add_argument(
        "--api-secret",
        default=os.getenv("BINANCE_API_SECRET"),
        help="Binance API secret (or set BINANCE_API_SECRET)",
    )

    parser.add_argument(
        "--base-url",
        default="https://testnet.binancefuture.com",
        help="Binance Futures Testnet base URL",
    )
    parser.add_argument(
        "--log-file",
        default="logs/trading_bot.log",
        help="Path to log file",
    )
    parser.add_argument("--timeout", type=int, default=15, help="API timeout in seconds")
    parser.add_argument("--recv-window", type=int, default=5000, help="recvWindow in ms")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate order response without calling Binance API",
    )

    return parser


def main() -> int:
    args = build_parser().parse_args()
    setup_logging(args.log_file)
    logger = logging.getLogger("cli")

    try:
        validated = validate_order_input(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )

        if not args.dry_run and (not args.api_key or not args.api_secret):
            raise ValidationError(
                "API credentials are required unless --dry-run is used. "
                "Set --api-key/--api-secret or BINANCE_API_KEY/BINANCE_API_SECRET."
            )

        request = OrderRequest(
            symbol=validated["symbol"],
            side=validated["side"],
            order_type=validated["order_type"],
            quantity=validated["quantity"],
            price=validated["price"],
        )

        print(OrderService.format_summary(request))

        client = BinanceFuturesTestnetClient(
            api_key=args.api_key or "dry-run-key",
            api_secret=args.api_secret or "dry-run-secret",
            base_url=args.base_url,
            timeout=args.timeout,
            recv_window=args.recv_window,
            dry_run=args.dry_run,
        )
        order_service = OrderService(client)

        response = order_service.place_order(request)
        print(OrderService.format_response(response))
        print("Success: order submitted successfully.")
        return 0

    except ValidationError as exc:
        logger.error("Validation error: %s", exc)
        print(f"Failure: validation error -> {exc}", file=sys.stderr)
        return 2
    except BinanceAPIError as exc:
        logger.error("Binance API error: %s", exc)
        print(f"Failure: Binance API error -> {exc}", file=sys.stderr)
        return 3
    except BinanceClientError as exc:
        logger.error("Client error: %s", exc)
        print(f"Failure: client error -> {exc}", file=sys.stderr)
        return 4
    except Exception as exc:
        logger.exception("Unexpected error")
        print(f"Failure: unexpected error -> {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
