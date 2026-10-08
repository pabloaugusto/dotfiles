#!/usr/bin/env bash

###############################################################################
# app/df/bash/.inc/signing-automation.sh
#
# Chave de assinatura de automacao por maquina (TARS_ACTOR=agent).
#
# Desenho (SSOT):
# - Humano: user.signingkey global = git.signing_key da config, via 1Password.
# - Maquina/IA: par ed25519 POR MAQUINA, `automation-<hostname>`, gerado pelo
#   bootstrap no 1o uso em ${XDG_CONFIG_HOME:-~/.config}/dotfiles/signing/.
#   Idempotente: existe -> nao regera. Nunca imprime chave privada.
# - Selecao pelo ator, sem tocar no global: com TARS_ACTOR=agent o Git usa a
#   chave de automacao via GIT_CONFIG_COUNT/GIT_CONFIG_KEY_n/VALUE_n, que sao
#   herdados por qualquer `git` rodado no shell (inclusive `task sync`).
###############################################################################

# Diretorio da chave de automacao (mesmo layout no WSL e no Windows).
dotfiles_automation_signing_dir() {
  printf '%s/dotfiles/signing' "${XDG_CONFIG_HOME:-$HOME/.config}"
}

dotfiles_automation_signing_key() {
  printf '%s/automation_ed25519' "$(dotfiles_automation_signing_dir)"
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

# Exporta o override de config que faz o Git assinar com a chave de automacao,
# sem 1Password. Silencioso e no-op quando o modo nao e' automation ou quando a
# chave ainda nao existe.
dotfiles_apply_automation_signing_env() {
  [ "$(dotfiles_resolve_signing_mode "${1:-.}")" = "automation" ] || return 0

  local key_path pub_path allowed_signers
  key_path="$(dotfiles_automation_signing_key)"
  pub_path="${key_path}.pub"
  [ -f "$pub_path" ] || return 0

  allowed_signers="$(dotfiles_automation_signing_dir)/allowed_signers"

  export GIT_CONFIG_COUNT=3
  export GIT_CONFIG_KEY_0="user.signingkey" GIT_CONFIG_VALUE_0="$pub_path"
  export GIT_CONFIG_KEY_1="gpg.ssh.program" GIT_CONFIG_VALUE_1="ssh-keygen"
  export GIT_CONFIG_KEY_2="gpg.ssh.allowedSignersFile" GIT_CONFIG_VALUE_2="$allowed_signers"
}
