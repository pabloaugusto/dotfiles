#!/usr/bin/env bash

###############################################################################
# df/bash/.inc/_functions.sh
#
# Shared Bash helpers used by bootstrap/bootstrap-ubuntu-wsl.sh and interactive
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
	local k_base="\033[0m\n"
	local k_green_inv="\033[32;7m"
	local k_red_inv="\033[31;7m"
	local k_yellow_inv="\033[33;7m"
	local status="$1"

	case "$status" in
		DONE)
			# shellcheck disable=SC2059
			printf " %s DONE %s " "$k_green_inv" "$k_base"
			;;
		ERROR)
			# shellcheck disable=SC2059
			printf " %s ERROR %s " "$k_red_inv" "$k_base"
			;;
		WARN)
			# shellcheck disable=SC2059
			printf " %s WARN %s " "$k_yellow_inv" "$k_base"
			;;
	esac
}

################################################################################
# installPKG
#
# Instala ou atualiza um pacote em gerenciadores suportados.
# Inputs:
#   $1 -> package manager (brew|apt)
#   $2 -> package name
################################################################################
installPKG() {
	local pkg_manager="$1"
	local pkg="$2"

	[[ -z "$pkg_manager" ]] && echo "Not specified: Package manager" && exit 1
	[[ -z "$pkg" ]] && echo "Not specified: Package to install" && exit 1

	case "$pkg_manager" in
		brew)
			if [[ -z "$(command -v "$pkg")" ]]; then
				printf "Instaling %s with %s" "$pkg" "$pkg_manager "
				export NONINTERACTIVE=1
				export HOMEBREW_NO_AUTO_UPDATE=1
				export HOMEBREW_NO_ENV_HINTS=1
				export HOMEBREW_NO_ANALYTICS=1
				export HOMEBREW_NO_INSTALL_CLEANUP=1
				export HOMEBREW_NO_INSTALL_UPGRADE=1
				export HOMEBREW_NO_UPDATE_REPORT_NEW=1
				export HOMEBREW_VERBOSE=0
				export HOMEBREW_VERBOSE_USING_DOTS=1
				brew install "$pkg" --quiet >/dev/null 2>&1
				print_status "DONE"
			else
				printf "Upgrading %s with %s" "$pkg" "$pkg_manager "
				export NONINTERACTIVE=1
				export HOMEBREW_NO_AUTO_UPDATE=1
				export HOMEBREW_NO_ENV_HINTS=1
				export HOMEBREW_NO_ANALYTICS=1
				export HOMEBREW_NO_INSTALL_CLEANUP=1
				export HOMEBREW_NO_INSTALL_UPGRADE=1
				export HOMEBREW_NO_UPDATE_REPORT_NEW=1
				export HOMEBREW_VERBOSE=0
				export HOMEBREW_VERBOSE_USING_DOTS=0
				brew upgrade "$pkg" --quiet >/dev/null 2>&1
				print_status "DONE"
			fi
			;;
		apt)
			if [[ -z "$(command -v "$pkg")" ]]; then
				printf "Instaling %s with %s" "$pkg" "$pkg_manager "
				export NONINTERACTIVE=1
				apt install "$pkg" -y -qqq >/dev/null 2>&1
				print_status "DONE"
			else
				printf "Upgrading %s with %s" "$pkg" "$pkg_manager "
				export NONINTERACTIVE=1
				apt upgrade "$pkg" -y -qqq >/dev/null 2>&1
				print_status "DONE"
			fi
			;;
		*)
			echo "don't found package-manager: '$pkg_manager'"
			;;
	esac
}

######################################################
# localEnvFile
#
# Legacy helper: materializa ~/.env.local plaintext via op inject.
# The preferred flow today is encrypted runtime env (~/.env.local.sops).
######################################################
localEnvFile() {
	op inject -i ~/dotfiles/df/secrets/.env.local.tpl -o ~/.env.local
}
