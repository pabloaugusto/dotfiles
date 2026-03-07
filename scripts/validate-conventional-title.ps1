param(
	[Parameter(Mandatory = $true)]
	[string]$Title
)

$ErrorActionPreference = 'Stop'

& (Join-Path $PSScriptRoot 'invoke-python.ps1') -ScriptPath (Join-Path $PSScriptRoot '..\.githooks\ci\validate_message.py') $Title --context 'PR title'
exit $LASTEXITCODE
