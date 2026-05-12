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

# Spinner helper — runs a command in the background and shows an animated spinner
run_with_spinner() {
  local label="$1"
  shift
  "$@" &>/tmp/robot-arm-install.log &
  local pid=$!
  local spin='|/-\'
  local i=0
  printf "%s  " "${label}"
  while kill -0 "${pid}" 2>/dev/null; do
    printf "\b${spin:i++%${#spin}:1}"
    sleep 0.1
  done
  wait "${pid}"
  local exit_code=$?
  if [[ ${exit_code} -eq 0 ]]; then
    printf "\b done\n"
  else
    printf "\b FAILED\n"
    cat /tmp/robot-arm-install.log
    exit ${exit_code}
  fi
}

run_with_spinner "Creating virtual environment..." "${PYTHON_BIN}" -m venv "${VENV_DIR}"
run_with_spinner "Upgrading pip.................." "${VENV_DIR}/bin/python" -m pip install --upgrade pip

if [[ -s "${REPO_ROOT}/requirements.txt" ]]; then
  run_with_spinner "Installing packages (this may take several minutes on Pi Zero)..." \
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
