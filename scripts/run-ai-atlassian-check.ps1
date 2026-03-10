[CmdletBinding(PositionalBinding = $false)]
param(
    [string]$SiteUrl = ''
)

$ErrorActionPreference = 'Stop'

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$invokePython = Join-Path $scriptRoot 'invoke-python.ps1'
$controlPlaneScript = Join-Path $scriptRoot 'ai-control-plane.py'

$arguments = @('atlassian-check')
if (-not [string]::IsNullOrWhiteSpace($SiteUrl)) {
    $arguments += @('--site-url', $SiteUrl)
}

& $invokePython -ScriptPath $controlPlaneScript -Arguments $arguments
exit $LASTEXITCODE
