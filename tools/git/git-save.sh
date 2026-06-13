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
