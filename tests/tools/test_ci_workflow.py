"""CI workflow metadata tests."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
README = REPO_ROOT / "README.md"
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"


def test_readme_documents_supported_platforms() -> None:
    readme = README.read_text()

    assert "actions/workflows/ci.yml/badge.svg" in readme
    assert "python-3.10--3.13-blue" in readme
    assert "ubuntu-22.04%20%7C%2024.04-orange" in readme
    assert "Ubuntu 22.04 LTS" in readme
    assert "Ubuntu 24.04 LTS" in readme
    assert "Python 3.10 through Python 3.13" in readme


def test_ci_workflow_covers_supported_matrix() -> None:
    workflow = CI_WORKFLOW.read_text()

    assert "ubuntu-22.04" in workflow
    assert "ubuntu-24.04" in workflow
    assert '"3.10"' in workflow
    assert '"3.11"' in workflow
    assert '"3.12"' in workflow
    assert '"3.13"' in workflow
    assert "python -m pytest -q" in workflow
    assert "python -m ruff check ." in workflow
    assert "bash -n tools/vm/*.sh install/install.sh" in workflow
