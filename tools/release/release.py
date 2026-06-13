#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2026 Maurice Garcia

"""RouterShell release automation."""

from __future__ import annotations

import argparse
import atexit
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Final

BUMP_SCRIPT_PATH: Final[Path] = Path("tools/support") / "bump_version.py"
PYPROJECT_FILE_PATH: Final[Path] = Path("pyproject.toml")
README_FILE_PATH: Final[Path] = Path("README.md")
DOCS_ROOT: Final[Path] = Path("doc")
WORKFLOWS_DIR: Final[Path] = Path(".github") / "workflows"
README_TAG_PATTERN: Final[re.Pattern[str]] = re.compile(r'TAG="v\d+\.\d+\.\d+(?:-rc\d+)?"')

VERSION_PART_SEPARATOR: Final[str] = "."
EXPECTED_VERSION_PARTS: Final[int] = 3
MAJOR_INDEX: Final[int] = 0
MINOR_INDEX: Final[int] = 1
PATCH_INDEX: Final[int] = 2
RC_SUFFIX_PREFIX: Final[str] = "-rc"
RC_DEFAULT_NUMBER: Final[int] = 1

REPORT_DIR_NAME: Final[str] = "release-reports"
REPORT_FILE_PREFIX: Final[str] = "release-report"
REPORT_SECTIONS: Final[list[str]] = [
    "Docs",
    "CLI",
    "Database",
    "Networking",
    "Services",
    "Install",
    "Packaging",
    "Tests",
    "Tools",
]
REPORT_HEADERS: Final[list[str]] = ["Section", "Files Changed"]

SUMMARY: dict[str, str] = {}
RELEASE_LOG_DIR: Path | None = None


def _run(
    cmd: list[str],
    check: bool = True,
    *,
    label: str | None = None,
    capture_output: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Run a subprocess command, capturing output for logging on failure."""
    if capture_output:
        proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    else:
        proc = subprocess.run(cmd, text=True, check=False)

    if proc.returncode != 0:
        if capture_output:
            _log_command_failure(label or Path(cmd[0]).name, proc)
        if check:
            raise subprocess.CalledProcessError(proc.returncode, cmd, output=proc.stdout, stderr=proc.stderr)
    return proc


def _init_release_logging() -> None:
    """Create a temporary directory for failed-command logs."""
    global RELEASE_LOG_DIR
    if RELEASE_LOG_DIR is not None:
        return
    logs_dir = Path(REPORT_DIR_NAME) / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    RELEASE_LOG_DIR = Path(tempfile.mkdtemp(prefix="routershell-release-logs-", dir=str(logs_dir)))
    print(f"[release] Command failures will be logged under: {RELEASE_LOG_DIR}")


def _sanitize_label(label: str) -> str:
    """Return a filesystem-safe label."""
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", label.strip().lower())
    return safe or "cmd"


def _log_command_failure(label: str, result: subprocess.CompletedProcess[str]) -> None:
    """Write stdout and stderr for a failed command."""
    if RELEASE_LOG_DIR is None:
        return
    safe_label = _sanitize_label(label)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = RELEASE_LOG_DIR / f"{safe_label}-{timestamp}.log"
    stdout = result.stdout or ""
    stderr = result.stderr or ""
    args = result.args if isinstance(result.args, list | tuple) else [str(result.args)]
    log_path.write_text(
        f"$ {' '.join(str(arg) for arg in args)}\n\nSTDOUT:\n{stdout}\n\nSTDERR:\n{stderr}\n",
        encoding="utf-8",
    )
    print(f"[release] {label} failed; see {log_path}")


def _format_state(state: str) -> str:
    """Format a release step state."""
    return state.upper()


def _print_status(label: str, state: str) -> None:
    """Record and print a release step status."""
    SUMMARY[label] = state
    print(f"{_format_state(state)} {label}")


def _print_release_summary() -> None:
    """Print the final release step summary."""
    if not SUMMARY:
        return
    print("\nRelease step summary:")
    for label, state in SUMMARY.items():
        print(f" {_format_state(state)} {label}")
    if RELEASE_LOG_DIR:
        print(f"Failure logs, if any, stored in: {RELEASE_LOG_DIR}")


atexit.register(_print_release_summary)


def _ensure_git_repo() -> None:
    """Ensure the current directory is inside a git repository."""
    result = _run(["git", "rev-parse", "--is-inside-work-tree"], check=False, label="git-repo")
    if result.returncode != 0:
        print("ERROR: release must run inside a git repository.", file=sys.stderr)
        sys.exit(1)


def _ensure_clean_worktree() -> None:
    """Ensure the git working tree has no uncommitted changes."""
    result = _run(["git", "status", "--porcelain"], check=False, label="git-status")
    output = (result.stdout or "").strip()
    if output:
        print("ERROR: Working tree is not clean. Commit or stash changes first.", file=sys.stderr)
        sys.exit(1)


def _get_current_branch() -> str:
    """Return the current branch name."""
    result = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], label="git-branch")
    return result.stdout.strip()


def _ensure_release_branch_allowed() -> None:
    """Fail fast unless running on an allowed release branch."""
    current_branch = _get_current_branch()
    if current_branch not in ("main", "hot-fix"):
        print("ERROR: release can only be performed on 'main' or 'hot-fix'.", file=sys.stderr)
        sys.exit(1)


def _get_head_commit() -> str:
    """Return the current HEAD commit."""
    result = _run(["git", "rev-parse", "HEAD"], label="git-rev-parse")
    return result.stdout.strip()


def _get_previous_commit() -> str | None:
    """Return the previous commit if one exists."""
    result = _run(["git", "rev-parse", "HEAD~1"], check=False, label="git-rev-parse-prev")
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def _collect_commit_files(commit: str) -> list[str]:
    """Collect file paths touched by a commit."""
    result = _run(["git", "show", "--pretty=format:", "--name-only", commit], label="git-show")
    return [line.strip() for line in (result.stdout or "").splitlines() if line.strip()]


def _classify_path(path: str) -> str:
    """Classify a changed path for release reporting."""
    normalized = path.replace("\\", "/").lower()
    if normalized.startswith("doc/") or normalized == "readme.md":
        return "Docs"
    if normalized.startswith("lib/cli/") or normalized.startswith("src/") or normalized == "routershell/cli.py":
        return "CLI"
    if normalized.startswith("lib/db/"):
        return "Database"
    if normalized.startswith("lib/network_manager/"):
        return "Networking"
    if normalized.startswith("lib/network_services/") or normalized.startswith("lib/system/"):
        return "Services"
    if normalized.startswith("install/") or normalized == "start.sh":
        return "Install"
    if normalized in {"pyproject.toml", "routershell/_version.py", "routershell/__init__.py"}:
        return "Packaging"
    if normalized.startswith("tests/"):
        return "Tests"
    if normalized.startswith("tools/"):
        return "Tools"
    return "Other"


def _summarize_sections(paths: list[str]) -> dict[str, int]:
    """Count changed files by report section."""
    counts = {section: 0 for section in REPORT_SECTIONS}
    counts["Other"] = 0
    for path in paths:
        section = _classify_path(path)
        counts[section] = counts.get(section, 0) + 1
    return counts


def _render_markdown_table(counts: dict[str, int]) -> str:
    """Render a markdown table for section counts."""
    rows = [(section, str(counts.get(section, 0))) for section in REPORT_SECTIONS]
    if counts.get("Other", 0) > 0:
        rows.append(("Other", str(counts["Other"])))
    lines = [f"| {REPORT_HEADERS[0]} | {REPORT_HEADERS[1]} |", "| --- | --- |"]
    lines.extend(f"| {section} | {count} |" for section, count in rows)
    return "\n".join(lines)


def _collect_workflows() -> list[tuple[str, str]]:
    """Collect GitHub workflow names and paths."""
    if not WORKFLOWS_DIR.exists():
        return []
    workflows: list[tuple[str, str]] = []
    for path in sorted(list(WORKFLOWS_DIR.glob("*.yml")) + list(WORKFLOWS_DIR.glob("*.yaml"))):
        workflows.append((path.name, os.path.relpath(path, Path.cwd())))
    return workflows


def _write_release_report(commit: str, version: str, tag_name: str, branch: str, report_mode: str) -> Path:
    """Write a markdown release or commit report."""
    report_dir = Path(REPORT_DIR_NAME)
    report_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    report_path = report_dir / f"{REPORT_FILE_PREFIX}-{version}-{timestamp}.md"
    files = sorted(_collect_commit_files(commit))
    counts = _summarize_sections(files)
    workflows = _collect_workflows()

    lines = [
        f"# RouterShell {report_mode} report",
        "",
        f"- Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"- Branch: {branch}",
        f"- Source commit: `{commit}`",
        f"- Release version: `{version}`",
        f"- Release tag: `{tag_name}`",
        "",
        "## Workflows",
        "",
    ]
    if workflows:
        lines.extend(f"- `{name}` (`{path}`)" for name, path in workflows)
    else:
        lines.append("_No workflows found._")

    lines.extend(["", "## Change Summary", "", _render_markdown_table(counts), "", "## Files", ""])
    if files:
        lines.extend(f"- `{path}`" for path in files)
    else:
        lines.append("_No files detected._")
    lines.append("")

    if SUMMARY:
        lines.extend(["## Release Step Summary", ""])
        lines.extend(f"- {state.upper()} {label}" for label, state in SUMMARY.items())
        lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def _read_pyproject_version() -> str:
    """Read the [project].version value from pyproject.toml."""
    if not PYPROJECT_FILE_PATH.exists():
        print(f"ERROR: pyproject.toml not found: {PYPROJECT_FILE_PATH}", file=sys.stderr)
        sys.exit(1)
    text = PYPROJECT_FILE_PATH.read_text(encoding="utf-8")
    match = re.search(r'^\s*version\s*=\s*"([^"]+)"\s*$', text, re.MULTILINE)
    if not match:
        print(f"ERROR: Could not find [project].version in {PYPROJECT_FILE_PATH}.", file=sys.stderr)
        sys.exit(1)
    return match.group(1)


def _validate_version_string(version: str) -> None:
    """Validate MAJOR.MINOR.PATCH version strings."""
    core_version = version.split(RC_SUFFIX_PREFIX, 1)[0]
    parts = core_version.split(VERSION_PART_SEPARATOR)
    if len(parts) != EXPECTED_VERSION_PARTS or not all(part.isdigit() for part in parts):
        print(f"ERROR: Invalid version '{version}'. Expected MAJOR.MINOR.PATCH.", file=sys.stderr)
        sys.exit(1)


def _parse_version_parts(version: str) -> list[int]:
    """Parse a semantic version into numeric parts."""
    _validate_version_string(version)
    core_version = version.split(RC_SUFFIX_PREFIX, 1)[0]
    return [int(part) for part in core_version.split(VERSION_PART_SEPARATOR)]


def _compute_next_version(current_version: str, mode: str) -> str:
    """Compute the next semantic version."""
    parts = _parse_version_parts(current_version)
    match mode:
        case "major":
            parts[MAJOR_INDEX] += 1
            parts[MINOR_INDEX] = 0
            parts[PATCH_INDEX] = 0
        case "minor":
            parts[MINOR_INDEX] += 1
            parts[PATCH_INDEX] = 0
        case "patch":
            parts[PATCH_INDEX] += 1
        case _:
            print(f"ERROR: Unsupported next mode '{mode}'.", file=sys.stderr)
            sys.exit(1)
    return VERSION_PART_SEPARATOR.join(str(part) for part in parts)


def _update_version_files(new_version: str) -> None:
    """Update pyproject.toml via support tooling."""
    if not BUMP_SCRIPT_PATH.exists():
        print(f"ERROR: Version bump script not found: {BUMP_SCRIPT_PATH}", file=sys.stderr)
        sys.exit(1)
    _run([sys.executable, str(BUMP_SCRIPT_PATH), new_version, "--version-files-only"], label="bump-version")


def _update_readme_tag(new_tag: str) -> None:
    """Rewrite TAG placeholders to the new release tag in README and docs."""
    paths = [README_FILE_PATH]
    if DOCS_ROOT.exists():
        paths.extend(path for path in DOCS_ROOT.rglob("*.md") if path.is_file())

    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            continue
        updated_text, count = README_TAG_PATTERN.subn(f'TAG="{new_tag}"', text)
        if count:
            path.write_text(updated_text, encoding="utf-8")
            print(f"Updated TAG placeholders in {path} to {new_tag}")


def _ensure_virtualenv() -> None:
    """Ensure release is running inside a virtual environment."""
    if os.environ.get("VIRTUAL_ENV"):
        return
    if getattr(sys, "base_prefix", sys.prefix) != sys.prefix:
        return
    print("ERROR: Release must run inside a Python virtual environment.", file=sys.stderr)
    print("Suggested setup:", file=sys.stderr)
    print("  python3 -m venv .venv && . .venv/bin/activate && python -m pip install -e '.[dev]'", file=sys.stderr)
    sys.exit(1)


def _run_tests(skip_tests: bool) -> None:
    """Run pytest unless skipped."""
    if skip_tests:
        _print_status("Tests", "skip")
        return
    result = _run([sys.executable, "-m", "pytest"], check=False, label="pytest")
    if result.returncode != 0:
        print("ERROR: pytest failed. Aborting release.", file=sys.stderr)
        _print_status("Tests", "fail")
        sys.exit(result.returncode)
    _print_status("Tests", "pass")


def _run_ruff(skip_ruff: bool) -> None:
    """Run Ruff unless skipped."""
    if skip_ruff:
        _print_status("Ruff", "skip")
        return
    result = _run([sys.executable, "-m", "ruff", "check", "."], check=False, label="ruff")
    if result.returncode != 0:
        print("ERROR: Ruff failed. Aborting release.", file=sys.stderr)
        _print_status("Ruff", "fail")
        sys.exit(result.returncode)
    _print_status("Ruff", "pass")


def _run_build(skip_build: bool) -> None:
    """Run python -m build unless skipped."""
    if skip_build:
        _print_status("Build", "skip")
        return
    result = _run([sys.executable, "-m", "build"], check=False, label="build")
    if result.returncode != 0:
        print("ERROR: build failed. Aborting release.", file=sys.stderr)
        _print_status("Build", "fail")
        sys.exit(result.returncode)
    _print_status("Build", "pass")


def _run_version_check() -> None:
    """Run the release version consistency check."""
    result = _run([sys.executable, "tools/release/check_version.py"], check=False, label="check-version")
    if result.returncode != 0:
        print(result.stdout or "", end="")
        print(result.stderr or "", end="", file=sys.stderr)
        _print_status("Version check", "fail")
        sys.exit(result.returncode)
    _print_status("Version check", "pass")


def _commit_version_bump(new_version: str) -> None:
    """Commit version bump files."""
    _run(["git", "add", str(PYPROJECT_FILE_PATH), str(README_FILE_PATH), str(DOCS_ROOT)], label="git-add")
    _run(["git", "commit", "-m", f"Release {new_version}"], label="git-commit")


def _create_tag(new_version: str, tag_prefix: str, tag_suffix: str = "") -> str:
    """Create an annotated git tag."""
    tag_name = f"{tag_prefix}{new_version}{tag_suffix}"
    _run(["git", "tag", "-a", tag_name, "-m", f"Release {new_version}"], label="git-tag")
    return tag_name


def _push_branch_and_tag(branch: str, tag_name: str) -> None:
    """Push release branch and tag."""
    _run(["git", "push", "origin", branch], label="git-push-branch")
    _run(["git", "push", "origin", tag_name], label="git-push-tag")


def _build_parser() -> argparse.ArgumentParser:
    """Build the release CLI parser."""
    parser = argparse.ArgumentParser(description="Automate a RouterShell release.")
    parser.add_argument("--version", help="Explicit release version in MAJOR.MINOR.PATCH format.")
    parser.add_argument("--next", choices=["major", "minor", "patch"], help="Compute the next version.")
    parser.add_argument("--branch", default="main", help="Branch to release from.")
    parser.add_argument("--tag-prefix", default="v", help="Prefix for git tags.")
    parser.add_argument("--skip-tests", action="store_true", help="Skip pytest.")
    parser.add_argument("--skip-ruff", action="store_true", help="Skip Ruff.")
    parser.add_argument("--skip-build", action="store_true", help="Skip python -m build.")
    parser.add_argument("--test-release", action="store_true", help="Run checks and restore previous version.")
    parser.add_argument("--dry-run", action="store_true", help="Show planned actions without modifying files.")
    parser.add_argument("--last-commit-report", action="store_true", help="Generate a report for HEAD~1.")
    parser.add_argument("--latest-commit-report", action="store_true", help="Generate a report for HEAD.")
    return parser


def main() -> None:
    """Run RouterShell release automation."""
    _ensure_git_repo()
    args = _build_parser().parse_args()

    if args.last_commit_report and args.latest_commit_report:
        print("ERROR: report modes cannot be combined.", file=sys.stderr)
        sys.exit(1)

    current_branch = _get_current_branch()
    if args.last_commit_report or args.latest_commit_report:
        target_commit = _get_previous_commit() if args.last_commit_report else _get_head_commit()
        if not target_commit:
            print("ERROR: unable to resolve report commit.", file=sys.stderr)
            sys.exit(1)
        version = _read_pyproject_version()
        mode = "last-commit" if args.last_commit_report else "latest-commit"
        report_path = _write_release_report(target_commit, version, "n/a", current_branch, mode)
        print(f"Commit report saved to {report_path}")
        return

    current_version = _read_pyproject_version()

    if args.version and args.next:
        print("ERROR: --version and --next cannot be used together.", file=sys.stderr)
        sys.exit(1)

    new_version = args.version if args.version else _compute_next_version(current_version, args.next or "patch")
    _validate_version_string(new_version)
    if new_version == current_version:
        print(f"No change: version is already {current_version}.")
        return

    release_tag = f"{args.tag_prefix}{new_version}"
    if args.dry_run:
        print("Dry run: the following actions would be performed:")
        print("  1) Ensure git working tree is clean")
        print(f"  2) Update version {current_version} -> {new_version}")
        print(f"  3) Update README/doc TAG placeholders to {release_tag}")
        print("  4) Run version check")
        if not args.skip_tests:
            print("  5) Run pytest")
        if not args.skip_ruff:
            print("  6) Run Ruff")
        if not args.skip_build:
            print("  7) Build distribution artifacts")
        if args.test_release:
            print(f"  8) Restore version files back to {current_version}")
        else:
            print(f"  8) Commit version bump, tag {release_tag}, and push")
        return

    _ensure_release_branch_allowed()
    if args.branch != current_branch:
        print(
            f"ERROR: --branch must match the current branch ({current_branch}); got {args.branch}.",
            file=sys.stderr,
        )
        sys.exit(1)
    _ensure_virtualenv()
    _init_release_logging()
    _ensure_clean_worktree()

    print(f"Current version: {current_version}")
    print(f"Planned version: {new_version}")
    answer = input("Proceed with release? [y/N]: ").strip().lower()
    if answer not in ("y", "yes"):
        print("Aborted.")
        sys.exit(1)

    report_commit = _get_head_commit()
    _update_version_files(new_version)
    _update_readme_tag(release_tag)
    _run_version_check()
    _run_tests(args.skip_tests)
    _run_ruff(args.skip_ruff)
    _run_build(args.skip_build)

    if args.test_release:
        print("Restoring version files after test release.")
        _update_version_files(current_version)
        _update_readme_tag(f"{args.tag_prefix}{current_version}")
        _print_status("Commit", "skip")
        _print_status("Tag", "skip")
        _print_status("Push", "skip")
        return

    _commit_version_bump(new_version)
    tag_name = _create_tag(new_version, args.tag_prefix)
    _push_branch_and_tag(args.branch, tag_name)
    _print_status("Release report", "pass")
    report_path = _write_release_report(report_commit, new_version, tag_name, args.branch, "release")
    print(f"Release report saved to {report_path}")
    print(f"Release {new_version} completed on branch '{args.branch}' with tag '{tag_name}'.")


if __name__ == "__main__":
    main()
