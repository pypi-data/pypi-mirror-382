"""Captcha service encapsulating task creation and status polling.

Uses the provided HTTP client to communicate with the API and raises mapped exceptions.
"""

import time
from typing import Optional

from ..http.client import HttpClient
from ..models.captcha import CaptchaTaskRequest
from ..models.response import CreateTaskResponse, TaskStatusResponse
from ..exceptions import raise_for_error_id, TaskFailedError


class CaptchaService:
    """Service responsible for captcha task lifecycle operations."""

    def __init__(self, http: HttpClient):
        self.http = http

    def create_task(self, request: CaptchaTaskRequest) -> CreateTaskResponse:
        """Creates a captcha task and returns the parsed creation response."""

        data = self.http.post_json("/v1/captcha/task/create", request.to_payload())
        parsed = CreateTaskResponse.from_json(data)
        if not parsed.success and parsed.error is not None:
            raise_for_error_id(parsed.error.id, parsed.error.message)
        return parsed

    def get_status(self, task_id: str) -> TaskStatusResponse:
        """Retrieves the current status for a given task id."""

        data = self.http.get_json("/v1/captcha/task/status", {"task_id": task_id})
        return TaskStatusResponse.from_json(data)

    def wait_for_completion(self, task_id: str, poll_interval: float = 1.0, timeout: Optional[float] = None) -> TaskStatusResponse:
        """Polls the task until it completes or fails, optionally with a timeout."""

        start = time.time()
        while True:
            status = self.get_status(task_id)
            if status.status == "completed":
                return status
            if status.status == "failed":
                raise TaskFailedError("Task failed while processing")
            if timeout is not None and (time.time() - start) > timeout:
                raise TaskFailedError("Task polling timed out")
            time.sleep(poll_interval)