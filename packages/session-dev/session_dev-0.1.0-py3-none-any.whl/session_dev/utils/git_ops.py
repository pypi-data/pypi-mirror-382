"""Git operations utilities"""

from pathlib import Path

from git import Repo
from git.exc import InvalidGitRepositoryError


def get_repo(project_root: Path) -> Repo:
    """Get git repository"""
    try:
        return Repo(project_root)
    except InvalidGitRepositoryError:
        raise ValueError(f"Not a git repository: {project_root}")


def is_git_clean(project_root: Path) -> bool:
    """Check if git working directory is clean"""
    try:
        repo = get_repo(project_root)
        return not repo.is_dirty() and len(repo.untracked_files) == 0
    except Exception:
        return False


def get_git_status(project_root: Path) -> tuple[list[str], list[str]]:
    """Get git status: (modified_files, untracked_files)"""
    try:
        repo = get_repo(project_root)
        modified = [item.a_path for item in repo.index.diff(None)]
        untracked = repo.untracked_files
        return modified, untracked
    except Exception:
        return [], []


def create_commit(project_root: Path, message: str, add_all: bool = True) -> None:
    """Create a git commit"""
    repo = get_repo(project_root)

    if add_all:
        repo.git.add(A=True)

    repo.index.commit(message)


def get_changed_files_since(project_root: Path, since: str = "HEAD~1") -> list[str]:
    """Get list of files changed since a git ref"""
    try:
        repo = get_repo(project_root)
        diff = repo.git.diff(since, name_only=True)
        return diff.split("\n") if diff else []
    except Exception:
        return []


def get_commit_log(project_root: Path, max_count: int = 10) -> list[str]:
    """Get recent commit messages"""
    try:
        repo = get_repo(project_root)
        commits = list(repo.iter_commits(max_count=max_count))
        return [
            f"{commit.hexsha[:7]} {commit.message.split(chr(10))[0]}"
            for commit in commits
        ]
    except Exception:
        return []
