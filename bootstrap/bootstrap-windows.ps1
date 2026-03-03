# inspired in https://github.com/rodolphocastro/dotfiles/
param (
	[switch]$RefreshDotfiles
)

#################################################################################
# Windows bootstrap executor
#
# Modes:
# - default (new install): full setup (links + apps + fonts + prefs + auth/checks)
# - -RefreshDotfiles: update links/config/runtime auth without full software phase
#
# Design choice:
# Auth/signing checks run in both modes to guarantee git/ssh/gh conformity.
#
# Execution phases:
# 1) Safety checks + dotfiles links
# 2) Optional software/fonts/preferences (full mode)
# 3) Mandatory auth/signing bootstrap (both modes)
# 4) Final checkEnv gate
#################################################################################

if (! ($MyInvocation.InvocationName -eq ".")) {
	Write-Output "cant run directly. Run _start.ps1 instead"
	exit 1
}

# install (or upgrade) powershell, choco, scoop
# winget comes with windows 10+ by default
# NOTE:
# Prerequisite installs are handled later in the flow/functions to avoid noisy
# warnings when packages are already present or source ids differ across hosts.

# pwsh -File $PSCommandPath -ExecutionPolicy Bypass

Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser
#Invoke-RestMethod get.scoop.sh | Invoke-Expression


#################################################################################
# verify: dotfiles was cloned from github?
#################################################################################
	$DotFilesDirectory = "$Env:USERPROFILE\dotfiles"
	if (!(Test-Path "$DotFilesDirectory")) {
		Write-Host -ForegroundColor red "Folder $Env:USERPROFILE\dotfiles. Did you forgot clone dotfiles?"
		break
	} else {
		. "${DotFilesDirectory}\df\powershell\_functions.ps1"
	}

#################################################################################
# verify: runnning bootstrap on elevated powershell (as admin)?
#################################################################################
	if (! (Test-PowershellElevated)){
		Write-Host -ForegroundColor red "This script must run on elevated powershell (as admin)"
		break
	}

#################################################################################
# verify: really want run bootstrap?
#################################################################################
	Write-Warning "This script will override some of your home files"
	Write-Warning "If you are okay with that complete the sentence below..."

	$Answer = Read-Host -Prompt "MARCO"
	if ($Answer -ne "POLO") {
		Write-Host "At least you have chicken 🐔"
		break
	}

#################################################################################
# bootstrap: symlink to onedrive folders
#################################################################################
#Write-Output "Replacing OneDrive Dirs"
if ($Env:Onedrive) {
	# User-agnostic project target:
	# - optional override: DOTFILES_ONEDRIVE_PROJECTS_PATH
	# - default: <OneDrive>\clients\<USERNAME>\projects
	$oneDriveProjectsPath = if (-not [string]::IsNullOrWhiteSpace($Env:DOTFILES_ONEDRIVE_PROJECTS_PATH)) {
		$Env:DOTFILES_ONEDRIVE_PROJECTS_PATH
	}
	else {
		Join-Path $Env:Onedrive ("clients\{0}\projects" -f $Env:USERNAME)
	}

	Add-Symlink "$Env:USERPROFILE\bin" "$Env:Onedrive\bin" > $null
	Add-Symlink "$Env:USERPROFILE\etc" "$Env:Onedrive\etc" > $null
	Add-Symlink "$Env:USERPROFILE\clients" "$Env:Onedrive\clients" > $null
	# Add-Symlink "${mydocs}" "$Env:Onedrive\documents" > $null
	Add-Symlink "$Env:USERPROFILE\projects" "$oneDriveProjectsPath" > $null

	Add-Symlink "d:\bin" "$Env:Onedrive\bin" > $null
	Add-Symlink "d:\etc" "$Env:Onedrive\etc" > $null
	Add-Symlink "d:\clients" "$Env:Onedrive\clients" > $null
	Add-Symlink "d:\projects" "$oneDriveProjectsPath" > $null

	# documents and image path change
	# Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" -name "Personal" -value "D:\OneDrive\documents"
	# Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" -name "My Pictures"  -value "D:\OneDrive\images"
	# Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" -name "Desktop"  -value "D:\OneDrive\desktop"
	# Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" -name "My Pictures"  -value "D:\OneDrive\images"
	# Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" -name "My Pictures"  -value "D:\OneDrive\images"
	# Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" -name "My Pictures"  -value "D:\OneDrive\images"

	# Computer\HKEY_CURRENT_USER\Software\Microsoft\OneDrive\Accounts\Personal


	### \\wsl$\Ubuntu\home\<user>

}
else {
	Write-Warning "ENV:OneDrive not found. Aborting"
	return
}

#################################################################################
# bootstrap: symlink dotfiles
#################################################################################
	#Write-Output "Replacing dotfiles"
	# remove deprecated .sops symlink from old layout if it points to dotfiles\df\sops
	$legacySopsLink = "$Env:USERPROFILE\.sops"
	if (Test-Path -Path $legacySopsLink) {
		$legacySopsItem = Get-Item -Path $legacySopsLink -Force -ErrorAction SilentlyContinue
		if ($null -ne $legacySopsItem -and $legacySopsItem.LinkType -eq 'SymbolicLink' -and "$($legacySopsItem.Target)" -like "*\dotfiles\df\sops*") {
			Remove-Item -Path $legacySopsLink -Force -ErrorAction SilentlyContinue
		}
	}

	Add-Symlink "$Env:USERPROFILE\.ssh" "$DotFilesDirectory\df\ssh" > $null
	Add-Symlink "$Env:USERPROFILE\.assets" "$DotFilesDirectory\df\assets" > $null
	Add-Symlink "$Env:USERPROFILE\.editorconfig" "$DotFilesDirectory\df\.editorconfig" > $null
	Add-Symlink "$Env:USERPROFILE\.gitconfig" "$DotFilesDirectory\df\git\.gitconfig" > $null
	Add-Symlink "$Env:USERPROFILE\.config\git" "$DotFilesDirectory\df\git" > $null
	Add-Symlink "$Env:USERPROFILE\.gitconfig-windows" "$DotFilesDirectory\df\git\.gitconfig-windows" > $null
	Add-Symlink "$Env:USERPROFILE\.gitconfig.local.sample" "$DotFilesDirectory\df\git\.gitconfig.local.sample" > $null
	Add-Symlink "$Env:USERPROFILE\.bashrc" "$DotFilesDirectory\df\bash\.bashrc" > $null
	Add-Symlink "$Env:USERPROFILE\.bash_profile" "$DotFilesDirectory\df\bash\.bash_profile" > $null
	Add-Symlink "$Env:USERPROFILE\.bashrc_profile" "$DotFilesDirectory\df\bash\.bashrc_profile" > $null
	Add-Symlink "$Env:USERPROFILE\.config\winfetch" "$DotFilesDirectory\df\winfetch" > $null
	Add-Symlink "$Env:USERPROFILE\.oh-my-posh" "$DotFilesDirectory\df\oh-my-posh" > $null

	# ----------------------------------------------------
	# Symlink para a config de ssh baseada no ambiente
	# ----------------------------------------------------
	sudo New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.ssh\config.local" -Target "$DotFilesDirectory\df\ssh\config.windows" -Force > $null

	# ----------------------------------------------------
	# Symlink Powershell dotfiles
	# ----------------------------------------------------
	$mydocs =  [Environment]::GetFolderPath("MyDocuments")
	Add-Symlink "${mydocs}\Powershell\profile.ps1" "$DotFilesDirectory\df\powershell\profile.ps1" > $null
	Add-Symlink "${mydocs}\powershell\env-vars.ps1" "$DotFilesDirectory\df\powershell\env-vars.ps1" > $null
	Add-Symlink "${mydocs}\powershell\env-check.ps1" "$DotFilesDirectory\df\powershell\env-check.ps1" > $null
	Add-Symlink "${mydocs}\powershell\plugins.ps1" "$DotFilesDirectory\df\powershell\plugins.ps1" > $null
	Add-Symlink "${mydocs}\powershell\aliases.ps1" "$DotFilesDirectory\df\powershell\aliases.ps1" > $null
	Add-Symlink "${mydocs}\powershell\hotkeys.ps1" "$DotFilesDirectory\df\powershell\hotkeys.ps1" > $null
	Add-Symlink "${mydocs}\powershell\wsl.ps1" "$DotFilesDirectory\df\powershell\wsl.ps1" > $null
	Add-Symlink "${mydocs}\powershell\_functions.ps1" "$DotFilesDirectory\df\powershell\_functions.ps1" > $null
	Add-Symlink "${mydocs}\Powershell\powershell.config.json" "$DotFilesDirectory\df\powershell\powershell.config.json" > $null

#################################################################################
# bootstrap: symlink VsCode settings
#################################################################################

	# ---------------------------------------------------------------
	# remove previous root dotfile dirs symlinks
	# make this check/delete a functionality into add-symlink function
	# ---------------------------------------------------------------
	if (Test-Path -Path "$Env:APPDATA\Code\User") {
		Remove-Item -r "$Env:APPDATA\Code\User"
	}

	Add-Symlink "$Env:APPDATA\Code\User" "$DotFilesDirectory\df\vscode" > $null
	#Add-Symlink "$Env:APPDATA\Code\User\settings.json" "$DotFilesDirectory\df\vscode\settings.json" > $null
	#Add-Symlink "$Env:APPDATA\Code\User\keybindings.json" "$DotFilesDirectory\df\vscode\keybindings.json" > $null
	#Add-Symlink "$Env:APPDATA\Code\User\snippets" "$DotFilesDirectory\df\vscode\snippets" > $null

#################################################################################
# bootstrap: symlink Windows Terminal setting
#################################################################################
		$WindowsTerminalDir = Get-ChildItem "$Env:USERPROFILE\AppData\Local\Packages\*Microsoft.WindowsTerminal*" -Directory -ErrorAction SilentlyContinue | Select-Object -First 1
		if ($WindowsTerminalDir) {
			Add-Symlink "$($WindowsTerminalDir.FullName)\LocalState\settings.json" "$DotFilesDirectory\df\windows-terminal\settings.json" > $null
		}

#################################################################################
# bootstrap: font install
#################################################################################
	if (-not $RefreshDotfiles) {
		Install-FontWindows("$DotFilesDirectory\df\assets\fonts\comic-code-nerdfonts")
	}
	#sudo oh-my-posh font install Hack
	#sudo oh-my-posh font install FiraCode
	#sudo oh-my-posh font install FiraMono


#################################################################################
# bootstrap: software install
#################################################################################
	if (-not $RefreshDotfiles) {
		# TODO: ask to install complete software list
		# Install powers Shell Modules
		. ${PSScriptRoot}\software-list.ps1

		# install powershell modules
		$powershellModules = $softwareList | Where-Object { $_.installer -like "powershell-module" }
		$powershellModules | ForEach-Object { Install-PowershellModule ($_.id) }

		# install winget modules
		$wingetPackages = $softwareList | Where-Object { $_.installer -like "winget" }
		$wingetPackages = $wingetPackages | Where-Object { $_.bootstrap -like "true" }
		$wingetInstalledCache = Get-WinGetInstalledCache
		$wingetPackages | ForEach-Object {
			Install-WinGetApp -Package ($_.id) -PackageName ($_.name) -InstalledIds $wingetInstalledCache.Ids -InstalledNames $wingetInstalledCache.Names -InstalledNameKeys $wingetInstalledCache.NameKeys
		}

		# install scripts
			Install-Script winfetch -AcceptLicense -Force
	}
	else {
		Write-Output "Refresh mode: skipping software/font installation."
	}

#################################################################################
# bootstrap: ensure auth/signing prerequisites for 1Password + GitHub CLI
#################################################################################
	# Even in refresh mode, auth/signing tooling must be present because
	# checkEnv validates runtime compliance immediately at the end.
	$authPrereqPackages = @(
		@{ id = 'AgileBits.1Password'; name = '1Password' },
		@{ id = 'AgileBits.1Password.CLI'; name = '1Password CLI' },
		@{ id = 'GitHub.cli'; name = 'GitHub CLI' }
	)

	$authPrereqCache = Get-WinGetInstalledCache
	foreach ($pkg in $authPrereqPackages) {
		Install-WinGetApp -Package $pkg.id -PackageName $pkg.name -InstalledIds $authPrereqCache.Ids -InstalledNames $authPrereqCache.Names -InstalledNameKeys $authPrereqCache.NameKeys
	}
	$Env:Path = ("{0};{1}" -f [Environment]::GetEnvironmentVariable('Path', 'Machine'), [Environment]::GetEnvironmentVariable('Path', 'User'))

#################################################################################
# bootstrap: runtime secrets + gh auth + final environment health check
#################################################################################
	# Runtime secrets are generated from 1Password refs and stored encrypted in
	# ~/.env.local.sops. No plaintext .env.local is kept on disk.
	$templatePath = Join-Path $DotFilesDirectory 'bootstrap\secrets\.env.local.tpl'
	$envLocalPath = Join-Path $Env:USERPROFILE '.env.local.sops'
	if (!(Set-LocalEnvFrom1Password -TemplatePath $templatePath -OutputPath $envLocalPath)) {
		throw "Failed to initialize encrypted env (.env.local.sops) from 1Password."
	}

	$loadedEnv = Import-DotEnvFromSops -EncryptedPath $envLocalPath
	if ($loadedEnv.Count -eq 0) {
		throw "Failed to decrypt/import runtime env from .env.local.sops."
	}

	# Legacy plaintext env file is removed when present.
	$legacyPlainEnvPath = Join-Path $Env:USERPROFILE '.env.local'
	if (Test-Path -Path $legacyPlainEnvPath -PathType Leaf) {
		Remove-Item -Path $legacyPlainEnvPath -Force -ErrorAction SilentlyContinue
	}

	# Persist only age material for next terminals.
	if (-not [string]::IsNullOrWhiteSpace($Env:SOPS_AGE_KEY)) {
		[Environment]::SetEnvironmentVariable('SOPS_AGE_KEY', $Env:SOPS_AGE_KEY, 'User')
	}
	[Environment]::SetEnvironmentVariable('SOPS_AGE_KEY_FILE', '', 'User')
	# Clear plaintext token persistence from previous bootstrap versions.
	[Environment]::SetEnvironmentVariable('OP_SERVICE_ACCOUNT_TOKEN', '', 'User')
	[Environment]::SetEnvironmentVariable('GITHUB_TOKEN', '', 'User')
	[Environment]::SetEnvironmentVariable('GH_TOKEN', '', 'User')

	if ([string]::IsNullOrWhiteSpace($Env:GH_TOKEN) -and -not [string]::IsNullOrWhiteSpace($Env:GITHUB_TOKEN)) {
		$Env:GH_TOKEN = $Env:GITHUB_TOKEN
	}

	if (!(Ensure-GitHubCliAuthFrom1Password)) {
		throw "Failed to authenticate gh using token from 1Password."
	}

	Write-Output "Running final environment health check (checkEnv)..."
	if (!(checkEnv)) {
		throw "checkEnv found failures. Review the output and fix before continuing."
	}

#################################################################################
# bootstrap: set personal windows configs
#################################################################################
	if (-not $RefreshDotfiles) {
		# set my preferences
		Set-MyPrefsWinDateTime
		Set-MyPrefsWinKeyboard
		Set-MyPrefsWinRegionalization
		Set-MyPrefsWinExplorer
	}
	else {
		Write-Output "Refresh mode: skipping system preference changes."
	}

#################################################################################
# bootstrap: done! reload profile
#################################################################################
	# Write-Warning "If you see Powershell Profile errors you'll want to run ./powershell/setup/install_pwsh_modules.ps1 as well"
	# Write-Output "If this is a really fresh install run install_softwares.ps1 to get going"
	Write-Output "Done, your profile will be reloaded"
	Write-Output "`n"

	# Reloads the Profile
	. $PROFILE.CurrentUserAllHosts
