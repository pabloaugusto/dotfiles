#!/usr/bin/env bats

setup() {
  export REPO_ROOT="$PWD"
  export HOME="$BATS_TEST_TMPDIR/home"
  export USER="tester"
  export DOTFILES_REPO_ROOT_UNIX="$REPO_ROOT"
  export DOTFILES_BOOTSTRAP_ASSUME_POLO="1"
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
