param(
	[string]$Range = '',
	[string]$Remote = 'origin',
	[string]$Branch = ''
)

$ErrorActionPreference = 'Stop'

$scriptPath = Join-Path $PSScriptRoot 'git-commit-subjects.py'
$pythonArgs = @('--repo-root', (Resolve-Path (Join-Path $PSScriptRoot '..')).Path)
if ([string]::IsNullOrWhiteSpace($Range)) {
	$pythonArgs += @('--remote', $Remote)
} else {
	$pythonArgs += @('--range', $Range)
}
$pythonArgs += '--include-files'

if ([string]::IsNullOrWhiteSpace($Branch)) {
	$Branch = (git rev-parse --abbrev-ref HEAD).Trim()
}

$payload = & (Join-Path $PSScriptRoot 'invoke-python.ps1') -ScriptPath $scriptPath @pythonArgs
if ($LASTEXITCODE -ne 0) {
	exit $LASTEXITCODE
}

& (Join-Path $PSScriptRoot 'invoke-python.ps1') -ScriptPath (Join-Path $PSScriptRoot '..\.githooks\conventional_emoji.py') --validate-many-json $payload --require-emoji --require-issue-key --branch $Branch
exit $LASTEXITCODE
