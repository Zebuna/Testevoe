from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.models import TaskPriority, TaskStatus

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    owner_id: int

class ProjectResponse(BaseModel):
    id: int
    name: str
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    project_id: int
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.medium
    author_id: int
    assignee_id: Optional[int] = None

class TaskUpdateStatus(BaseModel):
    status: TaskStatus
    changed_by_id: int

class TaskResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str] = None
    priority: TaskPriority
    status: TaskStatus
    author_id: int
    assignee_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    total: int
    page: int
    size: int

class StatusHistoryEntry(BaseModel):
    id: int
    task_id: int
    from_status: TaskStatus
    to_status: TaskStatus
    changed_by_id: int
    changed_at: datetime

    class Config:
        from_attributes = True

TaskStatusLiteral = Literal["created", "in_progress", "review", "done", "cancelled"]
TaskPriorityLiteral = Literal["low", "medium", "high", "critical"]
SortByLiteral = Literal["created_at", "priority"]

def parse_sort(sort_by: Optional[str]) -> Optional[SortByLiteral]:
    if sort_by is None:
        return None
    v = sort_by.strip().lower()
    if v in ("created_at", "priority"):
        return v
    return None
