#Includes and settings
if ($IsWindows) { Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass }
. $PSScriptRoot\.inc\3rd\SFTA.ps1

######################################################################################
# File map (high-level)
#
# Core helpers:
# - Add-Symlink, Test-CommandExists, Test-PowershellElevated
# - Install-* functions for winget/choco/pip/modules
#
# Runtime auth/signing (added for bootstrap conformity):
# - Import-DotEnvFile
# - Ensure-OpServiceAccountToken
# - Set-LocalEnvFrom1Password
# - Ensure-SopsAgeKeyFile
# - Ensure-GitHubCliAuthFrom1Password
# - checkEnv
#
# Note:
# This file is intentionally central for dotfiles automation routines.
######################################################################################


######################################################################################
# Remove a Item (file or folder) if exists (forced, recursive, without confirm)
######################################################################################
function Remove-ItemIfExists {
	param ( [Parameter(Mandatory)] [string]$Path )

	if ((Test-Path -Path $Path)) { Remove-Item $Path -Recurse -Force -Confirm:$false }
}

######################################################################################
# Update all apps (similar to apt update & apt upgrade)
######################################################################################
function updateAll {

	$isAdmin = ([Security.Principal.WindowsIdentity]::GetCurrent().Groups -contains 'S-1-5-32-544')

	if ($isAdmin) {
		winget settings --enable InstallerHashOverride
		winget update --all --silent --force --ignore-security-hash --accept-source-agreements --accept-package-agreements --disable-interactivity --unknown
		choco upgrade all -y
		scoop update *
		Update-Module #powershell modules
	}
	else {
		Write-Output "You must run this command with ADMIN privilegies"<# Action when all if and elseif conditions are false #>
	}
}

######################################################################################
# Create a symbolic link
######################################################################################
function Add-Symlink {

	[CmdletBinding()]
	param (
		[Parameter(Mandatory)]
		[string]$from,
		[Parameter(Mandatory)]
		[string]$to
	)

	$fromPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($from)
	$toPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($to)

	# Ensure parent folder exists before creating the link.
	$parentPath = Split-Path -Path $fromPath -Parent
	if ($parentPath -and !(Test-Path -Path $parentPath)) {
		New-Item -ItemType Directory -Path $parentPath -Force | Out-Null
	}

	if (Test-Path -Path $fromPath) {
		$currentItem = Get-Item -Path $fromPath -Force -ErrorAction SilentlyContinue
		$isSymbolicLink = $null -ne $currentItem -and $currentItem.LinkType -eq 'SymbolicLink'
		$currentTarget = if ($isSymbolicLink -and $null -ne $currentItem.Target) { [string]$currentItem.Target } else { '' }
		$resolvedCurrentTarget = if ($currentTarget) { $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($currentTarget) } else { '' }

		# No-op when the desired link already exists.
		if ($isSymbolicLink -and $resolvedCurrentTarget -eq $toPath) {
			return
		}

		Remove-Item -Path $fromPath -Recurse -Force -Confirm:$false -ErrorAction SilentlyContinue
	}

	New-Item -ItemType SymbolicLink -Path $fromPath -Target $toPath -Force -WarningAction SilentlyContinue -InformationAction Ignore -ErrorAction SilentlyContinue | Out-Null
}

######################################################################################
# Test if command exists
######################################################################################
function Test-CommandExists($cmd) {
	return [bool](Get-Command -Name $cmd -ErrorAction SilentlyContinue)
}


######################################################################################
# Test if powershell is running with admin privileges
######################################################################################
function Test-PowershellElevated {
	$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
	return $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}


######################################################################################
# Normalize text for resilient cache matching (spaces/symbols/case-insensitive)
######################################################################################
function ConvertTo-CacheKey {
	param (
		[string]$Value
	)

	if ([string]::IsNullOrWhiteSpace($Value)) { return '' }
	return (($Value.ToLowerInvariant()) -replace '[^a-z0-9]', '')
}


######################################################################################
# Build a cache of installed WinGet packages to avoid repeated lookups per package
######################################################################################
function Get-WinGetInstalledCache {

	[CmdletBinding()]
	param ()

	$ids = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::OrdinalIgnoreCase)
	$names = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::OrdinalIgnoreCase)
	$nameKeys = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::OrdinalIgnoreCase)

	$listOutput = winget list --disable-interactivity 2>$null

	foreach ($line in $listOutput) {
		$trimmed = [string]$line
		if ([string]::IsNullOrWhiteSpace($trimmed)) { continue }

		$trimmed = $trimmed.Trim()

		# Ignore spinners, table headers and separators.
		if ($trimmed -match '^[\-\|/\\]+$') { continue }
		if ($trimmed -like 'Name*Id*Version*Source*') { continue }
		if ($trimmed -match '^-+$') { continue }

		$matched = $false
		if ($trimmed -match '^(?<name>.+?)\s{2,}(?<id>[A-Za-z0-9][A-Za-z0-9\.\-]+)\s{2,}(?<version>\S+)\s{2,}(?<source>\S+)\s*$') {
			$matched = $true
		}
		elseif ($trimmed -match '^(?<name>.+?)\s+(?<id>[A-Za-z0-9][A-Za-z0-9\.\-]+)\s+(?<version>\S+)\s+(?<source>\S+)\s*$') {
			$matched = $true
		}

		if (-not $matched) { continue }

		if ($Matches.id) { [void]$ids.Add($Matches.id.Trim()) }
		if ($Matches.name) {
			$name = $Matches.name.Trim()
			[void]$names.Add($name)
			[void]$nameKeys.Add((ConvertTo-CacheKey $name))
		}
	}

	return [PSCustomObject]@{
		Ids      = $ids
		Names    = $names
		NameKeys = $nameKeys
	}
}


######################################################################################
# Install Winget App (Package)
# TODO: change package id at output to package name
######################################################################################
function Install-WinGetApp {
	param (
		[string]$Package,
		[string]$PackageName,
		[System.Collections.Generic.HashSet[string]]$InstalledIds,
		[System.Collections.Generic.HashSet[string]]$InstalledNames,
		[System.Collections.Generic.HashSet[string]]$InstalledNameKeys
	)

	Write-Host -NoNewline "Installing WinGet Package: $Package "

	$alreadyInstalled = $false
	$usingCache = ($null -ne $InstalledIds) -or ($null -ne $InstalledNames)

	if ($InstalledIds -and $InstalledIds.Contains($Package)) {
		$alreadyInstalled = $true
	}

	if (-not $alreadyInstalled -and $PackageName -and $InstalledNames -and $InstalledNames.Contains($PackageName)) {
		$alreadyInstalled = $true
	}

	if (-not $alreadyInstalled -and $PackageName -and $InstalledNameKeys) {
		$packageNameKey = ConvertTo-CacheKey $PackageName
		if ($packageNameKey -and $InstalledNameKeys.Contains($packageNameKey)) {
			$alreadyInstalled = $true
		}
	}

	# Fallback when cache could not be built/parsing failed.
	if (-not $alreadyInstalled -and $usingCache -and $InstalledIds -and $InstalledNames -and $InstalledIds.Count -eq 0 -and $InstalledNames.Count -eq 0) {
		$alreadyInstalled = -not ((winget list --id $Package --disable-interactivity) -like "*No installed package found*")
	}
	elseif (-not $alreadyInstalled -and -not $usingCache) {
		$alreadyInstalled = -not ((winget list --id $Package --disable-interactivity) -like "*No installed package found*")
	}

	#if not installed yet
	if (-not $alreadyInstalled) {

		$resp = winget install --id $Package --accept-source-agreements --accept-package-agreements --disable-interactivity --no-upgrade --silent --accept-source-agreements --ignore-security-hash
		if ($resp -like "*Successfully installed*") {
			if ($InstalledIds) { [void]$InstalledIds.Add($Package) }
			if ($PackageName -and $InstalledNames) {
				[void]$InstalledNames.Add($PackageName)
				if ($InstalledNameKeys) { [void]$InstalledNameKeys.Add((ConvertTo-CacheKey $PackageName)) }
			}
			Write-Host "[SUCCESS]" -ForegroundColor green
		}
		else { Write-Host "[FAIL]" -ForegroundColor red }
	}
	else { Write-Host "[SKIPPED - ALREADY INSTALLED]" -ForegroundColor yellow }
}

######################################################################################
# Install PIP App (Package)
######################################################################################
function Install-PipPackage {
	param (
		[string]$Package
	)

	Write-Host -NoNewline "Installing PIP Package: $Package "
	#if not installed yet
	if (-not ((pip list --disable-pip-version-check) -like "*$Package*" )) {

		$resp = python3 -m pip install --user $Package
		if ($resp -like "*Successfully installed*") {
			Write-Host "[SUCCESS]" -ForegroundColor green
		}
		else { Write-Host "[FAIL]" -ForegroundColor red }
	}
	else { Write-Host "[SKIPPED - ALREADY INSTALLED]" -ForegroundColor yellow }
}


######################################################################################
# Install Chocolatey App (Package)
# todo: change package id at output to package name
######################################################################################
function Install-ChocoApp {
	param (
		[string]$Package
	)

	#---------------------------------------
	# check choco installed and install it
	#---------------------------------------
	if (!(Get-Command -Name choco -ErrorAction SilentlyContinue)) {
		winget install --id chocolatey.chocolatey --source winget --accept-package-agreements --accept-source-agreements --disable-interactivity --silent --uninstall-previous
	}

	#---------------------------------------
	# Install package
	#---------------------------------------
	Write-Host -NoNewline "Installing Choco Package: $Package "

	# if not installed yet
	if ((choco list $Package) -like "*0 packages installed*") {
		$resp = choco install $Package -y --ignore-checksums --acceptlicense --force --limit-output
		if ($resp -like "*was successful*") {
			Write-Host "[SUCCESS]" -ForegroundColor green
		}
		else { Write-Host "[FAIL]" -ForegroundColor red }
	}
	else { Write-Host "[SKIPPED - ALREADY INSTALLED]" -ForegroundColor yellow }
}
# function Install-ChocoPackage {

# 	[cmdletbinding()]
# 	param(
# 		[String]$PackageName
# 	)

# 	$ChocoLibPath = "C:\ProgramData\chocolatey\lib"

# 	if (-not(test-path $ChocoLibPath)) {
# 		Set-ExecutionPolicy Bypass -Scope Process -Force;
# 		[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072;
# 		Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
# 	}

# 	#Test if the package folder exists on Choco Lib folder
# 	if (!((test-path "$ChocoLibPath\$PackageName"))) {

# 		Write-Host "[INFO]Installing $PackageName..." -ForegroundColor Yellow
# 		$start_time = Get-Date
# 		#Install the package without confirmation prompt
# 		choco install -y -v $PackageName
# 		Write-Host "Time taken: $((Get-Date).Subtract($start_time).Seconds) second(s)"

# 	}
# 	else {

# 		Write-host  "[INFO]$PackageName is already installed." -ForegroundColor Green
# 	}
# }

# #Loop through each package to install them
# foreach ($Package in $Packages) {
# 	Install-ChocoPackage -PackageName $Package
# }


######################################################################################
# Install Scoop App (Package)
# todo: falta ajustar o install do scoop (useless)
######################################################################################
function Install-ScoopApp {
	param (
		[string]$Package
	)

	#---------------------------------------
	# check scoop installed and install it
	#---------------------------------------
	if (!(Get-Command -Name scoop -ErrorAction SilentlyContinue)) {
		Invoke-RestMethod get.scoop.sh | Invoke-Expression #dont install as admin
		ProgressPreference = 'SilentlyContinue'
		Invoke-Expression "& {$(Invoke-RestMethod get.scoop.sh)} -RunAsAdmin" #force install as admin
	}

	#---------------------------------------
	# Install package
	#---------------------------------------
	Write-Verbose -Message "Preparing to install $Package"
	if (! (scoop info $Package).Installed ) {
		Write-Verbose -Message "Installing $Package"
		scoop install $Package
	}
	else {
		Write-Verbose -Message "Package $Package already installed! Skipping..."
	}
}


######################################################################################
# Install Powershell Module
# todo: change package id at output to package name
######################################################################################
function Install-PowershellModule {
	param (
		[string]$Module
	)

	# check powershell core installed and run it
	# if (!(Test-CommandExists pwsh)) {
	# 	winget install Powershell --source msstore --accept-package-agreements --accept-source-agreements --disable-interactivity --silent
	# 	#run powershell
	# 	pwsh
	# 	#if $PROFILE not exists, create it
	# 	if (!(Test-Path $PROFILE)) { New-Item -Path $PROFILE -ItemType File -Force }
	# }

	Write-Host -NoNewline "Installing Powershell Module: $Module "

	# if not installed yet
	if (!(Get-InstalledModule -Name $Module -ErrorAction Ignore -WarningAction Ignore)) {
		try {
			#try install
			Install-Module -Name $Module -AcceptLicense -AllowPrerelease -ErrorAction Stop -WarningAction SilentlyContinue

		}
		catch {
			Write-Host "[FAIL]" -ForegroundColor red
			$err = $true
		}
		finally {
			$err ? $null : (Write-Host "[SUCCESS]" -ForegroundColor green)
		}
	}
	else { Write-Host "[SKIPPED - ALREADY INSTALLED]" -ForegroundColor yellow }
}

######################################################################################
# Install UV Module (PIP alternative with more performance)
# todo: write uv package module installer
######################################################################################
function Install-UvPackage {
	param (
		[string]$Module
	)
}
######################################################################################
# Unzip a compressed file
######################################################################################
function Expand-Download {
	param (
		[string]$Folder,
		[string]$File
	)
	if (!(Test-Path -Path "$Folder" -PathType Container)) {
		Write-Error "$Folder does not exist!!!"
		Break
	}
	if (Test-Path -Path "$File" -PathType Leaf) {
		switch ($File.Split(".") | Select-Object -Last 1) {
			"rar" { Start-Process -FilePath "UnRar.exe" -ArgumentList "x", "-op'$Folder'", "-y", "$File" -WorkingDirectory "$Env:ProgramFiles\WinRAR\" -Wait | Out-Null }
			"zip" { 7z x -o"$Folder" -y "$File" | Out-Null }
			"7z" { 7z x -o"$Folder" -y "$File" | Out-Null }
			"exe" { 7z x -o"$Folder" -y "$File" | Out-Null }
			Default { Write-Error "No way to Extract $File !!!"; Break }
		}
	}
}


######################################################################################
# Download
######################################################################################
function Get-Download {
	param (
		[string]$Link,
		[string]$Folder
	)
	if ($null -ne (curl -sIL "$Link" | Select-String -Pattern "Content-Disposition")) {
		$Package = $(curl -sIL "$Link" | Select-String -Pattern "filename=" | Split-String -Separator "=" | Select-Object -Last 1).Trim('"')
	}
	else {
		$Package = $Link.split("/") | Select-Object -Last 1
	}
	Write-Verbose -Message "Preparing to download $Package"
	aria2c --quiet --dir="$Folder" "$Link"
	Return $Package
}

######################################################################################
# Install a custom app
######################################################################################
function Install-CustomApp {
	param (
		[string]$URL,
		[string]$Folder
	)
	$Package = Get-Download -Link $URL -Folder "$Env:UserProfile\Downloads\"
	if (Test-Path -Path "$Env:UserProfile\Downloads\$Package" -PathType Leaf) {
		if (Test-Path Variable:Folder) {
			if (!(Test-Path -Path "$Env:UserProfile\bin\$Folder")) {
				New-Item -Path "$Env:UserProfile\bin\$Folder" -ItemType Directory | Out-Null
			}
			Expand-Download -Folder "$Env:UserProfile\bin\$Folder" -File "$Env:UserProfile\Downloads\$Package"
		}
		else {
			Expand-Download -Folder "$Env:UserProfile\bin\" -File "$Env:UserProfile\Downloads\$Package"
		}
		Remove-Item -Path "$Env:UserProfile\Downloads\$Package"
	}
}

######################################################################################
# Install a custom package from web
######################################################################################
function Install-CustomPackage {
	param (
		[string]$URL
	)
	$Package = Get-Download -Link $URL -Folder "$Env:UserProfile\Downloads\"
	if (Test-Path -Path "$Env:UserProfile\Downloads\$Package" -PathType Leaf) {
		Start-Process -FilePath ".\$Package" -ArgumentList "/S" -WorkingDirectory "$Env:USERPROFILE\Downloads\" -Verb RunAs -Wait #-WindowStyle Hidden
		Remove-Item -Path "$Env:UserProfile\Downloads\$Package"
	}
}

######################################################################################
# Remove and App
######################################################################################
function Remove-InstalledApp {
	param (
		[string]$Package
	)
	Write-Verbose -Message "Uninstalling: $Package"
	Start-Process -FilePath "PowerShell" -ArgumentList "Get-AppxPackage", "-AllUsers", "-Name", "'$Package'" -Verb RunAs -WindowStyle Hidden
}

######################################################################################
# Enable a Scoop Bucket
######################################################################################
function Enable-ScoopBucket {
	param (
		[string]$Bucket
	)
	if (!($(scoop bucket list).Name -eq "$Bucket")) {
		Write-Verbose -Message "Adding Bucket $Bucket to scoop..."
		scoop bucket add $Bucket
	}
	else {
		Write-Verbose -Message "Bucket $Bucket already added! Skipping..."
	}
}

######################################################################################
# Show/Hide tray icons based on appFileName. Tested on Win11 & PS7
# @author @pabloaugusto github.com/pabloaugusto
#
# usage:
#   Show-TrayIcon skype
#   Show-TrayIcon SkyPE.ExE -hide
######################################################################################
function Show-TrayIcon {
	param (
		[string]$appFileName,
		[switch]$hide
	)

	# win11 tray icons reg path
	$regLocation = "HKCU:\Control Panel\NotifyIconSettings\"

	if (Test-Path $regLocation) {
		$TrayIcons = Get-ChildItem $regLocation

		# $TrayIcons
		foreach ($t in $TrayIcons) {
			$path = Get-ItemProperty "registry::$($t)" -Name ExecutablePath | Select-Object -ExpandProperty ExecutablePath
			if ($path.ToLower() -like "*$appFileName*".ToLower()) {
				if ($hide.IsPresent) {
					Remove-ItemProperty "registry::$($t)" -Name "IsPromoted" -ErrorAction SilentlyContinue
				}
				else {
					Set-ItemProperty "registry::$($t)" -Name "IsPromoted" -Value 1
				}
			}
		}

	}
}




######################################################################################
# SetFolderPermissions
######################################################################################
Function SetFolderPermissions {
	<#
    .SYNOPSIS
    Function SetFolderPermissions is an advanced function which can set NTFSpermissions on a specified folder.
    https://jonlabelle.com/snippets/view/powershell/set-folder-permissions

    .DESCRIPTION
    Function SetFolderPermissions is an advanced function which can set NTFSpermissions on a specified folder.

    .PARAMETER FolderPath
    Indicates the path to the folder whose permissions are being modified.
    This path must exist.

    .PARAMETER Grantee
    Indicates the user or group to which permissions are being granted.
    This user or group must exist.

    .PARAMETER Perms
    Indicates the ACL permissions that will be assigned to the user or group specified in $Grantee (comma-delimited).
    Possible ACL permissions are:
    *AppendData
    *ChangePermissions
    *CreateDirectories
    *CreateFiles
    *Delete
    *DeleteSubdirectoriesAndFiles
    *ExecuteFile
    *FullControl
    *ListDirectory
    *Modify
    *Read
    *ReadAndExecute
    *ReadAttributes
    *ReadData
    *ReadExtendedAttributes
    *ReadPermissions
    *Synchronize
    *TakeOwnership
    *Traverse
    *Write
    *WriteAttributes
    *WriteData
    *WriteExtendedAttributes

    .EXAMPLE
    SetFolderPermissions "E:\logs\Applogs" "IIS_IUSRS" "FullControl"
    SetFolderPermissions "E:\logs\LogFiles" "IIS_IUSRS" "FullControl"
    SetFolderPermissions "E:\logs\FailedReqLogFiles" "IIS_IUSRS" "FullControl"
    SetFolderPermissions "E:\Applications" "IIS_IUSRS" "ReadAndExecute"
#>
	[CmdletBinding()]
	Param
	(
		[Parameter(Mandatory = $true, Position = 1)]
		[String] $FolderPath,

		[Parameter(Mandatory = $true, Position = 2)]
		[String]$Grantee,

		[Parameter(Mandatory = $true, Position = 3)]
		[String]$Perms
	)

	# Verify that the specified path exists. Exit script if it does not.
	if (!(Test-Path "$FolderPath")) {
		Write-Host -ForegroundColor red "Error setting folder permissions. Path, $FolderPath, does not exist."
		break
	}

	$Acl = Get-Acl $FolderPath

	ForEach ($perm in $Perms.split("{,}")) {
		if ($perm -ne "FullControl") {
			$perm = "$perm, Synchronize"
		}

		$AclRule = New-Object System.Security.AccessControl.FileSystemAccessRule($Grantee, $Perm, "ContainerInherit, ObjectInherit", "None", "Allow")
		$Acl.SetAccessRule($AclRule)
	}

	# Commit the new permissions
	Set-Acl $FolderPath $Acl
}


######################################################################################
# Rename all subfolder at current dir to lowercase
######################################################################################
function RenameAllFoldersLowercase {
	Get-ChildItem -Directory | ForEach-Object {
		$NewName = $_.Name.ToLowerInvariant()
		$TempItem = Rename-Item -LiteralPath $_.FullName -NewName "a" -PassThru
		Rename-Item -LiteralPath $TempItem.FullName -NewName $NewName
	}
}

######################################################################################
# Set ou change computer Name (hostname)
######################################################################################
function Set-ComputerName {
	param ( [Parameter(Mandatory)] [string]$ComputerName )

	if ($ComputerName -ne (&Hostname)) {
		Rename-computer -NewName $ComputerName -Restart -Force
	}
}

######################################################################################
# set my Windows Lang and Regionalization preference
# Set My keyboard preferences (en-US: International)
######################################################################################
function Set-MyPrefsWinDateTime {
	Set-TimeZone -Name "E. South America Standard Time" #Set Timezone

	$regPath = 'HKCU:\Control Panel\International'
	Set-ItemProperty -Path $regPath -name sShortDate 	-value	"dd/MM/yy" #Set Short date format
	Set-ItemProperty -Path $regPath -name sLongDate 	-value	"dddd, d' de 'MMMM' de 'yyyy" # Set Long date format
	Set-ItemProperty -Path $regPath -name sTimeFormat 	-value	"HH:mm:ss" #set time format
	Set-ItemProperty -Path $regPath -name sShortTime 	-value	"HH:mm" # Set Short time format
}

######################################################################################
# set my Windows Lang and Regionalization preference
# Set My keyboard preferences (en-US: International)
######################################################################################
function Set-MyPrefsWinKeyboard {
	#############################################################
	# Keyboard settings
	# HKEY_USERS\.DEFAULT\Keyboard Layout\Preload
	# HKEY_CURRENT_USER\Keyboard Layout\Preload
	# https://answers.microsoft.com/en-us/windows/forum/all/unwanted-keyboard-layouts-keep-appearing-when-i/f26a0384-ad0c-42af-838d-c475a5326e25
	#############################################################
	Set-WinUserLanguageList -LanguageList en-US -WarningAction SilentlyContinue  -InformationAction Ignore -force #langs i want available at system
	Set-WinLanguageBarOption
	# Set-WinLanguageBarOption -UseLegacyLanguageBar -UseLegacySwitchMode # testing if works

	$actualKB = Get-WinUserLanguageList
	$actualKB[0].InputMethodTips.Clear()  > $null #clear all en-US Keyboards
	$actualKB[0].InputMethodTips.Add('0409:00020409') > $null #set only keyboard available to en-US(International)
	$actualKB.RemoveAll( { $args[0].LanguageTag -clike 'pt*' } ) > $null

	Set-WinUserLanguageList $actualKB -Force -WarningAction SilentlyContinue -InformationAction Ignore #apply settings globally
	Set-WinDefaultInputMethodOverride -InputTip "0409:00000409" -WarningAction SilentlyContinue  -InformationAction Ignore #Force keyboard layout to current user: en-US(International)
}


######################################################################################
# set my Windows Lang and Regionalization preference
# Set My keyboard preferences (en-US: International)
######################################################################################
function Set-MyPrefsWinRegionalization {
	#############################################################
	# Install optional language packs (-AsJobs = in background)
	#############################################################
	Install-Language pt-BR -AsJob
	Install-Language en-US -AsJob

	#############################################################
	# Geral settings
	#############################################################
	Set-WinHomeLocation -GeoId "0x20" #Set country/ region to Brazil
	Set-Culture -CultureInfo pt-BR #Set Culture to Brazil
	Set-WinSystemLocale en-US -WarningAction SilentlyContinue  -InformationAction Ignore #set hole system language
	Set-WinUILanguageOverride -Language en-US #override global system language to en-US


	#############################################################
	# Date and Time settings
	#############################################################
	Set-MyPrefsWinDateTime # my custom function to define prefs

	#############################################################
	# Set default Windows UI language
	#############################################################
	Set-SystemPreferredUILanguage en-US

	#############################################################
	# Set default Windows keyboard prefs
	#############################################################
	Set-MyPrefsWinKeyboard # my custom function to define prefs


}


######################################################################################
# set my Windows Style Settings
######################################################################################
function Set-MyPrefsWinExplorer {

	#############################################################
	# System Theme Style
	#############################################################
	$regPath = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize'
	Set-ItemProperty -Path $regPath -Name 'AppsUseLightTheme' -Value 0 -Force; #set "app" style mode to "dark"
	Set-ItemProperty -Path $regPath -Name 'SystemUsesLightTheme' -Value 0 -Force; #set "OS" style mode to "dark"

	#############################################################
	# Taskbar settings and style
	#############################################################
	$regPath = 'HKCU:\Control Panel\International'
	Set-ItemProperty -Path $regPath -Name "TaskbarDa" 				-Value 0 # taskbar: hide widgets (news and interests)
	Set-ItemProperty -Path $regPath -Name "ShowCopilotButton" 		-Value 0 # taskbar: unpin copilot button
	Set-ItemProperty -Path $regPath -Name "ShowTaskViewButton" 		-Value 0 # taskbar: unpin views button
	Set-ItemProperty -Path $regPath -Name "TaskbarGlomLevel" 		-Value 0 # taskbar: always combine and hide labels
	Set-ItemProperty -Path $regPath -Name "SearchboxTaskbarMode"	-Value 0 # taskbar: unpin search button

	###################################################################
	# Taskbar and Start Menu PIN/UNPIN
	# todo: check why when PING icons are gone (without icons)
	###################################################################
	#$a = (get-appxpackage | Where-Object Name -like '*windowsterminal*').InstallLocation
	#syspin "$a\WindowsTerminal.exe" 5386 > $null

	#syspin ((Get-Command wt).Source) 5386 > $null
	#$WindowsTerminalDir = Get-ChildItem "$Env:PROGRAMFILES\WindowsApps\Microsoft.Windowsterminal*__8wekyb3d8bbwe*" -ErrorAction SilentlyContinue
	###############################
	# Taskbar Pin / Unpin
	#
	# 	Usage:
	# 	syspin "file" Param
	#
	# 	Params:
	# 	5386  : Pin to taskbar
	# 	5387  : Unpin from taskbar
	# 	51201 : Pin to start
	# 	51394 : Unpin to start
	###############################


	###################################################################
	# Tray Icons SHOW/HIDE
	###################################################################
	Show-TrayIcon Skype -hide
	Show-TrayIcon slack
	Show-TrayIcon wingetui
	Show-TrayIcon mailbird
	Show-TrayIcon everything

	#############################################################
	# Explorer: Files and foder view settings
	#############################################################
	$regPath = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
	Set-ItemProperty -Path $regPath -Name 'HideFileExt' 					-Type DWord -Value 0 # show know file extensions
	Set-ItemProperty -Path $regPath -Name 'Hidden' 							-Type DWord -Value 1 # show hidden files
	Set-ItemProperty -Path $regPath -Name 'ShowSyncProviderNotifications' 	-Type DWord -Value 0 # hide sync provider notifications
	Set-ItemProperty -Path $regPath -Name 'LaunchTo' 						-Type DWord -Value 1 # set 'This PC' as default when open explorer.exe

	# Set explorer view: GroupBy NONE (to  current user: all folders)
	$Bags = 'HKCU:\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\Bags'
	$DLID = '{885A186E-A440-4ADA-812B-DB871B942259}'
	(Get-ChildItem $bags -recurse | Where-Object PSChildName -eq $DLID ) | Remove-Item

	#############################################################
	# Explorer: System, Bing Search, Cortana Search
	#############################################################
	$regPath = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Search'
	Set-ItemProperty -Path $regPath	-Name 'BingSearchEnabled' 			-Type DWord -Value 0
	Set-ItemProperty -Path $regPath	-Name 'AllowSearchToUseLocation' 	-Type DWord -Value 0
	Set-ItemProperty -Path $regPath	-Name 'CortanaConsent' 				-Type DWord -Value 0



	Get-Process explorer | Stop-Process #restart explorer

}

######################################################################################
# set my Windows Files Association preferences
######################################################################################
function Set-MyPrefsWinFileAssociations {

	#############################################################
	# Explorer: Default browser and browser action associations
	#############################################################
	$regPathPrefix = "HKCU:\Software\Microsoft\Windows\Shell\Associations\UrlAssociations"
	$browserName = 'ChromeHTML'
	Set-Itemproperty -path "$regPathPrefix\https\UserChoice" 			-name 	'ProgId' -value $browserName -force
	Set-Itemproperty -path "$regPathPrefix\http\UserChoice" 			-name 	'ProgId' -value $browserName -force
	Set-Itemproperty -path "$regPathPrefix\http\UserChoice" 			-name 	'ProgId' -value $browserName -force
	Set-Itemproperty -path "$regPathPrefix\read\UserChoice" 			-name 	'ProgId' -value $browserName -force
	# Set-Itemproperty -path "$regPathPrefix\webcal\UserChoice" 			-name 	'ProgId' -value $browserName -force
	Set-Itemproperty -path "$regPathPrefix\microsoft-edge\UserChoice" 	-name 	'ProgId' -value $browserName -force



	#############################################################
	# Explorer: Default file "open with" associations
	#############################################################

	####################################
	# System dll and .exe icons
	#
	# %systemroot%\system32\imageres.dll			- Collection of miscellaneous icons
	# %systemroot%\system32\shell32.dll				- Another collection of miscellaneous icons
	# %systemroot%\system32\pifmgr.dll				- Legacy and exotic (i.e. not very useful) icons used in Windows 95 and 98.
	# %systemroot%\explorer.exe						- A few icons used by Explorer and its older versions.
	# %systemroot%\system32\accessibilitycpl.dll	- Icons used for accessibility.
	# %systemroot%\system32\ddores.dll 				- Icons used for hardware devices and resources.
	# %systemroot%\system32\moricons.dll			- Set of legacy icons used in pre-2000 Windows versions
	# %systemroot%\system32\mmcndmgr.dll			- Another set of legacy icons
	# %systemroot%\system32\mmres.dll				- Icons related to audio hardware.
	# %systemroot%\system32\netcenter.dll			- A few icons related to networking.
	# %systemroot%\system32\netshell.dll			- More icons related to networking
	# %systemroot%\system32\networkexplorer.dll		- More icons related to networking
	# %systemroot%\system32\pnidui.dll				- Modern style white icons related to network status.
	# %systemroot%\system32\sensorscpl.dll			- Icons for various sensors, which mostly look the same unfortunately
	# %systemroot%\system32\setupapi.dll			- Icons used by hardware setup wizards
	# %systemroot%\system32\wmploc.dll				- Icons related to multimedia, including hardware icons, MIME type icons, status icons, etc.
	# %systemroot%\system32\wpdshext.dll			- A few icons related to portable devices battery.
	# %systemroot%\system32\compstui.dll			- Legacy icons mostly related to printing.
	# %systemroot%\system32\ieframe.dll				- All kinds of icons used by IE.
	# %systemroot%\system32\dmdskres.dll			- A few icons used for disk management.
	# %systemroot%\system32\dsuiext.dll				- Icons related to network locations and services.
	# %systemroot%\system32\mstscax.dll				- Icons used for remote desktop connection.
	# %systemroot%\system32\wiashext.dll			- Icons used for imaging hardware.
	# %systemroot%\system32\comres.dll				- Some general status icons.
	# %systemroot%\system32\mstsc.exe				- A few icons used for system monitoring and configuration.
	# %systemroot%\explorer.exe						- Few icons used by File Explorer
	# %systemroot%\regedit.exe						- Icons used by regedit and filetype association
	# %systemroot%\system32\mstsc.exe				- holds a few other network-related icons
	# Others under %systemroot%\system32			- actioncentercpl.dll, aclui.dll, autoplay.dll, comctl32.dll, xwizards.dll, ncpa.cpl, url.dll
	####################################

	#vscode
	$appPath = (Get-Command code).Source
	Register-FTA $appPath .ps1
	Register-FTA $appPath .nuspec
	Register-FTA $appPath .txt 				-icon "shell32.dll,070"
	Register-FTA $appPath .json 			-icon "%homepath%\.assets\img\json.ico"
	Register-FTA $appPath .csv 				-icon "%homepath%\.assets\img\csv.ico"
	Register-FTA $appPath .html 			-icon "%homepath%\.assets\img\html.ico"
	Register-FTA $appPath .css 				-icon "%homepath%\.assets\img\css.ico"
	Register-FTA $appPath .sass 			-icon "%homepath%\.assets\img\sass.ico"
	Register-FTA $appPath .js 				-icon "%homepath%\.assets\img\javascript.ico"
	Register-FTA $appPath .xml 				-icon "%homepath%\.assets\img\xml.ico"
	Register-FTA $appPath .md 				-icon "%homepath%\.assets\img\markdown.ico"
	Register-FTA $appPath .py 				-icon "%homepath%\.assets\img\python.ico"
	Register-FTA $appPath .cs 				-icon "%homepath%\.assets\img\csharp.ico"
	Register-FTA $appPath .razor 			-icon "%homepath%\.assets\img\csharp.ico"
	Register-FTA $appPath .yaml 			-icon "%homepath%\.assets\img\yaml.ico"
	Register-FTA $appPath .yml 				-icon "%homepath%\.assets\img\yaml.ico"
	Register-FTA $appPath .php 				-icon "%homepath%\.assets\img\php.ico"
	Register-FTA $appPath .bat 				-icon "%homepath%\.assets\img\shell.ico"
	Register-FTA $appPath .ptb 				-icon "%homepath%\.assets\img\config.ico"
	Register-FTA $appPath .sh 				-icon "%homepath%\.assets\img\shell.ico"
	Register-FTA $appPath .bash_profile 	-icon "%homepath%\.assets\img\config.ico"
	Register-FTA $appPath .bashrc 			-icon "%homepath%\.assets\img\config.ico"
	Register-FTA $appPath .gitconfig 		-icon "%homepath%\.assets\img\config.ico"
	Register-FTA $appPath .profile 			-icon "%homepath%\.assets\img\config.ico"
	Register-FTA $appPath .zprofile 		-icon "%homepath%\.assets\img\config.ico"
	Register-FTA $appPath .editorconfig 	-icon "%homepath%\.assets\img\config.ico"
	Register-FTA $appPath .dockerignore 	-icon "%homepath%\.assets\img\config.ico"
	Register-FTA $appPath .zshrc 			-icon "%homepath%\.assets\img\config.ico"
	Register-FTA $appPath .bashrc_profile 	-icon "%homepath%\.assets\img\config.ico"
	Register-FTA $appPath .ini 				-icon "shell32.dll,070"
	Register-FTA $appPath .reg 				-icon "%SystemRoot%\regedit.exe,1"
	Register-FTA $appPath .config 			-icon "%homepath%\.assets\img\config.ico"
	Register-FTA $appPath .conf 			-icon "%homepath%\.assets\img\config.ico"

	#7zip
	$appPath = "$Env:PROGRAMFILES\7-Zip\7zFM.exe"
	Register-FTA $appPath .7z
	Register-FTA $appPath .zip
	Register-FTA $appPath .rar
	Register-FTA $appPath .tar
	Register-FTA $appPath .apk
	Register-FTA $appPath .gz
	Register-FTA $appPath .gzip
	Register-FTA $appPath .tgz
	Register-FTA $appPath .cab
	Register-FTA $appPath .bz
	Register-FTA $appPath .bz2
	Register-FTA $appPath .z
	Register-FTA $appPath .wim
	Register-FTA $appPath .xz

	Register-FTA $appPath .nupkg

}

######################################################################################
# Display a time countdown
######################################################################################
function Start-CountDown {
	param (
		[Parameter(Mandatory)] [string]$Message,
		[Parameter(Mandatory)] [string]$Seconds
	)

	$EndTime = [datetime]::UtcNow.AddSeconds($Seconds)

	while (($TimeRemaining = ($EndTime - [datetime]::UtcNow)) -gt 0) {
		Write-Progress -Activity ' ' -Status "$Message " -SecondsRemaining $TimeRemaining.TotalSeconds
		Start-Sleep 1
	}
}

######################################################################################
# Get the install path from an App
######################################################################################
function Get-AppPath {
	param (
		[Parameter(Mandatory)] [string]$AppName
	)

	return (Get-AppxPackage -Name "*$AppName*").InstallLocation

}



######################################################################################
# Uninstall Microsoft Esge
######################################################################################
function Uninstall-Edge {
	[CmdletBinding()]
	param ()

	if ([Security.Principal.WindowsIdentity]::GetCurrent().Groups -contains 'S-1-5-32-544') {

		$regView = [Microsoft.Win32.RegistryView]::Registry32
		$microsoft = [Microsoft.Win32.RegistryKey]::OpenBaseKey([Microsoft.Win32.RegistryHive]::LocalMachine, $regView).
		OpenSubKey('SOFTWARE\Microsoft', $true)

		$edgeClient = $microsoft.OpenSubKey('EdgeUpdate\ClientState\{56EB18F8-B008-4CBD-B6D2-8C97FE7E9062}', $true)
		if ($null -ne $edgeClient.GetValue('experiment_control_labels')) {
			$edgeClient.DeleteValue('experiment_control_labels')
		}

		$microsoft.CreateSubKey('EdgeUpdateDev').SetValue('AllowUninstall', '')

		$uninstallRegKey = $microsoft.OpenSubKey('Windows\CurrentVersion\Uninstall\Microsoft Edge')
		$uninstallString = $uninstallRegKey.GetValue('UninstallString') + ' --force-uninstall'
		Start-Process cmd.exe "/c $uninstallString" -WindowStyle Hidden
	}
	else { Write-Error "Required admin privileges" }
}


######################################################################################
# Install and app inside an ISO
######################################################################################
function Install-FromIso {
	[CmdletBinding()]
	param (
		[Parameter(Mandatory = $true)][string]$ISOPath,
		[Parameter(Mandatory = $true)][string]$installer,
		#[switch]$sillent
		[Parameter(Mandatory = $true)][string]$crack,
		[Parameter(Mandatory = $true)][string]$destination
	)

	#if sillent is present try to install sillently
	$sillent ? "--silent=1" : $null
	#$sillent = "--silent=1" #allways silent

	#Mount Image
	$mountedPath = Mount-DiskImage -imagepath $ISOPath -PassThru
	$mountLetter = "$(($mountedPath | Get-Volume).DriveLetter):"
	$sourcePath = "$mountLetter\crack\*"

	#unlock hosts file (if locked)
	Set-ItemProperty -Path "C:\Windows\System32\drivers\etc\*" -Name IsReadOnly -Value $False

	#run Installer
	Start-Process -FilePath "$mountLetter\$installer" -ArgumentList "--silent=1" -Wait > $null


	# if destination path dont end with \ add it
	if ($destination -notmatch '\\$') { $destination += '\' }

	#crack
	copy-item "$sourcePath" "$destination" -force -recurse > $null


	#Dismount Image
	#Dismount-DiskImage -ImagePath $ISOPath

}


######################################################################################
# Install and app inside an ISO
######################################################################################
function Copy-KubeConfig {
	[CmdletBinding()]
	param (
		[Parameter(Mandatory = $true)][string]$Server
		#[Parameter(Mandatory = $false)][string]$ClusterServerUsername
	)

	#if no username defined, use username: root
	#$ClusterServerUsername ? $null : ($ClusterServerUsername = "root")

	#if user no defined use user: root
	($server -notmatch '\@') ? ($Server = "root@$Server") : $null

	# copy secret from server to local machine
	New-Item  $HOME\.kube\ -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
	scp "${Server}:~/.kube/config" $HOME\.kube\config
}


######################################################################################
# Install fonts at windows
######################################################################################
function Install-FontWindows {
	[CmdletBinding()]
	param (
		[Parameter(Mandatory = $true)][string]$FontFolder
		#[Parameter(Mandatory = $true)][string]$installer,
		#[switch]$sillent
	)


	#$FontFolder = "\\NetworkShare\FontsFolder"
	$FontItem = Get-Item -Path $FontFolder
	$FontList = Get-ChildItem -Path "$FontItem\*" -Include ('*.fon','*.otf','*.ttc','*.ttf')

	foreach ($Font in $FontList) {
			# Write-Host 'Installing font -' $Font.BaseName
			Copy-Item $Font "C:\Windows\Fonts" -WarningAction SilentlyContinue -InformationAction Ignore -Force -ErrorVariable capturedErrors -ErrorAction SilentlyContinue
			New-ItemProperty -Name $Font.BaseName -Path "HKLM:\Software\Microsoft\Windows NT\CurrentVersion\Fonts" -PropertyType string -Value $Font.name -Force | Out-Null
	}

}


######################################################################################
# Import dotenv file values into current process environment
######################################################################################
function Import-DotEnvFile {
	[CmdletBinding()]
	param (
		[Parameter(Mandatory = $true)]
		[string]$Path
	)

	$loaded = @{}
	if (!(Test-Path -Path $Path -PathType Leaf)) {
		return $loaded
	}

	foreach ($rawLine in (Get-Content -Path $Path -ErrorAction SilentlyContinue)) {
		$line = [string]$rawLine
		if ([string]::IsNullOrWhiteSpace($line)) { continue }
		$line = $line.Trim()
		if ($line.StartsWith('#')) { continue }

		if ($line -match '^(?:export\s+)?(?<name>[A-Za-z_][A-Za-z0-9_]*)=(?<value>.*)$') {
			$name = $Matches.name
			$value = $Matches.value.Trim()

			if (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'"))) {
				$value = $value.Substring(1, $value.Length - 2)
			}

			Set-Item -Path "Env:$name" -Value $value
			$loaded[$name] = $value
		}
	}

	return $loaded
}


######################################################################################
# Ensure OP service account token is available in process env
######################################################################################
function Ensure-OpServiceAccountToken {
	[CmdletBinding()]
	param ()

	if (-not [string]::IsNullOrWhiteSpace($Env:OP_SERVICE_ACCOUNT_TOKEN)) {
		return $true
	}

	$userToken = [Environment]::GetEnvironmentVariable('OP_SERVICE_ACCOUNT_TOKEN', 'User')
	if (-not [string]::IsNullOrWhiteSpace($userToken)) {
		$Env:OP_SERVICE_ACCOUNT_TOKEN = $userToken
		return $true
	}

	$envSopsPath = Join-Path $Env:USERPROFILE '.env.local.sops'
	if (Test-Path -Path $envSopsPath -PathType Leaf) {
		$loaded = Import-DotEnvFromSops -EncryptedPath $envSopsPath
		if ($loaded.ContainsKey('OP_SERVICE_ACCOUNT_TOKEN') -and -not [string]::IsNullOrWhiteSpace($Env:OP_SERVICE_ACCOUNT_TOKEN)) {
			return $true
		}
	}

	$legacyPlainPath = Join-Path $Env:USERPROFILE '.env.local'
	if (Test-Path -Path $legacyPlainPath -PathType Leaf) {
		$loaded = Import-DotEnvFile -Path $legacyPlainPath
		if ($loaded.ContainsKey('OP_SERVICE_ACCOUNT_TOKEN') -and -not [string]::IsNullOrWhiteSpace($Env:OP_SERVICE_ACCOUNT_TOKEN)) {
			return $true
		}
	}

	Write-Warning "OP_SERVICE_ACCOUNT_TOKEN not found. Enter a valid service account token."
	$secureToken = Read-Host -Prompt "OP_SERVICE_ACCOUNT_TOKEN" -AsSecureString
	if ($secureToken.Length -eq 0) {
		return $false
	}

	$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)
	try {
		$plainToken = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
	}
	finally {
		[Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
	}

	if ([string]::IsNullOrWhiteSpace($plainToken)) {
		return $false
	}

	$Env:OP_SERVICE_ACCOUNT_TOKEN = $plainToken
	return $true
}


######################################################################################
# Generate encrypted ~/.env.local.sops from 1Password template
######################################################################################
function Set-LocalEnvFrom1Password {
	[CmdletBinding()]
	param (
		[string]$TemplatePath = (Join-Path $Env:USERPROFILE 'dotfiles\bootstrap\secrets\.env.local.tpl'),
		[string]$OutputPath = (Join-Path $Env:USERPROFILE '.env.local.sops'),
		[switch]$AllowPlaintextFallback
	)

	if (!(Test-CommandExists op)) {
		Write-Warning "op command not found."
		return $false
	}

	if (!(Test-Path -Path $TemplatePath -PathType Leaf)) {
		Write-Warning "Template not found: $TemplatePath"
		return $false
	}

	if (!(Ensure-OpServiceAccountToken)) {
		Write-Warning "Unable to continue without OP_SERVICE_ACCOUNT_TOKEN."
		return $false
	}

	$tmpPlain = [System.IO.Path]::GetTempFileName()
	$tmpKey = $null
	try {
		& op inject -i $TemplatePath -o $tmpPlain -f *> $null
		if ($LASTEXITCODE -ne 0 -or !(Test-Path -Path $tmpPlain)) {
			Write-Warning "Failed to generate temporary .env from 1Password template."
			return $false
		}

		$loaded = Import-DotEnvFile -Path $tmpPlain
		if ($loaded.ContainsKey('GITHUB_TOKEN') -and [string]::IsNullOrWhiteSpace($Env:GH_TOKEN)) {
			$Env:GH_TOKEN = $loaded['GITHUB_TOKEN']
		}

		$ageKey = $Env:SOPS_AGE_KEY
		$canEncrypt = $ageKey -and (Test-CommandExists sops) -and (Test-CommandExists age-keygen)
		if ($canEncrypt) {
			# Derive public recipient from private age key using a temp identity file.
			$tmpKey = [System.IO.Path]::GetTempFileName()
			Set-Content -Path $tmpKey -Value $ageKey -NoNewline
			$recipient = (& age-keygen -y $tmpKey 2>$null | Out-String).Trim()
			if ([string]::IsNullOrWhiteSpace($recipient)) {
				$canEncrypt = $false
			}
			else {
				& sops --encrypt --age $recipient --output $OutputPath $tmpPlain *> $null
				if ($LASTEXITCODE -ne 0) { $canEncrypt = $false }
			}
		}

		if (-not $canEncrypt) {
			if ($AllowPlaintextFallback) {
				Copy-Item -Path $tmpPlain -Destination $OutputPath -Force
			}
			else {
				Write-Warning "SOPS_AGE_KEY/sops/age-keygen ausentes; criptografia .sops indisponível e fallback plaintext não permitido."
				return $false
			}
		}
	}
	finally {
		if (Test-Path -Path $tmpPlain) { Remove-Item -Path $tmpPlain -Force -ErrorAction SilentlyContinue }
		if ($tmpKey -and (Test-Path -Path $tmpKey)) { Remove-Item -Path $tmpKey -Force -ErrorAction SilentlyContinue }
	}

	return $true
}

function Import-DotEnvFromSops {
	[CmdletBinding()]
	param (
		[string]$EncryptedPath = (Join-Path $Env:USERPROFILE '.env.local.sops')
	)

	if (!(Test-Path -Path $EncryptedPath -PathType Leaf)) {
		Write-Warning "Encrypted env file not found: $EncryptedPath"
		return @{}
	}

	if (!(Test-CommandExists sops)) {
		Write-Warning "sops not found; cannot decrypt $EncryptedPath"
		return @{}
	}

	if ([string]::IsNullOrWhiteSpace($Env:SOPS_AGE_KEY)) {
		$userAgeKey = [Environment]::GetEnvironmentVariable('SOPS_AGE_KEY', 'User')
		if (-not [string]::IsNullOrWhiteSpace($userAgeKey)) {
			$Env:SOPS_AGE_KEY = $userAgeKey
		}
	}
	if ([string]::IsNullOrWhiteSpace($Env:SOPS_AGE_KEY_FILE)) {
		$userAgeKeyFile = [Environment]::GetEnvironmentVariable('SOPS_AGE_KEY_FILE', 'User')
		if (-not [string]::IsNullOrWhiteSpace($userAgeKeyFile)) {
			$Env:SOPS_AGE_KEY_FILE = $userAgeKeyFile
		}
	}

	$tmpPlain = [System.IO.Path]::GetTempFileName()
	try {
		& sops -d --output $tmpPlain $EncryptedPath *> $null
		if ($LASTEXITCODE -ne 0) {
			Write-Warning "Failed to decrypt $EncryptedPath"
			return @{}
		}
		return Import-DotEnvFile -Path $tmpPlain
	}
	finally {
		if (Test-Path -Path $tmpPlain) { Remove-Item -Path $tmpPlain -Force -ErrorAction SilentlyContinue }
	}
}


######################################################################################
# Materialize SOPS age key file from env when key content is available
######################################################################################
function Ensure-SopsAgeKeyFile {
	[CmdletBinding()]
	param (
		[string]$DefaultPath = (Join-Path $Env:USERPROFILE '.config\sops\age\keys.txt'),
		[switch]$ForceMaterialize
	)

	# If a key file is already present, we are done.
	if (-not [string]::IsNullOrWhiteSpace($Env:SOPS_AGE_KEY_FILE) -and (Test-Path -Path $Env:SOPS_AGE_KEY_FILE -PathType Leaf)) {
		return $true
	}

	# If no key material is present, nothing to do.
	if ([string]::IsNullOrWhiteSpace($Env:SOPS_AGE_KEY)) {
		return $true
	}

	# Default behavior now is non-materializing (keep only in env).
	if (-not $ForceMaterialize -and [string]::IsNullOrWhiteSpace($Env:SOPS_AGE_KEY_FILE)) {
		return $true
	}

	$targetPath = if (-not [string]::IsNullOrWhiteSpace($Env:SOPS_AGE_KEY_FILE)) { $Env:SOPS_AGE_KEY_FILE } else { $DefaultPath }
	$targetDir = Split-Path -Path $targetPath -Parent
	if ($targetDir -and !(Test-Path -Path $targetDir)) {
		New-Item -Path $targetDir -ItemType Directory -Force | Out-Null
	}

	Set-Content -Path $targetPath -Value $Env:SOPS_AGE_KEY -NoNewline
	$Env:SOPS_AGE_KEY_FILE = $targetPath
	return (Test-Path -Path $targetPath -PathType Leaf)
}


######################################################################################
# Ensure gh CLI is logged in using a token resolved from environment/1Password
######################################################################################
function Ensure-GitHubCliAuthFrom1Password {
	[CmdletBinding()]
	param ()

	if (!(Test-CommandExists gh)) {
		Write-Warning "gh command not found."
		return $false
	}

	$authStatusOutput = & gh auth status --hostname github.com 2>&1
	if ($LASTEXITCODE -eq 0) {
		& gh auth setup-git --hostname github.com *> $null
		& gh config set git_protocol ssh --host github.com *> $null
		return $true
	}

	$token = $Env:GH_TOKEN
	if ([string]::IsNullOrWhiteSpace($token)) {
		$token = $Env:GITHUB_TOKEN
	}

	if ([string]::IsNullOrWhiteSpace($token) -and (Test-CommandExists op)) {
		# Prefer least-privilege project token, then fallback to full-access token.
		$tokenRefs = @(
			'op://secrets/dotfiles/github/token',
			'op://secrets/github/api/token'
		)
		foreach ($ref in $tokenRefs) {
			$candidate = (& op read $ref 2>$null | Out-String).Trim()
			if (-not [string]::IsNullOrWhiteSpace($candidate)) {
				$token = $candidate
				break
			}
		}
	}

	if ([string]::IsNullOrWhiteSpace($token)) {
		Write-Warning "GitHub token not found in GH_TOKEN/GITHUB_TOKEN/op://secrets/dotfiles/github/token/op://secrets/github/api/token."
		return $false
	}
	$Env:GH_TOKEN = $token

	$token | & gh auth login --hostname github.com --git-protocol ssh --with-token *> $null
	if ($LASTEXITCODE -ne 0) {
		Write-Warning "gh auth login failed."
		return $false
	}

	& gh auth setup-git --hostname github.com *> $null
	& gh config set git_protocol ssh --host github.com *> $null
	return $true
}


######################################################################################
# Internal helper: signed commit test in a temporary repository
######################################################################################
function Invoke-CheckEnvSignedCommitTest {
	[CmdletBinding()]
	param ()

	$tempRepo = Join-Path ([System.IO.Path]::GetTempPath()) ("checkenv-" + [guid]::NewGuid().ToString("N"))
	$null = New-Item -Path $tempRepo -ItemType Directory -Force

	try {
		Push-Location $tempRepo

		& git init -q *> $null
		if ($LASTEXITCODE -ne 0) {
			return [PSCustomObject]@{
				Status   = 'fail'
				Detail   = 'git init failed.'
				Solution = 'Validate git installation and write permissions to temp folders.'
			}
		}

		$userName = (& git config --global --get user.name 2>$null | Out-String).Trim()
		$userEmail = (& git config --global --get user.email 2>$null | Out-String).Trim()
		if ([string]::IsNullOrWhiteSpace($userName)) { & git config user.name "checkEnv" *> $null }
		if ([string]::IsNullOrWhiteSpace($userEmail)) { & git config user.email "checkenv@local" *> $null }

		Set-Content -Path '.checkenv' -Value ("checkenv {0}" -f (Get-Date -Format o)) -NoNewline
		& git add .checkenv *> $null

		$commitOutput = & git commit -S -m "checkEnv signed commit" 2>&1
		if ($LASTEXITCODE -ne 0) {
			return [PSCustomObject]@{
				Status   = 'fail'
				Detail   = ("git commit -S failed: {0}" -f (($commitOutput | Out-String).Trim()))
				Solution = 'Fix gpg.ssh.program, user.signingkey and 1Password SSH agent availability.'
			}
		}

		$sigOutput = (& git log --show-signature -1 2>&1 | Out-String).Trim()
		if ($sigOutput -match 'Good "git" signature' -or $sigOutput -match 'Good SSH signature') {
			return [PSCustomObject]@{
				Status   = 'success'
				Detail   = 'git commit -S succeeded and signature validation output is good.'
				Solution = ''
			}
		}

		return [PSCustomObject]@{
			Status   = 'inconclusive'
			Detail   = 'Signed commit created, but no explicit "Good signature" marker was found.'
			Solution = 'Run git log --show-signature -1 in a test repo and validate signer output.'
		}
	}
	finally {
		Pop-Location
		Remove-Item -Path $tempRepo -Recurse -Force -ErrorAction SilentlyContinue
	}
}


######################################################################################
# checkEnv: environment health check for auth/signing/agent requirements
######################################################################################
function checkEnv {
	[CmdletBinding()]
	param ()

	# In-memory structured report used to print a deterministic summary at the end.
	$results = New-Object System.Collections.Generic.List[object]

	function Add-CheckResult {
		param (
			[string]$Item,
			[ValidateSet('success', 'fail', 'inconclusive')]
			[string]$Status,
			[string]$Detail,
			[string]$Solution
		)

		$results.Add([PSCustomObject]@{
				Item     = $Item
				Status   = $Status
				Detail   = $Detail
				Solution = $Solution
			}) | Out-Null
	}

	function Add-CommandCheck {
		param ([string]$Name)
		$cmd = Get-Command -Name $Name -ErrorAction SilentlyContinue
		if ($cmd) {
			Add-CheckResult -Item "Command: $Name" -Status 'success' -Detail "Available at $($cmd.Source)." -Solution ''
		}
		else {
			Add-CheckResult -Item "Command: $Name" -Status 'fail' -Detail "Command not found in PATH." -Solution "Install '$Name' in bootstrap and reload the shell."
		}
	}

	Write-Host "checkEnv: validating environment"

	# 1) Baseline command availability
	'op', 'gh', 'git', 'ssh' | ForEach-Object { Add-CommandCheck $_ }

	# 2) Optional sops/age readiness checks (non-blocking for SSH auth flow)
	if (Test-CommandExists sops) {
		Add-CheckResult -Item 'Command: sops' -Status 'success' -Detail "Available at $((Get-Command sops).Source)." -Solution ''
	}
	else {
		Add-CheckResult -Item 'Command: sops' -Status 'inconclusive' -Detail 'sops not found in PATH.' -Solution 'Install sops if you want encrypted local secret files with age.'
	}

	if (Test-CommandExists age) {
		Add-CheckResult -Item 'Command: age' -Status 'success' -Detail "Available at $((Get-Command age).Source)." -Solution ''
	}
	else {
		Add-CheckResult -Item 'Command: age' -Status 'inconclusive' -Detail 'age not found in PATH.' -Solution 'Install age to support sops encryption/decryption flow.'
	}

	if ([string]::IsNullOrWhiteSpace($Env:SOPS_AGE_KEY)) {
		$userAgeKey = [Environment]::GetEnvironmentVariable('SOPS_AGE_KEY', 'User')
		if (-not [string]::IsNullOrWhiteSpace($userAgeKey)) {
			$Env:SOPS_AGE_KEY = $userAgeKey
		}
	}

	if (-not [string]::IsNullOrWhiteSpace($Env:SOPS_AGE_KEY_FILE) -and (Test-Path -Path $Env:SOPS_AGE_KEY_FILE -PathType Leaf)) {
		Add-CheckResult -Item 'SOPS age key file' -Status 'success' -Detail "SOPS_AGE_KEY_FILE points to an existing file: $Env:SOPS_AGE_KEY_FILE." -Solution ''
	}
	elseif (-not [string]::IsNullOrWhiteSpace($Env:SOPS_AGE_KEY)) {
		Add-CheckResult -Item 'SOPS age key file' -Status 'success' -Detail 'SOPS_AGE_KEY is loaded in environment (env-only mode).' -Solution ''
	}
	else {
		Add-CheckResult -Item 'SOPS age key file' -Status 'fail' -Detail 'No SOPS age key detected in environment.' -Solution 'Set SOPS_AGE_KEY (recommended) or configure SOPS_AGE_KEY_FILE.'
	}

	# 3) 1Password CLI session and referenced-secret readability
	if (Test-CommandExists op) {
		$opHealthy = $false
		& op whoami *> $null
		if ($LASTEXITCODE -eq 0) {
			$opHealthy = $true
		}
		else {
			$envSopsPath = Join-Path $Env:USERPROFILE '.env.local.sops'
			if (Test-Path -Path $envSopsPath -PathType Leaf) {
				$loadedEnv = Import-DotEnvFromSops -EncryptedPath $envSopsPath
				if ($loadedEnv.ContainsKey('OP_SERVICE_ACCOUNT_TOKEN')) {
					& op whoami *> $null
					if ($LASTEXITCODE -eq 0) {
						$opHealthy = $true
					}
				}
			}
		}

		if ($opHealthy) {
			Add-CheckResult -Item '1Password CLI session' -Status 'success' -Detail 'op whoami succeeded.' -Solution ''
		}
		else {
			Add-CheckResult -Item '1Password CLI session' -Status 'fail' -Detail 'op whoami failed (including one automatic retry).' -Solution 'Ensure OP_SERVICE_ACCOUNT_TOKEN is valid in current shell and run op whoami.'
		}
	}

	if (Test-CommandExists op) {
		$secretsRefPath = Join-Path $Env:USERPROFILE 'dotfiles\df\secrets\secrets-ref.yaml'
		if (Test-Path -Path $secretsRefPath -PathType Leaf) {
			$refs = New-Object System.Collections.Generic.HashSet[string] ([System.StringComparer]::OrdinalIgnoreCase)
			foreach ($line in (Get-Content -Path $secretsRefPath -ErrorAction SilentlyContinue)) {
				$matches = [regex]::Matches([string]$line, 'op://[A-Za-z0-9\./\-_]+')
				foreach ($m in $matches) { [void]$refs.Add($m.Value) }
			}

			foreach ($ref in $refs) {
				& op read $ref *> $null
				if ($LASTEXITCODE -eq 0) {
					Add-CheckResult -Item "1Password secret ref" -Status 'success' -Detail "$ref is readable." -Solution ''
				}
				else {
					Add-CheckResult -Item "1Password secret ref" -Status 'inconclusive' -Detail "$ref is not readable in current context." -Solution "Validate vault/item permissions for the service account token."
				}
			}
		}
	}

	# 4) GitHub CLI auth and protocol policy (must be SSH for this setup)
	if (Test-CommandExists gh) {
		$statusOutput = & gh auth status --hostname github.com 2>&1
		if ($LASTEXITCODE -ne 0) {
			$null = Ensure-GitHubCliAuthFrom1Password
			$statusOutput = & gh auth status --hostname github.com 2>&1
		}

		if ($LASTEXITCODE -eq 0) {
			Add-CheckResult -Item 'GitHub CLI auth' -Status 'success' -Detail 'gh authenticated for github.com.' -Solution ''
		}
		else {
			Add-CheckResult -Item 'GitHub CLI auth' -Status 'fail' -Detail (($statusOutput | Out-String).Trim()) -Solution 'Authenticate with gh using a token from 1Password (prefer op://secrets/dotfiles/github/token).'
		}

		$gitProtocol = (& gh config get git_protocol --host github.com 2>$null | Out-String).Trim()
		if ($gitProtocol -eq 'ssh') {
			Add-CheckResult -Item 'GitHub CLI git protocol' -Status 'success' -Detail 'git_protocol=ssh.' -Solution ''
		}
		else {
			Add-CheckResult -Item 'GitHub CLI git protocol' -Status 'fail' -Detail "git_protocol='$gitProtocol'." -Solution 'Run gh config set git_protocol ssh --host github.com.'
		}
	}

	# 5) Git signing policy checks in repository context
	#    (supports includeIf rules that depend on current gitdir path).
	if (Test-CommandExists git) {
		$gitProbePath = Join-Path $Env:USERPROFILE 'dotfiles'
		$tempGitProbePath = $null
		if (!(Test-Path -Path (Join-Path $gitProbePath '.git'))) {
			$tempGitProbePath = Join-Path $Env:USERPROFILE ("checkenv-probe-" + [guid]::NewGuid().ToString("N"))
			New-Item -Path $tempGitProbePath -ItemType Directory -Force | Out-Null
			& git -C $tempGitProbePath init -q *> $null
			$gitProbePath = $tempGitProbePath
		}

		$gpgFormat = (& git -C $gitProbePath config --get gpg.format 2>$null | Out-String).Trim()
		$gpgProgram = (& git -C $gitProbePath config --get gpg.ssh.program 2>$null | Out-String).Trim()
		$signingKey = (& git -C $gitProbePath config --get user.signingkey 2>$null | Out-String).Trim()
		$commitSign = (& git -C $gitProbePath config --get commit.gpgsign 2>$null | Out-String).Trim()

		if ($gpgFormat -eq 'ssh') {
			Add-CheckResult -Item 'Git signing format' -Status 'success' -Detail 'gpg.format=ssh.' -Solution ''
		}
		else {
			Add-CheckResult -Item 'Git signing format' -Status 'fail' -Detail "gpg.format='$gpgFormat'." -Solution 'Run git config --global gpg.format ssh.'
		}

		if ($commitSign -eq 'true') {
			Add-CheckResult -Item 'Git commit signing default' -Status 'success' -Detail 'commit.gpgsign=true.' -Solution ''
		}
		else {
			Add-CheckResult -Item 'Git commit signing default' -Status 'fail' -Detail "commit.gpgsign='$commitSign'." -Solution 'Run git config --global commit.gpgsign true.'
		}

		if ($signingKey -match '^ssh-') {
			Add-CheckResult -Item 'Git signing key' -Status 'success' -Detail 'user.signingkey uses SSH key format.' -Solution ''
		}
		else {
			Add-CheckResult -Item 'Git signing key' -Status 'fail' -Detail 'user.signingkey is missing or invalid.' -Solution 'Set user.signingkey to the SSH public key managed by 1Password.'
		}

		$resolvedProgramPath = $gpgProgram.Trim('"')
		if (-not [string]::IsNullOrWhiteSpace($resolvedProgramPath) -and (Test-Path -Path $resolvedProgramPath)) {
			Add-CheckResult -Item '1Password signer program' -Status 'success' -Detail "gpg.ssh.program exists at $resolvedProgramPath." -Solution ''
		}
		elseif (-not [string]::IsNullOrWhiteSpace($resolvedProgramPath)) {
			Add-CheckResult -Item '1Password signer program' -Status 'fail' -Detail "gpg.ssh.program points to a missing path: $resolvedProgramPath." -Solution 'Fix gpg.ssh.program to a valid op-ssh-sign binary.'
		}
		else {
			Add-CheckResult -Item '1Password signer program' -Status 'fail' -Detail 'gpg.ssh.program is not set.' -Solution 'Set gpg.ssh.program to 1Password op-ssh-sign binary.'
		}

		if ($tempGitProbePath -and (Test-Path -Path $tempGitProbePath)) {
			Remove-Item -Path $tempGitProbePath -Recurse -Force -ErrorAction SilentlyContinue
		}
	}

	# 6) SSH identity agent policy + GitHub SSH handshake
	if (Test-CommandExists ssh) {
		$sshGraph = & ssh -G github.com 2>$null
		$identityAgentLine = $sshGraph | Where-Object { $_ -match '^identityagent\s+' } | Select-Object -First 1
		$identityAgent = if ($identityAgentLine) { ($identityAgentLine -replace '^identityagent\s+', '').Trim() } else { '' }

		if ($identityAgent -match '1password' -or $identityAgent -match 'openssh-ssh-agent' -or $identityAgent -eq '/tmp/1password-agent.sock') {
			Add-CheckResult -Item 'SSH identity agent' -Status 'success' -Detail "identityagent=$identityAgent." -Solution ''
		}
		elseif (-not [string]::IsNullOrWhiteSpace($identityAgent)) {
			Add-CheckResult -Item 'SSH identity agent' -Status 'fail' -Detail "Unexpected identityagent=$identityAgent." -Solution 'Point IdentityAgent to the 1Password-managed SSH agent.'
		}
		else {
			Add-CheckResult -Item 'SSH identity agent' -Status 'fail' -Detail 'identityagent is not configured for github.com.' -Solution 'Configure ~/.ssh/config(.local) to use 1Password SSH agent.'
		}

		$identityFileNone = $sshGraph | Where-Object { $_ -eq 'identityfile none' } | Select-Object -First 1
		if ($identityFileNone) {
			Add-CheckResult -Item 'SSH identity source policy' -Status 'success' -Detail 'identityfile none is active for github.com.' -Solution ''
		}
		else {
			Add-CheckResult -Item 'SSH identity source policy' -Status 'inconclusive' -Detail 'identityfile none not found in effective SSH config.' -Solution 'Set IdentityFile none to enforce agent-only key usage.'
		}

		if ((Test-Path -Path '/tmp/1password-agent.sock' -PathType Leaf) -or (Test-Path -Path '/tmp/1password-agent.sock' -PathType Container)) {
			Add-CheckResult -Item '1Password WSL agent socket' -Status 'success' -Detail '/tmp/1password-agent.sock is present.' -Solution ''
		}
		elseif (-not $IsWindows) {
			Add-CheckResult -Item '1Password WSL agent socket' -Status 'inconclusive' -Detail '/tmp/1password-agent.sock not found.' -Solution 'Enable 1Password SSH agent integration for Linux/WSL and restart shell.'
		}

		$sshTestOutput = & ssh -T git@github.com -o BatchMode=yes -o NumberOfPasswordPrompts=0 -o ConnectTimeout=10 -o ConnectionAttempts=1 -o StrictHostKeyChecking=accept-new 2>&1
		$sshTestText = ($sshTestOutput | Out-String).Trim()
		if ($sshTestText -match 'successfully authenticated') {
			Add-CheckResult -Item 'SSH auth to GitHub' -Status 'success' -Detail 'SSH handshake with GitHub succeeded.' -Solution ''
		}
		elseif ($sshTestText -match 'timed out') {
			Add-CheckResult -Item 'SSH auth to GitHub' -Status 'inconclusive' -Detail $sshTestText -Solution 'Check network connectivity and run checkEnv again.'
		}
		elseif ($LASTEXITCODE -eq 255) {
			Add-CheckResult -Item 'SSH auth to GitHub' -Status 'fail' -Detail $sshTestText -Solution 'Ensure GitHub account has the 1Password-managed SSH public key and the agent is active.'
		}
		else {
			Add-CheckResult -Item 'SSH auth to GitHub' -Status 'inconclusive' -Detail $sshTestText -Solution 'Run ssh -T git@github.com manually and inspect host/key output.'
		}
	}

	# 7) Detect local private key files (optional hardening signal)
	if (Test-CommandExists ssh) {
		$privateKeyCandidates = @(
			"$Env:USERPROFILE\.ssh\id_rsa",
			"$Env:USERPROFILE\.ssh\id_ed25519",
			"$Env:USERPROFILE\.ssh\id_ecdsa",
			"$Env:USERPROFILE\.ssh\id_dsa"
		) | Where-Object { Test-Path -Path $_ -PathType Leaf }

		if ($privateKeyCandidates.Count -eq 0) {
			Add-CheckResult -Item 'Local private SSH keys' -Status 'success' -Detail 'No default local private keys found.' -Solution ''
		}
		else {
			Add-CheckResult -Item 'Local private SSH keys' -Status 'inconclusive' -Detail ("Found local private keys: {0}" -f ($privateKeyCandidates -join ', ')) -Solution 'If you want strict 1Password-only management, archive/remove local private keys.'
		}
	}

	# 8) End-to-end signed commit smoke-test in disposable temp repository
	if (Test-CommandExists git) {
		$commitTest = Invoke-CheckEnvSignedCommitTest
		Add-CheckResult -Item 'Signed commit test' -Status $commitTest.Status -Detail $commitTest.Detail -Solution $commitTest.Solution
	}

	# 9) Render report + actionable remediation hints
	foreach ($entry in $results) {
		$label = switch ($entry.Status) {
			'success' { '[SUCCESS]' }
			'fail' { '[FAIL]' }
			default { '[INCONCLUSIVE]' }
		}
		$color = switch ($entry.Status) {
			'success' { 'Green' }
			'fail' { 'Red' }
			default { 'Yellow' }
		}
		Write-Host "$label $($entry.Item) - $($entry.Detail)" -ForegroundColor $color
	}

	$successCount = ($results | Where-Object { $_.Status -eq 'success' }).Count
	$failCount = ($results | Where-Object { $_.Status -eq 'fail' }).Count
	$inconclusiveCount = ($results | Where-Object { $_.Status -eq 'inconclusive' }).Count
	Write-Host ""
	Write-Host ("Summary: success={0} fail={1} inconclusive={2}" -f $successCount, $failCount, $inconclusiveCount)

	$fixes = $results | Where-Object { -not [string]::IsNullOrWhiteSpace($_.Solution) } | Select-Object -Unique Item, Solution
	if ($fixes.Count -gt 0) {
		Write-Host "Possible fixes:"
		foreach ($fix in $fixes) {
			Write-Host ("- {0}: {1}" -f $fix.Item, $fix.Solution)
		}
	}

	return ($failCount -eq 0)
}


######################################################################################
# Resolve dotfiles repo path from env/default location
######################################################################################
function Get-DotfilesRepoPath {
	[CmdletBinding()]
	param ()

	if (-not [string]::IsNullOrWhiteSpace($Env:DOTFILES)) {
		return $Env:DOTFILES
	}

	return (Join-Path $Env:USERPROFILE 'dotfiles')
}


######################################################################################
# Sync policy for cross-platform tests:
# 1) Windows repo must be clean
# 2) Push Windows branch to origin
# 3) WSL repo must be clean
# 4) Pull --ff-only in WSL
# 5) Validate both HEADs are identical
######################################################################################
function Sync-DotfilesWindowsToWsl {
	[CmdletBinding()]
	param (
		[string]$WslDistro = 'Ubuntu',
		[string]$WslRepoPath = '~/dotfiles',
		[switch]$SkipPush
	)

	$windowsRepoPath = Get-DotfilesRepoPath
	if (!(Test-Path -Path $windowsRepoPath -PathType Container)) {
		throw "Windows dotfiles path not found: $windowsRepoPath"
	}

	$winDirty = (& git -C $windowsRepoPath status --porcelain=v1 --untracked-files=no 2>$null | Out-String).Trim()
	if (-not [string]::IsNullOrWhiteSpace($winDirty)) {
		throw "Windows repo has uncommitted changes. Commit and push before WSL tests."
	}

	& git -C $windowsRepoPath fetch --prune origin *> $null
	if ($LASTEXITCODE -ne 0) {
		throw "Failed to fetch origin in Windows repo."
	}

	$currentBranch = (& git -C $windowsRepoPath rev-parse --abbrev-ref HEAD 2>$null | Out-String).Trim()
	if ([string]::IsNullOrWhiteSpace($currentBranch) -or $currentBranch -eq 'HEAD') {
		throw "Unable to detect current branch in Windows repo."
	}

	$upstreamRef = (& git -C $windowsRepoPath rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>$null | Out-String).Trim()
	if ([string]::IsNullOrWhiteSpace($upstreamRef)) {
		& git -C $windowsRepoPath branch --set-upstream-to ("origin/{0}" -f $currentBranch) $currentBranch *> $null
		$upstreamRef = (& git -C $windowsRepoPath rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>$null | Out-String).Trim()
		if ([string]::IsNullOrWhiteSpace($upstreamRef)) {
			throw ("No upstream configured for branch '{0}'." -f $currentBranch)
		}
	}

	if (-not $SkipPush) {
		& git -C $windowsRepoPath push origin $currentBranch *> $null
		if ($LASTEXITCODE -ne 0) {
			# Fallback for https remotes when default auth is not enough:
			# use GitHub token resolved from 1Password refs.
			$originUrl = (& git -C $windowsRepoPath remote get-url origin 2>$null | Out-String).Trim()
			$repoPath = $null
			if ($originUrl -match 'github\.com[:/](?<repo>[^/]+/[^/]+?)(?:\.git)?$') {
				$repoPath = $Matches.repo
			}

			$token = $null
			if ((Test-CommandExists op)) {
				foreach ($ref in @('op://secrets/dotfiles/github/token', 'op://secrets/github/api/token')) {
					$candidate = (& op read $ref 2>$null | Out-String).Trim()
					if (-not [string]::IsNullOrWhiteSpace($candidate)) {
						$token = $candidate
						break
					}
				}
			}

			if (-not [string]::IsNullOrWhiteSpace($token) -and -not [string]::IsNullOrWhiteSpace($repoPath)) {
				$pushUrl = "https://{0}@github.com/{1}.git" -f $token, $repoPath
				& git -C $windowsRepoPath push $pushUrl $currentBranch *> $null
			}

			if ($LASTEXITCODE -ne 0) {
				throw ("Failed to push Windows branch '{0}' to origin." -f $currentBranch)
			}
		}
	}

	$wslCheckCmd = "cd $WslRepoPath && git status --porcelain=v1 --untracked-files=no"
	$wslDirty = (& wsl -d $WslDistro bash -lc $wslCheckCmd 2>$null | Out-String).Trim()
	if ($LASTEXITCODE -ne 0) {
		throw ("WSL repo not accessible at {0} in distro '{1}'." -f $WslRepoPath, $WslDistro)
	}
	if (-not [string]::IsNullOrWhiteSpace($wslDirty)) {
		throw "WSL repo has uncommitted changes. Commit/stash in WSL before sync."
	}

	$wslSyncCmd = "cd $WslRepoPath && git fetch --prune origin && git pull --ff-only"
	& wsl -d $WslDistro bash -lc $wslSyncCmd *> $null
	if ($LASTEXITCODE -ne 0) {
		throw ("Failed to sync WSL repo ({0}) with pull --ff-only." -f $WslRepoPath)
	}

	$windowsHead = (& git -C $windowsRepoPath rev-parse HEAD 2>$null | Out-String).Trim()
	$wslHead = (& wsl -d $WslDistro bash -lc "cd $WslRepoPath && git rev-parse HEAD" 2>$null | Out-String).Trim()
	if ([string]::IsNullOrWhiteSpace($windowsHead) -or [string]::IsNullOrWhiteSpace($wslHead)) {
		throw "Unable to resolve HEAD in Windows and/or WSL repositories."
	}
	if ($windowsHead -ne $wslHead) {
		throw ("Sync mismatch: Windows HEAD={0} WSL HEAD={1}" -f $windowsHead, $wslHead)
	}

	$result = [PSCustomObject]@{
		WindowsRepo = $windowsRepoPath
		WslDistro   = $WslDistro
		WslRepo     = $WslRepoPath
		Branch      = $currentBranch
		Head        = $windowsHead
	}

	Write-Host ("Sync OK: branch={0} head={1}" -f $result.Branch, $result.Head)
	return $result
}
