#Requires -RunAsAdministrator
#requires -PSEdition Core
#requires -Version 7

# Helper functions
. ${PSScriptRoot}\..\.config\powershell\.inc\_functions.ps1

if ($Env:Onedrive) {
	# User-agnostic project target:
	# - optional override: DOTFILES_ONEDRIVE_PROJECTS_PATH
	# - default: <OneDrive>\clients\<USERNAME>\projects
	$OneDriveProjectsPath = if (-not [string]::IsNullOrWhiteSpace($Env:DOTFILES_ONEDRIVE_PROJECTS_PATH)) {
		$Env:DOTFILES_ONEDRIVE_PROJECTS_PATH
	}
	else {
		Join-Path $Env:Onedrive ("clients\{0}\projects" -f $Env:USERNAME)
	}
	$OneDriveDotfilesPath = Join-Path $OneDriveProjectsPath "dotfiles"

	###########################################################
	# Symlink default windows profile folders
	# todo: check if each folder exists under onedrive dir (if is already cloud synced)
	###########################################################
	Remove-ItemIfExists "~\Documents"	| Add-Symlink "~\Documents" "$Env:Onedrive\documents" > $null
	Remove-ItemIfExists "~\Clients" 	| Add-Symlink "~\Clients" "$Env:Onedrive\clients" > $null
	Remove-ItemIfExists "~\Desktop"		| Add-Symlink "~\Desktop" "$Env:Onedrive\desktop" > $null
	Remove-ItemIfExists "~\Downloads"	| Add-Symlink "~\Downloads" "$Env:Onedrive\downloads" > $null
	Remove-ItemIfExists "~\Pictures"	| Add-Symlink "~\Pictures" "$Env:Onedrive\images" > $null
	Remove-ItemIfExists "~\Videos"		| Add-Symlink "~\Videos" "$Env:Onedrive\videos" > $null
	Remove-ItemIfExists "~\Projects"	| Add-Symlink "~\Projects" "$OneDriveProjectsPath" > $null


	###########################################################
	# Symlink .ssh profile folder and configs
	###########################################################
	Add-Symlink "~\.ssh" "$Env:Onedrive\.ssh" > $null


	###########################################################
	# Symlink dotfile
	###########################################################
	#dotfile folder
	Add-Symlink "~\dotfiles" "$OneDriveDotfilesPath" > $null

	#dotfile items
	Add-Symlink "~\.assets" "$Env:USERPROFILE\dotfiles\.assets" > $null
	Add-Symlink "~\.editorconfig" "$Env:USERPROFILE\dotfiles\.editorconfig" > $null
	Add-Symlink "~\.gitconfig" "$Env:USERPROFILE\dotfiles\.gitconfig" > $null
	Add-Symlink "~\.gitconfig.local" "$Env:USERPROFILE\dotfiles\.gitconfig.local" > $null
	Add-Symlink "~\.gitignore" "$Env:USERPROFILE\dotfiles\.gitignore" > $null
	Add-Symlink "~\.bashrc" "$Env:USERPROFILE\dotfiles\.bashrc" > $null
	Add-Symlink "~\.bash_profile" "$Env:USERPROFILE\dotfiles\.bash_profile" > $null
	Add-Symlink "~\.bashrc_profile" "$Env:USERPROFILE\dotfiles\.bashrc_profile" > $null
	Add-Symlink "~\.config\winfetch" "$Env:USERPROFILE\dotfiles\.config\winfetch" > $null


	###########################################################
	# Symlink useful folder shortcuts
	###########################################################
	#user profile shortcuts
	Add-Symlink "~\Bin" "$Env:Onedrive\bin" > $null
	Add-Symlink "~\Etc" "$Env:Onedrive\etc" > $null

	#d:\ shortcuts
	Add-Symlink "d:\bin" "$Env:Onedrive\bin" > $null
	Add-Symlink "d:\etc" "$Env:Onedrive\etc" > $null
	Add-Symlink "d:\clients" "$Env:Onedrive\clients" > $null
	Add-Symlink "d:\projects" "$OneDriveProjectsPath" > $null


	###########################################################
	# Symlink app configs
	###########################################################
	#windows terminal
	$WindowsTerminalDir = (Get-AppxPackage -Name "*WindowsTerminal*").InstallLocation
	Add-Symlink "${WindowsTerminalDir}\LocalState\settings.json" "$Env:USERPROFILE\dotfiles\.config\windows-terminal\settings.json" > $null

	#powershell
	Remove-ItemIfExists "~\Documents\powershell" | Add-Symlink "$Env:USERPROFILE\Documents\powershell" "$Env:USERPROFILE\dotfiles\.config\powershell" > $null


	###########################################################
	# Script Done
	###########################################################
	Write-Output "Done, your profile will be reloaded"
	& $PROFILE #| Clear-Host

}
else {
	Write-Warning "ENV:OneDrive not found. You must install M$ OneDrive. Aborting"
	return
}
