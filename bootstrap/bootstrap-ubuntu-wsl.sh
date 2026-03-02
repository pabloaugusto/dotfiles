#!/bin/bash

################################################################################
# Ubuntu WSL bootstrap
#
# Responsibilities:
# - Install required CLI/tooling (including op/gh/sops/age stack).
# - Link dotfiles for current user.
# - Generate runtime secrets (.env.local) from 1Password references.
# - Ensure GitHub CLI auth over SSH and run final checkEnv validation.
#
# Execution phases:
# 1) Prompt
# 2) Software
# 3) Symlinks
# 4) Secrets/auth
# 5) Final checkEnv
################################################################################

BASE_DIR=$(dirname "$(readlink -m "$0")")
ONEDRIVE_ROOT="${DOTFILES_ONEDRIVE_ROOT:-/mnt/d/OneDrive}"
ONEDRIVE_CLIENTS_DIR="${DOTFILES_ONEDRIVE_CLIENTS_DIR:-$ONEDRIVE_ROOT/clients}"
ONEDRIVE_PROJECTS_DIR="${DOTFILES_ONEDRIVE_PROJECTS_DIR:-$ONEDRIVE_CLIENTS_DIR/$USER/projects}"

# shellcheck source=../df/bash/.inc/_functions.sh
source "$BASE_DIR/../df/bash/.inc/_functions.sh"
# shellcheck source=../df/bash/.inc/check-env.sh
source "$BASE_DIR/../df/bash/.inc/check-env.sh"

# ----------------------------------------------------------------------------------------
function setup_prompt {
	echo "Starting up dotfiles bootstrap (nix flavored)"
	echo "This script will override some of your home files"
	echo "If you are okay with that complete the sentence below, ALL CAPS please..."

	read -r -p "MARCO " answer
	if [ "$answer" != "polo" ]; then
		echo "At least you have chicken 🐔"
		exit 1
	fi
}

# --------------------------------------------------------------------
# Install sofware
# --------------------------------------------------------------------
function install_software {


	# Default package installs
	# --------------------------------------------------------------------
	sudo apt-get install unzip build-essential procps curl file git fontconfig -y

	# Install or Update homebrew.sh
	if [[ $(command -v brew) == "" ]]; then # can use also: "which brew" instead "command -v brew"
		echo "Installing Hombrew"
		export NONINTERACTIVE=1
		/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
		eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
	else
		echo "Updating Homebrew"
		sudo brew update >/dev/null
		eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
	fi

	# software install
	# --------------------------------------------------------------------
	installPKG brew 1password-cli@beta
	installPKG brew gh
	installPKG brew oh-my-posh
	installPKG brew zsh
	installPKG brew fastfetch
	installPKG brew ansible
	installPKG brew terraform
	installPKG brew cloudflared
	installPKG brew uv
	installPKG brew go-task/tap/go-task
	installPKG brew direnv
	installPKG brew age
	installPKG brew sops
	installPKG brew fluxcd/tap/flux
	installPKG brew siderolabs/tap/talosctl
	installPKG brew helm
	installPKG brew helmfile
	installPKG brew kubernetes-cli
	installPKG brew kustomize
	installPKG brew kubeconform
	installPKG brew moreutils
	installPKG brew talhelper
	installPKG brew talosctl
	installPKG brew stern
	installPKG brew yq
	installPKG brew jq
	installPKG brew node@22
	installPKG brew npm  	# package manager
	installPKG brew yarn 	# package manager
	installPKG brew pnpm 	# package manager
	installPKG apt postgresql-client	#	pgsql - Postgre CLI
	installPKG apt dos2unix	# tool to fix 'error in libcrypto' ssh key on windows wsl ubuntu
	installPKG brew atuin	# shell hystory command sync database across computers



	# --------------------------------------------------------------------
	# Install oh-my-zsh
	# --------------------------------------------------------------------
	if [ "$(command -v oh-my-zsh)" == "" ]; then # can use also: "which brew" instead "command -v brew"
		echo "Installing oh-my-zsh"
		sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
	fi

}


# --------------------------------------------------------------------
# fonts setup
# --------------------------------------------------------------------
function setup_fonts {
	mkdir -p ~/.local/share/fonts >/dev/null
	ln -sfn ~/dotfiles/.assets/fonts ~/.local/share/fonts
	fc-cache -f -v >/dev/null
}

# ====================================================================
# General Function: Symlink Setup
# ====================================================================
function setProfileSymlinks {

	# unset previous vars
	unset TEMP_USER
	unset TEMP_USER_PATH
	unset ADD_USER
	unset ADD_USER_PASS
	unset USR_HOME

	# set new vars
	TEMP_USER=$1 # set TEMP_USER env var to be used by other functions
	TEMP_USER_HOME="$(bash -c "cd ~$(printf %q "$TEMP_USER") && pwd")"
	export TEMP_USER
	export TEMP_USER_HOME

	# ---------------------------------------------------------------
	# remove previous root dotfile dirs symlinks
	# ---------------------------------------------------------------
	rm -rf ~/.ssh
	rm -rf ~/.oh-my-posh
	rm -rf ~/.assets
	rm -rf ~/.sops
	rm -rf ~/.config/Code/User
	rm -rf ~/.config/git
	rm -rf ~/.secrets
	if [ -L ~/.git ] && [ "$(readlink ~/.git)" = "$HOME/dotfiles/df/git" ]; then
		rm -f ~/.git
	fi

	# ---------------------------------------------------------------
	# symlink dotfiles
	# ---------------------------------------------------------------

	# dotfiles root directories
	ln -sfn ~/dotfiles/df/ssh ~/.ssh
	ln -sfn ~/dotfiles/df/assets ~/.assets
	ln -sfn ~/dotfiles/df/config/atuin ~/.config/atuin
	ln -sfn ~/dotfiles/df/secrets ~/.secrets
	ln -sfn ~/dotfiles/df/git ~/.config/git

	# vscode
	mkdir -p ~/.config/Code
	ln -sfn ~/dotfiles/df/vscode ~/.config/Code/User

	# oh-my-posh
	ln -sfn ~/dotfiles/df/oh-my-posh ~/.oh-my-posh

	# dotfile root files
	ln -sf ~/dotfiles/df/.editorconfig ~/.editorconfig
	ln -sf ~/dotfiles/df/git/.gitconfig ~/.gitconfig
	#ln -f ~/dotfiles/df/git/.gitconfig.local.sample ~/.gitconfig.local.sample

	# multi platform shell .aliases
	ln -sf ~/dotfiles/df/.aliases ~/.aliases

	# bash
	ln -sf ~/dotfiles/df/bash/.bash_logout ~/.bash_logout
	ln -sf ~/dotfiles/df/bash/.bashrc ~/.bashrc
	ln -sf ~/dotfiles/df/bash/.profile ~/.profile
	ln -sf ~/dotfiles/df/bash/.blerc ~/.blerc

	# zsh
	ln -sf ~/dotfiles/df/zsh/.zshrc ~/.zshrc
	ln -sf ~/dotfiles/df/zsh/.zprofile ~/.zprofile
	ln -sf ~/dotfiles/df/zsh/.zshenv ~/.zshenv

	# If is Windows WSL and onedrive installed
	# set useful profile aliases to common dirs
	if [ -d "$ONEDRIVE_ROOT" ]; then
		ln -sf "$ONEDRIVE_ROOT" ~/onedrive
		ln -sf "$ONEDRIVE_PROJECTS_DIR" ~/projects
		ln -sf "$ONEDRIVE_CLIENTS_DIR" ~/clients
	fi

}



# ====================================================================
# General Function: SSH File Permissions
# ====================================================================
function setSSHFilePermissions {
	TEMP_USER=~$1
	USR_HOME=$(bash -c "realpath $TEMP_USER")
	export TEMP_USER # set TEMP_USER env var to be used by other functions
	export USR_HOME

	chown -R "$1":"$1" "$USR_HOME"
	chmod -R 700 "$USR_HOME"/.ssh
	chmod 600 "$USR_HOME"/.ssh/id_rsa
	chmod 600 "$USR_HOME"/.ssh/id_rsa.pub
	chmod 600 "$USR_HOME"/.ssh/config
	chmod 600 "$USR_HOME"/.ssh/authorized_keys
	chown -R "$1":"$1" "$USR_HOME"/.ssh

	# fix Error loading key "/home/USER/.ssh/id_rsa": error in libcrypto ON UBUNTU WSL
	# https://forum.openmandriva.org/t/error-in-libcrypto/3990/4
	sudo dos2unix "$USR_HOME"/.ssh/id_rsa

}

# --------------------------------------------------------------------
# Optional: create an additional sudo user (disabled by default)
# Security note:
# - No default username/password hash is embedded in the repository.
# - To enable, export:
#   DOTFILES_ADD_USER=<username>
#   DOTFILES_ADD_USER_PASS_HASH='<openssl passwd -1 output>'
# --------------------------------------------------------------------
function add_user {
	export ADD_USER="$1"
	export ADD_USER_PASS="$2"

	if [ -z "$ADD_USER" ] || [ -z "$ADD_USER_PASS" ]; then
		echo "add_user: missing username or password hash."
		return 1
	fi

	if ! getent passwd "$ADD_USER" >/dev/null 2>&1; then
		if ! getent group "$ADD_USER" >/dev/null 2>&1; then
			sudo groupadd "$ADD_USER" >/dev/null 2>&1 || true
		fi
		sudo useradd -m -d /home/"$ADD_USER" -s /bin/bash -p "$ADD_USER_PASS" -g "$ADD_USER" -G sudo "$ADD_USER"
		cp -r /home/"$TEMP_USER"/dotfiles /home/"$ADD_USER"/dotfiles
		setProfileSymlinks "$ADD_USER"
	fi
}

# --------------------------------------------------------------------
# Generate .env.local from secrets/.env.local.tpl (1password)
# --------------------------------------------------------------------
function setLocalEnvFile {
	if ! op inject -i ~/dotfiles/bootstrap/secrets/.env.local.tpl -o ~/.env.local -f >/dev/null 2>&1; then
		echo "Falha ao gerar ~/.env.local com 1Password (op inject)."
		return 1
	fi

	# include local env vars
	# shellcheck disable=SC1090
	source ~/.env.local
}

# --------------------------------------------------------------------
# Check 1password service account env var, and ask if not defined
# --------------------------------------------------------------------
ensureOpToken() {
  if [[ -n "${OP_SERVICE_ACCOUNT_TOKEN:-}" ]]; then
    #echo "OP_SERVICE_ACCOUNT_TOKEN já está definida:"
    #echo "${OP_SERVICE_ACCOUNT_TOKEN}"
		return 0
  else
    read -r -s -p "Digite OP_SERVICE_ACCOUNT_TOKEN: " OP_SERVICE_ACCOUNT_TOKEN
    echo

    if [[ -z "${OP_SERVICE_ACCOUNT_TOKEN}" ]]; then
      echo "OP_SERVICE_ACCOUNT_TOKEN não pode ser vazia."
      return 1
    fi

    export OP_SERVICE_ACCOUNT_TOKEN
    echo "OP_SERVICE_ACCOUNT_TOKEN foi definida."
  fi
}

# --------------------------------------------------------------------
# Ensure GitHub CLI is logged in using a token resolved from 1Password
# --------------------------------------------------------------------
ensureGitHubAuth() {
	if ! command -v gh >/dev/null 2>&1; then
		echo "gh CLI nao encontrado."
		return 1
	fi

	local github_token="${GH_TOKEN:-${GITHUB_TOKEN:-}}"
	if [[ -z "$github_token" ]]; then
		# Prefer least-privilege project token, then fallback to full-access token.
		for ref in "op://secrets/dotfiles/github/token" "op://secrets/github/api/token"; do
			github_token="$(op read "$ref" 2>/dev/null || true)"
			if [[ -n "$github_token" ]]; then
				break
			fi
		done
	fi

	# Reuse existing authenticated session when available.
	if gh auth status --hostname github.com >/dev/null 2>&1; then
		gh auth setup-git --hostname github.com >/dev/null 2>&1 || true
		gh config set git_protocol ssh --host github.com >/dev/null 2>&1 || true
		return 0
	fi

	if [[ -z "$github_token" ]]; then
		echo "Token do GitHub nao encontrado (GITHUB_TOKEN/GH_TOKEN/op://secrets/dotfiles/github/token/op://secrets/github/api/token)."
		return 1
	fi
	export GH_TOKEN="$github_token"

	if ! printf '%s\n' "$github_token" | gh auth login --hostname github.com --git-protocol ssh --with-token >/dev/null 2>&1; then
		echo "Falha ao autenticar gh via token do 1Password."
		return 1
	fi

	gh auth setup-git --hostname github.com >/dev/null 2>&1 || true
	gh config set git_protocol ssh --host github.com >/dev/null 2>&1 || true
	return 0
}

# --------------------------------------------------------------------
# Materialize SOPS AGE key file from injected env (optional hardening)
# --------------------------------------------------------------------
ensureSopsAgeKeyFile() {
	local target="${SOPS_AGE_KEY_FILE:-$HOME/.config/sops/age/keys.txt}"

	if [[ -n "${SOPS_AGE_KEY_FILE:-}" && -f "${SOPS_AGE_KEY_FILE}" ]]; then
		return 0
	fi

	# No key content in env means this hardening step can be skipped.
	if [[ -z "${SOPS_AGE_KEY:-}" ]]; then
		echo "SOPS_AGE_KEY nao definida; pulando materializacao de chave AGE."
		return 0
	fi

	mkdir -p "$(dirname "$target")" || return 1
	umask 077
	printf '%s\n' "$SOPS_AGE_KEY" > "$target" || return 1
	chmod 600 "$target" 2>/dev/null || true
	export SOPS_AGE_KEY_FILE="$target"
	return 0
}

# --------------------------------------------------------------------
# Cleanup export vars
# --------------------------------------------------------------------
function clean_setup_vars {

	unset TEMP_USER
	unset TEMP_USER_PATH
	unset ADD_USER
	unset ADD_USER_PASS
	unset USR_HOME
}

# --------------------------------------------------------------------
# BOOTSTRAP steps
# --------------------------------------------------------------------

# 00 - prompt
setup_prompt

# 0 setup fonts
setup_fonts

# 1 - Install Software
install_software

# 2 - optional extra user provisioning
if [ -n "${DOTFILES_ADD_USER:-}" ] && [ -n "${DOTFILES_ADD_USER_PASS_HASH:-}" ]; then
	add_user "$DOTFILES_ADD_USER" "$DOTFILES_ADD_USER_PASS_HASH"
else
	echo "Skipping optional add_user step (DOTFILES_ADD_USER/DOTFILES_ADD_USER_PASS_HASH not set)."
fi

# 3 - Symlink Setup to current user
setProfileSymlinks "$USER"

# 4 - config ssh
# SSH Key Setup # ON CLIENT: ssh-copy-id -i ~/.ssh/id_rsa <user>@SERVER
#setSSHFilePermissions "$USER"
#eval "$(ssh-agent -s)"
#ssh-add

# 5 - setup secret local env vars (1password
# This phase guarantees runtime auth/signing dependencies before final checkEnv.
ensureOpToken || exit 1
setLocalEnvFile || exit 1
ensureSopsAgeKeyFile || exit 1
ensureGitHubAuth || exit 1


# 6 - unset setup vars
clean_setup_vars


# ----------------------------------------------------
# simlink para a config de ssh baseada no ambiente
# ----------------------------------------------------
ln -sf ~/.ssh/config.unix ~/.ssh/config.local
chmod 600 ~/.ssh/config ~/.ssh/config.local ~/.ssh/config.unix ~/.ssh/config.windows 2>/dev/null || true

echo "Running final environment health check (checkEnv)..."
checkEnv || {
	echo "checkEnv encontrou falhas de conformidade. Revise os itens acima."
	exit 1
}
