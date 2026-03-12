#!/usr/bin/env bash

# Generic secrets class/dispatcher.
#
# Operators:
#   - 1pass
#   - age
#   - sops
#
# Methods:
#   - help
#   - read
#   - inject
#   - keygen
#   - ageKey
#   - crypt
#   - decrypt

SECRET_AGE_KEY_FILE_CLASS=""

_secret_require_cmd() {
  local cmd="$1"
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "secret: comando nao encontrado: $cmd" >&2
    return 1
  }
}

_secret_require_op_login() {
  _secret_require_cmd op || return 1
  op whoami >/dev/null 2>&1 || {
    echo "secret: login no 1Password necessario (op signin)." >&2
    return 1
  }
}

_secret_prepare_target() {
  local target="$1"
  mkdir -p "$(dirname "$target")" || return 1
  umask 077
}

_secret_expect_1pass_operator() {
  local operator="$1"
  [[ "$operator" == "1pass" || "$operator" == "op" ]] || {
    echo "secret: operador invalido '$operator' (esperado: 1pass)." >&2
    return 1
  }
}

_secret_expect_age_operator() {
  local operator="$1"
  [[ "$operator" == "age" ]] || {
    echo "secret: operador invalido '$operator' (esperado: age)." >&2
    return 1
  }
}

_secret_expect_sops_operator() {
  local operator="$1"
  [[ "$operator" == "sops" || "$operator" == "age+sops" ]] || {
    echo "secret: operador invalido '$operator' (esperado: sops)." >&2
    return 1
  }
}

_secret_parse_common_args() {
  # Parse generic args used by crypt/decrypt.
  # Inputs:
  #   $@ -> [tokens...]
  # Outputs (globals):
  #   _secret_positional (array)
  #   _secret_parsed_age_key
  #   _secret_parsed_out
  #   _secret_parsed_config
  _secret_positional=()
  _secret_parsed_age_key=""
  _secret_parsed_out=""
  _secret_parsed_config=""

  while [ "$#" -gt 0 ]; do
    case "$1" in
      --age-key)
        shift
        [ -n "$1" ] || {
          echo "secret: faltou valor para --age-key" >&2
          return 2
        }
        _secret_parsed_age_key="$1"
        ;;
      --age-key=*)
        _secret_parsed_age_key="${1#*=}"
        ;;
      --out)
        shift
        [ -n "$1" ] || {
          echo "secret: faltou valor para --out" >&2
          return 2
        }
        _secret_parsed_out="$1"
        ;;
      --out=*)
        _secret_parsed_out="${1#*=}"
        ;;
      --config)
        shift
        [ -n "$1" ] || {
          echo "secret: faltou valor para --config" >&2
          return 2
        }
        _secret_parsed_config="$1"
        ;;
      --config=*)
        _secret_parsed_config="${1#*=}"
        ;;
      *)
        _secret_positional+=("$1")
        ;;
    esac
    shift
  done

  return 0
}

_secret_resolve_age_key() {
  # Order:
  # 1) method parameter
  # 2) secret ageKey value
  # 3) env var SOPS_AGE_KEY_FILE
  local method_age_key="$1"
  local resolved=""
  _secret_resolved_age_key=""

  if [ -n "$method_age_key" ]; then
    resolved="$method_age_key"
  elif [ -n "$SECRET_AGE_KEY_FILE_CLASS" ]; then
    resolved="$SECRET_AGE_KEY_FILE_CLASS"
  elif [ -n "$SOPS_AGE_KEY_FILE" ]; then
    resolved="$SOPS_AGE_KEY_FILE"
  else
    echo "secret: ageKey obrigatoria para sops (parametro, 'secret ageKey', ou SOPS_AGE_KEY_FILE)." >&2
    return 1
  fi

  [ -f "$resolved" ] || {
    echo "secret: ageKey nao encontrada: $resolved" >&2
    return 1
  }

  _secret_resolved_age_key="$resolved"
  return 0
}

secret.help() {
  cat <<'EOF'
Classe: secret()
Operadores:
  - 1pass
  - age
  - sops

Uso:
  secret help

  secret read 1pass op://secrets/dotfiles/age/age.key
  secret inject 1pass app/df/secrets/dotfiles.age.local.key.tpl app/df/secrets/dotfiles.age.local.key

  secret keygen age app/df/secrets/dotfiles.age.local.key
  secret keygen age app/df/secrets/dotfiles.age.local.key --force

  secret ageKey app/df/secrets/dotfiles.age.local.key

  secret crypt sops app/df/secrets/local.env
  secret crypt sops app/df/secrets/local.env app/df/secrets/local.env.sops app/df/secrets/dotfiles.sops.yaml
  secret crypt sops app/df/secrets/local.env --age-key app/df/secrets/dotfiles.age.local.key

  secret decrypt sops app/df/secrets/local.env.sops
  secret decrypt sops app/df/secrets/local.env.sops app/df/secrets/local.env app/df/secrets/dotfiles.sops.yaml
  secret decrypt sops app/df/secrets/local.env.sops --age-key app/df/secrets/dotfiles.age.local.key

Resolucao de ageKey (crypt/decrypt):
  1) --age-key / parametro positional
  2) secret ageKey <arquivo>
  3) variavel de ambiente SOPS_AGE_KEY_FILE
EOF
}

secret.read() {
  local operator="$1"
  local ref="$2"

  [ -n "$operator" ] && [ -n "$ref" ] || {
    echo "Uso: secret read 1pass <secret_ref>" >&2
    return 2
  }

  _secret_expect_1pass_operator "$operator" || return 1
  _secret_require_op_login || return 1
  op read "$ref"
}

secret.inject() {
  local operator="$1"
  local template="$2"
  local target="$3"
  local mode="${4:-0600}"
  local tmp

  [ -n "$operator" ] && [ -n "$template" ] && [ -n "$target" ] || {
    echo "Uso: secret inject 1pass <template_file> <target_file> [file_mode]" >&2
    return 2
  }
  [ -f "$template" ] || {
    echo "secret: template nao encontrado: $template" >&2
    return 1
  }

  _secret_expect_1pass_operator "$operator" || return 1
  _secret_require_op_login || return 1
  _secret_prepare_target "$target" || return 1

  tmp="$(mktemp "${target}.tmp.XXXXXX")" || return 1
  if ! op inject -i "$template" -o "$tmp" --file-mode "$mode"; then
    rm -f "$tmp"
    return 1
  fi

  chmod "$mode" "$tmp" 2>/dev/null || true
  mv -f "$tmp" "$target"
}

secret.keygen() {
  local operator="$1"
  local target="$2"
  local force="$3"

  [ -n "$operator" ] && [ -n "$target" ] || {
    echo "Uso: secret keygen age <target_key_file> [--force]" >&2
    return 2
  }

  _secret_expect_age_operator "$operator" || return 1
  _secret_require_cmd age-keygen || return 1
  _secret_prepare_target "$target" || return 1

  if [ -f "$target" ] && [ "$force" != "--force" ]; then
    echo "secret: arquivo ja existe: $target (use --force para sobrescrever)." >&2
    return 1
  fi

  age-keygen -o "$target" >/dev/null || return 1
  chmod 600 "$target" 2>/dev/null || true
  echo "secret: chave AGE gerada em $target"
  echo "secret: chave publica -> $(age-keygen -y "$target")"
}

secret.ageKey() {
  local key_file="$1"
  [ -n "$key_file" ] || {
    echo "Uso: secret ageKey <key_file>" >&2
    return 2
  }
  [ -f "$key_file" ] || {
    echo "secret: ageKey nao encontrada: $key_file" >&2
    return 1
  }

  SECRET_AGE_KEY_FILE_CLASS="$key_file"
  echo "secret: ageKey da classe definida: $SECRET_AGE_KEY_FILE_CLASS"
}

secret.crypt() {
  local operator="$1"
  local input_file="$2"
  local output_file=""
  local config_file=""
  local age_key_file=""
  local resolved_age_key=""
  local tmp

  [ -n "$operator" ] && [ -n "$input_file" ] || {
    echo "Uso: secret crypt sops <input_file> [output_file] [config_file] [age_key_file]" >&2
    return 2
  }
  [ -f "$input_file" ] || {
    echo "secret: arquivo de entrada nao encontrado: $input_file" >&2
    return 1
  }

  shift 2
  _secret_parse_common_args "$@" || return 1
  _secret_expect_sops_operator "$operator" || return 1
  _secret_require_cmd sops || return 1

  if [ "${#_secret_positional[@]}" -gt 3 ]; then
    echo "secret: argumentos posicionais demais para crypt." >&2
    return 2
  fi
  [ -n "${_secret_positional[0]:-}" ] && output_file="${_secret_positional[0]}"
  [ -n "${_secret_positional[1]:-}" ] && config_file="${_secret_positional[1]}"
  [ -n "${_secret_positional[2]:-}" ] && age_key_file="${_secret_positional[2]}"

  [ -n "$_secret_parsed_out" ] && output_file="$_secret_parsed_out"
  [ -n "$_secret_parsed_config" ] && config_file="$_secret_parsed_config"
  [ -n "$_secret_parsed_age_key" ] && age_key_file="$_secret_parsed_age_key"

  _secret_resolve_age_key "$age_key_file" || return 1
  resolved_age_key="$_secret_resolved_age_key"
  export SOPS_AGE_KEY_FILE="$resolved_age_key"

  if [ -n "$output_file" ]; then
    _secret_prepare_target "$output_file" || return 1
    tmp="$(mktemp "${output_file}.tmp.XXXXXX")" || return 1
    if [ -n "$config_file" ]; then
      sops --config "$config_file" -e "$input_file" >"$tmp" || {
        rm -f "$tmp"
        return 1
      }
    else
      sops -e "$input_file" >"$tmp" || {
        rm -f "$tmp"
        return 1
      }
    fi
    chmod 600 "$tmp" 2>/dev/null || true
    mv -f "$tmp" "$output_file"
    echo "secret: arquivo criptografado em $output_file"
  else
    if [ -n "$config_file" ]; then
      sops --config "$config_file" -e -i "$input_file" || return 1
    else
      sops -e -i "$input_file" || return 1
    fi
    echo "secret: arquivo criptografado in-place: $input_file"
  fi
}

secret.decrypt() {
  local operator="$1"
  local input_file="$2"
  local output_file=""
  local config_file=""
  local age_key_file=""
  local resolved_age_key=""
  local tmp

  [ -n "$operator" ] && [ -n "$input_file" ] || {
    echo "Uso: secret decrypt sops <input_file> [output_file] [config_file] [age_key_file]" >&2
    return 2
  }
  [ -f "$input_file" ] || {
    echo "secret: arquivo de entrada nao encontrado: $input_file" >&2
    return 1
  }

  shift 2
  _secret_parse_common_args "$@" || return 1
  _secret_expect_sops_operator "$operator" || return 1
  _secret_require_cmd sops || return 1

  if [ "${#_secret_positional[@]}" -gt 3 ]; then
    echo "secret: argumentos posicionais demais para decrypt." >&2
    return 2
  fi
  [ -n "${_secret_positional[0]:-}" ] && output_file="${_secret_positional[0]}"
  [ -n "${_secret_positional[1]:-}" ] && config_file="${_secret_positional[1]}"
  [ -n "${_secret_positional[2]:-}" ] && age_key_file="${_secret_positional[2]}"

  [ -n "$_secret_parsed_out" ] && output_file="$_secret_parsed_out"
  [ -n "$_secret_parsed_config" ] && config_file="$_secret_parsed_config"
  [ -n "$_secret_parsed_age_key" ] && age_key_file="$_secret_parsed_age_key"

  _secret_resolve_age_key "$age_key_file" || return 1
  resolved_age_key="$_secret_resolved_age_key"
  export SOPS_AGE_KEY_FILE="$resolved_age_key"

  if [ -n "$output_file" ]; then
    _secret_prepare_target "$output_file" || return 1
    tmp="$(mktemp "${output_file}.tmp.XXXXXX")" || return 1
    if [ -n "$config_file" ]; then
      sops --config "$config_file" -d "$input_file" >"$tmp" || {
        rm -f "$tmp"
        return 1
      }
    else
      sops -d "$input_file" >"$tmp" || {
        rm -f "$tmp"
        return 1
      }
    fi
    chmod 600 "$tmp" 2>/dev/null || true
    mv -f "$tmp" "$output_file"
    echo "secret: arquivo descriptografado em $output_file"
  else
    if [ -n "$config_file" ]; then
      sops --config "$config_file" -d "$input_file"
    else
      sops -d "$input_file"
    fi
  fi
}

secret() {
  local method="${1:-help}"
  shift || true

  case "$method" in
    help|-h|--help)
      secret.help "$@"
      ;;
    read)
      secret.read "$@"
      ;;
    inject)
      secret.inject "$@"
      ;;
    keygen)
      secret.keygen "$@"
      ;;
    ageKey)
      secret.ageKey "$@"
      ;;
    crypt)
      secret.crypt "$@"
      ;;
    decrypt)
      secret.decrypt "$@"
      ;;
    *)
      echo "secret: metodo invalido: $method" >&2
      secret.help >&2
      return 2
      ;;
  esac
}
