from httpx import AsyncClient

from ...errors import Error, RateLimitError
from .clients import APIClient


class BybitUSDMClient(APIClient):
    def __init__(self, config: dict = {}):
        super().__init__(config)

        self.base_url = (
            "https://api.bybit.com"
            if not self.demo
            else "https://api-testnet.bybit.com"
        )
        self.http_client = AsyncClient(base_url=self.base_url)
        self.timeframe_mapping = {
            "1m": "1",
            "3m": "3",
            "5m": "5",
            "15m": "15",
            "30m": "30",
            "1h": "60",
            "2h": "120",
            "4h": "240",
            "6h": "360",
            "12h": "720",
            "1d": "D",
            "1w": "W",
            "1M": "M",
        }

    async def get_candles(self, symbol, timeframe, since=None, limit=100):
        try:
            mapped_timeframe = self.timeframe_mapping.get(timeframe, None)
            if mapped_timeframe is None:
                raise ValueError(f"Unsupported timeframe: {timeframe}")

            endpoint = "/v5/market/kline"
            params = {
                "category": "linear",
                "symbol": symbol,
                "interval": mapped_timeframe,
                "limit": limit,
            }

            if since is not None:
                params["start"] = since

            response = await self.http_client.get(endpoint, params=params)
            response.raise_for_status()

            response_data = response.json()

            if response_data.get("retCode") != 0:
                self.__handle_error(
                    int(response_data["retCode"]),
                    response_data.get("ret_msg", None),
                )

            return [
                [
                    int(candle[0]),  # Open time
                    float(candle[1]),  # Open
                    float(candle[2]),  # High
                    float(candle[3]),  # Low
                    float(candle[4]),  # Close
                    float(candle[5]),  # Volume
                ]
                for candle in response_data.get("result").get("list", [])[::-1]
            ]
        except Exception as e:
            raise Error(-1, str(e)) from e

    async def close(self) -> None:
        await self.http_client.aclose()

    def __handle_error(self, code: int, msg: str) -> None:
        if code == 10006:
            raise RateLimitError(code, msg)

        raise Error(int(code), msg or "Unknown error")
