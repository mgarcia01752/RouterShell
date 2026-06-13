### Summary
RouterShell git-save and git-push now run the release QA checker early before staging and committing. The shared git helper chooses the active/project virtual environment before system Python so Ruff and pytest are available for the QA gate.

### Modified Files
- tools/git/git-common.sh
- tools/git/git-save.sh
- tools/git/git-push.sh
- tools/git/README.md

### Commands Executed And Results
- `bash -n tools/git/git-common.sh tools/git/git-save.sh tools/git/git-push.sh` -> pass
- `bash -c 'source tools/git/git-common.sh; rs_python'` -> pass; /opt/routershell/venv/bin/python
- `bash -c 'source tools/git/git-common.sh; rs_run_quality_gates'` -> pass; QA checker passed with 14 tests
- `/opt/routershell/venv/bin/ruff check tools/git tools/release/qa_checker.py tests/tools/test_qa_checker.py pyproject.toml` -> pass; All checks passed

### Tests
- `rs_run_quality_gates` -> pass; invoked tools/release/qa_checker.py --skip-pycycle and ran 14 pytest tests
- `bash -n` -> pass for git helper scripts
- `ruff` -> pass for touched helper/tooling files

### Notes / Warnings
- Git helpers pass --skip-pycycle so saving/pushing does not require pycycle in the local environment.
- No commit or push command was executed during validation.

### Remaining TODOs / Follow-Ups
- None

# FILE: tools/git/git-common.sh
#!/usr/bin/env bash
set -euo pipefail

rs_run_check() {
  local label="$1"
  shift

  echo "[check] ${label}..."
  if "$@"; then
    echo "[pass]  ${label}"
  else
    echo "[fail]  ${label}" >&2
    exit 1
  fi
}

rs_require_git_repo() {
  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "ERROR: This script must be run inside a Git repository." >&2
    exit 1
  fi
}

rs_repo_root() {
  git rev-parse --show-toplevel
}

rs_python() {
  if [[ -n "${VIRTUAL_ENV:-}" && -x "${VIRTUAL_ENV}/bin/python" ]]; then
    printf '%s\n' "${VIRTUAL_ENV}/bin/python"
    return
  fi

  if [[ -x "/opt/routershell/venv/bin/python" ]]; then
    printf '%s\n' "/opt/routershell/venv/bin/python"
    return
  fi

  if [[ -x ".venv/bin/python" ]]; then
    printf '%s\n' ".venv/bin/python"
    return
  fi

  if command -v python >/dev/null 2>&1; then
    command -v python
    return
  fi

  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return
  fi

  echo "ERROR: python3 or python is required." >&2
  exit 1
}

rs_run_quality_gates() {
  local python_bin
  python_bin="$(rs_python)"

  rs_run_check "RouterShell software QA checker" "${python_bin}" tools/release/qa_checker.py --skip-pycycle
}

# FILE: tools/git/git-save.sh
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_NAME="$(basename "$0")"
SCRIPT_VERSION="v1.0.0"

usage() {
  cat <<'EOF'
Stage and commit the current RouterShell Git repository.

Usage:
  git-save.sh [--commit-msg "Message"] [--push] [--skip-checks]

Options:
  --commit-msg   Commit message prefix (default: "Update RouterShell").
  --push         Push the current branch after commit.
  --skip-checks  Skip local quality gates.
  -h, --help     Show this help.
  -v, --version  Show script version.
EOF
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/git-common.sh"

commit_msg="Update RouterShell"
do_push="false"
skip_checks="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --commit-msg)
      shift
      if [[ "${1:-}" == "" ]] || [[ "${1}" =~ ^[[:space:]]*$ ]]; then
        echo "ERROR: --commit-msg requires a non-empty value." >&2
        exit 1
      fi
      commit_msg="$1"
      shift
      ;;
    --push)
      do_push="true"
      shift
      ;;
    --skip-checks)
      skip_checks="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -v|--version)
      echo "${SCRIPT_NAME} ${SCRIPT_VERSION}"
      exit 0
      ;;
    *)
      echo "ERROR: Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

rs_require_git_repo
cd "$(rs_repo_root)"

current_branch="$(git rev-parse --abbrev-ref HEAD)"
if [[ "${current_branch}" == "HEAD" ]]; then
  echo "ERROR: Detached HEAD detected. Check out a branch before committing." >&2
  exit 1
fi

pending_changes="$(git status --short)"

echo "========================================"
echo "RouterShell Git Save"
echo "Branch: ${current_branch}"
echo "Changes:"
if [[ -z "${pending_changes}" ]]; then
  echo "  (none)"
else
  printf '%s\n' "${pending_changes}"
fi
echo "========================================"

if git diff --quiet && git diff --cached --quiet; then
  echo "No changes to commit."
  exit 0
fi

if [[ "${skip_checks}" != "true" ]]; then
  echo "Running RouterShell software QA checker before staging..."
  rs_run_quality_gates
else
  echo "Software QA checker skipped by request."
fi

timestamp="$(date +'%Y-%m-%d %H:%M:%S')"
final_msg="${commit_msg} - ${timestamp}"

echo "Staging changes..."
git add -A

echo "Creating commit..."
git commit -m "${final_msg}"

if [[ "${do_push}" == "true" ]]; then
  remote_name="$(git config branch."${current_branch}".remote || true)"
  push_remote="${remote_name:-origin}"

  echo "Pushing to ${push_remote} (${current_branch})..."
  if [[ -z "${remote_name}" ]]; then
    git push -u "${push_remote}" "${current_branch}"
  else
    git push "${push_remote}" "${current_branch}"
  fi
else
  echo "Push skipped. Use --push to push."
fi

echo "Done."

# FILE: tools/git/git-push.sh
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_NAME="$(basename "$0")"
SCRIPT_VERSION="v1.0.0"

usage() {
  cat <<'EOF'
Auto-commit and push the current RouterShell Git repository.

Usage:
  git-push.sh [--commit-msg "Message"] [--skip-checks]

If --commit-msg is not supplied, a timestamped "Auto-push RouterShell" message is used.
Pushing non-main branches requires two confirmations.
EOF
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/git-common.sh"

commit_msg=""
skip_checks="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --commit-msg)
      shift
      if [[ "${1:-}" == "" ]] || [[ "${1}" =~ ^[[:space:]]*$ ]]; then
        echo "ERROR: --commit-msg requires a non-empty value." >&2
        exit 1
      fi
      commit_msg="$1"
      shift
      ;;
    --skip-checks)
      skip_checks="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -v|--version)
      echo "${SCRIPT_NAME} ${SCRIPT_VERSION}"
      exit 0
      ;;
    *)
      echo "ERROR: Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

rs_require_git_repo
cd "$(rs_repo_root)"

current_branch="$(git rev-parse --abbrev-ref HEAD)"
if [[ "${current_branch}" == "HEAD" ]]; then
  echo "ERROR: Detached HEAD detected. Check out a branch before pushing." >&2
  exit 1
fi

if [[ -z "${commit_msg}" ]]; then
  commit_msg="Auto-push RouterShell: $(date +'%Y-%m-%d %H:%M:%S')"
fi

if [[ "${current_branch}" != "main" && "${current_branch}" != "hot-fix" ]]; then
  echo "WARNING: Current branch is '${current_branch}' (not main/hot-fix)." >&2
  echo "WARNING: This branch may not exist on the remote repository." >&2
  read -r -p "Continue anyway? [y/N]: " confirm_first
  if [[ "${confirm_first,,}" != "y" && "${confirm_first,,}" != "yes" ]]; then
    echo "Aborted."
    exit 1
  fi

  read -r -p "Are you really sure you want to push '${current_branch}'? [y/N]: " confirm_second
  if [[ "${confirm_second,,}" != "y" && "${confirm_second,,}" != "yes" ]]; then
    echo "Aborted."
    exit 1
  fi
fi

if git diff --quiet && git diff --cached --quiet; then
  echo "No changes to commit."
  exit 0
fi

if [[ "${skip_checks}" != "true" ]]; then
  echo "Running RouterShell software QA checker before staging..."
  rs_run_quality_gates
else
  echo "Software QA checker skipped by request."
fi

echo "Staging changes..."
git add -A

echo "Creating commit..."
git commit -m "${commit_msg}"

remote_name="$(git config branch."${current_branch}".remote || true)"
push_remote="${remote_name:-origin}"

echo "Pushing to ${push_remote} (${current_branch})..."
if [[ -z "${remote_name}" ]]; then
  git push -u "${push_remote}" "${current_branch}"
else
  if ! git push "${push_remote}" "${current_branch}"; then
    echo "Initial push failed; retrying with upstream setup..."
    git push -u "${push_remote}" "${current_branch}"
  fi
fi

echo "Done."

# FILE: tools/git/README.md
# RouterShell Git Helpers

These scripts provide RouterShell Git workflow helpers adapted from the PyPNM
tooling style.

## Save Current Work

Run local quality gates, stage all changes, and create a timestamped commit:

```bash
./tools/git/git-save.sh --commit-msg "Add RouterShell packaging"
```

Push after committing:

```bash
./tools/git/git-save.sh --commit-msg "Add RouterShell packaging" --push
```

## Commit And Push

Create a commit and push the current branch:

```bash
./tools/git/git-push.sh --commit-msg "Add RouterShell packaging"
```

Pushing branches other than `main` or `hot-fix` requires confirmation.

## Reset Branch History

Rewrite a branch as a fresh orphan history:

```bash
./tools/git/git-reset-branch-history.sh --branch main --message "Initial RouterShell clean commit"
```

This command force-pushes. By default it creates a remote backup branch first.
Run it only when you intentionally want to rewrite branch history.

## Quality Gates

The save and push helpers run the RouterShell software QA checker before
staging or committing:

```bash
python3 tools/release/qa_checker.py --skip-pycycle
```

The checker runs metadata, version, compile, shell syntax, Ruff, and pytest
checks. Git helpers pass `--skip-pycycle` so commits do not require pycycle to
be installed locally.

The helpers prefer the active virtual environment, then
`/opt/routershell/venv`, then `.venv`, before falling back to system Python.

Use `--skip-checks` only when you are intentionally saving work that is not
ready for validation.

