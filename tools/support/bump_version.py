#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2026 Maurice Garcia

"""Inspect or update RouterShell version files."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Final


VERSION_FILE_PATH: Final[Path] = Path("routershell_version.py")
PYPROJECT_FILE_PATH: Final[Path] = Path("pyproject.toml")
DOC_TAG_ROOT: Final[Path] = Path("doc")
VERSION_PART_SEPARATOR: Final[str] = "."
EXPECTED_VERSION_PARTS: Final[int] = 3
MAJOR_INDEX: Final[int] = 0
MINOR_INDEX: Final[int] = 1
PATCH_INDEX: Final[int] = 2
TAG_PATTERN: Final[re.Pattern[str]] = re.compile(r'TAG="v\d+\.\d+\.\d+(?:-rc\d+)?"')


def _validate_version_string(version: str) -> None:
    """Validate that the version string matches MAJOR.MINOR.PATCH."""
    core_version = version.split("-rc", 1)[0]
    parts = core_version.split(VERSION_PART_SEPARATOR)
    if len(parts) != EXPECTED_VERSION_PARTS or not all(part.isdigit() for part in parts):
        print(f"ERROR: Invalid version '{version}'. Expected MAJOR.MINOR.PATCH.", file=sys.stderr)
        sys.exit(1)


def _read_current_version(version_file: Path) -> str:
    """Read the current __version__ value from the version file."""
    if not version_file.exists():
        print(f"ERROR: Version file not found: {version_file}", file=sys.stderr)
        sys.exit(1)

    text = version_file.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*(?::\s*[^=]+)?=\s*"([^"]+)"', text)
    if not match:
        print(f"ERROR: Could not find __version__ assignment in {version_file}.", file=sys.stderr)
        sys.exit(1)
    return match.group(1)


def _write_new_version(version_file: Path, new_version: str) -> None:
    """Write the new version into the version file."""
    text = version_file.read_text(encoding="utf-8")
    updated_text, count = re.subn(
        r'__version__\s*(?::\s*[^=]+)?=\s*"[^"]+"',
        f'__version__: str = "{new_version}"',
        text,
        count=1,
    )
    if count != 1:
        print(f"ERROR: Could not replace __version__ in {version_file}.", file=sys.stderr)
        sys.exit(1)
    version_file.write_text(updated_text, encoding="utf-8")


def _write_new_pyproject_version(pyproject_file: Path, new_version: str) -> None:
    """Write the new version into pyproject.toml [project].version."""
    if not pyproject_file.exists():
        print(f"ERROR: pyproject.toml not found: {pyproject_file}", file=sys.stderr)
        sys.exit(1)

    text = pyproject_file.read_text(encoding="utf-8")
    updated_text, count = re.subn(
        r'^(\s*version\s*=\s*)"[^"]+"',
        rf'\g<1>"{new_version}"',
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        print(f"ERROR: Could not replace [project].version in {pyproject_file}.", file=sys.stderr)
        sys.exit(1)
    pyproject_file.write_text(updated_text, encoding="utf-8")


def _update_tag_tokens(tag: str) -> None:
    """Rewrite TAG=\"vX.Y.Z\" occurrences in README and doc/*.md files."""
    paths = [Path("README.md")]
    if DOC_TAG_ROOT.exists():
        paths.extend(path for path in DOC_TAG_ROOT.rglob("*.md") if path.is_file())

    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            continue
        updated_text, count = TAG_PATTERN.subn(f'TAG="{tag}"', text)
        if count:
            path.write_text(updated_text, encoding="utf-8")


def _compute_next_version(current_version: str, mode: str) -> str:
    """Compute the next version by incrementing the requested component."""
    _validate_version_string(current_version)
    parts = [int(part) for part in current_version.split("-rc", 1)[0].split(VERSION_PART_SEPARATOR)]

    match mode:
        case "major":
            parts[MAJOR_INDEX] = parts[MAJOR_INDEX] + 1
            parts[MINOR_INDEX] = 0
            parts[PATCH_INDEX] = 0
        case "minor":
            parts[MINOR_INDEX] = parts[MINOR_INDEX] + 1
            parts[PATCH_INDEX] = 0
        case "patch":
            parts[PATCH_INDEX] = parts[PATCH_INDEX] + 1
        case _:
            print(f"ERROR: Unsupported --next mode '{mode}'.", file=sys.stderr)
            sys.exit(1)

    return VERSION_PART_SEPARATOR.join(str(part) for part in parts)


def main() -> None:
    """CLI entry point for inspecting or updating the RouterShell version."""
    parser = argparse.ArgumentParser(
        description=(
            "Inspect or update the __version__ string in routershell_version.py and "
            "the [project].version field in pyproject.toml. "
            "Version format: MAJOR.MINOR.PATCH."
        )
    )
    parser.add_argument("version", nargs="?", help="Explicit version to set, e.g. 0.2.0.")
    parser.add_argument("--current", action="store_true", help="Show the current version and exit.")
    parser.add_argument("--next", choices=["major", "minor", "patch"], help="Compute and apply the next version.")
    parser.add_argument(
        "--version-files-only",
        action="store_true",
        help="Update only version files; skip README/doc tag rewrites.",
    )

    args = parser.parse_args()

    if args.current:
        if args.version is not None or args.next is not None:
            print("ERROR: --current cannot be combined with a version argument or --next.", file=sys.stderr)
            sys.exit(1)
        current = _read_current_version(VERSION_FILE_PATH)
        print(f"Current version: {current}")
        sys.exit(0)

    if args.next is not None:
        if args.version is not None:
            print("ERROR: --next cannot be combined with an explicit version argument.", file=sys.stderr)
            sys.exit(1)
        current = _read_current_version(VERSION_FILE_PATH)
        new_version = _compute_next_version(current, args.next)
    elif args.version is not None:
        current = _read_current_version(VERSION_FILE_PATH)
        new_version = args.version
        _validate_version_string(new_version)
    else:
        print("ERROR: You must specify --current, --next <mode>, or an explicit version.", file=sys.stderr)
        sys.exit(1)

    if current == new_version:
        print(f"No change: version is already {current}.")
        sys.exit(0)

    _write_new_version(VERSION_FILE_PATH, new_version)
    _write_new_pyproject_version(PYPROJECT_FILE_PATH, new_version)
    if not args.version_files_only:
        _update_tag_tokens(f"v{new_version}")
    print(f"Updated version: {current} -> {new_version}")


if __name__ == "__main__":
    main()
