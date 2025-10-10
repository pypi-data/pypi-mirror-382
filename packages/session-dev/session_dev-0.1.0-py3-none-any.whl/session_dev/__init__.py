"""
Session-Driven Development Framework

A comprehensive methodology for AI-augmented software development with
perfect context continuity, enforced quality standards, and accumulated
institutional knowledge.
"""

__version__ = "0.1.0"
__author__ = "Session-Dev Project"

from session_dev.core.manager import SessionManager
from session_dev.core.models import (
    Learning,
    SessionSummary,
    StackUpdate,
    TreeUpdate,
    WorkItem,
)
from session_dev.core.work_items import WorkItemManager

__all__ = [
    "WorkItem",
    "SessionSummary",
    "Learning",
    "StackUpdate",
    "TreeUpdate",
    "SessionManager",
    "WorkItemManager",
    "__version__",
]
