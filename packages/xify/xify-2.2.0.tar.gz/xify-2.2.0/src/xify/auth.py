import base64
import hashlib
import hmac
import logging
import time
import uuid
from urllib.parse import quote, urlparse

logger = logging.getLogger(__name__)


class AuthHandler:
    """Handle the authentication operations."""

    def __init__(
        self,
        x_consumer_key: str,
        x_consumer_secret: str,
        x_access_token: str,
        x_access_token_secret: str,
    ) -> None:
        """Initialize the AuthHandler instance.

        Args:
            x_consumer_key: X API consumer key.
            x_consumer_secret: X API consumer secret.
            x_access_token: X API access token.
            x_access_token_secret: X API access token secret.
        """
        self._x_consumer_key = x_consumer_key
        self._x_consumer_secret = x_consumer_secret
        self._x_access_token = x_access_token
        self._x_access_token_secret = x_access_token_secret

        self._base_parameters = {
            "oauth_consumer_key": self._x_consumer_key,
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_token": self._x_access_token,
            "oauth_version": "1.0",
        }

        logger.debug("AuthHandler has been initialized.")

    def sign_request(
        self, http_method: str, url: str, params_for_signature: dict[str, str]
    ) -> str:
        """Sign a request to the X API with authentication.

        Args:
            http_method: The method of the HTTP request.
            url: The base URL of the API endpoint.
            params_for_signature: A dictionary with all the parameters included in
                the request.

        Returns:
            An authentication string to be used with the signed request.
        """
        logger.debug("Attempting to sign request for [%s] %s", http_method, url)

        # Parse the URL
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

        # Create nonce and get timestamp for this request
        oauth_nonce = self._create_nonce()
        oauth_timestamp = str(int(time.time()))

        # Create oauth signature for this request
        parameters = {
            **self._base_parameters,
            **params_for_signature,
            "oauth_nonce": oauth_nonce,
            "oauth_timestamp": oauth_timestamp,
        }
        oauth_signature = self._create_signature(http_method, base_url, parameters)

        # Create authorization string for this request
        parameters = {
            **self._base_parameters,
            "oauth_nonce": oauth_nonce,
            "oauth_timestamp": oauth_timestamp,
            "oauth_signature": oauth_signature,
        }
        auth_str = self._create_authorization_str(parameters)

        logger.debug("Successfully generated Authorization header.")
        return auth_str

    def _create_nonce(self) -> str:
        """Generate a string with 32 random alphanumeric characters.

        Returns:
            A string value with 32 random alphanumeric characters.
        """
        return str(uuid.uuid4()).replace("-", "")

    def _create_signature(
        self, http_method: str, base_url: str, parameters: dict[str, str]
    ) -> str:
        """Create an oauth signature using request parameters and API keys.

        Args:
            http_method: The method of the HTTP request.
            base_url: The base URL of the API endpoint.
            parameters: A dictionary with the parameters included in the request.

        Returns:
            A string representing the oauth signature.
        """
        # Encode parameters into a string for an OAuth signature base string
        encoded_parameters = {
            quote(k, safe=""): quote(str(v), safe="") for k, v in parameters.items()
        }
        sorted_parameters = sorted(encoded_parameters.items())
        parameter_str = "&".join([f"{k}={v}" for k, v in sorted_parameters])
        signature_base_str = (
            f"{http_method}&{quote(base_url, safe='')}&{quote(parameter_str, safe='')}"
        )
        logger.debug("OAuth signature base string: %s", signature_base_str)

        signing_key = (
            f"{quote(self._x_consumer_secret, safe='')}&"
            f"{quote(self._x_access_token_secret, safe='')}"
        )

        # Calculate signature
        signing_key_bytes = signing_key.encode("UTF-8")
        signature_base_str_bytes = signature_base_str.encode("UTF-8")

        h = hmac.new(signing_key_bytes, signature_base_str_bytes, hashlib.sha1)
        raw_signature_bytes = h.digest()
        oauth_signature = base64.b64encode(raw_signature_bytes).decode("utf-8")

        return oauth_signature

    def _create_authorization_str(self, parameters: dict[str, str]) -> str:
        """Create an authentication string to authenticate requests on the X API.

        Args:
            parameters: A dictionary with the parameters needed to authenticate a
                request.

        Returns:
            An authentication string to be used within requests headers.
        """
        auth_str_builder = [
            f'{quote(k, safe="")}="{quote(str(v), safe="")}"'
            for k, v in parameters.items()
        ]
        return "OAuth " + ", ".join(auth_str_builder)
