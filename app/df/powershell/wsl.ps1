################################################################################
# app/df/powershell/wsl.ps1
#
# Bridges selected Linux commands from WSL into PowerShell via WslInterop.
# This is optional convenience for mixed Windows+WSL workflows.
################################################################################

# Import commands from WSL to PowerShell.
# Reference: https://github.com/mikebattista/PowerShell-WSL-Interop
if (Get-Module -ListAvailable -Name WslInterop) {
	Import-WslCommand "find", "grep", "less", "sed", "seq", "tail", "base64", "nano", "direnv", "eval"
}
