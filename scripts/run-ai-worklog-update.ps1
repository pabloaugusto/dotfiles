[CmdletBinding(PositionalBinding = $false)]
param(
    [Parameter(Mandatory = $true)]
    [string]$WorklogId,

    [Parameter(Mandatory = $true)]
    [string]$ProgressText,

    [string]$NextStep = '',
    [string]$Blockers = '-',
    [string]$TaskMessage = '',
    [string]$ScopeText = '',
    [string]$BranchName = '',
    [string]$OwnerName = ''
)

$ErrorActionPreference = 'Stop'

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$invokePython = Join-Path $scriptRoot 'invoke-python.ps1'
$worklogScript = Join-Path $scriptRoot 'ai-worklog.py'

$arguments = @(
    'update',
    '--worklog-id', $WorklogId,
    '--progress', $ProgressText,
    '--next-step', $NextStep,
    '--blockers', $Blockers,
    '--message', $TaskMessage,
    '--scope', $ScopeText,
    '--branch', $BranchName,
    '--owner', $OwnerName
)

& $invokePython -ScriptPath $worklogScript -Arguments $arguments
exit $LASTEXITCODE
