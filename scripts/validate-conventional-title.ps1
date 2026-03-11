param(
	[Parameter(Mandatory = $true)]
	[string]$Title,

	[string]$Branch = ''
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($Branch)) {
	$Branch = (git rev-parse --abbrev-ref HEAD).Trim()
}

& (Join-Path $PSScriptRoot 'invoke-python.ps1') -ScriptPath (Join-Path $PSScriptRoot '..\.githooks\ci\validate_message.py') $Title --context 'PR title' --branch $Branch
exit $LASTEXITCODE
