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
# 1) OneDrive prerequisite (install/setup/migrate root when enabled)
# 2) Safety checks + dotfiles links
# 3) Optional software/fonts/preferences (full mode)
# 4) Mandatory auth/signing bootstrap (both modes)
# 5) Optional profile-folder links to OneDrive (with migration/backup policy)
# 6) Final checkEnv gate
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
# OneDrive path resolution helpers (Windows)
#
# Goals:
# - Support override via YAML/env without hardcoding D:.
# - Accept absolute or relative (to OneDrive root) values.
# - Fail fast with actionable error when no valid root exists.
#################################################################################
function Test-WindowsAbsolutePath {
	param ([string]$PathValue)
	if ([string]::IsNullOrWhiteSpace($PathValue)) { return $false }
	return ($PathValue -match '^[A-Za-z]:\\') -or ($PathValue -match '^\\\\')
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

function Expand-WindowsPathValue {
	param ([string]$PathValue)
	if ([string]::IsNullOrWhiteSpace($PathValue)) { return '' }
	$expanded = [Environment]::ExpandEnvironmentVariables($PathValue)
	if ($expanded -match '%[^%]+%') {
		throw "Unresolved Windows environment token in path '$PathValue'. Check variable names (example: %USERPROFILE%)."
	}
	return $expanded
}

function Normalize-WindowsPath {
	param ([string]$PathValue)
	if ([string]::IsNullOrWhiteSpace($PathValue)) { return '' }
	try {
		return ([System.IO.Path]::GetFullPath((Expand-WindowsPathValue -PathValue $PathValue))).TrimEnd('\')
	}
	catch {
		return ((Expand-WindowsPathValue -PathValue $PathValue).TrimEnd('\'))
	}
}

function Resolve-PathOrDefault {
	param (
		[string]$Candidate,
		[string]$DefaultPath
	)
	$resolved = Normalize-WindowsPath -PathValue $Candidate
	if ([string]::IsNullOrWhiteSpace($resolved)) {
		return (Normalize-WindowsPath -PathValue $DefaultPath)
	}
	return $resolved
}

function Resolve-WindowsPathWithRoot {
	param (
		[string]$RootPath,
		[string]$PathValue
	)

	if ([string]::IsNullOrWhiteSpace($PathValue)) { return '' }
	if (Test-WindowsAbsolutePath -PathValue $PathValue) {
		return $PathValue
	}
	$relative = ($PathValue -replace '^[\\/]+', '')
	return (Join-Path $RootPath $relative)
}

function Read-YesNoPrompt {
	param (
		[string]$Prompt,
		[bool]$DefaultNo = $true
	)

	$defaultLabel = if ($DefaultNo) { 'N' } else { 'Y' }
	while ($true) {
		$typed = Read-Host -Prompt "$Prompt (Y/N) [$defaultLabel]"
		if ([string]::IsNullOrWhiteSpace($typed)) {
			return -not $DefaultNo
		}
		switch -Regex ($typed.Trim()) {
			'^(y|yes|s|sim)$' { return $true }
			'^(n|no|nao|não)$' { return $false }
			default { Write-Host "Resposta inválida. Use Y ou N." }
		}
	}
}

function Get-OneDriveConfiguredRoot {
	$accountsPath = 'HKCU:\Software\Microsoft\OneDrive\Accounts'
	if (Test-Path -Path $accountsPath) {
		$keys = Get-ChildItem -Path $accountsPath -ErrorAction SilentlyContinue
		foreach ($key in ($keys | Sort-Object PSChildName)) {
			$userFolder = (Get-ItemProperty -Path $key.PSPath -Name 'UserFolder' -ErrorAction SilentlyContinue).UserFolder
			if (-not [string]::IsNullOrWhiteSpace($userFolder)) {
				return (Normalize-WindowsPath -PathValue $userFolder)
			}
		}
	}

	if (-not [string]::IsNullOrWhiteSpace($Env:OneDrive)) {
		return (Normalize-WindowsPath -PathValue $Env:OneDrive)
	}

	return ''
}

function Get-OneDriveExePath {
	$candidates = @(
		"$Env:LOCALAPPDATA\Microsoft\OneDrive\OneDrive.exe",
		"$Env:ProgramFiles\Microsoft OneDrive\OneDrive.exe",
		"$Env:ProgramFiles(x86)\Microsoft OneDrive\OneDrive.exe"
	)
	foreach ($candidate in $candidates) {
		if (-not [string]::IsNullOrWhiteSpace($candidate) -and (Test-Path -Path $candidate -PathType Leaf)) {
			return $candidate
		}
	}
	return ''
}

function Stop-OneDriveClient {
	$oneDriveExe = Get-OneDriveExePath
	if (-not [string]::IsNullOrWhiteSpace($oneDriveExe)) {
		Start-Process -FilePath $oneDriveExe -ArgumentList '/shutdown' -WindowStyle Hidden -ErrorAction SilentlyContinue | Out-Null
	}
	Start-Sleep -Seconds 2
	Get-Process -Name OneDrive -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
	Start-Sleep -Seconds 1
}

function Start-OneDriveClient {
	$oneDriveExe = Get-OneDriveExePath
	if ([string]::IsNullOrWhiteSpace($oneDriveExe)) {
		return $false
	}
	Start-Process -FilePath $oneDriveExe -WindowStyle Minimized -ErrorAction SilentlyContinue | Out-Null
	Start-Sleep -Seconds 2
	return $true
}

function Install-OneDriveClient {
	if (-not [string]::IsNullOrWhiteSpace((Get-OneDriveExePath))) {
		return $true
	}

	if (-not (Get-Command -Name winget -ErrorAction SilentlyContinue)) {
		Write-Warning "winget not found. Unable to install OneDrive automatically."
		return $false
	}

	Write-Output "OneDrive is not installed. Installing Microsoft.OneDrive via winget..."
	$null = & winget install --id Microsoft.OneDrive --exact --accept-source-agreements --accept-package-agreements --disable-interactivity 2>&1
	Start-Sleep -Seconds 2
	return (-not [string]::IsNullOrWhiteSpace((Get-OneDriveExePath)))
}

function Set-OneDriveConfiguredRoot {
	param (
		[string]$DesiredRoot,
		[string]$ExpectedCurrentRoot = ''
	)

	$desiredNormalized = Normalize-WindowsPath -PathValue $DesiredRoot
	if ([string]::IsNullOrWhiteSpace($desiredNormalized)) {
		return $false
	}

	$accountsPath = 'HKCU:\Software\Microsoft\OneDrive\Accounts'
	if (-not (Test-Path -Path $accountsPath)) {
		return $false
	}

	$expectedNormalized = Normalize-WindowsPath -PathValue $ExpectedCurrentRoot
	$updated = $false
	foreach ($key in (Get-ChildItem -Path $accountsPath -ErrorAction SilentlyContinue)) {
		$currentRoot = (Get-ItemProperty -Path $key.PSPath -Name 'UserFolder' -ErrorAction SilentlyContinue).UserFolder
		$currentNormalized = Normalize-WindowsPath -PathValue $currentRoot
		$canUpdate = [string]::IsNullOrWhiteSpace($expectedNormalized) -or
			$currentNormalized.Equals($expectedNormalized, [System.StringComparison]::OrdinalIgnoreCase)
		if (-not $canUpdate) {
			continue
		}

		try {
			Set-ItemProperty -Path $key.PSPath -Name 'UserFolder' -Value $desiredNormalized -ErrorAction Stop
			$updated = $true
		}
		catch {
			Write-Warning ("Failed to update OneDrive UserFolder in registry key {0}: {1}" -f $key.Name, $_.Exception.Message)
		}
	}
	return $updated
}

function Invoke-OneDriveJunctionMigration {
	param (
		[string]$CurrentRoot,
		[string]$DesiredRoot
	)

	$currentNormalized = Normalize-WindowsPath -PathValue $CurrentRoot
	$desiredNormalized = Normalize-WindowsPath -PathValue $DesiredRoot
	if ([string]::IsNullOrWhiteSpace($currentNormalized) -or [string]::IsNullOrWhiteSpace($desiredNormalized)) {
		throw "OneDrive migration requires both current and desired absolute paths."
	}
	if ($currentNormalized.Equals($desiredNormalized, [System.StringComparison]::OrdinalIgnoreCase)) {
		return $desiredNormalized
	}
	if ($desiredNormalized.StartsWith("$currentNormalized\", [System.StringComparison]::OrdinalIgnoreCase) -or
		$currentNormalized.StartsWith("$desiredNormalized\", [System.StringComparison]::OrdinalIgnoreCase)) {
		throw "OneDrive migration does not support nested roots ($currentNormalized <-> $desiredNormalized)."
	}

	Write-Host "Attempting OneDrive root migration (automatic, best-effort)..."
	Write-Host (" - current: {0}" -f $currentNormalized)
	Write-Host (" - desired: {0}" -f $desiredNormalized)

	Stop-OneDriveClient
	New-Item -ItemType Directory -Path $desiredNormalized -Force | Out-Null

	if (Test-Path -Path $currentNormalized -PathType Container) {
		# Copy first to preserve data in desired path before replacing original root with junction.
		# /XJ avoids traversing legacy junctions that commonly exist in large OneDrive trees.
		$roboLog = Join-Path $Env:TEMP ("dotfiles-onedrive-migration-{0}.log" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
		$null = & robocopy $currentNormalized $desiredNormalized /E /COPY:DAT /DCOPY:DAT /XJ /R:2 /W:2 /NFL /NDL /NJH /NJS /NP /LOG:$roboLog
		if ($LASTEXITCODE -gt 7) {
			Write-Warning ("Robocopy migration log: {0}" -f $roboLog)
			if (Test-Path -Path $roboLog -PathType Leaf) {
				$tail = Get-Content -Path $roboLog -Tail 40 -ErrorAction SilentlyContinue
				if ($tail) {
					foreach ($line in $tail) {
						Write-Warning $line
					}
				}
			}
			throw "Robocopy failed while migrating OneDrive root (exit=$LASTEXITCODE)."
		}
		Write-Host ("Robocopy migration log: {0}" -f $roboLog)

		$currentItem = Get-Item -Path $currentNormalized -Force -ErrorAction SilentlyContinue
		$isJunction = ($null -ne $currentItem -and $currentItem.LinkType -eq 'Junction')
		$junctionTarget = if ($isJunction -and $null -ne $currentItem.Target) { Normalize-WindowsPath -PathValue ([string]($currentItem.Target | Select-Object -First 1)) } else { '' }
		if ($isJunction -and $junctionTarget.Equals($desiredNormalized, [System.StringComparison]::OrdinalIgnoreCase)) {
			Start-OneDriveClient | Out-Null
			return $desiredNormalized
		}

		$backupPath = "{0}.dotfiles-backup-{1}" -f $currentNormalized, (Get-Date -Format 'yyyyMMddHHmmss')
		Move-Item -Path $currentNormalized -Destination $backupPath -Force
		New-Item -ItemType Junction -Path $currentNormalized -Target $desiredNormalized -Force | Out-Null
		Write-Host ("Created junction: {0} -> {1}" -f $currentNormalized, $desiredNormalized)
		Write-Host ("Backup preserved at: {0}" -f $backupPath)
	}
	else {
		New-Item -ItemType Junction -Path $currentNormalized -Target $desiredNormalized -Force | Out-Null
		Write-Host ("Created junction for missing configured root: {0} -> {1}" -f $currentNormalized, $desiredNormalized)
	}

	if (Set-OneDriveConfiguredRoot -DesiredRoot $desiredNormalized -ExpectedCurrentRoot $currentNormalized) {
		Write-Host ("Updated OneDrive registry root to: {0}" -f $desiredNormalized)
	}
	else {
		Write-Warning "OneDrive registry root could not be updated automatically; junction fallback remains active."
	}

	Start-OneDriveClient | Out-Null
	return $desiredNormalized
}

function Resolve-WindowsLinkLayout {
	param ([string]$UserProfilePath)

	return [ordered]@{
		profileBin      = Resolve-PathOrDefault -Candidate $Env:DOTFILES_LINK_PROFILE_BIN -DefaultPath (Join-Path $UserProfilePath 'bin')
		profileEtc      = Resolve-PathOrDefault -Candidate $Env:DOTFILES_LINK_PROFILE_ETC -DefaultPath (Join-Path $UserProfilePath 'etc')
		profileClients  = Resolve-PathOrDefault -Candidate $Env:DOTFILES_LINK_PROFILE_CLIENTS -DefaultPath (Join-Path $UserProfilePath 'clients')
		profileProjects = Resolve-PathOrDefault -Candidate $Env:DOTFILES_LINK_PROFILE_PROJECTS -DefaultPath (Join-Path $UserProfilePath 'projects')
		driveEnabled    = ConvertTo-BoolFlag -Value $Env:DOTFILES_LINKS_DRIVE_ENABLED -Default $true
		driveBin        = Resolve-PathOrDefault -Candidate $Env:DOTFILES_LINK_DRIVE_BIN -DefaultPath 'D:\bin'
		driveEtc        = Resolve-PathOrDefault -Candidate $Env:DOTFILES_LINK_DRIVE_ETC -DefaultPath 'D:\etc'
		driveClients    = Resolve-PathOrDefault -Candidate $Env:DOTFILES_LINK_DRIVE_CLIENTS -DefaultPath 'D:\clients'
		driveProjects   = Resolve-PathOrDefault -Candidate $Env:DOTFILES_LINK_DRIVE_PROJECTS -DefaultPath 'D:\projects'
	}
}

function Resolve-OneDriveFolderTargetPath {
	param (
		[string]$OneDriveRoot,
		[string]$ConfiguredTarget,
		[string]$DefaultRelativeTarget
	)

	$targetHint = if ([string]::IsNullOrWhiteSpace($ConfiguredTarget)) { $DefaultRelativeTarget } else { $ConfiguredTarget }
	$resolved = Resolve-WindowsPathWithRoot -RootPath $OneDriveRoot -PathValue $targetHint
	return (Normalize-WindowsPath -PathValue $resolved)
}

function Get-WindowsProfileFolderLinkRules {
	param (
		[string]$UserProfilePath,
		[string]$OneDriveRoot
	)

	$rawRules = @(
		@{ label = 'Documents'; source = Join-Path $UserProfilePath 'Documents'; enabled = $Env:DOTFILES_PROFILE_FOLDER_DOCUMENTS_ENABLED; target = $Env:DOTFILES_PROFILE_FOLDER_DOCUMENTS_TARGET; defaultTarget = 'documents' },
		@{ label = 'Desktop'; source = Join-Path $UserProfilePath 'Desktop'; enabled = $Env:DOTFILES_PROFILE_FOLDER_DESKTOP_ENABLED; target = $Env:DOTFILES_PROFILE_FOLDER_DESKTOP_TARGET; defaultTarget = 'desktop' },
		@{ label = 'Downloads'; source = Join-Path $UserProfilePath 'Downloads'; enabled = $Env:DOTFILES_PROFILE_FOLDER_DOWNLOADS_ENABLED; target = $Env:DOTFILES_PROFILE_FOLDER_DOWNLOADS_TARGET; defaultTarget = 'downloads' },
		@{ label = 'Pictures'; source = Join-Path $UserProfilePath 'Pictures'; enabled = $Env:DOTFILES_PROFILE_FOLDER_PICTURES_ENABLED; target = $Env:DOTFILES_PROFILE_FOLDER_PICTURES_TARGET; defaultTarget = 'Imagens' },
		@{ label = 'Videos'; source = Join-Path $UserProfilePath 'Videos'; enabled = $Env:DOTFILES_PROFILE_FOLDER_VIDEOS_ENABLED; target = $Env:DOTFILES_PROFILE_FOLDER_VIDEOS_TARGET; defaultTarget = 'Vídeos' },
		@{ label = 'Music'; source = Join-Path $UserProfilePath 'Music'; enabled = $Env:DOTFILES_PROFILE_FOLDER_MUSIC_ENABLED; target = $Env:DOTFILES_PROFILE_FOLDER_MUSIC_TARGET; defaultTarget = 'Música' },
		@{ label = 'Contacts'; source = Join-Path $UserProfilePath 'Contacts'; enabled = $Env:DOTFILES_PROFILE_FOLDER_CONTACTS_ENABLED; target = $Env:DOTFILES_PROFILE_FOLDER_CONTACTS_TARGET; defaultTarget = 'documents\profile\contacts' },
		@{ label = 'Favorites'; source = Join-Path $UserProfilePath 'Favorites'; enabled = $Env:DOTFILES_PROFILE_FOLDER_FAVORITES_ENABLED; target = $Env:DOTFILES_PROFILE_FOLDER_FAVORITES_TARGET; defaultTarget = 'documents\profile\favorites' },
		@{ label = 'Links'; source = Join-Path $UserProfilePath 'Links'; enabled = $Env:DOTFILES_PROFILE_FOLDER_LINKS_ENABLED; target = $Env:DOTFILES_PROFILE_FOLDER_LINKS_TARGET; defaultTarget = 'documents\profile\links' }
	)

	$resolvedRules = New-Object System.Collections.Generic.List[object]
	foreach ($r in $rawRules) {
		$resolvedRules.Add([PSCustomObject]@{
				label   = $r.label
				source  = (Normalize-WindowsPath -PathValue $r.source)
				enabled = (ConvertTo-BoolFlag -Value ([string]$r.enabled) -Default $false)
				target  = if ([string]::IsNullOrWhiteSpace($OneDriveRoot)) { '' } else { Resolve-OneDriveFolderTargetPath -OneDriveRoot $OneDriveRoot -ConfiguredTarget ([string]$r.target) -DefaultRelativeTarget ([string]$r.defaultTarget) }
			}) | Out-Null
	}

	return $resolvedRules
}

function Ensure-ProfileFolderOneDriveLink {
	param (
		[pscustomobject]$Rule,
		[bool]$MigrateContent
	)

	if ([string]::IsNullOrWhiteSpace($Rule.target)) {
		throw "Profile folder '$($Rule.label)' has empty target path. Review user-config profile_links_*_target."
	}
	if ($Rule.source.Equals($Rule.target, [System.StringComparison]::OrdinalIgnoreCase)) {
		Write-Warning "Profile folder '$($Rule.label)' source and target are equal ($($Rule.source)). Skipping."
		return
	}

	New-Item -ItemType Directory -Path $Rule.target -Force | Out-Null

	$backupPath = ''
	$sourceExists = Test-Path -Path $Rule.source
	if ($sourceExists) {
		$sourceItem = Get-Item -Path $Rule.source -Force -ErrorAction SilentlyContinue
		$isLink = ($null -ne $sourceItem -and ($sourceItem.LinkType -eq 'SymbolicLink' -or $sourceItem.LinkType -eq 'Junction'))
		if ($isLink) {
			$currentTarget = if ($null -ne $sourceItem.Target) { Normalize-WindowsPath -PathValue ([string]($sourceItem.Target | Select-Object -First 1)) } else { '' }
			if ($currentTarget.Equals($Rule.target, [System.StringComparison]::OrdinalIgnoreCase)) {
				Write-Output ("Profile folder '{0}' already linked: {1} -> {2}" -f $Rule.label, $Rule.source, $Rule.target)
				return
			}
		}

		if ($MigrateContent -and (Test-Path -Path $Rule.source -PathType Container)) {
			$hasContent = (Get-ChildItem -Path $Rule.source -Force -ErrorAction SilentlyContinue | Select-Object -First 1) -ne $null
			if ($hasContent) {
				Write-Output ("Migrating content from '{0}' to '{1}' before link replacement..." -f $Rule.source, $Rule.target)
				# Windows profile folders often contain hidden legacy junctions (My Music/My Pictures/My Videos).
				# /XJ avoids traversal/permission errors during migration and keeps copy semantics predictable.
				$null = & robocopy $Rule.source $Rule.target /E /COPY:DAT /DCOPY:DAT /R:1 /W:1 /XJ /NFL /NDL /NJH /NJS /NP
				if ($LASTEXITCODE -gt 7) {
					throw "Robocopy failed migrating '$($Rule.label)' (exit=$LASTEXITCODE)."
				}
			}
		}

		$backupPath = "{0}.dotfiles-prelink-{1}" -f $Rule.source, (Get-Date -Format 'yyyyMMddHHmmss')
		$backupLeaf = Split-Path -Path $backupPath -Leaf
		# Rename in place to preserve ACL/reparse metadata and avoid traversing legacy junctions.
		Rename-Item -Path $Rule.source -NewName $backupLeaf -Force
		Write-Output ("Backup preserved for {0}: {1}" -f $Rule.label, $backupPath)
	}

	Add-Symlink $Rule.source $Rule.target > $null
	$linkItem = Get-Item -Path $Rule.source -Force -ErrorAction SilentlyContinue
	$isLink = ($null -ne $linkItem -and ($linkItem.LinkType -eq 'SymbolicLink' -or $linkItem.LinkType -eq 'Junction'))
	$linkTarget = if ($null -ne $linkItem -and $null -ne $linkItem.Target) { Normalize-WindowsPath -PathValue ([string]($linkItem.Target | Select-Object -First 1)) } else { '' }
	$expectedTarget = Normalize-WindowsPath -PathValue $Rule.target
	$linkOk = $isLink -and $linkTarget.Equals($expectedTarget, [System.StringComparison]::OrdinalIgnoreCase)

	if (-not $linkOk) {
		Write-Warning ("Failed to create symbolic link for '{0}'. Trying junction fallback..." -f $Rule.label)
		if (Test-Path -Path $Rule.source) {
			Remove-Item -Path $Rule.source -Recurse -Force -ErrorAction SilentlyContinue
		}
		New-Item -ItemType Junction -Path $Rule.source -Target $Rule.target -Force | Out-Null

		$linkItem = Get-Item -Path $Rule.source -Force -ErrorAction SilentlyContinue
		$isLink = ($null -ne $linkItem -and ($linkItem.LinkType -eq 'SymbolicLink' -or $linkItem.LinkType -eq 'Junction'))
		$linkTarget = if ($null -ne $linkItem -and $null -ne $linkItem.Target) { Normalize-WindowsPath -PathValue ([string]($linkItem.Target | Select-Object -First 1)) } else { '' }
		$linkOk = $isLink -and $linkTarget.Equals($expectedTarget, [System.StringComparison]::OrdinalIgnoreCase)
	}

	if (-not $linkOk) {
		# Do not leave user without the original folder when link creation fails.
		if (-not [string]::IsNullOrWhiteSpace($backupPath) -and (Test-Path -Path $backupPath) -and -not (Test-Path -Path $Rule.source)) {
			$restoreLeaf = Split-Path -Path $Rule.source -Leaf
			Rename-Item -Path $backupPath -NewName $restoreLeaf -Force
			Write-Warning ("Link creation failed. Original folder restored from backup: {0}" -f $backupPath)
		}
		throw ("Unable to create link/junction for profile folder '{0}' -> '{1}'." -f $Rule.source, $Rule.target)
	}

	Write-Output ("Linked profile folder: {0} -> {1}" -f $Rule.source, $Rule.target)
}

function Invoke-ProfileFoldersToOneDriveLinking {
	param (
		[bool]$OneDriveEnabled,
		[hashtable]$OneDriveLayout,
		[string]$UserProfilePath
	)

	$oneDriveRoot = ''
	if ($null -ne $OneDriveLayout) {
		$oneDriveRoot = [string]$OneDriveLayout.root
	}
	$rules = Get-WindowsProfileFolderLinkRules -UserProfilePath $UserProfilePath -OneDriveRoot $oneDriveRoot
	$enabledRules = $rules | Where-Object { $_.enabled }
	if ($enabledRules.Count -eq 0) {
		Write-Output "No optional profile folders selected for OneDrive linking."
		return
	}

	if (-not $OneDriveEnabled) {
		$labels = ($enabledRules | ForEach-Object { $_.label }) -join ', '
		throw "OneDrive is disabled, but profile folder links are enabled for: $labels. Disable them or enable OneDrive."
	}

	$migrateContent = ConvertTo-BoolFlag -Value $Env:DOTFILES_PROFILE_FOLDER_MIGRATE_CONTENT -Default $true
	if ($migrateContent) {
		Write-Output "Profile folder linking mode: migrate existing content to OneDrive targets before creating links."
	}
	else {
		Write-Output "Profile folder linking mode: create links only (no content migration; source folders become backups)."
	}
	foreach ($rule in $enabledRules) {
		Ensure-ProfileFolderOneDriveLink -Rule $rule -MigrateContent:$migrateContent
	}
}

function Remove-StaleProfileFolderPrelinkBackups {
	param (
		[string]$UserProfilePath
	)

	if ([string]::IsNullOrWhiteSpace($UserProfilePath) -or -not (Test-Path -Path $UserProfilePath -PathType Container)) {
		return
	}

	$items = Get-ChildItem -Path $UserProfilePath -Force -ErrorAction SilentlyContinue |
		Where-Object { $_.Name -like '*.dotfiles-prelink-*' } |
		Sort-Object LastWriteTime

	$removed = 0
	$migrated = 0
	$kept = 0

	foreach ($item in $items) {
		$removedCurrent = $false

		# Link/junction backups do not carry unique data; safe to delete.
		if (-not [string]::IsNullOrWhiteSpace([string]$item.LinkType)) {
			Remove-Item -Path $item.FullName -Recurse -Force -ErrorAction SilentlyContinue
			$removedCurrent = -not (Test-Path -Path $item.FullName)
		}
		elseif ($item.PSIsContainer) {
			$hasContent = (Get-ChildItem -Path $item.FullName -Force -ErrorAction SilentlyContinue | Select-Object -First 1) -ne $null
			if (-not $hasContent) {
				Remove-Item -Path $item.FullName -Recurse -Force -ErrorAction SilentlyContinue
				$removedCurrent = -not (Test-Path -Path $item.FullName)
			}
			else {
				$backupName = [string]$item.Name
				$prefix = '.dotfiles-prelink-'
				$prefixIdx = $backupName.LastIndexOf($prefix, [System.StringComparison]::OrdinalIgnoreCase)
				$baseFolderName = if ($prefixIdx -gt 0) { $backupName.Substring(0, $prefixIdx) } else { '' }
				if ([string]::IsNullOrWhiteSpace($baseFolderName)) {
					Write-Warning ("Unable to infer original folder for backup '{0}'. Keeping as-is." -f $item.FullName)
				}
				else {
					$sourcePath = Join-Path $UserProfilePath $baseFolderName
					if (-not (Test-Path -Path $sourcePath)) {
						Write-Warning ("Active profile folder '{0}' not found for backup '{1}'. Keeping as-is." -f $sourcePath, $item.FullName)
					}
					else {
						$sourceItem = Get-Item -Path $sourcePath -Force -ErrorAction SilentlyContinue
						$isSourceLink = ($null -ne $sourceItem -and ($sourceItem.LinkType -eq 'SymbolicLink' -or $sourceItem.LinkType -eq 'Junction'))
						if (-not $isSourceLink -or $null -eq $sourceItem.Target) {
							Write-Warning ("Active profile folder '{0}' is not a link/junction. Keeping backup '{1}'." -f $sourcePath, $item.FullName)
						}
						else {
							$targetPath = Normalize-WindowsPath -PathValue ([string]($sourceItem.Target | Select-Object -First 1))
							if ([string]::IsNullOrWhiteSpace($targetPath)) {
								Write-Warning ("Unable to resolve link target for '{0}'. Keeping backup '{1}'." -f $sourcePath, $item.FullName)
							}
							else {
								New-Item -ItemType Directory -Path $targetPath -Force | Out-Null
								Write-Output ("Migrating backup content: {0} -> {1}" -f $item.FullName, $targetPath)
								$roboLog = Join-Path $Env:TEMP ("dotfiles-prelink-restore-{0}-{1}.log" -f $baseFolderName.ToLowerInvariant(), (Get-Date -Format 'yyyyMMdd-HHmmss'))
								$null = & robocopy $item.FullName $targetPath /E /COPY:DAT /DCOPY:DAT /R:1 /W:1 /XJ /NFL /NDL /NJH /NJS /NP /LOG:$roboLog
								if ($LASTEXITCODE -le 7) {
									Remove-Item -Path $item.FullName -Recurse -Force -ErrorAction SilentlyContinue
									$removedCurrent = -not (Test-Path -Path $item.FullName)
									if ($removedCurrent) {
										$migrated++
									}
									else {
										Write-Warning ("Content migrated but failed to remove backup folder: {0}" -f $item.FullName)
									}
								}
								else {
									Write-Warning ("Failed to migrate backup '{0}' (robocopy exit={1}). Log: {2}" -f $item.FullName, $LASTEXITCODE, $roboLog)
								}
							}
						}
					}
				}
			}
		}

		if ($removedCurrent) {
			$removed++
			if ($item.PSIsContainer -and [string]::IsNullOrWhiteSpace([string]$item.LinkType)) {
				Write-Output ("Removed prelink backup after migration: {0}" -f $item.FullName)
			}
			else {
				Write-Output ("Removed stale prelink backup: {0}" -f $item.FullName)
			}
		}
		else {
			$kept++
		}
	}

	if (($removed + $kept) -gt 0) {
		Write-Output ("Prelink backup reconciliation summary: removed={0}, migrated={1}, kept={2}" -f $removed, $migrated, $kept)
	}
}

function Resolve-WindowsOneDriveLayout {
	param (
		[string]$UserProfilePath,
		[string]$UserName,
		[bool]$AutoMigrate = $true
	)

	$configuredRoot = Get-OneDriveConfiguredRoot
	$requestedRoot = Normalize-WindowsPath -PathValue $Env:DOTFILES_ONEDRIVE_ROOT_WINDOWS
	$defaultRoot = Normalize-WindowsPath -PathValue (Join-Path $UserProfilePath 'OneDrive')
	if (-not [string]::IsNullOrWhiteSpace($requestedRoot) -and -not (Test-WindowsAbsolutePath -PathValue $requestedRoot)) {
		throw "Configured OneDrive root must be absolute (received: '$requestedRoot')."
	}
	if ([string]::IsNullOrWhiteSpace($requestedRoot)) {
		$requestedRoot = if (-not [string]::IsNullOrWhiteSpace($configuredRoot)) { $configuredRoot } else { $defaultRoot }
	}

	if ([string]::IsNullOrWhiteSpace($configuredRoot)) {
		$desiredBootstrapRoot = if ([string]::IsNullOrWhiteSpace($requestedRoot)) { $defaultRoot } else { $requestedRoot }
		$oneDriveExe = Get-OneDriveExePath
		if ([string]::IsNullOrWhiteSpace($oneDriveExe)) {
			Write-Warning "OneDrive is not installed but OneDrive mode is enabled."
			$typedRoot = Read-Host -Prompt ("OneDrive base path to use/install (ABS) [{0}]" -f $desiredBootstrapRoot)
			if (-not [string]::IsNullOrWhiteSpace($typedRoot)) {
				$desiredBootstrapRoot = Normalize-WindowsPath -PathValue $typedRoot
			}
			if (-not (Test-WindowsAbsolutePath -PathValue $desiredBootstrapRoot)) {
				throw "OneDrive base path must be absolute (received: '$desiredBootstrapRoot')."
			}
			$requestedRoot = $desiredBootstrapRoot

			if (-not (Install-OneDriveClient)) {
				throw "Failed to install OneDrive automatically. Install Microsoft.OneDrive and rerun bootstrap."
			}
		}
		else {
			Write-Warning "OneDrive is installed but no configured account root was found."
		}

		# Best-effort pre-seed: when desired root differs from default root and default root does not
		# exist yet, create junction so first OneDrive bootstrap can target desired storage location.
		if (-not $requestedRoot.Equals($defaultRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
			New-Item -ItemType Directory -Path $requestedRoot -Force | Out-Null
			if (-not (Test-Path -Path $defaultRoot)) {
				New-Item -ItemType Junction -Path $defaultRoot -Target $requestedRoot -Force | Out-Null
				Write-Host ("Created pre-seed junction for initial OneDrive setup: {0} -> {1}" -f $defaultRoot, $requestedRoot)
			}
			else {
				Write-Warning ("Default OneDrive path already exists ({0}). Initial setup may require selecting path manually." -f $defaultRoot)
			}
		}

		if (-not (Start-OneDriveClient)) {
			throw "Unable to start OneDrive client after install/config step."
		}

		Write-Warning "Complete OneDrive sign-in/setup now."
		$setupDone = Read-YesNoPrompt -Prompt 'Concluiu o login/configuracao inicial do OneDrive?' -DefaultNo $false
		if (-not $setupDone) {
			throw "OneDrive setup was not completed. Bootstrap cannot continue with OneDrive links."
		}

		$configuredRoot = Get-OneDriveConfiguredRoot
		if ([string]::IsNullOrWhiteSpace($configuredRoot)) {
			throw "OneDrive account root still not detected after setup. Open OneDrive, finish setup and rerun bootstrap."
		}
	}

	Write-Host ("OneDrive current configured root: {0}" -f $configuredRoot)
	$shouldPromptChange = $true
	if ($RefreshDotfiles -and $configuredRoot.Equals($requestedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
		$shouldPromptChange = $false
	}

	if ($shouldPromptChange) {
		$defaultNo = $configuredRoot.Equals($requestedRoot, [System.StringComparison]::OrdinalIgnoreCase)
		$changeRoot = Read-YesNoPrompt -Prompt 'Deseja mover/alterar o path base do OneDrive para este bootstrap?' -DefaultNo $defaultNo
		if ($changeRoot) {
			$typedRoot = Read-Host -Prompt ("Novo path base OneDrive (ABS) [{0}]" -f $requestedRoot)
			if (-not [string]::IsNullOrWhiteSpace($typedRoot)) {
				$requestedRoot = Normalize-WindowsPath -PathValue $typedRoot
			}
			if (-not (Test-WindowsAbsolutePath -PathValue $requestedRoot)) {
				throw "OneDrive new base path must be absolute (received: '$requestedRoot')."
			}

			if (-not $configuredRoot.Equals($requestedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
				if ($AutoMigrate) {
					$requestedRoot = Invoke-OneDriveJunctionMigration -CurrentRoot $configuredRoot -DesiredRoot $requestedRoot
				}
				else {
					Write-Warning "Automatic OneDrive migration disabled by config; keeping current configured root."
					$requestedRoot = $configuredRoot
				}
			}
		}
		else {
			$requestedRoot = $configuredRoot
		}
	}
	else {
		$requestedRoot = $configuredRoot
	}

	$resolvedRoot = $requestedRoot

	$clientsHint = if ([string]::IsNullOrWhiteSpace($Env:DOTFILES_ONEDRIVE_CLIENTS_PATH_WINDOWS)) {
		if ([string]::IsNullOrWhiteSpace($Env:DOTFILES_ONEDRIVE_CLIENTS_DIR)) { 'clients' } else { $Env:DOTFILES_ONEDRIVE_CLIENTS_DIR }
	}
	else {
		$Env:DOTFILES_ONEDRIVE_CLIENTS_PATH_WINDOWS
	}
	$resolvedClients = Resolve-WindowsPathWithRoot -RootPath $resolvedRoot -PathValue $clientsHint

	$projectsHint = $null
	if (-not [string]::IsNullOrWhiteSpace($Env:DOTFILES_ONEDRIVE_PROJECTS_PATH)) {
		$projectsHint = $Env:DOTFILES_ONEDRIVE_PROJECTS_PATH
	}
	elseif (-not [string]::IsNullOrWhiteSpace($Env:DOTFILES_ONEDRIVE_PROJECTS_DIR_WINDOWS)) {
		$projectsHint = $Env:DOTFILES_ONEDRIVE_PROJECTS_DIR_WINDOWS
	}
	elseif (-not [string]::IsNullOrWhiteSpace($Env:DOTFILES_ONEDRIVE_PROJECTS_DIR)) {
		$projectsHint = $Env:DOTFILES_ONEDRIVE_PROJECTS_DIR
	}
	else {
		$projectsHint = Join-Path $resolvedClients ("{0}\projects" -f $UserName)
	}
	$resolvedProjects = Resolve-WindowsPathWithRoot -RootPath $resolvedRoot -PathValue $projectsHint

	return [ordered]@{
		root = $resolvedRoot
		clients = $resolvedClients
		projects = $resolvedProjects
	}
}

function Ensure-OneDriveLayoutPaths {
	param ([hashtable]$Layout)

	$requiredPaths = @(
		(Join-Path $Layout.root 'bin'),
		(Join-Path $Layout.root 'etc'),
		$Layout.clients,
		$Layout.projects
	)
	foreach ($path in ($requiredPaths | Select-Object -Unique)) {
		if (-not (Test-Path -Path $path -PathType Container)) {
			New-Item -ItemType Directory -Path $path -Force | Out-Null
		}
	}
}

function Ensure-LocalProfilePaths {
	param ([hashtable]$LinkLayout)

	$localPaths = @(
		$LinkLayout.profileBin,
		$LinkLayout.profileEtc,
		$LinkLayout.profileClients,
		$LinkLayout.profileProjects
	)
	foreach ($path in ($localPaths | Select-Object -Unique)) {
		if (-not (Test-Path -Path $path -PathType Container)) {
			New-Item -ItemType Directory -Path $path -Force | Out-Null
		}
	}
}

function Test-OneDriveLayoutHealth {
	param (
		[bool]$OneDriveEnabled,
		[hashtable]$OneDriveLayout,
		[hashtable]$LinkLayout,
		[string]$UserProfilePath
	)

	$state = [ordered]@{ ok = $true }
	function Write-LayoutResult {
		param ([string]$Label, [bool]$Success, [string]$Detail)
		$prefix = if ($Success) { '[SUCCESS]' } else { '[FAIL]' }
		$color = if ($Success) { 'Green' } else { 'Red' }
		Write-Host "$prefix $Label - $Detail" -ForegroundColor $color
		if (-not $Success) { $state.ok = $false }
	}

	if ($OneDriveEnabled) {
		$configuredRoot = Get-OneDriveConfiguredRoot
		if ([string]::IsNullOrWhiteSpace($configuredRoot)) {
			Write-LayoutResult -Label 'OneDrive account root' -Success $false -Detail 'OneDrive account/root not detected in registry.'
		}
		else {
			Write-LayoutResult -Label 'OneDrive account root' -Success $true -Detail $configuredRoot
		}

		foreach ($name in @('root', 'clients', 'projects')) {
			$path = [string]$OneDriveLayout[$name]
			Write-LayoutResult -Label "OneDrive path $name" -Success (Test-Path -Path $path -PathType Container) -Detail $path
		}
	}

	$linkPairs = @(
		@{ from = $LinkLayout.profileBin; to = if ($OneDriveEnabled) { Join-Path $OneDriveLayout.root 'bin' } else { $LinkLayout.profileBin } },
		@{ from = $LinkLayout.profileEtc; to = if ($OneDriveEnabled) { Join-Path $OneDriveLayout.root 'etc' } else { $LinkLayout.profileEtc } },
		@{ from = $LinkLayout.profileClients; to = if ($OneDriveEnabled) { $OneDriveLayout.clients } else { $LinkLayout.profileClients } },
		@{ from = $LinkLayout.profileProjects; to = if ($OneDriveEnabled) { $OneDriveLayout.projects } else { $LinkLayout.profileProjects } }
	)

	foreach ($pair in $linkPairs) {
		$fromPath = Normalize-WindowsPath -PathValue $pair.from
		if (-not (Test-Path -Path $fromPath)) {
			Write-LayoutResult -Label 'Profile path' -Success $false -Detail "$fromPath missing."
			continue
		}

		$item = Get-Item -Path $fromPath -Force -ErrorAction SilentlyContinue
		if ($OneDriveEnabled) {
			$isLink = ($null -ne $item -and ($item.LinkType -eq 'SymbolicLink' -or $item.LinkType -eq 'Junction'))
			if (-not $isLink) {
				Write-LayoutResult -Label 'Profile symlink' -Success $false -Detail "$fromPath is not a symlink/junction."
				continue
			}
			$target = if ($null -ne $item.Target) { Normalize-WindowsPath -PathValue ([string]($item.Target | Select-Object -First 1)) } else { '' }
			$expected = Normalize-WindowsPath -PathValue $pair.to
			Write-LayoutResult -Label 'Profile symlink target' -Success ($target.Equals($expected, [System.StringComparison]::OrdinalIgnoreCase)) -Detail "$fromPath -> $target (expected $expected)"
		}
		else {
			Write-LayoutResult -Label 'Profile path (local mode)' -Success ($item.PSIsContainer) -Detail "$fromPath exists as local directory."
		}
	}

	$rulesRoot = ''
	if ($OneDriveEnabled -and $null -ne $OneDriveLayout) {
		$rulesRoot = [string]$OneDriveLayout.root
	}
	$profileRules = Get-WindowsProfileFolderLinkRules -UserProfilePath $UserProfilePath -OneDriveRoot $rulesRoot
	$enabledProfileRules = $profileRules | Where-Object { $_.enabled }
	if ($enabledProfileRules.Count -gt 0) {
		if (-not $OneDriveEnabled) {
			Write-LayoutResult -Label 'Profile folder link policy' -Success $false -Detail 'Optional profile links enabled while OneDrive mode is disabled.'
		}
		foreach ($rule in $enabledProfileRules) {
			$sourceExists = Test-Path -Path $rule.source
			if (-not $sourceExists) {
				Write-LayoutResult -Label "Profile folder link ($($rule.label))" -Success $false -Detail "Source path missing: $($rule.source)"
				continue
			}

			$item = Get-Item -Path $rule.source -Force -ErrorAction SilentlyContinue
			$isLink = ($null -ne $item -and ($item.LinkType -eq 'SymbolicLink' -or $item.LinkType -eq 'Junction'))
			if (-not $isLink) {
				Write-LayoutResult -Label "Profile folder link ($($rule.label))" -Success $false -Detail "$($rule.source) is not a symlink/junction."
				continue
			}

			$target = if ($null -ne $item.Target) { Normalize-WindowsPath -PathValue ([string]($item.Target | Select-Object -First 1)) } else { '' }
			$expected = Normalize-WindowsPath -PathValue $rule.target
			Write-LayoutResult -Label "Profile folder target ($($rule.label))" -Success ($target.Equals($expected, [System.StringComparison]::OrdinalIgnoreCase)) -Detail "$($rule.source) -> $target (expected $expected)"
		}
	}

	return [bool]$state.ok
}


#################################################################################
# verify: dotfiles was cloned from github?
#################################################################################
	$DotFilesDirectory = "$Env:USERPROFILE\dotfiles"
	if (!(Test-Path "$DotFilesDirectory")) {
		Write-Host -ForegroundColor red "Folder $Env:USERPROFILE\dotfiles. Did you forgot clone dotfiles?"
		return
	} else {
		. "${DotFilesDirectory}\df\powershell\_functions.ps1"
	}

#################################################################################
# verify: runnning bootstrap on elevated powershell (as admin)?
#################################################################################
	if (! (Test-PowershellElevated)){
		Write-Host -ForegroundColor red "This script must run on elevated powershell (as admin)"
		return
	}

#################################################################################
# verify: really want run bootstrap?
#################################################################################
	Write-Warning "This script will override some of your home files"
	Write-Warning "If you are okay with that complete the sentence below..."

	$Answer = Read-Host -Prompt "MARCO"
	if ($Answer -ne "POLO") {
		Write-Host "At least you have chicken 🐔"
		return
	}

#################################################################################
# bootstrap: symlink to onedrive folders
#################################################################################
$oneDriveEnabled = ConvertTo-BoolFlag -Value $Env:DOTFILES_ONEDRIVE_ENABLED -Default $true
$oneDriveAutoMigrate = ConvertTo-BoolFlag -Value $Env:DOTFILES_ONEDRIVE_AUTO_MIGRATE -Default $true
$linkLayout = Resolve-WindowsLinkLayout -UserProfilePath $Env:USERPROFILE
$oneDriveLayout = $null
try {
	if ($oneDriveEnabled) {
		$oneDriveLayout = Resolve-WindowsOneDriveLayout -UserProfilePath $Env:USERPROFILE -UserName $Env:USERNAME -AutoMigrate:$oneDriveAutoMigrate
		Ensure-OneDriveLayoutPaths -Layout $oneDriveLayout
		$Env:OneDrive = $oneDriveLayout.root

		# Show resolved plan to improve traceability and troubleshooting.
		Write-Output "OneDrive layout resolved:"
		Write-Output (" - root:     {0}" -f $oneDriveLayout.root)
		Write-Output (" - clients:  {0}" -f $oneDriveLayout.clients)
		Write-Output (" - projects: {0}" -f $oneDriveLayout.projects)

		Add-Symlink $linkLayout.profileBin (Join-Path $oneDriveLayout.root 'bin') > $null
		Add-Symlink $linkLayout.profileEtc (Join-Path $oneDriveLayout.root 'etc') > $null
		Add-Symlink $linkLayout.profileClients $oneDriveLayout.clients > $null
		Add-Symlink $linkLayout.profileProjects $oneDriveLayout.projects > $null

		if ($linkLayout.driveEnabled) {
			$drivePairs = @(
				@{ from = $linkLayout.driveBin; to = (Join-Path $oneDriveLayout.root 'bin') },
				@{ from = $linkLayout.driveEtc; to = (Join-Path $oneDriveLayout.root 'etc') },
				@{ from = $linkLayout.driveClients; to = $oneDriveLayout.clients },
				@{ from = $linkLayout.driveProjects; to = $oneDriveLayout.projects }
			)
			foreach ($pair in $drivePairs) {
				$qualifier = Split-Path -Path $pair.from -Qualifier
				$driveRoot = if ([string]::IsNullOrWhiteSpace($qualifier)) { '' } else { "$qualifier\" }
				if (-not [string]::IsNullOrWhiteSpace($driveRoot) -and -not (Test-Path -Path $driveRoot -PathType Container)) {
					Write-Warning "Drive root not found for link '$($pair.from)'. Skipping."
					continue
				}
				Add-Symlink $pair.from $pair.to > $null
			}
		}
		else {
			Write-Output "Drive-root links disabled by config (paths.windows.links_drive_enabled=false)."
		}
	}
	else {
		Write-Output "OneDrive disabled by config (paths.windows.onedrive_enabled=false)."
		Ensure-LocalProfilePaths -LinkLayout $linkLayout
	}

	Invoke-ProfileFoldersToOneDriveLinking -OneDriveEnabled:$oneDriveEnabled -OneDriveLayout $oneDriveLayout -UserProfilePath $Env:USERPROFILE
	Remove-StaleProfileFolderPrelinkBackups -UserProfilePath $Env:USERPROFILE

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
catch {
	throw "Failed to prepare OneDrive/profile paths: $($_.Exception.Message)"
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
	Add-Symlink "$env:USERPROFILE\.ssh\config.local" "$DotFilesDirectory\df\ssh\config.windows" > $null

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

	Write-Output "Running OneDrive/profile link health check..."
	if (!(Test-OneDriveLayoutHealth -OneDriveEnabled:$oneDriveEnabled -OneDriveLayout $oneDriveLayout -LinkLayout $linkLayout -UserProfilePath $Env:USERPROFILE)) {
		throw "OneDrive/profile path validation failed. Review symlink and path output above."
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
