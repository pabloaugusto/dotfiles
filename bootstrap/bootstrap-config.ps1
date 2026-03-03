#######################################################################################
# bootstrap-config.ps1
#
# Centralized bootstrap configuration manager.
# - Uses a simple YAML file (local, non-versioned) as single source of truth.
# - Can run guided setup in terminal.
# - Syncs derived files used by existing bootstrap flow:
#   - df/secrets/secrets-ref.yaml
#   - bootstrap/secrets/.env.local.tpl
#   - df/git/.gitconfig.local
#######################################################################################

function Get-BootstrapConfigDefaults {
	$defaults = [ordered]@{}
	$defaults['version'] = '1'
	$defaults['profile.name'] = 'CHANGE_ME'

	$defaults['git.name'] = 'CHANGE_ME'
	$defaults['git.email'] = 'you@example.com'
	$defaults['git.username'] = 'your-github-user'
	$defaults['git.signing_key'] = 'ssh-ed25519 AAAA_REPLACE_WITH_YOUR_PUBLIC_SSH_SIGNING_KEY'

	$defaults['paths.windows.onedrive_projects_path'] = ''
	$defaults['paths.wsl.onedrive_root'] = '/mnt/d/OneDrive'
	$defaults['paths.wsl.onedrive_clients_dir'] = ''
	$defaults['paths.wsl.onedrive_projects_dir'] = ''

	$defaults['bootstrap.add_user.enabled'] = 'false'
	$defaults['bootstrap.add_user.username'] = ''
	$defaults['bootstrap.add_user.password_hash'] = ''

	$defaults['secrets.onepassword_service_account_ref'] = 'op://secrets/dotfiles/1password/service-account'
	$defaults['secrets.github_project_pat_ref'] = 'op://secrets/dotfiles/github/token'
	$defaults['secrets.github_full_access_ref'] = 'op://secrets/github/api/token'
	$defaults['secrets.age_key_ref'] = 'op://secrets/dotfiles/age/age.key'
	return $defaults
}

function Convert-SimpleYamlScalar {
	param ([string]$RawValue)

	$v = $RawValue.Trim()
	if ($v -match "^'(.*)'$") { return $matches[1] }
	if ($v -match '^"(.*)"$') { return $matches[1] }
	if ($v -ieq 'true') { return 'true' }
	if ($v -ieq 'false') { return 'false' }
	if ($v -ieq 'null') { return '' }
	return $v
}

function Read-SimpleYamlAsPathMap {
	param ([string]$Path)

	$map = [ordered]@{}
	if (!(Test-Path -Path $Path -PathType Leaf)) {
		return $map
	}

	$stack = New-Object System.Collections.Generic.List[string]
	foreach ($rawLine in (Get-Content -Path $Path -ErrorAction SilentlyContinue)) {
		$line = ($rawLine -replace "`t", '  ')
		if ([string]::IsNullOrWhiteSpace($line) -or $line -match '^\s*#') {
			continue
		}
		if ($line -notmatch '^(\s*)([A-Za-z0-9_-]+):\s*(.*)$') {
			continue
		}

		$indentLen = $matches[1].Length
		if (($indentLen % 2) -ne 0) {
			continue
		}
		$level = [int]($indentLen / 2)
		$key = $matches[2]
		$valuePart = $matches[3].Trim()

		while ($stack.Count -gt $level) {
			$stack.RemoveAt($stack.Count - 1)
		}
		if ($stack.Count -eq $level) {
			$stack.Add($key)
		}
		else {
			continue
		}

		if ($valuePart -ne '') {
			$pathKey = ($stack -join '.')
			$map[$pathKey] = (Convert-SimpleYamlScalar -RawValue $valuePart)
		}
	}

	return $map
}

function Merge-BootstrapConfigWithDefaults {
	param ([hashtable]$ConfigMap)

	$merged = [ordered]@{}
	$defaults = Get-BootstrapConfigDefaults
	foreach ($k in $defaults.Keys) {
		if ($ConfigMap.Contains($k)) {
			$merged[$k] = [string]$ConfigMap[$k]
		}
		else {
			$merged[$k] = [string]$defaults[$k]
		}
	}
	return $merged
}

function Escape-YamlDoubleQuotedValue {
	param ([string]$Value)
	return ($Value -replace '\\', '\\' -replace '"', '\"')
}

function Write-BootstrapConfigYaml {
	param (
		[string]$Path,
		[hashtable]$Config
	)

	$yaml = @(
		'# bootstrap/user-config.yaml'
		'# Guia rapido (didatico) - preencha aqui tudo que o wizard pergunta.'
		'# Este arquivo fica apenas na sua maquina (ignorado pelo Git).'
		'# Dica: mantenha os comentarios para lembrar o significado de cada campo.'
		'#'
		'# Legenda de exemplos:'
		'# - EX: exemplo realista'
		'# - Opcional vazio: use ""'
		'# - Boolean: true | false'
		'version: 1'
		'profile:'
		'  # Nome "humano" para identificar o setup/local (aparece em logs).'
		'  # EX: "work-wsl", "desktop-windows", "notebook-venda"'
		("  name: ""{0}""" -f (Escape-YamlDoubleQuotedValue $Config['profile.name']))
		'git:'
		'  # Nome que vai nos commits.'
		'  # EX: "Pablo Augusto"'
		("  name: ""{0}""" -f (Escape-YamlDoubleQuotedValue $Config['git.name']))
		'  # Email usado nos commits (ideal: verificado no GitHub).'
		'  # EX: "pablo@pabloaugusto.com"'
		("  email: ""{0}""" -f (Escape-YamlDoubleQuotedValue $Config['git.email']))
		'  # Login do GitHub.'
		'  # EX: "pabloaugusto"'
		("  username: ""{0}""" -f (Escape-YamlDoubleQuotedValue $Config['git.username']))
		'  # Chave publica SSH para assinatura de commit (linha ssh-ed25519 completa).'
		'  # Isso e chave PUBLICA (nao segredo); a privada deve ficar no 1Password.'
		'  # EX: "ssh-ed25519 AAAA... user@host"'
		("  signing_key: ""{0}""" -f (Escape-YamlDoubleQuotedValue $Config['git.signing_key']))
		'paths:'
		'  windows:'
		'    # Caminho absoluto de projetos no OneDrive (Windows).'
		'    # EX: "D:\\OneDrive\\projects"'
		'    # Deixe "" para usar autodeteccao.'
		("    onedrive_projects_path: ""{0}""" -f (Escape-YamlDoubleQuotedValue $Config['paths.windows.onedrive_projects_path']))
		'  wsl:'
		'    # Raiz do OneDrive no WSL.'
		'    # EX: "/mnt/d/OneDrive"'
		("    onedrive_root: ""{0}""" -f (Escape-YamlDoubleQuotedValue $Config['paths.wsl.onedrive_root']))
		'    # Subpasta de clientes dentro da raiz (opcional).'
		'    # EX: "clients"'
		("    onedrive_clients_dir: ""{0}""" -f (Escape-YamlDoubleQuotedValue $Config['paths.wsl.onedrive_clients_dir']))
		'    # Subpasta de projetos dentro da raiz (opcional).'
		'    # EX: "projects"'
		("    onedrive_projects_dir: ""{0}""" -f (Escape-YamlDoubleQuotedValue $Config['paths.wsl.onedrive_projects_dir']))
		'bootstrap:'
		'  add_user:'
		'    # Criar usuario Linux extra no WSL (alem do principal)?'
		'    # Utilidade: separar contexto pessoal x automacao/deploy e aplicar permissao minima.'
		'    # Em desktop pessoal, normalmente deixe false.'
		'    # EX: false'
		("    enabled: {0}" -f (($Config['bootstrap.add_user.enabled']).ToLowerInvariant()))
		'    # Nome do usuario adicional (somente se enabled=true).'
		'    # Exemplo comum: "deploy" ou "automation".'
		'    # EX: "deploy"'
		("    username: ""{0}""" -f (Escape-YamlDoubleQuotedValue $Config['bootstrap.add_user.username']))
		'    # Hash de senha (openssl passwd -1 "senha"), somente se enabled=true.'
		("    password_hash: ""{0}""" -f (Escape-YamlDoubleQuotedValue $Config['bootstrap.add_user.password_hash']))
		'secrets:'
		'  # Ref do token de service account do 1Password (entrada unica do bootstrap).'
		'  # EX: "op://secrets/dotfiles/1password/service-account"'
		("  onepassword_service_account_ref: ""{0}""" -f (Escape-YamlDoubleQuotedValue $Config['secrets.onepassword_service_account_ref']))
		'  # Ref do token GitHub dedicado ao projeto (preferido).'
		'  # EX: "op://secrets/dotfiles/github/token"'
		("  github_project_pat_ref: ""{0}""" -f (Escape-YamlDoubleQuotedValue $Config['secrets.github_project_pat_ref']))
		'  # Ref de token GitHub amplo (fallback de contingencia).'
		'  # EX: "op://secrets/github/api/token"'
		("  github_full_access_ref: ""{0}""" -f (Escape-YamlDoubleQuotedValue $Config['secrets.github_full_access_ref']))
		'  # Ref da chave age usada para criptografar/decriptar arquivos .sops.'
		'  # EX: "op://secrets/dotfiles/age/age.key"'
		("  age_key_ref: ""{0}""" -f (Escape-YamlDoubleQuotedValue $Config['secrets.age_key_ref']))
	)

	$targetDir = Split-Path -Path $Path -Parent
	if ($targetDir -and !(Test-Path -Path $targetDir)) {
		New-Item -Path $targetDir -ItemType Directory -Force | Out-Null
	}
	Set-Content -Path $Path -Value $yaml
}

function Test-BootstrapConfigFilled {
	param ([hashtable]$Config)

	$requiredKeys = @(
		'git.name',
		'git.email',
		'git.username',
		'git.signing_key',
		'secrets.onepassword_service_account_ref',
		'secrets.github_project_pat_ref',
		'secrets.github_full_access_ref',
		'secrets.age_key_ref'
	)

	foreach ($k in $requiredKeys) {
		$v = [string]$Config[$k]
		if ([string]::IsNullOrWhiteSpace($v)) {
			return $false
		}
		if ($v -match 'CHANGE_ME|REPLACE_WITH|you@example\.com|your-github-user|AAAA_REPLACE') {
			return $false
		}
	}

	if (($Config['bootstrap.add_user.enabled']).ToLowerInvariant() -eq 'true') {
		if ([string]::IsNullOrWhiteSpace([string]$Config['bootstrap.add_user.username']) -or
			[string]::IsNullOrWhiteSpace([string]$Config['bootstrap.add_user.password_hash'])) {
			return $false
		}
	}

	return $true
}

function Read-ConfigPrompt {
	param (
		[string]$Label,
		[string]$CurrentValue,
		[switch]$AllowEmpty
	)

	$display = if ([string]::IsNullOrWhiteSpace($CurrentValue)) { '(vazio)' } else { $CurrentValue }
	$typed = Read-Host -Prompt "$Label [$display]"
	if ([string]::IsNullOrWhiteSpace($typed)) {
		if ($AllowEmpty) { return '' }
		return $CurrentValue
	}
	return $typed.Trim()
}

function Read-BooleanPrompt {
	param (
		[string]$Label,
		[string]$CurrentValue
	)

	$defaultLabel = if (($CurrentValue).ToLowerInvariant() -eq 'true') { 'Y' } else { 'N' }
	while ($true) {
		$typed = Read-Host -Prompt "$Label (Y/N) [$defaultLabel]"
		if ([string]::IsNullOrWhiteSpace($typed)) {
			return if ($defaultLabel -eq 'Y') { 'true' } else { 'false' }
		}
		switch -Regex ($typed.Trim()) {
			'^(y|yes|s|sim)$' { return 'true' }
			'^(n|no|nao|não)$' { return 'false' }
			default { Write-Host "Resposta inválida. Use Y ou N." }
		}
	}
}

function Invoke-BootstrapConfigWizard {
	param ([hashtable]$Config)

	Write-Host "`nConfiguração guiada do bootstrap (YAML central)."
	Write-Host "Pressione ENTER para manter o valor atual."

	$Config['profile.name'] = Read-ConfigPrompt -Label 'Nome do perfil local (apelido). EX: work-wsl | desktop-windows' -CurrentValue $Config['profile.name']
	$Config['git.name'] = Read-ConfigPrompt -Label 'Git name (nome exibido nos commits). EX: Pablo Augusto' -CurrentValue $Config['git.name']
	$Config['git.email'] = Read-ConfigPrompt -Label 'Git email (ideal: verificado no GitHub). EX: pablo@pabloaugusto.com' -CurrentValue $Config['git.email']
	$Config['git.username'] = Read-ConfigPrompt -Label 'Git username (login GitHub). EX: pabloaugusto' -CurrentValue $Config['git.username']
	$Config['git.signing_key'] = Read-ConfigPrompt -Label 'Chave publica SSH para assinatura. EX: ssh-ed25519 AAA... user@host' -CurrentValue $Config['git.signing_key']

	$Config['paths.windows.onedrive_projects_path'] = Read-ConfigPrompt -Label 'Windows OneDrive projects path (abs, ex: D:\\OneDrive\\projects ou vazio p/ auto)' -CurrentValue $Config['paths.windows.onedrive_projects_path'] -AllowEmpty
	$Config['paths.wsl.onedrive_root'] = Read-ConfigPrompt -Label 'WSL OneDrive root (ex: /mnt/d/OneDrive)' -CurrentValue $Config['paths.wsl.onedrive_root']
	$Config['paths.wsl.onedrive_clients_dir'] = Read-ConfigPrompt -Label 'WSL clients dir (subpasta, ex: clients, ou vazio)' -CurrentValue $Config['paths.wsl.onedrive_clients_dir'] -AllowEmpty
	$Config['paths.wsl.onedrive_projects_dir'] = Read-ConfigPrompt -Label 'WSL projects dir (subpasta, ex: projects, ou vazio)' -CurrentValue $Config['paths.wsl.onedrive_projects_dir'] -AllowEmpty

	$Config['bootstrap.add_user.enabled'] = Read-BooleanPrompt -Label 'Criar usuario extra no WSL? (isolamento para deploy/automacao)' -CurrentValue $Config['bootstrap.add_user.enabled']
	if (($Config['bootstrap.add_user.enabled']).ToLowerInvariant() -eq 'true') {
		$Config['bootstrap.add_user.username'] = Read-ConfigPrompt -Label 'Usuário extra (ex: deploy)' -CurrentValue $Config['bootstrap.add_user.username']
		$Config['bootstrap.add_user.password_hash'] = Read-ConfigPrompt -Label 'Password hash (openssl passwd -1 \"senha\")' -CurrentValue $Config['bootstrap.add_user.password_hash']
	}
	else {
		$Config['bootstrap.add_user.username'] = ''
		$Config['bootstrap.add_user.password_hash'] = ''
	}

	$Config['secrets.onepassword_service_account_ref'] = Read-ConfigPrompt -Label 'Ref 1Password service account (op://.../service-account)' -CurrentValue $Config['secrets.onepassword_service_account_ref']
	$Config['secrets.github_project_pat_ref'] = Read-ConfigPrompt -Label 'Ref GitHub token dedicado (project-pat, op://secrets/dotfiles/github/token)' -CurrentValue $Config['secrets.github_project_pat_ref']
	$Config['secrets.github_full_access_ref'] = Read-ConfigPrompt -Label 'Ref GitHub full-access (fallback, pode ficar vazio)' -CurrentValue $Config['secrets.github_full_access_ref']
	$Config['secrets.age_key_ref'] = Read-ConfigPrompt -Label 'Ref SOPS age key (op://.../age.key)' -CurrentValue $Config['secrets.age_key_ref']

	return $Config
}

function Sync-BootstrapDerivedFiles {
	param (
		[hashtable]$Config,
		[string]$DotFilesDirectory
	)

	$secretsRefPath = Join-Path $DotFilesDirectory 'df\secrets\secrets-ref.yaml'
	$envTplPath = Join-Path $DotFilesDirectory 'bootstrap\secrets\.env.local.tpl'
	$gitLocalPath = Join-Path $DotFilesDirectory 'df\git\.gitconfig.local'

	$secretsRef = @(
		'---'
		'# Secrets do repositório dotfiles (gerado a partir de bootstrap/user-config.yaml)'
		'1password:'
		("  service-account: ""{0}""" -f $Config['secrets.onepassword_service_account_ref'])
		'github:'
		("  full-access-token: ""{0}""" -f $Config['secrets.github_full_access_ref'])
		("  project-pat: ""{0}""" -f $Config['secrets.github_project_pat_ref'])
		'age:'
		("  key: ""{0}""" -f $Config['secrets.age_key_ref'])
	)
	Set-Content -Path $secretsRefPath -Value $secretsRef

	$envTpl = @(
		'# Runtime secrets template resolved by 1Password (`op inject`).'
		'# Bootstrap persists this material encrypted at ~/.env.local.sops.'
		'# Generated from bootstrap/user-config.yaml'
		("export OP_SERVICE_ACCOUNT_TOKEN=""{0}""" -f $Config['secrets.onepassword_service_account_ref'])
		("export GH_TOKEN=""{0}""" -f $Config['secrets.github_project_pat_ref'])
		("export GITHUB_TOKEN=""{0}""" -f $Config['secrets.github_project_pat_ref'])
		("export SOPS_AGE_KEY=""{0}""" -f $Config['secrets.age_key_ref'])
	)
	Set-Content -Path $envTplPath -Value $envTpl

	$gitLocal = @(
		'# -----------------------------------------------------------------------------'
		'# ~/.config/git/.gitconfig.local (local, nao versionado)'
		'# Generated from bootstrap/user-config.yaml'
		'#'
		'# Objetivo: identidade Git local e chave publica de assinatura.'
		'#'
		'# IMPORTANTE:'
		'# - Nao coloque tokens, senhas ou chaves privadas aqui.'
		'# - "signingkey" abaixo e uma chave PUBLICA SSH (nao segredo).'
		'# - A chave privada continua protegida no 1Password SSH Agent.'
		'# -----------------------------------------------------------------------------'
		''
		'[user]'
		'    # Nome exibido como autor nos commits.'
		("    name = {0}" -f $Config['git.name'])
		''
		'    # Email do autor dos commits.'
		("    email = {0}" -f $Config['git.email'])
		''
		'    # Username usado por alguns aliases/fluxos GitHub.'
		("    username = {0}" -f $Config['git.username'])
		''
		'    # Chave PUBLICA SSH usada para identificar assinaturas de commit.'
		'    # Formato esperado: ssh-ed25519 AAAA...'
		("    signingkey = {0}" -f $Config['git.signing_key'])
	)
	Set-Content -Path $gitLocalPath -Value $gitLocal

	# Export for current bootstrap process (consumed by windows/wsl bootstrap scripts).
	if ([string]::IsNullOrWhiteSpace($Config['paths.windows.onedrive_projects_path'])) {
		Remove-Item Env:DOTFILES_ONEDRIVE_PROJECTS_PATH -ErrorAction SilentlyContinue
	}
	else {
		$Env:DOTFILES_ONEDRIVE_PROJECTS_PATH = $Config['paths.windows.onedrive_projects_path']
	}

	$Env:DOTFILES_ONEDRIVE_ROOT = $Config['paths.wsl.onedrive_root']
	if ([string]::IsNullOrWhiteSpace($Config['paths.wsl.onedrive_clients_dir'])) {
		Remove-Item Env:DOTFILES_ONEDRIVE_CLIENTS_DIR -ErrorAction SilentlyContinue
	}
	else {
		$Env:DOTFILES_ONEDRIVE_CLIENTS_DIR = $Config['paths.wsl.onedrive_clients_dir']
	}
	if ([string]::IsNullOrWhiteSpace($Config['paths.wsl.onedrive_projects_dir'])) {
		Remove-Item Env:DOTFILES_ONEDRIVE_PROJECTS_DIR -ErrorAction SilentlyContinue
	}
	else {
		$Env:DOTFILES_ONEDRIVE_PROJECTS_DIR = $Config['paths.wsl.onedrive_projects_dir']
	}

	if (($Config['bootstrap.add_user.enabled']).ToLowerInvariant() -eq 'true') {
		$Env:DOTFILES_ADD_USER = $Config['bootstrap.add_user.username']
		$Env:DOTFILES_ADD_USER_PASS_HASH = $Config['bootstrap.add_user.password_hash']
	}
	else {
		Remove-Item Env:DOTFILES_ADD_USER -ErrorAction SilentlyContinue
		Remove-Item Env:DOTFILES_ADD_USER_PASS_HASH -ErrorAction SilentlyContinue
	}
}

function Ensure-BootstrapConfigReady {
	param ([string]$DotFilesDirectory)

	$templatePath = Join-Path $DotFilesDirectory 'bootstrap\user-config.yaml.tpl'
	$configPath = Join-Path $DotFilesDirectory 'bootstrap\user-config.yaml'

	if (!(Test-Path -Path $templatePath -PathType Leaf)) {
		throw "Config template not found: $templatePath"
	}

	if (!(Test-Path -Path $configPath -PathType Leaf)) {
		Copy-Item -Path $templatePath -Destination $configPath -Force
		Write-Warning "Arquivo de config local criado em: $configPath"
	}

	$config = Merge-BootstrapConfigWithDefaults (Read-SimpleYamlAsPathMap -Path $configPath)
	$isFilled = Test-BootstrapConfigFilled -Config $config

	if ($isFilled) {
		$choice = Read-Host -Prompt "Config YAML ja preenchido. Escolha: 1=usar como esta, 2=sobrescrever em modo guiado"
		if ($choice -eq '2') {
			$config = Invoke-BootstrapConfigWizard -Config $config
			Write-BootstrapConfigYaml -Path $configPath -Config $config
		}
	}
	else {
		$choice = Read-Host -Prompt "Config YAML incompleto. Escolha: 1=preencher agora em modo guiado, 2=preencher manualmente e abortar"
		if ($choice -eq '1') {
			$config = Invoke-BootstrapConfigWizard -Config $config
			Write-BootstrapConfigYaml -Path $configPath -Config $config
		}
		else {
			Write-Warning "Preencha manualmente: $configPath e execute o bootstrap novamente."
			return $false
		}
	}

	$config = Merge-BootstrapConfigWithDefaults (Read-SimpleYamlAsPathMap -Path $configPath)
	if (!(Test-BootstrapConfigFilled -Config $config)) {
		Write-Warning "Config YAML ainda incompleto. Ajuste manualmente: $configPath"
		return $false
	}

	Sync-BootstrapDerivedFiles -Config $config -DotFilesDirectory $DotFilesDirectory
	Write-Output "Config central aplicada com sucesso a partir de: $configPath"
	return $true
}
