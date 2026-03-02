##########################################################
# Includes
##########################################################
$DotFilesDirectory = "$Env:USERPROFILE\dotfiles"
. "${DotFilesDirectory}\df\powershell\_functions.ps1"
. ${PSScriptRoot}\software-list.ps1


##########################################################
# Split Software List by package installer
##########################################################
$wingetPackages = $softwareList | Where-Object { $_.installer -like "winget" }
#$scoopPackages = $softwareList | Where-Object { $_.installer -like "scoop" }
$chocoPackages = $softwareList | Where-Object { $_.installer -like "choco" }
$powershellModules = $softwareList | Where-Object { $_.installer -like "powershell-module" }
$pipPackages = $softwareList | Where-Object { $_.installer -like "pip" }

##########################################################
# Install Powershell Modules
##########################################################

# $wingetPackages | ForEach-Object { Write-Output $_.id "`n" }
# $scoopPackages | ForEach-Object { Write-Output $_.id "`n" }

# todo: change $_.id to $_ and change id at output to name
$powershellModules | ForEach-Object { Install-PowershellModule ($_.id) }
$wingetInstalledCache = Get-WinGetInstalledCache
$wingetPackages | ForEach-Object {
	Install-WinGetApp -Package ($_.id) -PackageName ($_.name) -InstalledIds $wingetInstalledCache.Ids -InstalledNames $wingetInstalledCache.Names -InstalledNameKeys $wingetInstalledCache.NameKeys
}
$chocoPackages | ForEach-Object { Install-ChocoApp ($_.id) }
$pipPackages | ForEach-Object { Install-PipPackage ($_.id) }

# todo: convert int a function and put in software-list.ps1
Install-Script winfetch -AcceptLicense -Confirm
#https://github.com/Pscx/Pscx
