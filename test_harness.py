"""Acceptance and boundary tests for the TaskAnalyzer SDD contract."""
from datetime import datetime
import pytest
from src.task_analyzer import TaskValidationError, analyze_tasks

D = datetime.fromisoformat

def task(identifier: int, status: str, created: str, due: str, completed: str | None = None, priority: str = "high") -> dict:
    """Create deterministic task test fixtures."""
    return {"id": identifier, "title": f"Tarefa {identifier}", "status": status,
            "created_at": D(created), "due_date": D(due),
            "completed_at": D(completed) if completed else None, "priority": priority}

def test_success_and_priority() -> None:
    """Verify counts, rates, durations and priority metrics."""
    data = [task(1, "completed", "2026-01-01T00:00:00", "2026-01-02T00:00:00", "2026-01-01T12:00:00", "high"),
            task(2, "completed", "2026-01-01T00:00:00", "2026-01-02T00:00:00", "2026-01-03T00:00:00", "low"),
            task(3, "pending", "2026-01-01T00:00:00", "2026-01-02T00:00:00")]
    result = analyze_tasks(data, D("2026-01-04T00:00:00"))
    assert result["total_tasks"] == 3
    assert result["completed_tasks"] == 2
    assert result["pending_tasks"] == 1
    assert result["overdue_tasks"] == 2
    assert result["completion_rate"] == 66.67
    assert result["overdue_rate"] == 66.67
    assert result["average_completion_hours"] == 30.0
    assert result["average_completion_hours_by_priority"] == {"high": 12.0, "low": 48.0}

def test_invalid_due_date() -> None:
    """Reject deadlines before creation."""
    with pytest.raises(TaskValidationError, match="due_date"):
        analyze_tasks([task(1, "pending", "2026-01-03T00:00:00", "2026-01-02T00:00:00")])

def test_invalid_completion_date() -> None:
    """Reject completion before creation."""
    with pytest.raises(TaskValidationError, match="completed_at"):
        analyze_tasks([task(1, "completed", "2026-01-03T00:00:00", "2026-01-04T00:00:00", "2026-01-02T00:00:00")])

def test_invalid_status() -> None:
    """Reject unsupported statuses."""
    with pytest.raises(TaskValidationError, match="status"):
        analyze_tasks([task(1, "cancelled", "2026-01-01T00:00:00", "2026-01-02T00:00:00")])

def test_empty() -> None:
    """Return zeros for empty inputs."""
    result = analyze_tasks([], D("2026-01-04T00:00:00"))
    assert result["total_tasks"] == result["completed_tasks"] == result["pending_tasks"] == 0
    assert result["overdue_rate"] == result["completion_rate"] == result["average_completion_hours"] == 0.0
    assert result["average_completion_hours_by_priority"] == {}

def test_pending_only() -> None:
    """Avoid division by zero when no tasks are completed."""
    result = analyze_tasks([task(1, "pending", "2026-01-01T00:00:00", "2026-01-02T00:00:00")], D("2026-01-04T00:00:00"))
    assert result["average_completion_hours"] == 0.0
    assert result["overdue_tasks"] == 1

def test_duplicate_id() -> None:
    """Reject duplicate identifiers."""
    with pytest.raises(TaskValidationError, match="duplicado"):
        analyze_tasks([task(1, "pending", "2026-01-01T00:00:00", "2026-01-02T00:00:00")]*2)
