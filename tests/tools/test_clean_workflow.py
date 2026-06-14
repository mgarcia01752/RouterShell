"""Maintenance cleanup script tests."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CLEAN_SCRIPT = REPO_ROOT / "tools" / "maintenance" / "clean.sh"
MAINTENANCE_README = REPO_ROOT / "tools" / "maintenance" / "README.md"
TOOLS_LAYOUT = REPO_ROOT / "tools" / "reference" / "tools-layout.md"


def test_clean_script_is_valid_bash() -> None:
    subprocess.run(
        ["bash", "-n", str(CLEAN_SCRIPT)],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )


def test_clean_script_documents_expected_router_shell_actions() -> None:
    clean_script = CLEAN_SCRIPT.read_text()

    assert "--python" in clean_script
    assert "--build" in clean_script
    assert "--runtime" in clean_script
    assert "--release" in clean_script
    assert "--agent-review" in clean_script
    assert "--vm" in clean_script
    assert "--all" in clean_script
    assert "--all-force" in clean_script


def test_clean_script_preserves_virtualenv_while_cleaning_python_cache() -> None:
    clean_script = CLEAN_SCRIPT.read_text()

    assert '-path "${ROOT_DIR}/.venv" -prune' in clean_script
    assert '-type d -name "__pycache__"' in clean_script
    assert '-type f -name "*.pyc"' in clean_script
    assert '"${ROOT_DIR}/.pytest_cache"' in clean_script
    assert '"${ROOT_DIR}/.ruff_cache"' in clean_script


def test_clean_script_removes_build_and_runtime_artifacts() -> None:
    clean_script = CLEAN_SCRIPT.read_text()

    assert '"${ROOT_DIR}/build"' in clean_script
    assert '"${ROOT_DIR}/dist"' in clean_script
    assert '"${ROOT_DIR}/src"/*.egg-info' in clean_script
    assert '"${ROOT_DIR}/.routershell"' in clean_script
    assert '"${ROOT_DIR}/release-reports"' in clean_script
    assert '"${ROOT_DIR}/tools/agent-review"/*.review.md' in clean_script


def test_clean_all_delegates_vm_cleanup_to_vm_script() -> None:
    clean_script = CLEAN_SCRIPT.read_text()

    assert 'vm_cleanup_script="${ROOT_DIR}/tools/vm/multipass-cleanup.sh"' in clean_script
    assert '"${vm_cleanup_script}" --all --purge' in clean_script
    assert "clean_vm" in clean_script


def test_clean_all_preserves_agent_review_until_all_force() -> None:
    clean_script = CLEAN_SCRIPT.read_text()
    all_block = clean_script.split('    --all)\n', maxsplit=1)[1].split("      ;;\n", maxsplit=1)[0]
    all_force_block = clean_script.split('    --all-force)\n', maxsplit=1)[1].split("      ;;\n", maxsplit=1)[0]

    assert "clean_agent_review" not in all_block
    assert "clean_agent_review" in all_force_block


def test_tools_layout_documents_maintenance_category() -> None:
    tools_layout = TOOLS_LAYOUT.read_text()

    assert "`maintenance/`" in tools_layout
    assert "Repository cleanup helpers" in tools_layout


def test_maintenance_readme_documents_vm_cleanup_delegation() -> None:
    maintenance_readme = MAINTENANCE_README.read_text()

    assert "tools/maintenance/clean.sh --all" in maintenance_readme
    assert "tools/maintenance/clean.sh --all-force" in maintenance_readme
    assert "tools/vm/multipass-cleanup.sh --all --purge" in maintenance_readme
    assert "does not remove the project `.venv`" in maintenance_readme
