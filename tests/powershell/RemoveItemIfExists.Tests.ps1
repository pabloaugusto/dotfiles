$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $here '..\..')).Path
. (Join-Path $repoRoot 'app\df\powershell\_functions.ps1')

Describe 'Remove-ItemIfExists' {
	It 'e no-op quando o caminho nao existe' {
		$missing = Join-Path $TestDrive 'nao-existe-xyz'
		{ Remove-ItemIfExists -Path $missing } | Should Not Throw
		Test-Path -LiteralPath $missing | Should Be $false
	}

	It 'preserva conteudo real de ARQUIVO em backup .dotfiles-prelink-*' {
		$file = Join-Path $TestDrive 'real.txt'
		Set-Content -Path $file -Value 'conteudo-do-usuario'

		Remove-ItemIfExists -Path $file -WarningAction SilentlyContinue

		Test-Path -LiteralPath $file | Should Be $false
		$backups = @(Get-ChildItem -Path $TestDrive -File -Force | Where-Object { $_.Name -like 'real.txt.dotfiles-prelink-*' })
		$backups.Count | Should Be 1
		(Get-Content -Path $backups[0].FullName -Raw).Trim() | Should Be 'conteudo-do-usuario'
	}

	It 'preserva conteudo real de DIRETORIO em backup .dotfiles-prelink-*' {
		$dir = Join-Path $TestDrive 'real-dir'
		New-Item -ItemType Directory -Path $dir -Force | Out-Null
		Set-Content -Path (Join-Path $dir 'keep.txt') -Value 'guardar'

		Remove-ItemIfExists -Path $dir -WarningAction SilentlyContinue

		Test-Path -LiteralPath $dir | Should Be $false
		$backups = @(Get-ChildItem -Path $TestDrive -Directory -Force | Where-Object { $_.Name -like 'real-dir.dotfiles-prelink-*' })
		$backups.Count | Should Be 1
		(Get-Content -Path (Join-Path $backups[0].FullName 'keep.txt') -Raw).Trim() | Should Be 'guardar'
	}

	It 'remove apenas o link e preserva o alvo apontado' {
		$target = Join-Path $TestDrive 'link-target'
		$link = Join-Path $TestDrive 'link-alvo'
		New-Item -ItemType Directory -Path $target -Force | Out-Null
		Set-Content -Path (Join-Path $target 'keep.txt') -Value 'sobrevive'

		Add-Symlink -from $link -to $target -WarningAction SilentlyContinue
		(Get-Item -LiteralPath $link -Force).LinkType | Should Not Be $null

		Remove-ItemIfExists -Path $link

		Test-Path -LiteralPath $link | Should Be $false
		Test-Path -LiteralPath (Join-Path $target 'keep.txt') | Should Be $true
		# Nenhum backup criado: era apenas um link.
		@(Get-ChildItem -Path $TestDrive -Force | Where-Object { $_.Name -like 'link-alvo.dotfiles-prelink-*' }).Count | Should Be 0
	}
}
