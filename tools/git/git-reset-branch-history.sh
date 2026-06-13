#!/usr/bin/env bash
set -euo pipefail

SCRIPT_NAME="$(basename "$0")"
SCRIPT_VERSION="v1.0.0"

REMOTE="origin"
BRANCH="main"
COMMIT_MESSAGE="Initial RouterShell clean commit"
ALLOW_DIRTY_WORKTREE="0"
CREATE_BACKUP="1"

usage() {
  cat <<EOF
${SCRIPT_NAME} - Rewrite a RouterShell Git branch as a fresh orphan history.

Usage:
  ${SCRIPT_NAME} [options]

Options:
  --remote NAME          Remote name to push to (default: origin)
  --branch NAME          Branch name to rewrite (default: main)
  --message TEXT         Commit message for the new initial commit
                         (default: "Initial RouterShell clean commit")
  --allow-dirty          Allow running with a dirty working tree.
  --no-backup            Do NOT create a backup branch before rewriting.
  -h, --help             Show this help message.
  -v, --version          Show script version.

WARNING:
  This script force-pushes and rewrites history on the target branch.
  By default it creates and pushes a backup branch first.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --remote)
      REMOTE="${2:-}"
      shift 2
      ;;
    --branch)
      BRANCH="${2:-}"
      shift 2
      ;;
    --message)
      COMMIT_MESSAGE="${2:-}"
      shift 2
      ;;
    --allow-dirty)
      ALLOW_DIRTY_WORKTREE="1"
      shift
      ;;
    --no-backup)
      CREATE_BACKUP="0"
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

if [[ -z "${REMOTE}" || -z "${BRANCH}" || -z "${COMMIT_MESSAGE}" ]]; then
  echo "ERROR: --remote, --branch, and --message values must be non-empty." >&2
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "ERROR: This script must be run inside a Git repository." >&2
  exit 1
fi

repo_root="$(git rev-parse --show-toplevel)"
cd "${repo_root}"

if [[ "${ALLOW_DIRTY_WORKTREE}" != "1" ]]; then
  if [[ -n "$(git status --porcelain)" ]]; then
    echo "ERROR: Working tree is not clean." >&2
    echo "Commit, stash, or discard changes before running this script," >&2
    echo "or re-run with --allow-dirty if you are sure." >&2
    exit 1
  fi
fi

echo "Remote: ${REMOTE}"
echo "Branch: ${BRANCH}"
echo
if [[ "${CREATE_BACKUP}" == "1" ]]; then
  echo "This will:"
  echo "  - Create a BACKUP branch from the current '${BRANCH}' tip on '${REMOTE}'"
  echo "  - Create a NEW orphan history for branch '${BRANCH}'"
  echo "  - Use the CURRENT WORKING TREE as the new initial commit"
  echo "  - FORCE-PUSH the rewritten branch to remote '${REMOTE}'"
else
  echo "This will:"
  echo "  - Create a NEW orphan history for branch '${BRANCH}'"
  echo "  - Use the CURRENT WORKING TREE as the new initial commit"
  echo "  - FORCE-PUSH the rewritten branch to remote '${REMOTE}'"
  echo "  - Skip backup branch creation"
fi
echo
read -r -p "Type YES to continue: " confirm

if [[ "${confirm}" != "YES" ]]; then
  echo "Aborted."
  exit 1
fi

echo "Fetching latest refs from '${REMOTE}'..."
git fetch "${REMOTE}"

echo "Checking out branch '${BRANCH}'..."
git checkout "${BRANCH}"

echo "Pulling latest from '${REMOTE}/${BRANCH}'..."
git pull "${REMOTE}" "${BRANCH}"

backup_branch=""
if [[ "${CREATE_BACKUP}" == "1" ]]; then
  current_commit="$(git rev-parse HEAD)"
  timestamp="$(date +%Y%m%d-%H%M%S)"
  backup_branch="${BRANCH}-backup-${timestamp}"

  echo "Creating backup branch '${backup_branch}' at ${current_commit}..."
  git branch "${backup_branch}" "${current_commit}"

  echo "Pushing backup branch '${backup_branch}' to remote '${REMOTE}'..."
  git push "${REMOTE}" "${backup_branch}"
fi

orphan_branch="__rs_orphan_reset_${BRANCH}"

echo "Creating orphan branch '${orphan_branch}'..."
git checkout --orphan "${orphan_branch}"

echo "Staging all files for new initial commit..."
git add -A

echo "Creating new initial commit..."
git commit -m "${COMMIT_MESSAGE}"

echo "Renaming orphan branch '${orphan_branch}' to '${BRANCH}'..."
git branch -M "${BRANCH}"

echo "Force-pushing rewritten branch '${BRANCH}' to remote '${REMOTE}'..."
git push -f "${REMOTE}" "${BRANCH}"

echo
echo "Done."
echo "Branch '${BRANCH}' on '${REMOTE}' now has a fresh history with a new initial commit."
if [[ "${CREATE_BACKUP}" == "1" ]]; then
  echo "Previous history is preserved on backup branch: ${backup_branch}"
else
  echo "No backup branch was created."
fi
