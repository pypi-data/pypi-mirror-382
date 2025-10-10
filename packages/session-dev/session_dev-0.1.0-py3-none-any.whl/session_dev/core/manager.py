"""Main session manager"""

from pathlib import Path
from typing import Optional

from session_dev.core.models import WorkItem
from session_dev.core.work_items import WorkItemManager


class SessionManager:
    """Main interface for session management"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.work_item_manager = WorkItemManager(project_root)

    def start_session(
        self, auto_next: bool = False, item_id: Optional[str] = None
    ) -> WorkItem:
        """Start a new session"""
        from session_dev.scripts.session_init import SessionInitializer

        initializer = SessionInitializer(self.project_root)
        initializer.initialize(auto_next=auto_next, item_id=item_id)

        # Return the work item that was started
        return self.work_item_manager.get_in_progress_work_item()

    def complete_session(self, item_id: Optional[str] = None) -> None:
        """Complete current session"""
        from session_dev.scripts.session_complete import SessionCompleter

        completer = SessionCompleter(self.project_root)
        completer.complete(item_id=item_id)

    def get_work_items(self, **filters):
        """Get work items with filters"""
        return self.work_item_manager.list_work_items(**filters)

    def get_ready_work_items(self):
        """Get work items ready to start (dependencies satisfied)"""
        return [
            item
            for item in self.work_item_manager.list_work_items()
            if self.work_item_manager._are_dependencies_satisfied(item)
        ]
