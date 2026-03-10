[CmdletBinding()]
param(
    [string]$IssueKeys = ""
)

$scriptPath = Join-Path $PSScriptRoot "ai-atlassian-docs-sync.py"
$pythonInvoker = Join-Path $PSScriptRoot "invoke-python.ps1"

$arguments = @()
if ($IssueKeys) {
    $arguments += "--issue-keys"
    $arguments += $IssueKeys
}

& $pythonInvoker -ScriptPath $scriptPath -Arguments $arguments
exit $LASTEXITCODE
