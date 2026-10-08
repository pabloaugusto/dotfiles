#!/usr/bin/env bats
#
# bootstrap-ubuntu-wsl.sh: configureGitSigningKey
#
# A chave PUBLICA de assinatura nao e' segredo e nao deve vir de `op read`
# (a service account do bootstrap so enxerga o cofre `secrets`). O SSOT passa a
# ser `git.signing_key` em app/bootstrap/user-config.yaml.
#
# Regressoes cobertas:
# - campo vazio: avisa e NAO derruba o bootstrap; user.signingkey efetivo fica
#   como estava;
# - campo preenchido: grava user.signingkey no `.gitconfig.local` (o arquivo
#   incluido pelo ~/.gitconfig), NUNCA no ~/.gitconfig versionado;
# - idempotencia: rodar 2x nao altera o resultado nem o ~/.gitconfig.

setup() {
  export REPO_ROOT="$PWD"
  export STUB_BIN="$BATS_TEST_TMPDIR/bin"
  export HOME="$BATS_TEST_TMPDIR/home"
  unset XDG_CONFIG_HOME
  mkdir -p "$STUB_BIN" "$HOME/.config/git"

  # HOME falso com a MESMA estrutura da maquina: um ~/.gitconfig (versionado,
  # symlink para app/df/git/.gitconfig) que inclui o `.gitconfig.local`, onde
  # vive o dado local (identidade/assinatura).
  export GIT_CONFIG_GLOBAL="$HOME/.gitconfig"
  cat >"$GIT_CONFIG_GLOBAL" <<'EOF'
[include]
    path = ~/.config/git/.gitconfig.local
EOF
  export GIT_LOCAL_CONFIG="$HOME/.config/git/.gitconfig.local"
  : >"$GIT_LOCAL_CONFIG"

  export SCRIPT="$REPO_ROOT/app/bootstrap/bootstrap-ubuntu-wsl.sh"
  export FN_SRC="$BATS_TEST_TMPDIR/fns.sh"

  # Arvore minima com o SSOT da chave publica.
  export FAKE_ROOT="$BATS_TEST_TMPDIR/repo"
  mkdir -p "$FAKE_ROOT/app/bootstrap"
  export DOTFILES_REPO_ROOT="$FAKE_ROOT"

  # Harness: o runner costuma rodar sobre uma COPIA do worktree, cujo .git e' um
  # arquivo apontando para um caminho que nao existe no Linux (ex.: C:/...). O
  # Git aborta com "not a git repository" em qualquer `git config`, mesmo com
  # --global. Nenhum teste depende do repo do cwd (tudo usa paths absolutos),
  # entao roda do tmpdir isolado, fora de qualquer descoberta de repo.
  mkdir -p "$BATS_TEST_TMPDIR/cwd"
  cd "$BATS_TEST_TMPDIR/cwd" || return 1
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
  extract_fn gitLocalConfigPath > "$FN_SRC"
  extract_fn configureGitSigningKey >> "$FN_SRC"
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

hash_file() {
  sha256sum "$1" | awk '{print $1}'
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
  # Valor EFETIVO (merge do ~/.gitconfig com o .local incluido).
  [ "$(git config --get user.signingkey)" = "$pub" ]
  # E o dono do valor e' o .local, nao o versionado.
  [ -s "$GIT_LOCAL_CONFIG" ]
  ! grep -q 'signingkey' "$GIT_CONFIG_GLOBAL"
}

@test "configureGitSigningKey nao altera o ~/.gitconfig versionado (2x)" {
  command -v ssh-keygen >/dev/null 2>&1 || skip "ssh-keygen ausente"
  command -v git >/dev/null 2>&1 || skip "git ausente"

  ssh-keygen -q -t ed25519 -N '' -C 'boot-sign@test' -f "$BATS_TEST_TMPDIR/k" >/dev/null
  local pub before after
  pub="$(cat "$BATS_TEST_TMPDIR/k.pub")"

  write_config "$pub"
  load_signing_fns

  before="$(hash_file "$GIT_CONFIG_GLOBAL")"
  configureGitSigningKey >/dev/null
  configureGitSigningKey >/dev/null
  after="$(hash_file "$GIT_CONFIG_GLOBAL")"

  [ "$before" = "$after" ]
  [ "$(git config --get user.signingkey)" = "$pub" ]
  ! grep -qF "$pub" "$GIT_CONFIG_GLOBAL"
}

@test "configureGitSigningKey e' idempotente (rodar 2x = mesmo estado)" {
  command -v ssh-keygen >/dev/null 2>&1 || skip "ssh-keygen ausente"
  command -v git >/dev/null 2>&1 || skip "git ausente"

  ssh-keygen -q -t ed25519 -N '' -C 'boot-sign@test' -f "$BATS_TEST_TMPDIR/k" >/dev/null
  local pub first
  pub="$(cat "$BATS_TEST_TMPDIR/k.pub")"

  write_config "$pub"
  load_signing_fns

  configureGitSigningKey >/dev/null
  first="$(hash_file "$GIT_LOCAL_CONFIG")"

  configureGitSigningKey >/dev/null
  [ "$(hash_file "$GIT_LOCAL_CONFIG")" = "$first" ]
  [ "$(git config --get user.signingkey)" = "$pub" ]
}

@test "configureGitSigningKey com campo vazio avisa e nao quebra o bootstrap" {
  command -v git >/dev/null 2>&1 || skip "git ausente"

  # Estado anterior do dono da maquina precisa sobreviver ao campo vazio.
  printf '[user]\n\tsigningkey = ssh-ed25519 AAAA_PREEXISTENTE user@host\n' > "$GIT_LOCAL_CONFIG"
  local before
  before="$(hash_file "$GIT_CONFIG_GLOBAL")"

  write_config ""
  load_signing_fns

  run configureGitSigningKey
  [ "$status" -eq 0 ]
  [[ "$output" == *"git.signing_key vazio"* ]]
  [ "$(git config --get user.signingkey)" = 'ssh-ed25519 AAAA_PREEXISTENTE user@host' ]
  [ "$(hash_file "$GIT_CONFIG_GLOBAL")" = "$before" ]
}

@test "configureGitSigningKey nao usa op read nem git config --global de escrita" {
  local fn_body
  fn_body="$(extract_fn configureGitSigningKey)"
  [[ "$fn_body" != *"op read"* ]]
  [[ "$fn_body" != *"config --global"* ]]
  [[ "$fn_body" == *'config --file'* ]]
}
