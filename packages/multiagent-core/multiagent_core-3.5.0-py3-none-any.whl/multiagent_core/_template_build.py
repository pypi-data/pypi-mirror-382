"""Custom build hooks that keep packaged templates aligned with repository sources."""
from __future__ import annotations

import importlib
import shutil
from pathlib import Path
from typing import Any, Callable

from setuptools.command.build_py import build_py as _build_py

from ._template_sync import sync_templates


def _package_template_root() -> Path:
    return Path(__file__).resolve().parent / "templates"


def _repo_root() -> Path:
    return _package_template_root().parent.parent


def _prune_pycache(root: Path) -> None:
    for cache_dir in root.rglob("__pycache__"):
        shutil.rmtree(cache_dir, ignore_errors=True)


def _sync_for_build() -> None:
    """Copy template sources into the package before delegating to setuptools."""

    package_templates = _package_template_root()
    sync_templates(quiet=True, repo_root=_repo_root())
    version_src = _repo_root() / 'VERSION'
    if version_src.exists():
        shutil.copy(version_src, package_templates.parent / 'VERSION')
    _prune_pycache(package_templates)
    
    # AUTO-UPDATE: Trigger update of all registered projects after build
    try:
        import subprocess
        import sys
        from pathlib import Path
        
        # Find the track_and_update.py script
        candidates = [
            _repo_root() / "build-system" / "track_and_update.py",
            _repo_root() / "scripts" / "track_and_update.py",  # Legacy fallback
        ]
        update_script = next((path for path in candidates if path.exists()), None)
        if update_script is not None:
            print("\n[AUTO-UPDATE] Updating all registered projects...")
            result = subprocess.run(
                [sys.executable, str(update_script), "update"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("[AUTO-UPDATE] All projects updated successfully!")
            else:
                print(f"[AUTO-UPDATE] Warning: Update had issues: {result.stderr}")
    except Exception as e:
        print(f"[AUTO-UPDATE] Warning: Could not auto-update projects: {e}")
        # Don't fail the build if auto-update fails


_BUILD_META = importlib.import_module("setuptools.build_meta")


def _delegate(name: str) -> Callable[..., Any]:
    return getattr(_BUILD_META, name)


def _build_and_sync(func: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        _sync_for_build()
        return func(*args, **kwargs)

    return wrapper


build_wheel_backend = _delegate("build_wheel")
build_sdist_backend = _delegate("build_sdist")
prepare_metadata_wheel_backend = _delegate("prepare_metadata_for_build_wheel")
prepare_metadata_editable_backend = getattr(_BUILD_META, "prepare_metadata_for_build_editable", None)
build_editable_backend = getattr(_BUILD_META, "build_editable", None)
requires_wheel_backend = _delegate("get_requires_for_build_wheel")
requires_editable_backend = getattr(_BUILD_META, "get_requires_for_build_editable", None)
requires_sdist_backend = getattr(_BUILD_META, "get_requires_for_build_sdist", None)


build_wheel = _build_and_sync(build_wheel_backend)
build_sdist = _build_and_sync(build_sdist_backend)


if build_editable_backend is not None:
    build_editable = _build_and_sync(build_editable_backend)


prepare_metadata_for_build_wheel = _build_and_sync(prepare_metadata_wheel_backend)


if prepare_metadata_editable_backend is not None:
    prepare_metadata_for_build_editable = _build_and_sync(prepare_metadata_editable_backend)


get_requires_for_build_wheel = requires_wheel_backend


if requires_editable_backend is not None:
    get_requires_for_build_editable = requires_editable_backend


if requires_sdist_backend is not None:
    get_requires_for_build_sdist = requires_sdist_backend


class build_py_cmd(_build_py):  # lowercase matches setuptools command naming
    """Run template sync before packaging Python modules."""

    def run(self) -> None:  # noqa: D401 - override
        _sync_for_build()
        super().run()
        build_templates = Path(self.build_lib) / "multiagent_core" / "templates"
        if build_templates.exists():
            _prune_pycache(build_templates)


class build_editable_cmd(build_py_cmd):
    """PEP 660 editable build hook (setuptools >= 64)."""

    def run(self) -> None:  # noqa: D401 - override
        _sync_for_build()
        super().run()
        build_templates = Path(self.build_lib) / "multiagent_core" / "templates"
        if build_templates.exists():
            _prune_pycache(build_templates)


__all__ = [
    "build_py_cmd",
    "build_editable_cmd",
    "build_wheel",
    "build_sdist",
    "prepare_metadata_for_build_wheel",
]

if prepare_metadata_editable_backend is not None:
    __all__.append("prepare_metadata_for_build_editable")

if requires_editable_backend is not None:
    __all__.append("get_requires_for_build_editable")

if requires_sdist_backend is not None:
    __all__.append("get_requires_for_build_sdist")

__all__.append("get_requires_for_build_wheel")
