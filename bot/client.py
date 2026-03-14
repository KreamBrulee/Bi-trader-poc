import hashlib
import hmac
import logging
import time
from typing import Any
from urllib.parse import urlencode

import requests


class BinanceClientError(Exception):
    """Base exception for Binance client failures."""


class BinanceAPIError(BinanceClientError):
    """Raised when Binance API returns a non-success response."""


class BinanceNetworkError(BinanceClientError):
    """Raised for transport-level request failures."""


class BinanceFuturesTestnetClient:
    """Minimal wrapper for Binance USDT-M Futures Testnet signed endpoints."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = "https://testnet.binancefuture.com",
        timeout: int = 15,
        recv_window: int = 5000,
        dry_run: bool = False,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.recv_window = recv_window
        self.dry_run = dry_run

        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})

    def _sign(self, params: dict[str, Any]) -> str:
        query_string = urlencode(params, doseq=True)
        return hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        signed: bool = False,
    ) -> dict[str, Any]:
        params = params.copy() if params else {}

        if signed:
            params["timestamp"] = int(time.time() * 1000)
            params["recvWindow"] = self.recv_window
            params["signature"] = self._sign(params)

        url = f"{self.base_url}{path}"
        self.logger.info("API Request | %s %s | params=%s", method, path, params)

        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            self.logger.exception("Network error while calling Binance API")
            raise BinanceNetworkError(f"Network error: {exc}") from exc

        content_type = response.headers.get("Content-Type", "")
        is_json = "application/json" in content_type
        body: dict[str, Any] | str
        if is_json:
            body = response.json()
        else:
            body = response.text

        self.logger.info(
            "API Response | status=%s | body=%s",
            response.status_code,
            body,
        )

        if response.status_code >= 400:
            raise BinanceAPIError(f"Binance API error {response.status_code}: {body}")

        if isinstance(body, dict):
            return body
        raise BinanceAPIError("Unexpected non-JSON response from Binance API")

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        price: str | None = None,
        time_in_force: str = "GTC",
    ) -> dict[str, Any]:
        if self.dry_run:
            now_ms = int(time.time() * 1000)
            simulated = {
                "symbol": symbol,
                "orderId": now_ms,
                "clientOrderId": f"dryrun_{now_ms}",
                "status": "NEW" if order_type == "LIMIT" else "FILLED",
                "type": order_type,
                "side": side,
                "executedQty": quantity if order_type == "MARKET" else "0",
                "avgPrice": price if order_type == "LIMIT" else "0.0",
            }
            self.logger.info("DRY RUN order response | %s", simulated)
            return simulated

        params: dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }

        if order_type == "LIMIT":
            params["price"] = price
            params["timeInForce"] = time_in_force

        return self._request("POST", "/fapi/v1/order", params=params, signed=True)
