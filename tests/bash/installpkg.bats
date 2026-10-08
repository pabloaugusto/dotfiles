#!/usr/bin/env bats
#
# installPKG: idempotencia e honestidade do resultado.
#
# Regressoes cobertas:
# - teste de "ja instalado" usava o NOME DO PACOTE, entao `node@22`,
#   `1password-cli@beta` e taps como `fluxcd/tap/flux` nunca eram detectados;
# - falha de install era engolida e reportada como DONE.

setup() {
  export REPO_ROOT="$PWD"
  export STUB_BIN="$BATS_TEST_TMPDIR/bin"
  mkdir -p "$STUB_BIN"
  export PATH="$STUB_BIN:$PATH"

  # Gerenciador que sempre falha, com stderr reconhecivel.
  cat >"$STUB_BIN/brew" <<'STUB'
#!/usr/bin/env bash
echo "Error: formula not found" >&2
echo "linha 2 do erro" >&2
exit 1
STUB
  chmod +x "$STUB_BIN/brew"

  # sudo que apenas repassa (registra os argumentos recebidos).
  cat >"$STUB_BIN/sudo" <<STUB
#!/usr/bin/env bash
echo "\$*" >> "$BATS_TEST_TMPDIR/sudo.log"
shift
exec "\$@"
STUB
  chmod +x "$STUB_BIN/sudo"

  # apt-get que sempre falha.
  cat >"$STUB_BIN/apt-get" <<'STUB'
#!/usr/bin/env bash
echo "E: Unable to locate package" >&2
exit 100
STUB
  chmod +x "$STUB_BIN/apt-get"
}

@test "installPKG retorna != 0 e imprime FAIL quando o install falha" {
  source "$REPO_ROOT/app/df/bash/.inc/_functions.sh"

  run installPKG brew pacote-inexistente

  [ "$status" -ne 0 ]
  [[ "$output" == *"FAIL pacote-inexistente"* ]]
  [[ "$output" == *"Error: formula not found"* ]]
}

@test "installPKG faz SKIP quando o binario ja esta presente" {
  printf '#!/usr/bin/env bash\nexit 0\n' >"$STUB_BIN/ja-existe"
  chmod +x "$STUB_BIN/ja-existe"

  source "$REPO_ROOT/app/df/bash/.inc/_functions.sh"

  run installPKG brew pacote-qualquer ja-existe

  [ "$status" -eq 0 ]
  [[ "$output" == *"SKIP"* ]]
  [[ "$output" != *"Installing"* ]]
}

@test "installPKG deriva o binario de nomes com @versao e prefixo de tap" {
  printf '#!/usr/bin/env bash\nexit 0\n' >"$STUB_BIN/node"
  chmod +x "$STUB_BIN/node"

  source "$REPO_ROOT/app/df/bash/.inc/_functions.sh"

  # node@22         -> node
  run installPKG brew node@22
  [ "$status" -eq 0 ]
  [[ "$output" == *"SKIP node@22"* ]]
}

@test "installPKG nao tenta upgrade de pacote ja instalado" {
  printf '#!/usr/bin/env bash\nexit 0\n' >"$STUB_BIN/zsh"
  chmod +x "$STUB_BIN/zsh"
  cat >"$STUB_BIN/brew" <<'STUB'
#!/usr/bin/env bash
echo "brew chamado: $*" >&2
exit 1
STUB
  chmod +x "$STUB_BIN/brew"

  source "$REPO_ROOT/app/df/bash/.inc/_functions.sh"

  run installPKG brew zsh

  [ "$status" -eq 0 ]
  [[ "$output" != *"upgrade"* ]]
}

@test "installPKG no apt usa sudo com DEBIAN_FRONTEND=noninteractive" {
  source "$REPO_ROOT/app/df/bash/.inc/_functions.sh"

  run installPKG apt postgresql-client psql

  [ "$status" -ne 0 ]
  [[ "$(cat "$BATS_TEST_TMPDIR/sudo.log")" == *"DEBIAN_FRONTEND=noninteractive apt-get install"* ]]
}

@test "installPKG rejeita argumentos ausentes sem derrubar a shell" {
  source "$REPO_ROOT/app/df/bash/.inc/_functions.sh"

  run installPKG "" pacote
  [ "$status" -ne 0 ]

  run installPKG brew ""
  [ "$status" -ne 0 ]
}
