"""
Command-line interface for Session-Driven Development
"""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Session-Driven Development CLI

    A framework for AI-augmented software development with perfect context continuity.
    """
    pass


@main.command()
@click.option(
    "--preset",
    type=click.Choice(["web_app", "library", "pipeline", "microservices"]),
    default="web_app",
    help="Project type preset",
)
def init(preset: str):
    """Initialize Session-Driven Development in current project"""
    from session_dev.core.initializer import ProjectInitializer

    project_root = Path.cwd()
    initializer = ProjectInitializer(project_root)

    try:
        initializer.initialize(preset=preset)
        console.print("\n[green]✓ Session-Dev initialized successfully![/green]\n")
        console.print("Next steps:")
        console.print("1. Review .sessionrc.json configuration")
        console.print("2. Create docs/vision.md with project goals")
        console.print("3. Define work items: session-dev work-item create")
        console.print("4. Start first session: @session-start\n")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


# Work Item Management
@main.group(name="work-item")
def work_item():
    """Manage work items"""
    pass


@work_item.command(name="create")
def work_item_create():
    """Create a new work item interactively"""
    from session_dev.core.models import Priority, WorkItem, WorkItemType
    from session_dev.core.work_items import WorkItemManager

    project_root = Path.cwd()
    manager = WorkItemManager(project_root)

    console.print("\n[bold blue]Create New Work Item[/bold blue]\n")

    # Collect information
    item_id = click.prompt("Work item ID (e.g., feature_oauth)", type=str)
    title = click.prompt("Title", type=str)
    item_type = click.prompt(
        "Type",
        type=click.Choice([t.value for t in WorkItemType]),
        default="feature",
    )
    priority = click.prompt(
        "Priority", type=click.Choice([p.value for p in Priority]), default="medium"
    )

    deps_input = click.prompt(
        "Dependencies (comma-separated IDs, or press Enter for none)",
        default="",
        type=str,
    )
    dependencies = [d.strip() for d in deps_input.split(",") if d.strip()]

    milestone = click.prompt("Milestone (optional)", default="", type=str)

    # Create work item
    work_item = WorkItem(
        id=item_id,
        type=item_type,
        title=title,
        priority=priority,
        dependencies=dependencies,
        milestone=milestone if milestone else None,
    )

    try:
        manager.add_work_item(work_item)
        console.print(f"\n[green]✓ Work item created: {item_id}[/green]\n")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        sys.exit(1)


@work_item.command(name="list")
@click.option("--status", type=str, help="Filter by status")
@click.option("--milestone", type=str, help="Filter by milestone")
def work_item_list(status: Optional[str], milestone: Optional[str]):
    """List all work items"""
    from session_dev.core.models import WorkItemStatus
    from session_dev.core.work_items import WorkItemManager

    project_root = Path.cwd()
    manager = WorkItemManager(project_root)

    status_filter = WorkItemStatus(status) if status else None
    items = manager.list_work_items(status=status_filter, milestone=milestone)

    if not items:
        console.print("\n[yellow]No work items found[/yellow]\n")
        return

    table = Table(title="Work Items")
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Type")
    table.add_column("Status")
    table.add_column("Priority")

    for item in items:
        table.add_row(
            item.id,
            item.title,
            item.type.value,
            item.status.value,
            item.priority.value,
        )

    console.print()
    console.print(table)
    console.print()


@work_item.command(name="show")
@click.argument("item_id")
def work_item_show(item_id: str):
    """Show details of a work item"""
    from session_dev.core.work_items import WorkItemManager

    project_root = Path.cwd()
    manager = WorkItemManager(project_root)

    item = manager.get_work_item(item_id)

    if not item:
        console.print(f"\n[red]Work item not found: {item_id}[/red]\n")
        sys.exit(1)

    console.print(f"\n[bold cyan]{item.title}[/bold cyan]")
    console.print(f"ID: {item.id}")
    console.print(f"Type: {item.type.value}")
    console.print(f"Status: {item.status.value}")
    console.print(f"Priority: {item.priority.value}")

    if item.dependencies:
        console.print("\nDependencies:")
        for dep in item.dependencies:
            console.print(f"  - {dep}")

    if item.sessions:
        console.print(f"\nSessions: {', '.join(str(s) for s in item.sessions)}")

    console.print()


@work_item.command(name="update")
@click.argument("item_id")
@click.option("--status", type=str, help="New status")
@click.option("--priority", type=str, help="New priority")
def work_item_update(item_id: str, status: Optional[str], priority: Optional[str]):
    """Update a work item"""
    from session_dev.core.work_items import WorkItemManager

    project_root = Path.cwd()
    manager = WorkItemManager(project_root)

    updates = {}
    if status:
        updates["status"] = status
    if priority:
        updates["priority"] = priority

    if not updates:
        console.print("\n[yellow]No updates specified[/yellow]\n")
        return

    try:
        manager.update_work_item(item_id, updates)
        console.print(f"\n[green]✓ Work item updated: {item_id}[/green]\n")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        sys.exit(1)


# Session Management
@main.group(name="session")
def session():
    """Manage development sessions"""
    pass


@session.command(name="start")
@click.option("--next", "auto_next", is_flag=True, help="Auto-select next work item")
@click.option("--item", type=str, help="Specific work item ID")
@click.option("--skip-git-check", is_flag=True, help="Skip git clean check")
def session_start(auto_next: bool, item: Optional[str], skip_git_check: bool):
    """Start a new session"""
    from session_dev.scripts.session_init import SessionInitializer

    project_root = Path.cwd()
    initializer = SessionInitializer(project_root)

    try:
        initializer.initialize(
            auto_next=auto_next, item_id=item, skip_git_check=skip_git_check
        )
    except SystemExit:
        raise
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        sys.exit(1)


@session.command(name="complete")
@click.option("--item", type=str, help="Specific work item ID")
@click.option("--force", is_flag=True, help="Force completion (skip quality gates)")
@click.option("--no-tests", is_flag=True, help="Skip test execution")
@click.option("--no-lint", is_flag=True, help="Skip linting")
@click.option("--no-commit", is_flag=True, help="Skip git commit")
def session_complete(
    item: Optional[str], force: bool, no_tests: bool, no_lint: bool, no_commit: bool
):
    """Complete current session"""
    from session_dev.scripts.session_complete import SessionCompleter

    project_root = Path.cwd()
    completer = SessionCompleter(project_root)

    try:
        completer.complete(
            item_id=item,
            force=force,
            no_tests=no_tests,
            no_lint=no_lint,
            no_commit=no_commit,
        )
    except SystemExit:
        raise
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        sys.exit(1)


@session.command(name="status")
def session_status():
    """Show current session status"""
    from session_dev.core.work_items import WorkItemManager

    project_root = Path.cwd()
    manager = WorkItemManager(project_root)

    current = manager.get_in_progress_work_item()

    if current:
        console.print("\n[bold]Current Session:[/bold]")
        console.print(f"Work Item: {current.id}")
        console.print(f"Title: {current.title}")
        console.print(f"Type: {current.type.value}")
        console.print(f"Sessions: {', '.join(str(s) for s in current.sessions)}\n")
    else:
        console.print("\n[yellow]No session in progress[/yellow]\n")

        # Show next available
        next_item = manager.get_next_available_work_item()
        if next_item:
            console.print("[bold]Next available:[/bold]")
            console.print(f"{next_item.id}: {next_item.title}\n")


# Documentation Commands
@main.group(name="docs")
def docs():
    """Documentation management"""
    pass


@docs.command(name="stack-scan")
def docs_stack_scan():
    """Scan and document technology stack"""
    from session_dev.scripts.generate_stack import StackGenerator

    project_root = Path.cwd()
    generator = StackGenerator(project_root)

    try:
        generator.generate()
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        sys.exit(1)


@docs.command(name="tree-scan")
@click.option("--include-hidden", is_flag=True, help="Include hidden files")
def docs_tree_scan(include_hidden: bool):
    """Generate project structure tree"""
    from session_dev.scripts.generate_tree import TreeGenerator

    project_root = Path.cwd()
    generator = TreeGenerator(project_root)

    try:
        generator.generate(include_hidden=include_hidden)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        sys.exit(1)


# Validation Commands
@main.command(name="validate")
@click.option("--fix-issues", is_flag=True, help="Attempt to fix issues")
def validate(fix_issues: bool):
    """Validate project environment"""
    from session_dev.scripts.session_validate import SessionValidator

    project_root = Path.cwd()
    validator = SessionValidator(project_root)

    try:
        success = validator.validate_all(fix_issues=fix_issues)
        sys.exit(0 if success else 1)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        sys.exit(1)


# Learning Management
@main.group(name="learnings")
def learnings():
    """Manage project learnings"""
    pass


@learnings.command(name="curate")
@click.option("--dry-run", is_flag=True, help="Show changes without saving")
def learnings_curate(dry_run: bool):
    """Curate and organize learnings"""
    from session_dev.scripts.curate_learnings import LearningsCurator

    project_root = Path.cwd()
    curator = LearningsCurator(project_root)

    try:
        curator.curate(dry_run=dry_run)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        sys.exit(1)


@learnings.command(name="report")
def learnings_report():
    """Show learnings summary report"""
    from session_dev.scripts.curate_learnings import LearningsCurator

    project_root = Path.cwd()
    curator = LearningsCurator(project_root)

    try:
        curator.generate_report()
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        sys.exit(1)


@learnings.command(name="show")
@click.option("--category", type=str, help="Specific category to show")
def learnings_show(category: Optional[str]):
    """Show learnings"""
    from session_dev.scripts.curate_learnings import LearningsCurator

    project_root = Path.cwd()
    curator = LearningsCurator(project_root)

    try:
        curator.show_learnings(category=category)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
