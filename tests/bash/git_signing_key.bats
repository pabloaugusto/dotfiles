#!/usr/bin/env bats
#
# bootstrap-ubuntu-wsl.sh: configureGitSigningKey
#
# A chave PUBLICA de assinatura nao e' segredo e nao deve vir de `op read`
# (a service account do bootstrap so enxerga o cofre `secrets`). O SSOT passa a
# ser `git.signing_key` em app/bootstrap/user-config.yaml.
#
# Regressoes cobertas:
# - campo vazio: avisa e NAO derruba o bootstrap; user.signingkey global fica
#   como estava;
# - campo preenchido: grava `git config --global user.signingkey`;
# - idempotencia: rodar 2x nao altera o resultado.

setup() {
  export REPO_ROOT="$PWD"
  export STUB_BIN="$BATS_TEST_TMPDIR/bin"
  export HOME="$BATS_TEST_TMPDIR/home"
  mkdir -p "$STUB_BIN" "$HOME"

  # HOME falso: isola o ~/.gitconfig do dono da maquina.
  export GIT_CONFIG_GLOBAL="$HOME/.gitconfig"
  : >"$GIT_CONFIG_GLOBAL"

  export SCRIPT="$REPO_ROOT/app/bootstrap/bootstrap-ubuntu-wsl.sh"
  export FN_SRC="$BATS_TEST_TMPDIR/fns.sh"

  # Arvore minima com o SSOT da chave publica.
  export FAKE_ROOT="$BATS_TEST_TMPDIR/repo"
  mkdir -p "$FAKE_ROOT/app/bootstrap"
  export DOTFILES_REPO_ROOT="$FAKE_ROOT"
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
  extract_fn configureGitSigningKey > "$FN_SRC"
  cat "$REPO_ROOT/app/df/bash/.inc/yaml-get.sh" >> "$FN_SRC"
  # shellcheck disable=SC1090
  source "$FN_SRC"
}

write_config() {
  {
    printf 'git:\n'
    printf '  signing_key: "%s"\n' "$1"
  } > "$FAKE_ROOT/app/bootstrap/user-config.yaml"
}

@test "configureGitSigningKey grava user.signingkey a partir de git.signing_key" {
  command -v ssh-keygen >/dev/null 2>&1 || skip "ssh-keygen ausente"
  command -v git >/dev/null 2>&1 || skip "git ausente"

  ssh-keygen -q -t ed25519 -N '' -C 'boot-sign@test' -f "$BATS_TEST_TMPDIR/k" >/dev/null
  local pub
  pub="$(cat "$BATS_TEST_TMPDIR/k.pub")"

  write_config "$pub"
  load_signing_fns

  run configureGitSigningKey
  [ "$status" -eq 0 ]
  [ "$(git config --global --get user.signingkey)" = "$(printf '%s' "$pub" | tr -s '[:space:]' ' ' | sed 's/ $//')" ] \
    || [ "$(git config --global --get user.signingkey)" = "$pub" ]
}

@test "configureGitSigningKey e' idempotente (rodar 2x = mesmo estado)" {
  command -v ssh-keygen >/dev/null 2>&1 || skip "ssh-keygen ausente"
  command -v git >/dev/null 2>&1 || skip "git ausente"

  ssh-keygen -q -t ed25519 -N '' -C 'boot-sign@test' -f "$BATS_TEST_TMPDIR/k" >/dev/null
  local pub
  pub="$(cat "$BATS_TEST_TMPDIR/k.pub")"

  write_config "$pub"
  load_signing_fns

  configureGitSigningKey >/dev/null
  local first
  first="$(git config --global --get user.signingkey)"

  configureGitSigningKey >/dev/null
  [ "$(git config --global --get user.signingkey)" = "$first" ]
}

@test "configureGitSigningKey com campo vazio avisa e nao quebra o bootstrap" {
  command -v git >/dev/null 2>&1 || skip "git ausente"

  # Estado anterior do dono da maquina precisa sobreviver ao campo vazio.
  git config --global user.signingkey 'ssh-ed25519 AAAA_PREEXISTENTE user@host'

  write_config ""
  load_signing_fns

  run configureGitSigningKey
  [ "$status" -eq 0 ]
  [[ "$output" == *"git.signing_key vazio"* ]]
  [ "$(git config --global --get user.signingkey)" = 'ssh-ed25519 AAAA_PREEXISTENTE user@host' ]
}

@test "configureGitSigningKey nao usa op read (chave publica nao e' segredo)" {
  local fn_body
  fn_body="$(extract_fn configureGitSigningKey)"
  [[ "$fn_body" != *"op read"* ]]
}
