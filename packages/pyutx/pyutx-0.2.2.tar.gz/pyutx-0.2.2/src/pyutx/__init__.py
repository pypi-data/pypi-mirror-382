from .api.async_support.clients import APIClient
from .types import TRADING_PLATFORM


def apyutx(trading_platform: TRADING_PLATFORM, config: dict = {}) -> APIClient:
    match trading_platform:
        case "okx":
            from .api.async_support.okx import OKXClient

            return OKXClient(config)
        case "binanceusdm":
            from .api.async_support.binance import BinanceUSDMClient

            return BinanceUSDMClient(config)
        case "bybitusdm":
            from .api.async_support.bybit import BybitUSDMClient

            return BybitUSDMClient(config)
        case "bingxusdm":
            from .api.async_support.bingx import BingXUSDMClient

            return BingXUSDMClient(config)
        case _:
            raise ValueError(f"Unsupported trading platform: {trading_platform}")
