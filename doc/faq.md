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
