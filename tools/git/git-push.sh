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
  echo "Running RouterShell quality gates..."
  rs_run_quality_gates
else
  echo "Quality gates skipped by request."
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
