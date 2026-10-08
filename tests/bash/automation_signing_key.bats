#!/usr/bin/env bats
#
# Chave de assinatura de automacao por maquina (TARS_ACTOR=agent).
#
# Cobre:
# - geracao idempotente do par ed25519 em ${XDG_CONFIG_HOME}/dotfiles/signing;
# - a saida imprime apenas a chave PUBLICA (nunca a privada);
# - TARS_ACTOR=agent faz o Git assinar com a chave de automacao, verificavel;
# - sem TARS_ACTOR o Git continua usando a chave humana da config global.
#
# HOME e GIT_CONFIG_GLOBAL sao temporarios: a config global real nunca e' tocada.

setup() {
  export REPO_ROOT="$PWD"
  export HOME="$BATS_TEST_TMPDIR/home"
  export XDG_CONFIG_HOME="$BATS_TEST_TMPDIR/cfg"
  mkdir -p "$HOME" "$XDG_CONFIG_HOME"

  # Isola a config global real do dono da maquina.
  export GIT_CONFIG_GLOBAL="$BATS_TEST_TMPDIR/gitconfig"
  : >"$GIT_CONFIG_GLOBAL"

  export SIGNING_DIR="$XDG_CONFIG_HOME/dotfiles/signing"
  export AUTO_KEY="$SIGNING_DIR/automation_ed25519"

  export SCRIPT="$REPO_ROOT/app/bootstrap/bootstrap-ubuntu-wsl.sh"
  export FN_SRC="$BATS_TEST_TMPDIR/fns.sh"

  export FAKE_ROOT="$BATS_TEST_TMPDIR/repo"
  mkdir -p "$FAKE_ROOT/app/bootstrap"
  export DOTFILES_REPO_ROOT="$FAKE_ROOT"

  command -v ssh-keygen >/dev/null 2>&1 || skip "ssh-keygen ausente"
  command -v git >/dev/null 2>&1 || skip "git ausente"
}

# Extrai uma funcao do script real, para testa-la isolada.
extract_fn() {
  awk -v n="$1" '
    index($0, n "() {") == 1 || $0 == "function " n " {" { f = 1 }
    f { print }
    f && /^\}$/ { exit }
  ' "$SCRIPT"
}

load_signing_fns() {
  extract_fn ensureAutomationSigningKey >"$FN_SRC"
  cat "$REPO_ROOT/app/df/bash/.inc/yaml-get.sh" >>"$FN_SRC"
  # shellcheck disable=SC1090
  source "$FN_SRC"
}

write_config() {
  {
    printf 'git:\n'
    printf '  signing_key: "%s"\n' "$1"
  } >"$FAKE_ROOT/app/bootstrap/user-config.yaml"
}

@test "ensureAutomationSigningKey gera o par ed25519 e imprime so a publica" {
  load_signing_fns
  write_config 'ssh-ed25519 AAAATESTHUMAN human@host'

  run ensureAutomationSigningKey
  [ "$status" -eq 0 ]
  [ -f "$AUTO_KEY" ]
  [ -f "$AUTO_KEY.pub" ]

  # A chave publica sai; a privada nunca aparece na saida.
  echo "$output" | grep -q 'ssh-ed25519'
  # Sanidade: a privada comeca com o header PEM e nao deve estar na saida.
  local priv_head
  priv_head="$(head -n1 "$AUTO_KEY")"
  [[ "$output" != *"$priv_head"* ]]
}

@test "ensureAutomationSigningKey e' idempotente (2a execucao nao regera)" {
  load_signing_fns
  write_config 'ssh-ed25519 AAAATESTHUMAN human@host'

  ensureAutomationSigningKey >/dev/null
  local before
  before="$(cat "$AUTO_KEY.pub")"

  run ensureAutomationSigningKey
  [ "$status" -eq 0 ]
  [ "$(cat "$AUTO_KEY.pub")" = "$before" ]
  echo "$output" | grep -qi 'ja existe'
}

@test "ensureAutomationSigningKey escreve allowed_signers com humana e automacao" {
  load_signing_fns
  write_config 'ssh-ed25519 AAAATESTHUMAN human@host'

  ensureAutomationSigningKey >/dev/null
  local file="$SIGNING_DIR/allowed_signers"
  [ -f "$file" ]
  grep -q 'AAAATESTHUMAN' "$file"
  grep -q "$(awk '{print $2}' "$AUTO_KEY.pub")" "$file"
}

@test "TARS_ACTOR=agent assina commit com a chave de automacao, verificavel" {
  load_signing_fns
  write_config 'ssh-ed25519 AAAATESTHUMAN human@host'
  ensureAutomationSigningKey >/dev/null

  # shellcheck disable=SC1090
  source "$REPO_ROOT/app/df/bash/.inc/signing-automation.sh"

  local repo="$BATS_TEST_TMPDIR/repo-auto"
  mkdir -p "$repo"
  git -C "$repo" init -q
  git -C "$repo" config user.email agent@host
  git -C "$repo" config user.name agent
  git -C "$repo" config gpg.format ssh
  git -C "$repo" config commit.gpgsign true
  git -C "$repo" config gpg.ssh.allowedSignersFile "$SIGNING_DIR/allowed_signers"

  printf 'one\n' >"$repo/f"
  git -C "$repo" add f

  export TARS_ACTOR=agent
  dotfiles_apply_automation_signing_env "$repo"

  [ "$GIT_CONFIG_COUNT" = "3" ]
  [ "$GIT_CONFIG_KEY_0" = "user.signingkey" ]
  [ "$GIT_CONFIG_VALUE_0" = "$AUTO_KEY.pub" ]
  [ "$GIT_CONFIG_VALUE_1" = "ssh-keygen" ]

  git -C "$repo" commit -q -m c1
  # %G? = G => assinatura boa; %GS = principal do allowed_signers.
  [ "$(git -C "$repo" log -1 --format=%G?)" = "G" ]
  [ -n "$(git -C "$repo" log -1 --format=%GS?)" ]
}

@test "sem TARS_ACTOR o Git usa a chave humana (nao a de automacao)" {
  load_signing_fns
  # Humana: par proprio, configurado no GIT_CONFIG_GLOBAL temporario.
  ssh-keygen -t ed25519 -N '' -C 'human@host' -f "$BATS_TEST_TMPDIR/human_ed25519" -q
  git config --global user.signingkey "$BATS_TEST_TMPDIR/human_ed25519"

  write_config 'ssh-ed25519 AAAATESTHUMAN human@host'
  ensureAutomationSigningKey >/dev/null

  # shellcheck disable=SC1090
  source "$REPO_ROOT/app/df/bash/.inc/signing-automation.sh"

  local repo="$BATS_TEST_TMPDIR/repo-human"
  mkdir -p "$repo"
  git -C "$repo" init -q

  unset TARS_ACTOR
  dotfiles_apply_automation_signing_env "$repo"

  # Sem agente: nenhum override de env e a chave efetiva segue a global humana.
  [ -z "${GIT_CONFIG_COUNT:-}" ]
  # Git normaliza paths (ex.: /tmp -> C:/... no Git Bash), entao comparamos com
  # o valor canonico lido da propria config global humana.
  local human_key
  human_key="$(git config --global --get user.signingkey)"
  [ -n "$human_key" ]
  [ "$(git -C "$repo" config --get user.signingkey)" != "$AUTO_KEY.pub" ]
  [ "$(git -C "$repo" config --get user.signingkey)" = "$human_key" ]
}
