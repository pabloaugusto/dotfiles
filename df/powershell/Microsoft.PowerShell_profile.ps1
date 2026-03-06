################################################################################
# Host-specific PowerShell profile shim.
#
# PowerShell 7+ already loads the canonical runtime from:
#   df/powershell/profile.ps1
#
# Windows PowerShell 5.1 cannot parse parts of the PowerShell 7 runtime, so
# this shim limits itself to the aliases map to preserve basic ergonomics like
# `ag -> antigravity`.
################################################################################
$DotFilesDirectory = "$Env:USERPROFILE\dotfiles"
$PWSconfDir = Join-Path $DotFilesDirectory 'df\powershell'

if (-not (Test-Path -Path $PWSconfDir -PathType Container)) {
	return
}

if ($PSVersionTable.PSVersion.Major -ge 7) {
	return
}

. (Join-Path $PWSconfDir 'aliases.ps1') -WarningAction SilentlyContinue
