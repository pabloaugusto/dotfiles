$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $here '..\..')).Path
. (Join-Path $repoRoot 'app\df\powershell\_functions.ps1')

Describe 'Test-EnvTemplateHasOpRefs' {
	It 'retorna false quando o template nao existe' {
		(Test-EnvTemplateHasOpRefs -TemplatePath (Join-Path $TestDrive 'ausente.tpl')) | Should Be $false
	}

	It 'retorna false quando o template so tem comentarios' {
		$template = Join-Path $TestDrive 'so-comentarios.tpl'
		Set-Content -Path $template -Value @(
			'# NENHUM token entra aqui.',
			'   # op://Vault/Item/field tambem nao conta',
			''
		)

		(Test-EnvTemplateHasOpRefs -TemplatePath $template) | Should Be $false
	}

	It 'retorna true quando existe ref op:// ativa' {
		$template = Join-Path $TestDrive 'com-ref.tpl'
		Set-Content -Path $template -Value @(
			'# runtime secrets',
			'GITHUB_TOKEN=op://vault/item/token'
		)

		(Test-EnvTemplateHasOpRefs -TemplatePath $template) | Should Be $true
	}

	It 'retorna false para o template real do repositorio' {
		# Guarda de regressao: se alguem reintroduzir refs do 1Password no
		# template, o bootstrap volta a gerar/exigir ~/.env.local.sops.
		$realTemplate = Join-Path $repoRoot 'app\bootstrap\secrets\.env.local.tpl'

		(Test-EnvTemplateHasOpRefs -TemplatePath $realTemplate) | Should Be $false
	}
}

Describe 'Import-DotEnvFromSops' {
	It 'fica em silencio quando o arquivo nao existe' {
		$warnings = @()
		$result = Import-DotEnvFromSops -EncryptedPath (Join-Path $TestDrive 'inexistente.sops') -WarningVariable warnings

		$warnings.Count | Should Be 0
		$result.Count | Should Be 0
	}

	It 'avisa que o arquivo e legado e nunca o remove quando a decifragem falha' {
		$originalPath = $env:PATH
		$originalAgeKeyFile = $env:SOPS_AGE_KEY_FILE
		try {
			# Stub de `sops` que sempre falha: simula o arquivo cifrado para um
			# recipient age cuja chave nao esta mais acessivel.
			$stubBin = Join-Path $TestDrive 'stub-bin'
			New-Item -ItemType Directory -Path $stubBin -Force | Out-Null
			Set-Content -Path (Join-Path $stubBin 'sops.cmd') -Value @('@echo off', 'exit /b 1')
			$env:PATH = $stubBin + [IO.Path]::PathSeparator + $env:PATH
			# Chave presente evita que o import tente falar com o 1Password.
			$env:SOPS_AGE_KEY_FILE = Join-Path $TestDrive 'age-keys.txt'
			Set-Content -Path $env:SOPS_AGE_KEY_FILE -Value 'chave-falsa-de-teste'

			$sopsFile = Join-Path $TestDrive '.env.local.sops'
			Set-Content -Path $sopsFile -Value 'AGE[ENCRYPTED]'

			$warnings = @()
			$result = Import-DotEnvFromSops -EncryptedPath $sopsFile -WarningVariable warnings

			$warnings.Count | Should Be 1
			$warnings[0].Message | Should Match 'legado'
			$result.Count | Should Be 0
			# Arquivo do dono: nunca removido por causa de uma falha de leitura.
			(Test-Path -Path $sopsFile -PathType Leaf) | Should Be $true
		}
		finally {
			$env:PATH = $originalPath
			$env:SOPS_AGE_KEY_FILE = $originalAgeKeyFile
		}
	}
}
