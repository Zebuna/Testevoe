from typing import Optional

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Project, Task, TaskPriority, TaskStatus, TaskStatusHistory
from app.schemas import ProjectCreate, TaskCreate, TaskUpdateStatus
from app.status_transitions import is_allowed_transition

async def create_project(db: AsyncSession, payload: ProjectCreate) -> Project:
    project = Project(name=payload.name, owner_id=payload.owner_id)
    db.add(project)
    await db.flush()
    await db.refresh(project)
    return project

async def get_project_by_id(db: AsyncSession, project_id: int) -> Optional[Project]:
    result = await db.execute(select(Project).where(Project.id == project_id))
    return result.scalar_one_or_none()

async def create_task(db: AsyncSession, payload: TaskCreate) -> Task:
    task = Task(
        project_id=payload.project_id,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        status=TaskStatus.created,
        author_id=payload.author_id,
        assignee_id=payload.assignee_id,
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task

async def get_task_by_id(db: AsyncSession, task_id: int) -> Optional[Task]:
    result = await db.execute(select(Task).where(Task.id == task_id))
    return result.scalar_one_or_none()

async def get_tasks(
    db: AsyncSession,
    *,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    assignee_id: Optional[int] = None,
    page: int = 1,
    size: int = 20,
    sort_by: Optional[str] = None,
    sort_order: str = "desc",
) -> tuple[list[Task], int]:
    q = select(Task)
    count_q = select(func.count()).select_from(Task)
    if status is not None:
        q = q.where(Task.status == status)
        count_q = count_q.where(Task.status == status)
    if priority is not None:
        q = q.where(Task.priority == priority)
        count_q = count_q.where(Task.priority == priority)
    if assignee_id is not None:
        q = q.where(Task.assignee_id == assignee_id)
        count_q = count_q.where(Task.assignee_id == assignee_id)

    total_result = await db.execute(count_q)
    total = total_result.scalar_one()

    if sort_by == "created_at":
        if sort_order == "asc":
            q = q.order_by(Task.created_at.asc())
        else:
            q = q.order_by(Task.created_at.desc())
    elif sort_by == "priority":
        priority_order = case(
            (Task.priority == TaskPriority.critical, 1),
            (Task.priority == TaskPriority.high, 2),
            (Task.priority == TaskPriority.medium, 3),
            (Task.priority == TaskPriority.low, 4),
            else_=5,
        )
        if sort_order == "asc":
            q = q.order_by(priority_order.asc())
        else:
            q = q.order_by(priority_order.desc())
    else:
        q = q.order_by(Task.created_at.desc())

    offset = (page - 1) * size
    q = q.offset(offset).limit(size)
    result = await db.execute(q)
    items = list(result.scalars().all())
    return items, total

async def update_task_status(
    db: AsyncSession, task: Task, payload: TaskUpdateStatus
) -> tuple[Task, Optional[TaskStatusHistory]]:
    if not is_allowed_transition(task.status, payload.status):
        return task, None 

    history_entry = TaskStatusHistory(
        task_id=task.id,
        from_status=task.status,
        to_status=payload.status,
        changed_by_id=payload.changed_by_id,
    )
    db.add(history_entry)
    task.status = payload.status
    await db.flush()
    await db.refresh(task)
    return task, history_entry

async def get_task_status_history(db: AsyncSession, task_id: int) -> list[TaskStatusHistory]:
    result = await db.execute(
        select(TaskStatusHistory)
        .where(TaskStatusHistory.task_id == task_id)
        .order_by(TaskStatusHistory.changed_at.asc())
    )
    return list(result.scalars().all())
