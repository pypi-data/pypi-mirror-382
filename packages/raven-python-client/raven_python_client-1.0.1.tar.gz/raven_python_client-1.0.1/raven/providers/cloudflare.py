"""Cloudflare captcha provider for Turnstile.

Constructs request models for Turnstile and delegates execution to the captcha service.
Only proxy configuration is supported; no additional options are sent.
"""

from typing import Optional

from ..models.captcha import Captcha, Proxy, Retry, CaptchaTaskRequest
from ..models.response import TaskStatusResponse
from ..services.captcha_service import CaptchaService


class CloudflareProvider:
    """Provider exposing methods for Cloudflare Turnstile.

    Offers a synchronous method that builds request models and executes them via the captcha service.
    Returns a `TaskStatusResponse` containing the solution token and task metadata when completed.
    """

    def __init__(self, service: CaptchaService):
        self.service = service

    def Turnstile(
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
        """Creates and solves a Cloudflare Turnstile challenge synchronously.

        Parameters
        website_url: Full URL of the page containing the Turnstile widget.
        website_key: Site key associated with the Turnstile widget.
        proxy_scheme: Default None. Proxy scheme such as http or https.
        proxy_host: Default None. Proxy host used to route the task.
        proxy_port: Default None. Proxy port value as a string.
        proxy_username: Default None. Proxy authentication username.
        proxy_password: Default None. Proxy authentication password.
        max_retry: Default None. Remote retry count when a task fails; service default applies if None.
        poll_interval: Default 1.0 seconds. Interval between status checks while polling.
        timeout: Default None. Waits indefinitely until completion when None.

        Returns
        TaskStatusResponse holding the task id, timestamps, and solution token when status equals completed.

        Raises
        RavenError subclass mapped from API error ids when task creation fails.
        TaskFailedError if the task reports failed status or the polling times out.
        """

        captcha = Captcha(websiteURL=website_url, websiteKey=website_key, type="Turnstile")
        proxy = Proxy(
            scheme=proxy_scheme,
            host=proxy_host,
            port=proxy_port,
            username=proxy_username,
            password=proxy_password,
        )
        retry = Retry(max_retry=max_retry)
        req = CaptchaTaskRequest(captcha=captcha, options=None, proxy=proxy, retry=retry)
        created = self.service.create_task(req)
        return self.service.wait_for_completion(created.data.task_id, poll_interval=poll_interval, timeout=timeout)