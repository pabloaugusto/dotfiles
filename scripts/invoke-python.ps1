[CmdletBinding(PositionalBinding = $false)]
param(
	[string]$ScriptPath = '',

	[Parameter(ValueFromRemainingArguments = $true)]
	[string[]]$Arguments,

	[string]$Module = ''
)

$ErrorActionPreference = 'Stop'
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'

function Get-PythonCommand {
	$candidates = @(
		@('py', '-3'),
		@('python3'),
		@('python'),
		@('python.exe')
	)

	foreach ($candidate in $candidates) {
		$cmd = Get-Command $candidate[0] -ErrorAction SilentlyContinue
		if (-not $cmd) {
			continue
		}

		& $candidate[0] @($candidate[1..($candidate.Count - 1)]) -c 'import sys' *> $null
		if ($LASTEXITCODE -eq 0) {
			return ,$candidate
		}
	}

	throw 'Runtime Python nao encontrado para executar validacoes.'
}

$pythonCommand = Get-PythonCommand
$pythonExe = $pythonCommand[0]
$pythonArgs = @()
if ($pythonCommand.Count -gt 1) {
	$pythonArgs += $pythonCommand[1..($pythonCommand.Count - 1)]
}

if (-not [string]::IsNullOrWhiteSpace($Module)) {
	& $pythonExe @pythonArgs -m $Module @Arguments
	exit $LASTEXITCODE
}

if ([string]::IsNullOrWhiteSpace($ScriptPath)) {
	throw 'Informe -ScriptPath ou -Module.'
}

if ($ScriptPath.StartsWith('-')) {
	& $pythonExe @pythonArgs $ScriptPath @Arguments
	exit $LASTEXITCODE
}

$resolvedScriptPath = (Resolve-Path $ScriptPath).Path
& $pythonExe @pythonArgs $resolvedScriptPath @Arguments
exit $LASTEXITCODE
