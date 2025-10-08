from httpx import AsyncClient, HTTPStatusError

from ...errors import Error, RateLimitError
from .clients import APIClient


class BinanceUSDMClient(APIClient):
    def __init__(self, config: dict = {}):
        super().__init__(config)

        self.base_url = (
            "https://fapi.binance.com"
            if not self.demo
            else "https://testnet.binancefuture.com"
        )
        self.http_client = AsyncClient(base_url=self.base_url)
        self.timeframe_mapping = {
            "1m": "1m",
            "3m": "3m",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "1h": "1h",
            "2h": "2h",
            "4h": "4h",
            "6h": "6h",
            "8h": "8h",
            "12h": "12h",
            "1d": "1d",
            "3d": "3d",
            "1w": "1w",
            "1M": "1M",
        }

    async def get_candles(self, symbol, timeframe, since=None, limit=100):
        try:
            mapped_timeframe = self.timeframe_mapping.get(timeframe, None)
            if mapped_timeframe is None:
                raise Error(51000, f"Unsupported timeframe: {timeframe}")

            endpoint = "/fapi/v1/klines"
            params = {
                "symbol": symbol,
                "interval": mapped_timeframe,
                "limit": limit,
            }

            if since is not None:
                params["startTime"] = since

            response = await self.http_client.get(endpoint, params=params)
            response.raise_for_status()

            response_data = response.json()

            if isinstance(response_data, dict) and response_data.get("code"):
                raise Error(
                    int(response_data["code"]),
                    response_data.get("msg", "Unknown error"),
                )

            return [
                [
                    int(item[0]),  # Open time
                    float(item[1]),  # Open price
                    float(item[2]),  # High price
                    float(item[3]),  # Low price
                    float(item[4]),  # Close price
                    float(item[5]),  # Volume
                ]
                for item in response_data
            ]
        except HTTPStatusError as http_err:
            if http_err.response.status_code == 429:
                raise RateLimitError(429, str(http_err)) from http_err
            raise Error(http_err.response.status_code, str(http_err)) from http_err
        except Exception as e:
            raise Error(-1, str(e)) from e
