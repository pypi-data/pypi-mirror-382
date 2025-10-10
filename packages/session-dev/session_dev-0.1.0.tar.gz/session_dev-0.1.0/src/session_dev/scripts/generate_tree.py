#!/usr/bin/env python3
"""
Project tree generation script

Generates deterministic project structure documentation:
1. Runs tree-like structure generation
2. Filters common noise
3. Compares with previous tree
4. Shows additions and removals
5. Provides statistics
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console

from session_dev.utils.file_ops import read_file, write_file

console = Console()


class TreeGenerator:
    """Generates project structure documentation"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.session_dir = project_root / ".session"

        # Patterns to ignore
        self.ignore_patterns = [
            ".git",
            "__pycache__",
            "*.pyc",
            ".pytest_cache",
            ".venv",
            "venv",
            "env",
            "node_modules",
            ".DS_Store",
            "*.egg-info",
            ".mypy_cache",
            ".ruff_cache",
            "*.log",
            "*.tmp",
            "*.backup",
            "dist",
            "build",
            ".session/briefings",
            ".session/history",
        ]

    def generate(self, include_hidden: bool = False) -> str:
        """Generate project tree"""
        console.print("\n[bold blue]Generating Project Tree[/bold blue]\n")

        # Generate tree structure
        tree_output = self._generate_tree(include_hidden)

        # Add header
        content = f"""# Project Structure

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

```
{tree_output}
```

---
Total directories and files listed
"""

        # Save to file
        tree_path = self.session_dir / "tracking" / "project_tree.txt"
        write_file(tree_path, content)

        console.print(
            f"[green]✓ Tree saved to {tree_path.relative_to(self.project_root)}[/green]\n"
        )

        return content

    def _generate_tree(self, include_hidden: bool) -> str:
        """Generate tree structure"""
        # Try using system tree command if available
        if self._has_tree_command():
            return self._generate_with_tree_command(include_hidden)
        else:
            return self._generate_custom_tree(include_hidden)

    def _has_tree_command(self) -> bool:
        """Check if tree command is available"""
        try:
            subprocess.run(
                ["tree", "--version"],
                capture_output=True,
                check=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _generate_with_tree_command(self, include_hidden: bool) -> str:
        """Generate tree using system tree command"""
        cmd = ["tree"]

        if include_hidden:
            cmd.append("-a")

        # Add ignore patterns
        for pattern in self.ignore_patterns:
            cmd.extend(["-I", pattern])

        cmd.append("-L")
        cmd.append("4")  # Max depth of 4

        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.stdout
        except Exception as e:
            console.print(f"[yellow]Warning: tree command failed: {e}[/yellow]")
            return self._generate_custom_tree(include_hidden)

    def _generate_custom_tree(self, include_hidden: bool, max_depth: int = 4) -> str:
        """Generate tree using custom implementation"""
        lines = []

        def should_ignore(path: Path) -> bool:
            """Check if path should be ignored"""
            name = path.name

            # Check exact matches
            if name in self.ignore_patterns:
                return True

            # Check wildcard patterns
            for pattern in self.ignore_patterns:
                if "*" in pattern:
                    # Simple wildcard matching
                    if pattern.startswith("*"):
                        if name.endswith(pattern[1:]):
                            return True
                    elif pattern.endswith("*"):
                        if name.startswith(pattern[:-1]):
                            return True

            # Check if hidden
            if (
                not include_hidden
                and name.startswith(".")
                and name not in [".session", ".sessionrc.json"]
            ):
                return True

            return False

        def walk_tree(path: Path, prefix: str = "", depth: int = 0):
            """Recursively walk directory tree"""
            if depth > max_depth:
                return

            try:
                entries = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
            except PermissionError:
                return

            # Filter ignored entries
            entries = [e for e in entries if not should_ignore(e)]

            for i, entry in enumerate(entries):
                is_last = i == len(entries) - 1
                connector = "└── " if is_last else "├── "
                extension = "    " if is_last else "│   "

                # Add entry
                lines.append(f"{prefix}{connector}{entry.name}")

                # Recurse for directories
                if entry.is_dir():
                    walk_tree(entry, prefix + extension, depth + 1)

        # Start with project root
        lines.append(f"{self.project_root.name}/")
        walk_tree(self.project_root)

        return "\n".join(lines)

    def show_changes(self) -> None:
        """Show changes from last tree"""
        tree_path = self.session_dir / "tracking" / "project_tree.txt"

        if not tree_path.exists():
            console.print("[yellow]No previous tree found[/yellow]\n")
            return

        # For now, just show a message
        # Could implement diff logic here
        console.print("[yellow]Tree diff not yet implemented[/yellow]\n")
        console.print("Previous tree exists at:", tree_path)

    def display_current(self) -> None:
        """Display current tree"""
        tree_path = self.session_dir / "tracking" / "project_tree.txt"

        if not tree_path.exists():
            console.print(
                "[yellow]No tree file found. Run generation first.[/yellow]\n"
            )
            return

        content = read_file(tree_path)
        console.print(content)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Generate project structure tree")
    parser.add_argument(
        "--show-changes", action="store_true", help="Show changes from last scan"
    )
    parser.add_argument(
        "--include-hidden", action="store_true", help="Include hidden files"
    )
    parser.add_argument(
        "--display-current", action="store_true", help="Display current tree"
    )

    args = parser.parse_args()

    project_root = Path.cwd()
    session_dir = project_root / ".session"

    if not session_dir.exists():
        console.print("[red]Error: Not a session-dev project[/red]", style="bold")
        console.print("Run 'session-dev init' first\n")
        sys.exit(1)

    generator = TreeGenerator(project_root)

    if args.display_current:
        generator.display_current()
    elif args.show_changes:
        generator.show_changes()
    else:
        generator.generate(include_hidden=args.include_hidden)


if __name__ == "__main__":
    main()
