#######################################################################################
# bootstrap-config.ps1
#
# Centralized bootstrap configuration manager.
# - Uses a simple YAML file (local, non-versioned) as single source of truth.
# - Can run guided setup in terminal.
# - Syncs derived files used by existing bootstrap flow:
#   - df/secrets/secrets-ref.yaml
#   - bootstrap/secrets/.env.local.tpl
#   - df/git/.gitconfig.local
#######################################################################################

function Get-BootstrapConfigDefaults {
	$defaults = [ordered]@{}
	$defaults['version'] = '1'
	$defaults['profile.name'] = 'CHANGE_ME'

	$defaults['git.name'] = 'CHANGE_ME'
	$defaults['git.email'] = 'you@example.com'
	$defaults['git.username'] = 'your-github-user'
	$defaults['git.signing_key'] = 'ssh-ed25519 AAAA_REPLACE_WITH_YOUR_PUBLIC_SSH_SIGNING_KEY'

	$defaults['paths.windows.onedrive_enabled'] = 'true'
	$defaults['paths.windows.onedrive_root'] = ''
	$defaults['paths.windows.onedrive_auto_migrate'] = 'true'
	$defaults['paths.windows.onedrive_clients_dir'] = ''
	$defaults['paths.windows.onedrive_projects_dir'] = ''
	$defaults['paths.windows.onedrive_projects_path'] = ''
	$defaults['paths.windows.links_profile_bin'] = '%USERPROFILE%\bin'
	$defaults['paths.windows.links_profile_etc'] = '%USERPROFILE%\etc'
	$defaults['paths.windows.links_profile_clients'] = '%USERPROFILE%\clients'
	$defaults['paths.windows.links_profile_projects'] = '%USERPROFILE%\projects'
	$defaults['paths.windows.links_drive_enabled'] = 'true'
	$defaults['paths.windows.links_drive_bin'] = 'D:\bin'
	$defaults['paths.windows.links_drive_etc'] = 'D:\etc'
	$defaults['paths.windows.links_drive_clients'] = 'D:\clients'
	$defaults['paths.windows.links_drive_projects'] = 'D:\projects'
	$defaults['paths.windows.profile_links_documents_enabled'] = 'false'
	$defaults['paths.windows.profile_links_migrate_content'] = 'true'
	$defaults['paths.windows.profile_links_documents_target'] = 'documents'
	$defaults['paths.windows.profile_links_desktop_enabled'] = 'false'
	$defaults['paths.windows.profile_links_desktop_target'] = 'desktop'
	$defaults['paths.windows.profile_links_downloads_enabled'] = 'false'
	$defaults['paths.windows.profile_links_downloads_target'] = 'downloads'
	$defaults['paths.windows.profile_links_pictures_enabled'] = 'false'
	$defaults['paths.windows.profile_links_pictures_target'] = 'Imagens'
	$defaults['paths.windows.profile_links_videos_enabled'] = 'false'
	$defaults['paths.windows.profile_links_videos_target'] = 'Vídeos'
	$defaults['paths.windows.profile_links_music_enabled'] = 'false'
	$defaults['paths.windows.profile_links_music_target'] = 'Música'
	$defaults['paths.windows.profile_links_contacts_enabled'] = 'false'
	$defaults['paths.windows.profile_links_contacts_target'] = 'documents\profile\contacts'
	$defaults['paths.windows.profile_links_favorites_enabled'] = 'false'
	$defaults['paths.windows.profile_links_favorites_target'] = 'documents\profile\favorites'
	$defaults['paths.windows.profile_links_links_enabled'] = 'false'
	$defaults['paths.windows.profile_links_links_target'] = 'documents\profile\links'
	$defaults['paths.wsl.onedrive_root'] = '/mnt/d/OneDrive'
	$defaults['paths.wsl.onedrive_clients_dir'] = ''
	$defaults['paths.wsl.onedrive_projects_dir'] = ''

	$defaults['bootstrap.add_user.enabled'] = 'false'
	$defaults['bootstrap.add_user.username'] = ''
	$defaults['bootstrap.add_user.password_hash'] = ''

	$defaults['secrets.onepassword_service_account_ref'] = 'op://secrets/dotfiles/1password/service-account'
	$defaults['secrets.github_project_pat_ref'] = 'op://secrets/dotfiles/github/token'
	$defaults['secrets.github_full_access_ref'] = 'op://secrets/github/api/token'
	$defaults['secrets.age_key_ref'] = 'op://secrets/dotfiles/age/age.key'
	return $defaults
}

function Test-WindowsAbsolutePath {
	param ([string]$PathValue)
	if ([string]::IsNullOrWhiteSpace($PathValue)) { return $false }
	return ($PathValue -match '^[A-Za-z]:\\') -or ($PathValue -match '^\\\\')
}

function Test-UnixAbsolutePath {
	param ([string]$PathValue)
	if ([string]::IsNullOrWhiteSpace($PathValue)) { return $false }
	return $PathValue.StartsWith('/')
}

function Resolve-PathWithRoot {
	param (
		[string]$RootPath,
		[string]$PathValue,
		[ValidateSet('windows', 'unix')]
		[string]$Style
	)

	if ([string]::IsNullOrWhiteSpace($PathValue)) { return '' }

	if ($Style -eq 'windows') {
		if (Test-WindowsAbsolutePath -PathValue $PathValue) { return $PathValue }
		if ([string]::IsNullOrWhiteSpace($RootPath)) { return $PathValue }
		$relative = ($PathValue -replace '^[\\/]+', '')
		return (Join-Path $RootPath $relative)
	}

	if (Test-UnixAbsolutePath -PathValue $PathValue) {
		return $PathValue
	}
	if ([string]::IsNullOrWhiteSpace($RootPath)) {
		return ($PathValue -replace '\\', '/')
	}
	$normalizedRoot = $RootPath.TrimEnd('/')
	$normalizedRelative = ($PathValue.TrimStart('/').TrimStart('\') -replace '\\', '/')
	return "$normalizedRoot/$normalizedRelative"
}

function ConvertTo-BoolString {
	param (
		[string]$Value,
		[string]$Default = 'false'
	)

	if ([string]::IsNullOrWhiteSpace($Value)) {
		return $Default
	}
	switch -Regex ($Value.Trim().ToLowerInvariant()) {
		'^(1|true|yes|y|sim|s)$' { return 'true' }
		'^(0|false|no|n|nao|não)$' { return 'false' }
		default { return $Default }
	}
}

function Expand-WindowsPathValue {
	param ([string]$PathValue)
	if ([string]::IsNullOrWhiteSpace($PathValue)) { return '' }
	$expanded = [Environment]::ExpandEnvironmentVariables($PathValue)
	if ($expanded -match '%[^%]+%') {
		throw "Unresolved Windows environment token in path '$PathValue'. Corrija para variaveis validas (ex: %USERPROFILE%)."
	}
	return $expanded
}

function Convert-SimpleYamlScalar {
	param ([string]$RawValue)

	$v = $RawValue.Trim()
	if ($v -match "^'(.*)'$") { return $matches[1] }
	if ($v -match '^"(.*)"$') {
		# Minimal unescape for double-quoted values used in this repo:
		# - \\\\ => \
		# - \"  => "
		$unescaped = $matches[1]
		$unescaped = $unescaped.Replace('\\', '\')
		$unescaped = $unescaped.Replace('\"', '"')
		return $unescaped
	}
	if ($v -ieq 'true') { return 'true' }
	if ($v -ieq 'false') { return 'false' }
	if ($v -ieq 'null') { return '' }
	return $v
}

function Read-SimpleYamlAsPathMap {
	param ([string]$Path)

	$map = [ordered]@{}
	if (!(Test-Path -Path $Path -PathType Leaf)) {
		return $map
	}

	$stack = New-Object System.Collections.Generic.List[string]
	foreach ($rawLine in (Get-Content -Path $Path -ErrorAction SilentlyContinue)) {
		$line = ($rawLine -replace "`t", '  ')
		if ([string]::IsNullOrWhiteSpace($line) -or $line -match '^\s*#') {
			continue
		}
		if ($line -notmatch '^(\s*)([A-Za-z0-9_-]+):\s*(.*)$') {
			continue
		}

		$indentLen = $matches[1].Length
		if (($indentLen % 2) -ne 0) {
			continue
		}
		$level = [int]($indentLen / 2)
		$key = $matches[2]
		$valuePart = $matches[3].Trim()

		while ($stack.Count -gt $level) {
			$stack.RemoveAt($stack.Count - 1)
		}
		if ($stack.Count -eq $level) {
			$stack.Add($key)
		}
		else {
			continue
		}

		if ($valuePart -ne '') {
			$pathKey = ($stack -join '.')
			$map[$pathKey] = (Convert-SimpleYamlScalar -RawValue $valuePart)
		}
	}

	return $map
}

function Merge-BootstrapConfigWithDefaults {
	param ([hashtable]$ConfigMap)

	$merged = [ordered]@{}
	$defaults = Get-BootstrapConfigDefaults
	foreach ($k in $defaults.Keys) {
		if ($ConfigMap.Contains($k)) {
			$merged[$k] = [string]$ConfigMap[$k]
		}
		else {
			$merged[$k] = [string]$defaults[$k]
		}
	}

	# Normalize legacy over-escaped windows paths (e.g. D:\\\\bin) to canonical text
	# representation (e.g. D:\\bin in YAML, D:\bin in memory).
	$windowsPathKeys = @(
		'paths.windows.onedrive_root',
		'paths.windows.onedrive_clients_dir',
		'paths.windows.onedrive_projects_dir',
		'paths.windows.onedrive_projects_path',
		'paths.windows.links_profile_bin',
		'paths.windows.links_profile_etc',
		'paths.windows.links_profile_clients',
		'paths.windows.links_profile_projects',
		'paths.windows.links_drive_bin',
		'paths.windows.links_drive_etc',
		'paths.windows.links_drive_clients',
		'paths.windows.links_drive_projects',
		'paths.windows.profile_links_documents_target',
		'paths.windows.profile_links_desktop_target',
		'paths.windows.profile_links_downloads_target',
		'paths.windows.profile_links_pictures_target',
		'paths.windows.profile_links_videos_target',
		'paths.windows.profile_links_music_target',
		'paths.windows.profile_links_contacts_target',
		'paths.windows.profile_links_favorites_target',
		'paths.windows.profile_links_links_target'
	)
	foreach ($pathKey in $windowsPathKeys) {
		if ($merged.Contains($pathKey)) {
			$merged[$pathKey] = Normalize-WindowsPathTextForConfig -Value ([string]$merged[$pathKey])
		}
	}

	return $merged
}

function Normalize-WindowsPathTextForConfig {
	param ([string]$Value)

	if ([string]::IsNullOrWhiteSpace($Value)) { return '' }
	$normalized = $Value
	$hasUncPrefix = $normalized.StartsWith('\\')

	while ($normalized.Contains('\\')) {
		$next = $normalized.Replace('\\', '\')
		if ($next -eq $normalized) {
			break
		}
		$normalized = $next
	}

	if ($hasUncPrefix -and -not $normalized.StartsWith('\\')) {
		$normalized = "\" + $normalized
	}
	return $normalized
}

function Escape-YamlDoubleQuotedValue {
	param ([string]$Value)
	$escaped = if ([string]::IsNullOrEmpty($Value)) { '' } else { $Value }
	$escaped = $escaped.Replace('\', '\\')
	$escaped = $escaped.Replace('"', '\"')
	return $escaped
}

function Get-CanonicalWindowsPathText {
	param ([string]$PathValue)

	$normalized = Normalize-WindowsPathTextForConfig -Value $PathValue
	if ([string]::IsNullOrWhiteSpace($normalized)) { return '' }

	$candidate = $normalized
	$suffix = New-Object System.Collections.Generic.List[string]

	while (-not [string]::IsNullOrWhiteSpace($candidate) -and -not (Test-Path -LiteralPath $candidate)) {
		$leaf = Split-Path -Path $candidate -Leaf
		$parent = Split-Path -Path $candidate -Parent
		if ([string]::IsNullOrWhiteSpace($parent) -or $parent -eq $candidate) {
			return $normalized
		}
		$suffix.Insert(0, $leaf)
		$candidate = $parent
	}

	if ([string]::IsNullOrWhiteSpace($candidate) -or -not (Test-Path -LiteralPath $candidate)) {
		return $normalized
	}

	try {
		$resolved = (Get-Item -LiteralPath $candidate -Force).FullName
	}
	catch {
		return $normalized
	}

	foreach ($segment in $suffix) {
		$resolved = Join-Path $resolved $segment
	}

	return (Normalize-WindowsPathTextForConfig -Value $resolved)
}

function Convert-ConfigPathValueToPreferredAbsolute {
	param (
		[string]$Value,
		[string]$RootPath,
		[ValidateSet('windows', 'unix')]
		[string]$Style
	)

	if ([string]::IsNullOrWhiteSpace($Value)) { return '' }

	if ($Style -eq 'windows') {
		$expanded = Expand-WindowsPathValue -PathValue $Value
		$resolved = Resolve-PathWithRoot -RootPath $RootPath -PathValue $expanded -Style windows
		return (Get-CanonicalWindowsPathText -PathValue $resolved)
	}

	return (Resolve-PathWithRoot -RootPath $RootPath -PathValue $Value -Style unix)
}

function Convert-BootstrapConfigToPreferredAbsolutePaths {
	param ([hashtable]$Config)

	$normalized = [ordered]@{}
	foreach ($key in $Config.Keys) {
		$normalized[$key] = [string]$Config[$key]
	}

	$windowsRoot = Convert-ConfigPathValueToPreferredAbsolute -Value $normalized['paths.windows.onedrive_root'] -RootPath '' -Style windows
	$normalized['paths.windows.onedrive_root'] = $windowsRoot

	$normalized['paths.windows.onedrive_clients_dir'] = Convert-ConfigPathValueToPreferredAbsolute -Value $normalized['paths.windows.onedrive_clients_dir'] -RootPath $windowsRoot -Style windows
	$windowsProjectsDir = Convert-ConfigPathValueToPreferredAbsolute -Value $normalized['paths.windows.onedrive_projects_dir'] -RootPath $windowsRoot -Style windows
	$windowsProjectsPath = Convert-ConfigPathValueToPreferredAbsolute -Value $normalized['paths.windows.onedrive_projects_path'] -RootPath $windowsRoot -Style windows
	if ([string]::IsNullOrWhiteSpace($windowsProjectsPath) -and -not [string]::IsNullOrWhiteSpace($windowsProjectsDir)) {
		$windowsProjectsPath = $windowsProjectsDir
		$windowsProjectsDir = ''
	}
	elseif (-not [string]::IsNullOrWhiteSpace($windowsProjectsPath)) {
		$windowsProjectsDir = ''
	}
	$normalized['paths.windows.onedrive_projects_dir'] = $windowsProjectsDir
	$normalized['paths.windows.onedrive_projects_path'] = $windowsProjectsPath

	foreach ($key in @(
			'paths.windows.profile_links_documents_target',
			'paths.windows.profile_links_desktop_target',
			'paths.windows.profile_links_downloads_target',
			'paths.windows.profile_links_pictures_target',
			'paths.windows.profile_links_videos_target',
			'paths.windows.profile_links_music_target',
			'paths.windows.profile_links_contacts_target',
			'paths.windows.profile_links_favorites_target',
			'paths.windows.profile_links_links_target'
		)) {
		$normalized[$key] = Convert-ConfigPathValueToPreferredAbsolute -Value $normalized[$key] -RootPath $windowsRoot -Style windows
	}

	foreach ($key in @(
			'paths.windows.links_profile_bin',
			'paths.windows.links_profile_etc',
			'paths.windows.links_profile_clients',
			'paths.windows.links_profile_projects',
			'paths.windows.links_drive_bin',
			'paths.windows.links_drive_etc',
			'paths.windows.links_drive_clients',
			'paths.windows.links_drive_projects'
		)) {
		$normalized[$key] = Convert-ConfigPathValueToPreferredAbsolute -Value $normalized[$key] -RootPath '' -Style windows
	}

	$wslRoot = Convert-ConfigPathValueToPreferredAbsolute -Value $normalized['paths.wsl.onedrive_root'] -RootPath '' -Style unix
	$normalized['paths.wsl.onedrive_root'] = $wslRoot

	foreach ($key in @(
			'paths.wsl.onedrive_clients_dir',
			'paths.wsl.onedrive_projects_dir'
		)) {
		$normalized[$key] = Convert-ConfigPathValueToPreferredAbsolute -Value $normalized[$key] -RootPath $wslRoot -Style unix
	}

	return $normalized
}

function Test-BootstrapConfigMapsEqual {
	param (
		[hashtable]$Left,
		[hashtable]$Right
	)

	if ($Left.Count -ne $Right.Count) { return $false }
	foreach ($key in $Left.Keys) {
		if (-not $Right.Contains($key)) { return $false }
		if ([string]$Left[$key] -cne [string]$Right[$key]) { return $false }
	}
	return $true
}

function Write-BootstrapConfigPathPreferenceWarnings {
	param ([hashtable]$Config)

	$relativeEntries = New-Object System.Collections.Generic.List[string]

	foreach ($key in @(
			'paths.windows.onedrive_clients_dir',
			'paths.windows.onedrive_projects_dir',
			'paths.windows.onedrive_projects_path',
			'paths.windows.links_profile_bin',
			'paths.windows.links_profile_etc',
			'paths.windows.links_profile_clients',
			'paths.windows.links_profile_projects',
			'paths.windows.links_drive_bin',
			'paths.windows.links_drive_etc',
			'paths.windows.links_drive_clients',
			'paths.windows.links_drive_projects',
			'paths.windows.profile_links_documents_target',
			'paths.windows.profile_links_desktop_target',
			'paths.windows.profile_links_downloads_target',
			'paths.windows.profile_links_pictures_target',
			'paths.windows.profile_links_videos_target',
			'paths.windows.profile_links_music_target',
			'paths.windows.profile_links_contacts_target',
			'paths.windows.profile_links_favorites_target',
			'paths.windows.profile_links_links_target'
		)) {
		$value = [string]$Config[$key]
		if (-not [string]::IsNullOrWhiteSpace($value) -and -not (Test-WindowsAbsolutePath -PathValue $value)) {
			$relativeEntries.Add(("{0} = {1}" -f $key, $value))
		}
	}

	foreach ($key in @(
			'paths.wsl.onedrive_clients_dir',
			'paths.wsl.onedrive_projects_dir'
		)) {
		$value = [string]$Config[$key]
		if (-not [string]::IsNullOrWhiteSpace($value) -and -not (Test-UnixAbsolutePath -PathValue $value)) {
			$relativeEntries.Add(("{0} = {1}" -f $key, $value))
		}
	}

	if ($relativeEntries.Count -eq 0) { return }

	Write-Warning 'Ainda existem caminhos relativos no bootstrap/user-config.yaml. O padrao recomendado agora e usar caminhos absolutos e canonicos.'
	Write-Host 'Riscos de manter relativo, alias ou symlink como fonte de verdade:'
	Write-Host ' - o destino final passa a depender de outra base implicita'
	Write-Host ' - mudar a root pode redirecionar varios links sem ficar obvio na config'
	Write-Host ' - symlinks/atalhos podem mascarar drift e apontar para destinos antigos'
	Write-Host ' - variaveis de ambiente exigem expansao extra e falham se houver typo'
	Write-Host ' - existe um pequeno custo extra de resolucao a cada bootstrap; o maior ganho do absoluto e previsibilidade'
	Write-Host 'Campos que ainda merecem ajuste:'
	foreach ($entry in $relativeEntries) {
		Write-Host (" - {0}" -f $entry)
	}
}

function Write-BootstrapConfigYaml {
	param (
		[string]$Path,
		[hashtable]$Config
	)

	$templatePath = Join-Path (Split-Path -Path $Path -Parent) 'user-config.yaml.tpl'
	if (!(Test-Path -Path $templatePath -PathType Leaf)) {
		throw "Config template not found: $templatePath"
	}

	$relativeTargetBaseConfigured = [string]$Config['paths.windows.onedrive_root']
	$relativeTargetBaseForPath = if ([string]::IsNullOrWhiteSpace($relativeTargetBaseConfigured)) { '%USERPROFILE%\OneDrive' } else { $relativeTargetBaseConfigured }
	$relativeTargetBaseHint = if ([string]::IsNullOrWhiteSpace($relativeTargetBaseConfigured)) { 'AUTO (registro OneDrive -> env OneDrive -> %USERPROFILE%\OneDrive)' } else { $relativeTargetBaseConfigured }

	$documentsTargetValue = if ([string]::IsNullOrWhiteSpace([string]$Config['paths.windows.profile_links_documents_target'])) { 'documents' } else { [string]$Config['paths.windows.profile_links_documents_target'] }
	$desktopTargetValue = if ([string]::IsNullOrWhiteSpace([string]$Config['paths.windows.profile_links_desktop_target'])) { 'desktop' } else { [string]$Config['paths.windows.profile_links_desktop_target'] }
	$downloadsTargetValue = if ([string]::IsNullOrWhiteSpace([string]$Config['paths.windows.profile_links_downloads_target'])) { 'downloads' } else { [string]$Config['paths.windows.profile_links_downloads_target'] }
	$picturesTargetValue = if ([string]::IsNullOrWhiteSpace([string]$Config['paths.windows.profile_links_pictures_target'])) { 'Imagens' } else { [string]$Config['paths.windows.profile_links_pictures_target'] }
	$videosTargetValue = if ([string]::IsNullOrWhiteSpace([string]$Config['paths.windows.profile_links_videos_target'])) { 'Vídeos' } else { [string]$Config['paths.windows.profile_links_videos_target'] }
	$musicTargetValue = if ([string]::IsNullOrWhiteSpace([string]$Config['paths.windows.profile_links_music_target'])) { 'Música' } else { [string]$Config['paths.windows.profile_links_music_target'] }
	$contactsTargetValue = if ([string]::IsNullOrWhiteSpace([string]$Config['paths.windows.profile_links_contacts_target'])) { 'documents\profile\contacts' } else { [string]$Config['paths.windows.profile_links_contacts_target'] }
	$favoritesTargetValue = if ([string]::IsNullOrWhiteSpace([string]$Config['paths.windows.profile_links_favorites_target'])) { 'documents\profile\favorites' } else { [string]$Config['paths.windows.profile_links_favorites_target'] }
	$linksTargetValue = if ([string]::IsNullOrWhiteSpace([string]$Config['paths.windows.profile_links_links_target'])) { 'documents\profile\links' } else { [string]$Config['paths.windows.profile_links_links_target'] }

	$documentsTargetPreview = Resolve-PathWithRoot -RootPath $relativeTargetBaseForPath -PathValue $documentsTargetValue -Style windows
	$desktopTargetPreview = Resolve-PathWithRoot -RootPath $relativeTargetBaseForPath -PathValue $desktopTargetValue -Style windows
	$downloadsTargetPreview = Resolve-PathWithRoot -RootPath $relativeTargetBaseForPath -PathValue $downloadsTargetValue -Style windows
	$picturesTargetPreview = Resolve-PathWithRoot -RootPath $relativeTargetBaseForPath -PathValue $picturesTargetValue -Style windows
	$videosTargetPreview = Resolve-PathWithRoot -RootPath $relativeTargetBaseForPath -PathValue $videosTargetValue -Style windows
	$musicTargetPreview = Resolve-PathWithRoot -RootPath $relativeTargetBaseForPath -PathValue $musicTargetValue -Style windows
	$contactsTargetPreview = Resolve-PathWithRoot -RootPath $relativeTargetBaseForPath -PathValue $contactsTargetValue -Style windows
	$favoritesTargetPreview = Resolve-PathWithRoot -RootPath $relativeTargetBaseForPath -PathValue $favoritesTargetValue -Style windows
	$linksTargetPreview = Resolve-PathWithRoot -RootPath $relativeTargetBaseForPath -PathValue $linksTargetValue -Style windows

	$yaml = Get-Content -Raw -Path $templatePath
	$replacements = [ordered]@{
		'@@VERSION@@' = '1'
		'@@PROFILE_NAME@@' = Escape-YamlDoubleQuotedValue $Config['profile.name']
		'@@GIT_NAME@@' = Escape-YamlDoubleQuotedValue $Config['git.name']
		'@@GIT_EMAIL@@' = Escape-YamlDoubleQuotedValue $Config['git.email']
		'@@GIT_USERNAME@@' = Escape-YamlDoubleQuotedValue $Config['git.username']
		'@@GIT_SIGNING_KEY@@' = Escape-YamlDoubleQuotedValue $Config['git.signing_key']
		'@@WINDOWS_ONEDRIVE_ENABLED@@' = ConvertTo-BoolString -Value $Config['paths.windows.onedrive_enabled'] -Default 'true'
		'@@WINDOWS_ONEDRIVE_ROOT@@' = Escape-YamlDoubleQuotedValue $Config['paths.windows.onedrive_root']
		'@@WINDOWS_ONEDRIVE_AUTO_MIGRATE@@' = ConvertTo-BoolString -Value $Config['paths.windows.onedrive_auto_migrate'] -Default 'true'
		'@@WINDOWS_ONEDRIVE_CLIENTS_DIR@@' = Escape-YamlDoubleQuotedValue $Config['paths.windows.onedrive_clients_dir']
		'@@WINDOWS_ONEDRIVE_PROJECTS_DIR@@' = Escape-YamlDoubleQuotedValue $Config['paths.windows.onedrive_projects_dir']
		'@@WINDOWS_ONEDRIVE_PROJECTS_PATH@@' = Escape-YamlDoubleQuotedValue $Config['paths.windows.onedrive_projects_path']
		'@@WINDOWS_LINKS_PROFILE_BIN@@' = Escape-YamlDoubleQuotedValue $Config['paths.windows.links_profile_bin']
		'@@WINDOWS_LINKS_PROFILE_ETC@@' = Escape-YamlDoubleQuotedValue $Config['paths.windows.links_profile_etc']
		'@@WINDOWS_LINKS_PROFILE_CLIENTS@@' = Escape-YamlDoubleQuotedValue $Config['paths.windows.links_profile_clients']
		'@@WINDOWS_LINKS_PROFILE_PROJECTS@@' = Escape-YamlDoubleQuotedValue $Config['paths.windows.links_profile_projects']
		'@@WINDOWS_LINKS_DRIVE_ENABLED@@' = ConvertTo-BoolString -Value $Config['paths.windows.links_drive_enabled'] -Default 'true'
		'@@WINDOWS_LINKS_DRIVE_BIN@@' = Escape-YamlDoubleQuotedValue $Config['paths.windows.links_drive_bin']
		'@@WINDOWS_LINKS_DRIVE_ETC@@' = Escape-YamlDoubleQuotedValue $Config['paths.windows.links_drive_etc']
		'@@WINDOWS_LINKS_DRIVE_CLIENTS@@' = Escape-YamlDoubleQuotedValue $Config['paths.windows.links_drive_clients']
		'@@WINDOWS_LINKS_DRIVE_PROJECTS@@' = Escape-YamlDoubleQuotedValue $Config['paths.windows.links_drive_projects']
		'@@RELATIVE_TARGET_BASE_HINT@@' = Escape-YamlDoubleQuotedValue $relativeTargetBaseHint
		'@@WINDOWS_PROFILE_LINKS_MIGRATE_CONTENT@@' = ConvertTo-BoolString -Value $Config['paths.windows.profile_links_migrate_content'] -Default 'true'
		'@@WINDOWS_PROFILE_LINKS_DOCUMENTS_PREVIEW@@' = Escape-YamlDoubleQuotedValue $documentsTargetPreview
		'@@WINDOWS_PROFILE_LINKS_DOCUMENTS_ENABLED@@' = ConvertTo-BoolString -Value $Config['paths.windows.profile_links_documents_enabled'] -Default 'false'
		'@@WINDOWS_PROFILE_LINKS_DOCUMENTS_TARGET@@' = Escape-YamlDoubleQuotedValue $Config['paths.windows.profile_links_documents_target']
		'@@WINDOWS_PROFILE_LINKS_DESKTOP_PREVIEW@@' = Escape-YamlDoubleQuotedValue $desktopTargetPreview
		'@@WINDOWS_PROFILE_LINKS_DESKTOP_ENABLED@@' = ConvertTo-BoolString -Value $Config['paths.windows.profile_links_desktop_enabled'] -Default 'false'
		'@@WINDOWS_PROFILE_LINKS_DESKTOP_TARGET@@' = Escape-YamlDoubleQuotedValue $Config['paths.windows.profile_links_desktop_target']
		'@@WINDOWS_PROFILE_LINKS_DOWNLOADS_PREVIEW@@' = Escape-YamlDoubleQuotedValue $downloadsTargetPreview
		'@@WINDOWS_PROFILE_LINKS_DOWNLOADS_ENABLED@@' = ConvertTo-BoolString -Value $Config['paths.windows.profile_links_downloads_enabled'] -Default 'false'
		'@@WINDOWS_PROFILE_LINKS_DOWNLOADS_TARGET@@' = Escape-YamlDoubleQuotedValue $Config['paths.windows.profile_links_downloads_target']
		'@@WINDOWS_PROFILE_LINKS_PICTURES_PREVIEW@@' = Escape-YamlDoubleQuotedValue $picturesTargetPreview
		'@@WINDOWS_PROFILE_LINKS_PICTURES_ENABLED@@' = ConvertTo-BoolString -Value $Config['paths.windows.profile_links_pictures_enabled'] -Default 'false'
		'@@WINDOWS_PROFILE_LINKS_PICTURES_TARGET@@' = Escape-YamlDoubleQuotedValue $Config['paths.windows.profile_links_pictures_target']
		'@@WINDOWS_PROFILE_LINKS_VIDEOS_PREVIEW@@' = Escape-YamlDoubleQuotedValue $videosTargetPreview
		'@@WINDOWS_PROFILE_LINKS_VIDEOS_ENABLED@@' = ConvertTo-BoolString -Value $Config['paths.windows.profile_links_videos_enabled'] -Default 'false'
		'@@WINDOWS_PROFILE_LINKS_VIDEOS_TARGET@@' = Escape-YamlDoubleQuotedValue $Config['paths.windows.profile_links_videos_target']
		'@@WINDOWS_PROFILE_LINKS_MUSIC_PREVIEW@@' = Escape-YamlDoubleQuotedValue $musicTargetPreview
		'@@WINDOWS_PROFILE_LINKS_MUSIC_ENABLED@@' = ConvertTo-BoolString -Value $Config['paths.windows.profile_links_music_enabled'] -Default 'false'
		'@@WINDOWS_PROFILE_LINKS_MUSIC_TARGET@@' = Escape-YamlDoubleQuotedValue $Config['paths.windows.profile_links_music_target']
		'@@WINDOWS_PROFILE_LINKS_CONTACTS_PREVIEW@@' = Escape-YamlDoubleQuotedValue $contactsTargetPreview
		'@@WINDOWS_PROFILE_LINKS_CONTACTS_ENABLED@@' = ConvertTo-BoolString -Value $Config['paths.windows.profile_links_contacts_enabled'] -Default 'false'
		'@@WINDOWS_PROFILE_LINKS_CONTACTS_TARGET@@' = Escape-YamlDoubleQuotedValue $Config['paths.windows.profile_links_contacts_target']
		'@@WINDOWS_PROFILE_LINKS_FAVORITES_PREVIEW@@' = Escape-YamlDoubleQuotedValue $favoritesTargetPreview
		'@@WINDOWS_PROFILE_LINKS_FAVORITES_ENABLED@@' = ConvertTo-BoolString -Value $Config['paths.windows.profile_links_favorites_enabled'] -Default 'false'
		'@@WINDOWS_PROFILE_LINKS_FAVORITES_TARGET@@' = Escape-YamlDoubleQuotedValue $Config['paths.windows.profile_links_favorites_target']
		'@@WINDOWS_PROFILE_LINKS_LINKS_PREVIEW@@' = Escape-YamlDoubleQuotedValue $linksTargetPreview
		'@@WINDOWS_PROFILE_LINKS_LINKS_ENABLED@@' = ConvertTo-BoolString -Value $Config['paths.windows.profile_links_links_enabled'] -Default 'false'
		'@@WINDOWS_PROFILE_LINKS_LINKS_TARGET@@' = Escape-YamlDoubleQuotedValue $Config['paths.windows.profile_links_links_target']
		'@@WSL_ONEDRIVE_ROOT@@' = Escape-YamlDoubleQuotedValue $Config['paths.wsl.onedrive_root']
		'@@WSL_ONEDRIVE_CLIENTS_DIR@@' = Escape-YamlDoubleQuotedValue $Config['paths.wsl.onedrive_clients_dir']
		'@@WSL_ONEDRIVE_PROJECTS_DIR@@' = Escape-YamlDoubleQuotedValue $Config['paths.wsl.onedrive_projects_dir']
		'@@BOOTSTRAP_ADD_USER_ENABLED@@' = ($Config['bootstrap.add_user.enabled']).ToLowerInvariant()
		'@@BOOTSTRAP_ADD_USER_USERNAME@@' = Escape-YamlDoubleQuotedValue $Config['bootstrap.add_user.username']
		'@@BOOTSTRAP_ADD_USER_PASSWORD_HASH@@' = Escape-YamlDoubleQuotedValue $Config['bootstrap.add_user.password_hash']
		'@@SECRETS_ONEPASSWORD_SERVICE_ACCOUNT_REF@@' = Escape-YamlDoubleQuotedValue $Config['secrets.onepassword_service_account_ref']
		'@@SECRETS_GITHUB_PROJECT_PAT_REF@@' = Escape-YamlDoubleQuotedValue $Config['secrets.github_project_pat_ref']
		'@@SECRETS_GITHUB_FULL_ACCESS_REF@@' = Escape-YamlDoubleQuotedValue $Config['secrets.github_full_access_ref']
		'@@SECRETS_AGE_KEY_REF@@' = Escape-YamlDoubleQuotedValue $Config['secrets.age_key_ref']
	}

	foreach ($key in $replacements.Keys) {
		$yaml = $yaml.Replace($key, [string]$replacements[$key])
	}

	$targetDir = Split-Path -Path $Path -Parent
	if ($targetDir -and !(Test-Path -Path $targetDir)) {
		New-Item -Path $targetDir -ItemType Directory -Force | Out-Null
	}
	Set-Content -Path $Path -Value $yaml
}

function Test-BootstrapConfigFilled {
	param ([hashtable]$Config)

	$requiredKeys = @(
		'git.name',
		'git.email',
		'git.username',
		'git.signing_key',
		'secrets.onepassword_service_account_ref',
		'secrets.github_project_pat_ref',
		'secrets.github_full_access_ref',
		'secrets.age_key_ref'
	)

	foreach ($k in $requiredKeys) {
		$v = [string]$Config[$k]
		if ([string]::IsNullOrWhiteSpace($v)) {
			return $false
		}
		if ($v -match 'CHANGE_ME|REPLACE_WITH|you@example\.com|your-github-user|AAAA_REPLACE') {
			return $false
		}
	}

	if (($Config['bootstrap.add_user.enabled']).ToLowerInvariant() -eq 'true') {
		if ([string]::IsNullOrWhiteSpace([string]$Config['bootstrap.add_user.username']) -or
			[string]::IsNullOrWhiteSpace([string]$Config['bootstrap.add_user.password_hash'])) {
			return $false
		}
	}

	return $true
}

function Read-ConfigPrompt {
	param (
		[string]$Label,
		[string]$CurrentValue,
		[switch]$AllowEmpty
	)

	$display = if ([string]::IsNullOrWhiteSpace($CurrentValue)) { '(vazio)' } else { $CurrentValue }
	$typed = Read-Host -Prompt "$Label [$display]"
	if ([string]::IsNullOrWhiteSpace($typed)) {
		if ($AllowEmpty) { return '' }
		return $CurrentValue
	}
	return $typed.Trim()
}

function Read-BooleanPrompt {
	param (
		[string]$Label,
		[string]$CurrentValue
	)

	$defaultLabel = if (($CurrentValue).ToLowerInvariant() -eq 'true') { 'Y' } else { 'N' }
	while ($true) {
		$typed = Read-Host -Prompt "$Label (Y/N) [$defaultLabel]"
		if ([string]::IsNullOrWhiteSpace($typed)) {
			return if ($defaultLabel -eq 'Y') { 'true' } else { 'false' }
		}
		switch -Regex ($typed.Trim()) {
			'^(y|yes|s|sim)$' { return 'true' }
			'^(n|no|nao|não)$' { return 'false' }
			default { Write-Host "Resposta inválida. Use Y ou N." }
		}
	}
}

function Invoke-BootstrapConfigWizard {
	param ([hashtable]$Config)

	Write-Host "`nConfiguração guiada do bootstrap (YAML central)."
	Write-Host "Pressione ENTER para manter o valor atual."
	Write-Host "Preferencia atual: caminhos absolutos e canonicos em todos os campos de path."
	Write-Host "Relativos, %USERPROFILE% e symlinks devem ficar como ultimo recurso."

	$Config['profile.name'] = Read-ConfigPrompt -Label 'Nome do perfil local (apelido). EX: work-wsl | desktop-windows' -CurrentValue $Config['profile.name']
	$Config['git.name'] = Read-ConfigPrompt -Label 'Git name (nome exibido nos commits). EX: Pablo Augusto' -CurrentValue $Config['git.name']
	$Config['git.email'] = Read-ConfigPrompt -Label 'Git email (ideal: verificado no GitHub). EX: pablo@pabloaugusto.com' -CurrentValue $Config['git.email']
	$Config['git.username'] = Read-ConfigPrompt -Label 'Git username (login GitHub). EX: pabloaugusto' -CurrentValue $Config['git.username']
	$Config['git.signing_key'] = Read-ConfigPrompt -Label 'Chave publica SSH para assinatura. EX: ssh-ed25519 AAA... user@host' -CurrentValue $Config['git.signing_key']

	$Config['paths.windows.onedrive_enabled'] = Read-BooleanPrompt -Label 'Windows: exigir/usar OneDrive no bootstrap?' -CurrentValue $Config['paths.windows.onedrive_enabled']
	$Config['paths.windows.onedrive_root'] = Read-ConfigPrompt -Label 'Windows OneDrive root canônica (prefira ABS, ex: D:\\onedrive; vazio=detectar/perguntar)' -CurrentValue $Config['paths.windows.onedrive_root'] -AllowEmpty
	$Config['paths.windows.onedrive_auto_migrate'] = Read-BooleanPrompt -Label 'Se root mudar, migrar dados + ajustar OneDrive automaticamente?' -CurrentValue $Config['paths.windows.onedrive_auto_migrate']
	$Config['paths.windows.onedrive_clients_dir'] = Read-ConfigPrompt -Label 'Windows clients dir (prefira ABS, ex: D:\\onedrive\\clients; relativo so em ultimo caso)' -CurrentValue $Config['paths.windows.onedrive_clients_dir'] -AllowEmpty
	$Config['paths.windows.onedrive_projects_dir'] = Read-ConfigPrompt -Label 'Windows projects dir (fallback legado; prefira vazio e usar onedrive_projects_path ABS)' -CurrentValue $Config['paths.windows.onedrive_projects_dir'] -AllowEmpty
	$Config['paths.windows.onedrive_projects_path'] = Read-ConfigPrompt -Label 'Windows projects path (campo preferido; ABS canônico, ex: D:\\onedrive\\clients\\pablo\\projects)' -CurrentValue $Config['paths.windows.onedrive_projects_path'] -AllowEmpty
	$Config['paths.windows.links_profile_bin'] = Read-ConfigPrompt -Label 'Link profile bin (prefira ABS, ex: C:\\Users\\seu-usuario\\bin)' -CurrentValue $Config['paths.windows.links_profile_bin']
	$Config['paths.windows.links_profile_etc'] = Read-ConfigPrompt -Label 'Link profile etc (prefira ABS, ex: C:\\Users\\seu-usuario\\etc)' -CurrentValue $Config['paths.windows.links_profile_etc']
	$Config['paths.windows.links_profile_clients'] = Read-ConfigPrompt -Label 'Link profile clients (prefira ABS, ex: C:\\Users\\seu-usuario\\clients)' -CurrentValue $Config['paths.windows.links_profile_clients']
	$Config['paths.windows.links_profile_projects'] = Read-ConfigPrompt -Label 'Link profile projects (prefira ABS, ex: C:\\Users\\seu-usuario\\projects)' -CurrentValue $Config['paths.windows.links_profile_projects']
	$Config['paths.windows.links_drive_enabled'] = Read-BooleanPrompt -Label 'Criar links adicionais no drive (d:\\* ou equivalente)?' -CurrentValue $Config['paths.windows.links_drive_enabled']
	$Config['paths.windows.links_drive_bin'] = Read-ConfigPrompt -Label 'Link drive bin (ex: D:\\bin)' -CurrentValue $Config['paths.windows.links_drive_bin']
	$Config['paths.windows.links_drive_etc'] = Read-ConfigPrompt -Label 'Link drive etc (ex: D:\\etc)' -CurrentValue $Config['paths.windows.links_drive_etc']
	$Config['paths.windows.links_drive_clients'] = Read-ConfigPrompt -Label 'Link drive clients (ex: D:\\clients)' -CurrentValue $Config['paths.windows.links_drive_clients']
	$Config['paths.windows.links_drive_projects'] = Read-ConfigPrompt -Label 'Link drive projects (ex: D:\\projects)' -CurrentValue $Config['paths.windows.links_drive_projects']
	Write-Host "Links opcionais de pastas padrao do perfil para OneDrive (Documents/Desktop/etc)."
	$wizardRelativeBase = if ([string]::IsNullOrWhiteSpace([string]$Config['paths.windows.onedrive_root'])) { 'AUTO (registro OneDrive -> env OneDrive -> %USERPROFILE%\\OneDrive)' } else { [string]$Config['paths.windows.onedrive_root'] }
	Write-Host "Se ainda usar target relativo, a base sera: $wizardRelativeBase"
	$Config['paths.windows.profile_links_migrate_content'] = Read-BooleanPrompt -Label 'Ao linkar pastas, migrar conteudo atual automaticamente para OneDrive?' -CurrentValue $Config['paths.windows.profile_links_migrate_content']
	$Config['paths.windows.profile_links_documents_enabled'] = Read-BooleanPrompt -Label 'Linkar Documents para OneDrive?' -CurrentValue $Config['paths.windows.profile_links_documents_enabled']
	$Config['paths.windows.profile_links_documents_target'] = Read-ConfigPrompt -Label 'Destino Documents (prefira ABS, ex: D:\\onedrive\\documents; relativo so em ultimo caso)' -CurrentValue $Config['paths.windows.profile_links_documents_target']
	$Config['paths.windows.profile_links_desktop_enabled'] = Read-BooleanPrompt -Label 'Linkar Desktop para OneDrive?' -CurrentValue $Config['paths.windows.profile_links_desktop_enabled']
	$Config['paths.windows.profile_links_desktop_target'] = Read-ConfigPrompt -Label 'Destino Desktop (prefira ABS, ex: D:\\onedrive\\desktop; relativo so em ultimo caso)' -CurrentValue $Config['paths.windows.profile_links_desktop_target']
	$Config['paths.windows.profile_links_downloads_enabled'] = Read-BooleanPrompt -Label 'Linkar Downloads para OneDrive?' -CurrentValue $Config['paths.windows.profile_links_downloads_enabled']
	$Config['paths.windows.profile_links_downloads_target'] = Read-ConfigPrompt -Label 'Destino Downloads (prefira ABS, ex: D:\\onedrive\\downloads; relativo so em ultimo caso)' -CurrentValue $Config['paths.windows.profile_links_downloads_target']
	$Config['paths.windows.profile_links_pictures_enabled'] = Read-BooleanPrompt -Label 'Linkar Pictures para OneDrive?' -CurrentValue $Config['paths.windows.profile_links_pictures_enabled']
	$Config['paths.windows.profile_links_pictures_target'] = Read-ConfigPrompt -Label 'Destino Pictures (prefira ABS, ex: D:\\onedrive\\Imagens; relativo so em ultimo caso)' -CurrentValue $Config['paths.windows.profile_links_pictures_target']
	$Config['paths.windows.profile_links_videos_enabled'] = Read-BooleanPrompt -Label 'Linkar Videos para OneDrive?' -CurrentValue $Config['paths.windows.profile_links_videos_enabled']
	$Config['paths.windows.profile_links_videos_target'] = Read-ConfigPrompt -Label 'Destino Videos (prefira ABS, ex: D:\\onedrive\\Vídeos; relativo so em ultimo caso)' -CurrentValue $Config['paths.windows.profile_links_videos_target']
	$Config['paths.windows.profile_links_music_enabled'] = Read-BooleanPrompt -Label 'Linkar Music para OneDrive?' -CurrentValue $Config['paths.windows.profile_links_music_enabled']
	$Config['paths.windows.profile_links_music_target'] = Read-ConfigPrompt -Label 'Destino Music (prefira ABS, ex: D:\\onedrive\\Música; relativo so em ultimo caso)' -CurrentValue $Config['paths.windows.profile_links_music_target']
	$Config['paths.windows.profile_links_contacts_enabled'] = Read-BooleanPrompt -Label 'Linkar Contacts para OneDrive?' -CurrentValue $Config['paths.windows.profile_links_contacts_enabled']
	$Config['paths.windows.profile_links_contacts_target'] = Read-ConfigPrompt -Label 'Destino Contacts (prefira ABS, ex: D:\\onedrive\\documents\\profile\\contacts; relativo so em ultimo caso)' -CurrentValue $Config['paths.windows.profile_links_contacts_target']
	$Config['paths.windows.profile_links_favorites_enabled'] = Read-BooleanPrompt -Label 'Linkar Favorites para OneDrive?' -CurrentValue $Config['paths.windows.profile_links_favorites_enabled']
	$Config['paths.windows.profile_links_favorites_target'] = Read-ConfigPrompt -Label 'Destino Favorites (prefira ABS, ex: D:\\onedrive\\documents\\profile\\favorites; relativo so em ultimo caso)' -CurrentValue $Config['paths.windows.profile_links_favorites_target']
	$Config['paths.windows.profile_links_links_enabled'] = Read-BooleanPrompt -Label 'Linkar Links para OneDrive?' -CurrentValue $Config['paths.windows.profile_links_links_enabled']
	$Config['paths.windows.profile_links_links_target'] = Read-ConfigPrompt -Label 'Destino Links (prefira ABS, ex: D:\\onedrive\\documents\\profile\\links; relativo so em ultimo caso)' -CurrentValue $Config['paths.windows.profile_links_links_target']
	$Config['paths.wsl.onedrive_root'] = Read-ConfigPrompt -Label 'WSL OneDrive root canônica (prefira ABS, ex: /mnt/d/onedrive)' -CurrentValue $Config['paths.wsl.onedrive_root']
	$Config['paths.wsl.onedrive_clients_dir'] = Read-ConfigPrompt -Label 'WSL clients dir (prefira ABS, ex: /mnt/d/onedrive/clients; relativo so em ultimo caso)' -CurrentValue $Config['paths.wsl.onedrive_clients_dir'] -AllowEmpty
	$Config['paths.wsl.onedrive_projects_dir'] = Read-ConfigPrompt -Label 'WSL projects dir (prefira ABS, ex: /mnt/d/onedrive/clients/pablo/projects; relativo so em ultimo caso)' -CurrentValue $Config['paths.wsl.onedrive_projects_dir'] -AllowEmpty

	$Config['bootstrap.add_user.enabled'] = Read-BooleanPrompt -Label 'Criar usuario extra no WSL? (isolamento para deploy/automacao)' -CurrentValue $Config['bootstrap.add_user.enabled']
	if (($Config['bootstrap.add_user.enabled']).ToLowerInvariant() -eq 'true') {
		$Config['bootstrap.add_user.username'] = Read-ConfigPrompt -Label 'Usuário extra (ex: deploy)' -CurrentValue $Config['bootstrap.add_user.username']
		$Config['bootstrap.add_user.password_hash'] = Read-ConfigPrompt -Label 'Password hash (openssl passwd -1 \"senha\")' -CurrentValue $Config['bootstrap.add_user.password_hash']
	}
	else {
		$Config['bootstrap.add_user.username'] = ''
		$Config['bootstrap.add_user.password_hash'] = ''
	}

	$Config['secrets.onepassword_service_account_ref'] = Read-ConfigPrompt -Label 'Ref 1Password service account (op://.../service-account)' -CurrentValue $Config['secrets.onepassword_service_account_ref']
	$Config['secrets.github_project_pat_ref'] = Read-ConfigPrompt -Label 'Ref GitHub token dedicado (project-pat, op://secrets/dotfiles/github/token)' -CurrentValue $Config['secrets.github_project_pat_ref']
	$Config['secrets.github_full_access_ref'] = Read-ConfigPrompt -Label 'Ref GitHub full-access (fallback, pode ficar vazio)' -CurrentValue $Config['secrets.github_full_access_ref']
	$Config['secrets.age_key_ref'] = Read-ConfigPrompt -Label 'Ref SOPS age key (op://.../age.key)' -CurrentValue $Config['secrets.age_key_ref']

	return $Config
}

function Sync-BootstrapDerivedFiles {
	param (
		[hashtable]$Config,
		[string]$DotFilesDirectory
	)

	$secretsRefPath = Join-Path $DotFilesDirectory 'df\secrets\secrets-ref.yaml'
	$envTplPath = Join-Path $DotFilesDirectory 'bootstrap\secrets\.env.local.tpl'
	$gitLocalPath = Join-Path $DotFilesDirectory 'df\git\.gitconfig.local'

	$secretsRef = @(
		'---'
		'# Secrets do repositório dotfiles (gerado a partir de bootstrap/user-config.yaml)'
		'1password:'
		("  service-account: ""{0}""" -f $Config['secrets.onepassword_service_account_ref'])
		'github:'
		("  full-access-token: ""{0}""" -f $Config['secrets.github_full_access_ref'])
		("  project-pat: ""{0}""" -f $Config['secrets.github_project_pat_ref'])
		'age:'
		("  key: ""{0}""" -f $Config['secrets.age_key_ref'])
	)
	Set-Content -Path $secretsRefPath -Value $secretsRef

	$envTpl = @(
		'# Runtime secrets template resolved by 1Password (`op inject`).'
		'# Bootstrap persists this material encrypted at ~/.env.local.sops.'
		'# Generated from bootstrap/user-config.yaml'
		("export OP_SERVICE_ACCOUNT_TOKEN=""{{{{{0}}}}}""" -f $Config['secrets.onepassword_service_account_ref'])
		("export GH_TOKEN=""{{{{{0}}}}}""" -f $Config['secrets.github_project_pat_ref'])
		("export GITHUB_TOKEN=""{{{{{0}}}}}""" -f $Config['secrets.github_project_pat_ref'])
		("export SOPS_AGE_KEY=""{{{{{0}}}}}""" -f $Config['secrets.age_key_ref'])
	)
	Set-Content -Path $envTplPath -Value $envTpl

	$gitLocal = @(
		'# -----------------------------------------------------------------------------'
		'# ~/.config/git/.gitconfig.local (local, nao versionado)'
		'# Generated from bootstrap/user-config.yaml'
		'#'
		'# Objetivo: identidade Git local e chave publica de assinatura.'
		'#'
		'# IMPORTANTE:'
		'# - Nao coloque tokens, senhas ou chaves privadas aqui.'
		'# - "signingkey" abaixo e uma chave PUBLICA SSH (nao segredo).'
		'# - A chave privada continua protegida no 1Password SSH Agent.'
		'# -----------------------------------------------------------------------------'
		''
		'[user]'
		'    # Nome exibido como autor nos commits.'
		("    name = {0}" -f $Config['git.name'])
		''
		'    # Email do autor dos commits.'
		("    email = {0}" -f $Config['git.email'])
		''
		'    # Username usado por alguns aliases/fluxos GitHub.'
		("    username = {0}" -f $Config['git.username'])
		''
		'    # Chave PUBLICA SSH usada para identificar assinaturas de commit.'
		'    # Formato esperado: ssh-ed25519 AAAA...'
		("    signingkey = {0}" -f $Config['git.signing_key'])
	)
	Set-Content -Path $gitLocalPath -Value $gitLocal

	# Export for current bootstrap process (consumed by windows/wsl bootstrap scripts).
	# -------- Windows OneDrive envs --------
	$Env:DOTFILES_ONEDRIVE_ENABLED = ConvertTo-BoolString -Value $Config['paths.windows.onedrive_enabled'] -Default 'true'
	$Env:DOTFILES_ONEDRIVE_AUTO_MIGRATE = ConvertTo-BoolString -Value $Config['paths.windows.onedrive_auto_migrate'] -Default 'true'
	$Env:DOTFILES_LINKS_DRIVE_ENABLED = ConvertTo-BoolString -Value $Config['paths.windows.links_drive_enabled'] -Default 'true'

	$windowsRoot = Expand-WindowsPathValue -PathValue ([string]$Config['paths.windows.onedrive_root'])
	if ([string]::IsNullOrWhiteSpace($windowsRoot) -and $Env:DOTFILES_ONEDRIVE_ENABLED -eq 'true') {
		if (-not [string]::IsNullOrWhiteSpace($Env:OneDrive)) {
			$windowsRoot = $Env:OneDrive
		}
		elseif (-not [string]::IsNullOrWhiteSpace($Env:USERPROFILE)) {
			$windowsRoot = Join-Path $Env:USERPROFILE 'OneDrive'
		}
	}
	if ([string]::IsNullOrWhiteSpace($windowsRoot) -or $Env:DOTFILES_ONEDRIVE_ENABLED -ne 'true') {
		Remove-Item Env:DOTFILES_ONEDRIVE_ROOT_WINDOWS -ErrorAction SilentlyContinue
	}
	else {
		$Env:DOTFILES_ONEDRIVE_ROOT_WINDOWS = $windowsRoot
	}

	$windowsClientsRaw = Expand-WindowsPathValue -PathValue ([string]$Config['paths.windows.onedrive_clients_dir'])
	$windowsClients = Resolve-PathWithRoot -RootPath $windowsRoot -PathValue $windowsClientsRaw -Style windows
	if ([string]::IsNullOrWhiteSpace($windowsClients)) {
		Remove-Item Env:DOTFILES_ONEDRIVE_CLIENTS_PATH_WINDOWS -ErrorAction SilentlyContinue
	}
	else {
		$Env:DOTFILES_ONEDRIVE_CLIENTS_PATH_WINDOWS = $windowsClients
	}

	$windowsProjectsPathRaw = Expand-WindowsPathValue -PathValue ([string]$Config['paths.windows.onedrive_projects_path'])
	$windowsProjectsPath = Resolve-PathWithRoot -RootPath $windowsRoot -PathValue $windowsProjectsPathRaw -Style windows
	if ([string]::IsNullOrWhiteSpace($windowsProjectsPath)) {
		$windowsProjectsDirRaw = Expand-WindowsPathValue -PathValue ([string]$Config['paths.windows.onedrive_projects_dir'])
		$windowsProjectsPath = Resolve-PathWithRoot -RootPath $windowsRoot -PathValue $windowsProjectsDirRaw -Style windows
	}
	if ([string]::IsNullOrWhiteSpace($windowsProjectsPath)) {
		Remove-Item Env:DOTFILES_ONEDRIVE_PROJECTS_PATH -ErrorAction SilentlyContinue
	}
	else {
		$Env:DOTFILES_ONEDRIVE_PROJECTS_PATH = $windowsProjectsPath
	}

	$linkMap = [ordered]@{
		'DOTFILES_LINK_PROFILE_BIN'      = [string]$Config['paths.windows.links_profile_bin']
		'DOTFILES_LINK_PROFILE_ETC'      = [string]$Config['paths.windows.links_profile_etc']
		'DOTFILES_LINK_PROFILE_CLIENTS'  = [string]$Config['paths.windows.links_profile_clients']
		'DOTFILES_LINK_PROFILE_PROJECTS' = [string]$Config['paths.windows.links_profile_projects']
		'DOTFILES_LINK_DRIVE_BIN'        = [string]$Config['paths.windows.links_drive_bin']
		'DOTFILES_LINK_DRIVE_ETC'        = [string]$Config['paths.windows.links_drive_etc']
		'DOTFILES_LINK_DRIVE_CLIENTS'    = [string]$Config['paths.windows.links_drive_clients']
		'DOTFILES_LINK_DRIVE_PROJECTS'   = [string]$Config['paths.windows.links_drive_projects']
		'DOTFILES_PROFILE_FOLDER_MIGRATE_CONTENT'   = (ConvertTo-BoolString -Value $Config['paths.windows.profile_links_migrate_content'] -Default 'true')
		'DOTFILES_PROFILE_FOLDER_DOCUMENTS_ENABLED' = (ConvertTo-BoolString -Value $Config['paths.windows.profile_links_documents_enabled'] -Default 'false')
		'DOTFILES_PROFILE_FOLDER_DOCUMENTS_TARGET'  = [string]$Config['paths.windows.profile_links_documents_target']
		'DOTFILES_PROFILE_FOLDER_DESKTOP_ENABLED'   = (ConvertTo-BoolString -Value $Config['paths.windows.profile_links_desktop_enabled'] -Default 'false')
		'DOTFILES_PROFILE_FOLDER_DESKTOP_TARGET'    = [string]$Config['paths.windows.profile_links_desktop_target']
		'DOTFILES_PROFILE_FOLDER_DOWNLOADS_ENABLED' = (ConvertTo-BoolString -Value $Config['paths.windows.profile_links_downloads_enabled'] -Default 'false')
		'DOTFILES_PROFILE_FOLDER_DOWNLOADS_TARGET'  = [string]$Config['paths.windows.profile_links_downloads_target']
		'DOTFILES_PROFILE_FOLDER_PICTURES_ENABLED'  = (ConvertTo-BoolString -Value $Config['paths.windows.profile_links_pictures_enabled'] -Default 'false')
		'DOTFILES_PROFILE_FOLDER_PICTURES_TARGET'   = [string]$Config['paths.windows.profile_links_pictures_target']
		'DOTFILES_PROFILE_FOLDER_VIDEOS_ENABLED'    = (ConvertTo-BoolString -Value $Config['paths.windows.profile_links_videos_enabled'] -Default 'false')
		'DOTFILES_PROFILE_FOLDER_VIDEOS_TARGET'     = [string]$Config['paths.windows.profile_links_videos_target']
		'DOTFILES_PROFILE_FOLDER_MUSIC_ENABLED'     = (ConvertTo-BoolString -Value $Config['paths.windows.profile_links_music_enabled'] -Default 'false')
		'DOTFILES_PROFILE_FOLDER_MUSIC_TARGET'      = [string]$Config['paths.windows.profile_links_music_target']
		'DOTFILES_PROFILE_FOLDER_CONTACTS_ENABLED'  = (ConvertTo-BoolString -Value $Config['paths.windows.profile_links_contacts_enabled'] -Default 'false')
		'DOTFILES_PROFILE_FOLDER_CONTACTS_TARGET'   = [string]$Config['paths.windows.profile_links_contacts_target']
		'DOTFILES_PROFILE_FOLDER_FAVORITES_ENABLED' = (ConvertTo-BoolString -Value $Config['paths.windows.profile_links_favorites_enabled'] -Default 'false')
		'DOTFILES_PROFILE_FOLDER_FAVORITES_TARGET'  = [string]$Config['paths.windows.profile_links_favorites_target']
		'DOTFILES_PROFILE_FOLDER_LINKS_ENABLED'     = (ConvertTo-BoolString -Value $Config['paths.windows.profile_links_links_enabled'] -Default 'false')
		'DOTFILES_PROFILE_FOLDER_LINKS_TARGET'      = [string]$Config['paths.windows.profile_links_links_target']
	}
	foreach ($item in $linkMap.GetEnumerator()) {
		$expanded = Expand-WindowsPathValue -PathValue $item.Value
		if ([string]::IsNullOrWhiteSpace($expanded)) {
			Remove-Item ("Env:{0}" -f $item.Key) -ErrorAction SilentlyContinue
		}
		else {
			Set-Item -Path ("Env:{0}" -f $item.Key) -Value $expanded
		}
	}

	# -------- WSL OneDrive envs --------
	$wslRoot = [string]$Config['paths.wsl.onedrive_root']
	$Env:DOTFILES_ONEDRIVE_ROOT = $wslRoot

	$wslClients = Resolve-PathWithRoot -RootPath $wslRoot -PathValue $Config['paths.wsl.onedrive_clients_dir'] -Style unix
	if ([string]::IsNullOrWhiteSpace($wslClients)) {
		Remove-Item Env:DOTFILES_ONEDRIVE_CLIENTS_DIR -ErrorAction SilentlyContinue
	}
	else {
		$Env:DOTFILES_ONEDRIVE_CLIENTS_DIR = $wslClients
	}

	$wslProjects = Resolve-PathWithRoot -RootPath $wslRoot -PathValue $Config['paths.wsl.onedrive_projects_dir'] -Style unix
	if ([string]::IsNullOrWhiteSpace($wslProjects)) {
		Remove-Item Env:DOTFILES_ONEDRIVE_PROJECTS_DIR -ErrorAction SilentlyContinue
	}
	else {
		$Env:DOTFILES_ONEDRIVE_PROJECTS_DIR = $wslProjects
	}

	if (($Config['bootstrap.add_user.enabled']).ToLowerInvariant() -eq 'true') {
		$Env:DOTFILES_ADD_USER = $Config['bootstrap.add_user.username']
		$Env:DOTFILES_ADD_USER_PASS_HASH = $Config['bootstrap.add_user.password_hash']
	}
	else {
		Remove-Item Env:DOTFILES_ADD_USER -ErrorAction SilentlyContinue
		Remove-Item Env:DOTFILES_ADD_USER_PASS_HASH -ErrorAction SilentlyContinue
	}
}

function Ensure-BootstrapConfigReady {
	param ([string]$DotFilesDirectory)

	$templatePath = Join-Path $DotFilesDirectory 'bootstrap\user-config.yaml.tpl'
	$configPath = Join-Path $DotFilesDirectory 'bootstrap\user-config.yaml'

	if (!(Test-Path -Path $templatePath -PathType Leaf)) {
		throw "Config template not found: $templatePath"
	}

	if (!(Test-Path -Path $configPath -PathType Leaf)) {
		$defaults = Get-BootstrapConfigDefaults
		Write-BootstrapConfigYaml -Path $configPath -Config $defaults
		Write-Warning "Arquivo de config local criado em: $configPath"
	}

	$configBeforeAbsolute = Merge-BootstrapConfigWithDefaults (Read-SimpleYamlAsPathMap -Path $configPath)
	$config = Convert-BootstrapConfigToPreferredAbsolutePaths -Config $configBeforeAbsolute
	if (-not (Test-BootstrapConfigMapsEqual -Left $configBeforeAbsolute -Right $config)) {
		Write-Warning "Config local continha caminhos relativos, com alias ou nao canonicos. Regravando em formato absoluto/canonico quando possivel."
		Write-BootstrapConfigYaml -Path $configPath -Config $config
	}
	Write-BootstrapConfigPathPreferenceWarnings -Config $config
	$isFilled = Test-BootstrapConfigFilled -Config $config

	if ($isFilled) {
		$choice = Read-Host -Prompt "Config YAML ja preenchido. Escolha: 1=usar como esta, 2=sobrescrever em modo guiado"
		if ($choice -eq '2') {
			$config = Invoke-BootstrapConfigWizard -Config $config
			$config = Convert-BootstrapConfigToPreferredAbsolutePaths -Config $config
			Write-BootstrapConfigYaml -Path $configPath -Config $config
		}
	}
	else {
		$choice = Read-Host -Prompt "Config YAML incompleto. Escolha: 1=preencher agora em modo guiado, 2=preencher manualmente e abortar"
		if ($choice -eq '1') {
			$config = Invoke-BootstrapConfigWizard -Config $config
			$config = Convert-BootstrapConfigToPreferredAbsolutePaths -Config $config
			Write-BootstrapConfigYaml -Path $configPath -Config $config
		}
		else {
			Write-Warning "Preencha manualmente: $configPath e execute o bootstrap novamente."
			return $false
		}
	}

	$configBeforeAbsolute = Merge-BootstrapConfigWithDefaults (Read-SimpleYamlAsPathMap -Path $configPath)
	$config = Convert-BootstrapConfigToPreferredAbsolutePaths -Config $configBeforeAbsolute
	if (-not (Test-BootstrapConfigMapsEqual -Left $configBeforeAbsolute -Right $config)) {
		Write-Warning "Alguns caminhos ainda foram normalizados para absoluto/canonico apos a leitura final da config."
		Write-BootstrapConfigYaml -Path $configPath -Config $config
	}
	Write-BootstrapConfigPathPreferenceWarnings -Config $config
	if (!(Test-BootstrapConfigFilled -Config $config)) {
		Write-Warning "Config YAML ainda incompleto. Ajuste manualmente: $configPath"
		return $false
	}

	Sync-BootstrapDerivedFiles -Config $config -DotFilesDirectory $DotFilesDirectory
	Write-Output "Config central aplicada com sucesso a partir de: $configPath"
	return $true
}
