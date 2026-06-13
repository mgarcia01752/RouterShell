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
