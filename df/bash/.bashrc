# ~/.bashrc: executed by bash(1) for non-login shells.
# see /usr/share/doc/bash/examples/startup-files (in the package bash-doc)
# for examples

# If not running interactively, don't do anything
case $- in
*i*) ;;
*) return ;;
esac

# ble.sh hook top
[[ $- == *i* ]] && source ~/.local/share/blesh/ble.sh --attach=none


# don't put duplicate lines or lines starting with space in the history.
# See bash(1) for more options
HISTCONTROL=ignoreboth

# append to the history file, don't overwrite it
shopt -s histappend

# for setting history length see HISTSIZE and HISTFILESIZE in bash(1)
HISTSIZE=1000
HISTFILESIZE=2000

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

# If set, the pattern "**" used in a pathname expansion context will
# match all files and zero or more directories and subdirectories.
#shopt -s globstar

# make less more friendly for non-text input files, see lesspipe(1)
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

# set variable identifying the chroot you work in (used in the prompt below)
if [ -z "${debian_chroot:-}" ] && [ -r /etc/debian_chroot ]; then
	debian_chroot=$(cat /etc/debian_chroot)
fi

# set a fancy prompt (non-color, unless we know we "want" color)
case "$TERM" in
xterm-color | *-256color) color_prompt=yes ;;
esac

# uncomment for a colored prompt, if the terminal has the capability; turned
# off by default to not distract the user: the focus in a terminal window
# should be on the output of commands, not on the prompt
#force_color_prompt=yes

if [ -n "$force_color_prompt" ]; then
	if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
		# We have color support; assume it's compliant with Ecma-48
		# (ISO/IEC-6429). (Lack of such support is extremely rare, and such
		# a case would tend to support setf rather than setaf.)
		color_prompt=yes
	else
		color_prompt=
	fi
fi

if [ "$color_prompt" = yes ]; then
	PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
else
	PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '
fi
unset color_prompt force_color_prompt

# If this is an xterm set the title to user@host:dir
case "$TERM" in
xterm* | rxvt*)
	PS1="\[\e]0;${debian_chroot:+($debian_chroot)}\u@\h: \w\a\]$PS1"
	;;
*) ;;
esac

# enable color support of ls and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
	test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
	alias ls='ls --color=auto'
	#alias dir='dir --color=auto'
	#alias vdir='vdir --color=auto'

	alias grep='grep --color=auto'
	alias fgrep='fgrep --color=auto'
	alias egrep='egrep --color=auto'
fi

# colored GCC warnings and errors
#export GCC_COLORS='error=01;31:warning=01;35:note=01;36:caret=01;32:locus=01:quote=01'

# some more ls aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

# Normaliza comando de assinatura para referencia unica no Git config.
if ! command -v op-ssh-sign >/dev/null 2>&1 && command -v op-ssh-sign-wsl.exe >/dev/null 2>&1; then
	alias op-ssh-sign='op-ssh-sign-wsl.exe'
fi

# Add an "alert" alias for long running commands.  Use like so:
#   sleep 10; alert
alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'

# Alias definitions.
# You may want to put all your additions into a separate file like
# ~/.bash_aliases, instead of adding them here directly.
# See /usr/share/doc/bash-doc/examples in the bash-doc package.

if [ -f ~/.bash_aliases ]; then
	. ~/.bash_aliases
fi

# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash.bashrc and /etc/profile
# sources /etc/bash.bashrc).
if ! shopt -oq posix; then
	if [ -f /usr/share/bash-completion/bash_completion ]; then
		. /usr/share/bash-completion/bash_completion
	elif [ -f /etc/bash_completion ]; then
		. /etc/bash_completion
	fi
fi

####################################### end defaul /etc/skel .bashrc

#--------------------------------------------------------------
# load this files / commands if they exists
#--------------------------------------------------------------

# custom aliases file multi platform
[ -f ~/.aliases ] && source ~/.aliases
[ -f "$HOME/dotfiles/df/bash/.inc/secrets-manager.sh" ] && source "$HOME/dotfiles/df/bash/.inc/secrets-manager.sh"
[ -f "$HOME/dotfiles/df/bash/.inc/check-env.sh" ] && source "$HOME/dotfiles/df/bash/.inc/check-env.sh"

# set PATH so it includes brew bin if exists
[ -f "/home/linuxbrew/.linuxbrew/bin/brew" ] && eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"

# include ohmyposh if command exists
# # can use also: "which brew" instead "command -v brew"
[ -n "$(command -v oh-my-posh)" ] && eval "$(oh-my-posh --init --shell bash --config ~/.oh-my-posh/pablo.omp.json)"

# include direnv if command exists
# https://direnv.net/docs/hook.html
[ -n "$(command -v direnv)" ] && eval "$(direnv hook bash)"




#--------------------------------------------------------------
# env vars setup
#--------------------------------------------------------------
export   ASSETS="$HOME/dotfiles/df/assets"
export PROJECTS="$HOME/projects"
export HOME_OPS="$HOME/projects/home-ops"
export DOTFILES="$HOME/dotfiles"
export  CLIENTS="$HOME/clients"
export   MYDOCS="$HOME/onedrive/documents"
export ONEDRIVE="$HOME/onedrive"

# include local env vars from encrypted file when available (preferred)
if [ "${DOTFILES_RUNTIME_ENV_LOADED:-0}" != "1" ] || [ -z "${OP_SERVICE_ACCOUNT_TOKEN:-}" ]; then
	DOTFILES_RUNTIME_ENV_FILE="${DOTFILES_RUNTIME_ENV_FILE:-$HOME/.config/dotfiles/runtime.env}"
	[ -f "$DOTFILES_RUNTIME_ENV_FILE" ] && source "$DOTFILES_RUNTIME_ENV_FILE"

	if [ -f ~/.env.local.sops ] && [ -n "$(command -v sops)" ]; then
		_dotfiles_env_tmp="$(mktemp)"
		if sops -d ~/.env.local.sops > "$_dotfiles_env_tmp" 2>/dev/null; then
			set -a
			# shellcheck disable=SC1090
			source "$_dotfiles_env_tmp"
			set +a
		fi
		rm -f "$_dotfiles_env_tmp"
	elif [ -f ~/.env.local ]; then
		# legacy fallback for previous bootstrap versions
		# shellcheck disable=SC1090
		source ~/.env.local
	fi
fi
[ -z "${GH_TOKEN:-}" ] && [ -n "${GITHUB_TOKEN:-}" ] && export GH_TOKEN="$GITHUB_TOKEN"
[ -n "${OP_SERVICE_ACCOUNT_TOKEN:-}" ] && export OP_SERVICE_ACCOUNT_TOKEN="$(printf '%s' "$OP_SERVICE_ACCOUNT_TOKEN" | tr -d '\r')"
[ -n "${GH_TOKEN:-}" ] && export GH_TOKEN="$(printf '%s' "$GH_TOKEN" | tr -d '\r')"
[ -n "${GITHUB_TOKEN:-}" ] && export GITHUB_TOKEN="$(printf '%s' "$GITHUB_TOKEN" | tr -d '\r')"
[ -n "${SOPS_AGE_KEY:-}" ] && export SOPS_AGE_KEY="$(printf '%s' "$SOPS_AGE_KEY" | tr -d '\r')"
[ -n "${SOPS_AGE_KEY_FILE:-}" ] && export SOPS_AGE_KEY_FILE="$(printf '%s' "$SOPS_AGE_KEY_FILE" | tr -d '\r')"

# Prefer 1Password SSH agent socket when available in WSL/Linux.
[ -S /tmp/1password-agent.sock ] && export SSH_AUTH_SOCK=/tmp/1password-agent.sock

# 1password bash plugins integration if file exists
# only supported by unix systems at this date 03/2026
# Disabled for WSL dotfiles since Shell Plugins require 1Password app integration (Biometric Unlock)
# and do not work well with OP_SERVICE_ACCOUNT_TOKEN or headless setups.
# [ -f $HOME/.config/op/plugins.sh ] && source $HOME/.config/op/plugins.sh






#--------------------------------------------------------------
# run at startup this commands if they exists
#--------------------------------------------------------------

# ---------------- fastfetch
	# fastfetch (terminal stats with great ui at terminal startup)
	# set PATH so it includes fastfetch if command exists
#	[ -n "$(command -v fastfetch)" ] && fastfetch

# ---------------- kubectl
	# Include Kubectl bash completion
	# https://livro.descomplicandokubernetes.com.br/pt/day-1/#customizando-o-kubectl
	[ -n "$(command -v kubectl)" ] && eval "$(kubectl completion bash)"
	complete -F __start_kubectl k


# ---------------- pnpm
	export PNPM_HOME="$HOME/.local/share/pnpm"
	case ":$PATH:" in
	  *":$PNPM_HOME:"*) ;;
	  *) export PATH="$PNPM_HOME:$PATH" ;;
	esac

# ---------------- atuin
	# https://docs.atuin.sh/guide/installation/
	#--------------------------------------------------------------
	[ -n "$(command -v atuin)" ] && eval "$(atuin init bash)"

# ---------------- ble.sh
	# ble.sh hook bottom
	[[ ${BLE_VERSION-} ]] && ble-attach


# uv
#export PATH="$HOME/.local/bin:$PATH"
