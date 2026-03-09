[CmdletBinding(PositionalBinding = $false)]
param(
    [switch]$AllowVisualBoardGap
)

$ErrorActionPreference = 'Stop'

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$invokePython = Join-Path $scriptRoot 'invoke-python.ps1'
$seedScript = Join-Path $scriptRoot 'ai-atlassian-seed.py'

$arguments = @('apply')
if ($AllowVisualBoardGap) {
    $arguments += '--allow-visual-board-gap'
}

& $invokePython -ScriptPath $seedScript -Arguments $arguments
exit $LASTEXITCODE
