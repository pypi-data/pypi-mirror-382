import logging
import types
from typing import Any, cast

from .auth import AuthHandler
from .exceptions import XifyError
from .request import RequestHandler

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Xify:
    """An asynchronous Python client for interacting with the X API."""

    def __init__(
        self,
        *,
        x_consumer_key: str,
        x_consumer_secret: str,
        x_access_token: str,
        x_access_token_secret: str,
    ) -> None:
        """Initialize the Xify instance.

        Args:
            x_consumer_key: X API consumer key.
            x_consumer_secret: X API consumer secret.
            x_access_token: X API access token.
            x_access_token_secret: X API access token secret.
        """
        self._auth_handler = AuthHandler(
            x_consumer_key, x_consumer_secret, x_access_token, x_access_token_secret
        )
        self._request_handler = RequestHandler(self._auth_handler)
        logger.info("Xify instance has been initialized.")

    async def __aenter__(self) -> "Xify":
        """Enter async context and intialize resources.

        Returns:
            The initialized Xify instance.
        """
        await self._request_handler.start_session()
        logger.debug("Xify context entered.")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        """Exit async context and close resources."""
        await self._request_handler.stop_session()
        logger.debug("Xify context exited.")

    async def tweet(self, content: dict[str, Any]) -> dict[str, Any]:
        """Send a tweet.

        Args:
            content: The content of the tweet.

        Raises:
            XifyError: If an error arises while sending tweet.

        Returns:
            A dictionary containing the data of the sent tweet.
        """
        logger.debug("Attempting to post a tweet.")

        try:
            url = "https://api.twitter.com/2/tweets"
            payload = {}

            if "msg" in content:
                payload["text"] = content["msg"]

            response = await self._request_handler.send("POST", url, json_body=payload)
            data = response.get("data", {})

            logger.info("Tweet posted successfully: %s", data)
            return cast(dict[str, Any], data)

        except Exception as e:
            if isinstance(e, XifyError):
                raise

            raise XifyError(
                f"An unexpected error occurred while sending tweet: {e}"
            ) from e
