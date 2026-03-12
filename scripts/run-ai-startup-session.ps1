[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$RepoRoot = '',
    [string]$Out = '.cache/ai/startup-session.md',
    [string]$ReadyOut = '.cache/ai/startup-ready.json',
    [ValidateSet('', 'concluir_primeiro', 'roadmap_pendente')]
    [string]$PendingAction = ''
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

if (-not [string]::IsNullOrWhiteSpace($ReadyOut)) {
    $arguments += @('--ready-out', $ReadyOut)
}

if (-not [string]::IsNullOrWhiteSpace($PendingAction)) {
    $arguments += @('--pending-action', $PendingAction)
}

& $invokePython -ScriptPath $startupScript -Arguments $arguments
exit $LASTEXITCODE
