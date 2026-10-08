$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $here '..\..')).Path
. (Join-Path $repoRoot 'app\bootstrap\bootstrap-config.ps1')

Describe 'bootstrap-config path helpers' {
	# Isolamento: Sync-BootstrapDerivedFiles chama Set-GitGlobalSigningKey, que
	# roda `git config --global`. Sem isto o teste sobrescreveria o
	# user.signingkey REAL da maquina com a chave falsa AAAATESTLOCAL.
	BeforeAll {
		$script:OriginalGitConfigGlobal = $env:GIT_CONFIG_GLOBAL
		$script:OriginalAppData = $env:APPDATA
		$env:GIT_CONFIG_GLOBAL = Join-Path $TestDrive 'gitconfig'
		Set-Content -Path $env:GIT_CONFIG_GLOBAL -Value ''
		# Mantem a chave de automacao do teste fora do %APPDATA% real.
		$env:APPDATA = Join-Path $TestDrive 'appdata'
	}
	AfterAll {
		$env:GIT_CONFIG_GLOBAL = $script:OriginalGitConfigGlobal
		$env:APPDATA = $script:OriginalAppData
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

	It 'writes automation signing ref into secrets-ref when configured' {
		$config = Get-BootstrapConfigDefaults
		$config['git.name'] = 'Pablo'
		$config['git.email'] = 'pablo@example.com'
		$config['git.username'] = 'pabloaugusto'
		$config['git.signing_key'] = 'ssh-ed25519 AAAATESTLOCAL human@host'
		$config['git.automation_signing_key_ref'] = 'op://secrets/dotfiles/git-automation/public key'

		$repo = Join-Path $TestDrive 'repo'
		New-Item -ItemType Directory -Path (Join-Path $repo 'app\df\secrets') -Force | Out-Null
		New-Item -ItemType Directory -Path (Join-Path $repo 'app\bootstrap\secrets') -Force | Out-Null
		New-Item -ItemType Directory -Path (Join-Path $repo 'app\df\git') -Force | Out-Null

		Sync-BootstrapDerivedFiles -Config $config -DotFilesDirectory $repo

		$secretsRef = Get-Content -Raw -Path (Join-Path $repo 'app\df\secrets\secrets-ref.yaml')
		$secretsRef | Should Match 'git-signing:'
		$secretsRef | Should Match 'automation-public-key: "op://secrets/dotfiles/git-automation/public key"'
		# Nada de cofre Personal no derivado: a service account do bootstrap so
		# enxerga o cofre `secrets`.
		$secretsRef | Should Not Match 'op://Personal/'
	}
}

Describe 'automation signing key' {
	BeforeAll {
		# Get-AutomationSigningKeyPath / Get-CheckEnvGitProbeContext vivem aqui.
		. (Join-Path $repoRoot 'app\df\powershell\_functions.ps1')
		$script:OriginalAppData = $env:APPDATA
		$script:OriginalTarsActor = $env:TARS_ACTOR
		$script:OriginalGitConfigGlobal = $env:GIT_CONFIG_GLOBAL

		$env:APPDATA = Join-Path $TestDrive 'appdata'
		New-Item -ItemType Directory -Path $env:APPDATA -Force | Out-Null
		# Nunca tocar no global real: Sync-BootstrapDerivedFiles roda git config --global.
		$env:GIT_CONFIG_GLOBAL = Join-Path $TestDrive 'gitconfig'
		Set-Content -Path $env:GIT_CONFIG_GLOBAL -Value ''
	}
	AfterAll {
		$env:APPDATA = $script:OriginalAppData
		$env:GIT_CONFIG_GLOBAL = $script:OriginalGitConfigGlobal
		if ($null -eq $script:OriginalTarsActor) { Remove-Item Env:TARS_ACTOR -ErrorAction SilentlyContinue }
		else { $env:TARS_ACTOR = $script:OriginalTarsActor }
	}

	It 'gera a chave de automacao e e idempotente' {
		if (-not (Get-Command ssh-keygen -ErrorAction SilentlyContinue)) { Set-ItResult -Skipped -Because 'ssh-keygen ausente'; return }

		Ensure-AutomationSigningKey -HumanPublicKey 'ssh-ed25519 AAAATESTHUMAN human@host'
		$keyPath = Get-AutomationSigningKeyPath
		Test-Path -Path $keyPath -PathType Leaf | Should Be $true

		$before = (Get-Content -Raw -Path "$keyPath.pub").Trim()
		Ensure-AutomationSigningKey -HumanPublicKey 'ssh-ed25519 AAAATESTHUMAN human@host'
		(Get-Content -Raw -Path "$keyPath.pub").Trim() | Should Be $before

		# allowed_signers cobre a humana e a de automacao.
		$allowed = Get-Content -Raw -Path (Join-Path (Split-Path -Parent $keyPath) 'allowed_signers')
		$allowed | Should Match 'AAAATESTHUMAN'
		$allowed | Should Match 'automation-'
	}

	It 'TARS_ACTOR=agent resolve o modo automation; sem ele, human' {
		$env:TARS_ACTOR = 'agent'
		(Get-CheckEnvGitProbeContext).ResolvedMode | Should Be 'automation'

		Remove-Item Env:TARS_ACTOR -ErrorAction SilentlyContinue
		(Get-CheckEnvGitProbeContext).ResolvedMode | Should Be 'human'
	}
}
