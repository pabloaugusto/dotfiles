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
		@('.venv/windows/Scripts/python.exe'),
		@('.venv/windows/Scripts/python'),
		@('.venv/linux/bin/python3'),
		@('.venv/linux/bin/python'),
		@('py', '-3'),
		@('python3'),
		@('python'),
		@('python.exe')
	)

	foreach ($candidate in $candidates) {
		$candidateExe = $candidate[0]
		$candidateArgs = @()
		if ($candidate.Count -gt 1) {
			$candidateArgs = $candidate[1..($candidate.Count - 1)]
		}

		if ($candidateExe -like '.venv/*') {
			$resolved = Join-Path (Get-Location) $candidateExe
			if (-not (Test-Path $resolved)) {
				continue
			}
			& $resolved @candidateArgs -c 'import sys' *> $null
			if ($LASTEXITCODE -eq 0) {
				$resolvedCandidate = @($resolved)
				if ($candidateArgs.Count -gt 0) {
					$resolvedCandidate += $candidateArgs
				}
				return ,$resolvedCandidate
			}
			continue
		}

		$cmd = Get-Command $candidateExe -ErrorAction SilentlyContinue
		if (-not $cmd) {
			continue
		}

		& $candidateExe @candidateArgs -c 'import sys' *> $null
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
