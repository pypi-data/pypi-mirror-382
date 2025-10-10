"""Work item management"""

from pathlib import Path
from typing import Optional

from session_dev.core.models import (
    Milestone,
    WorkItem,
    WorkItemStatus,
)
from session_dev.utils.file_ops import backup_file, load_json, save_json


class WorkItemManager:
    """Manages work items for a project"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.work_items_path = (
            project_root / ".session" / "tracking" / "work_items.json"
        )
        self._data: Optional[dict] = None

    def load(self) -> dict:
        """Load work items data"""
        if self._data is None:
            if self.work_items_path.exists():
                self._data = load_json(self.work_items_path)
            else:
                self._data = self._create_empty_structure()
        return self._data

    def save(self) -> None:
        """Save work items data"""
        if self._data is not None:
            # Create backup before saving
            if self.work_items_path.exists():
                backup_file(self.work_items_path)

            # Update metadata
            self._update_metadata()

            save_json(self.work_items_path, self._data)

    def _create_empty_structure(self) -> dict:
        """Create empty work items structure"""
        return {
            "metadata": {
                "total_items": 0,
                "completed": 0,
                "in_progress": 0,
                "blocked": 0,
                "last_updated": None,
            },
            "milestones": {},
            "work_items": {},
        }

    def _update_metadata(self) -> None:
        """Update metadata counts"""
        from datetime import datetime

        work_items = self._data.get("work_items", {})

        self._data["metadata"] = {
            "total_items": len(work_items),
            "completed": sum(
                1 for item in work_items.values() if item["status"] == "completed"
            ),
            "in_progress": sum(
                1 for item in work_items.values() if item["status"] == "in_progress"
            ),
            "blocked": sum(
                1 for item in work_items.values() if item["status"] == "blocked"
            ),
            "last_updated": datetime.now().isoformat(),
        }

    def get_work_item(self, item_id: str) -> Optional[WorkItem]:
        """Get a work item by ID"""
        data = self.load()
        item_data = data.get("work_items", {}).get(item_id)

        if item_data:
            return WorkItem(**item_data)
        return None

    def list_work_items(
        self, status: Optional[WorkItemStatus] = None, milestone: Optional[str] = None
    ) -> list[WorkItem]:
        """List work items with optional filters"""
        data = self.load()
        items = []

        for item_data in data.get("work_items", {}).values():
            item = WorkItem(**item_data)

            if status and item.status != status:
                continue

            if milestone and item.milestone != milestone:
                continue

            items.append(item)

        return items

    def add_work_item(self, work_item: WorkItem) -> None:
        """Add a new work item"""
        data = self.load()

        if work_item.id in data["work_items"]:
            raise ValueError(f"Work item already exists: {work_item.id}")

        data["work_items"][work_item.id] = work_item.model_dump()
        self._data = data
        self.save()

    def update_work_item(self, item_id: str, updates: dict) -> Optional[WorkItem]:
        """Update a work item"""
        data = self.load()

        if item_id not in data["work_items"]:
            return None

        # Validate status transitions
        old_status = data["work_items"][item_id].get("status")
        new_status = updates.get("status")

        if new_status and old_status != new_status:
            if not self._is_valid_status_transition(old_status, new_status):
                raise ValueError(
                    f"Invalid status transition: {old_status} -> {new_status}"
                )

        data["work_items"][item_id].update(updates)
        self._data = data
        self.save()

        return WorkItem(**data["work_items"][item_id])

    def _is_valid_status_transition(self, old: str, new: str) -> bool:
        """Check if status transition is valid"""
        valid_transitions = {
            "not_started": ["in_progress", "blocked"],
            "in_progress": ["completed", "blocked", "not_started"],
            "completed": ["in_progress"],  # Re-opening
            "blocked": ["in_progress", "not_started"],
        }

        return new in valid_transitions.get(old, [])

    def get_next_available_work_item(self) -> Optional[WorkItem]:
        """Find next work item where all dependencies are satisfied"""
        data = self.load()
        work_items = data.get("work_items", {})

        for item_data in work_items.values():
            item = WorkItem(**item_data)

            # Skip if not ready
            if item.status != WorkItemStatus.NOT_STARTED:
                continue

            # Check dependencies
            if self._are_dependencies_satisfied(item):
                return item

        return None

    def _are_dependencies_satisfied(self, work_item: WorkItem) -> bool:
        """Check if all dependencies are completed"""
        if not work_item.dependencies:
            return True

        data = self.load()
        work_items = data.get("work_items", {})

        for dep_id in work_item.dependencies:
            dep_item = work_items.get(dep_id)
            if not dep_item or dep_item.get("status") != "completed":
                return False

        return True

    def get_in_progress_work_item(self) -> Optional[WorkItem]:
        """Get the currently in-progress work item"""
        items = self.list_work_items(status=WorkItemStatus.IN_PROGRESS)
        return items[0] if items else None

    def add_milestone(self, milestone: Milestone) -> None:
        """Add a milestone"""
        data = self.load()

        if milestone.id in data["milestones"]:
            raise ValueError(f"Milestone already exists: {milestone.id}")

        data["milestones"][milestone.id] = milestone.model_dump()
        self._data = data
        self.save()

    def get_milestone(self, milestone_id: str) -> Optional[Milestone]:
        """Get a milestone by ID"""
        data = self.load()
        milestone_data = data.get("milestones", {}).get(milestone_id)

        if milestone_data:
            return Milestone(**milestone_data)
        return None

    def get_dependency_graph(self) -> dict[str, list[str]]:
        """Get dependency graph for all work items"""
        data = self.load()
        graph = {}

        for item_id, item_data in data.get("work_items", {}).items():
            graph[item_id] = item_data.get("dependencies", [])

        return graph
