#!/bin/bash

###############################################################################
# archive/bootstrap/bootstrap-ubuntu.original.sh
#
# Legacy Ubuntu bootstrap preserved for historical reference.
# Current canonical Linux/WSL flow lives in:
#   bootstrap/bootstrap-ubuntu-wsl.sh
#
# Keep this file only for comparison/recovery scenarios.
###############################################################################

BASE_DIR=$(dirname "$(readlink -m "$0")")
ONEDRIVE_ROOT="${DOTFILES_ONEDRIVE_ROOT:-/mnt/d/OneDrive}"
ONEDRIVE_CLIENTS_DIR="${DOTFILES_ONEDRIVE_CLIENTS_DIR:-$ONEDRIVE_ROOT/clients}"
ONEDRIVE_PROJECTS_DIR="${DOTFILES_ONEDRIVE_PROJECTS_DIR:-$ONEDRIVE_CLIENTS_DIR/$USER/projects}"

# shellcheck source=../../df/bash/.inc/_functions.sh
source "$BASE_DIR/../../df/bash/.inc/_functions.sh"

# ----------------------------------------------------------------------------------------

echo "Starting up dotfiles bootstrap (nix flavored)"
echo "This script will override some of your home files"
echo "If you are okay with that complete the sentence below, ALL CAPS please..."

read -r -p "MARCO " answer
if [ "$answer" != "polo" ]; then
	echo "At least you have chicken 🐔"
	exit 1
fi

unset TEMP_USER
unset TEMP_USER_PATH
unset ADD_USER
unset ADD_USER_PASS
unset USR_HOME

# --------------------------------------------------------------------
# Default package installs
# --------------------------------------------------------------------
# apt
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

# Install oh-my-posh
installPKG brew oh-my-posh
installPKG brew zsh
installPKG brew fastfetch
installPKG brew ansible
installPKG brew terraform
installPKG brew cloudflared
installPKG brew uv
installPKG brew go-task
installPKG brew direnv
installPKG brew age
installPKG brew sops
installPKG brew 'fluxcd/tap/flux'
installPKG brew helm
installPKG brew kubernetes-cli
installPKG brew kustomize
installPKG brew kubeconform
installPKG brew yq
installPKG brew jq
installPKG brew node@22
installPKG brew npm  	# package manager
installPKG brew yarn 	# package manager
installPKG brew pnpm 	# package manager
installPKG apt postgresql-client	#	pgsql - Postgre CLI

# Install oh-my-zsh
if [ "$(command -v oh-my-zsh)" == "" ]; then # can use also: "which brew" instead "command -v brew"
	echo "Installing oh-my-zsh"
	sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
fi

# --------------------------------------------------------------------
# fonts setup
# --------------------------------------------------------------------
mkdir -p ~/.local/share/fonts >/dev/null
ln -sfn ~/dotfiles/.assets/fonts ~/.local/share/fonts
fc-cache -f -v >/dev/null

# ====================================================================
# General Function: Symlink Setup
# ====================================================================
function setProfileSymlinks {

	TEMP_USER=$1 # set TEMP_USER env var to be used by other functions
	TEMP_USER_HOME="$(bash -c "cd ~$(printf %q "$TEMP_USER") && pwd")"
	export TEMP_USER
	export TEMP_USER_HOME

	# ---------------------------------------------------------------
	# remove previous root dotfile dirs symlinks
	# ---------------------------------------------------------------
	rm -rf "$TEMP_USER_HOME"/.ssh
	rm -rf "$TEMP_USER_HOME"/.oh-my-posh
	rm -rf "$TEMP_USER_HOME"/.assets
	rm -rf "$TEMP_USER_HOME"/.sops
	rm -rf "$TEMP_USER_HOME"/.config/Code/User

	# ---------------------------------------------------------------
	# symlink dotfiles
	# ---------------------------------------------------------------

	# dotfiles root directories
	ln -sfn "$TEMP_USER_HOME"/dotfiles/df/ssh "$TEMP_USER_HOME"/.ssh
	ln -sfn "$TEMP_USER_HOME"/dotfiles/df/assets "$TEMP_USER_HOME"/.assets

	# vscode
	mkdir -p "$TEMP_USER_HOME"/.config/Code
	ln -sfn "$TEMP_USER_HOME"/dotfiles/df/vscode "$TEMP_USER_HOME"/.config/Code/User

	# oh-my-posh
	ln -sfn "$TEMP_USER_HOME"/dotfiles/df/oh-my-posh "$TEMP_USER_HOME"/.oh-my-posh

	# dotfile root files
	ln -f "$TEMP_USER_HOME"/dotfiles/df/.editorconfig "$TEMP_USER_HOME"/.editorconfig
	ln -f "$TEMP_USER_HOME"/dotfiles/df/git/.gitconfig "$TEMP_USER_HOME"/.gitconfig
	ln -f "$TEMP_USER_HOME"/dotfiles/df/git/.gitconfig-linux "$TEMP_USER_HOME"/.gitconfig-linux
	#ln -f "$TEMP_USER_HOME"/dotfiles/df/git/.gitconfig.local.sample "$TEMP_USER_HOME"/.gitconfig.local.sample

	# multi platform shell .aliases
	ln -f "$TEMP_USER_HOME"/dotfiles/df/.aliases "$TEMP_USER_HOME"/.aliases

	# bash
	ln -f "$TEMP_USER_HOME"/dotfiles/df/bash/.bash_logout "$TEMP_USER_HOME"/.bash_logout
	ln -f "$TEMP_USER_HOME"/dotfiles/df/bash/.bashrc "$TEMP_USER_HOME"/.bashrc
	ln -f "$TEMP_USER_HOME"/dotfiles/df/bash/.profile "$TEMP_USER_HOME"/.profile

	# zsh
	ln -f "$TEMP_USER_HOME"/dotfiles/df/zsh/.zshrc "$TEMP_USER_HOME"/.zshrc
	ln -f "$TEMP_USER_HOME"/dotfiles/df/zsh/.zprofile "$TEMP_USER_HOME"/.zprofile
	ln -f "$TEMP_USER_HOME"/dotfiles/df/zsh/.zshenv "$TEMP_USER_HOME"/.zshenv

	# If is Windows WSL and onedrive installed
	# set useful profile aliases to common dirs
	if [ -d "$ONEDRIVE_ROOT" ]; then
		ln -sf "$ONEDRIVE_ROOT" "$TEMP_USER_HOME"/onedrive
		ln -sf "$ONEDRIVE_PROJECTS_DIR" "$TEMP_USER_HOME"/projects
		ln -sf "$ONEDRIVE_CLIENTS_DIR" "$TEMP_USER_HOME"/clients
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
	chmod 600 "$USR_HOME"/.ssh/authorized_keys
	chown -R "$1":"$1" "$USR_HOME"/.ssh
}

# --------------------------------------------------------------------
# Symlink Setup to current user
# --------------------------------------------------------------------
setProfileSymlinks "$USER"

# --------------------------------------------------------------------
# Optional: create an additional sudo user (disabled by default)
# Security note:
# - No default username/password hash is embedded in the repository.
# - To enable, export:
#   DOTFILES_ADD_USER=<username>
#   DOTFILES_ADD_USER_PASS_HASH='<openssl passwd -1 output>'
# --------------------------------------------------------------------
if [ -n "${DOTFILES_ADD_USER:-}" ] && [ -n "${DOTFILES_ADD_USER_PASS_HASH:-}" ]; then
	ADD_USER="$DOTFILES_ADD_USER"
	ADD_USER_PASS="$DOTFILES_ADD_USER_PASS_HASH"
	if ! getent passwd "$ADD_USER" >/dev/null 2>&1; then
		if ! getent group "$ADD_USER" >/dev/null 2>&1; then
			sudo groupadd "$ADD_USER" >/dev/null 2>&1 || true
		fi
		sudo useradd -m -d /home/"$ADD_USER" -s /bin/bash -p "$ADD_USER_PASS" -g "$ADD_USER" -G sudo "$ADD_USER"
		cp -r /home/"$TEMP_USER"/dotfiles /home/"$ADD_USER"/dotfiles
		setProfileSymlinks "$ADD_USER"
		setSSHFilePermissions "$ADD_USER"
		chsh --shell /bin/bash "$ADD_USER" # set default shell
	fi
else
	echo "Skipping optional add_user step (DOTFILES_ADD_USER/DOTFILES_ADD_USER_PASS_HASH not set)."
fi

# --------------------------------------------------------------------
# SSH Key Setup # ON CLIENT: ssh-copy-id -i ~/.ssh/id_rsa <user>@SERVER
# --------------------------------------------------------------------
setSSHFilePermissions "$USER"
eval "$(ssh-agent -s)"
ssh-add

# --------------------------------------------------------------------
# Cleanup export vars
# --------------------------------------------------------------------
unset TEMP_USER
unset TEMP_USER_PATH
unset ADD_USER
unset ADD_USER_PASS
unset USR_HOME
