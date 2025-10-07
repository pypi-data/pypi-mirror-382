class XifyError(Exception):
    """A base exception for general library errors."""


class ConfigError(XifyError):
    """Raise for configuration related errors."""


class RequestError(XifyError):
    """Raised for errors during the HTTP request process."""


class APIError(XifyError):
    """Raised for errors returned by the X API."""
