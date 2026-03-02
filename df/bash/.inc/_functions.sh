#!/bin/bash

######################################################
# Print colored status
######################################################
function print_status {

	K_BASE="\033[0m\n"
	K_GREEN_INV="\033[32;7m"
	K_RED_INV="\033[31;7m"
	K_YELLOW_INV="\033[33;7m"

	STATUS=$1

	case $STATUS in
	# ---------------------------------
	# info note DONE
	# ---------------------------------
	DONE)
		# shellcheck disable=SC2059
		printf " $K_GREEN_INV DONE $K_BASE "

		;;
	# ---------------------------------
	# info note ERROR
	# ---------------------------------
	ERROR)
		# shellcheck disable=SC2059
		printf " $K_RED_INV ERROR $K_BASE "
		;;
	# ---------------------------------
	# info note WARN
	# ---------------------------------
	WARN)
		# shellcheck disable=SC2059
		printf " $K_YELLOW_INV WARN $K_BASE "
		;;
	esac

}
######################################################################################
# Remove a Item (file or folder) if exists (forced, recursive, without confirm)
######################################################################################
function installPKG {

	PKG_MANAGER="$1"
	PKG="$2"

	[[ -z $1 ]] && echo "Not specified: Package manager" && exit 1
	[[ -z $2 ]] && echo "Not specified: Package to install" && exit 1

	# switch package managers
	case $PKG_MANAGER in

	# --------------------------------------------------------------------------------
	# Install packages with: brew
	# --------------------------------------------------------------------------------
	brew)
		if [[ -z $(command -v "$PKG") ]]; then # can use also: "which brew" instead "command -v brew"
			printf "Instaling %s with %s" "$PKG" "$PKG_MANAGER "
			export NONINTERACTIVE=1 # install non-interactive way
			export HOMEBREW_NO_AUTO_UPDATE=1
			export HOMEBREW_NO_ENV_HINTS=1
			export HOMEBREW_NO_ANALYTICS=1
			export HOMEBREW_NO_INSTALL_CLEANUP=1
			export HOMEBREW_NO_INSTALL_UPGRADE=1
			export HOMEBREW_NO_UPDATE_REPORT_NEW=1
			export HOMEBREW_VERBOSE=0
			export HOMEBREW_VERBOSE_USING_DOTS=1
			brew install "$PKG" --quiet >/dev/null 2>&1
			print_status "DONE"

		else
			printf "Upgrading %s with %s" "$PKG" "$PKG_MANAGER "
			export NONINTERACTIVE=1 # install non-interactive way
			export HOMEBREW_NO_AUTO_UPDATE=1
			export HOMEBREW_NO_ENV_HINTS=1
			export HOMEBREW_NO_ANALYTICS=1
			export HOMEBREW_NO_INSTALL_CLEANUP=1
			export HOMEBREW_NO_INSTALL_UPGRADE=1
			export HOMEBREW_NO_UPDATE_REPORT_NEW=1
			export HOMEBREW_VERBOSE=0
			export HOMEBREW_VERBOSE_USING_DOTS=0
			brew upgrade "$PKG" --quiet >/dev/null 2>&1
			print_status DONE
		fi
		;;

	# --------------------------------------------------------------------------------
	# Install packages with: apt
	# --------------------------------------------------------------------------------
	apt)
		if [[ -z $(command -v "$PKG") ]]; then # can use also: "which brew" instead "command -v brew"
			printf "Instaling %s with %s" "$PKG" "$PKG_MANAGER "
			export NONINTERACTIVE=1 # install non-interactive way
			apt install "$PKG" -y -qqq >/dev/null 2>&1
			print_status "DONE"

		else
			printf "Upgrading %s with %s" "$PKG" "$PKG_MANAGER "
			export NONINTERACTIVE=1 # install non-interactive way
			apt upgrade "$PKG" -y -qqq >/dev/null 2>&1
			print_status DONE
		fi
		;;


	# --------------------------------------------------------------------------------
	# Dont have the pakage manager or misstyped
	# --------------------------------------------------------------------------------
	*)
		echo "don't found package-manager: '$1'"
		;;
	esac

}


######################################################
# Create / update local env file (with 1password cli)
######################################################
function localEnvFile {
	op inject -i ~/dotfiles/df/secrets/.env.local.tpl -o ~/.env.local
}
