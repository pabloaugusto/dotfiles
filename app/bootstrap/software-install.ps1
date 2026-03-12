################################################################################
# app/bootstrap/software-install.ps1
#
# Legacy helper to install software catalog entries grouped by installer type.
# The active Windows bootstrap path already performs equivalent logic directly
# in app/bootstrap/bootstrap-windows.ps1, but this file remains useful for manual
# execution and troubleshooting isolated package-install issues.
#
# Input dependency:
# - app/bootstrap/software-list.ps1 (provides $softwareList array)
# - app/df/powershell/_functions.ps1 (installer helper functions)
################################################################################

##########################################################
# Includes
##########################################################
$DotFilesDirectory = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
. "${DotFilesDirectory}\app\df\powershell\_functions.ps1"
. ${PSScriptRoot}\software-list.ps1

##########################################################
# Split software list by package manager
##########################################################
$wingetPackages = $softwareList | Where-Object { $_.installer -like "winget" }
# $scoopPackages = $softwareList | Where-Object { $_.installer -like "scoop" }
$chocoPackages = $softwareList | Where-Object { $_.installer -like "choco" }
$powershellModules = $softwareList | Where-Object { $_.installer -like "powershell-module" }
$pipPackages = $softwareList | Where-Object { $_.installer -like "pip" }

##########################################################
# Execute installation batches
##########################################################
# Order choice:
# 1) PowerShell modules first (some aliases/profile hooks depend on them).
# 2) winget/choco/pip packages next.

$powershellModules | ForEach-Object { Install-PowershellModule ($_.id) }

$wingetInstalledCache = Get-WinGetInstalledCache
$wingetPackages | ForEach-Object {
	Install-WinGetApp -Package ($_.id) -PackageName ($_.name) -InstalledIds $wingetInstalledCache.Ids -InstalledNames $wingetInstalledCache.Names -InstalledNameKeys $wingetInstalledCache.NameKeys
}

$chocoPackages | ForEach-Object { Install-ChocoApp ($_.id) }
$pipPackages | ForEach-Object { Install-PipPackage ($_.id) }

# Optional CLI script managed historically by this helper.
Install-Script winfetch -AcceptLicense -Confirm
