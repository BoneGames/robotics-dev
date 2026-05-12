#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SERVICE_NAME="robot-arm"
SERVICE_TEMPLATE="${REPO_ROOT}/systemd/robot-arm.service"
SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}.service"
VENV_DIR="${REPO_ROOT}/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "This installer only supports Linux."
  exit 1
fi

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "Could not find ${PYTHON_BIN}. Install Python 3 first."
  exit 1
fi

if [[ ! -f "${REPO_ROOT}/requirements.txt" ]]; then
  echo "Missing requirements.txt in ${REPO_ROOT}."
  exit 1
fi

if [[ ! -f "${SERVICE_TEMPLATE}" ]]; then
  echo "Missing service template at ${SERVICE_TEMPLATE}."
  exit 1
fi

"${PYTHON_BIN}" -m venv "${VENV_DIR}"
"${VENV_DIR}/bin/python" -m pip install --upgrade pip

if [[ -s "${REPO_ROOT}/requirements.txt" ]]; then
  "${VENV_DIR}/bin/python" -m pip install -r "${REPO_ROOT}/requirements.txt"
fi

if [[ "${EUID}" -eq 0 ]]; then
  sed -e "s|__REPO_ROOT__|${REPO_ROOT}|g" -e "s|__VENV_PYTHON__|${VENV_DIR}/bin/python|g" "${SERVICE_TEMPLATE}" > "${SERVICE_PATH}"
else
  sed -e "s|__REPO_ROOT__|${REPO_ROOT}|g" -e "s|__VENV_PYTHON__|${VENV_DIR}/bin/python|g" "${SERVICE_TEMPLATE}" | sudo tee "${SERVICE_PATH}" >/dev/null
fi

if [[ "${EUID}" -eq 0 ]]; then
  systemctl daemon-reload
  systemctl enable "${SERVICE_NAME}"
  systemctl restart "${SERVICE_NAME}"
else
  sudo systemctl daemon-reload
  sudo systemctl enable "${SERVICE_NAME}"
  sudo systemctl restart "${SERVICE_NAME}"
fi

echo "Installed ${SERVICE_NAME}.service"
