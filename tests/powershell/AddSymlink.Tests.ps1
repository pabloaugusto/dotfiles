$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $here '..\..')).Path
. (Join-Path $repoRoot 'df\powershell\_functions.ps1')

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
}
