param(
	[string]$Branch = ''
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($Branch)) {
	$Branch = (git rev-parse --abbrev-ref HEAD).Trim()
}

& (Join-Path $PSScriptRoot 'invoke-python.ps1') -ScriptPath (Join-Path $PSScriptRoot '..\.githooks\conventional_emoji.py') --validate-branch $Branch
exit $LASTEXITCODE
