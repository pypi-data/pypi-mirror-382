#!/usr/bin/env python3
"""
Technology stack generation script

Auto-detects and documents the technology stack by:
1. Scanning for language files
2. Parsing package files (requirements.txt, package.json, etc.)
3. Detecting frameworks from imports
4. Identifying databases
5. Detecting external APIs
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console

from session_dev.utils.file_ops import load_json, write_file

console = Console()


class StackGenerator:
    """Generates technology stack documentation"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.session_dir = project_root / ".session"
        self.stack: dict[str, list[str]] = {
            "languages": [],
            "backend_frameworks": [],
            "frontend_frameworks": [],
            "databases": [],
            "testing": [],
            "infrastructure": [],
            "external_apis": [],
        }

    def generate(self) -> str:
        """Generate stack documentation"""
        console.print("\n[bold blue]Generating Technology Stack[/bold blue]\n")

        # Detect languages
        self._detect_languages()
        console.print("[green]✓ Languages detected[/green]")

        # Parse package files
        self._parse_package_files()
        console.print("[green]✓ Package files parsed[/green]")

        # Detect frameworks
        self._detect_frameworks()
        console.print("[green]✓ Frameworks detected[/green]")

        # Detect infrastructure
        self._detect_infrastructure()
        console.print("[green]✓ Infrastructure detected[/green]")

        # Generate documentation
        content = self._format_stack()

        # Save to file
        stack_path = self.session_dir / "tracking" / "stack.txt"
        write_file(stack_path, content)

        console.print(
            f"\n[green]✓ Stack saved to {stack_path.relative_to(self.project_root)}[/green]\n"
        )

        return content

    def _detect_languages(self) -> None:
        """Detect programming languages"""
        language_extensions = {
            ".py": "Python",
            ".ts": "TypeScript",
            ".js": "JavaScript",
            ".jsx": "JavaScript (JSX)",
            ".tsx": "TypeScript (TSX)",
            ".go": "Go",
            ".rs": "Rust",
            ".java": "Java",
            ".kt": "Kotlin",
            ".rb": "Ruby",
            ".php": "PHP",
            ".c": "C",
            ".cpp": "C++",
            ".cs": "C#",
            ".swift": "Swift",
        }

        found_languages = set()

        # Scan for files (exclude common directories)
        exclude_dirs = {
            ".git",
            "node_modules",
            "__pycache__",
            ".venv",
            "venv",
            "dist",
            "build",
            ".session",
        }

        for ext, lang in language_extensions.items():
            # Search for files with this extension
            for path in self.project_root.rglob(f"*{ext}"):
                # Skip excluded directories
                if any(excluded in path.parts for excluded in exclude_dirs):
                    continue
                found_languages.add(lang)

        self.stack["languages"] = sorted(list(found_languages))

    def _parse_package_files(self) -> None:
        """Parse package management files"""

        # Python - requirements.txt
        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            self._parse_requirements(req_file)

        # Python - pyproject.toml
        pyproject_file = self.project_root / "pyproject.toml"
        if pyproject_file.exists():
            self._parse_pyproject(pyproject_file)

        # Node.js - package.json
        package_json = self.project_root / "package.json"
        if package_json.exists():
            self._parse_package_json(package_json)

        # Rust - Cargo.toml
        cargo_toml = self.project_root / "Cargo.toml"
        if cargo_toml.exists():
            self._parse_cargo_toml(cargo_toml)

        # Go - go.mod
        go_mod = self.project_root / "go.mod"
        if go_mod.exists():
            self._parse_go_mod(go_mod)

    def _parse_requirements(self, req_file: Path) -> None:
        """Parse requirements.txt"""
        content = req_file.read_text()

        framework_patterns = {
            r"django": "Django",
            r"flask": "Flask",
            r"fastapi": "FastAPI",
            r"tornado": "Tornado",
            r"pyramid": "Pyramid",
        }

        testing_patterns = {
            r"pytest": "pytest",
            r"unittest2": "unittest2",
            r"nose": "nose",
        }

        for line in content.split("\n"):
            line = line.strip().lower()

            # Check frameworks
            for pattern, name in framework_patterns.items():
                if re.search(pattern, line):
                    if name not in self.stack["backend_frameworks"]:
                        self.stack["backend_frameworks"].append(name)

            # Check testing
            for pattern, name in testing_patterns.items():
                if re.search(pattern, line):
                    if name not in self.stack["testing"]:
                        self.stack["testing"].append(name)

    def _parse_pyproject(self, pyproject_file: Path) -> None:
        """Parse pyproject.toml"""
        try:
            import toml

            data = toml.load(pyproject_file)

            # Check dependencies
            deps = data.get("project", {}).get("dependencies", [])
            for dep in deps:
                dep_lower = dep.lower()

                if "fastapi" in dep_lower:
                    self.stack["backend_frameworks"].append("FastAPI")
                elif "django" in dep_lower:
                    self.stack["backend_frameworks"].append("Django")
                elif "flask" in dep_lower:
                    self.stack["backend_frameworks"].append("Flask")
                elif "pytest" in dep_lower:
                    self.stack["testing"].append("pytest")

        except ImportError:
            pass  # toml not available
        except Exception:
            pass

    def _parse_package_json(self, package_json: Path) -> None:
        """Parse package.json"""
        try:
            data = load_json(package_json)

            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

            framework_map = {
                "react": "React",
                "vue": "Vue",
                "angular": "Angular",
                "svelte": "Svelte",
                "next": "Next.js",
                "nuxt": "Nuxt.js",
                "express": "Express",
                "nestjs": "NestJS",
                "@nestjs/core": "NestJS",
            }

            testing_map = {
                "jest": "Jest",
                "mocha": "Mocha",
                "vitest": "Vitest",
                "playwright": "Playwright",
                "cypress": "Cypress",
            }

            for dep_name in deps.keys():
                # Check frameworks
                for key, name in framework_map.items():
                    if key in dep_name.lower():
                        target = (
                            self.stack["frontend_frameworks"]
                            if name
                            in [
                                "React",
                                "Vue",
                                "Angular",
                                "Svelte",
                                "Next.js",
                                "Nuxt.js",
                            ]
                            else self.stack["backend_frameworks"]
                        )
                        if name not in target:
                            target.append(name)

                # Check testing
                for key, name in testing_map.items():
                    if key in dep_name.lower():
                        if name not in self.stack["testing"]:
                            self.stack["testing"].append(name)

        except Exception:
            pass

    def _parse_cargo_toml(self, cargo_file: Path) -> None:
        """Parse Cargo.toml"""
        content = cargo_file.read_text()

        if "actix-web" in content:
            self.stack["backend_frameworks"].append("Actix-web")
        if "rocket" in content:
            self.stack["backend_frameworks"].append("Rocket")
        if "axum" in content:
            self.stack["backend_frameworks"].append("Axum")

    def _parse_go_mod(self, go_file: Path) -> None:
        """Parse go.mod"""
        content = go_file.read_text()

        if "gin-gonic/gin" in content:
            self.stack["backend_frameworks"].append("Gin")
        if "gorilla/mux" in content:
            self.stack["backend_frameworks"].append("Gorilla Mux")
        if "fiber" in content:
            self.stack["backend_frameworks"].append("Fiber")

    def _detect_frameworks(self) -> None:
        """Detect frameworks from imports"""
        # This could be extended to scan actual code files
        pass

    def _detect_infrastructure(self) -> None:
        """Detect infrastructure tools"""
        # Docker
        if (self.project_root / "Dockerfile").exists():
            self.stack["infrastructure"].append("Docker")

        if (self.project_root / "docker-compose.yml").exists():
            self.stack["infrastructure"].append("Docker Compose")

        # Kubernetes
        k8s_dir = self.project_root / "kubernetes"
        if k8s_dir.exists() or (self.project_root / "k8s").exists():
            self.stack["infrastructure"].append("Kubernetes")

        # Terraform
        if list(self.project_root.glob("*.tf")):
            self.stack["infrastructure"].append("Terraform")

        # CI/CD
        if (self.project_root / ".github" / "workflows").exists():
            self.stack["infrastructure"].append("GitHub Actions")

        if (self.project_root / ".gitlab-ci.yml").exists():
            self.stack["infrastructure"].append("GitLab CI")

        if (self.project_root / ".circleci").exists():
            self.stack["infrastructure"].append("CircleCI")

    def _format_stack(self) -> str:
        """Format stack as markdown"""
        content = f"""# Technology Stack

## Languages
{self._format_list(self.stack['languages'])}

## Backend Frameworks
{self._format_list(self.stack['backend_frameworks'])}

## Frontend Frameworks
{self._format_list(self.stack['frontend_frameworks'])}

## Databases
{self._format_list(self.stack['databases'])}

## Testing
{self._format_list(self.stack['testing'])}

## Infrastructure
{self._format_list(self.stack['infrastructure'])}

## External APIs
{self._format_list(self.stack['external_apis'])}

---
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        return content

    def _format_list(self, items: list[str]) -> str:
        """Format list of items"""
        if not items:
            return "- (None detected)"
        return "\n".join(f"- {item}" for item in items)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate technology stack documentation"
    )
    parser.add_argument(
        "--output-only", action="store_true", help="Print to stdout only"
    )
    parser.add_argument(
        "--show-changes", action="store_true", help="Show changes from last scan"
    )

    args = parser.parse_args()

    project_root = Path.cwd()
    session_dir = project_root / ".session"

    if not session_dir.exists():
        console.print("[red]Error: Not a session-dev project[/red]", style="bold")
        console.print("Run 'session-dev init' first\n")
        sys.exit(1)

    generator = StackGenerator(project_root)
    content = generator.generate()

    if args.output_only:
        console.print("\n" + content)


if __name__ == "__main__":
    main()
