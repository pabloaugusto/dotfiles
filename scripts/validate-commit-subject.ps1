param(
	[string]$Subject = '',
	[string]$Branch = ''
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($Subject)) {
	$Subject = (git log -1 --format=%s).Trim()
}

if ([string]::IsNullOrWhiteSpace($Branch)) {
	$Branch = (git rev-parse --abbrev-ref HEAD).Trim()
}

& (Join-Path $PSScriptRoot 'invoke-python.ps1') -ScriptPath (Join-Path $PSScriptRoot '..\.githooks\ci\validate_message.py') $Subject --context 'commit subject' --branch $Branch
exit $LASTEXITCODE
