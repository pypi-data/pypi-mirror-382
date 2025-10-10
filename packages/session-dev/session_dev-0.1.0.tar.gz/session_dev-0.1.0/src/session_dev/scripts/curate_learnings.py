#!/usr/bin/env python3
"""
Learning curation script

Curates and organizes accumulated learnings:
1. Loads raw learnings from session summaries
2. Categorizes learnings
3. Merges similar/duplicate learnings
4. Archives obsolete learnings
5. Generates learning summary reports
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.table import Table

from session_dev.utils.file_ops import load_json, save_json

console = Console()


class LearningsCurator:
    """Curates project learnings"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.session_dir = project_root / ".session"
        self.learnings_path = self.session_dir / "tracking" / "learnings.json"

    def curate(self, dry_run: bool = False) -> None:
        """Curate learnings"""
        console.print("\n[bold blue]═══ Learning Curation ═══[/bold blue]\n")

        # Load existing learnings
        learnings = self._load_learnings()

        # Statistics
        initial_count = self._count_all_learnings(learnings)
        console.print(f"Initial learnings: {initial_count}\n")

        # Categorize uncategorized learnings
        categorized = self._categorize_learnings(learnings)
        console.print(f"[green]✓ Categorized {categorized} learnings[/green]")

        # Merge similar learnings
        merged = self._merge_similar_learnings(learnings)
        console.print(f"[green]✓ Merged {merged} duplicate learnings[/green]")

        # Archive old learnings
        archived = self._archive_old_learnings(learnings)
        console.print(f"[green]✓ Archived {archived} old learnings[/green]")

        # Update metadata
        learnings["last_curated"] = datetime.now().isoformat()
        learnings["curator"] = "session_curator"

        final_count = self._count_all_learnings(learnings)

        console.print(f"\nFinal learnings: {final_count}\n")

        if not dry_run:
            save_json(self.learnings_path, learnings)
            console.print("[green]✓ Learnings saved[/green]\n")
        else:
            console.print("[yellow]Dry run - no changes saved[/yellow]\n")

    def _load_learnings(self) -> dict:
        """Load learnings file"""
        if self.learnings_path.exists():
            return load_json(self.learnings_path)
        else:
            # Create default structure
            return {
                "last_curated": None,
                "curator": "session_curator",
                "categories": {
                    "architecture_patterns": [],
                    "gotchas": [],
                    "best_practices": [],
                    "technical_debt": [],
                    "performance_insights": [],
                },
                "archived": [],
            }

    def _count_all_learnings(self, learnings: dict) -> int:
        """Count all learnings"""
        count = 0
        categories = learnings.get("categories", {})

        for category in categories.values():
            count += len(category)

        count += len(learnings.get("archived", []))

        return count

    def _categorize_learnings(self, learnings: dict) -> int:
        """Categorize uncategorized learnings"""
        # This would load from session summaries
        # For now, return 0 as we don't have raw learnings yet
        return 0

    def _merge_similar_learnings(self, learnings: dict) -> int:
        """Merge similar learnings"""
        merged_count = 0
        categories = learnings.get("categories", {})

        for category_name, category_learnings in categories.items():
            # Group by similarity (simple keyword matching for now)
            to_remove = []

            for i, learning_a in enumerate(category_learnings):
                if i in to_remove:
                    continue

                for j in range(i + 1, len(category_learnings)):
                    if j in to_remove:
                        continue

                    learning_b = category_learnings[j]

                    # Simple similarity check
                    if self._are_similar(learning_a, learning_b):
                        # Merge into first learning
                        self._merge_learning(learning_a, learning_b)
                        to_remove.append(j)
                        merged_count += 1

            # Remove merged learnings
            for idx in sorted(to_remove, reverse=True):
                category_learnings.pop(idx)

        return merged_count

    def _are_similar(self, learning_a: dict, learning_b: dict) -> bool:
        """Check if two learnings are similar"""
        content_a = learning_a.get("content", "").lower()
        content_b = learning_b.get("content", "").lower()

        # Simple keyword overlap check
        words_a = set(content_a.split())
        words_b = set(content_b.split())

        if len(words_a) == 0 or len(words_b) == 0:
            return False

        overlap = len(words_a & words_b)
        total = len(words_a | words_b)

        similarity = overlap / total if total > 0 else 0

        return similarity > 0.7  # 70% similarity threshold

    def _merge_learning(self, target: dict, source: dict) -> None:
        """Merge source learning into target"""
        # Merge applies_to
        target_applies = set(target.get("applies_to", []))
        source_applies = set(source.get("applies_to", []))
        target["applies_to"] = list(target_applies | source_applies)

        # Add note about merge
        if "merged_from" not in target:
            target["merged_from"] = []
        target["merged_from"].append(source.get("learned_in", "unknown"))

    def _archive_old_learnings(
        self, learnings: dict, max_age_sessions: int = 50
    ) -> int:
        """Archive old, unreferenced learnings"""
        # For now, don't archive anything
        # Would need to track session numbers and references
        return 0

    def generate_report(self) -> None:
        """Generate learning summary report"""
        console.print("\n[bold blue]Learning Summary Report[/bold blue]\n")

        learnings = self._load_learnings()

        # Create table
        table = Table(title="Learnings by Category")
        table.add_column("Category", style="cyan")
        table.add_column("Count", justify="right", style="green")

        categories = learnings.get("categories", {})
        total = 0

        for category_name, category_learnings in categories.items():
            count = len(category_learnings)
            total += count
            table.add_row(category_name.replace("_", " ").title(), str(count))

        # Add archived
        archived_count = len(learnings.get("archived", []))
        if archived_count > 0:
            table.add_row("Archived", str(archived_count), style="dim")

        # Add total
        table.add_row("[bold]Total[/bold]", f"[bold]{total}[/bold]")

        console.print(table)
        console.print()

        # Show last curated
        last_curated = learnings.get("last_curated")
        if last_curated:
            console.print(f"Last curated: {last_curated}\n")
        else:
            console.print("[yellow]Never curated[/yellow]\n")

    def show_learnings(self, category: str = None) -> None:
        """Show learnings by category"""
        learnings = self._load_learnings()
        categories = learnings.get("categories", {})

        if category:
            # Show specific category
            if category not in categories:
                console.print(f"[red]Category not found: {category}[/red]\n")
                return

            console.print(
                f"\n[bold cyan]{category.replace('_', ' ').title()}[/bold cyan]\n"
            )

            for i, learning in enumerate(categories[category], 1):
                console.print(f"{i}. {learning.get('content', 'N/A')}")
                if "learned_in" in learning:
                    console.print(f"   [dim]Learned in: {learning['learned_in']}[/dim]")
                console.print()
        else:
            # Show all categories
            for category_name, category_learnings in categories.items():
                if not category_learnings:
                    continue

                console.print(
                    f"\n[bold cyan]{category_name.replace('_', ' ').title()}[/bold cyan]"
                )
                console.print(f"Count: {len(category_learnings)}\n")

                # Show first 3
                for learning in category_learnings[:3]:
                    console.print(f"  • {learning.get('content', 'N/A')}")

                if len(category_learnings) > 3:
                    console.print(
                        f"  [dim]... and {len(category_learnings) - 3} more[/dim]"
                    )

                console.print()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Curate project learnings")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show changes without saving"
    )
    parser.add_argument("--report", action="store_true", help="Generate summary report")
    parser.add_argument("--show", type=str, help="Show learnings by category")
    parser.add_argument(
        "--recategorize-all", action="store_true", help="Recategorize all learnings"
    )

    args = parser.parse_args()

    project_root = Path.cwd()
    session_dir = project_root / ".session"

    if not session_dir.exists():
        console.print("[red]Error: Not a session-dev project[/red]", style="bold")
        console.print("Run 'session-dev init' first\n")
        sys.exit(1)

    curator = LearningsCurator(project_root)

    if args.report:
        curator.generate_report()
    elif args.show:
        curator.show_learnings(category=args.show)
    else:
        curator.curate(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
