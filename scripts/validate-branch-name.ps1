param(
	[string]$Branch = '',
	[string]$Range = ''
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($Branch)) {
	$Branch = (git rev-parse --abbrev-ref HEAD).Trim()
}

$pathsJson = '[]'
if (-not [string]::IsNullOrWhiteSpace($Range)) {
	$payload = & (Join-Path $PSScriptRoot 'invoke-python.ps1') -ScriptPath (Join-Path $PSScriptRoot 'git-commit-subjects.py') --repo-root (Resolve-Path (Join-Path $PSScriptRoot '..')).Path --range $Range --include-files
	if ($LASTEXITCODE -ne 0) {
		exit $LASTEXITCODE
	}

	$paths = @()
	$entries = $payload | ConvertFrom-Json
	foreach ($entry in @($entries)) {
		foreach ($path in @($entry.paths)) {
			if (-not [string]::IsNullOrWhiteSpace($path)) {
				$paths += [string]$path
			}
		}
	}
	$pathsJson = ($paths | Select-Object -Unique | ConvertTo-Json -Compress)
}

& (Join-Path $PSScriptRoot 'invoke-python.ps1') -ScriptPath (Join-Path $PSScriptRoot '..\.githooks\conventional_emoji.py') --validate-branch $Branch --paths-json $pathsJson
exit $LASTEXITCODE
