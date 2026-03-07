param(
	[string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path,
	[string]$TargetRoot = (Join-Path $HOME '.codex/skills/private/dotfiles')
)

$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path $RepoRoot).Path
$skillsRoot = Join-Path $repoRoot '.agents/skills'

if (-not (Test-Path $skillsRoot -PathType Container)) {
	throw "Pasta de skills nao encontrada: $skillsRoot"
}

New-Item -ItemType Directory -Force -Path $TargetRoot | Out-Null

foreach ($skillDir in Get-ChildItem $skillsRoot -Directory | Sort-Object Name) {
	$targetPath = Join-Path $TargetRoot $skillDir.Name

	if (Test-Path $targetPath) {
		Remove-Item -Path $targetPath -Recurse -Force
	}

	if ($IsWindows) {
		New-Item -ItemType Junction -Path $targetPath -Target $skillDir.FullName | Out-Null
	}
	else {
		New-Item -ItemType SymbolicLink -Path $targetPath -Target $skillDir.FullName | Out-Null
	}

	Write-Host "Skill instalada: $($skillDir.Name) -> $targetPath"
}
