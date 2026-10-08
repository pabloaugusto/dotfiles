#!/usr/bin/env bats

setup() {
  export REPO_ROOT="$PWD"
  export HOME="$BATS_TEST_TMPDIR/home"
  export USER="tester"
  export DOTFILES_REPO_ROOT_UNIX="$REPO_ROOT"
  export DOTFILES_ONEDRIVE_ROOT="$BATS_TEST_TMPDIR/onedrive"
  export DOTFILES_ONEDRIVE_CLIENTS_DIR="clients"
  export DOTFILES_ONEDRIVE_PROJECTS_DIR="clients/tester/projects"

  mkdir -p \
    "$HOME/.config" \
    "$DOTFILES_ONEDRIVE_ROOT/clients/tester/projects"
}

@test "relink cria symlinks canonicos no perfil Linux" {
  run bash "$REPO_ROOT/app/bootstrap/bootstrap-ubuntu-wsl.sh" relink

  [ "$status" -eq 0 ]
  [ -L "$HOME/.ssh" ]
  [ "$(readlink -f "$HOME/.ssh")" = "$REPO_ROOT/app/df/ssh" ]
  [ -L "$HOME/.config/git" ]
  [ "$(readlink -f "$HOME/.config/git")" = "$REPO_ROOT/app/df/git" ]
  [ -L "$HOME/.config/Code/User" ]
  [ "$(readlink -f "$HOME/.config/Code/User")" = "$REPO_ROOT/app/df/vscode" ]
  [ -L "$HOME/projects" ]
  [ "$(readlink -f "$HOME/projects")" = "$DOTFILES_ONEDRIVE_ROOT/clients/tester/projects" ]
  [ -L "$HOME/clients" ]
  [ "$(readlink -f "$HOME/clients")" = "$DOTFILES_ONEDRIVE_ROOT/clients" ]
  [ -L "$HOME/onedrive" ]
  [ "$(readlink -f "$HOME/onedrive")" = "$DOTFILES_ONEDRIVE_ROOT" ]
}

@test "relink Linux e idempotente" {
  run bash "$REPO_ROOT/app/bootstrap/bootstrap-ubuntu-wsl.sh" relink
  [ "$status" -eq 0 ]

  run bash "$REPO_ROOT/app/bootstrap/bootstrap-ubuntu-wsl.sh" relink
  [ "$status" -eq 0 ]
  [ -L "$HOME/.bashrc" ]
  [ "$(readlink -f "$HOME/.bashrc")" = "$REPO_ROOT/app/df/bash/.bashrc" ]
  [ -L "$HOME/.zshrc" ]
  [ "$(readlink -f "$HOME/.zshrc")" = "$REPO_ROOT/app/df/zsh/.zshrc" ]
}

@test "relink preserva pasta real do usuario com backup prelink" {
  mkdir -p "$HOME/.ssh"
  echo "minha-chave-real" > "$HOME/.ssh/id_rsa"

  run bash "$REPO_ROOT/app/bootstrap/bootstrap-ubuntu-wsl.sh" relink
  [ "$status" -eq 0 ]

  # pasta original preservada num backup, nao destruida
  backup="$(echo "$HOME"/.ssh.dotfiles-prelink-* )"
  [ -d "$backup" ]
  [ "$(cat "$backup/id_rsa")" = "minha-chave-real" ]
  # e o link canonico foi criado
  [ -L "$HOME/.ssh" ]
  [ "$(readlink -f "$HOME/.ssh")" = "$REPO_ROOT/app/df/ssh" ]
}

@test "relink nao faz backup repetido de link ja correto" {
  run bash "$REPO_ROOT/app/bootstrap/bootstrap-ubuntu-wsl.sh" relink
  [ "$status" -eq 0 ]
  run bash "$REPO_ROOT/app/bootstrap/bootstrap-ubuntu-wsl.sh" relink
  [ "$status" -eq 0 ]

  # glob precisa incluir dotfiles (backups comecam com '.')
  run bash -c "find \"$HOME\" -maxdepth 1 -name '.*.dotfiles-prelink-*' | wc -l"
  [ "$output" = "0" ]
}

@test "relink nao quebra o symlink de .bashrc" {
  run bash "$REPO_ROOT/app/bootstrap/bootstrap-ubuntu-wsl.sh" relink
  [ "$status" -eq 0 ]

  [ -L "$HOME/.bashrc" ]
  [ -L "$HOME/.profile" ]
}

