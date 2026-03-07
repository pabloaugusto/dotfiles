param(
	[Parameter(Mandatory = $true)]
	[string]$Repo,

	[Parameter(Mandatory = $true)]
	[int]$PrNumber
)

$ErrorActionPreference = 'Stop'

& (Join-Path $PSScriptRoot 'invoke-python.ps1') -ScriptPath (Join-Path $PSScriptRoot '..\.githooks\ci\validate_pr_commits.py') $Repo $PrNumber
exit $LASTEXITCODE
