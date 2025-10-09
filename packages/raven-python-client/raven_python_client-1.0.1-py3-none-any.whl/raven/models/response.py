"""Response models for create task and status polling.

Captures error shapes, task metadata, and solution details.
"""

from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class Error:
    """Error information returned by the API."""

    id: str
    message: str


@dataclass
class TaskData:
    """Metadata returned upon successful task creation."""

    task_id: str
    status: str
    created_at: str


@dataclass
class ConcurrencyInfo:
    """Information about current concurrency limits and usage."""

    current: int
    max: int
    remaining: int


@dataclass
class CreateTaskResponse:
    """Response shape for task creation requests."""

    success: bool
    error: Optional[Error] = None
    data: Optional[TaskData] = None
    concurrency_info: Optional[ConcurrencyInfo] = None

    @staticmethod
    def from_json(data: dict) -> "CreateTaskResponse":
        error_obj = None
        if data.get("error"):
            error_obj = Error(id=data["error"]["id"], message=data["error"]["message"]) 
        task_data = None
        if data.get("data"):
            td = data["data"]
            task_data = TaskData(task_id=td.get("task_id"), status=td.get("status"), created_at=td.get("created_at"))
        concurrency = None
        if data.get("concurrency_info"):
            ci = data["concurrency_info"]
            concurrency = ConcurrencyInfo(current=ci.get("current"), max=ci.get("max"), remaining=ci.get("remaining"))
        return CreateTaskResponse(success=bool(data.get("success")), error=error_obj, data=task_data, concurrency_info=concurrency)


@dataclass
class Solution:
    """Captcha solution returned upon task completion."""

    token: Optional[str]
    duration: Optional[Any]


@dataclass
class TaskStatusResponse:
    """Response shape for task status polling."""

    success: bool
    status: str
    created_at: Optional[str]
    task_id: str
    solution: Solution

    @staticmethod
    def from_json(data: dict) -> "TaskStatusResponse":
        sol = data.get("solution") or {}
        solution = Solution(token=sol.get("token"), duration=sol.get("duration"))
        return TaskStatusResponse(
            success=bool(data.get("success")),
            status=str(data.get("status")),
            created_at=data.get("created_at"),
            task_id=str(data.get("task_id")),
            solution=solution,
        )