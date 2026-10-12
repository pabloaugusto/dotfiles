$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $here '..\..')).Path
. (Join-Path $repoRoot 'app\df\powershell\_functions.ps1')

Describe 'Find-OpSshSignWindows' {
	It 'encontra op-ssh-sign.exe direto na raiz de busca' {
		$root = Join-Path $TestDrive 'WindowsApps'
		New-Item -ItemType Directory -Path $root -Force | Out-Null
		$exe = Join-Path $root 'op-ssh-sign.exe'
		Set-Content -Path $exe -Value 'stub'

		$found = Find-OpSshSignWindows -SearchRoots @($root)

		$found | Should Not Be ''
		(Split-Path -Path $found -Leaf) | Should Be 'op-ssh-sign.exe'
	}

	It 'encontra em subpasta versionada e prefere a mais recente' {
		$root = Join-Path $TestDrive '1Password\app'
		$oldDir = Join-Path $root '8.9.0'
		$newDir = Join-Path $root '8.10.0'
		New-Item -ItemType Directory -Path $oldDir -Force | Out-Null
		New-Item -ItemType Directory -Path $newDir -Force | Out-Null
		Set-Content -Path (Join-Path $oldDir 'op-ssh-sign.exe') -Value 'old'
		Set-Content -Path (Join-Path $newDir 'op-ssh-sign.exe') -Value 'new'
		(Get-Item -LiteralPath $oldDir).LastWriteTime = (Get-Date).AddDays(-30)

		$found = Find-OpSshSignWindows -SearchRoots @($root)

		(Split-Path -Path (Split-Path -Path $found -Parent) -Leaf) | Should Be '8.10.0'
	}

	It 'retorna vazio quando nao existe nenhum binario' {
		$originalPath = $Env:PATH
		try {
			$Env:PATH = ''
			$found = Find-OpSshSignWindows -SearchRoots @((Join-Path $TestDrive 'inexistente-xyz'))
			$found | Should Be ''
		}
		finally {
			$Env:PATH = $originalPath
		}
	}
}
