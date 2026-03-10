[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$RepoRoot = '',
    [string]$Out = '.cache/ai/startup-session.md'
)

$ErrorActionPreference = 'Stop'

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$invokePython = Join-Path $scriptRoot 'invoke-python.ps1'
$startupScript = Join-Path $scriptRoot 'ai-session-startup.py'

$arguments = @('report')

if (-not [string]::IsNullOrWhiteSpace($RepoRoot)) {
    $arguments += @('--repo-root', $RepoRoot)
}

if (-not [string]::IsNullOrWhiteSpace($Out)) {
    $arguments += @('--out', $Out)
}

& $invokePython -ScriptPath $startupScript -Arguments $arguments
exit $LASTEXITCODE
