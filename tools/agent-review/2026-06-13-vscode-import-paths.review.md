### Summary
VSCode and Pyright configuration now match the RouterShell src-layout, test suite, and root release tooling imports. The workspace settings point VSCode at the installed RouterShell development interpreter under /opt/routershell/venv, and the FAQ documents the import warning recovery path.

### Modified Files
- pyproject.toml
- .vscode/settings.json
- doc/faq.md
- todo.md

### Commands Executed And Results
- `/opt/routershell/venv/bin/python - <<'PY' ...` -> pass; pyproject.toml and .vscode/settings.json parsed successfully
- `/opt/routershell/venv/bin/python - <<'PY' ...` -> pass; imported routershell and tools.release.qa_checker
- `/opt/routershell/venv/bin/python -m pyright --version` -> fail; pyright is not installed in /opt/routershell/venv
- `/opt/routershell/venv/bin/python -m pip show pyright ruff pytest` -> pass; pyright missing, ruff and pytest installed
- `/opt/routershell/venv/bin/python tools/release/qa_checker.py --skip-pycycle` -> pass; Ruff passed and pytest passed with 14 tests

### Tests
- `tools/release/qa_checker.py --skip-pycycle` -> pass; includes compileall, shell syntax, Ruff, and pytest
- `pytest` -> pass; 14 tests passed through the QA checker
- `ruff` -> pass; All checks passed through the QA checker

### Notes / Warnings
- Command-line pyright is declared as a dev dependency but is not currently installed in /opt/routershell/venv.
- VSCode/Pylance should use the configured interpreter after reloading the window or selecting the interpreter.

### Remaining TODOs / Follow-Ups
- Reinstall dev extras if command-line pyright should be available: `/opt/routershell/venv/bin/python -m pip install -e ".[dev]"`

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
    "python-envs.pythonProjects": [
        {
            "path": ".",
            "envManager": "ms-python.python:system",
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

# FILE: todo.md
# RouterShell TODO

- Keep install troubleshooting notes current when installer errors are fixed.
- Keep IDE import troubleshooting notes current when workspace settings change.

