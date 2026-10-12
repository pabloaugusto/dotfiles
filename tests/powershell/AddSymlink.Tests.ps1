$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $here '..\..')).Path
. (Join-Path $repoRoot 'app\df\powershell\_functions.ps1')

Describe 'Add-Symlink' {
	It 'cria um vinculo funcional para arquivo existente' {
		$targetFile = Join-Path $TestDrive 'target.txt'
		$linkFile = Join-Path $TestDrive 'link.txt'

		Set-Content -Path $targetFile -Value 'dotfiles-test'

		Add-Symlink -from $linkFile -to $targetFile

		Test-Path -Path $linkFile | Should Be $true
		(Get-Content -Path $linkFile -Raw) | Should Be "dotfiles-test$([Environment]::NewLine)"
	}

	It 'cria um vinculo funcional para diretorio existente' {
		$targetDir = Join-Path $TestDrive 'target-dir'
		$linkDir = Join-Path $TestDrive 'link-dir'

		New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
		Set-Content -Path (Join-Path $targetDir 'sample.txt') -Value 'ok'

		Add-Symlink -from $linkDir -to $targetDir

		Test-Path -Path $linkDir -PathType Container | Should Be $true
		(Get-Content -Path (Join-Path $linkDir 'sample.txt') -Raw) | Should Be "ok$([Environment]::NewLine)"
	}

	It 'preserva pasta real em backup .dotfiles-prelink-* antes de linkar' {
		$source = Join-Path $TestDrive 'vscode-src'
		$dest = Join-Path $TestDrive 'CodeUser'
		New-Item -ItemType Directory -Path $source -Force | Out-Null
		New-Item -ItemType Directory -Path $dest -Force | Out-Null
		Set-Content -Path (Join-Path $dest 'settings.json') -Value 'do-usuario'

		Add-Symlink -from $dest -to $source -WarningAction SilentlyContinue

		$backups = @(Get-ChildItem -Path $TestDrive -Directory -Force | Where-Object { $_.Name -like 'CodeUser.dotfiles-prelink-*' })
		$backups.Count | Should Be 1
		(Get-Content -Path (Join-Path $backups[0].FullName 'settings.json') -Raw).Trim() | Should Be 'do-usuario'
		(Get-Item -Path $dest -Force).LinkType | Should Be 'SymbolicLink'
	}

	It 'e no-op quando o link correto ja existe' {
		$source = Join-Path $TestDrive 'src-noop'
		$dest = Join-Path $TestDrive 'dest-noop'
		New-Item -ItemType Directory -Path $source -Force | Out-Null

		Add-Symlink -from $dest -to $source -WarningAction SilentlyContinue
		$firstTarget = [string](Get-Item -Path $dest -Force).Target
		Add-Symlink -from $dest -to $source -WarningAction SilentlyContinue

		(Get-Item -Path $dest -Force).LinkType | Should Be 'SymbolicLink'
		[string](Get-Item -Path $dest -Force).Target | Should Be $firstTarget
	}

	It 'remove apenas o link ao re-apontar, preservando o alvo anterior' {
		$oldSource = Join-Path $TestDrive 'old-src'
		$newSource = Join-Path $TestDrive 'new-src'
		$dest = Join-Path $TestDrive 'dest-retarget'
		New-Item -ItemType Directory -Path $oldSource -Force | Out-Null
		New-Item -ItemType Directory -Path $newSource -Force | Out-Null
		Set-Content -Path (Join-Path $oldSource 'keep.txt') -Value 'antigo'

		Add-Symlink -from $dest -to $oldSource -WarningAction SilentlyContinue
		Add-Symlink -from $dest -to $newSource -WarningAction SilentlyContinue

		Test-Path -Path (Join-Path $oldSource 'keep.txt') | Should Be $true
		@(Get-ChildItem -Path $TestDrive -Directory -Force | Where-Object { $_.Name -like 'dest-retarget.dotfiles-prelink-*' }).Count | Should Be 0
	}
}
