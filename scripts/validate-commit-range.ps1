param(
	[string]$Range = ''
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($Range)) {
	$Range = 'origin/main..HEAD'
}

$subjects = @(git log --format=%s $Range)
$payload = @($subjects | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }) | ConvertTo-Json -Compress -AsArray

& (Join-Path $PSScriptRoot 'invoke-python.ps1') -ScriptPath (Join-Path $PSScriptRoot '..\.githooks\conventional_emoji.py') --validate-many-json $payload --require-emoji
exit $LASTEXITCODE
