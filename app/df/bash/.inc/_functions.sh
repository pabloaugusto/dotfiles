#!/usr/bin/env bash

###############################################################################
# app/df/bash/.inc/_functions.sh
#
# Shared Bash helpers used by app/bootstrap/bootstrap-ubuntu-wsl.sh and interactive
# shell routines.
#
# Design principles:
# - Minimal dependencies
# - Quiet output by default
# - Explicit status markers (DONE/ERROR/WARN)
###############################################################################

######################################################
# Print colored status label used by installer routines.
#
# Usage:
#   print_status DONE
#   print_status ERROR
#   print_status WARN
######################################################
print_status() {
	local k_base=$'\033[0m'
	local k_green_inv=$'\033[32;7m'
	local k_red_inv=$'\033[31;7m'
	local k_yellow_inv=$'\033[33;7m'
	local status="$1"

	case "$status" in
		DONE)
			printf ' %s DONE %s\n' "$k_green_inv" "$k_base"
			;;
		ERROR)
			printf ' %s ERROR %s\n' "$k_red_inv" "$k_base"
			;;
		WARN)
			printf ' %s WARN %s\n' "$k_yellow_inv" "$k_base"
			;;
	esac
}

################################################################################
# installPKG
#
# Instala um pacote em gerenciadores suportados, de forma idempotente.
#
# O pacote (2o argumento) e o nome usado pelo gerenciador e frequentemente NAO
# e o nome do binario: "1password-cli@beta", "node@22" e taps como
# "fluxcd/tap/flux" nunca existem como comando, entao testar `command -v "$pkg"`
# sempre dava "nao instalado" e re-instalava/atualizava a cada execucao. O 3o
# argumento permite informar o binario real a testar.
#
# Inputs:
#   $1 -> package manager (brew|apt)
#   $2 -> package name (nome usado pelo gerenciador)
#   $3 -> (opcional) binario a testar como sinal de "ja instalado"
#         default: $2 sem "@versao" e sem prefixo de tap
#
# Output markers: SKIP (ja instalado) | DONE (instalado) | FAIL <pacote>
# Retorno: 0 em SKIP/DONE, != 0 em falha (com as ultimas linhas do erro).
################################################################################
installPKG() {
	local pkg_manager="$1"
	local pkg="$2"
	local bin="${3:-}"

	[[ -z "$pkg_manager" ]] && echo "Not specified: Package manager" && return 1
	[[ -z "$pkg" ]] && echo "Not specified: Package to install" && return 1

	# Default do binario: nome do pacote sem prefixo de tap e sem "@versao"
	# ("fluxcd/tap/flux" -> "flux"; "node@22" -> "node").
	if [[ -z "$bin" ]]; then
		bin="${pkg##*/}"
		bin="${bin%%@*}"
	fi

	if [[ -n "$(command -v "$bin" 2>/dev/null)" ]]; then
		printf "SKIP %s (%s ja instalado)\n" "$pkg" "$bin"
		return 0
	fi

	local err_log
	err_log="$(mktemp)" || return 1

	local -a install_cmd=()
	case "$pkg_manager" in
		brew)
			export NONINTERACTIVE=1
			export HOMEBREW_NO_AUTO_UPDATE=1
			export HOMEBREW_NO_ENV_HINTS=1
			export HOMEBREW_NO_ANALYTICS=1
			export HOMEBREW_NO_INSTALL_CLEANUP=1
			export HOMEBREW_NO_INSTALL_UPGRADE=1
			export HOMEBREW_NO_UPDATE_REPORT_NEW=1
			export HOMEBREW_VERBOSE=0
			export HOMEBREW_VERBOSE_USING_DOTS=0
			install_cmd=(brew install "$pkg" --quiet)
			;;
		apt)
			install_cmd=(sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq "$pkg")
			;;
		*)
			echo "don't found package-manager: '$pkg_manager'"
			rm -f "$err_log"
			return 1
			;;
	esac

	printf "Installing %s with %s " "$pkg" "$pkg_manager"
	if "${install_cmd[@]}" >/dev/null 2>"$err_log"; then
		print_status "DONE"
		rm -f "$err_log"
		return 0
	fi

	printf "FAIL %s\n" "$pkg" >&2
	tail -n 5 "$err_log" >&2
	rm -f "$err_log"
	return 1
}

######################################################
# localEnvFile
#
# Legacy helper: materializa ~/.env.local plaintext via op inject.
# The preferred flow today is encrypted runtime env (~/.env.local.sops).
######################################################
localEnvFile() {
	op inject -i ~/dotfiles/app/df/secrets/.env.local.tpl -o ~/.env.local
}
