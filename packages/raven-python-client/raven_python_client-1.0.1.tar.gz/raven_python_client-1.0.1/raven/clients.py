"""Client interfaces for raven-py.

Provides synchronous and asynchronous clients sharing the same core service implementation.
"""

import asyncio
from typing import Optional

from .http.client import HttpClient
from .services.captcha_service import CaptchaService
from .providers.google import GoogleProvider
from .providers.cloudflare import CloudflareProvider
from .models.response import TaskStatusResponse


class RavenClient:
    """Synchronous client for interacting with the Raven captcha API."""

    def __init__(self, api_key: str, base_url: str = "https://ai.ravens.best", timeout: Optional[float] = 30.0):
        self.http = HttpClient(base_url=base_url, api_key=api_key, timeout=timeout)
        self._captcha_service = CaptchaService(self.http)
        self.google = GoogleProvider(self._captcha_service)
        self.cloudflare = CloudflareProvider(self._captcha_service)


class AsyncGoogleProvider:
    """Async wrapper around the synchronous Google provider using asyncio.to_thread."""

    def __init__(self, sync_provider: GoogleProvider):
        self._sync = sync_provider

    async def RecaptchaV2(
        self,
        *,
        website_url: str,
        website_key: str,
        invisible: Optional[bool] = None,
        enterprise: Optional[bool] = None,
        action: Optional[str] = None,
        proxy_scheme: Optional[str] = None,
        proxy_host: Optional[str] = None,
        proxy_port: Optional[str] = None,
        proxy_username: Optional[str] = None,
        proxy_password: Optional[str] = None,
        max_retry: Optional[int] = None,
        poll_interval: float = 1.0,
        timeout: Optional[float] = None,
    ) -> TaskStatusResponse:
        """Creates and solves a Google reCAPTCHA v2 challenge asynchronously.

        Parameters
        website_url: Full URL of the page containing the captcha widget.
        website_key: Site key associated with the captcha widget.
        invisible: Default None. When True, uses the invisible widget variant.
        enterprise: Default None. When True, enables enterprise mode when supported.
        action: Default None. Expected action string used by some site configurations.
        proxy_scheme: Default None. Proxy scheme such as http or https.
        proxy_host: Default None. Proxy host used to route the task.
        proxy_port: Default None. Proxy port value as a string.
        proxy_username: Default None. Proxy authentication username.
        proxy_password: Default None. Proxy authentication password.
        max_retry: Default None. Remote retry count when a task fails; service default applies if None.
        poll_interval: Default 1.0 seconds. Interval between status checks while polling.
        timeout: Default None. Waits indefinitely until completion when None.

        Returns
        TaskStatusResponse containing the solution token and metadata upon completion.

        Raises
        RavenError subclass mapped from API error ids on creation failure.
        TaskFailedError if task reports failed status or polling times out.
        """

        return await asyncio.to_thread(
            self._sync.RecaptchaV2,
            website_url=website_url,
            website_key=website_key,
            invisible=invisible,
            enterprise=enterprise,
            action=action,
            proxy_scheme=proxy_scheme,
            proxy_host=proxy_host,
            proxy_port=proxy_port,
            proxy_username=proxy_username,
            proxy_password=proxy_password,
            max_retry=max_retry,
            poll_interval=poll_interval,
            timeout=timeout,
        )

    async def RecaptchaV3(
        self,
        *,
        website_url: str,
        website_key: str,
        action: Optional[str] = None,
        enterprise: Optional[bool] = None,
        proxy_scheme: Optional[str] = None,
        proxy_host: Optional[str] = None,
        proxy_port: Optional[str] = None,
        proxy_username: Optional[str] = None,
        proxy_password: Optional[str] = None,
        max_retry: Optional[int] = None,
        poll_interval: float = 1.0,
        timeout: Optional[float] = None,
    ) -> TaskStatusResponse:
        """Creates and solves a Google reCAPTCHA v3 challenge asynchronously.

        Parameters
        website_url: Full URL of the page containing the captcha widget.
        website_key: Site key associated with the captcha widget.
        action: Default None. Expected action string used by v3 scoring flow.
        enterprise: Default None. When True, enables enterprise mode when supported.
        proxy_scheme: Default None. Proxy scheme such as http or https.
        proxy_host: Default None. Proxy host used to route the task.
        proxy_port: Default None. Proxy port value as a string.
        proxy_username: Default None. Proxy authentication username.
        proxy_password: Default None. Proxy authentication password.
        max_retry: Default None. Remote retry count when a task fails; service default applies if None.
        poll_interval: Default 1.0 seconds. Interval between status checks while polling.
        timeout: Default None. Waits indefinitely until completion when None.

        Returns
        TaskStatusResponse containing the solution token and metadata upon completion.

        Raises
        RavenError subclass mapped from API error ids on creation failure.
        TaskFailedError if task reports failed status or polling times out.
        """

        return await asyncio.to_thread(
            self._sync.RecaptchaV3,
            website_url=website_url,
            website_key=website_key,
            action=action,
            enterprise=enterprise,
            proxy_scheme=proxy_scheme,
            proxy_host=proxy_host,
            proxy_port=proxy_port,
            proxy_username=proxy_username,
            proxy_password=proxy_password,
            max_retry=max_retry,
            poll_interval=poll_interval,
            timeout=timeout,
        )


class AsyncCloudflareProvider:
    """Async wrapper around the synchronous Cloudflare provider using asyncio.to_thread."""

    def __init__(self, sync_provider: CloudflareProvider):
        self._sync = sync_provider

    async def Turnstile(
        self,
        *,
        website_url: str,
        website_key: str,
        proxy_scheme: Optional[str] = None,
        proxy_host: Optional[str] = None,
        proxy_port: Optional[str] = None,
        proxy_username: Optional[str] = None,
        proxy_password: Optional[str] = None,
        max_retry: Optional[int] = None,
        poll_interval: float = 1.0,
        timeout: Optional[float] = None,
    ) -> TaskStatusResponse:
        """Creates and solves a Cloudflare Turnstile challenge asynchronously."""

        return await asyncio.to_thread(
            self._sync.Turnstile,
            website_url=website_url,
            website_key=website_key,
            proxy_scheme=proxy_scheme,
            proxy_host=proxy_host,
            proxy_port=proxy_port,
            proxy_username=proxy_username,
            proxy_password=proxy_password,
            max_retry=max_retry,
            poll_interval=poll_interval,
            timeout=timeout,
        )


class AsyncRavenClient:
    """Asynchronous client exposing async methods by delegating to a synchronous core via threads."""

    def __init__(self, api_key: str, base_url: str = "https://ai.ravens.best", timeout: Optional[float] = 30.0):
        self._sync_client = RavenClient(api_key=api_key, base_url=base_url, timeout=timeout)
        self.google = AsyncGoogleProvider(self._sync_client.google)
        self.cloudflare = AsyncCloudflareProvider(self._sync_client.cloudflare)