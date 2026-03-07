#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
# shellcheck disable=SC1091
source "${ROOT_DIR}/scripts/python-runtime.sh"
require_python_cmd "${ROOT_DIR}" "❌ Runtime Python nao encontrado para executar validacoes."
"${PYTHON_CMD[@]}" "$@"
