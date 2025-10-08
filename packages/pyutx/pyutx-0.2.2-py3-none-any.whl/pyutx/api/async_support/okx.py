from httpx import AsyncClient

from ...errors import Error, RateLimitError
from .clients import APIClient


class OKXClient(APIClient):
    def __init__(self, config: dict = {}):
        super().__init__(config)

        self.base_url = "https://www.okx.com"
        self.http_client = AsyncClient(
            base_url=self.base_url,
            headers={"x-simulated-trading": "1" if self.demo else "0"},
        )
        self.timeframe_mapping = {
            "1m": "1m",
            "3m": "3m",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "1h": "1H",
            "2h": "2H",
            "4h": "4H",
            "6h": "6Hutc",
            "12h": "12Hutc",
            "1d": "1Dutc",
            "2d": "2Dutc",
            "3d": "3Dutc",
            "1w": "1Wutc",
            "1M": "1Mutc",
            "3M": "3Mutc",
        }

    async def get_candles(self, symbol, timeframe, since=None, limit=100):
        mapped_timeframe = self.timeframe_mapping.get(timeframe, None)
        if mapped_timeframe is None:
            raise ValueError(f"Unsupported timeframe: {timeframe}")

        endpoint = "/api/v5/market/candles"
        params = {
            "instId": symbol,
            "bar": self.timeframe_mapping[timeframe],
            "limit": limit,
        }

        if since is not None:
            params["before"] = since

        response = await self.http_client.get(endpoint, params=params)
        response.raise_for_status()

        response_data = response.json()

        code = response_data.get("code")
        if code != "0":
            self.__handle_error(int(code), response_data.get("msg", None))

        return [
            [
                int(candle[0]),  # timestamp
                float(candle[1]),  # open
                float(candle[2]),  # high
                float(candle[3]),  # low
                float(candle[4]),  # close
                float(candle[5]),  # volume
            ]
            for candle in response_data.get("data", [])[::-1]
        ]

    def __handle_error(self, code: int, msg: str) -> None:
        if code == 50011:
            raise RateLimitError(code, msg)

        raise Error(int(code), msg or "Unknown error")
