"""Custom exceptions for raven-py.

Maps API error identifiers to rich exception classes for explicit handling.
"""

class RavenError(Exception):
    """Base exception for raven-py errors."""


class InvalidFieldsError(RavenError):
    """Invalid fields in the main request."""


class InvalidCaptchaFieldsError(RavenError):
    """Invalid fields inside the captcha object."""


class InvalidCaptchaTypeError(RavenError):
    """Unsupported captcha type requested."""


class InvalidOptionsFieldsError(RavenError):
    """Invalid fields inside options object."""


class InvalidProxyFieldsError(RavenError):
    """Invalid fields inside proxy object."""


class ProxySchemeRequiredError(RavenError):
    """Proxy scheme must be provided."""


class ProxyHostRequiredError(RavenError):
    """Proxy host must be provided."""


class ProxyPortRequiredError(RavenError):
    """Proxy port must be provided."""


class ProxyPasswordRequiredError(RavenError):
    """Proxy password required when username is provided."""


class InvalidRetryFieldsError(RavenError):
    """Invalid fields in retry policy."""


class ApiKeyRequiredError(RavenError):
    """API key missing or not provided."""


class CaptchaDataRequiredError(RavenError):
    """Captcha data missing in the request."""


class WebsiteUrlRequiredError(RavenError):
    """Website URL is required."""


class WebsiteKeyRequiredError(RavenError):
    """Website key is required."""


class CaptchaTypeRequiredError(RavenError):
    """Captcha type is required."""


class InvalidApiKeyError(RavenError):
    """API key is invalid."""


class NoActiveSubscriptionError(RavenError):
    """No active subscription found for the account."""


class MaxConcurrencyReachedError(RavenError):
    """Maximum concurrency reached."""


class OtherConcurrencyError(RavenError):
    """Other concurrency error encountered."""


class InternalServerError(RavenError):
    """Internal server error returned by the API."""


class TaskFailedError(RavenError):
    """Task failed while polling for completion."""


ERROR_ID_MAP = {
    "INVALID_FIELDS": InvalidFieldsError,
    "INVALID_CAPTCHA_FIELDS": InvalidCaptchaFieldsError,
    "INVALID_CAPTCHA_TYPE": InvalidCaptchaTypeError,
    "INVALID_OPTIONS_FIELDS": InvalidOptionsFieldsError,
    "INVALID_PROXY_FIELDS": InvalidProxyFieldsError,
    "PROXY_SCHEME_REQUIRED": ProxySchemeRequiredError,
    "PROXY_HOST_REQUIRED": ProxyHostRequiredError,
    "PROXY_PORT_REQUIRED": ProxyPortRequiredError,
    "PROXY_PASSWORD_REQUIRED": ProxyPasswordRequiredError,
    "INVALID_RETRY_FIELDS": InvalidRetryFieldsError,
    "API_KEY_REQUIRED": ApiKeyRequiredError,
    "CAPTCHA_DATA_REQUIRED": CaptchaDataRequiredError,
    "WEBSITE_URL_REQUIRED": WebsiteUrlRequiredError,
    "WEBSITE_KEY_REQUIRED": WebsiteKeyRequiredError,
    "CAPTCHA_TYPE_REQUIRED": CaptchaTypeRequiredError,
    "INVALID_API_KEY": InvalidApiKeyError,
    "NO_ACTIVE_SUBSCRIPTION": NoActiveSubscriptionError,
    "MAX_CONCURRENCY_REACHED": MaxConcurrencyReachedError,
    "OTHER_CONCURRENCY_ERROR": OtherConcurrencyError,
    "INTERNAL_SERVER_ERROR": InternalServerError,
}

def raise_for_error_id(error_id: str, message: str) -> None:
    """Raises a mapped exception for a given error id with a message."""

    exc = ERROR_ID_MAP.get(error_id, RavenError)
    raise exc(message)