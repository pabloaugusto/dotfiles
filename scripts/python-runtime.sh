#!/usr/bin/env bash
set -euo pipefail

ensure_python_cache_prefix() {
  local project_root="${1:-$PWD}"
  local default_prefix="${project_root}/.cache/pycache"

  if [[ -z "${PYTHONPYCACHEPREFIX:-}" ]]; then
    export PYTHONPYCACHEPREFIX="${default_prefix}"
  fi

  mkdir -p "${PYTHONPYCACHEPREFIX}"

  if [[ -z "${PYTHONUTF8:-}" ]]; then
    export PYTHONUTF8="1"
  fi

  if [[ -z "${PYTHONIOENCODING:-}" ]]; then
    export PYTHONIOENCODING="utf-8"
  fi
}

resolve_python_cmd() {
  local project_root="${1:-$PWD}"
  PYTHON_CMD=()
  ensure_python_cache_prefix "${project_root}"

  is_usable_python() {
    local candidate="${1:-}"
    [[ -n "${candidate}" && -x "${candidate}" ]] || return 1
    "${candidate}" -c 'import sys' >/dev/null 2>&1
  }

  local -A seen=()
  try_candidates() {
    local candidate
    for candidate in "$@"; do
      [[ -n "${candidate}" ]] || continue
      if [[ -n "${seen[${candidate}]:-}" ]]; then
        continue
      fi
      seen["${candidate}"]=1
      if is_usable_python "${candidate}"; then
        PYTHON_CMD=("${candidate}")
        return 0
      fi
    done
    return 1
  }

  local -a local_candidates=(
    "${project_root}/.venv/bin/python"
    "${project_root}/.venv/bin/python3"
    "${project_root}/.venv/Scripts/python"
    "${project_root}/.venv/Scripts/python.exe"
    "${VIRTUAL_ENV:-}/bin/python"
    "${VIRTUAL_ENV:-}/bin/python3"
    "${VIRTUAL_ENV:-}/Scripts/python"
    "${VIRTUAL_ENV:-}/Scripts/python.exe"
    "${PYTHON_BIN:-}"
  )
  if try_candidates "${local_candidates[@]}"; then
    return 0
  fi

  if command -v py >/dev/null 2>&1 && py -3 -c 'import sys' >/dev/null 2>&1; then
    PYTHON_CMD=(py -3)
    return 0
  fi

  if command -v python3 >/dev/null 2>&1 && python3 -c 'import sys' >/dev/null 2>&1; then
    PYTHON_CMD=(python3)
    return 0
  fi

  if command -v python >/dev/null 2>&1 && python -c 'import sys' >/dev/null 2>&1; then
    PYTHON_CMD=(python)
    return 0
  fi

  if command -v python.exe >/dev/null 2>&1 && python.exe -c 'import sys' >/dev/null 2>&1; then
    PYTHON_CMD=(python.exe)
    return 0
  fi

  return 1
}

require_python_cmd() {
  local project_root="${1:-$PWD}"
  local fail_msg="${2:-❌ Runtime Python nao encontrado (.venv, VIRTUAL_ENV, python3, python, py ou python.exe).}"
  if ! resolve_python_cmd "${project_root}"; then
    echo "${fail_msg}"
    return 1
  fi
}
