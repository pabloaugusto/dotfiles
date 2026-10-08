################################################################################
# app/df/powershell/env-vars.ps1
#
# Persists baseline environment variables to HKCU for new terminal sessions.
# This file intentionally writes user-scoped values (not machine-wide).
################################################################################

# TODO: check if path exists before set each env var
# set custom envs

# this method is way faster
# https://stackoverflow.com/questions/4825967/environment-setenvironmentvariable-takes-a-long-time-to-set-a-variable-at-user-o#comment135137797_4826777

Set-ItemProperty -Path HKCU:\Environment -Name 'MYDOCS' -Value " $Env:USERPROFILE\documents"
Set-ItemProperty -Path HKCU:\Environment -Name 'PROJECTS' -Value "$Env:USERPROFILE\projects"
Set-ItemProperty -Path HKCU:\Environment -Name 'DOTFILES' -Value (Get-DotfilesRepoPath)
Set-ItemProperty -Path HKCU:\Environment -Name 'CLIENTS' -Value "$Env:USERPROFILE\clients"
# A chave age vive apenas em arquivo com ACL restrita; nunca no ambiente.
# Remove conteudo de chave persistido por versoes anteriores do bootstrap.
Remove-ItemProperty -Path HKCU:\Environment -Name 'SOPS_AGE_KEY' -ErrorAction SilentlyContinue
Set-ItemProperty -Path HKCU:\Environment -Name 'HOME_OPS' -Value "$Env:USERPROFILE\projects\home-ops"

# direnv (set env vars needed due a bug https://github.com/direnv/direnv/issues/1105)
Set-ItemProperty -Path HKCU:\Environment -Name 'DIRENV_CONFIG' -Value "$Env:USERPROFILE\.config"
Set-ItemProperty -Path HKCU:\Environment -Name 'XDG_CACHE_HOME' -Value "$Env:USERPROFILE\.config"
Set-ItemProperty -Path HKCU:\Environment -Name 'XDG_DATA_HOME' -Value "$Env:USERPROFILE\.config"

# git ssh command conditional to OS
Set-ItemProperty -Path HKCU:\Environment -Name 'GIT_SSH_COMMAND' -Value 'C:\\Windows\\System32\\OpenSSH\\ssh.exe'

# powershell
$pwshProfilePath = Split-Path -Parent ${PROFILE}
Set-ItemProperty -Path HKCU:\Environment -Name 'PWSH_PROFILE_PATH' -Value "$pwshProfilePath" #faster

# Add APPs folder to PATH
$Env:Path +=
"$Env:PROGRAMFILES\7-Zip\;
$Env:PROGRAMFILES\Git\bin;
/mnt/c/ProgramData/chocolatey/bin/direnv;"
