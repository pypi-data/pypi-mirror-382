"""Google captcha provider with specific Recaptcha variants.

Constructs request models and delegates execution to the captcha service.
"""

from typing import Optional

from ..models.captcha import Captcha, Options, Proxy, Retry, CaptchaTaskRequest
from ..models.response import TaskStatusResponse
from ..services.captcha_service import CaptchaService


class GoogleProvider:
    """Provider exposing methods for Google reCAPTCHA variants.

    Offers synchronous methods that build request models and execute them via the captcha service.
    Each method returns a `TaskStatusResponse` containing the solution token and task metadata when completed.
    """

    def __init__(self, service: CaptchaService):
        self.service = service

    def RecaptchaV2(
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
        """Creates and solves a Google reCAPTCHA v2 challenge synchronously.

        Parameters
        website_url: Full URL of the page containing the captcha widget.
        website_key: Site key associated with the captcha widget.
        invisible: Default None. When True, uses the invisible widget variant.
        enterprise: Default None. When True, enables enterprise mode when supported.
        action: Default None. Expected action value used by some site configurations.
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

        captcha = Captcha(websiteURL=website_url, websiteKey=website_key, type="RecaptchaV2")
        options = Options(invisible=invisible, enterprise=enterprise, action=action)
        proxy = Proxy(scheme=proxy_scheme, host=proxy_host, port=proxy_port, username=proxy_username, password=proxy_password)
        retry = Retry(max_retry=max_retry)
        req = CaptchaTaskRequest(captcha=captcha, options=options, proxy=proxy, retry=retry)
        created = self.service.create_task(req)
        return self.service.wait_for_completion(created.data.task_id, poll_interval=poll_interval, timeout=timeout)

    def RecaptchaV3(
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
        """Creates and solves a Google reCAPTCHA v3 challenge synchronously.

        Parameters
        website_url: Full URL of the page containing the captcha widget.
        website_key: Site key associated with the captcha widget.
        action: Default None. Expected action string used by reCAPTCHA v3 scoring flow.
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
        TaskStatusResponse holding the task id, timestamps, and solution token when status equals completed.

        Raises
        RavenError subclass mapped from API error ids when task creation fails.
        TaskFailedError if the task reports failed status or the polling times out.
        """

        captcha = Captcha(websiteURL=website_url, websiteKey=website_key, type="RecaptchaV3")
        options = Options(action=action, enterprise=enterprise)
        proxy = Proxy(scheme=proxy_scheme, host=proxy_host, port=proxy_port, username=proxy_username, password=proxy_password)
        retry = Retry(max_retry=max_retry)
        req = CaptchaTaskRequest(captcha=captcha, options=options, proxy=proxy, retry=retry)
        created = self.service.create_task(req)
        return self.service.wait_for_completion(created.data.task_id, poll_interval=poll_interval, timeout=timeout)