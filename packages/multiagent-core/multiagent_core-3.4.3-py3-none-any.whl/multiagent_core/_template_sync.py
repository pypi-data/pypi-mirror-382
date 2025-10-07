"""Utilities for keeping packaged templates in sync with repository sources."""
from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


TEMPLATE_NAMES: List[str] = [
    ".claude",
    ".github",
    ".multiagent",
    ".multiagent-feedback",
    ".vscode",
]


@dataclass
class SyncResult:
    """Record of a single directory sync."""

    source: Path
    destination: Path
    copied: bool
    reason: str = ""


def _find_repo_root(start: Path | None = None) -> Path:
    """Locate the project root by walking up until pyproject.toml is found."""
    start = start or Path.cwd()
    for candidate in [start, *start.parents]:
        if (candidate / "pyproject.toml").exists():
            return candidate
    return start


def _package_template_root() -> Path:
    return Path(__file__).resolve().parent / "templates"


def sync_templates(
    template_names: Iterable[str] | None = None,
    *,
    quiet: bool = False,
    repo_root: Path | None = None,
) -> List[SyncResult]:
    names = list(template_names or TEMPLATE_NAMES)
    repo_root = repo_root or _find_repo_root()
    package_root = _package_template_root()
    package_root.mkdir(parents=True, exist_ok=True)

    results: List[SyncResult] = []

    for name in names:
        src = repo_root / name
        dest = package_root / name

        if dest.exists():
            shutil.rmtree(dest)

        if not src.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            results.append(SyncResult(src, dest, copied=False, reason="missing source"))
            if not quiet:
                print(f"⚠️  {name} not found in {repo_root}; removed packaged copy if present")
            continue

        shutil.copytree(
            src,
            dest,
            ignore=shutil.ignore_patterns(
                '__pycache__',
                '*.pyc',
                'build-system',        # Exclude build-system (repo infrastructure only)
                'local-overrides'       # Exclude local-overrides (development only)
            )
        )
        results.append(SyncResult(src, dest, copied=True))
        if not quiet:
            print(f"✅ Synced {name}")

    return results


__all__ = ["sync_templates", "SyncResult", "TEMPLATE_NAMES"]
