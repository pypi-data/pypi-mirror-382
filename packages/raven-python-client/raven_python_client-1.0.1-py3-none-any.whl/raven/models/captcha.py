"""Data models for captcha task creation request.

Defines structures for captcha specification, options, proxy configuration, and retry policy.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Captcha:
    """Captcha description including website information and type."""

    websiteURL: str
    websiteKey: str
    type: str


@dataclass
class Options:
    """Optional captcha solving parameters."""

    invisible: Optional[bool] = None
    enterprise: Optional[bool] = None
    action: Optional[str] = None


@dataclass
class Proxy:
    """Proxy configuration for task execution."""

    scheme: Optional[str] = None
    host: Optional[str] = None
    port: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


@dataclass
class Retry:
    """Retry policy handled by the remote service."""

    max_retry: Optional[int] = None


@dataclass
class CaptchaTaskRequest:
    """Complete request payload for creating a captcha task."""

    captcha: Captcha
    options: Optional[Options] = None
    proxy: Optional[Proxy] = None
    retry: Optional[Retry] = None

    def to_payload(self) -> dict:
        """Converts the request to a serializable dictionary payload."""

        payload: dict = {
            "captcha": {
                "websiteURL": self.captcha.websiteURL,
                "websiteKey": self.captcha.websiteKey,
                "type": self.captcha.type,
            }
        }
        if self.options is not None:
            payload["options"] = {}
            if self.options.invisible is not None:
                payload["options"]["invisible"] = self.options.invisible
            if self.options.enterprise is not None:
                payload["options"]["enterprise"] = self.options.enterprise
            if self.options.action is not None:
                payload["options"]["action"] = self.options.action
        if self.proxy is not None:
            payload["proxy"] = {}
            if self.proxy.scheme is not None:
                payload["proxy"]["scheme"] = self.proxy.scheme
            if self.proxy.host is not None:
                payload["proxy"]["host"] = self.proxy.host
            if self.proxy.port is not None:
                payload["proxy"]["port"] = self.proxy.port
            if self.proxy.username is not None:
                payload["proxy"]["username"] = self.proxy.username
            if self.proxy.password is not None:
                payload["proxy"]["password"] = self.proxy.password
        if self.retry is not None:
            payload["retry"] = {}
            if self.retry.max_retry is not None:
                payload["retry"]["max_retry"] = self.retry.max_retry
        return payload