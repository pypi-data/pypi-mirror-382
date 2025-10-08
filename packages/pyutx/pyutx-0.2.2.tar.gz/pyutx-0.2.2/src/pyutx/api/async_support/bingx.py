from httpx import AsyncClient

from ...errors import Error, RateLimitError
from .clients import APIClient


class BingXUSDMClient(APIClient):
    def __init__(self, config={}):
        super().__init__(config)

        self.base_url = (
            "https://api.bingx.com"
            if not self.demo
            else "https://open-api-vst.bingx.com"
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
        mapped_timeframe = self.timeframe_mapping.get(timeframe, None)
        if mapped_timeframe is None:
            raise ValueError(f"Unsupported timeframe: {timeframe}")

        endpoint = "/openApi/swap/v3/quote/klines"
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

        if response_data.get("code") != 0:
            self.__handle_error(
                int(response_data["code"]),
                response_data.get("msg", None),
            )

        return [
            [
                int(candle.get("time")),
                float(candle.get("open")),
                float(candle.get("high")),
                float(candle.get("low")),
                float(candle.get("close")),
                float(candle.get("volume")),
            ]
            for candle in response_data.get("data", [])[::-1]
        ]

    async def close(self) -> None:
        await self.http_client.aclose()

    def __handle_error(self, code: int, msg: str) -> None:
        if code == 100410:
            raise RateLimitError(code, msg)
        raise Error(int(code), msg or "Unknown error")
