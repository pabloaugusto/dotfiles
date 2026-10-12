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

# --- Ferramentas exigidas: caminho Linux, nao caminho do Windows -------------
#
# O PATH do Windows continua visivel no WSL (appendWindowsPath padrao). Se
# `command -v` resolve um comando exigido para /mnt/*, o binario so existe do
# lado Windows: o bootstrap Linux nao instalou nada. O mount /mnt e simulado
# por DOTFILES_WINDOWS_PATH_PREFIX apontando para um diretorio temporario.

# Cria um "mount do Windows" simulado com um stub de kubeconform.
_fake_windows_mount() {
  FAKE_MNT="$BATS_TEST_TMPDIR/win-mnt"
  mkdir -p "$FAKE_MNT"
  printf '#!/usr/bin/env bash\nexit 0\n' >"$FAKE_MNT/kubeconform"
  chmod +x "$FAKE_MNT/kubeconform"
  export FAKE_MNT
  export PATH="$FAKE_MNT:$PATH"
}

@test "checkEnv marca FALHA quando comando exigido resolve so no Windows (/mnt)" {
  cd "$PROBE_REPO"
  _fake_windows_mount
  export DOTFILES_WINDOWS_PATH_PREFIX="$FAKE_MNT"

  source "$REPO_ROOT/app/df/bash/.inc/check-env.sh"
  run checkEnv
  [[ "$output" == *"[FALHA] Command: kubeconform"* ]]
  [[ "$output" == *"instalado so no Windows"* ]]
  [[ "$output" != *"[OK] Command: kubeconform"* ]]
  [ "$status" -ne 0 ]
}

@test "checkEnv marca OK quando o mesmo comando resolve em caminho Linux" {
  cd "$PROBE_REPO"
  _fake_windows_mount
  # Prefixo que nao casa: o binario esta em caminho Linux, nao no mount.
  export DOTFILES_WINDOWS_PATH_PREFIX="$BATS_TEST_TMPDIR/nao-e-mount"

  source "$REPO_ROOT/app/df/bash/.inc/check-env.sh"
  run checkEnv
  [[ "$output" == *"[OK] Command: kubeconform"* ]]
  [[ "$output" != *"[FALHA] Command: kubeconform"* ]]
}

@test "checkEnv exige bats e nao exige node/npm/yarn/pnpm" {
  local expected_block
  expected_block="$(sed -n '/^  local _expected_cmds=(/,/^  )/p' "$REPO_ROOT/app/df/bash/.inc/check-env.sh")"
  [ -n "$expected_block" ]

  [[ "$expected_block" == *"bats"* ]]
  [[ "$expected_block" != *"node"* ]]
  [[ "$expected_block" != *"npm"* ]]
  [[ "$expected_block" != *"yarn"* ]]
  [[ "$expected_block" != *"pnpm"* ]]
}

@test "bootstrap-ubuntu-wsl.sh instala bats e nao instala node/npm/yarn/pnpm" {
  local bootstrap="$REPO_ROOT/app/bootstrap/bootstrap-ubuntu-wsl.sh"
  ! grep -E 'install_counted[^#]*\b(node|npm|yarn|pnpm)\b' "$bootstrap"
  grep -E 'install_counted (apt|brew) bats' "$bootstrap"
}

# --- Gate do probe de assinatura (nao pode ser rebaixado para warning) --------
#
# Regra: `warning` SO quando o agente exige desbloqueio humano (agente sem
# chaves listadas / 1Password bloqueado) ou timeout por prompt de aprovacao,
# sempre com "requer desbloqueio" e o comando de validacao. Signer ausente,
# chave publica ilegivel e erro real de assinatura sao `fail`.

# Stub configuravel: FAIL_MSG / FAIL_RC controlam a resposta de `-Y sign`.
_stub_ssh_keygen_fail() {
  export SIGN_FAIL_MSG="$1"
  export SIGN_FAIL_RC="${2:-255}"
  cat >"$STUB_BIN/ssh-keygen" <<'STUB'
#!/usr/bin/env bash
case " $* " in
  *" -Y sign "*)
    printf '%s\n' "$SIGN_FAIL_MSG" >&2
    exit "$SIGN_FAIL_RC"
    ;;
esac
for arg in "$@"; do last="$arg"; done
: >"${last}.sig"
exit 0
STUB
  chmod +x "$STUB_BIN/ssh-keygen"
}

@test "checkEnv marca FALHA quando user.signingkey esta ausente" {
  cd "$PROBE_REPO"
  git config user.signingkey ""
  source "$REPO_ROOT/app/df/bash/.inc/check-env.sh"

  run checkEnv
  [[ "$output" == *"[FALHA] Signature verification"* ]]
  [[ "$output" == *"signer nao configurado"* ]]
  [ "$status" -ne 0 ]
}

@test "checkEnv marca FALHA quando user.signingkey nao e chave legivel" {
  cd "$PROBE_REPO"
  git config user.signingkey "$BATS_TEST_TMPDIR/nao-existe/nem-publica"
  source "$REPO_ROOT/app/df/bash/.inc/check-env.sh"

  run checkEnv
  [[ "$output" == *"[FALHA] Signature verification"* ]]
  [[ "$output" == *"chave publica ilegivel"* ]]
  [ "$status" -ne 0 ]
}

@test "checkEnv marca FALHA em erro real de assinatura" {
  cd "$PROBE_REPO"
  printf 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIfake checkenv@test\n' >"$BATS_TEST_TMPDIR/fake.pub"
  git config user.signingkey "$BATS_TEST_TMPDIR/fake.pub"
  _stub_ssh_keygen_fail "unknown key type" 255
  source "$REPO_ROOT/app/df/bash/.inc/check-env.sh"

  run checkEnv
  [[ "$output" == *"[FALHA] Signature verification"* ]]
  [[ "$output" == *"erro real de assinatura"* ]]
  [[ "$output" != *"[AVISO] Signature verification"* ]]
  [ "$status" -ne 0 ]
}

@test "checkEnv marca AVISO com 'requer desbloqueio' quando o agente exige unlock" {
  cd "$PROBE_REPO"
  printf 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIfake checkenv@test\n' >"$BATS_TEST_TMPDIR/fake.pub"
  git config user.signingkey "$BATS_TEST_TMPDIR/fake.pub"
  _stub_ssh_keygen_fail 'No private key found for public key "fake.pub"' 255
  source "$REPO_ROOT/app/df/bash/.inc/check-env.sh"

  run checkEnv
  [[ "$output" == *"[AVISO] Signature verification"* ]]
  [[ "$output" == *"requer desbloqueio"* ]]
  [[ "$output" == *"valide com: ssh-keygen -Y sign"* ]]
  [[ "$output" != *"[FALHA] Signature verification"* ]]
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
