#!/usr/bin/env bash

###############################################################################
# bootstrap/scripts/install-windows.sh
#
# Legacy script for Git Bash on Windows to create symlinks and copy terminal
# assets. It is retained for historical support and quick manual recovery.
#
# Canonical path today:
# - Use bootstrap/_start.ps1 on Windows host.
#
# This script does not implement the current one-credential auth/secrets model.
###############################################################################

dir=~/dotfiles
files=" .aliases
        .bash_profile
        .bashrc
        .bash_prompt
        .exports
        .gitconfig
        .minttyrc
        .vimrc
        .inputrc
        .editorconfig
        .eslintrc.js
        package.json
        package-lock.json"

for file in $files; do
    echo "Creating symlink to $file in home directory."
    ln -sf "$dir/$file" ~/$file
done

# Windows Terminal settings
terminalDir=~/AppData/Local/Packages/Microsoft.WindowsTerminal_8wekyb3d8bbwe
if [ -d "$terminalDir" ]; then
    cp ./windows-terminal-settings.json "$terminalDir/LocalState/settings.json"
    cp ./git-bash.ico "$terminalDir/RoamingState"
    cp ./ubuntu.ico "$terminalDir/RoamingState"
fi

# echo "Installing npm dependencies..."
# cd ~/ && npm i
