#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SERVICE_NAME="robot-arm"
SERVICE_TEMPLATE="${REPO_ROOT}/systemd/robot-arm.service"
SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}.service"
VENV_PYTHON="${REPO_ROOT}/.venv/bin/python"

cd "${REPO_ROOT}"

echo "Pulling latest changes (fast-forward only)..."
git pull --ff-only

echo "Updating ${SERVICE_NAME} service file..."
if [[ "${EUID}" -eq 0 ]]; then
  sed -e "s|__REPO_ROOT__|${REPO_ROOT}|g" -e "s|__VENV_PYTHON__|${VENV_PYTHON}|g" "${SERVICE_TEMPLATE}" > "${SERVICE_PATH}"
  systemctl daemon-reload
else
  sed -e "s|__REPO_ROOT__|${REPO_ROOT}|g" -e "s|__VENV_PYTHON__|${VENV_PYTHON}|g" "${SERVICE_TEMPLATE}" | sudo tee "${SERVICE_PATH}" >/dev/null
  sudo systemctl daemon-reload
fi

echo "Restarting ${SERVICE_NAME} service..."
if [[ "${EUID}" -eq 0 ]]; then
  systemctl restart "${SERVICE_NAME}"
  systemctl status --no-pager "${SERVICE_NAME}"
else
  sudo systemctl restart "${SERVICE_NAME}"
  sudo systemctl status --no-pager "${SERVICE_NAME}"
fi

echo "Done."
