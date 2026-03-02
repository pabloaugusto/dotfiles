# Import commands from WSL to PowerShell https://github.com/mikebattista/PowerShell-WSL-Interop
# Requires -> Install-Module WslInterop

Import-WslCommand "find", "grep", "less", "sed", "seq", "tail", "base64", "nano", "direnv", "eval"
