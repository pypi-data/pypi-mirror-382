import warnings
from abc import ABC, abstractmethod

from httpx import AsyncClient

from ...types import TIMEFRAME

warnings.simplefilter("always", ResourceWarning)


class APIClient(ABC):
    """
    Abstract base class for asynchronous API clients.

    This class provides a common interface and initialization pattern
    for API clients of different trading platforms. It should be subclassed to implement
    platform-specific logic.

    Attributes:
        demo (bool): Indicates whether to use the demo environment.
        base_url (str): The base URL for the API endpoints.
        http_client (AsyncClient): The underlying HTTP client for making requests.

    Args:
        config (dict): Configuration dictionary for initializing the client.

    Note:
        This is an abstract base class and should be subclassed for specific trading platforms.
        Subclasses must implement the abstract methods defined in this class.
    """

    def __init__(self, config: dict = {}) -> None:
        """Initialize the APIClient.

        Args:
            config (dict): Configuration dictionary for initializing the client.
                Expected keys include:
                - demo (bool, optional): Whether to use the demo environment. Defaults to False.
                - api_key (str, optional): API key for authenticated requests.
                - api_secret (str, optional): API secret for authenticated requests.
                - password (str, optional): Password for authenticated requests.

        Note:
            This is an abstract base class and should be subclassed for specific trading platforms.
            Subclasses must implement the abstract methods defined in this class.
        """
        self.demo = config.get("demo", False)
        self.base_url = config.get("base_url", "")
        self.http_client = AsyncClient(base_url=self.base_url)
        self.api_key = config.get("api_key", "")
        self.api_secret = config.get("api_secret", "")
        self.password = config.get("password", "")

    @abstractmethod
    async def get_candles(
        self,
        symbol: str,
        timeframe: TIMEFRAME,
        since: int | None = None,
        limit: int = 100,
    ) -> list[float]:
        """
        Get historical candlestick data for a given symbol and timeframe.

        Args:
            symbol (str): The trading pair symbol (e.g., "BTCUSDT").
            timeframe (TIMEFRAME): The timeframe for the candlesticks.
            since (int | None, optional): Timestamp in milliseconds to start fetching data from. Defaults to None.
            limit (int, optional): Maximum number of candlesticks to retrieve. Defaults to 100.

        Returns:
            list[float]: A list of candlestick data.
        """
        pass

    async def close(self) -> None:
        """
        Close the underlying HTTP client session.

        This method should be called to properly close the HTTP client and release resources.
        """

        await self.http_client.aclose()
