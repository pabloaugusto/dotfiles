#!/usr/bin/env bats
#
# checkEnv (bash): validacao real, sem prompt de biometria.
#
# Regressoes cobertas:
# - `$git_probe` era lido ANTES de ser atribuido: o bloco de refs 1Password
#   nunca encontrava `<repo>/app/df/secrets/secrets-ref.yaml` e o check
#   silenciosamente caia no fallback `$HOME/dotfiles`, reportando sucesso
#   vazio. Agora o probe e resolvido antes de qualquer consumidor.
# - binarios esperados: lista unica derivada do install_software do
#   app/bootstrap/bootstrap-ubuntu-wsl.sh, cada item com success/fail.
# - saida final: tabela OK/FALHA e exit code != 0 quando ha FALHA.

setup() {
  # CHECKENV_UNDER_TEST permite apontar para uma arvore alternativa (usado no
  # controle negativo: o teste tem que FALHAR contra a versao pre-fix).
  export REPO_ROOT="${CHECKENV_UNDER_TEST:-$PWD}"
  export STUB_BIN="$BATS_TEST_TMPDIR/bin"
  mkdir -p "$STUB_BIN"
  export PATH="$STUB_BIN:$PATH"

  # HOME falso: garante que o fallback $HOME/dotfiles nao existe, entao a
  # UNICA forma de achar secrets-ref.yaml e via $git_probe.
  export HOME="$BATS_TEST_TMPDIR/home"
  mkdir -p "$HOME"

  export OP_LOG="$BATS_TEST_TMPDIR/op.log"
  : >"$OP_LOG"

  cat >"$STUB_BIN/op" <<'STUB'
#!/usr/bin/env bash
printf '%s\n' "$*" >>"$OP_LOG"
case "$1" in
  whoami) exit 0 ;;
  read) exit 0 ;;
  *) exit 0 ;;
esac
STUB
  chmod +x "$STUB_BIN/op"

  cat >"$STUB_BIN/gh" <<'STUB'
#!/usr/bin/env bash
case "$1 $2" in
  "auth status") echo "Logged in to github.com"; exit 0 ;;
  "config get") echo "ssh"; exit 0 ;;
  *) exit 0 ;;
esac
STUB
  chmod +x "$STUB_BIN/gh"

  cat >"$STUB_BIN/ssh" <<'STUB'
#!/usr/bin/env bash
for arg in "$@"; do
  if [ "$arg" = "-G" ]; then
    echo "identityagent /tmp/1password-agent.sock"
    echo "identityfile none"
    exit 0
  fi
done
echo "Hi! You've successfully authenticated, but GitHub does not provide shell access."
exit 1
STUB
  chmod +x "$STUB_BIN/ssh"

  # ssh-keygen -Y sign <key> <payload>: simula agent desbloqueado criando .sig
  cat >"$STUB_BIN/ssh-keygen" <<'STUB'
#!/usr/bin/env bash
for arg in "$@"; do last="$arg"; done
: >"${last}.sig"
exit 0
STUB
  chmod +x "$STUB_BIN/ssh-keygen"

  # Repo temporario que contem a ref de segredo, para exercitar $git_probe.
  export PROBE_REPO="$BATS_TEST_TMPDIR/probe-repo"
  mkdir -p "$PROBE_REPO/app/df/secrets"
  printf 'refs:\n  - op://test/vault/item\n' >"$PROBE_REPO/app/df/secrets/secrets-ref.yaml"
  git -C "$PROBE_REPO" init -q
}

@test "checkEnv resolve secrets-ref.yaml via git_probe do repo atual" {
  cd "$PROBE_REPO"
  source "$REPO_ROOT/app/df/bash/.inc/check-env.sh"

  run checkEnv
  # A ref so pode ter sido lida de <repo>/app/df/secrets/secrets-ref.yaml.
  run grep -F "read op://test/vault/item" "$OP_LOG"
  [ "$status" -eq 0 ]
}

@test "checkEnv reporta Command: task como FALHA quando ausente do PATH" {
  cd "$PROBE_REPO"

  # Esconde o diretorio que fornece `task` para que a ausencia seja
  # deterministica, independente da maquina que roda o teste.
  local hide_dir clean_path p
  hide_dir="$(dirname "$(command -v task)")"
  clean_path="$STUB_BIN"
  IFS=':' read -ra _parts <<<"$PATH"
  for p in "${_parts[@]}"; do
    [ "$p" = "$hide_dir" ] && continue
    clean_path="$clean_path:$p"
  done
  export PATH="$clean_path"
  command -v task >/dev/null && skip "task ainda resolvivel; teste nao aplicavel"

  source "$REPO_ROOT/app/df/bash/.inc/check-env.sh"
  run checkEnv
  [[ "$output" == *"[FALHA] Command: task"* ]]
  [[ "$output" != *"[OK] Command: task"* ]]
}

@test "checkEnv imprime tabela final OK/FALHA e retorna != 0 com FALHA" {
  cd "$PROBE_REPO"
  source "$REPO_ROOT/app/df/bash/.inc/check-env.sh"

  run checkEnv
  [ "$status" -ne 0 ]
  [[ "$output" == *"RESULTADO"* ]]
  [[ "$output" == *"FALHA"* ]]
  [[ "$output" == *"Summary: ok="* ]]
}

@test "checkEnv nao dispara git commit -S (sem prompt de biometria)" {
  cd "$PROBE_REPO"
  # git que falha o teste se receber `commit -S`.
  cat >"$STUB_BIN/git" <<'STUB'
#!/usr/bin/env bash
for arg in "$@"; do
  [ "$arg" = "-S" ] && { echo "BIOMETRY PROMPT TRIGGERED" >&2; exit 99; }
done
exec /usr/bin/git "$@"
STUB
  chmod +x "$STUB_BIN/git"

  source "$REPO_ROOT/app/df/bash/.inc/check-env.sh"
  run checkEnv
  [[ "$output" != *"BIOMETRY PROMPT TRIGGERED"* ]]
}
