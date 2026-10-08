#!/bin/bash

################################################################################
# Ubuntu WSL bootstrap
#
# Responsibilities:
# - Install required CLI/tooling (including op/gh/sops/age stack).
# - Link dotfiles for current user.
# - Generate runtime secrets (.env.local.sops) from 1Password references.
# - Ensure GitHub CLI auth over SSH and run final checkEnv validation.
#
# Execution phases:
# 1) Prompt
# 2) Software
# 3) Symlinks
# 4) Secrets/auth
# 5) Final checkEnv
# Modes:
# - full (default)
# - relink: recreate canonical symlinks only
################################################################################

SCRIPT_PATH="${BASH_SOURCE[0]}"
BASE_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd -P)"
BOOTSTRAP_MODE="${1:-full}"
DOTFILES_REPO_ROOT="${DOTFILES_REPO_ROOT_UNIX:-$(cd "$BASE_DIR/../.." && pwd -P)}"

is_sourced() {
	[[ "${BASH_SOURCE[0]}" != "$0" ]]
}

bootstrap_exit() {
	local code="${1:-0}"
	if is_sourced; then
		return "$code"
	fi
	exit "$code"
}

case "$BOOTSTRAP_MODE" in
	full|relink) ;;
	--relink-only) BOOTSTRAP_MODE="relink" ;;
	*)
		echo "Uso: bash app/bootstrap/bootstrap-ubuntu-wsl.sh [full|relink|--relink-only]"
		bootstrap_exit 2
		;;
esac

# Leitor YAML compartilhado com check-env.sh (SSOT em app/df/bash/.inc/yaml-get.sh).
# shellcheck source=../df/bash/.inc/yaml-get.sh
if ! source "$BASE_DIR/../df/bash/.inc/yaml-get.sh"; then
	echo "Falha ao carregar helper: $BASE_DIR/../df/bash/.inc/yaml-get.sh"
	bootstrap_exit 1
fi

resolve_unix_path_with_root() {
	local root="$1"
	local value="$2"

	if [[ -z "$value" ]]; then
		echo ""
		return
	fi
	if [[ "$value" == /* ]]; then
		echo "$value"
		return
	fi

	local normalized_root="${root%/}"
	local normalized_value="${value#/}"
	normalized_value="${normalized_value//\\//}"
	echo "${normalized_root}/${normalized_value}"
}

load_onedrive_overrides_from_user_config() {
	local cfg="$DOTFILES_REPO_ROOT/app/bootstrap/user-config.yaml"
	[ -f "$cfg" ] || return 0

	# Use local YAML values only when env overrides are absent.
	if [[ -z "${DOTFILES_ONEDRIVE_ROOT:-}" ]]; then
		DOTFILES_ONEDRIVE_ROOT="$(_yaml_get "$cfg" "paths.wsl.onedrive_root")"
	fi
	if [[ -z "${DOTFILES_ONEDRIVE_CLIENTS_DIR:-}" ]]; then
		DOTFILES_ONEDRIVE_CLIENTS_DIR="$(_yaml_get "$cfg" "paths.wsl.onedrive_clients_dir")"
	fi
	if [[ -z "${DOTFILES_ONEDRIVE_PROJECTS_DIR:-}" ]]; then
		DOTFILES_ONEDRIVE_PROJECTS_DIR="$(_yaml_get "$cfg" "paths.wsl.onedrive_projects_dir")"
	fi
}

load_onedrive_overrides_from_user_config
ONEDRIVE_ROOT="${DOTFILES_ONEDRIVE_ROOT:-/mnt/d/OneDrive}"
ONEDRIVE_CLIENTS_DIR="$(resolve_unix_path_with_root "$ONEDRIVE_ROOT" "${DOTFILES_ONEDRIVE_CLIENTS_DIR:-clients}")"
ONEDRIVE_PROJECTS_DIR="$(resolve_unix_path_with_root "$ONEDRIVE_ROOT" "${DOTFILES_ONEDRIVE_PROJECTS_DIR:-}")"
if [[ -z "$ONEDRIVE_PROJECTS_DIR" ]]; then
	ONEDRIVE_PROJECTS_DIR="${ONEDRIVE_CLIENTS_DIR%/}/$USER/projects"
fi

# shellcheck source=../df/bash/.inc/_functions.sh
if ! source "$BASE_DIR/../df/bash/.inc/_functions.sh"; then
	echo "Falha ao carregar helper: $BASE_DIR/../df/bash/.inc/_functions.sh"
	bootstrap_exit 1
fi
# shellcheck source=../df/bash/.inc/check-env.sh
if ! source "$BASE_DIR/../df/bash/.inc/check-env.sh"; then
	echo "Falha ao carregar helper: $BASE_DIR/../df/bash/.inc/check-env.sh"
	bootstrap_exit 1
fi

# ----------------------------------------------------------------------------------------
function setup_prompt {
	echo "Starting up dotfiles bootstrap (nix flavored)"
	echo "This script will override some of your home files"
	echo "Iniciar o bootstrap ja e a confirmacao; seguindo sem prompt."
}

# --------------------------------------------------------------------
# Install sofware
# --------------------------------------------------------------------
function install_software {

	# Contadores para o resumo final (instalados/pulados/falhas).
	local installed=0
	local skipped=0
	local failed=0

	# installPKG ja imprime SKIP/DONE/FAIL; aqui apenas contabilizamos para o
	# resumo e nao interrompemos no primeiro erro (queremos ver todas as falhas).
	install_counted() {
		local out rc
		out="$(installPKG "$@" 2>&1)"
		rc=$?
		printf '%s\n' "$out"
		if ((rc != 0)); then
			failed=$((failed + 1))
		elif [[ "$out" == SKIP* ]]; then
			skipped=$((skipped + 1))
		else
			installed=$((installed + 1))
		fi
		return 0
	}

	# Default package installs
	# --------------------------------------------------------------------
	# `apt-get install` sem `apt-get update` antes falha com "Unable to locate
	# package" em imagem recem-criada; atualiza os indices uma vez.
	sudo apt-get update
	sudo DEBIAN_FRONTEND=noninteractive apt-get install -y unzip build-essential procps curl file git fontconfig socat

	# Install or Update homebrew.sh
	if [[ $(command -v brew) == "" ]]; then # can use also: "which brew" instead "command -v brew"
		echo "Installing Hombrew"
		export NONINTERACTIVE=1
		/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
	else
		echo "Updating Homebrew"
		brew update >/dev/null
	fi

	# O caminho /home/linuxbrew e fixo e nao existe quando o Homebrew foi
	# instalado no $HOME (instalacao nao-root). Resolve na ordem:
	# PATH -> $HOME/.linuxbrew -> /home/linuxbrew; nada encontrado = erro alto.
	local brew_bin=""
	brew_bin="$(command -v brew 2>/dev/null || true)"
	if [[ -z "$brew_bin" ]]; then
		local brew_candidate
		for brew_candidate in "$HOME/.linuxbrew/bin/brew" "/home/linuxbrew/.linuxbrew/bin/brew"; do
			if [[ -x "$brew_candidate" ]]; then
				brew_bin="$brew_candidate"
				break
			fi
		done
	fi
	if [[ -z "$brew_bin" ]]; then
		echo "install_software: Homebrew nao encontrado no PATH, em $HOME/.linuxbrew/bin/brew nem em /home/linuxbrew/.linuxbrew/bin/brew." >&2
		return 1
	fi
	eval "$("$brew_bin" shellenv)"

	# software install
	# --------------------------------------------------------------------
	# 3o argumento = binario testado para detectar "ja instalado" quando ele
	# difere do nome do pacote (versao pinada, tap, formula renomeada).
	install_counted brew 1password-cli@beta op
	install_counted brew gh
	install_counted brew oh-my-posh
	install_counted brew zsh
	install_counted brew fastfetch
	install_counted brew ansible
	install_counted brew hashicorp/tap/terraform terraform
	install_counted brew cloudflared
	install_counted brew uv
	install_counted brew go-task/tap/go-task task
	install_counted brew direnv
	install_counted brew age
	install_counted brew sops
	install_counted brew fluxcd/tap/flux flux
	install_counted brew siderolabs/tap/talosctl talosctl
	install_counted brew helm
	install_counted brew helmfile
	install_counted brew kubernetes-cli kubectl
	install_counted brew kustomize
	install_counted brew kubeconform
	install_counted brew moreutils sponge
	install_counted brew talhelper
	install_counted brew stern
	install_counted brew yq
	install_counted brew jq
	install_counted apt postgresql-client psql	#	pgsql - Postgre CLI
	install_counted apt bats	# harness de testes bash (tests/bash/*.bats)
	install_counted apt dos2unix	# tool to fix 'error in libcrypto' ssh key on windows wsl ubuntu
	install_counted brew atuin	# shell hystory command sync database across computers



	# --------------------------------------------------------------------
	# Install oh-my-zsh (idempotente)
	# --------------------------------------------------------------------
	if [ -d "$HOME/.oh-my-zsh" ]; then
		echo "oh-my-zsh já instalado em $HOME/.oh-my-zsh, pulando instalação."
	else
		echo "Installing oh-my-zsh"
		# O instalador oficial retorna erro quando a pasta já existe; como
		# checamos explicitamente acima, aqui qualquer erro passa a ser
		# genuíno (rede, permissão, etc.).
		sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
	fi

	# --------------------------------------------------------------------
	# Resumo: nao mentir sobre o resultado (ver `installPKG`)
	# --------------------------------------------------------------------
	echo "install_software: instalados=$installed pulados=$skipped falhas=$failed"
	if ((failed > 0)); then
		echo "install_software: $failed pacote(s) falharam" >&2
		return 1
	fi
	return 0
}


# --------------------------------------------------------------------
# fonts setup
# --------------------------------------------------------------------
function setup_fonts {
	local font_src="$DOTFILES_REPO_ROOT/app/df/assets/fonts"
	local font_dest="$HOME/.local/share/fonts"

	if [[ ! -d "$font_src" ]]; then
		echo "setup_fonts: origem de fontes nao encontrada: $font_src" >&2
		return 1
	fi

	# So o diretorio PAI pode ser criado: criar o proprio $font_dest como pasta
	# real fazia o `ln` cair dentro dele e gerar ~/.local/share/fonts/fonts.
	mkdir -p "$HOME/.local/share" >/dev/null

	# Repara o artefato do defeito antigo (link aninhado) antes de religar.
	if [[ -L "$font_dest/fonts" ]]; then
		rm -f "$font_dest/fonts"
		if [[ -z "$(ls -A "$font_dest" 2>/dev/null)" ]]; then
			rmdir "$font_dest" 2>/dev/null || true
		fi
	fi

	# _link_safe preserva pasta real em backup em vez de sobrescrever (idempotente
	# quando o destino ja e o link correto).
	_link_safe "$font_src" "$font_dest" || return 1
	fc-cache -f -v >/dev/null
}

# ====================================================================
# General Function: Symlink Setup
# ====================================================================
# Cria/atualiza um link de forma segura: nunca sobrescreve nem apaga
# um arquivo/pasta REAL do usuario sem antes preserva-lo num backup.
#   _link_safe <alvo> <destino>
_link_safe() {
	local alvo="$1"
	local destino="$2"
	local backup

	if [ -L "$destino" ]; then
		if [ "$(readlink -f "$destino")" = "$(readlink -f "$alvo")" ]; then
			return 0
		fi
		ln -sfn "$alvo" "$destino"
		return 0
	fi

	if [ -e "$destino" ]; then
		backup="${destino}.dotfiles-prelink-$(date +%Y%m%d%H%M%S)"
		mv "$destino" "$backup" || return 1
		echo "Aviso: '$destino' era um caminho real; movido para '$backup' antes de criar o link."
	fi

	ln -sfn "$alvo" "$destino"
}

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
	# cleanup de link legado do repo (nao apaga pasta real)
	# ---------------------------------------------------------------
	if [ -L ~/.git ] && [ "$(readlink ~/.git)" = "$DOTFILES_REPO_ROOT/app/df/git" ]; then
		rm -f ~/.git
	fi

	# ---------------------------------------------------------------
	# symlink dotfiles (nunca destroi caminho real: faz backup antes)
	# ---------------------------------------------------------------

	# dotfiles root directories
	_link_safe "$DOTFILES_REPO_ROOT/app/df/ssh" ~/.ssh
	_link_safe "$DOTFILES_REPO_ROOT/app/df/assets" ~/.assets
	_link_safe "$DOTFILES_REPO_ROOT/app/df/config/atuin" ~/.config/atuin
	_link_safe "$DOTFILES_REPO_ROOT/app/df/secrets" ~/.secrets
	_link_safe "$DOTFILES_REPO_ROOT/app/df/git" ~/.config/git

	# vscode
	mkdir -p ~/.config/Code
	_link_safe "$DOTFILES_REPO_ROOT/app/df/vscode" ~/.config/Code/User

	# oh-my-posh
	_link_safe "$DOTFILES_REPO_ROOT/app/df/oh-my-posh" ~/.oh-my-posh

	# dotfile root files
	_link_safe "$DOTFILES_REPO_ROOT/app/df/.editorconfig" ~/.editorconfig
	_link_safe "$DOTFILES_REPO_ROOT/app/df/git/.gitconfig" ~/.gitconfig
	#ln -f ~/dotfiles/app/df/git/.gitconfig.local.sample ~/.gitconfig.local.sample

	# multi platform shell .aliases
	_link_safe "$DOTFILES_REPO_ROOT/app/df/.aliases" ~/.aliases

	# bash
	_link_safe "$DOTFILES_REPO_ROOT/app/df/bash/.bash_logout" ~/.bash_logout
	_link_safe "$DOTFILES_REPO_ROOT/app/df/bash/.bashrc" ~/.bashrc
	_link_safe "$DOTFILES_REPO_ROOT/app/df/bash/.profile" ~/.profile
	_link_safe "$DOTFILES_REPO_ROOT/app/df/bash/.blerc" ~/.blerc

	# zsh
	_link_safe "$DOTFILES_REPO_ROOT/app/df/zsh/.zshrc" ~/.zshrc
	_link_safe "$DOTFILES_REPO_ROOT/app/df/zsh/.zprofile" ~/.zprofile
	_link_safe "$DOTFILES_REPO_ROOT/app/df/zsh/.zshenv" ~/.zshenv

	# If is Windows WSL and onedrive installed
	# set useful profile aliases to common dirs
	if [ -d "$ONEDRIVE_ROOT" ]; then
		mkdir -p "$ONEDRIVE_CLIENTS_DIR" "$ONEDRIVE_PROJECTS_DIR" >/dev/null 2>&1 || true
		_link_safe "$ONEDRIVE_ROOT" ~/onedrive
		# ~/projects real (repos no ext4 do WSL) nunca vira link: _link_safe o moveria
		# para backup e esconderia os repos. So' linka quando nao existe ou ja e' link.
		if [ -d ~/projects ] && [ ! -L ~/projects ]; then
			echo "Aviso: ~/projects e' diretorio real; link para o OneDrive pulado."
		else
			_link_safe "$ONEDRIVE_PROJECTS_DIR" ~/projects
		fi
		_link_safe "$ONEDRIVE_CLIENTS_DIR" ~/clients
	else
		echo "Aviso: OneDrive root nao encontrado em '$ONEDRIVE_ROOT'. Links ~/onedrive ~/clients ~/projects foram pulados."
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
		# A variavel de usuario temporario nao existe aqui: e desatribuido por clean_setup_vars e por
		# setProfileSymlinks, e nunca e definido no call site deste passo. O `cp`
		# apontava para /home//dotfiles e falhava. A fonte e o clone do usuario
		# atual (~/dotfiles), com fallback para o root real do repo.
		local src_dotfiles="/home/${USER}/dotfiles"
		[[ -d "$src_dotfiles" ]] || src_dotfiles="$DOTFILES_REPO_ROOT"
		cp -r "$src_dotfiles" /home/"$ADD_USER"/dotfiles || return 1
		setProfileSymlinks "$ADD_USER"
	fi
}

# --------------------------------------------------------------------
# Age key materialization: o conteudo da chave mora SOMENTE num arquivo 600.
# Nunca em variavel de ambiente persistida, runtime.env ou rc file.
# --------------------------------------------------------------------
# Fonte do recipient publico esperado (arquivo de config do sops, nao segredo).
AGE_KEY_RECIPIENT_SOURCE="${DOTFILES_REPO_ROOT}/app/df/secrets/dotfiles.sops.yaml"

# Caminho do arquivo da chave age (padrao do sops, sobrescrivivel por config).
ageKeyFilePath() {
	if [[ -n "${DOTFILES_AGE_KEY_FILE:-}" ]]; then
		printf '%s' "$DOTFILES_AGE_KEY_FILE"
		return 0
	fi
	printf '%s/sops/age/keys.txt' "${XDG_CONFIG_HOME:-$HOME/.config}"
}

ageKeyFileExpectedRecipient() {
	[ -f "$AGE_KEY_RECIPIENT_SOURCE" ] || return 0
	grep -o 'age1[0-9a-z]*' "$AGE_KEY_RECIPIENT_SOURCE" 2>/dev/null | head -n1 | tr -d '\r\n'
}

# Grava a chave (lida de SOPS_AGE_KEY em memoria) no arquivo 600/700.
# Ref (nunca o conteudo) da chave age: config > default. Nunca vem do template.
_age_key_ref() {
	local cfg="$DOTFILES_REPO_ROOT/app/bootstrap/user-config.yaml" ref=""
	[[ -f "$cfg" ]] && ref="$(_yaml_get "$cfg" "secrets.age_key_ref")"
	printf '%s' "${ref:-op://secrets/dotfiles/age/age.key}"
}

materializeAgeKeyFile() {
	# Override explicito (testes/servidor) por DOTFILES_AGE_KEY_REF; nunca do cache.
	SOPS_AGE_KEY_REF="${DOTFILES_AGE_KEY_REF:-$(_age_key_ref)}"
	local target dir

	target="$(ageKeyFilePath)"
	dir="$(dirname "$target")"

	( umask 077 && mkdir -p "$dir" ) || return 1
	chmod 700 "$dir" 2>/dev/null || true

	# Fonte unica: a ref do 1Password. SOPS_AGE_KEY herdado (runtime.env antigo) e'
	# descartado sem uso: pode ser a chave vazada/rotacionada.
	unset SOPS_AGE_KEY
	if [[ -n "${SOPS_AGE_KEY_REF:-}" ]] && command -v op >/dev/null 2>&1; then
		if [[ "$SOPS_AGE_KEY_REF" != op://* ]]; then
			# Nunca ecoar o valor: se nao e' ref, pode ser o proprio segredo.
			echo "SOPS_AGE_KEY_REF invalida (nao comeca com op://); valor nao exibido. Confira .env.local.tpl."
			return 1
		fi
		( umask 077 && op read "$SOPS_AGE_KEY_REF" > "$target" 2>/dev/null ) || {
			echo "Falha ao ler a chave age de $SOPS_AGE_KEY_REF via 1Password (rode: op read \"$SOPS_AGE_KEY_REF\" >/dev/null para ver o erro)."
			rm -f "$target"
			return 1
		}
	elif [[ ! -f "$target" ]]; then
		echo "Chave age indisponivel: nem SOPS_AGE_KEY, nem SOPS_AGE_KEY_REF, nem $target."
		return 1
	fi

	chmod 600 "$target" 2>/dev/null || true
	export SOPS_AGE_KEY_FILE="$target"
	return 0
}

# Detecta se o filesystem honra chmod (MSYS/DrvFs nao honram).
chmodSupportsPosix() {
	local probe rc
	probe="$(mktemp)" || return 1
	chmod 600 "$probe" 2>/dev/null || true
	[[ "$(stat -c '%a' "$probe" 2>/dev/null || true)" == "600" ]]
	rc=$?
	rm -f "$probe"
	return $rc
}

# Valida existencia, permissao 600 e identidade (recipient) do arquivo.
# Nunca imprime o conteudo da chave.
validateAgeKeyFile() {
	local target recipient expected perm

	target="$(ageKeyFilePath)"
	expected="$(ageKeyFileExpectedRecipient)"

	if [[ ! -f "$target" ]]; then
		echo "Arquivo de chave age ausente: $target"
		return 1
	fi

	# Permissao 600: falha clara apenas se o filesystem honra perms POSIX
	# (chmod e no-op em MSYS/DrvFs, onde o aviso e o melhor possivel).
	perm="$(stat -c '%a' "$target" 2>/dev/null || true)"
	if [[ -n "$perm" && "$perm" != "600" ]]; then
		chmod 600 "$target" 2>/dev/null || true
		perm="$(stat -c '%a' "$target" 2>/dev/null || true)"
	fi
	if [[ -n "$perm" && "$perm" != "600" ]]; then
		if chmodSupportsPosix; then
			echo "Permissao incorreta em $target: $perm (esperado 600)."
			return 1
		fi
		echo "aviso: nao foi possivel aplicar 600 em $target (filesystem sem perms POSIX)."
	fi

	if [[ -z "$expected" ]]; then
		echo "Recipient de referencia nao encontrado em $AGE_KEY_RECIPIENT_SOURCE; identidade nao verificada."
		return 0
	fi

	recipient="$(age-keygen -y "$target" 2>/dev/null | tr -d '\r\n')"
	if [[ -z "$recipient" ]]; then
		echo "Falha ao derivar recipient age de $target."
		return 1
	fi
	if [[ "$recipient" != "$expected" ]]; then
		echo "Recipient de $target diverge do esperado em $AGE_KEY_RECIPIENT_SOURCE."
		return 1
	fi
	return 0
}

# --------------------------------------------------------------------
# Generate encrypted runtime env (.env.local.sops) from 1Password template
# --------------------------------------------------------------------
function setLocalEnvFile {
	local template="$DOTFILES_REPO_ROOT/app/bootstrap/secrets/.env.local.tpl"
	local output="$HOME/.env.local.sops"
	local tmp_plain
	local tmp_age
	local age_recipient

	tmp_plain="$(mktemp)" || return 1
	tmp_age="$(mktemp)" || {
		rm -f "$tmp_plain"
		return 1
	}

	# Falha alta (R4): mostra QUAIS refs falharam, testando cada uma isolada com a
	# saida descartada. Nunca imprime stdout do op (que e' o valor do segredo).
	if ! op inject -i "$template" -o "$tmp_plain" -f >/dev/null 2>&1; then
		echo "Falha ao gerar env temporario com 1Password (op inject). Refs do template:"
		local ref
		for ref in $(grep -o 'op://[^}"]*' "$template" | sort -u); do
			if op read "$ref" >/dev/null 2>&1; then
				echo "  OK     $ref"
			else
				echo "  FALHA  $ref  (item/campo inexistente ou service account sem acesso ao vault)"
			fi
		done
		rm -f "$tmp_plain" "$tmp_age"
		return 1
	fi

	# Load injected values in-memory for current bootstrap process.
	set -a
	# shellcheck disable=SC1090
	source "$tmp_plain"
	set +a
	if [[ -n "${OP_SERVICE_ACCOUNT_TOKEN:-}" ]]; then
		export OP_SERVICE_ACCOUNT_TOKEN="$(printf '%s' "$OP_SERVICE_ACCOUNT_TOKEN" | tr -d '\r')"
	fi

	if ! materializeAgeKeyFile; then
		echo "Chave age indisponivel; nao e possivel criptografar .env.local.sops."
		rm -f "$tmp_plain" "$tmp_age"
		return 1
	fi
	if ! command -v sops >/dev/null 2>&1 || ! command -v age-keygen >/dev/null 2>&1; then
		echo "Dependencias ausentes para criptografia (.sops): sops e/ou age-keygen."
		rm -f "$tmp_plain" "$tmp_age"
		return 1
	fi

	# O recipient e derivado do arquivo 600 ja materializado (nunca de env).
	cp "$(ageKeyFilePath)" "$tmp_age" || {
		rm -f "$tmp_plain" "$tmp_age"
		return 1
	}
	chmod 600 "$tmp_age" 2>/dev/null || true
	age_recipient="$(age-keygen -y "$tmp_age" 2>/dev/null | tr -d '\r\n')"
	if [[ -z "$age_recipient" ]]; then
		echo "Falha ao derivar recipient age a partir do arquivo de chave."
		rm -f "$tmp_plain" "$tmp_age"
		return 1
	fi

	if ! sops --encrypt --age "$age_recipient" "$tmp_plain" > "$output"; then
		echo "Falha ao criptografar $output."
		rm -f "$tmp_plain" "$tmp_age"
		return 1
	fi
	chmod 600 "$output" 2>/dev/null || true

	# Legacy plaintext file is removed, if present.
	rm -f "$HOME/.env.local"
	rm -f "$tmp_plain" "$tmp_age"
}

# --------------------------------------------------------------------
# Decrypt ~/.env.local.sops and load vars in current shell process
# --------------------------------------------------------------------
importLocalEnvFromSops() {
	local encrypted="$HOME/.env.local.sops"
	local tmp_plain

	if [[ ! -f "$encrypted" ]]; then
		echo "Arquivo de env cifrado nao encontrado: $encrypted"
		return 1
	fi
	if ! command -v sops >/dev/null 2>&1; then
		echo "sops nao encontrado; nao foi possivel carregar $encrypted"
		return 1
	fi

	tmp_plain="$(mktemp)" || return 1
	if ! sops -d "$encrypted" > "$tmp_plain"; then
		echo "Falha ao decriptar $encrypted"
		rm -f "$tmp_plain"
		return 1
	fi

	set -a
	# shellcheck disable=SC1090
	source "$tmp_plain"
	set +a
	if [[ -n "${OP_SERVICE_ACCOUNT_TOKEN:-}" ]]; then
		export OP_SERVICE_ACCOUNT_TOKEN="$(printf '%s' "$OP_SERVICE_ACCOUNT_TOKEN" | tr -d '\r')"
	fi
	rm -f "$tmp_plain"

	# Migracao: residuos de token no arquivo cifrado nao devem virar env (o token
	# do 1Password e' lido por ref/arquivo; o `gh` usa a sessao do `gh auth`).
	if [[ -n "${GH_TOKEN:-}" || -n "${GITHUB_TOKEN:-}" ]]; then
		unset GH_TOKEN GITHUB_TOKEN
		echo "Migracao: GH_TOKEN/GITHUB_TOKEN ignorados (nunca vem do env local)."
	fi
}

# --------------------------------------------------------------------
# Persist SOPS age runtime env in local non-versioned file
# --------------------------------------------------------------------
persistSopsAgeEnv() {
	local runtime_dir="$HOME/.config/dotfiles"
	local runtime_file="$runtime_dir/runtime.env"
	local key_file

	if ! materializeAgeKeyFile; then
		return 1
	fi
	if ! validateAgeKeyFile; then
		echo "Validacao do arquivo de chave age falhou; abortando persistencia."
		return 1
	fi
	key_file="$(ageKeyFilePath)"

	mkdir -p "$runtime_dir"
	chmod 700 "$runtime_dir" 2>/dev/null || true

	# Apenas o CAMINHO e persistido. O conteudo da chave vive no arquivo 600.
	cat > "$runtime_file" <<EOF
export SOPS_AGE_KEY_FILE="$key_file"
EOF
	chmod 600 "$runtime_file" 2>/dev/null || true
	export DOTFILES_RUNTIME_ENV_FILE="$runtime_file"

	# Migracao: elimina qualquer residuo do conteudo da chave no ambiente.
	unset SOPS_AGE_KEY

	# Remove legacy plaintext exports from startup files.
	# NUNCA usar sed -i em symlink: GNU sed substitui o link por arquivo regular
	# (quebrando o link para os dotfiles). Arquivo inexistente tambem e pulado.
	for _f in "$HOME/.profile" "$HOME/.bashrc"; do
		[ -L "$_f" ] && continue
		[ -f "$_f" ] || continue
		sed -i '/^export OP_SERVICE_ACCOUNT_TOKEN=/d' "$_f"
		sed -i '/^export OP_CONNECT_HOST=/d' "$_f"
		sed -i '/^export OP_CONNECT_TOKEN=/d' "$_f"
		sed -i '/^export GH_TOKEN=/d' "$_f"
		sed -i '/^export GITHUB_TOKEN=/d' "$_f"
		sed -i '/^export SOPS_AGE_KEY=/d' "$_f"
		sed -i '/^export SOPS_AGE_KEY_FILE=/d' "$_f"
	done
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
	local gh_bin=""
	gh_bin="$(type -P gh 2>/dev/null || true)"
	if [[ -z "$gh_bin" ]] && command -v gh >/dev/null 2>&1; then
		gh_bin="$(command -v gh)"
	fi
	if [[ -z "$gh_bin" ]]; then
		echo "gh CLI nao encontrado."
		return 1
	fi

	# Keep both host-specific and default gh protocol on SSH to avoid context drift.
	_set_gh_protocol_ssh() {
		"$gh_bin" config set git_protocol ssh --host github.com >/dev/null 2>&1 || true
		"$gh_bin" config set git_protocol ssh >/dev/null 2>&1 || true
	}

	# O token do GitHub vive SO no 1Password e nunca e' exportado: `gh` guarda a
	# sessao propria (gh auth). Aqui o valor so passa por stdin do `gh auth login`.
	local github_token=""
	# Prefer least-privilege project token, then the full-access fallback.
	for ref in "op://secrets/dotfiles/github/token" "op://secrets/github/api/token"; do
		github_token="$(op read "$ref" 2>/dev/null || true)"
		if [[ -n "$github_token" ]]; then
			break
		fi
	done

	# Reuse existing authenticated session when available.
	if "$gh_bin" auth status --hostname github.com >/dev/null 2>&1; then
		_set_gh_protocol_ssh
		return 0
	fi

	if [[ -z "$github_token" ]]; then
		echo "Token do GitHub nao encontrado (op://secrets/dotfiles/github/token; fallback op://secrets/github/api/token)."
		return 1
	fi

	if ! printf '%s\n' "$github_token" | "$gh_bin" auth login --hostname github.com --git-protocol ssh --with-token >/dev/null 2>&1; then
		# In some environments (plugins/wrappers), login may fail even with an active session.
		if "$gh_bin" auth status --hostname github.com >/dev/null 2>&1; then
			_set_gh_protocol_ssh
			return 0
		fi
		echo "Falha ao autenticar gh via token do 1Password."
		return 1
	fi

	_set_gh_protocol_ssh
	return 0
}

# --------------------------------------------------------------------
# Ensure a stable cross-platform command name for Git signer program
# (op-ssh-sign -> op-ssh-sign-wsl.exe in WSL)
# --------------------------------------------------------------------
ensureOpSshSignAlias() {
	local op_sign_real=""
	op_sign_real="$(type -P op-ssh-sign 2>/dev/null || true)"
	if [[ -n "$op_sign_real" && -x "$op_sign_real" ]]; then
		case ":$PATH:" in
			*":$HOME/.local/bin:"*) ;;
			*) export PATH="$HOME/.local/bin:$PATH" ;;
		esac
		return 0
	fi
	if ! command -v op-ssh-sign-wsl.exe >/dev/null 2>&1; then
		echo "op-ssh-sign-wsl.exe nao encontrado para criar alias op-ssh-sign."
		return 1
	fi

	mkdir -p "$HOME/.local/bin"
	cat > "$HOME/.local/bin/op-ssh-sign" <<'EOF'
#!/usr/bin/env bash
exec op-ssh-sign-wsl.exe "$@"
EOF
	chmod 700 "$HOME/.local/bin/op-ssh-sign"
	case ":$PATH:" in
		*":$HOME/.local/bin:"*) ;;
		*) export PATH="$HOME/.local/bin:$PATH" ;;
	esac
	return 0
}

# --------------------------------------------------------------------
# Cleanup export vars
# --------------------------------------------------------------------
# SSOT da chave PUBLICA de assinatura: user-config.yaml -> git.signing_key.
# Nunca vem de `op read` (chave publica nao e' segredo). Idempotente: so grava
# user.signingkey global quando o valor atual difere. Campo vazio = aviso, sem
# quebrar o restante do bootstrap.
configureGitSigningKey() {
	local cfg="$DOTFILES_REPO_ROOT/app/bootstrap/user-config.yaml"
	local signing_key=""

	if [[ -f "$cfg" ]]; then
		signing_key="$(_yaml_get "$cfg" "git.signing_key")"
	fi

	if [[ -z "${signing_key//[[:space:]]/}" ]]; then
		echo "AVISO: git.signing_key vazio em app/bootstrap/user-config.yaml; user.signingkey global preservado. Preencha para assinar commits."
		return 0
	fi
	if ! command -v git >/dev/null 2>&1; then
		echo "AVISO: git nao encontrado no PATH; user.signingkey global nao sincronizado."
		return 0
	fi

	local current=""
	current="$(git config --global --get user.signingkey 2>/dev/null || true)"
	if [[ "$current" == "$signing_key" ]]; then
		return 0
	fi

	if git config --global user.signingkey "$signing_key"; then
		echo "user.signingkey global sincronizado a partir de git.signing_key."
	else
		echo "AVISO: falha ao gravar git config --global user.signingkey."
	fi
	return 0
}

# --------------------------------------------------------------------
# Identidade de automacao UNICA (`daneel`) + allowed_signers.
#
# SSOT e' o 1Password: a config local guarda apenas REFS (`automation.*` em
# app/bootstrap/user-config.yaml). Este passo materializa, sempre via
# `op read --out-file` (o valor NUNCA passa pelo stdout):
#   - ${XDG_CONFIG_HOME:-~/.config}/tars/automation/daneel_ed25519 (600)
#   - ${XDG_CONFIG_HOME:-~/.config}/tars/automation/op-sa.token   (600)
#   - ${XDG_CONFIG_HOME:-~/.config}/git/allowed_signers (SSOT da ref)
# e publica gpg.ssh.allowedSignersFile no git config global.
#
# Idempotente: regrava apenas quando o conteudo difere. NUNCA gera chave sozinho:
# se o item nao existir no 1Password, falha com instrucao para o dono criar.
# --------------------------------------------------------------------

# Default refs do robo. Ficam aqui (e nao espalhadas) para o bootstrap funcionar
# em maquinas cujo user-config.yaml ainda nao tem a secao `automation`.
daneel_default_signing_key_ref() {
	printf 'op://secrets/daneel/private key?ssh-format=openssh'
}

daneel_default_op_token_ref() {
	printf 'op://secrets/daneel/1password/service-account'
}

daneel_default_allowed_signers_ref() {
	printf 'op://secrets/dotfiles/git/allowed_signers'
}

_daneel_config_value() {
	local cfg="$DOTFILES_REPO_ROOT/app/bootstrap/user-config.yaml"
	local value=""
	if [[ -f "$cfg" ]]; then
		value="$(_yaml_get "$cfg" "$1")"
	fi
	printf '%s' "$value"
}

# Materializa um item do 1Password em arquivo. $1=ref $2=destino $3=rotulo $4=mode
# Retorna 0 quando o arquivo ja estava atualizado (no-op idempotente).
_daneel_materialize_ref() {
	local ref="$1" dest="$2" label="$3" mode="${4:-600}"
	local dir tmp
	dir="$(dirname "$dest")"

	if ! command -v op >/dev/null 2>&1; then
		echo "FALHA: op (1Password CLI) nao encontrado; $label nao materializado." >&2
		return 1
	fi

	tmp="$(mktemp)" || {
		echo "FALHA: sem diretorio temporario para materializar $label." >&2
		return 1
	}
	chmod 600 "$tmp" 2>/dev/null || true

	if ! op read --out-file "$tmp" "$ref" >/dev/null 2>&1; then
		rm -f "$tmp"
		echo "FALHA: nao foi possivel ler $ref do 1Password ($label)." >&2
		echo "Instrucao: crie/atualize o item e o campo em $ref e garanta que a" >&2
		echo "service account em uso tenha acesso ao vault. O bootstrap nao gera $label." >&2
		return 1
	fi
	if [[ ! -s "$tmp" ]]; then
		rm -f "$tmp"
		echo "FALHA: $ref retornou vazio ($label)." >&2
		return 1
	fi

	# Idempotencia: so regrava quando o conteudo difere.
	if [[ -f "$dest" ]] && cmp -s "$tmp" "$dest"; then
		rm -f "$tmp"
		chmod "$mode" "$dest" 2>/dev/null || true
		return 0
	fi

	mkdir -p "$dir" || {
		rm -f "$tmp"
		echo "FALHA: nao foi possivel criar $dir." >&2
		return 1
	}
	chmod 700 "$dir" 2>/dev/null || true
	mv -f "$tmp" "$dest" || {
		rm -f "$tmp"
		echo "FALHA: nao foi possivel gravar $dest." >&2
		return 1
	}
	chmod "$mode" "$dest" 2>/dev/null || true
	echo "$label atualizado em $dest."
	return 0
}

# Chave privada do daneel precisa terminar em newline para o ssh-keygen aceitar.
_daneel_normalize_key_newline() {
	local key_path="$1"
	[[ -s "$key_path" ]] || return 0
	[[ "$(tail -c1 "$key_path" | od -An -c | tr -d ' ')" = "\n" ]] && return 0
	printf '\n' >>"$key_path"
}

ensureDaneelIdentity() {
	local dir key_path pub_path op_token_path allowed_signers_path
	local signing_key_ref op_token_ref allowed_signers_ref rc=0

	dir="${XDG_CONFIG_HOME:-$HOME/.config}/tars/automation"
	key_path="$dir/daneel_ed25519"
	pub_path="${key_path}.pub"
	op_token_path="$dir/op-sa.token"
	allowed_signers_path="${XDG_CONFIG_HOME:-$HOME/.config}/git/allowed_signers"

	signing_key_ref="$(_daneel_config_value "automation.signing_key_ref")"
	op_token_ref="$(_daneel_config_value "automation.op_token_ref")"
	allowed_signers_ref="$(_daneel_config_value "automation.allowed_signers_ref")"
	: "${signing_key_ref:=$(daneel_default_signing_key_ref)}"
	: "${op_token_ref:=$(daneel_default_op_token_ref)}"
	: "${allowed_signers_ref:=$(daneel_default_allowed_signers_ref)}"

	# Chave privada + publica derivada dela (nunca geramos par novo).
	if ! _daneel_materialize_ref "$signing_key_ref" "$key_path" "Chave de assinatura do daneel" 600; then
		echo "Instrucao: cadastre a chave PUBLICA correspondente no 1Password em" >&2
		echo "op://secrets/daneel/public key e no GitHub como Signing key." >&2
		return 1
	fi
	_daneel_normalize_key_newline "$key_path"

	if ! command -v ssh-keygen >/dev/null 2>&1; then
		echo "FALHA: ssh-keygen nao encontrado; chave PUBLICA do daneel nao derivada." >&2
		return 1
	fi
	if ! ssh-keygen -y -f "$key_path" >"$pub_path" 2>/dev/null || [[ ! -s "$pub_path" ]]; then
		rm -f "$pub_path"
		echo "FALHA: chave privada do daneel invalida em $key_path (nao derivou a publica)." >&2
		return 1
	fi
	chmod 600 "$pub_path" 2>/dev/null || true

	# Token da service account do daneel (para uso headless do op).
	if ! _daneel_materialize_ref "$op_token_ref" "$op_token_path" "Token da service account do daneel" 600; then
		rc=1
	fi

	# allowed_signers: SSOT no 1Password, materializado + registrado no git global.
	if ! _daneel_materialize_ref "$allowed_signers_ref" "$allowed_signers_path" "allowed_signers" 644; then
		rc=1
	elif command -v git >/dev/null 2>&1; then
		git config --global gpg.ssh.allowedSignersFile "$allowed_signers_path" ||
			echo "AVISO: falha ao gravar gpg.ssh.allowedSignersFile no git config global."
	fi

	# Migracao: nenhum allowed_signers gerado localmente deve sobreviver.
	local legacy_dir="${XDG_CONFIG_HOME:-$HOME/.config}/dotfiles/signing"
	if [[ -f "$legacy_dir/allowed_signers" ]] && [[ "$legacy_dir/allowed_signers" != "$allowed_signers_path" ]]; then
		rm -f "$legacy_dir/allowed_signers"
		echo "Migracao: removedor o allowed_signers local legado ($legacy_dir/allowed_signers)."
	fi

	[[ $rc -eq 0 ]] || return 1
	echo "Identidade de automacao (TARS_ACTOR=agent) usa: $key_path"
	return 0
}

function clean_setup_vars {

	unset TEMP_USER
	unset TEMP_USER_PATH
	unset ADD_USER
	unset ADD_USER_PASS
	unset USR_HOME
}

ensureUnixSshConfigLocalLink() {
	ln -sf ~/.ssh/config.unix ~/.ssh/config.local
	chmod 600 ~/.ssh/config ~/.ssh/config.local ~/.ssh/config.unix ~/.ssh/config.windows 2>/dev/null || true
}

# --------------------------------------------------------------------
# Pre-checagem WSL: ferramentas do lado Windows que o bootstrap consome.
# Falha alta e cedo (antes de instalar/alterar qualquer coisa) porque sem elas
# o assinador SSH e o relay do ssh-agent quebram tarde e em silencio.
# --------------------------------------------------------------------
ensureWslWindowsTools() {
	# Nao e WSL: nada a checar.
	if ! grep -qi microsoft /proc/version 2>/dev/null; then
		return 0
	fi

	local missing=()
	local tool
	for tool in op-ssh-sign-wsl.exe npiperelay.exe; do
		if ! command -v "$tool" >/dev/null 2>&1; then
			missing+=("$tool")
		fi
	done

	if (( ${#missing[@]} > 0 )); then
		echo "Pre-checagem WSL: ferramenta(s) do Windows ausente(s) no PATH: ${missing[*]}" >&2
		echo "Instale no Windows e exponha no PATH do WSL (ex.: /mnt/c/.../bin):" >&2
		echo "  op-ssh-sign-wsl.exe -> cliente 1Password para Windows (assinatura SSH do git)" >&2
		echo "  npiperelay.exe      -> https://github.com/albertony/npiperelay (relay do ssh-agent)" >&2
		echo "Sem elas o bootstrap falharia depois, ao configurar op-ssh-sign/ssh-agent." >&2
		return 1
	fi

	return 0
}

# --------------------------------------------------------------------
# BOOTSTRAP steps
# --------------------------------------------------------------------

# 00 - prompt
setup_prompt || bootstrap_exit 1

# 00b - pre-checagem WSL (antes de qualquer install/symlink)
ensureWslWindowsTools || bootstrap_exit 1

if [ "$BOOTSTRAP_MODE" = "relink" ]; then
	setProfileSymlinks "$USER" || bootstrap_exit 1
	ensureUnixSshConfigLocalLink
	clean_setup_vars
	echo "Relink mode concluido."
	bootstrap_exit 0
fi

# 0 setup fonts
setup_fonts || bootstrap_exit 1

# 1 - Install Software
install_software || bootstrap_exit 1

# 2 - optional extra user provisioning
if [ -n "${DOTFILES_ADD_USER:-}" ] && [ -n "${DOTFILES_ADD_USER_PASS_HASH:-}" ]; then
	add_user "$DOTFILES_ADD_USER" "$DOTFILES_ADD_USER_PASS_HASH"
else
	echo "Skipping optional add_user step (DOTFILES_ADD_USER/DOTFILES_ADD_USER_PASS_HASH not set)."
fi

# 3 - Symlink Setup to current user
setProfileSymlinks "$USER" || bootstrap_exit 1

# 4 - config ssh
# SSH Key Setup # ON CLIENT: ssh-copy-id -i ~/.ssh/id_rsa <user>@SERVER
#setSSHFilePermissions "$USER"
#eval "$(ssh-agent -s)"
#ssh-add

# 5 - setup secret local env vars (1password
# This phase guarantees runtime auth/signing dependencies before final checkEnv.
ensureOpToken || bootstrap_exit 1
setLocalEnvFile || bootstrap_exit 1
importLocalEnvFromSops || bootstrap_exit 1
persistSopsAgeEnv || bootstrap_exit 1
ensureOpSshSignAlias || bootstrap_exit 1
ensureGitHubAuth || bootstrap_exit 1
configureGitSigningKey
ensureDaneelIdentity || bootstrap_exit 1


# 6 - unset setup vars
clean_setup_vars


# ----------------------------------------------------
# simlink para a config de ssh baseada no ambiente
# ----------------------------------------------------
ensureUnixSshConfigLocalLink

# O token do dono ficou so em memoria para as fases que precisavam do 1Password.
# Nada de segredo no ambiente ao rodar o checkEnv final (que falha se existir).
unset OP_SERVICE_ACCOUNT_TOKEN OP_CONNECT_HOST OP_CONNECT_TOKEN GH_TOKEN GITHUB_TOKEN

echo "Running final environment health check (checkEnv)..."
checkEnv || {
	echo "checkEnv encontrou falhas de conformidade. Revise os itens acima."
	bootstrap_exit 1
}
