<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright (c) 2026 Maurice Garcia -->

# RouterShell Python Development

RouterShell includes Python packaging metadata in `pyproject.toml`.

For installer-managed local development, use the local environment install:

```bash
sudo ./install/install.sh --local-env
.venv/bin/python -m pytest
```

For manual local development, use an isolated virtual environment and install
the project in editable mode:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

After installation, run the CLI entry point:

```bash
routershell
```

Factory reset is also exposed as a console entry point:

```bash
routershell-factory-reset
```

Runtime logs default to `/tmp/log/routershell.log`. Override logging for one
run with environment variables such as:

```bash
ROUTERSHELL_LOG_LEVEL=DEBUG routershell
```

Build distribution artifacts with:

```bash
python -m build
```

Run validation with:

```bash
python -m pytest
python -m ruff check .
```

Or run the standard software QA sweep with:

```bash
routershell-software-qa-checker
```

See [RouterShell Software QA Checker](../tests/software-qa.md) for the full
check sequence and options.
