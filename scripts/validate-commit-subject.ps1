param(
	[string]$Subject = ''
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($Subject)) {
	$Subject = (git log -1 --format=%s).Trim()
}

& (Join-Path $PSScriptRoot 'invoke-python.ps1') -ScriptPath (Join-Path $PSScriptRoot '..\.githooks\ci\validate_message.py') $Subject --context 'commit subject'
exit $LASTEXITCODE
