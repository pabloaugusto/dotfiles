#!/usr/bin/env bats
#
# Trailer `Machine: <hostname>` nos commits da automacao (daneel).
#
# A identidade de assinatura e' unica (daneel); o host entra apenas no trailer,
# via .githooks/prepare-commit-msg. Idempotente e restrito ao modo automation:
# commits humanos (default) nao ganham trailer.
#
# HOME e GIT_CONFIG_GLOBAL sao temporarios: a config global real nunca e' tocada.

setup() {
  export REPO_ROOT="$PWD"
  export HOOK="$REPO_ROOT/.githooks/prepare-commit-msg"
  export HOME="$BATS_TEST_TMPDIR/home"
  export XDG_CONFIG_HOME="$BATS_TEST_TMPDIR/cfg"
  export GIT_CONFIG_GLOBAL="$BATS_TEST_TMPDIR/gitconfig"
  mkdir -p "$HOME" "$XDG_CONFIG_HOME"
  : >"$GIT_CONFIG_GLOBAL"

  # Roda o hook fora do repo: o ROOT_DIR dele (pwd) nao tem run-python.sh, e o
  # `--inject` do emoji ja e' tolerado com `|| true`.
  export WORK="$BATS_TEST_TMPDIR/work"
  mkdir -p "$WORK"
  cd "$WORK" || return 1

  export MACHINE_SHORT="$(hostname 2>/dev/null || printf 'unknown')"
  export MACHINE_SHORT="${MACHINE_SHORT%%.*}"

  command -v hostname >/dev/null 2>&1 || skip "hostname ausente"
}

run_hook() { # $1=arquivo de mensagem
  bash "$HOOK" "$1"
}

@test "commit do agente (TARS_ACTOR=agent) ganha o trailer Machine" {
  printf 'fix(x): algo\n' >"$WORK/msg"

  TARS_ACTOR=agent run_hook "$WORK/msg"

  grep -qE "^Machine: ${MACHINE_SHORT}$" "$WORK/msg"
  # Trailer exige linha em branco antes.
  grep -qE "^$" "$WORK/msg"
}

@test "trailer e' idempotente (2a execucao nao duplica)" {
  printf 'fix(x): algo\n' >"$WORK/msg"

  TARS_ACTOR=agent run_hook "$WORK/msg"
  TARS_ACTOR=agent run_hook "$WORK/msg"

  [ "$(grep -cE '^Machine: ' "$WORK/msg")" = "1" ]
}

@test "commit humano (sem TARS_ACTOR) nao ganha trailer" {
  printf 'fix(x): algo\n' >"$WORK/msg"

  run_hook "$WORK/msg"

  ! grep -qE '^Machine: ' "$WORK/msg"
  [ "$(cat "$WORK/msg")" = "fix(x): algo" ]
}

@test "trailer tambem vale com DOTFILES_GIT_SIGN_MODE=automation" {
  printf 'fix(x): algo\n' >"$WORK/msg"

  DOTFILES_GIT_SIGN_MODE=automation run_hook "$WORK/msg"

  grep -qE "^Machine: ${MACHINE_SHORT}$" "$WORK/msg"
}

@test "hook tolera arquivo de mensagem ausente sem quebrar" {
  run bash "$HOOK" ""
  [ "$status" -eq 0 ]
}
