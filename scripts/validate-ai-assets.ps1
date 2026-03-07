[CmdletBinding(PositionalBinding = $false)]
param(
	[string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
)

$ErrorActionPreference = 'Stop'

$scriptPath = Join-Path $PSScriptRoot 'invoke-python.ps1'
$validatorPath = Join-Path $PSScriptRoot 'validate-ai-assets.py'

& $scriptPath -ScriptPath $validatorPath $RepoRoot
exit $LASTEXITCODE
