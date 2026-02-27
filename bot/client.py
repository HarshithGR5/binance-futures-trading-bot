"""Binance Futures Testnet HTTP client with HMAC-SHA256 authentication."""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

BASE_URL = "https://testnet.binancefuture.com"


class BinanceAPIError(Exception):
    def __init__(self, status_code: int, code: int, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(f"[HTTP {status_code}] Binance error {code}: {message}")


class BinanceClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        base_url: str = BASE_URL,
    ) -> None:
        self.api_key = api_key or os.getenv("BINANCE_TESTNET_API_KEY", "")
        self.api_secret = api_secret or os.getenv("BINANCE_TESTNET_API_SECRET", "")
        self.base_url = base_url.rstrip("/")

        if not self.api_key or not self.api_secret:
            raise ValueError(
                "API credentials are missing. Set BINANCE_TESTNET_API_KEY and "
                "BINANCE_TESTNET_API_SECRET in your .env file."
            )

        self._session = requests.Session()
        self._session.headers.update({
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        })
        logger.info("BinanceClient initialised (testnet: %s)", self.base_url)

    def _sign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        params["recvWindow"] = 5000
        params["timestamp"] = int(time.time() * 1000)
        query = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode(), query.encode(), hashlib.sha256
        ).hexdigest()
        params["signature"] = signature
        return params

    def _request(
        self, method: str, path: str, params: Optional[Dict[str, Any]] = None, signed: bool = True
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        params = dict(params or {})

        if signed:
            self._sign(params)

        logger.debug("→ %s %s  params=%s", method.upper(), url, params)

        try:
            resp = self._session.request(method, url, params=params, timeout=15)
        except requests.ConnectionError as exc:
            logger.error("Network error: %s", exc)
            raise ConnectionError(f"Cannot reach {url}: {exc}") from exc
        except requests.Timeout as exc:
            logger.error("Request timed out: %s", exc)
            raise TimeoutError(f"Request to {url} timed out.") from exc

        logger.debug("← HTTP %s  body=%s", resp.status_code, resp.text[:500])

        if resp.status_code >= 400:
            try:
                body = resp.json()
                api_code = body.get("code", resp.status_code)
                api_msg = body.get("msg", resp.text)
            except ValueError:
                api_code = resp.status_code
                api_msg = resp.text
            raise BinanceAPIError(resp.status_code, api_code, api_msg)

        return resp.json()

    def get(self, path: str, params: Optional[Dict[str, Any]] = None, signed: bool = True):
        return self._request("GET", path, params, signed)

    def post(self, path: str, params: Optional[Dict[str, Any]] = None, signed: bool = True):
        return self._request("POST", path, params, signed)

    def delete(self, path: str, params: Optional[Dict[str, Any]] = None, signed: bool = True):
        return self._request("DELETE", path, params, signed)

    def server_time(self) -> int:
        data = self.get("/fapi/v1/time", signed=False)
        return data["serverTime"]

    def exchange_info(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        params = {}
        if symbol:
            params["symbol"] = symbol
        return self.get("/fapi/v1/exchangeInfo", params=params, signed=False)

    def account_info(self) -> Dict[str, Any]:
        return self.get("/fapi/v2/account")

    def ticker_price(self, symbol: str) -> Dict[str, Any]:
        return self.get("/fapi/v1/ticker/price", params={"symbol": symbol}, signed=False)
