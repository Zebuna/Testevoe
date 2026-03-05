from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import create_task, get_task_by_id, get_tasks, get_task_status_history, update_task_status
from app.database import get_db
from app.models import TaskPriority, TaskStatus
from app.schemas import (
    StatusHistoryEntry,
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdateStatus,
)
from app.status_transitions import get_transition_error_message

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse)
async def task_create(payload: TaskCreate, db: AsyncSession = Depends(get_db)):
    task = await create_task(db, payload)
    return TaskResponse.model_validate(task)


@router.get("/", response_model=TaskListResponse)
async def task_list(
    db: AsyncSession = Depends(get_db),
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    assignee_id: Optional[int] = Query(None, description="Filter by assignee (bonus)"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: Optional[str] = Query(None, description="Sort by: created_at | priority"),
    sort_order: str = Query("desc", description="Sort order: asc | desc"),
):
    if sort_by and sort_by not in ("created_at", "priority"):
        sort_by = None
    if sort_order not in ("asc", "desc"):
        sort_order = "desc"
    items, total = await get_tasks(
        db,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return TaskListResponse(
        items=[TaskResponse.model_validate(t) for t in items],
        total=total,
        page=page,
        size=size,
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def task_get(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task)


@router.patch("/{task_id}/status", response_model=TaskResponse)
async def task_update_status(
    task_id: int,
    payload: TaskUpdateStatus,
    db: AsyncSession = Depends(get_db),
):
    task = await get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    updated_task, _ = await update_task_status(db, task, payload)
    if updated_task.status != payload.status:
        msg = get_transition_error_message(task.status, payload.status)
        raise HTTPException(status_code=400, detail=msg)
    return TaskResponse.model_validate(updated_task)


@router.get("/{task_id}/history", response_model=list[StatusHistoryEntry])
async def task_history(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    history = await get_task_status_history(db, task_id)
    return [StatusHistoryEntry.model_validate(h) for h in history]
