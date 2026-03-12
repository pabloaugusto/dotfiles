#requires -RunAsAdministrator
#requires -PSEdition Core
#requires -Version 7
#requires -Modules PowerShellGet

param (
	[switch]$Refresh,
	[switch]$Relink
)

#######################################################################################
# Entry-point bootstrap for Windows host
#
# Responsibilities:
# 1) Validate prerequisites available in current host (winget/onedrive/config state).
# 2) Ask target operation mode (new install vs refresh).
# 3) Dispatch to app/bootstrap/bootstrap-windows.ps1 and post actions.
#
# Important:
# - Option 1 (new install) applies software + preferences + auth checks.
# - Option 2 (refresh) keeps software/system changes minimal, focusing on links/config.
# - -Relink recreates only the canonical bootstrap symlinks/junctions.
#######################################################################################
if ($Refresh -and $Relink) {
	throw "Use either -Refresh or -Relink, not both."
}

Set-ExecutionPolicy -ExecutionPolicy Bypass -Force #-Scope CurrentUser #  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned
Set-PSRepository -Name PSGallery -InstallationPolicy Trusted

#######################################################################################
# Ensure winget is available (install App Installer when needed)
#######################################################################################
function Ensure-WinGet {
	if (Get-Command -Name winget -ErrorAction SilentlyContinue) {
		return $true
	}

	Write-Warning "Winget not found. Trying to install App Installer (winget)..."

	$bundlePath = Join-Path $env:TEMP "winget.msixbundle"
	$downloadUri = "https://aka.ms/getwinget"

	try {
		$ProgressPreference = 'SilentlyContinue'
		Invoke-WebRequest -Uri $downloadUri -OutFile $bundlePath -UseBasicParsing -ErrorAction Stop

		$addAppx = Get-Command -Name Add-AppxPackage -ErrorAction SilentlyContinue
		if (-not $addAppx) {
			throw "Add-AppxPackage command is not available in this session."
		}

		Add-AppxPackage -Path $bundlePath -ErrorAction Stop
	}
	catch {
		Write-Warning "Automatic winget install failed: $($_.Exception.Message)"
		Write-Warning "Opening Microsoft Store App Installer page. Install it and run this script again."
		Start-Process "ms-windows-store://pdp/?ProductId=9NBLGGH4NNS1" -ErrorAction SilentlyContinue
		return $false
	}
	finally {
		Remove-Item -Path $bundlePath -Force -ErrorAction SilentlyContinue
	}

	# Refresh PATH from registry to make newly installed command discoverable.
	$machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
	$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
	$env:Path = "$machinePath;$userPath"
	Start-Sleep -Seconds 2

	if (!(Get-Command -Name winget -ErrorAction SilentlyContinue)) {
		Write-Warning "Winget install completed but command is still unavailable in current session."
		Write-Warning "Close and reopen terminal, then run this script again."
		return $false
	}

	Write-Output "Winget installed successfully."
	return $true
}

#--------------------------------------------------------------------------------------
# Check winget installed and adjust winget Installer policies
#--------------------------------------------------------------------------------------
if (!(Ensure-WinGet)) {
	return
}
winget settings --enable InstallerHashOverride >$null

# TODO: check winget version and update it if necessary
#  (> winget install -s msstore --id 9NBLGGH4NNS1) https://github.com/microsoft/winget-cli/issues/4187


#--------------------------------------------------------------------------------------
# Resolve OneDrive root path for current execution.
# Priority:
# 1) DOTFILES_ONEDRIVE_ROOT_WINDOWS (explicit override)
# 2) OneDrive environment variable
# 3) %USERPROFILE%\OneDrive (common default)
#--------------------------------------------------------------------------------------
function Resolve-OneDriveRootPath {
	$candidates = New-Object System.Collections.Generic.List[string]
	if (-not [string]::IsNullOrWhiteSpace($Env:DOTFILES_ONEDRIVE_ROOT_WINDOWS)) {
		$candidates.Add($Env:DOTFILES_ONEDRIVE_ROOT_WINDOWS)
	}
	if (-not [string]::IsNullOrWhiteSpace($Env:OneDrive)) {
		$candidates.Add($Env:OneDrive)
	}
	if (-not [string]::IsNullOrWhiteSpace($Env:USERPROFILE)) {
		$candidates.Add((Join-Path $Env:USERPROFILE 'OneDrive'))
	}

	foreach ($candidate in ($candidates | Select-Object -Unique)) {
		if (Test-Path -Path $candidate -PathType Container) {
			return $candidate
		}
	}
	return $null
}

function ConvertTo-BoolFlag {
	param (
		[string]$Value,
		[bool]$Default = $false
	)
	if ([string]::IsNullOrWhiteSpace($Value)) { return $Default }
	switch -Regex ($Value.Trim().ToLowerInvariant()) {
		'^(1|true|yes|y|sim|s)$' { return $true }
		'^(0|false|no|n|nao|não)$' { return $false }
		default { return $Default }
	}
}

##########################################################
# Dotfiles root and central bootstrap config
##########################################################
$DotFilesDirectory = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
if (!(Test-Path -Path "$DotFilesDirectory\app\df\powershell\_functions.ps1")) {
	Write-Host "functions.ps1 don't found at $DotFilesDirectory\app\df\powershell\_functions.ps1"
	Write-Host "forgot clone dotfiles from github? ABORTING ..."
	return
}

$bootstrapConfigScript = Join-Path $DotFilesDirectory 'app\bootstrap\bootstrap-config.ps1'
if (!(Test-Path -Path $bootstrapConfigScript -PathType Leaf)) {
	Write-Host "bootstrap-config.ps1 not found at $bootstrapConfigScript"
	return
}
. $bootstrapConfigScript

if (!(Ensure-BootstrapConfigReady -DotFilesDirectory $DotFilesDirectory)) {
	return
}

# OneDrive requirement is config-driven:
# - enabled=true  -> bootstrap-windows.ps1 executes guided/root migration flow.
# - enabled=false -> skip OneDrive pre-checks in entrypoint.
$oneDriveEnabled = ConvertTo-BoolFlag -Value $Env:DOTFILES_ONEDRIVE_ENABLED -Default $true
if ($oneDriveEnabled) {
	$resolvedOneDriveRoot = Resolve-OneDriveRootPath
	if ($resolvedOneDriveRoot) {
		$Env:DOTFILES_ONEDRIVE_ROOT_WINDOWS = $resolvedOneDriveRoot
	}
	else {
		Write-Warning "OneDrive root not resolved at entrypoint."
		Write-Warning "Bootstrap Windows will run a guided OneDrive setup/migration step before creating links."
		Write-Warning "Checked sources: DOTFILES_ONEDRIVE_ROOT_WINDOWS, OneDrive env, and %USERPROFILE%\\OneDrive."
	}
}

##########################################################
# Check / install pre requisites
##########################################################

if (![bool](Get-Command -Name 'pwsh' -ErrorAction SilentlyContinue)) {
	Write-Output 'installing pre-req: PowerShell 7'
	winget install Microsoft.PowerShell
}

if (![bool](Get-Command -Name 'git' -ErrorAction SilentlyContinue)) {
	Write-Output 'installing pre-req: git'
	winget install Git.Git
}


##########################################################
# adjust explorer folders
##########################################################
#assegure have d:\
#create d:\onedrive (if not exists)
#go to onedrive settings
#unlink ondrive from pc
#link again
#put your email
#change ondrive base dir
#log again


#Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" -name "Personal" -value "D:\OneDrive\documents"
#Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" -name "My Pictures"  -value "D:\OneDrive\images"


##########################################################
# Install WSL
##########################################################
# TODO: Improve verification of installation and checks. Also try fill (linux) user and pass without asked
if (!(Get-Command -Name wsl -ErrorAction SilentlyContinue)) {
&wsl --install ubuntu
 wsl --shutdown
 ubuntu config --default-user $Env:USERNAME # set default wsl ubuntu user to windows terminal/powershell
&wsl --update
}







##########################################################
# Bootstrap Function
##########################################################
# inicial questions to install
function Invoke-WindowsBootstrapFull {
	Write-Host -NoNewline "`nConfiguring Windows: "

	. "${DotFilesDirectory}\app\df\powershell\_functions.ps1"

	. "${DotFilesDirectory}\app\bootstrap\bootstrap-windows.ps1"

	Set-ComputerName('RYZEN')			#from _functions.ps1
	Set-MyPrefsWinRegionalization 		#from _functions.ps1
	Set-MyPrefsWinExplorer				#from _functions.ps1
	# Set-MyPrefsWinFileAssociations	#from _functions.ps1

	Write-Host "[DONE] `b" -ForegroundColor green
	Write-Output "`n`nConfigure Dotfiles: DONE!"
	Start-CountDown -Message "Restarting Windows Explorer in" -Seconds 5
	Get-Process explorer | Stop-Process #restart explorer
}

function Invoke-WindowsBootstrapRefresh {
	Write-Host -NoNewline "`nRefreshing Dotfiles: "

	. "${DotFilesDirectory}\app\df\powershell\_functions.ps1"

	. "${DotFilesDirectory}\app\bootstrap\bootstrap-windows.ps1" -RefreshDotfiles

	Write-Host "[DONE] `b" -ForegroundColor green
	Write-Output "`n`nRefresh Dotfiles: DONE!"
}

function Invoke-WindowsBootstrapRelink {
	Write-Host -NoNewline "`nRecreating bootstrap symlinks: "

	. "${DotFilesDirectory}\app\df\powershell\_functions.ps1"

	. "${DotFilesDirectory}\app\bootstrap\bootstrap-windows.ps1" -RelinkOnly

	Write-Host "[DONE] `b" -ForegroundColor green
	Write-Output "`n`nRecreate Bootstrap Symlinks: DONE!"
}

function bootstrap {
	if ($Relink) {
		Invoke-WindowsBootstrapRelink
		return
	}
	if ($Refresh) {
		Invoke-WindowsBootstrapRefresh
		return
	}


	$prompt = @("`n"
		"This script will override some of your home files, many system `n"
		"configs, user preferences and style settings (look and feel). `n"
		"If you are okay with that, choice a SO to boostrap dotfiles: `n `n"
		"0 - ABORT (Cancel Bootstrap) `n"
		"1 - Windows - new install `n"
		"2 - Windows - refresh dotfiles `n"
		"5 - Windows - recreate bootstrap symlinks `n"
		"3 - Linux `n"
		"4 - Mac `n`n"
	) -join ''



	# Prompt decision drives which operation mode is forwarded to bootstrap-windows.ps1.
	Switch (Read-Host -Prompt $prompt) {
		"0" {
			Write-Host "`nABORTING! At least you have 🐔 `n"
		}
		"1" {
			Invoke-WindowsBootstrapFull
		}
		"2" {
			Invoke-WindowsBootstrapRefresh
		}
		"5" {
			Invoke-WindowsBootstrapRelink
		}

		default {
			Write-Output "`nOnly WIN supportted at this momment. `n Other SOs comming Soon.."
		}
	}
}

##########################################################
# FINALLY: Run Bootstrap!!!
##########################################################
&bootstrap
