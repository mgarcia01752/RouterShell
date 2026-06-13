# RouterShell Software QA Checker

RouterShell includes a lightweight software QA checker for local development
and simple CI pipelines.

Install development dependencies first:

```bash
python -m pip install -e ".[dev]"
```

Run the standard QA suite:

```bash
routershell-software-qa-checker
```

The checker source lives under `tools/release/qa_checker.py`.

The default suite runs:

- pyproject console-script metadata sanity check
- version consistency check
- Python source compilation
- shell script syntax checks
- Ruff
- pytest
- pycycle import cycle detection, when installed

Include Pyright static type checking with:

```bash
routershell-software-qa-checker --with-pyright
```

Skip pycycle when needed:

```bash
routershell-software-qa-checker --skip-pycycle
```

Pass additional arguments to pytest after `--`:

```bash
routershell-software-qa-checker -- -k typing --maxfail=1
```

The command exits with `0` when all selected checks pass. It returns the first
non-zero exit code when any selected check fails.
