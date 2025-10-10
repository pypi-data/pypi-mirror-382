#!/usr/bin/env python3
"""
Session completion script

Completes the current session by:
1. Running quality gates (tests, linting, formatting)
2. Updating work item status
3. Generating session summary
4. Creating git commit
5. Updating project tracking files
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel

from session_dev.core.models import SessionMetrics, SessionSummary, WorkItem
from session_dev.core.work_items import WorkItemManager
from session_dev.utils.file_ops import (
    ensure_directory,
    load_json,
    save_json,
    write_file,
)
from session_dev.utils.git_ops import create_commit, get_changed_files_since

console = Console()


class QualityGate:
    """Represents a single quality gate"""

    def __init__(self, name: str, command: str, blocking: bool = True):
        self.name = name
        self.command = command
        self.blocking = blocking
        self.passed = False
        self.output = ""


class SessionCompleter:
    """Handles session completion"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.session_dir = project_root / ".session"
        self.work_item_manager = WorkItemManager(project_root)
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load session configuration"""
        config_path = self.project_root / ".sessionrc.json"
        if config_path.exists():
            return load_json(config_path)
        return {}

    def complete(
        self,
        item_id: Optional[str] = None,
        force: bool = False,
        no_tests: bool = False,
        no_lint: bool = False,
        no_commit: bool = False,
    ) -> None:
        """Complete the current session"""

        console.print("\n[bold blue]═══ Session Completion ═══[/bold blue]\n")

        # Step 1: Identify current work item
        if item_id:
            work_item = self.work_item_manager.get_work_item(item_id)
            if not work_item:
                console.print(f"[red]Work item not found: {item_id}[/red]\n")
                sys.exit(1)
        else:
            work_item = self.work_item_manager.get_in_progress_work_item()
            if not work_item:
                console.print("[yellow]No work item currently in progress[/yellow]\n")
                sys.exit(1)

        console.print(f"[cyan]Completing: {work_item.id}[/cyan]")
        console.print(f"{work_item.title}\n")

        # Step 2: Run quality gates
        if not force:
            gates_passed = self._run_quality_gates(
                work_item, skip_tests=no_tests, skip_lint=no_lint
            )

            if not gates_passed:
                console.print("\n[red bold]Quality gates failed[/red bold]")
                console.print("Fix issues or use --force to override\n")
                sys.exit(1)

        # Step 3: Get session number
        session_number = work_item.sessions[-1] if work_item.sessions else 1

        # Step 4: Generate session summary
        summary = self._generate_session_summary(work_item, session_number)
        console.print("[green]✓ Session summary generated[/green]")

        # Step 5: Update work item status
        self.work_item_manager.update_work_item(work_item.id, {"status": "completed"})
        console.print("[green]✓ Work item status updated to completed[/green]")

        # Step 6: Save session summary
        self._save_session_summary(summary, session_number)

        # Step 7: Update status_update.json
        self._update_status_file(summary)
        console.print("[green]✓ Status updated[/green]")

        # Step 8: Create git commit
        if not no_commit and self.config.get("git", {}).get("auto_commit", True):
            commit_message = self._generate_commit_message(work_item, summary)
            create_commit(self.project_root, commit_message)
            console.print("[green]✓ Git commit created[/green]")

        # Step 9: Show summary
        self._show_completion_summary(work_item, session_number, summary)

        # Step 10: Suggest next work item
        next_item = self.work_item_manager.get_next_available_work_item()
        if next_item:
            console.print("\n[cyan]Next available work item:[/cyan]")
            console.print(f"  {next_item.id}: {next_item.title}")
            console.print("  Dependencies: ✅ All satisfied\n")

    def _run_quality_gates(
        self, work_item: WorkItem, skip_tests: bool = False, skip_lint: bool = False
    ) -> bool:
        """Run all quality gates"""

        console.print("[bold]Running Quality Gates[/bold]\n")

        gates: list[QualityGate] = []

        # Gate 1: Tests
        if not skip_tests and self.config.get("validation_rules", {}).get(
            "post_session", {}
        ).get("tests_pass", True):
            test_cmd = self.config.get("testing", {}).get("command", "pytest")
            gates.append(QualityGate("Tests", test_cmd, blocking=True))

        # Gate 2: Linting
        if not skip_lint and self.config.get("runtime_standards", {}).get(
            "linting", {}
        ).get("enabled", True):
            lint_cmd = self._get_lint_command()
            if lint_cmd:
                gates.append(QualityGate("Linting", lint_cmd, blocking=True))

        # Gate 3: Formatting
        if (
            self.config.get("runtime_standards", {})
            .get("formatting", {})
            .get("enabled", True)
        ):
            format_cmd = self._get_format_command()
            if format_cmd:
                gates.append(QualityGate("Formatting", format_cmd, blocking=False))

        # Run each gate
        results = {}
        for gate in gates:
            result = self._run_gate(gate)
            results[gate.name] = result

            if not result and gate.blocking:
                console.print(f"[red]✗ {gate.name} failed (blocking)[/red]")
                return False
            elif not result:
                console.print(f"[yellow]⚠  {gate.name} failed (warning)[/yellow]")
            else:
                console.print(f"[green]✓ {gate.name} passed[/green]")

        console.print()
        return all(results.values())

    def _run_gate(self, gate: QualityGate) -> bool:
        """Run a single quality gate"""
        try:
            result = subprocess.run(
                gate.command.split(),
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300,  # 5 minute timeout
            )
            gate.output = result.stdout + result.stderr
            gate.passed = result.returncode == 0
            return gate.passed
        except subprocess.TimeoutExpired:
            gate.output = "Command timed out"
            return False
        except Exception as e:
            gate.output = str(e)
            return False

    def _get_lint_command(self) -> Optional[str]:
        """Get linting command for the project"""
        # Check for Python
        if (self.project_root / "pyproject.toml").exists():
            return "ruff check ."

        # Check for TypeScript/JavaScript
        if (self.project_root / ".eslintrc.json").exists() or (
            self.project_root / ".eslintrc.js"
        ).exists():
            return "eslint ."

        return None

    def _get_format_command(self) -> Optional[str]:
        """Get formatting command for the project"""
        # Check for Python
        if (self.project_root / "pyproject.toml").exists():
            return "black . --check"

        # Check for TypeScript/JavaScript
        if (self.project_root / ".prettierrc").exists():
            return "prettier --check ."

        return None

    def _generate_session_summary(
        self, work_item: WorkItem, session_number: int
    ) -> SessionSummary:
        """Generate session summary"""

        # Get metrics
        changed_files = get_changed_files_since(self.project_root)
        metrics = SessionMetrics(
            files_changed=len(changed_files),
            tests_added=0,  # TODO: Calculate from git diff
            lines_added=0,  # TODO: Calculate from git diff
            lines_removed=0,  # TODO: Calculate from git diff
        )

        # Create summary
        summary = SessionSummary(
            session_id=f"session_{session_number:03d}",
            timestamp=datetime.now(),
            work_items_completed=[work_item.id],
            work_items_started=[],
            achievements=[f"Completed {work_item.title}"],
            challenges_encountered=[],
            next_session_priorities=[],
            documentation_references=[],
            metrics=metrics,
        )

        return summary

    def _save_session_summary(
        self, summary: SessionSummary, session_number: int
    ) -> None:
        """Save session summary to file"""
        history_dir = self.session_dir / "history"
        ensure_directory(history_dir)

        summary_path = history_dir / f"session_{session_number:03d}_summary.md"

        content = f"""# Session {session_number} Summary

{summary.timestamp.strftime("%Y-%m-%d %H:%M:%S")}

## Work Items Completed
{self._format_list(summary.work_items_completed)}

## Achievements
{self._format_list(summary.achievements)}

## Challenges Encountered
{self._format_list(summary.challenges_encountered) if summary.challenges_encountered else "None"}

## Metrics
- Files changed: {summary.metrics.files_changed}
- Tests added: {summary.metrics.tests_added}
- Lines added: {summary.metrics.lines_added}
- Lines removed: {summary.metrics.lines_removed}

## Next Session Priorities
{self._format_list(summary.next_session_priorities) if summary.next_session_priorities else "To be determined"}
"""

        write_file(summary_path, content)

    def _format_list(self, items: list[str]) -> str:
        """Format list items"""
        return "\n".join(f"- {item}" for item in items)

    def _update_status_file(self, summary: SessionSummary) -> None:
        """Update status_update.json"""
        status_path = self.session_dir / "tracking" / "status_update.json"
        save_json(status_path, summary.model_dump())

    def _generate_commit_message(
        self, work_item: WorkItem, summary: SessionSummary
    ) -> str:
        """Generate git commit message"""
        session_num = summary.session_id.split("_")[1]

        message = f"""Session {session_num}: {work_item.title}

{chr(10).join(f'- {achievement}' for achievement in summary.achievements)}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"""

        return message

    def _show_completion_summary(
        self, work_item: WorkItem, session_number: int, summary: SessionSummary
    ) -> None:
        """Show session completion summary"""
        summary_text = f"""
[bold green]Session {session_number} Completed Successfully![/bold green]

[bold]Work Item:[/bold] {work_item.id}
[bold]Title:[/bold] {work_item.title}
[bold]Status:[/bold] Completed ✅

[bold]Metrics:[/bold]
- Files changed: {summary.metrics.files_changed}
- Tests added: {summary.metrics.tests_added}

[bold cyan]Session summary saved[/bold cyan]
"""
        console.print(Panel(summary_text, border_style="green"))


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Complete current session")
    parser.add_argument("--item", type=str, help="Specific work item ID")
    parser.add_argument(
        "--force", action="store_true", help="Force completion (skip quality gates)"
    )
    parser.add_argument("--no-tests", action="store_true", help="Skip test execution")
    parser.add_argument("--no-lint", action="store_true", help="Skip linting")
    parser.add_argument("--no-commit", action="store_true", help="Skip git commit")

    args = parser.parse_args()

    project_root = Path.cwd()
    session_dir = project_root / ".session"

    if not session_dir.exists():
        console.print("[red]Error: Not a session-dev project[/red]", style="bold")
        console.print("Run 'session-dev init' first\n")
        sys.exit(1)

    completer = SessionCompleter(project_root)
    completer.complete(
        item_id=args.item,
        force=args.force,
        no_tests=args.no_tests,
        no_lint=args.no_lint,
        no_commit=args.no_commit,
    )


if __name__ == "__main__":
    main()
