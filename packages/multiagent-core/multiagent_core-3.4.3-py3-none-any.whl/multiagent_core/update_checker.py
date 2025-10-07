"""Utilities for checking MultiAgent package versions and caching results."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

import requests
from packaging import version

try:  # pragma: no cover - importlib backport for <3.8
    from importlib import metadata
except ImportError:  # pragma: no cover
    import importlib_metadata as metadata

MULTIAGENT_PACKAGES: List[str] = [
    "multiagent-core",
    "multiagent-agentswarm",
    "multiagent-devops",
    "multiagent-testing",
]

CACHE_TTL = timedelta(hours=24)
CACHE_FILE = Path.home() / ".multiagent" / "update_cache.json"
PYPI_URL_TEMPLATE = "https://pypi.org/pypi/{package}/json"


def _read_cache() -> Dict:
    if CACHE_FILE.exists():
        try:
            with CACHE_FILE.open("r") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _write_cache(data: Dict) -> None:
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = CACHE_FILE.with_suffix(".tmp")
    try:
        with tmp_path.open("w") as fh:
            json.dump(data, fh)
        tmp_path.replace(CACHE_FILE)
    except OSError:
        pass  # Cache failures should not break CLI behaviour


@dataclass
class PackageUpdate:
    package: str
    current: str
    latest: str
    summary: str | None = None


class UpdateChecker:
    """Check PyPI for newer releases of MultiAgent packages."""

    def __init__(self, *, ttl: timedelta = CACHE_TTL):
        self.ttl = ttl
        self.cache = _read_cache()
        self.current_versions: Dict[str, str] = {}
        self.latest_versions: Dict[str, str] = self.cache.get("latest", {})

    def _is_expired(self) -> bool:
        timestamp = self.cache.get("timestamp")
        if not timestamp:
            return True
        try:
            last = datetime.fromisoformat(timestamp)
        except ValueError:
            return True
        return datetime.utcnow() - last > self.ttl

    def _collect_current_versions(self) -> Dict[str, str]:
        versions: Dict[str, str] = {}
        for package in MULTIAGENT_PACKAGES:
            try:
                versions[package] = metadata.version(package)
            except metadata.PackageNotFoundError:
                continue
        return versions

    def _fetch_latest_versions(self) -> Dict[str, str]:
        results: Dict[str, str] = {}
        for package in MULTIAGENT_PACKAGES:
            try:
                resp = requests.get(PYPI_URL_TEMPLATE.format(package=package), timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    results[package] = data["info"]["version"]
            except requests.RequestException:
                continue
        return results

    def check(self, *, force: bool = False) -> List[PackageUpdate]:
        """Return a list of packages where a newer version exists."""

        self.current_versions = self._collect_current_versions()

        if force or self._is_expired() or not self.latest_versions:
            self.latest_versions = self._fetch_latest_versions()
            self.cache = {
                "timestamp": datetime.utcnow().isoformat(),
                "latest": self.latest_versions,
            }
            _write_cache(self.cache)

        updates: List[PackageUpdate] = []
        for package, current in self.current_versions.items():
            latest = self.latest_versions.get(package)
            if not latest:
                continue
            if version.parse(latest) > version.parse(current):
                updates.append(PackageUpdate(package, current, latest))

        return updates


def clear_cache() -> None:
    """Remove cached update information."""
    try:
        CACHE_FILE.unlink()
    except FileNotFoundError:
        pass
    except OSError:
        pass
