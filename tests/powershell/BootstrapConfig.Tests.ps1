$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $here '..\..')).Path
. (Join-Path $repoRoot 'app\bootstrap\bootstrap-config.ps1')

# Stub de `op` no PATH: materializa arquivos deterministicos sem tocar o
# 1Password real. Nunca le/escreve segredo. Falha quando STUB_OP_FAIL=1.
function New-OpStub {
	param ([string]$Directory)
	New-Item -ItemType Directory -Path $Directory -Force | Out-Null
	$stubPath = Join-Path $Directory 'op.cmd'
	$lines = @(
		'@echo off'
		'if not "%1"=="read" exit /b 1'
		'if not "%2"=="--out-file" exit /b 1'
		'if "%STUB_OP_FAIL%"=="1" exit /b 1'
		'> "%3" echo daneel-content-for-%4'
		'exit /b 0'
	)
	Set-Content -Path $stubPath -Value $lines
	return $Directory
}

Describe 'bootstrap-config path helpers' {
	# Isolamento: Sync-BootstrapDerivedFiles chama Set-GitGlobalSigningKey, que
	# roda `git config --global`. Sem isto o teste sobrescreveria o
	# user.signingkey REAL da maquina com a chave falsa AAAATESTLOCAL.
	BeforeAll {
		$script:OriginalGitConfigGlobal = $env:GIT_CONFIG_GLOBAL
		$script:OriginalAppData = $env:APPDATA
		$script:OriginalPath = $env:PATH
		$env:GIT_CONFIG_GLOBAL = Join-Path $TestDrive 'gitconfig'
		Set-Content -Path $env:GIT_CONFIG_GLOBAL -Value ''
		# Mantem a identidade de automacao do teste fora do %APPDATA% real.
		$env:APPDATA = Join-Path $TestDrive 'appdata'
		New-Item -ItemType Directory -Path $env:APPDATA -Force | Out-Null
		$env:PATH = (New-OpStub -Directory (Join-Path $TestDrive 'stub-bin')) + [IO.Path]::PathSeparator + $env:PATH
		Remove-Item Env:STUB_OP_FAIL -ErrorAction SilentlyContinue
	}
	AfterAll {
		$env:GIT_CONFIG_GLOBAL = $script:OriginalGitConfigGlobal
		$env:APPDATA = $script:OriginalAppData
		$env:PATH = $script:OriginalPath
		Remove-Item Env:STUB_OP_FAIL -ErrorAction SilentlyContinue
	}

	It 'joins windows relative paths against a root' {
		$result = Resolve-PathWithRoot -RootPath 'C:\Root' -PathValue 'clients\demo' -Style windows
		$result | Should Be 'C:\Root\clients\demo'
	}

	It 'preserves windows absolute paths' {
		$result = Resolve-PathWithRoot -RootPath 'C:\Root' -PathValue 'D:\Elsewhere\projects' -Style windows
		$result | Should Be 'D:\Elsewhere\projects'
	}

	It 'joins unix relative paths against a root' {
		$result = Resolve-PathWithRoot -RootPath '/mnt/d/onedrive' -PathValue 'clients/demo' -Style unix
		$result | Should Be '/mnt/d/onedrive/clients/demo'
	}

	It 'promotes projects dir into projects path when absolute is resolved' {
		$defaults = Get-BootstrapConfigDefaults
		$onedriveRoot = Join-Path $TestDrive 'onedrive'
		$projectsPath = Join-Path $onedriveRoot 'clients\pablo\projects'
		New-Item -ItemType Directory -Path $projectsPath -Force | Out-Null

		$defaults['paths.windows.onedrive_root'] = $onedriveRoot
		$defaults['paths.windows.onedrive_projects_dir'] = 'clients\pablo\projects'
		$defaults['paths.windows.onedrive_projects_path'] = ''

		$normalized = Convert-BootstrapConfigToPreferredAbsolutePaths -Config $defaults

		$normalized['paths.windows.onedrive_projects_dir'] | Should Be ''
		$normalized['paths.windows.onedrive_projects_path'] | Should Be $projectsPath
	}

	It 'expands profile links into canonical absolute windows paths' {
		$defaults = Get-BootstrapConfigDefaults
		$expected = Join-Path $Env:USERPROFILE 'bin'

		$normalized = Convert-BootstrapConfigToPreferredAbsolutePaths -Config $defaults

		$normalized['paths.windows.links_profile_bin'] | Should Be $expected
	}

	It 'renderiza a secao automation do template sem placeholders literais' {
		# Exercita o renderer contra o TEMPLATE REAL do repo (copiado para o
		# TestDrive: o repo nunca e' escrito).
		$tplDir = Join-Path $TestDrive 'render'
		New-Item -ItemType Directory -Path $tplDir -Force | Out-Null
		Copy-Item -Path (Join-Path $repoRoot 'app\bootstrap\user-config.yaml.tpl') -Destination (Join-Path $tplDir 'user-config.yaml.tpl') -Force
		$outPath = Join-Path $tplDir 'user-config.yaml'

		Write-BootstrapConfigYaml -Path $outPath -Config (Get-BootstrapConfigDefaults)
		$rendered = Get-Content -Raw -Path $outPath

		$rendered | Should Not Match '@@'
		$rendered | Should Not Match 'automation_signing_key_ref'
		$rendered | Should Match 'signing_key_ref: "op://secrets/daneel/signing/private_key"'
		$rendered | Should Match 'signing_public_key_ref: "op://secrets/daneel/signing/public_key"'
		$rendered | Should Match 'op_token_ref: "op://secrets/daneel/1password/service-account"'
		$rendered | Should Match 'allowed_signers_ref: "op://secrets/dotfiles/git/allowed_signers"'
		$rendered | Should Match 'git_name: "Daneel"'
		$rendered | Should Match 'git_email: "daneel@pabloaugusto.com"'
	}

	It 'nao escreve ref de automacao por maquina no secrets-ref' {
		$config = Get-BootstrapConfigDefaults
		$config['git.name'] = 'Pablo'
		$config['git.email'] = 'pablo@example.com'
		$config['git.username'] = 'pabloaugusto'
		$config['git.signing_key'] = 'ssh-ed25519 AAAATESTLOCAL human@host'

		$repo = Join-Path $TestDrive 'repo'
		New-Item -ItemType Directory -Path (Join-Path $repo 'app\df\secrets') -Force | Out-Null
		New-Item -ItemType Directory -Path (Join-Path $repo 'app\df\git') -Force | Out-Null

		Sync-BootstrapDerivedFiles -Config $config -DotFilesDirectory $repo

		$secretsRef = Get-Content -Raw -Path (Join-Path $repo 'app\df\secrets\secrets-ref.yaml')
		$secretsRef | Should Not Match 'git-signing'
		$secretsRef | Should Not Match 'automation-public-key'
		# Nada de cofre Personal no derivado: a service account do bootstrap so
		# enxerga o cofre `secrets`.
		$secretsRef | Should Not Match 'op://Personal/'
	}
}

Describe 'identidade de automacao daneel' {
	BeforeAll {
		# Get-AutomationSigningKeyPath / Get-CheckEnvGitProbeContext vivem aqui.
		. (Join-Path $repoRoot 'app\df\powershell\_functions.ps1')
		$script:OriginalAppData = $env:APPDATA
		$script:OriginalTarsActor = $env:TARS_ACTOR
		$script:OriginalGitConfigGlobal = $env:GIT_CONFIG_GLOBAL
		$script:OriginalPath = $env:PATH

		$env:APPDATA = Join-Path $TestDrive 'appdata'
		New-Item -ItemType Directory -Path $env:APPDATA -Force | Out-Null
		# Nunca tocar no global real: Sync-BootstrapDerivedFiles roda git config --global.
		$env:GIT_CONFIG_GLOBAL = Join-Path $TestDrive 'gitconfig'
		Set-Content -Path $env:GIT_CONFIG_GLOBAL -Value ''
		$env:PATH = (New-OpStub -Directory (Join-Path $TestDrive 'stub-bin')) + [IO.Path]::PathSeparator + $env:PATH
		Remove-Item Env:STUB_OP_FAIL -ErrorAction SilentlyContinue
	}
	AfterAll {
		$env:APPDATA = $script:OriginalAppData
		$env:GIT_CONFIG_GLOBAL = $script:OriginalGitConfigGlobal
		$env:PATH = $script:OriginalPath
		if ($null -eq $script:OriginalTarsActor) { Remove-Item Env:TARS_ACTOR -ErrorAction SilentlyContinue }
		else { $env:TARS_ACTOR = $script:OriginalTarsActor }
		Remove-Item Env:STUB_OP_FAIL -ErrorAction SilentlyContinue
	}

	It 'materializa a identidade daneel do 1Password e e idempotente' {
		Ensure-DaneelAutomationIdentity -Config (Get-BootstrapConfigDefaults) | Out-Null

		$keyPath = Get-AutomationSigningKeyPath
		$pubPath = Get-AutomationSigningPublicKeyPath
		$tokenPath = Get-AutomationOpTokenPath

		# Sem hostname no nome dos arquivos: identidade unica.
		(Split-Path -Path $keyPath -Leaf) | Should Be 'daneel_ed25519'
		Test-Path -Path $keyPath -PathType Leaf | Should Be $true
		Test-Path -Path $pubPath -PathType Leaf | Should Be $true
		Test-Path -Path $tokenPath -PathType Leaf | Should Be $true

		$keyContent = (Get-Content -Raw -Path $keyPath).Trim()
		$keyContent | Should Match 'op://secrets/daneel/signing/private_key'
		(Get-Content -Raw -Path $tokenPath).Trim() | Should Match 'op://secrets/daneel/1password/service-account'

		# Idempotencia: materializar de novo nao reescreve (timestamp preservado).
		$beforeWrite = (Get-Item -Path $keyPath).LastWriteTimeUtc
		Ensure-DaneelAutomationIdentity -Config (Get-BootstrapConfigDefaults) | Out-Null
		(Get-Item -Path $keyPath).LastWriteTimeUtc | Should Be $beforeWrite
	}

	It 'falha claro quando o item nao existe no 1Password (nunca gera chave)' {
		$env:STUB_OP_FAIL = '1'
		try {
			$threw = $false
			try {
				Ensure-DaneelAutomationIdentity -Config (Get-BootstrapConfigDefaults) | Out-Null
			}
			catch {
				$threw = $true
				$_.Exception.Message | Should Match 'ausente ou ilegivel'
			}
			$threw | Should Be $true
		}
		finally {
			Remove-Item Env:STUB_OP_FAIL -ErrorAction SilentlyContinue
		}
	}

	It 'TARS_ACTOR=agent resolve o modo automation; sem ele, human' {
		$env:TARS_ACTOR = 'agent'
		(Get-CheckEnvGitProbeContext).ResolvedMode | Should Be 'automation'

		Remove-Item Env:TARS_ACTOR -ErrorAction SilentlyContinue
		(Get-CheckEnvGitProbeContext).ResolvedMode | Should Be 'human'
	}
}
