"""Project initialization for Session-Driven Development"""

import json
from pathlib import Path

from session_dev.utils.file_ops import ensure_directory, write_file


class ProjectInitializer:
    """Initializes SDD in a project"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def initialize(self, preset: str = "web_app") -> None:
        """Initialize SDD structure"""

        # Create directory structure
        self._create_directories()

        # Create configuration
        self._create_config(preset)

        # Create CLAUDE.md
        self._create_claude_instructions()

        # Create initial work_items.json
        self._create_work_items_file()

        # Create initial documentation
        self._create_initial_docs()

        # Create gitignore entry
        self._update_gitignore()

    def _create_directories(self) -> None:
        """Create .session directory structure"""
        base = self.project_root / ".session"

        directories = [
            base / "tracking",
            base / "briefings",
            base / "history",
            base / "specs",
            base / "scripts",
            self.project_root / "docs",
        ]

        for directory in directories:
            ensure_directory(directory)

    def _create_config(self, preset: str) -> None:
        """Create .sessionrc.json configuration"""
        project_name = self.project_root.name

        config = {
            "framework_version": "1.0.0",
            "project": {
                "name": project_name,
                "type": preset,
                "work_item_model": "feature_based",
            },
            "session_protocol": {
                "start_trigger": "@session-start",
                "end_trigger": "@session-end",
                "auto_briefing": True,
            },
            "paths": {
                "tracking": ".session/tracking",
                "briefings": ".session/briefings",
                "specs": ".session/specs",
                "scripts": ".session/scripts",
                "history": ".session/history",
            },
            "validation_rules": {
                "pre_session": {
                    "git_clean": True,
                    "dependencies_met": True,
                    "environment_valid": True,
                },
                "post_session": {
                    "tests_pass": True,
                    "test_coverage_min": 80,
                    "linting_pass": True,
                    "documentation_updated": True,
                },
            },
            "work_item_types": {
                "feature": {
                    "template": "feature_spec.md",
                    "typical_sessions": "2-4",
                    "validation": {
                        "tests_required": True,
                        "coverage_min": 80,
                    },
                },
                "bug": {
                    "template": "bug_report.md",
                    "typical_sessions": "1-2",
                    "validation": {"tests_required": True, "regression_test": True},
                },
                "refactor": {
                    "template": "refactor_plan.md",
                    "typical_sessions": "1-3",
                    "validation": {"tests_required": True},
                },
            },
            "testing": {"framework": "pytest", "command": "pytest", "coverage_min": 80},
            "runtime_standards": {
                "linting": {"enabled": True, "auto_fix": True, "fail_on_error": True},
                "formatting": {"enabled": True, "auto_fix": True},
            },
            "git": {"auto_commit": True, "require_clean": True},
        }

        config_path = self.project_root / ".sessionrc.json"
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

    def _create_claude_instructions(self) -> None:
        """Create CLAUDE.md with AI instructions"""
        content = """# Project Instructions for Claude Code

## Session Protocol

### Starting a Session

When you see `@session-start`:
1. Run: `session-dev session start --next`
2. Read the generated briefing file
3. Understand the context and objectives
4. Begin implementation

### Ending a Session

When you see `@session-end`:
1. Run: `session-dev session complete`
2. Review quality gate results
3. Ensure all tests pass
4. Verify documentation is updated

## Project Context

This project uses Session-Driven Development (SDD) for maintaining context
across multiple AI coding sessions.

## Development Guidelines

### Code Quality

- Write tests for all new functionality
- Maintain test coverage above 80%
- Run linter before committing
- Update documentation as code changes

### Work Item Management

- Work on one item at a time
- Complete dependencies before starting new items
- Update session notes during development
- Capture learnings as you discover them

## Commands Reference

- Start session: `session-dev session start --next`
- Complete session: `session-dev session complete`
- Check status: `session-dev session status`
- List work items: `session-dev work-item list`
- Show work item: `session-dev work-item show <id>`

## Learning Capture

When you discover important patterns, gotchas, or insights:
1. Note them during the session
2. Add them to session notes
3. They will be curated into the knowledge base

## Quality Standards

All code must:
- Pass all tests
- Meet linting requirements
- Be properly formatted
- Have adequate documentation
- Follow project patterns
"""

        claude_path = self.project_root / "CLAUDE.md"
        write_file(claude_path, content)

    def _create_work_items_file(self) -> None:
        """Create initial work_items.json"""
        data = {
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

        work_items_path = (
            self.project_root / ".session" / "tracking" / "work_items.json"
        )
        with open(work_items_path, "w") as f:
            json.dump(data, f, indent=2)

    def _create_initial_docs(self) -> None:
        """Create initial documentation files"""
        docs_dir = self.project_root / "docs"

        # vision.md
        vision_content = """# Project Vision

## Purpose

[Describe why this project exists and what problem it solves]

## Goals

- [Primary goal]
- [Secondary goal]
- [Additional goals]

## Success Criteria

[How will you measure success?]
"""
        write_file(docs_dir / "vision.md", vision_content)

        # architecture.md
        arch_content = """# Architecture

## System Overview

[High-level description of the system]

## Components

### [Component Name]

[Description]

## Data Flow

[How data moves through the system]

## Technology Stack

[Key technologies and why they were chosen]
"""
        write_file(docs_dir / "architecture.md", arch_content)

        # development_plan.md
        plan_content = """# Development Plan

## Milestones

### Milestone 1: [Name]

**Target Date:** TBD

**Work Items:**
- [List work items]

### Milestone 2: [Name]

**Target Date:** TBD

**Work Items:**
- [List work items]

## Timeline

[Overall project timeline]
"""
        write_file(docs_dir / "development_plan.md", plan_content)

    def _update_gitignore(self) -> None:
        """Add .session entries to .gitignore"""
        gitignore_path = self.project_root / ".gitignore"

        entries = [
            "",
            "# Session-Dev",
            ".session/briefings/",
            ".session/history/",
            ".session/tracking/*.backup",
        ]

        if gitignore_path.exists():
            content = gitignore_path.read_text()
            if "Session-Dev" not in content:
                with open(gitignore_path, "a") as f:
                    f.write("\n".join(entries) + "\n")
        else:
            write_file(gitignore_path, "\n".join(entries) + "\n")
