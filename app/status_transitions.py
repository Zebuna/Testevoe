"""
Valid status transitions:
- created -> in_progress | cancelled
- in_progress -> review | created
- review -> done | in_progress
- done -> (none)
- cancelled -> (none)
"""
from app.models import TaskStatus

ALLOWED_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.created: {TaskStatus.in_progress, TaskStatus.cancelled},
    TaskStatus.in_progress: {TaskStatus.review, TaskStatus.created},
    TaskStatus.review: {TaskStatus.done, TaskStatus.in_progress},
    TaskStatus.done: set(),
    TaskStatus.cancelled: set(),
}

def is_allowed_transition(from_status: TaskStatus, to_status: TaskStatus) -> bool:
    return to_status in ALLOWED_TRANSITIONS.get(from_status, set())

def get_transition_error_message(from_status: TaskStatus, to_status: TaskStatus) -> str:
    allowed = ALLOWED_TRANSITIONS.get(from_status, set())
    if not allowed:
        return f"Из статуса '{from_status.value}' переходы запрещены."
    allowed_list = ", ".join(s.value for s in allowed)
    return f"Переход из '{from_status.value}' в '{to_status.value}' запрещён. Допустимые переходы: {allowed_list}."
