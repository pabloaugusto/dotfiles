[CmdletBinding()]
param (
	[string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
)

$ErrorActionPreference = 'Stop'

. (Join-Path $RepoRoot 'app\df\powershell\_functions.ps1')

function Get-NormalizedPath {
	param ([string]$PathValue)

	return ([System.IO.Path]::GetFullPath($PathValue)).TrimEnd('\')
}

function Assert-LinkTarget {
	param (
		[string]$Path,
		[string]$ExpectedTarget
	)

	if (-not (Test-Path -Path $Path)) {
		throw "Path ausente: $Path"
	}

	$item = Get-Item -Path $Path -Force -ErrorAction Stop
	$expected = Get-NormalizedPath -PathValue $ExpectedTarget

	if ($item.PSIsContainer) {
		if ($item.LinkType -ne 'SymbolicLink' -and $item.LinkType -ne 'Junction') {
			throw "Esperado SymbolicLink/Junction em '$Path', obtido '$($item.LinkType)'."
		}

		$target = if ($null -ne $item.Target) { Get-NormalizedPath -PathValue ([string]($item.Target | Select-Object -First 1)) } else { '' }
		if (-not $target.Equals($expected, [System.StringComparison]::OrdinalIgnoreCase)) {
			throw "Target inesperado para '$Path'. Atual='$target' Esperado='$expected'."
		}
		return
	}

	if ($item.LinkType -eq 'SymbolicLink') {
		$target = if ($null -ne $item.Target) { Get-NormalizedPath -PathValue ([string]($item.Target | Select-Object -First 1)) } else { '' }
		if (-not $target.Equals($expected, [System.StringComparison]::OrdinalIgnoreCase)) {
			throw "Target inesperado para '$Path'. Atual='$target' Esperado='$expected'."
		}
		return
	}

	$expectedContent = Get-Content -Path $ExpectedTarget -Raw -ErrorAction Stop
	$currentContent = Get-Content -Path $Path -Raw -ErrorAction Stop
	if ($currentContent -ne $expectedContent) {
		throw "Arquivo '$Path' nao aponta para o mesmo conteudo de '$ExpectedTarget'."
	}
}

$tempRoot = Join-Path $env:TEMP ("dotfiles-bootstrap-windows-{0}" -f ([guid]::NewGuid().ToString('N')))
$profileRoot = Join-Path $tempRoot 'profile'
$documentsPath = Join-Path $profileRoot 'Documents'
$appDataPath = Join-Path $profileRoot 'AppData\Roaming'
$localAppDataPath = Join-Path $profileRoot 'AppData\Local'
$codeUserPath = Join-Path $appDataPath 'Code\User'
$terminalSettingsPath = Join-Path $tempRoot 'terminal\settings.json'

New-Item -ItemType Directory -Path $documentsPath -Force | Out-Null
New-Item -ItemType Directory -Path $codeUserPath -Force | Out-Null
New-Item -ItemType Directory -Path $localAppDataPath -Force | Out-Null
New-Item -ItemType Directory -Path (Split-Path -Path $terminalSettingsPath -Parent) -Force | Out-Null

$previousEnv = @{}
$overrides = @{
	USERPROFILE                           = $profileRoot
	APPDATA                               = $appDataPath
	LOCALAPPDATA                          = $localAppDataPath
	DOTFILES_REPO_ROOT_WINDOWS            = $RepoRoot
	DOTFILES_WINDOWS_DOCUMENTS_PATH       = $documentsPath
	DOTFILES_WINDOWS_CODE_USER_PATH       = $codeUserPath
	DOTFILES_WINDOWS_TERMINAL_SETTINGS_PATH = $terminalSettingsPath
	DOTFILES_ONEDRIVE_ENABLED             = 'false'
	DOTFILES_LINKS_DRIVE_ENABLED          = 'false'
	DOTFILES_BOOTSTRAP_ALLOW_UNELEVATED_RELINK = 'true'
	DOTFILES_BOOTSTRAP_SKIP_PROFILE_RELOAD = 'true'
	DOTFILES_PROFILE_FOLDER_DOCUMENTS_ENABLED = 'false'
	DOTFILES_PROFILE_FOLDER_DESKTOP_ENABLED   = 'false'
	DOTFILES_PROFILE_FOLDER_DOWNLOADS_ENABLED = 'false'
	DOTFILES_PROFILE_FOLDER_PICTURES_ENABLED  = 'false'
	DOTFILES_PROFILE_FOLDER_VIDEOS_ENABLED    = 'false'
	DOTFILES_PROFILE_FOLDER_MUSIC_ENABLED     = 'false'
	DOTFILES_PROFILE_FOLDER_CONTACTS_ENABLED  = 'false'
	DOTFILES_PROFILE_FOLDER_FAVORITES_ENABLED = 'false'
	DOTFILES_PROFILE_FOLDER_LINKS_ENABLED     = 'false'
}

function Set-ProcessOverrides {
	param ([hashtable]$Items)

	foreach ($name in $Items.Keys) {
		[Environment]::SetEnvironmentVariable($name, [string]$Items[$name], 'Process')
	}
}

try {
	foreach ($name in $overrides.Keys) {
		$previousEnv[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
	}

	Set-ProcessOverrides -Items $overrides
	. (Join-Path $RepoRoot 'app\bootstrap\bootstrap-windows.ps1') -RelinkOnly
	Set-ProcessOverrides -Items $overrides
	. (Join-Path $RepoRoot 'app\bootstrap\bootstrap-windows.ps1') -RelinkOnly

	Assert-LinkTarget -Path (Join-Path $profileRoot '.ssh') -ExpectedTarget (Join-Path $RepoRoot 'app\df\ssh')
	Assert-LinkTarget -Path (Join-Path $profileRoot '.assets') -ExpectedTarget (Join-Path $RepoRoot 'app\df\assets')
	Assert-LinkTarget -Path (Join-Path $profileRoot '.config\git') -ExpectedTarget (Join-Path $RepoRoot 'app\df\git')
	Assert-LinkTarget -Path (Join-Path $profileRoot '.oh-my-posh') -ExpectedTarget (Join-Path $RepoRoot 'app\df\oh-my-posh')
	Assert-LinkTarget -Path (Join-Path $documentsPath 'Powershell\profile.ps1') -ExpectedTarget (Join-Path $RepoRoot 'app\df\powershell\profile.ps1')
	Assert-LinkTarget -Path (Join-Path $documentsPath 'WindowsPowerShell\Microsoft.PowerShell_profile.ps1') -ExpectedTarget (Join-Path $RepoRoot 'app\df\powershell\Microsoft.PowerShell_profile.ps1')
	Assert-LinkTarget -Path $codeUserPath -ExpectedTarget (Join-Path $RepoRoot 'app\df\vscode')

	foreach ($localPath in @('bin', 'etc', 'clients', 'projects')) {
		$fullPath = Join-Path $profileRoot $localPath
		if (-not (Test-Path -Path $fullPath -PathType Container)) {
			throw "Path local esperado nao encontrado: $fullPath"
		}
		$item = Get-Item -Path $fullPath -Force -ErrorAction Stop
		if ($null -ne $item.LinkType) {
			throw "Path local '$fullPath' deveria permanecer diretorio local no modo sem OneDrive."
		}
	}

	Write-Host 'Windows bootstrap relink integration OK.'
}
finally {
	foreach ($name in $previousEnv.Keys) {
		[Environment]::SetEnvironmentVariable($name, $previousEnv[$name], 'Process')
	}
	Remove-Item -Path $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
}
