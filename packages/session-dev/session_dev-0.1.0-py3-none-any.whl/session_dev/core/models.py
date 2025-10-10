"""
Core data models for Session-Driven Development
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class WorkItemStatus(str, Enum):
    """Status of a work item"""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class WorkItemType(str, Enum):
    """Type of work item"""

    FEATURE = "feature"
    BUG = "bug"
    REFACTOR = "refactor"
    SETUP = "setup"
    SECURITY = "security"
    SPIKE = "spike"
    PERFORMANCE = "performance"
    DOCUMENTATION = "documentation"


class Priority(str, Enum):
    """Priority level"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ValidationCriteria(BaseModel):
    """Validation requirements for a work item"""

    tests_pass: bool = True
    coverage_min: Optional[int] = None
    linting_pass: bool = True
    documentation_required: bool = False
    regression_test_required: bool = False
    security_scan_required: bool = False


class WorkItemMetadata(BaseModel):
    """Metadata about a work item"""

    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    time_estimate: Optional[str] = None
    actual_time: Optional[str] = None


class WorkItem(BaseModel):
    """A single unit of work to be completed"""

    id: str
    type: WorkItemType
    title: str
    status: WorkItemStatus = WorkItemStatus.NOT_STARTED
    priority: Priority = Priority.MEDIUM

    sessions: list[int] = Field(default_factory=list)
    milestone: Optional[str] = None

    dependencies: list[str] = Field(default_factory=list)
    dependents: list[str] = Field(default_factory=list)

    specification_path: Optional[str] = None
    implementation_paths: list[str] = Field(default_factory=list)
    test_paths: list[str] = Field(default_factory=list)

    outputs: list[str] = Field(default_factory=list)
    validation_criteria: ValidationCriteria = Field(default_factory=ValidationCriteria)
    metadata: WorkItemMetadata = Field(default_factory=WorkItemMetadata)
    session_notes: dict[str, str] = Field(default_factory=dict)


class Milestone(BaseModel):
    """A collection of related work items"""

    id: str
    name: str
    work_items: list[str] = Field(default_factory=list)
    completed: int = 0
    target_date: Optional[str] = None
    dependencies: list[str] = Field(default_factory=list)


class SessionMetrics(BaseModel):
    """Metrics from a completed session"""

    files_changed: int = 0
    tests_added: int = 0
    lines_added: int = 0
    lines_removed: int = 0


class SessionSummary(BaseModel):
    """Summary of a completed session"""

    session_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    work_items_completed: list[str] = Field(default_factory=list)
    work_items_started: list[str] = Field(default_factory=list)

    achievements: list[str] = Field(default_factory=list)
    challenges_encountered: list[str] = Field(default_factory=list)
    next_session_priorities: list[str] = Field(default_factory=list)

    documentation_references: list[str] = Field(default_factory=list)
    metrics: SessionMetrics = Field(default_factory=SessionMetrics)


class LearningType(str, Enum):
    """Type of learning"""

    ARCHITECTURE_PATTERN = "architecture_pattern"
    GOTCHA = "gotcha"
    BEST_PRACTICE = "best_practice"
    TECHNICAL_DEBT = "technical_debt"
    PERFORMANCE_INSIGHT = "performance_insight"


class Learning(BaseModel):
    """A captured piece of project knowledge"""

    type: LearningType
    content: str
    description: Optional[str] = None
    context: Optional[str] = None
    applies_to: list[str] = Field(default_factory=list)
    learned_in: str  # session_id
    example: Optional[str] = None
    rationale: Optional[str] = None

    # For patterns/practices
    established_in: Optional[str] = None
    violations: int = 0

    # For gotchas
    solution: Optional[str] = None
    affected_sessions: list[str] = Field(default_factory=list)
    resolution_session: Optional[str] = None

    # For technical debt
    location: Optional[str] = None
    severity: Optional[str] = None
    planned_resolution: Optional[str] = None
    workaround: Optional[str] = None
    impact: Optional[str] = None

    # For performance insights
    metric: Optional[str] = None
    measured_in: Optional[str] = None
    action_taken: Optional[str] = None
    configuration: Optional[str] = None

    # Library-specific
    library: Optional[str] = None
    library_version: Optional[str] = None
    verified_via: Optional[str] = None
    verified_date: Optional[str] = None
    documentation_url: Optional[str] = None


class StackChangeType(str, Enum):
    """Type of stack change"""

    ADDITION = "addition"
    VERSION_UPGRADE = "version_upgrade"
    REMOVAL = "removal"
    CONFIGURATION_CHANGE = "configuration_change"


class StackUpdate(BaseModel):
    """A change to the technology stack"""

    timestamp: datetime = Field(default_factory=datetime.now)
    session: str
    change_type: StackChangeType
    component: str
    technology: str
    reasoning: str
    alternatives_considered: list[str] = Field(default_factory=list)
    selection_rationale: Optional[str] = None
    breaking_changes: list[str] = Field(default_factory=list)
    migration_notes: Optional[str] = None


class TreeChangeType(str, Enum):
    """Type of project structure change"""

    DIRECTORY_ADDED = "directory_added"
    FILE_MOVED = "file_moved"
    BRANCH_SEPARATION = "branch_separation"
    DIRECTORY_REMOVED = "directory_removed"
    FILE_REMOVED = "file_removed"


class TreeUpdate(BaseModel):
    """A change to project structure"""

    timestamp: datetime = Field(default_factory=datetime.now)
    session: str
    change_type: TreeChangeType
    path: Optional[str] = None
    from_path: Optional[str] = None
    to_path: Optional[str] = None
    reasoning: str
    contains: list[str] = Field(default_factory=list)
    architecture_impact: Optional[str] = None
    breaking_changes: list[str] = Field(default_factory=list)
    migration_commits: list[str] = Field(default_factory=list)
    old_location: Optional[str] = None
    new_structure: Optional[str] = None
    refactoring_approach: Optional[str] = None
    tests_updated: bool = False


class ProjectConfig(BaseModel):
    """Project configuration from .sessionrc.json"""

    framework_version: str = "1.0.0"

    project_name: str
    project_type: str = "web_application"
    work_item_model: str = "feature_based"
    description: Optional[str] = None

    session_start_trigger: str = "@session-start"
    session_end_trigger: str = "@session-end"
    auto_briefing: bool = True

    validation_rules: dict[str, Any] = Field(default_factory=dict)
    work_item_types: dict[str, Any] = Field(default_factory=dict)
    runtime_standards: dict[str, Any] = Field(default_factory=dict)

    testing_framework: str = "pytest"
    testing_command: str = "pytest"
    coverage_min: int = 80

    git_auto_commit: bool = True
    git_require_clean: bool = True
