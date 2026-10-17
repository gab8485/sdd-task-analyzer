"""TaskAnalyzer: deterministic productivity metrics for structured tasks."""
from __future__ import annotations
from datetime import date, datetime
import logging
from typing import Any

logger = logging.getLogger(__name__)

class TaskValidationError(ValueError):
    """Raised when a task violates the SDD business contract."""

def _as_datetime(value: Any, field: str) -> datetime:
    """Convert date/datetime inputs into comparable datetime values."""
    if isinstance(value, datetime):
        return value.replace(tzinfo=None)
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    raise TaskValidationError(f"{field} deve ser date ou datetime")

def _validate_task(task: Any, ids: set[int | str]) -> dict[str, Any]:
    """Validate a single task and normalize date fields."""
    if not isinstance(task, dict):
        raise TaskValidationError("Cada tarefa deve ser um dicionário")
    required = ("id", "title", "status", "created_at", "due_date")
    if any(k not in task for k in required):
        raise TaskValidationError("Campos obrigatórios ausentes")
    identifier = task["id"]
    if type(identifier) not in (int, str) or identifier in ids:
        raise TaskValidationError("id inválido ou duplicado")
    ids.add(identifier)
    if not isinstance(task["title"], str) or not task["title"].strip():
        raise TaskValidationError("title deve ser texto não vazio")
    if task["status"] not in ("pending", "completed"):
        raise TaskValidationError("status deve ser pending ou completed")
    created = _as_datetime(task["created_at"], "created_at")
    due = _as_datetime(task["due_date"], "due_date")
    if due < created:
        raise TaskValidationError("due_date não pode anteceder created_at")
    completed = task.get("completed_at")
    if task["status"] == "completed":
        if completed is None:
            raise TaskValidationError("completed_at é obrigatório para tarefas concluídas")
        completed = _as_datetime(completed, "completed_at")
        if completed < created:
            raise TaskValidationError("completed_at não pode anteceder created_at")
    elif completed is not None:
        raise TaskValidationError("completed_at deve ser None para tarefa pendente")
    return {**task, "created_at": created, "due_date": due, "completed_at": completed}

def analyze_tasks(tasks: list[dict[str, Any]], reference_date: date | datetime | None = None) -> dict[str, Any]:
    """Validate tasks and return SDD metrics, including optional priority averages."""
    if not isinstance(tasks, list):
        raise TaskValidationError("tasks deve ser uma lista")
    reference = _as_datetime(reference_date if reference_date is not None else date.today(), "reference_date")
    ids: set[int | str] = set()
    validated = [_validate_task(t, ids) for t in tasks]
    total = len(validated)
    completed = [t for t in validated if t["status"] == "completed"]
    overdue = sum((t["completed_at"] > t["due_date"]) if t["status"] == "completed" else (t["due_date"] < reference) for t in validated)
    durations = [(t["completed_at"] - t["created_at"]).total_seconds() / 3600 for t in completed]
    priority_groups: dict[str, list[float]] = {}
    for t, hours in zip(completed, durations):
        if "priority" in t:
            if not isinstance(t["priority"], str) or not t["priority"].strip():
                raise TaskValidationError("priority deve ser texto não vazio quando informado")
            priority_groups.setdefault(t["priority"], []).append(hours)
    result = {
        "total_tasks": total,
        "completed_tasks": len(completed),
        "pending_tasks": total - len(completed),
        "overdue_tasks": overdue,
        "completion_rate": round(100 * len(completed) / total, 2) if total else 0.0,
        "overdue_rate": round(100 * overdue / total, 2) if total else 0.0,
        "average_completion_hours": round(sum(durations) / len(durations), 2) if durations else 0.0,
        "average_completion_hours_by_priority": {p: round(sum(v) / len(v), 2) for p, v in priority_groups.items()},
    }
    logger.info("TaskAnalyzer: total=%d completed=%d overdue=%d", total, len(completed), overdue)
    return result
