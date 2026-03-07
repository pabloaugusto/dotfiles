param()

$ErrorActionPreference = 'Stop'

& (Join-Path $PSScriptRoot 'invoke-python.ps1') -Module unittest -Arguments @(
	'discover',
	'-s',
	'./tests/python',
	'-p',
	'*_test.py'
)
exit $LASTEXITCODE
