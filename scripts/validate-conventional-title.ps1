param(
	[Parameter(Mandatory = $true)]
	[string]$Title
)

$pattern = '^(?<emoji>\S+)\s+(?<type>feat|fix|docs|refactor|test|chore|ci|perf|build|revert)(\([a-z0-9._/-]+\))?:\s+[a-z0-9].+$'

if ($Title -notmatch $pattern) {
	Write-Error @"
Titulo invalido.

Esperado:
  <emoji> <type>(<scope opcional>): <descricao>

Exemplo:
  ✨ feat(test-harness): add pester foundation
"@
	exit 1
}

Write-Host "PR title OK: $Title"
