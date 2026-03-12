$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $here '..\..')).Path
. (Join-Path $repoRoot 'app\df\powershell\_functions.ps1')

Describe 'Get-1PasswordRefReadPolicy' {
	It 'trata o fallback Personal como contingencia humana final' {
		$result = Get-1PasswordRefReadPolicy -Ref 'op://Personal/github/token-full-access' -UserType ''
		$result | Should Be 'human-contingency'
	}

	It 'mantem refs do projeto como obrigatorios' {
		$result = Get-1PasswordRefReadPolicy -Ref 'op://secrets/dotfiles/github/token' -UserType 'SERVICE_ACCOUNT'
		$result | Should Be 'required'
	}
}

Describe 'Sync-WindowsSshHomeLayout' {
	It 'materializa ~/.ssh como diretorio real e migra runtime local do repo' {
		$repoSsh = Join-Path $TestDrive 'repo-ssh'
		$homeSsh = Join-Path $TestDrive 'home\.ssh'

		New-Item -ItemType Directory -Path (Join-Path $repoSsh '1Password') -Force | Out-Null
		Set-Content -Path (Join-Path $repoSsh 'config') -Value 'base-config'
		Set-Content -Path (Join-Path $repoSsh 'config.windows') -Value 'windows-config'
		Set-Content -Path (Join-Path $repoSsh 'config.unix') -Value 'unix-config'
		Set-Content -Path (Join-Path $repoSsh 'authorized_keys') -Value 'authorized'
		Set-Content -Path (Join-Path $repoSsh '1Password\config') -Value 'onepassword-config'
		Set-Content -Path (Join-Path $repoSsh 'known_hosts') -Value 'github.com ssh-ed25519 AAAATEST'

		Add-Symlink -from $homeSsh -to $repoSsh

		Sync-WindowsSshHomeLayout -HomeSshPath $homeSsh -RepoSshPath $repoSsh

		$homeItem = Get-Item -Path $homeSsh -Force -ErrorAction Stop
		$homeItem.PSIsContainer | Should Be $true
		$homeItem.LinkType | Should Be $null

		(Get-Content -Path (Join-Path $homeSsh 'config') -Raw) | Should Match 'base-config'
		(Get-Content -Path (Join-Path $homeSsh 'config.local') -Raw) | Should Match 'windows-config'
		(Get-Content -Path (Join-Path $homeSsh '1Password\config') -Raw) | Should Match 'onepassword-config'
		(Get-Content -Path (Join-Path $homeSsh 'known_hosts') -Raw) | Should Match 'github.com ssh-ed25519 AAAATEST'

		Test-Path -Path (Join-Path $repoSsh 'known_hosts') | Should Be $false
	}
}
