# bootstrap/user-config.yaml
# Guia rápido (didático) – preencha aqui tudo que o wizard pergunta.
# Este arquivo fica apenas na sua máquina (é ignorado pelo Git).
# Dica: mantenha os comentários, eles explicam cada campo.
#
# Legenda de exemplos:
# - Exemplo realista      -> linha começando com EX:
# - Valor opcional vazio  -> use "" (aspas duplas) ou deixe string vazia
# - Booleans              -> true | false (minúsculo)

version: 1
profile:
  # Nome "humano" para identificar este setup/local (aparece em logs).
  # EX: "work-wsl", "desktop-windows", "notebook-venda"
  name: "CHANGE_ME"
git:
  # Nome que vai nos commits (precisa bater com o usado no GitHub).
  # EX: "Pablo Augusto"
  name: "CHANGE_ME"

  # E-mail dos commits (domínio verificado no GitHub para assinar).
  # EX: "pablo@pabloaugusto.com"
  email: "you@example.com"

  # Seu usuário do GitHub (login).
  # EX: "pabloaugusto"
  username: "your-github-user"

  # Chave pública de assinatura SSH (linha completa, começa com ssh-...).
  # Isso é chave PUBLICA (não segredo); não precisa sops/1Password.
  # Gere com: ssh-keygen -t ed25519 -C "assinatura-git"
  # Pegue a parte pública e cole aqui.
  # EX: "ssh-ed25519 AAAA_REPLACE_WITH_YOUR_PUBLIC_SSH_SIGNING_KEY"
  signing_key: "ssh-ed25519 AAAA_REPLACE_WITH_YOUR_PUBLIC_SSH_SIGNING_KEY"
paths:
  windows:
    # Caminho absoluto no Windows onde ficam os projetos no OneDrive.
    # Se vazio, o bootstrap tenta deduzir a partir da variável OneDrive.
    # EX: "D:\\OneDrive\\projects"   (note o uso de \\)
    onedrive_projects_path: ""
  wsl:
    # Raiz do OneDrive dentro do WSL (montagem do drive).
    # EX: "/mnt/d/OneDrive"
    onedrive_root: "/mnt/d/OneDrive"

    # (Opcional) Subpasta de clientes dentro do OneDrive.
    # Deixe "" se não usar.
    # EX: "clients"
    onedrive_clients_dir: ""

    # (Opcional) Subpasta de projetos dentro do OneDrive.
    # Deixe "" se não usar.
    # EX: "projects"
    onedrive_projects_dir: ""
bootstrap:
  add_user:
    # Criar usuario Linux extra (WSL) alem do usuario principal? true/false.
    # Utilidade:
    # - separar contexto pessoal x automacao/deploy
    # - reduzir risco de rodar scripts de CI/CD com seu usuario principal
    # - facilitar permissao minima por usuario
    # Na maioria dos desktops pessoais, use false.
    enabled: false

    # Nome do usuario extra (so se enabled=true).
    # Exemplo comum: "deploy" ou "automation".
    # EX: "deploy"
    username: ""

    # Hash de senha desse usuario (openssl passwd -1 'senha').
    # So e usado quando enabled=true.
    # EX: "$1$abcd1234$abcdefghijklmnopqrstuv"
    password_hash: ""
secrets:
  # Ref 1Password do Service Account (op CLI), entrada unica do bootstrap.
  # O valor real e resolvido em runtime via `op` e gravado somente em `.env.local.sops`.
  # EX: "op://secrets/dotfiles/1password/service-account"
  onepassword_service_account_ref: "op://secrets/dotfiles/1password/service-account"

  # Token GitHub dedicado ao projeto (escopo minimo repo). Preferido.
  # Esse token alimenta GH_TOKEN/GITHUB_TOKEN no env cifrado `.env.local.sops`.
  # EX: "op://secrets/dotfiles/github/token"
  github_project_pat_ref: "op://secrets/dotfiles/github/token"

  # Token GitHub full-access (só para emergências). Pode deixar vazio.
  # EX: "op://secrets/github/api/token"
  github_full_access_ref: "op://secrets/github/api/token"

  # Chave age usada pelo sops para arquivos cifrados.
  # Ela e persistida como `SOPS_AGE_KEY` para decriptar `.sops` em novos shells.
  # EX: "op://secrets/dotfiles/age/age.key"
  age_key_ref: "op://secrets/dotfiles/age/age.key"
