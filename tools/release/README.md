# RouterShell Release Helpers

These scripts provide the RouterShell release workflow adapted from the PyPNM
release tooling.

## Version Check

Verify that `routershell_version.py` and `pyproject.toml` agree:

```bash
./tools/release/check_version.py
```

JSON output is also available:

```bash
./tools/release/check_version.py --json
```

## Release Dry Run

Show the planned release steps without changing files:

```bash
./tools/release/release.py --next patch --dry-run
```

Supported version bump modes are:

```bash
--next major
--next minor
--next patch
```

An explicit version can also be supplied:

```bash
./tools/release/release.py --version 0.2.0 --dry-run
```

## Actual Release

Run from `main` or `hot-fix` with a clean working tree and an activated virtual
environment containing development dependencies:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
./tools/release/release.py --next patch
```

The release command updates version files, runs checks, commits the version
bump, creates an annotated tag, pushes the branch and tag, and writes a release
report under `release-reports/`.

Version updates are delegated to:

```bash
./tools/support/bump_version.py
```

Use this mode to test version changes and checks without committing or tagging:

```bash
./tools/release/release.py --next patch --test-release
```

## Commit Reports

Generate a release-style report for the current commit:

```bash
./tools/release/release.py --latest-commit-report
```

Generate a report for the previous commit:

```bash
./tools/release/release.py --last-commit-report
```

## Test Runner

Run unittest-compatible tests without pytest:

```bash
./tools/release/test-runner.py
```
