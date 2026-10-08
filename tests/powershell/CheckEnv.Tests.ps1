$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $here '..\..')).Path
. (Join-Path $repoRoot 'app\df\powershell\_functions.ps1')

Describe 'checkEnv' {
	It 'nao invoca git commit -S (evita prompt de biometria)' {
		# Contrato estatico: a sonda de assinatura nao pode chamar commit -S,
		# que com o signer do 1Password bloqueia num prompt biometrico.
		# Linhas de comentario sao removidas: um comentario explicando a
		# proibicao nao e uma invocacao.
		$code = (Get-Content (Join-Path $repoRoot 'app\df\powershell\_functions.ps1') |
			Where-Object { $_ -notmatch '^\s*#' }) -join "`n"
		$code | Should Not Match 'git commit -S'
	}

	It 'usa ssh-keygen -Y sign na sonda de assinatura' {
		$source = Get-Content -Raw (Join-Path $repoRoot 'app\df\powershell\_functions.ps1')
		$source | Should Match 'ssh-keygen -Y sign'
	}

	It 'lista unica de binarios esperados cobre o fluxo de auth/signing' {
		$source = Get-Content -Raw (Join-Path $repoRoot 'app\df\powershell\_functions.ps1')
		foreach ($bin in 'op', 'gh', 'glab', 'git', 'ssh', 'sops', 'age', 'task', 'uv',
			'oh-my-posh', 'jq', 'yq', 'kubectl', 'kustomize', 'kubeconform', 'terraform',
			'helm', 'flux', 'cloudflared', 'direnv', 'python') {
			$source | Should Match ([regex]::Escape("'$bin'"))
		}
	}

	It 'nao exige node na lista de binarios esperados' {
		# O dotfiles nao usa Node: exigir node no check quebraria o bootstrap
		# em maquinas sem Node instalado.
		$source = Get-Content -Raw (Join-Path $repoRoot 'app\df\powershell\_functions.ps1')
		$source | Should Not Match '''node'''
	}

	It 'tabela final usa OK/FALHA por item' {
		$source = Get-Content -Raw (Join-Path $repoRoot 'app\df\powershell\_functions.ps1')
		$source | Should Match "'success' \{ 'OK' \}"
		$source | Should Match "'fail' \{ 'FALHA' \}"
		$source | Should Match 'RESULTADO'
	}

	It 'checkEnv retorna falso quando ha FALHA, e o bootstrap sai diferente de zero' {
		# Contrato de codigo de saida: checkEnv devolve ($failCount -eq 0) e o
		# entrypoint converte isso em excecao => exit != 0.
		$source = Get-Content -Raw (Join-Path $repoRoot 'app\df\powershell\_functions.ps1')
		$source | Should Match 'return \(\$failCount -eq 0\)'

		$bootstrap = Get-Content -Raw (Join-Path $repoRoot 'app\bootstrap\bootstrap-windows.ps1')
		$bootstrap | Should Match 'if \(!\(checkEnv\)\)'
	}
}

Describe 'helpers da identidade daneel' {
	BeforeAll {
		$script:OriginalAppData = $env:APPDATA
		$script:OriginalLocalAppData = $env:LOCALAPPDATA
		$env:APPDATA = Join-Path $TestDrive 'appdata'
		$env:LOCALAPPDATA = Join-Path $TestDrive 'localappdata'
	}
	AfterAll {
		$env:APPDATA = $script:OriginalAppData
		$env:LOCALAPPDATA = $script:OriginalLocalAppData
	}

	It 'resolve os caminhos da identidade unica (sem hostname)' {
		(Get-AutomationSigningKeyPath) | Should Be (Join-Path $env:APPDATA 'tars\automation\daneel_ed25519')
		(Get-AutomationSigningPublicKeyPath) | Should Be (Join-Path $env:APPDATA 'tars\automation\daneel_ed25519.pub')
		(Get-AutomationOpTokenPath) | Should Be (Join-Path $env:APPDATA 'tars\automation\op-sa.token')
	}

	It 'materializa o allowed_signers no diretorio de estado, fora do repo' {
		$signers = Get-AutomationAllowedSignersPath
		$signers | Should Be (Join-Path $env:LOCALAPPDATA 'dotfiles\git\allowed_signers')
		# Nunca sob um caminho que o bootstrap linka ao app/df/git versionado.
		$signers | Should Not Match ([regex]::Escape('app\df\git'))
		$signers | Should Not Be (Join-Path $env:APPDATA 'git\allowed_signers')
	}
}

Describe 'Get-ForbiddenEnvLeaks' {
	It 'reporta NOMES dos segredos presentes no processo, nunca valores' {
		$marker = 'segredo-nao-deve-vazar-123'
		$original = $env:GH_TOKEN
		$env:GH_TOKEN = $marker
		try {
			$leaks = @(Get-ForbiddenEnvLeaks)
			($leaks -contains 'GH_TOKEN') | Should Be $true
			($leaks -join ',') | Should Not Match $marker
		}
		finally {
			if ($null -eq $original) { Remove-Item Env:GH_TOKEN -ErrorAction SilentlyContinue }
			else { $env:GH_TOKEN = $original }
		}
	}

	It 'cobre os segredos proibidos exigidos (nomes)' {
		$source = Get-Content -Raw (Join-Path $repoRoot 'app\df\powershell\_functions.ps1')
		foreach ($name in 'OP_SERVICE_ACCOUNT_TOKEN', 'OP_CONNECT_HOST', 'OP_CONNECT_TOKEN', 'GH_TOKEN', 'GITHUB_TOKEN', 'SOPS_AGE_KEY') {
			$source | Should Match ([regex]::Escape("'$name'"))
		}
		$source | Should Match 'Segredos no ambiente'
	}
}

Describe 'Invoke-CheckEnvSignedCommitTest' {
	# Gate: `warning` SO quando o agente exige desbloqueio humano (agente sem
	# chaves listadas / 1Password bloqueado) ou timeout por prompt de aprovacao,
	# sempre com "requer desbloqueio" e o comando de validacao. Signer ausente,
	# chave publica ilegivel e erro real de assinatura sao `fail`.

	It 'retorna warning (nao bloqueia) quando a chave exige desbloqueio' {
		# Cenario de unlock: chave publica VALIDA cuja metade privada nao esta
		# no agent. O ssh-keygen falha rapido com "no private key found for
		# public key" -> warning, nunca fail nem hang.
		# Um blob base64 sintetico nao serve para este caso: o OpenSSH o rejeita
		# ainda no load ("Couldn't load public key ... No such file or
		# directory"), o que e um erro real de chave e, pelo gate, `fail`.
		if (-not (Get-Command ssh-keygen -ErrorAction SilentlyContinue)) {
			Set-TestInconclusive 'ssh-keygen ausente no PATH'
		}
		$privKey = Join-Path $TestDrive 'unlock-probe'
		& ssh-keygen -t ed25519 -N '' -C 'checkenv@test' -f $privKey *> $null
		$pubKey = "$privKey.pub"
		Remove-Item -Path $privKey -Force

		$result = Invoke-CheckEnvSignedCommitTest -SigningKey $pubKey -GpgFormat 'ssh' -CommitSign 'true' -GitSigningMode 'human'

		$result.Status | Should Be 'warning'
		($result.Detail -match 'requer desbloqueio') | Should Be $true
		($result.Detail -match 'valide com: ssh-keygen -Y sign -n git') | Should Be $true
	}

	It 'retorna fail quando o signer nao esta configurado' {
		$result = Invoke-CheckEnvSignedCommitTest -SigningKey '' -GitSigningMode 'human'

		$result.Status | Should Be 'fail'
		($result.Detail -match 'signer nao configurado') | Should Be $true
	}

	It 'retorna fail quando user.signingkey nao e chave publica legivel' {
		$result = Invoke-CheckEnvSignedCommitTest -SigningKey (Join-Path $TestDrive 'nao-existe') -GitSigningMode 'human'

		$result.Status | Should Be 'fail'
		($result.Detail -match 'chave publica ilegivel') | Should Be $true
	}

	It 'mantem o probe sem git commit -S e com classificacao de unlock' {
		$source = Get-Content -Raw (Join-Path $repoRoot 'app\df\powershell\_functions.ps1')
		$source | Should Match 'no private key found for public key'
		$source | Should Match 'erro real de assinatura'
	}
}
