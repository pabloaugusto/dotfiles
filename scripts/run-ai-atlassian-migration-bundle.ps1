[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$OutputRoot = ''
)

$ErrorActionPreference = 'Stop'

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$invokePython = Join-Path $scriptRoot 'invoke-python.ps1'
$bundleScript = Join-Path $scriptRoot 'ai-atlassian-migration-bundle.py'

$arguments = @('bundle')
if (-not [string]::IsNullOrWhiteSpace($OutputRoot)) {
    $arguments += @('--output-root', $OutputRoot)
}

& $invokePython -ScriptPath $bundleScript -Arguments $arguments
exit $LASTEXITCODE
