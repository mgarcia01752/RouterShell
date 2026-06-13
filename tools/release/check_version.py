#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2026 Maurice Garcia

"""Verify RouterShell version consistency."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import tomllib


class VersionCheckTool:
    """Verify version consistency between the package and pyproject.toml."""

    MAX_ROOT_SEARCH_DEPTH: int = 6
    PYPROJECT_RELATIVE: str = "pyproject.toml"
    EXIT_OK: int = 0
    EXIT_ERROR: int = 1
    EXIT_MISMATCH: int = 2

    @staticmethod
    def _find_project_root(start_path: Path) -> Path:
        """Walk upwards to locate pyproject.toml, fallback to start path."""
        current = start_path
        for _ in range(VersionCheckTool.MAX_ROOT_SEARCH_DEPTH):
            if (current / VersionCheckTool.PYPROJECT_RELATIVE).is_file():
                return current
            if current.parent == current:
                break
            current = current.parent
        return start_path

    @staticmethod
    def _read_version_from_pyproject(path: Path) -> str:
        """Extract the project version value from pyproject.toml."""
        try:
            with path.open("rb") as handle:
                pyproject = tomllib.load(handle)
        except OSError:
            return ""

        project = pyproject.get("project", {})
        version = project.get("version", "")
        if not isinstance(version, str):
            return ""
        return version

    @staticmethod
    def _read_version_from_package(root_path: Path) -> str:
        """Read the runtime package version."""
        if str(root_path) not in sys.path:
            sys.path.insert(0, str(root_path))
        try:
            import routershell
        except ImportError:
            return ""
        return routershell.__version__

    @staticmethod
    def _build_parser() -> argparse.ArgumentParser:
        """Build the CLI parser for the version check tool."""
        parser = argparse.ArgumentParser(
            description="Verify that the RouterShell package and pyproject.toml carry the same version."
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Print results as JSON.",
        )
        return parser

    @staticmethod
    def _emit_text(package_version: str, pyproject_version: str, status: str) -> None:
        """Emit human-readable output."""
        if status == "error":
            print("Version check failed: unable to read one or more version values.")
        print(f"routershell package: {package_version or 'missing'}")
        print(f"pyproject.toml: {pyproject_version or 'missing'}")
        if status == "mismatch":
            print("Version mismatch detected.")
        if status == "ok":
            print("Version match confirmed.")

    @staticmethod
    def _emit_json(package_version: str, pyproject_version: str, status: str) -> None:
        """Emit JSON output."""
        payload = {
            "package": package_version,
            "pyproject": pyproject_version,
            "match": status == "ok",
            "status": status,
        }
        print(json.dumps(payload, ensure_ascii=True))

    @staticmethod
    def run(options: argparse.Namespace) -> int:
        """Print versions from tracked files and return a status code."""
        script_dir = Path(__file__).resolve().parent
        root_path = VersionCheckTool._find_project_root(script_dir)
        pyproject_path = root_path / VersionCheckTool.PYPROJECT_RELATIVE

        package_version = VersionCheckTool._read_version_from_package(root_path)
        pyproject_version = VersionCheckTool._read_version_from_pyproject(pyproject_path)

        if not package_version or not pyproject_version:
            if options.json:
                VersionCheckTool._emit_json(package_version, pyproject_version, "error")
            else:
                VersionCheckTool._emit_text(package_version, pyproject_version, "error")
            return VersionCheckTool.EXIT_ERROR

        if package_version != pyproject_version:
            if options.json:
                VersionCheckTool._emit_json(package_version, pyproject_version, "mismatch")
            else:
                VersionCheckTool._emit_text(package_version, pyproject_version, "mismatch")
            return VersionCheckTool.EXIT_MISMATCH

        if options.json:
            VersionCheckTool._emit_json(package_version, pyproject_version, "ok")
        else:
            VersionCheckTool._emit_text(package_version, pyproject_version, "ok")
        return VersionCheckTool.EXIT_OK


if __name__ == "__main__":
    parser = VersionCheckTool._build_parser()
    args = parser.parse_args()
    sys.exit(VersionCheckTool.run(args))
