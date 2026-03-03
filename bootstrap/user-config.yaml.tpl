# bootstrap/user-config.yaml
# Guia rapido (didatico) - preencha aqui tudo que o wizard pergunta.
# Este arquivo fica apenas na sua maquina (ignorado pelo Git).
# Dica: mantenha os comentarios para lembrar o significado de cada campo.
#
# Legenda de exemplos:
# - EX: exemplo realista
# - Opcional vazio: use ""
# - Boolean: true | false
version: 1
profile:
  # Nome "humano" para identificar o setup/local (aparece em logs).
  # EX: "work-wsl", "desktop-windows", "notebook-venda"
  name: "CHANGE_ME"
git:
  # Nome que vai nos commits.
  # EX: "Pablo Augusto"
  name: "CHANGE_ME"
  # Email usado nos commits (ideal: verificado no GitHub).
  # EX: "pablo@pabloaugusto.com"
  email: "you@example.com"
  # Login do GitHub.
  # EX: "pabloaugusto"
  username: "your-github-user"
  # Chave publica SSH para assinatura de commit (linha ssh-ed25519 completa).
  # Isso e chave PUBLICA (nao segredo); a privada deve ficar no 1Password.
  # EX: "ssh-ed25519 AAAA... user@host"
  signing_key: "ssh-ed25519 AAAA_REPLACE_WITH_YOUR_PUBLIC_SSH_SIGNING_KEY"
paths:
  windows:
    # Caminho absoluto de projetos no OneDrive (Windows).
    # EX: "D:\\OneDrive\\projects"
    # Deixe "" para usar autodeteccao.
    onedrive_projects_path: ""
  wsl:
    # Raiz do OneDrive no WSL.
    # EX: "/mnt/d/OneDrive"
    onedrive_root: "/mnt/d/OneDrive"
    # Subpasta de clientes dentro da raiz (opcional).
    # EX: "clients"
    onedrive_clients_dir: ""
    # Subpasta de projetos dentro da raiz (opcional).
    # EX: "projects"
    onedrive_projects_dir: ""
bootstrap:
  add_user:
    # Criar usuario Linux extra no WSL (alem do principal)?
    # Utilidade: separar contexto pessoal x automacao/deploy e aplicar permissao minima.
    # Em desktop pessoal, normalmente deixe false.
    # EX: false
    enabled: false
    # Nome do usuario adicional (somente se enabled=true).
    # Exemplo comum: "deploy" ou "automation".
    # EX: "deploy"
    username: ""
    # Hash de senha (openssl passwd -1 "senha"), somente se enabled=true.
    password_hash: ""
secrets:
  # Ref do token de service account do 1Password (entrada unica do bootstrap).
  # EX: "op://secrets/dotfiles/1password/service-account"
  onepassword_service_account_ref: "op://secrets/dotfiles/1password/service-account"
  # Ref do token GitHub dedicado ao projeto (preferido).
  # EX: "op://secrets/dotfiles/github/token"
  github_project_pat_ref: "op://secrets/dotfiles/github/token"
  # Ref de token GitHub amplo (fallback de contingencia).
  # EX: "op://secrets/github/api/token"
  github_full_access_ref: "op://secrets/github/api/token"
  # Ref da chave age usada para criptografar/decriptar arquivos .sops.
  # EX: "op://secrets/dotfiles/age/age.key"
  age_key_ref: "op://secrets/dotfiles/age/age.key"
