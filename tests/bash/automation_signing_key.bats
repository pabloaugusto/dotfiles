#!/usr/bin/env bats
#
# Identidade de automacao UNICA `daneel` (TARS_ACTOR=agent).
#
# Cobre:
# - materializacao da chave/op-sa.token/allowed_signers a partir do 1Password
#   (op em stub, sempre `op read --out-file`; o valor nunca passa pelo stdout);
# - idempotencia (2a execucao nao regrava);
# - falha clara quando o item nao existe (sem gerar chave sozinho);
# - TARS_ACTOR=agent assina commits com o daneel, com nome/email dele;
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

  export AUTO_DIR="$XDG_CONFIG_HOME/tars/automation"
  export AUTO_KEY="$AUTO_DIR/daneel_ed25519"
  export SA_TOKEN="$AUTO_DIR/op-sa.token"
  export ALLOWED_SIGNERS="$XDG_CONFIG_HOME/git/allowed_signers"

  export SCRIPT="$REPO_ROOT/app/bootstrap/bootstrap-ubuntu-wsl.sh"
  export FN_SRC="$BATS_TEST_TMPDIR/fns.sh"

  export FAKE_ROOT="$BATS_TEST_TMPDIR/repo"
  mkdir -p "$FAKE_ROOT/app/bootstrap"
  export DOTFILES_REPO_ROOT="$FAKE_ROOT"

  # op em stub: `op read --out-file <arquivo> <ref>` copia de OP_FIXTURES.
  export OP_FIXTURES="$BATS_TEST_TMPDIR/op"
  mkdir -p "$OP_FIXTURES" "$BATS_TEST_TMPDIR/bin"
  cat >"$BATS_TEST_TMPDIR/bin/op" <<'STUB'
#!/usr/bin/env bash
[ "${1:-}" = "read" ] || exit 1
out="" ref=""
shift
while [ $# -gt 0 ]; do
  case "$1" in
    --out-file) out="$2"; shift 2 ;;
    *) ref="$1"; shift ;;
  esac
done
[ -n "$out" ] || exit 1
src="${OP_FIXTURES}/$(printf '%s' "$ref" | tr '/:' '__')"
[ -f "$src" ] || exit 1
cp "$src" "$out"
STUB
  chmod +x "$BATS_TEST_TMPDIR/bin/op"
  export PATH="$BATS_TEST_TMPDIR/bin:$PATH"

  # Fixture de um par ed25519 real (chave de teste, nunca a do dono).
  ssh-keygen -t ed25519 -N '' -C 'daneel@pabloaugusto.com' -f "$BATS_TEST_TMPDIR/daneel_fixture" -q

  # Em Git Bash (Windows) chmod nao tem efeito (dirs ficam 755); a assercao de
  # modo POSIX so vale onde o SO representa permissao de verdade (WSL/Linux).
  local _probe="$BATS_TEST_TMPDIR/permprobe"
  mkdir -p "$_probe"
  chmod 700 "$_probe" 2>/dev/null || true
  export POSIX_MODE_SUPPORTED=0
  [ "$(stat -c '%a' "$_probe" 2>/dev/null || true)" = "700" ] && export POSIX_MODE_SUPPORTED=1

  command -v ssh-keygen >/dev/null 2>&1 || skip "ssh-keygen ausente"
  command -v git >/dev/null 2>&1 || skip "git ausente"

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

load_daneel_fns() {
  {
    extract_fn daneel_default_signing_key_ref
    extract_fn daneel_default_op_token_ref
    extract_fn daneel_default_allowed_signers_ref
    extract_fn _daneel_config_value
    extract_fn _daneel_materialize_ref
    extract_fn _daneel_normalize_key_newline
    extract_fn ensureDaneelIdentity
  } >"$FN_SRC"
  cat "$REPO_ROOT/app/df/bash/.inc/yaml-get.sh" >>"$FN_SRC"
  # shellcheck disable=SC1090
  source "$FN_SRC"
}

op_publish() { # $1=ref $2=arquivo-com-o-conteudo
  cp "$2" "$OP_FIXTURES/$(printf '%s' "$1" | tr '/:' '__')"
}

publish_all_refs() {
  op_publish 'op://secrets/daneel-bot/private key?ssh-format=openssh' "$BATS_TEST_TMPDIR/daneel_fixture"
  printf 'sa-token-de-teste\n' >"$BATS_TEST_TMPDIR/token"
  op_publish 'op://secrets/daneel-bot/1password/service-account' "$BATS_TEST_TMPDIR/token"
  printf 'daneel@pabloaugusto.com %s\n' "$(cat "$BATS_TEST_TMPDIR/daneel_fixture.pub")" >"$BATS_TEST_TMPDIR/as"
  op_publish 'op://secrets/dotfiles/git/allowed_signers' "$BATS_TEST_TMPDIR/as"
}

@test "ensureDaneelIdentity materializa chave 600, op-sa.token e allowed_signers" {
  load_daneel_fns
  publish_all_refs

  run ensureDaneelIdentity
  [ "$status" -eq 0 ]
  [ -f "$AUTO_KEY" ]
  [ -f "$SA_TOKEN" ]
  [ -f "$ALLOWED_SIGNERS" ]

  # Permissoes: dir 700, arquivos 600 (allowed_signers fica 644 para leitura).
  if [ "${POSIX_MODE_SUPPORTED}" = "1" ]; then
    [ "$(stat -c '%a' "$AUTO_DIR")" = "700" ]
    [ "$(stat -c '%a' "$AUTO_KEY")" = "600" ]
    [ "$(stat -c '%a' "$SA_TOKEN")" = "600" ]
  fi

  # A privada nunca aparece na saida; a publica derivada confere com o fixture.
  local priv_head
  priv_head="$(head -n1 "$AUTO_KEY")"
  [[ "$output" != *"$priv_head"* ]]
  [ "$(cat "$AUTO_KEY.pub")" = "$(cat "$BATS_TEST_TMPDIR/daneel_fixture.pub")" ]

  # allowed_signers registrado no git global. O Git normaliza o caminho
  # (ex.: /tmp -> C:/... no Git Bash), entao validamos existencia + nome.
  local configured_signer=""
  configured_signer="$(git config --global --get gpg.ssh.allowedSignersFile)"
  [ -n "$configured_signer" ]
  [ -f "$configured_signer" ]
  case "$configured_signer" in
    *allowed_signers) ;;
    *) false ;;
  esac
}

@test "ensureDaneelIdentity e' idempotente (2a execucao nao regrava)" {
  load_daneel_fns
  publish_all_refs

  ensureDaneelIdentity >/dev/null
  local before="" mtime=""
  before="$(cat "$AUTO_KEY")"
  mtime="$(stat -c '%Y' "$AUTO_KEY")"

  run ensureDaneelIdentity
  [ "$status" -eq 0 ]
  [ "$(cat "$AUTO_KEY")" = "$before" ]
  [ "$(stat -c '%Y' "$AUTO_KEY")" = "$mtime" ]
}

@test "ensureDaneelIdentity falha claro quando o item nao existe no 1Password" {
  load_daneel_fns
  # Nenhum fixture publicado: o stub falha como item inexistente.

  run ensureDaneelIdentity
  [ "$status" -ne 0 ]
  [[ "$output" == *"FALHA"* ]]
  [[ "$output" == *"op://secrets/daneel-bot/private key?ssh-format=openssh"* ]]
  # Nunca gera chave sozinho.
  [ ! -f "$AUTO_KEY" ]
}

@test "TARS_ACTOR=agent assina commit com o daneel, com nome/email dele" {
  load_daneel_fns
  publish_all_refs
  ensureDaneelIdentity >/dev/null

  # shellcheck disable=SC1090
  source "$REPO_ROOT/app/df/bash/.inc/signing-automation.sh"

  local repo="$BATS_TEST_TMPDIR/repo-auto"
  mkdir -p "$repo"
  git -C "$repo" init -q
  git -C "$repo" config gpg.format ssh
  git -C "$repo" config commit.gpgsign true

  printf 'one\n' >"$repo/f"
  git -C "$repo" add f

  export TARS_ACTOR=agent
  dotfiles_apply_automation_signing_env "$repo"

  [ "$GIT_CONFIG_COUNT" = "6" ]
  [ "$GIT_CONFIG_KEY_0" = "user.signingkey" ]
  [ "$GIT_CONFIG_VALUE_0" = "$AUTO_KEY.pub" ]
  [ "$GIT_CONFIG_KEY_2" = "gpg.ssh.allowedSignersFile" ]
  [ "$GIT_CONFIG_VALUE_2" = "$ALLOWED_SIGNERS" ]
  [ "$GIT_CONFIG_KEY_3" = "user.name" ]
  [ "$GIT_CONFIG_VALUE_3" = "Daneel" ]
  [ "$GIT_CONFIG_VALUE_4" = "daneel@pabloaugusto.com" ]
  # Identidade unica: nada de hostname em nome de chave/config.
  [[ "$GIT_CONFIG_VALUE_0" != *"$(hostname)"* ]]

  git -C "$repo" commit -q -m c1
  # %G? = G => assinatura boa; %GS = principal do allowed_signers.
  [ "$(git -C "$repo" log -1 --format=%G?)" = "G" ]
  [ -n "$(git -C "$repo" log -1 --format=%GS?)" ]
}

@test "sem TARS_ACTOR o Git usa a chave humana (nao a do daneel)" {
  load_daneel_fns
  publish_all_refs
  ensureDaneelIdentity >/dev/null

  # Humana: par proprio, configurado no GIT_CONFIG_GLOBAL temporario.
  ssh-keygen -t ed25519 -N '' -C 'human@host' -f "$BATS_TEST_TMPDIR/human_ed25519" -q
  git config --global user.signingkey "$BATS_TEST_TMPDIR/human_ed25519"

  # shellcheck disable=SC1090
  source "$REPO_ROOT/app/df/bash/.inc/signing-automation.sh"

  local repo="$BATS_TEST_TMPDIR/repo-human"
  mkdir -p "$repo"
  git -C "$repo" init -q

  unset TARS_ACTOR
  dotfiles_apply_automation_signing_env "$repo"

  # Sem agente: nenhum override de env e a chave efetiva segue a global humana.
  [ -z "${GIT_CONFIG_COUNT:-}" ]
  local human_key
  human_key="$(git config --global --get user.signingkey)"
  [ -n "$human_key" ]
  [ "$(git -C "$repo" config --get user.signingkey)" = "$human_key" ]
  [ "$(git -C "$repo" config --get user.name)" != "Daneel" ]
}
