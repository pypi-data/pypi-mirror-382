#!/usr/bin/env python3
"""
Session validation script

Validates the project environment and session state:
1. Git repository validation
2. File structure validation
3. Work item data integrity
4. Dependency validation
5. Environment validation
"""

import argparse
import sys
from pathlib import Path

from rich.console import Console

from session_dev.core.work_items import WorkItemManager
from session_dev.utils.file_ops import load_json
from session_dev.utils.git_ops import get_repo, is_git_clean

console = Console()


class SessionValidator:
    """Validates session environment and state"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.session_dir = project_root / ".session"
        self.work_item_manager = WorkItemManager(project_root)
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate_all(self, fix_issues: bool = False) -> bool:
        """Run all validation checks"""
        console.print("\n[bold blue]═══ Session Validation ═══[/bold blue]\n")

        checks = [
            ("Git Repository", self._validate_git),
            ("Directory Structure", self._validate_structure),
            ("Work Items Data", self._validate_work_items),
            ("Dependencies", self._validate_dependencies),
            ("Configuration", self._validate_config),
        ]

        all_passed = True

        for check_name, check_func in checks:
            console.print(f"[cyan]Checking {check_name}...[/cyan]")
            passed = check_func()

            if passed:
                console.print(f"[green]✓ {check_name} valid[/green]\n")
            else:
                console.print(f"[red]✗ {check_name} failed[/red]\n")
                all_passed = False

        # Show summary
        self._show_summary()

        if fix_issues and (self.errors or self.warnings):
            console.print("\n[yellow]Attempting to fix issues...[/yellow]\n")
            self._fix_issues()

        return all_passed

    def _validate_git(self) -> bool:
        """Validate git repository"""
        try:
            # Check if git repo exists
            get_repo(self.project_root)

            # Check if clean (warning only)
            if not is_git_clean(self.project_root):
                self.warnings.append("Git working directory has uncommitted changes")

            return True

        except Exception as e:
            self.errors.append(f"Git validation failed: {e}")
            return False

    def _validate_structure(self) -> bool:
        """Validate directory structure"""
        required_dirs = [
            self.session_dir / "tracking",
            self.session_dir / "briefings",
            self.session_dir / "history",
            self.session_dir / "specs",
        ]

        required_files = [
            self.project_root / ".sessionrc.json",
            self.session_dir / "tracking" / "work_items.json",
        ]

        all_valid = True

        for directory in required_dirs:
            if not directory.exists():
                self.errors.append(
                    f"Missing directory: {directory.relative_to(self.project_root)}"
                )
                all_valid = False

        for file_path in required_files:
            if not file_path.exists():
                self.errors.append(
                    f"Missing file: {file_path.relative_to(self.project_root)}"
                )
                all_valid = False

        return all_valid

    def _validate_work_items(self) -> bool:
        """Validate work items data integrity"""
        try:
            data = self.work_item_manager.load()

            # Check structure
            if "work_items" not in data:
                self.errors.append("work_items.json missing 'work_items' key")
                return False

            if "metadata" not in data:
                self.warnings.append("work_items.json missing 'metadata' key")

            # Validate each work item
            work_items = data.get("work_items", {})

            for item_id, item_data in work_items.items():
                # Check required fields
                required_fields = ["id", "type", "title", "status"]
                for field in required_fields:
                    if field not in item_data:
                        self.errors.append(
                            f"Work item {item_id} missing field: {field}"
                        )

                # Validate ID matches
                if item_data.get("id") != item_id:
                    self.errors.append(
                        f"Work item ID mismatch: {item_id} vs {item_data.get('id')}"
                    )

            # Check metadata counts match
            metadata = data.get("metadata", {})
            actual_total = len(work_items)
            reported_total = metadata.get("total_items", 0)

            if actual_total != reported_total:
                self.warnings.append(
                    f"Metadata total_items mismatch: {reported_total} reported, {actual_total} actual"
                )

            return len([e for e in self.errors if "Work item" in e]) == 0

        except Exception as e:
            self.errors.append(f"Failed to validate work items: {e}")
            return False

    def _validate_dependencies(self) -> bool:
        """Validate work item dependencies"""
        try:
            data = self.work_item_manager.load()
            work_items = data.get("work_items", {})

            all_valid = True

            for item_id, item_data in work_items.items():
                dependencies = item_data.get("dependencies", [])

                for dep_id in dependencies:
                    # Check dependency exists
                    if dep_id not in work_items:
                        self.errors.append(
                            f"Work item {item_id} has non-existent dependency: {dep_id}"
                        )
                        all_valid = False

                    # Check for circular dependencies
                    if self._has_circular_dependency(item_id, dep_id, work_items):
                        self.errors.append(
                            f"Circular dependency detected: {item_id} <-> {dep_id}"
                        )
                        all_valid = False

            return all_valid

        except Exception as e:
            self.errors.append(f"Failed to validate dependencies: {e}")
            return False

    def _has_circular_dependency(
        self, item_id: str, dep_id: str, work_items: dict, visited: set = None
    ) -> bool:
        """Check for circular dependencies"""
        if visited is None:
            visited = set()

        if dep_id == item_id:
            return True

        if dep_id in visited:
            return False

        visited.add(dep_id)

        dep_item = work_items.get(dep_id, {})
        for next_dep in dep_item.get("dependencies", []):
            if self._has_circular_dependency(item_id, next_dep, work_items, visited):
                return True

        return False

    def _validate_config(self) -> bool:
        """Validate configuration file"""
        try:
            config_path = self.project_root / ".sessionrc.json"

            if not config_path.exists():
                self.errors.append("Missing .sessionrc.json")
                return False

            config = load_json(config_path)

            # Check required sections
            required_sections = ["project", "session_protocol", "validation_rules"]

            for section in required_sections:
                if section not in config:
                    self.warnings.append(f"Configuration missing section: {section}")

            return True

        except Exception as e:
            self.errors.append(f"Failed to validate configuration: {e}")
            return False

    def _show_summary(self) -> None:
        """Show validation summary"""
        console.print("\n[bold]Validation Summary[/bold]\n")

        if self.errors:
            console.print(f"[red bold]Errors: {len(self.errors)}[/red bold]")
            for error in self.errors:
                console.print(f"  [red]✗ {error}[/red]")
            console.print()

        if self.warnings:
            console.print(f"[yellow bold]Warnings: {len(self.warnings)}[/yellow bold]")
            for warning in self.warnings:
                console.print(f"  [yellow]⚠  {warning}[/yellow]")
            console.print()

        if not self.errors and not self.warnings:
            console.print("[green bold]✓ All validations passed![/green bold]\n")

    def _fix_issues(self) -> None:
        """Attempt to fix common issues"""
        fixed_count = 0

        # Fix missing directories
        required_dirs = [
            self.session_dir / "tracking",
            self.session_dir / "briefings",
            self.session_dir / "history",
            self.session_dir / "specs",
        ]

        for directory in required_dirs:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                console.print(
                    f"[green]✓ Created directory: {directory.relative_to(self.project_root)}[/green]"
                )
                fixed_count += 1

        # Fix metadata counts
        try:
            self.work_item_manager.load()
            self.work_item_manager._update_metadata()
            self.work_item_manager.save()
            console.print("[green]✓ Updated metadata counts[/green]")
            fixed_count += 1
        except Exception:
            pass

        if fixed_count > 0:
            console.print(f"\n[green]Fixed {fixed_count} issue(s)[/green]\n")
        else:
            console.print("\n[yellow]No issues could be automatically fixed[/yellow]\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Validate session environment")
    parser.add_argument(
        "--fix-issues", action="store_true", help="Attempt to fix issues"
    )
    parser.add_argument("--item", type=str, help="Validate specific work item")

    args = parser.parse_args()

    project_root = Path.cwd()
    session_dir = project_root / ".session"

    if not session_dir.exists():
        console.print("[red]Error: Not a session-dev project[/red]", style="bold")
        console.print("Run 'session-dev init' first\n")
        sys.exit(1)

    validator = SessionValidator(project_root)
    success = validator.validate_all(fix_issues=args.fix_issues)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
