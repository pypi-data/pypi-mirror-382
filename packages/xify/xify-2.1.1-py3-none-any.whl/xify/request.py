import logging
from typing import Any, cast
from urllib.parse import parse_qs, urlparse

import aiohttp

from .auth import AuthHandler
from .exceptions import APIError, RequestError, XifyError

logger = logging.getLogger(__name__)


class RequestHandler:
    """Handle the authentication operations."""

    def __init__(self, auth: AuthHandler) -> None:
        """Initialize the request handler.

        Args:
            auth: The AuthHandler used for signing requests.
        """
        self._auth_handler = auth
        self._session: aiohttp.ClientSession | None = None

        logger.debug("RequestHandler has been initialized.")

    async def start_session(self) -> None:
        """Create the aiohttp session."""
        if not self._session:
            self._session = aiohttp.ClientSession()
        logger.debug("Aiohttp session started.")

    async def stop_session(self) -> None:
        """Create the aiohttp session."""
        if self._session:
            await self._session.close()
            self._session = None
        logger.debug("Aiohttp session stopped.")

    async def send(
        self,
        http_method: str,
        url: str,
        query_params: dict[str, str] | None = None,
        form_body_params: dict[str, str] | None = None,
        json_body: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Handle sending HTTP requests with OAuth 1.0a authentication.

        Args:
            http_method: The method of the HTTP request.
            url: The URL of the API endpoint.
            query_params: The URL's query parameters.
            form_body_params: The form body content.
            json_body: The json body content.

        Returns:
            The JSON response containing the data of the successful request.
        """
        if query_params is None:
            query_params = {}
        if form_body_params is None:
            form_body_params = {}
        if json_body is None:
            json_body = {}

        http_method_upper = http_method.upper()

        headers, request_kwargs = self._create_request_arguements(
            http_method_upper, url, query_params, form_body_params, json_body
        )

        return await self._send_request(http_method_upper, url, headers, request_kwargs)

    def _create_request_arguements(
        self,
        http_method_upper: str,
        url: str,
        query_params: dict[str, str],
        form_body_params: dict[str, str],
        json_body: dict[str, str],
    ) -> tuple[dict[str, str], dict[str, dict[str, str]]]:
        """Create and format the arguments for a request.

        Args:
            http_method_upper: The method of the HTTP request.
            url: The URL of the API endpoint.
            query_params: The URL's query parameters.
            form_body_params: The form body content.
            json_body: The json body content.

        Raises:
            ValueError: If json_Body and form_body_params are given.

        Returns:
            The header and request kwargs needed to complete a request to the X API.
        """
        logger.debug("Creating request arguments for %s %s", http_method_upper, url)

        # Collect parameters for the OAuth signature
        parsed_url = urlparse(url)
        query_params_from_url = {k: v[0] for k, v in parse_qs(parsed_url.query).items()}

        params_for_signature = {
            **query_params_from_url,
            **query_params,
        }
        request_kwargs = {"params": {**query_params_from_url, **query_params}}
        headers = {}

        if http_method_upper in {"POST", "PUT", "PATCH"}:
            if json_body and form_body_params:
                raise ValueError("Cannot use both 'json_body' and 'form_body_params'.")

            if json_body:
                headers["Content-Type"] = "application/json"
                request_kwargs["json"] = json_body
            elif form_body_params:
                headers["Content-Type"] = "application/x-www-form-urlencoded"
                params_for_signature.update(form_body_params)
                request_kwargs["data"] = form_body_params

        # Create OAuth authorization string
        auth_str = self._auth_handler.sign_request(
            http_method_upper, url, params_for_signature
        )
        headers["Authorization"] = auth_str

        return headers, request_kwargs

    async def _send_request(
        self,
        http_method_upper: str,
        url: str,
        headers: dict[str, str],
        request_kwargs: dict[str, dict[str, str]],
    ) -> dict[str, Any]:
        """Send a HTTP request to the X API.

        Args:
            http_method_upper: The method of the HTTP request.
            url: The URL of the API endpoint.
            headers: The request argument to authenticate this request as well as
                include any necessary arguments.
            request_kwargs: Additional arguments that are needed for the request.

        Raises:
            RequestError: If a unsuccesful request attempt arises or if
                the ClientSession is not setup or open.

        Returns:
            The JSON response containing the data of the successful request.
        """
        if not self._session:
            raise RequestError("Aiohttp session has not been started.")

        try:
            logger.debug(
                "Sending request: [%s] %s, headers=%s, kwargs=%s",
                http_method_upper,
                url,
                headers,
                request_kwargs,
            )
            async with self._session.request(
                http_method_upper, url, headers=headers, **request_kwargs
            ) as response:
                response.raise_for_status()

                logger.debug("Received response with status: %s", response.status)
                return cast(dict[str, Any], await response.json())

        except aiohttp.ClientResponseError as e:
            raise APIError(
                f"HTTP {e.status} {e.message} for {e.request_info.url}"
            ) from e

        except Exception as e:
            if isinstance(e, XifyError):
                raise
            raise RequestError("An error occurred while sending request.") from e
