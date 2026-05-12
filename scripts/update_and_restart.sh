#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SERVICE_NAME="robot-arm"

cd "${REPO_ROOT}"

echo "Pulling latest changes (fast-forward only)..."
git pull --ff-only

echo "Restarting ${SERVICE_NAME} service..."
if [[ "${EUID}" -eq 0 ]]; then
  systemctl restart "${SERVICE_NAME}"
  systemctl status --no-pager "${SERVICE_NAME}"
else
  sudo systemctl restart "${SERVICE_NAME}"
  sudo systemctl status --no-pager "${SERVICE_NAME}"
fi

echo "Done."
