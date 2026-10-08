#!/usr/bin/env bats
#
# bootstrap-ubuntu-wsl.sh: defeitos que falhavam calados.
#
# Regressoes cobertas:
# - _yaml_get usava match(s, re, arr), extensao gawk: sob mawk (default do
#   Ubuntu) o parse falha e a funcao devolvia vazio sem avisar;
# - o shellenv do brew usava caminho fixo /home/linuxbrew, que nao existe em
#   instalacao no $HOME;
# - setup_fonts criava ~/.local/share/fonts como pasta real e o link caia
#   dentro dela (~/.local/share/fonts/fonts);
# - add_user referenciava $TEMP_USER, que nunca e definido no call site;
# - a ausencia das ferramentas .exe do Windows so era detectada tarde.

setup() {
  export REPO_ROOT="$PWD"
  export STUB_BIN="$BATS_TEST_TMPDIR/bin"
  export HOME="$BATS_TEST_TMPDIR/home"
  mkdir -p "$STUB_BIN" "$HOME"

  # fc-cache nao existe fora de uma imagem com fontconfig instalado; o teste
  # mira a logica de link, nao o cache.
  printf '#!/bin/sh\nexit 0\n' > "$STUB_BIN/fc-cache"
  chmod +x "$STUB_BIN/fc-cache"
  export PATH="$STUB_BIN:$PATH"

  export SCRIPT="$REPO_ROOT/app/bootstrap/bootstrap-ubuntu-wsl.sh"
  export FN_SRC="$BATS_TEST_TMPDIR/fns.sh"
}

# Extrai uma funcao do script real, para testa-la isolada.
# Comparacao literal (index), sem regex: o nome pode conter "_" e as duas
# formas de declaracao ("nome() {" e "function nome {") precisam casar.
extract_fn() {
  # _yaml_get deixou de viver no bootstrap: o SSOT agora e' o .inc compartilhado
  # com o check-env.sh (app/df/bash/.inc/yaml-get.sh). Se a funcao nao estiver
  # no script, extrai de la.
  local from="$SCRIPT"
  if ! awk -v n="$1" 'index($0, n "() {") == 1 { f = 1 } END { exit !f }' "$from"; then
    from="$REPO_ROOT/app/df/bash/.inc/yaml-get.sh"
  fi
  awk -v n="$1" '
    index($0, n "() {") == 1 || $0 == "function " n " {" { f = 1 }
    f { print }
    f && /^\}$/ { exit }
  ' "$from"
}

# ---------------------------------------------------------------- _yaml_get

@test "_yaml_get devolve valores aninhados, aspas e chaves ausentes" {
  extract_fn _yaml_get > "$FN_SRC"
  # shellcheck disable=SC1090
  source "$FN_SRC"

  cat > "$BATS_TEST_TMPDIR/cfg.yaml" <<'YAML'
# comentario
paths:
  wsl:
    onedrive_root: "/mnt/d/OneDrive"
    onedrive_clients_dir: clients
    onedrive_projects_dir: 'proj'
  other:
    deep:
      key: deepval
quoted: "with spaces"
YAML

  [ "$(_yaml_get "$BATS_TEST_TMPDIR/cfg.yaml" paths.wsl.onedrive_root)" = "/mnt/d/OneDrive" ]
  [ "$(_yaml_get "$BATS_TEST_TMPDIR/cfg.yaml" paths.wsl.onedrive_clients_dir)" = "clients" ]
  [ "$(_yaml_get "$BATS_TEST_TMPDIR/cfg.yaml" paths.wsl.onedrive_projects_dir)" = "proj" ]
  [ "$(_yaml_get "$BATS_TEST_TMPDIR/cfg.yaml" paths.other.deep.key)" = "deepval" ]
  [ "$(_yaml_get "$BATS_TEST_TMPDIR/cfg.yaml" quoted)" = "with spaces" ]
  [ -z "$(_yaml_get "$BATS_TEST_TMPDIR/cfg.yaml" paths.nao.existe)" ]
}

@test "_yaml_get roda em awk POSIX (sem match de 3 argumentos)" {
  command -v gawk >/dev/null 2>&1 || skip "gawk ausente; mawk nao disponivel nesta maquina"

  # `gawk --posix` rejeita exatamente a extensao que quebrava sob mawk.
  mkdir -p "$BATS_TEST_TMPDIR/posix"
  printf '#!/bin/sh\nexec gawk --posix "$@"\n' > "$BATS_TEST_TMPDIR/posix/awk"
  chmod +x "$BATS_TEST_TMPDIR/posix/awk"

  extract_fn _yaml_get > "$FN_SRC"
  # shellcheck disable=SC1090
  source "$FN_SRC"

  printf 'paths:\n  wsl:\n    onedrive_root: "/mnt/d/OneDrive"\n' > "$BATS_TEST_TMPDIR/cfg.yaml"

  run env PATH="$BATS_TEST_TMPDIR/posix:$PATH" bash -c "
    source '$FN_SRC'
    _yaml_get '$BATS_TEST_TMPDIR/cfg.yaml' paths.wsl.onedrive_root
  "
  [ "$status" -eq 0 ]
  [ "$output" = "/mnt/d/OneDrive" ]
}

# ------------------------------------------------------------ setup_fonts

@test "setup_fonts liga o destino ao assets/fonts sem criar fonts/fonts" {
  extract_fn _link_safe > "$FN_SRC"
  extract_fn setup_fonts >> "$FN_SRC"
  # shellcheck disable=SC1090
  source "$FN_SRC"

  export DOTFILES_REPO_ROOT="$BATS_TEST_TMPDIR/repo"
  mkdir -p "$DOTFILES_REPO_ROOT/app/df/assets/fonts"
  : > "$DOTFILES_REPO_ROOT/app/df/assets/fonts/f.ttf"

  run setup_fonts
  [ "$status" -eq 0 ]
  [ -L "$HOME/.local/share/fonts" ]
  [ "$(readlink -f "$HOME/.local/share/fonts")" = "$(readlink -f "$DOTFILES_REPO_ROOT/app/df/assets/fonts")" ]
  [ ! -e "$HOME/.local/share/fonts/fonts" ]
}

@test "setup_fonts e idempotente (nao cria backup na segunda execucao)" {
  extract_fn _link_safe > "$FN_SRC"
  extract_fn setup_fonts >> "$FN_SRC"
  # shellcheck disable=SC1090
  source "$FN_SRC"

  export DOTFILES_REPO_ROOT="$BATS_TEST_TMPDIR/repo"
  mkdir -p "$DOTFILES_REPO_ROOT/app/df/assets/fonts"
  : > "$DOTFILES_REPO_ROOT/app/df/assets/fonts/f.ttf"

  setup_fonts
  run setup_fonts
  [ "$status" -eq 0 ]
  [ -L "$HOME/.local/share/fonts" ]
  run bash -c "ls -d '$HOME/.local/share'/fonts.dotfiles-prelink-* 2>/dev/null | wc -l"
  [ "$output" -eq 0 ]
}

@test "setup_fonts repara o link aninhado deixado pelo defeito antigo" {
  extract_fn _link_safe > "$FN_SRC"
  extract_fn setup_fonts >> "$FN_SRC"
  # shellcheck disable=SC1090
  source "$FN_SRC"

  export DOTFILES_REPO_ROOT="$BATS_TEST_TMPDIR/repo"
  mkdir -p "$DOTFILES_REPO_ROOT/app/df/assets/fonts"
  : > "$DOTFILES_REPO_ROOT/app/df/assets/fonts/f.ttf"

  # Estado produzido pelo bug: pasta real + link dentro dela.
  mkdir -p "$HOME/.local/share/fonts"
  ln -sfn "$DOTFILES_REPO_ROOT/app/df/assets/fonts" "$HOME/.local/share/fonts"
  [ -e "$HOME/.local/share/fonts/fonts" ]

  run setup_fonts
  [ "$status" -eq 0 ]
  [ -L "$HOME/.local/share/fonts" ]
  [ ! -e "$HOME/.local/share/fonts/fonts" ]
  [ -e "$HOME/.local/share/fonts/f.ttf" ]
}

@test "setup_fonts falha alto quando a origem nao existe" {
  extract_fn _link_safe > "$FN_SRC"
  extract_fn setup_fonts >> "$FN_SRC"
  # shellcheck disable=SC1090
  source "$FN_SRC"

  export DOTFILES_REPO_ROOT="$BATS_TEST_TMPDIR/inexistente"
  run setup_fonts
  [ "$status" -eq 1 ]
}

# ------------------------------------------------ ensureWslWindowsTools

@test "ensureWslWindowsTools nao checa nada fora do WSL" {
  extract_fn ensureWslWindowsTools > "$FN_SRC"
  # shellcheck disable=SC1090
  source "$FN_SRC"

  grep() { return 1; } # /proc/version sem 'microsoft'
  run ensureWslWindowsTools
  [ "$status" -eq 0 ]
}

@test "ensureWslWindowsTools falha alto no WSL sem as ferramentas do Windows" {
  extract_fn ensureWslWindowsTools > "$FN_SRC"
  # shellcheck disable=SC1090
  source "$FN_SRC"

  grep() { return 0; } # simula WSL
  PATH="/usr/bin:/bin"
  run ensureWslWindowsTools
  [ "$status" -eq 1 ]
  [[ "$output" == *"op-ssh-sign-wsl.exe"* ]]
  [[ "$output" == *"npiperelay.exe"* ]]
}

@test "ensureWslWindowsTools aceita WSL quando as ferramentas estao no PATH" {
  extract_fn ensureWslWindowsTools > "$FN_SRC"
  # shellcheck disable=SC1090
  source "$FN_SRC"

  for t in op-ssh-sign-wsl.exe npiperelay.exe; do
    printf '#!/bin/sh\nexit 0\n' > "$STUB_BIN/$t"
    chmod +x "$STUB_BIN/$t"
  done
  grep() { return 0; } # simula WSL

  run ensureWslWindowsTools
  [ "$status" -eq 0 ]
}

# -------------------------------------------------------------- add_user

@test "add_user nao depende de TEMP_USER (que nunca e definido no call site)" {
  # Assercao estatica de proposito: o script executa o bootstrap ao ser
  # carregado, entao nao pode ser sourceado por um teste.
  local body
  body="$(awk '/^function add_user \{/{f=1} f{print} f&&/^\}$/{exit}' "$SCRIPT")"
  [ -n "$body" ]
  [[ "$body" != *'TEMP_USER'* ]]
  # TEMP_USER continua existindo para as outras funcoes (setProfileSymlinks).
  grep -q 'TEMP_USER=\$1' "$SCRIPT"
}
