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
			'helm', 'flux', 'cloudflared', 'direnv', 'node', 'python') {
			$source | Should Match ([regex]::Escape("'$bin'"))
		}
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

Describe 'Invoke-CheckEnvSignedCommitTest' {
	It 'retorna warning (nao bloqueia) quando a chave exige desbloqueio' {
		# Chave publica sintetica sem chave privada no agent: ssh-keygen deve
		# falhar rapido, e o resultado tem que ser aviso, nunca fail nem hang.
		$pubKey = Join-Path $TestDrive 'signing.pub'
		Set-Content -Path $pubKey -Value 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINotARealKeyJustForTests checkenv@test'

		$result = Invoke-CheckEnvSignedCommitTest -SigningKey $pubKey -GpgFormat 'ssh' -CommitSign 'true' -GitSigningMode 'human'

		$result.Status | Should Be 'warning'
		($result.Detail -match 'requer desbloqueio') | Should Be $true
	}
}
