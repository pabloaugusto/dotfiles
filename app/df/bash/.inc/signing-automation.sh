#!/usr/bin/env bash

###############################################################################
# app/df/bash/.inc/signing-automation.sh
#
# Identidade de automacao UNICA: `daneel` (uma chave para TODAS as maquinas).
#
# Desenho (SSOT):
# - Humano: user.signingkey global = git.signing_key da config, via 1Password.
# - Robo (`daneel`): par ed25519 unico, privada so no 1Password; o bootstrap
#   materializa em ${XDG_CONFIG_HOME:-~/.config}/tars/automation/daneel_ed25519
#   (dir 700, arquivo 600) com `op read --out-file`. Nao existe mais chave por
#   hostname nem geracao local: sem o item no 1Password o bootstrap falha claro.
# - Selecao pelo ator, sem tocar no global: com TARS_ACTOR=agent o Git usa a
#   identidade do daneel via GIT_CONFIG_COUNT/GIT_CONFIG_KEY_n/VALUE_n, que sao
#   herdados por qualquer `git` rodado no shell (inclusive `task sync`).
# - allowed_signers: SSOT no 1Password, materializado pelo bootstrap em
#   ${XDG_STATE_HOME:-~/.local/state}/dotfiles/git/allowed_signers (humano +
#   daneel). Fica FORA de ~/.config/git de proposito: esse diretorio e' o
#   app/df/git do proprio repo (symlink do bootstrap), entao materializar ali
#   sujaria a working tree versionada a cada bootstrap.
###############################################################################

# Diretorio da identidade de automacao (mesmo layout no WSL e no Windows).
dotfiles_automation_dir() {
  printf '%s/tars/automation' "${XDG_CONFIG_HOME:-$HOME/.config}"
}

dotfiles_automation_signing_key() {
  printf '%s/daneel_ed25519' "$(dotfiles_automation_dir)"
}

# Caminho materializado do allowed_signers (SSOT: ref no 1Password).
# Diretorio de estado, NUNCA dentro de ~/.config/git (que e' o repo).
dotfiles_automation_allowed_signers() {
  printf '%s/dotfiles/git/allowed_signers' "${XDG_STATE_HOME:-$HOME/.local/state}"
}

# Identidade do robo: le automation.<campo> do user-config.yaml (SSOT) e cai no
# fallback quando o YAML/leitor nao estao disponiveis (ex.: shell sem o repo).
_dotfiles_automation_git_identity() {
  local key="$1" fallback="$2"
  local cfg="${DOTFILES_REPO_ROOT:-$HOME/dotfiles}/app/bootstrap/user-config.yaml"
  local value=""
  if [ -f "$cfg" ] && command -v _yaml_get >/dev/null 2>&1; then
    value="$(_yaml_get "$cfg" "$key")"
  fi
  printf '%s' "${value:-$fallback}"
}

# Ponto unico de resolucao do modo de assinatura.
# Ordem: TARS_ACTOR=agent > DOTFILES_GIT_SIGN_MODE > worktree > human.
dotfiles_resolve_signing_mode() {
  if [ "${TARS_ACTOR:-}" = "agent" ]; then
    printf 'automation'
    return 0
  fi
  case "${DOTFILES_GIT_SIGN_MODE:-auto}" in
    human|automation)
      printf '%s' "$DOTFILES_GIT_SIGN_MODE"
      return 0
      ;;
  esac
  local probe="${1:-.}" worktree_mode=""
  worktree_mode="$(git -C "$probe" config --worktree --get dotfiles.signing.mode 2>/dev/null || true)"
  if [ "$worktree_mode" = "automation" ]; then
    printf 'automation'
  else
    printf 'human'
  fi
}

# Exporta o override de config que faz o Git usar a identidade `daneel` (chave +
# nome/email) sem 1Password. Silencioso e no-op quando o modo nao e' automation ou
# quando a chave ainda nao foi materializada pelo bootstrap.
dotfiles_apply_automation_signing_env() {
  [ "$(dotfiles_resolve_signing_mode "${1:-.}")" = "automation" ] || return 0

  local key_path pub_path allowed_signers
  key_path="$(dotfiles_automation_signing_key)"
  pub_path="${key_path}.pub"
  [ -f "$pub_path" ] || return 0

  allowed_signers="$(dotfiles_automation_allowed_signers)"

  # Identidade git do robo. SSOT: automation.git_name/git_email em
  # app/bootstrap/user-config.yaml; TARS_AUTOMATION_GIT_* e os defaults sao
  # apenas fallback (editar o YAML muda o autor dos commits do agente).
  local git_name git_email
  git_name="$(_dotfiles_automation_git_identity "automation.git_name" "${TARS_AUTOMATION_GIT_NAME:-Daneel}")"
  git_email="$(_dotfiles_automation_git_identity "automation.git_email" "${TARS_AUTOMATION_GIT_EMAIL:-daneel-bot@pabloaugusto.com}")"

  local -a pairs=(
    "user.signingkey=$pub_path"
    "gpg.ssh.program=ssh-keygen"
    "gpg.ssh.allowedSignersFile=$allowed_signers"
    "user.name=$git_name"
    "user.email=$git_email"
    "commit.gpgsign=true"
  )

  local i=0 pair
  export GIT_CONFIG_COUNT="${#pairs[@]}"
  for pair in "${pairs[@]}"; do
    export "GIT_CONFIG_KEY_$i=${pair%%=*}"
    export "GIT_CONFIG_VALUE_$i=${pair#*=}"
    i=$((i + 1))
  done
}
