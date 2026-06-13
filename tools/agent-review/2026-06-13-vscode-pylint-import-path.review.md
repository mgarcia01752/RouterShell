### Summary
VSCode Pylint configuration now matches the RouterShell src-layout and installed development interpreter. Pylint is included in development extras, and the FAQ documents how to resolve Pylint E0401 import warnings for RouterShell modules.

### Modified Files
- pyproject.toml
- .vscode/settings.json
- doc/faq.md

### Commands Executed And Results
- `/opt/routershell/venv/bin/python - <<'PY' ...` -> pass; verified Pylint settings and dev dependency metadata
- `PYTHONPATH=src /opt/routershell/venv/bin/python - <<'PY' ...` -> pass; resolved routershell.lib.cli.base.clear_mode from src
- `/opt/routershell/venv/bin/python -m pip install -e ".[dev]"` -> fail; root-owned src/routershell.egg-info blocked editable metadata update
- `/opt/routershell/venv/bin/python -m pip install "pylint>=3.3"` -> fail; /opt/routershell/venv site-packages is root-owned
- `/opt/routershell/venv/bin/python tools/release/qa_checker.py --skip-pycycle` -> pass; Ruff passed and pytest passed with 18 tests

### Tests
- `tools/release/qa_checker.py --skip-pycycle` -> pass; includes compileall, shell syntax, Ruff, and pytest
- `pytest` -> pass; 18 tests passed through the QA checker
- `ruff` -> pass; All checks passed through the QA checker

### Notes / Warnings
- The installer-created virtual environment at /opt/routershell/venv is root-owned, so installing Pylint there requires sudo.
- src/routershell.egg-info is ignored generated metadata but is currently root-owned from a previous sudo editable install.
- Reload VSCode after the settings change so the Pylint extension restarts with the configured interpreter.

### Remaining TODOs / Follow-Ups
- Run `sudo /opt/routershell/venv/bin/python -m pip install -e ".[dev]"` if the VSCode Pylint extension reports that Pylint is missing.

# FILE: pyproject.toml
# SPDX-License-Identifier: Apache-2.0

[build-system]
requires = ["setuptools>=77", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "routershell"
version = "0.1.0"
description = "IOS-like Python CLI distribution for Linux router configuration workflows."
readme = "README.md"
requires-python = ">=3.10"
license = "Apache-2.0"
license-files = ["LICENSE", "NOTICE"]
authors = [
    { name = "Maurice Garcia" },
]
keywords = [
    "cli",
    "linux",
    "networking",
    "router",
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: System Administrators",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: System :: Networking",
    "Topic :: System :: Systems Administration",
    "Typing :: Typed",
]
dependencies = [
    "argcomplete>=3.0",
    "beautifulsoup4>=4.12",
    "cmd2>=2.4",
    "jc>=1.25",
    "prettytable>=3.0",
    "prompt-toolkit>=3.0",
    "pyte>=0.8",
    "tabulate>=0.9",
]

[project.optional-dependencies]
dev = [
    "build>=1.2",
    "pycycle>=0.0.8",
    "pyright>=1.1.407",
    "pylint>=3.3",
    "pytest>=8.0",
    "ruff>=0.5",
    "twine>=5.0",
]

[project.scripts]
routershell = "routershell.cli:main"
routershell-factory-reset = "routershell.cli:factory_reset"
routershell-software-qa-checker = "tools.release.qa_checker:main"

[project.urls]
Homepage = "https://github.com/mgarcia01752/RouterShell"
Repository = "https://github.com/mgarcia01752/RouterShell"

[tool.setuptools]
package-dir = { "" = "src" }
include-package-data = true

[tool.setuptools.packages.find]
where = ["src"]
include = ["routershell*"]
namespaces = true

[tool.setuptools.package-data]
"routershell" = ["py.typed"]
"routershell.lib.db.sqlite_db" = ["*.sql"]
"routershell.lib.network_services.dhcp.dnsmasq" = ["*.conf"]

[tool.pytest.ini_options]
addopts = "-ra"
pythonpath = [
    "src",
]
testpaths = [
    "tests",
]

[tool.ruff]
src = ["src"]
target-version = "py310"
line-length = 120
exclude = [
    "tools",
    "src/routershell/lib/cli/config-bak",
    "**/*-bak.py",
    "**/*-orig.py",
]

[tool.ruff.lint]
select = [
    "F",
    "E",
    "W",
    "I",
    "B",
    "UP",
    "ANN",
    "SIM",
    "PERF",
]
ignore = [
    "E501",
    "B006",
    "ANN001",
    "ANN002",
    "ANN003",
    "ANN201",
    "ANN202",
    "ANN204",
    "ANN205",
    "ANN206",
    "W291",
    "W292",
    "W293",
    "B007",
    "B018",
    "B024",
    "B904",
    "E711",
    "F811",
    "F841",
    "SIM",
    "PERF",
    "UP022",
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = [
    "ANN",
]

[tool.pyright]
pythonVersion = "3.10"
pythonPlatform = "Linux"
include = [
    "src",
    "tests",
    "tools/release",
]
extraPaths = [
    "src",
    ".",
]
exclude = [
    "**/__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "build",
    "dist",
]

# FILE: .vscode/settings.json
{
    "python.defaultInterpreterPath": "/opt/routershell/venv/bin/python",
    "python.analysis.extraPaths": [
        "${workspaceFolder}/src",
        "${workspaceFolder}"
    ],
    "python.analysis.include": [
        "src",
        "tests",
        "tools/release"
    ],
    "python.analysis.exclude": [
        "**/__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        "build",
        "dist"
    ],
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.pytestArgs": [
        "tests"
    ],
    "pylint.interpreter": [
        "/opt/routershell/venv/bin/python"
    ],
    "pylint.importStrategy": "fromEnvironment",
    "pylint.args": [
        "--init-hook=import sys; from pathlib import Path; root = Path.cwd(); sys.path[:0] = [str(root / 'src'), str(root)]"
    ],
    "python-envs.pythonProjects": [
        {
            "path": ".",
            "envManager": "ms-python.python:venv",
            "packageManager": "ms-python.python:pip"
        }
    ]
}

# FILE: doc/faq.md
# RouterShell FAQ

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

