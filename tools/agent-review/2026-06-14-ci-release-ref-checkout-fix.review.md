### Summary
Updated the GitHub Actions CI workflow to check out the exact triggering commit SHA and use Node 24-compatible GitHub Actions versions. Added workflow metadata coverage and documented the release ref ambiguity troubleshooting path.

### Modified Files
- .github/workflows/ci.yml
- tests/tools/test_ci_workflow.py
- doc/faq.md
- todo.md

### Commands Executed And Results
- `curl https://api.github.com/repos/mgarcia01752/RouterShell/actions/runs/27504184230/jobs` -> pass, all 8 matrix jobs failed at `Run tests`.
- `git ls-remote --heads --tags https://github.com/mgarcia01752/RouterShell.git 'v0.1.6' ...` -> pass, found both `refs/heads/v0.1.6` and `refs/tags/v0.1.6`.
- Clean clone checkout of exact release commit `b895a98bb8d9f6e16f555bf386e0a213caa75b05`, editable install, and `pytest -q` -> pass, 56 passed.
- `python -m pytest tests/tools/test_ci_workflow.py -q` -> pass, 2 passed.
- `python -m pytest -q` -> pass, 56 passed.
- `python -m ruff check .` -> pass, all checks passed.
- `bash -n tools/vm/*.sh install/install.sh install/uninstall.sh tools/maintenance/clean.sh` -> pass.
- Python 3.10 syntax parse with `ast.parse(..., feature_version=(3, 10))` -> pass.

### Tests
- `pytest` -> pass, 56 passed.
- `ruff` -> pass, all checks passed.
- `bash -n` -> pass for VM, install, uninstall, and maintenance scripts.
- Python 3.10 syntax parse -> pass.

### Notes / Warnings
- GitHub job logs still require sign-in/admin access; public annotations only reported `Process completed with exit code 1`.
- Public refs currently include both a branch and an annotated tag named `v0.1.6`; CI now uses `ref: ${{ github.sha }}` to avoid ambiguous checkout behavior.
- `actions/checkout@v5` and `actions/setup-python@v6` are used to address the Node 20 deprecation warning shown in the job.

### Remaining TODOs / Follow-Ups
- Re-run CI on GitHub to verify the matrix passes with exact-SHA checkout.
- Consider deleting or renaming the stale remote branch `v0.1.6` so it no longer collides with the release tag.

# FILE: .github/workflows/ci.yml
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Maurice Garcia

name: CI

on:
  push:
  pull_request:

permissions:
  contents: read

jobs:
  python:
    name: Python ${{ matrix.python-version }} on ${{ matrix.os }}
    runs-on: ${{ matrix.os }}

    strategy:
      fail-fast: false
      matrix:
        os:
          - ubuntu-22.04
          - ubuntu-24.04
        python-version:
          - "3.10"
          - "3.11"
          - "3.12"
          - "3.13"

    steps:
      - name: Check out repository
        uses: actions/checkout@v5
        with:
          ref: ${{ github.sha }}

      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip

      - name: Install package
        run: |
          python -m pip install --upgrade pip
          python -m pip install -e ".[dev]"

      - name: Run tests
        run: python -m pytest -q

      - name: Run Ruff
        run: python -m ruff check .

      - name: Validate shell scripts
        run: bash -n tools/vm/*.sh install/install.sh

# FILE: tests/tools/test_ci_workflow.py
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
    assert "actions/checkout@v5" in workflow
    assert "ref: ${{ github.sha }}" in workflow
    assert "actions/setup-python@v6" in workflow
    assert "python -m pytest -q" in workflow
    assert "python -m ruff check ." in workflow
    assert "bash -n tools/vm/*.sh install/install.sh" in workflow

# FILE: doc/faq.md
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright (c) 2026 Maurice Garcia -->

# RouterShell FAQ

## Python 3.10 CI fails with missing tomllib

If the Python 3.10 GitHub Actions job fails during `python -m pytest -q` with
this error:

```text
ModuleNotFoundError: No module named 'tomllib'
```

make sure RouterShell includes the Python 3.10 TOML backport dependency and
uses the compatibility import fallback:

```python
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
```

The `tomllib` module is built into Python 3.11 and newer. Python 3.10 needs
`tomli`, which is installed through the conditional `pyproject.toml`
dependency.

## Release CI checks out an ambiguous version ref

If every GitHub Actions matrix job fails at `python -m pytest -q` after a
release push, check whether a branch and tag share the same version name, such
as `v0.1.6`. Ambiguous release refs can make checkout behavior harder to
reason about.

RouterShell CI checks out the exact triggering commit SHA:

```yaml
ref: ${{ github.sha }}
```

Keep the workflow on Node 24-compatible action versions, such as
`actions/checkout@v5` and `actions/setup-python@v6`, so runner deprecation
warnings do not hide the real test failure.

## Install fails with setuptools InvalidConfigError

If `sudo ./install/install.sh --development` fails while getting editable
build requirements and reports this error:

```text
setuptools.errors.InvalidConfigError: License classifiers have been superseded by license expressions
```

Update RouterShell to a version whose `pyproject.toml` uses the SPDX
`license = "Apache-2.0"` expression without deprecated license classifiers,
then rerun the installer:

```bash
sudo ./install/install.sh --development
```

This error is raised by newer setuptools releases during package metadata
validation.

## VSCode reports unresolved RouterShell imports

If VSCode or Pylance reports unresolved imports for `routershell` or
`tools.release.qa_checker`, reload the VSCode window after opening the
RouterShell workspace. The workspace settings select the installed development
interpreter at `/opt/routershell/venv/bin/python` and add the project `src`
layout plus release tooling paths to Python analysis.

If command-line Pyright is also needed, reinstall development extras:

```bash
/opt/routershell/venv/bin/python -m pip install -e ".[dev]"
```

If VSCode reports a Pylint `E0401:import-error` for a RouterShell module such
as `routershell.lib.cli.base.clear_mode`, make sure the workspace is using the
RouterShell interpreter and reload VSCode. The workspace settings configure the
Pylint extension to run from `/opt/routershell/venv/bin/python` with the
project `src` layout on the import path.

If the Pylint extension reports that Pylint is missing, refresh development
dependencies in the installer-created virtual environment:

```bash
sudo /opt/routershell/venv/bin/python -m pip install -e ".[dev]"
```

## RouterShell fails with unable to open database file

If `routershell` exits during startup with this error:

```text
RouterShellDB - ERROR - Error: unable to open database file
AttributeError: 'NoneType' object has no attribute 'cursor'
```

the launcher is missing a writable `ROUTERSHELL_DB_FILE` setting or is using an
older install. Reinstall RouterShell so the launcher-loaded env file gets any
missing required keys and the installed package receives the current DB path
code:

```bash
sudo ./install/install.sh --development
```

For local/development installs, the default database path is
`.routershell/routershell.db` under the project root. For production installs,
the default path is `/var/lib/routershell/routershell.db`.

## Interface database is empty after install

`routershell` should seed the interface database during startup when the
database has no interface records. Start the CLI normally:

```bash
routershell
```

Then verify the discovered interfaces:

```text
show interface database
```

If the database is still empty, confirm that the launcher-loaded environment
file defines a writable `ROUTERSHELL_DB_FILE` path and reinstall with the
current installer.

## Running configuration shows hostname None

If `show running-config` displays this line:

```text
hostname None
```

the runtime database is missing a RouterShell hostname value. Current
RouterShell startup seeds the hostname database value from the operating system
when it is blank, and running configuration output falls back to the OS
hostname instead of rendering `None`.

Start RouterShell normally, then check the running configuration again:

```bash
routershell
```

```text
show running-config
```

# FILE: todo.md
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright (c) 2026 Maurice Garcia -->

# RouterShell TODO

- Keep Python-version compatibility troubleshooting notes current when CI
  compatibility errors are fixed.
- Keep release-ref troubleshooting notes current when CI checkout behavior
  changes.
- Keep install troubleshooting notes current when installer errors are fixed.
- Keep IDE import troubleshooting notes current when workspace settings change.
- Keep runtime database troubleshooting notes current when DB path handling changes.
- Keep runtime display troubleshooting notes current when CLI output renders missing DB values.
