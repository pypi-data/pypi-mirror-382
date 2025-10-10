#!/usr/bin/env python3
"""
Session initialization script

Initializes a new development session by:
1. Validating git repository is clean
2. Finding next available work item
3. Generating comprehensive briefing
4. Updating work item status to in_progress
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel

from session_dev.core.models import WorkItem, WorkItemStatus
from session_dev.core.work_items import WorkItemManager
from session_dev.utils.file_ops import ensure_directory, read_file, write_file
from session_dev.utils.git_ops import is_git_clean

console = Console()


class SessionInitializer:
    """Handles session initialization"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.session_dir = project_root / ".session"
        self.work_item_manager = WorkItemManager(project_root)

    def initialize(
        self,
        auto_next: bool = False,
        item_id: Optional[str] = None,
        skip_git_check: bool = False,
    ) -> None:
        """Initialize a new session"""

        console.print("\n[bold blue]═══ Session Initialization ═══[/bold blue]\n")

        # Step 1: Validate environment
        if not skip_git_check:
            if not self._validate_git_clean():
                console.print("[red]✗ Working directory not clean[/red]", style="bold")
                console.print("\nUse --skip-git-check to bypass (not recommended)\n")
                sys.exit(1)
            console.print("[green]✓ Git working directory clean[/green]")

        # Step 2: Check for existing in-progress work item
        existing = self.work_item_manager.get_in_progress_work_item()
        if existing:
            console.print(
                f"\n[yellow]⚠  Work item already in progress: {existing.id}[/yellow]"
            )
            console.print(f"   {existing.title}")
            console.print("\nComplete the current session first or force start.\n")
            sys.exit(1)

        # Step 3: Select work item
        if auto_next:
            work_item = self.work_item_manager.get_next_available_work_item()
            if not work_item:
                console.print("[yellow]No work items available[/yellow]")
                console.print("All dependencies may not be satisfied.\n")
                sys.exit(1)
        elif item_id:
            work_item = self.work_item_manager.get_work_item(item_id)
            if not work_item:
                console.print(f"[red]Work item not found: {item_id}[/red]\n")
                sys.exit(1)

            # Check dependencies
            if not self.work_item_manager._are_dependencies_satisfied(work_item):
                console.print(f"[red]✗ Dependencies not satisfied for {item_id}[/red]")
                self._show_unsatisfied_dependencies(work_item)
                sys.exit(1)
        else:
            console.print("[red]Must specify --next or --item <id>[/red]\n")
            sys.exit(1)

        console.print(f"[green]✓ Work item selected: {work_item.id}[/green]")
        console.print(f"  {work_item.title}\n")

        # Step 4: Get next session number
        session_number = self._get_next_session_number()

        # Step 5: Generate briefing
        briefing_path = self._generate_briefing(work_item, session_number)
        console.print("[green]✓ Briefing generated[/green]")

        # Step 6: Update work item status
        self.work_item_manager.update_work_item(
            work_item.id,
            {
                "status": "in_progress",
                "sessions": work_item.sessions + [session_number],
            },
        )
        console.print("[green]✓ Work item status updated to in_progress[/green]")

        # Step 7: Show summary
        self._show_session_summary(work_item, session_number, briefing_path)

    def _validate_git_clean(self) -> bool:
        """Validate git repository is clean"""
        return is_git_clean(self.project_root)

    def _show_unsatisfied_dependencies(self, work_item: WorkItem) -> None:
        """Show which dependencies are not satisfied"""
        console.print("\nUnsatisfied dependencies:")
        for dep_id in work_item.dependencies:
            dep_item = self.work_item_manager.get_work_item(dep_id)
            if dep_item and dep_item.status != WorkItemStatus.COMPLETED:
                console.print(
                    f"  ✗ {dep_id}: {dep_item.title} (status: {dep_item.status})"
                )

    def _get_next_session_number(self) -> int:
        """Get the next session number"""
        history_dir = self.session_dir / "history"
        if not history_dir.exists():
            return 1

        session_files = list(history_dir.glob("session_*_summary.md"))
        if not session_files:
            return 1

        # Extract session numbers
        numbers = []
        for f in session_files:
            try:
                num = int(f.stem.split("_")[1])
                numbers.append(num)
            except (IndexError, ValueError):
                continue

        return max(numbers) + 1 if numbers else 1

    def _generate_briefing(self, work_item: WorkItem, session_number: int) -> Path:
        """Generate comprehensive session briefing"""
        briefing_dir = self.session_dir / "briefings"
        ensure_directory(briefing_dir)

        briefing_path = briefing_dir / f"session_{session_number:03d}_briefing.md"

        # Load specification if exists
        spec_content = ""
        if work_item.specification_path:
            spec_path = self.project_root / work_item.specification_path
            if spec_path.exists():
                spec_content = read_file(spec_path)

        # Get dependency status
        dep_status = self._format_dependencies(work_item)

        # Get relevant learnings
        learnings = self._get_relevant_learnings(work_item)

        # Get previous session notes
        prev_notes = self._format_previous_notes(work_item)

        # Generate briefing content
        content = f"""# Session {session_number}: {work_item.title}

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Quick Overview
- **Work Item**: {work_item.id}
- **Type**: {work_item.type}
- **Priority**: {work_item.priority}
- **Status**: {work_item.status}
- **Milestone**: {work_item.milestone or "None"}

## Dependencies
{dep_status}

## Objectives
{self._format_objectives(work_item)}

## Specification
{spec_content if spec_content else "No specification provided"}

## Previous Session Notes
{prev_notes}

## Implementation Checklist
{self._format_checklist(work_item)}

## Success Criteria
{self._format_success_criteria(work_item)}

## Related Files
{self._format_related_files(work_item)}

## Relevant Learnings
{learnings}

## Next Steps
1. Review this briefing thoroughly
2. Run validation: `session-dev session validate`
3. Begin implementation
4. Update documentation as you go
5. Run tests frequently
6. Complete session: `session-dev session complete`

---
**Commands:**
- Status: `session-dev session status`
- Validate: `session-dev session validate`
- Complete: `session-dev session complete`
"""

        write_file(briefing_path, content)
        return briefing_path

    def _format_dependencies(self, work_item: WorkItem) -> str:
        """Format dependency status"""
        if not work_item.dependencies:
            return "No dependencies"

        lines = []
        for dep_id in work_item.dependencies:
            dep_item = self.work_item_manager.get_work_item(dep_id)
            if dep_item:
                status_icon = (
                    "✅" if dep_item.status == WorkItemStatus.COMPLETED else "⏳"
                )
                session_info = ""
                if dep_item.sessions:
                    session_info = f" (session_{dep_item.sessions[-1]:03d})"
                lines.append(f"{status_icon} {dep_id}: {dep_item.title}{session_info}")
            else:
                lines.append(f"❓ {dep_id}: Unknown work item")

        return "\n".join(lines)

    def _format_objectives(self, work_item: WorkItem) -> str:
        """Format work item objectives"""
        if work_item.outputs:
            return "\n".join(f"- {output}" for output in work_item.outputs)
        return "No specific objectives defined"

    def _format_previous_notes(self, work_item: WorkItem) -> str:
        """Format previous session notes"""
        if not work_item.session_notes:
            return "This is the first session for this work item"

        lines = []
        for session_id, notes in work_item.session_notes.items():
            lines.append(f"**{session_id}**: {notes}")

        return "\n".join(lines)

    def _format_checklist(self, work_item: WorkItem) -> str:
        """Format implementation checklist"""
        items = [
            "Implement core functionality",
            "Write unit tests",
            "Update documentation",
            "Review code quality",
        ]

        if work_item.type == "feature":
            items.insert(1, "Add integration tests")

        return "\n".join(f"- [ ] {item}" for item in items)

    def _format_success_criteria(self, work_item: WorkItem) -> str:
        """Format success criteria"""
        criteria = work_item.validation_criteria
        lines = []

        if criteria.tests_pass:
            lines.append("- All tests passing")

        if criteria.coverage_min:
            lines.append(f"- Test coverage ≥ {criteria.coverage_min}%")

        if criteria.linting_pass:
            lines.append("- Code linting passes")

        if criteria.documentation_required:
            lines.append("- Documentation updated")

        return "\n".join(lines) if lines else "No specific criteria defined"

    def _format_related_files(self, work_item: WorkItem) -> str:
        """Format related files"""
        lines = []

        if work_item.implementation_paths:
            lines.append("**Implementation:**")
            lines.extend(f"- {path}" for path in work_item.implementation_paths)

        if work_item.test_paths:
            lines.append("\n**Tests:**")
            lines.extend(f"- {path}" for path in work_item.test_paths)

        return "\n".join(lines) if lines else "No files specified"

    def _get_relevant_learnings(self, work_item: WorkItem) -> str:
        """Get relevant learnings for this work item"""
        # TODO: Implement learning lookup
        return "No relevant learnings found"

    def _show_session_summary(
        self, work_item: WorkItem, session_number: int, briefing_path: Path
    ) -> None:
        """Show session initialization summary"""
        summary = f"""
[bold green]Session {session_number} Initialized Successfully![/bold green]

[bold]Work Item:[/bold] {work_item.id}
[bold]Title:[/bold] {work_item.title}
[bold]Type:[/bold] {work_item.type}
[bold]Priority:[/bold] {work_item.priority}

[bold]Briefing:[/bold] {briefing_path.relative_to(self.project_root)}

[bold cyan]Ready to begin development[/bold cyan]
"""
        console.print(Panel(summary, border_style="green"))


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Initialize a new session")
    parser.add_argument(
        "--next", action="store_true", help="Auto-select next available work item"
    )
    parser.add_argument("--item", type=str, help="Specific work item ID")
    parser.add_argument(
        "--skip-git-check", action="store_true", help="Skip git clean check"
    )

    args = parser.parse_args()

    project_root = Path.cwd()
    session_dir = project_root / ".session"

    if not session_dir.exists():
        console.print("[red]Error: Not a session-dev project[/red]", style="bold")
        console.print("Run 'session-dev init' first\n")
        sys.exit(1)

    initializer = SessionInitializer(project_root)
    initializer.initialize(
        auto_next=args.next,
        item_id=args.item,
        skip_git_check=args.skip_git_check,
    )


if __name__ == "__main__":
    main()
