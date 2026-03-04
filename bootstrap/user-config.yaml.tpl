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
    # Controla se o bootstrap exige/usa OneDrive no Windows.
    # true  = executa etapa guiada de root OneDrive ANTES de criar links:
    #         - se OneDrive nao existir: instala e pede caminho base.
    #         - se existir: pergunta manter/mover path base.
    # false = ignora OneDrive e cria apenas diretorios locais de perfil.
    # EX: true
    onedrive_enabled: true
    # Raiz desejada do OneDrive no Windows (ABS).
    # Se vazio: usa root atual detectada; se nao houver setup, pergunta no wizard.
    # EX: "D:\\OneDrive"
    onedrive_root: ""
    # Se root desejada diferir da root atual, tenta migracao automatica:
    # mover dados + criar junction + atualizar root no registro (best-effort).
    # EX: true
    onedrive_auto_migrate: true
    # Pasta de clients no Windows. Pode ser ABS ou relativa a onedrive_root.
    # EX (rel): "clients" | EX (abs): "D:\\OneDrive\\clientes"
    onedrive_clients_dir: ""
    # Pasta de projects no Windows. Pode ser ABS ou relativa a onedrive_root.
    # EX (rel): "clients\\pablo\\projects" | EX (abs): "D:\\OneDrive\\projects"
    onedrive_projects_dir: ""
    # Caminho absoluto de projetos no OneDrive (Windows).
    # Se preenchido, tem prioridade sobre onedrive_projects_dir.
    # EX: "D:\\OneDrive\\clients\\pablo\\projects"
    onedrive_projects_path: ""
    # Caminhos de link no perfil Windows (origem dos symlinks criados).
    # Aceita variaveis como %USERPROFILE%.
    # EX: "%USERPROFILE%\\bin"
    links_profile_bin: "%USERPROFILE%\\bin"
    # EX: "%USERPROFILE%\\etc"
    links_profile_etc: "%USERPROFILE%\\etc"
    # EX: "%USERPROFILE%\\clients"
    links_profile_clients: "%USERPROFILE%\\clients"
    # EX: "%USERPROFILE%\\projects"
    links_profile_projects: "%USERPROFILE%\\projects"
    # Ativa links adicionais na raiz de drive (atalhos d:\* por padrao).
    # Se o drive nao existir, bootstrap apenas informa e segue.
    # EX: true
    links_drive_enabled: true
    # EX: "D:\\bin"
    links_drive_bin: "D:\\bin"
    # EX: "D:\\etc"
    links_drive_etc: "D:\\etc"
    # EX: "D:\\clients"
    links_drive_clients: "D:\\clients"
    # EX: "D:\\projects"
    links_drive_projects: "D:\\projects"
    # ----------------------------------------------------------------------
    # Links opcionais de pastas padrao do perfil para dentro do OneDrive.
    # Cada pasta tem 2 campos: *_enabled (liga/desliga) e *_target (destino).
    #
    # Regra de resolucao do *_target (IMPORTANTE):
    # - Se *_target for relativo (ex: "documents\\profile\\links"), o bootstrap
    #   concatena esse valor com a BASE abaixo.
    # - Se *_target for absoluto (ex: "D:\\OneDrive\\documents\\profile\\links"),
    #   usa o valor diretamente, sem concatenar.
    # Base atual desta config para targets relativos: "AUTO (registro OneDrive -> env OneDrive -> %USERPROFILE%\\OneDrive)"
    #
    # profile_links_migrate_content controla o comportamento de migracao:
    # - true  = migra conteudo atual da pasta para destino OneDrive antes de linkar.
    # - false = nao migra; apenas cria link (origem vira backup local).
    #
    # Exemplos reais observados no ambiente pablo:
    # - desktop  -> "desktop"
    # - documents -> "documents"
    # - downloads -> "downloads"
    # - pictures -> "Imagens"
    # - videos -> "Vídeos"
    # - music -> "Música"
    #
    # Exemplos sugeridos (quando ainda nao existe pasta no OneDrive):
    # - contacts -> "documents\\profile\\contacts"
    # - favorites -> "documents\\profile\\favorites"
    # - links -> "documents\\profile\\links"
    # ----------------------------------------------------------------------
    # Migracao de conteudo para pastas linkadas (segura):
    # true  = copia conteudo atual para destino e depois linka.
    # false = nao copia conteudo; apenas backup + link.
    profile_links_migrate_content: true
    # Documents (%USERPROFILE%\Documents).
    #   target atual: "documents"
    #   caminho final com esta config: "%USERPROFILE%\\OneDrive\\documents"
    profile_links_documents_enabled: false
    profile_links_documents_target: "documents"
    # Desktop (%USERPROFILE%\Desktop).
    #   target atual: "desktop"
    #   caminho final com esta config: "%USERPROFILE%\\OneDrive\\desktop"
    profile_links_desktop_enabled: false
    profile_links_desktop_target: "desktop"
    # Downloads (%USERPROFILE%\Downloads).
    #   target atual: "downloads"
    #   caminho final com esta config: "%USERPROFILE%\\OneDrive\\downloads"
    profile_links_downloads_enabled: false
    profile_links_downloads_target: "downloads"
    # Pictures (%USERPROFILE%\Pictures).
    #   target atual: "Imagens"
    #   caminho final com esta config: "%USERPROFILE%\\OneDrive\\Imagens"
    profile_links_pictures_enabled: false
    profile_links_pictures_target: "Imagens"
    # Videos (%USERPROFILE%\Videos).
    #   target atual: "Vídeos"
    #   caminho final com esta config: "%USERPROFILE%\\OneDrive\\Vídeos"
    profile_links_videos_enabled: false
    profile_links_videos_target: "Vídeos"
    # Music (%USERPROFILE%\Music).
    #   target atual: "Música"
    #   caminho final com esta config: "%USERPROFILE%\\OneDrive\\Música"
    profile_links_music_enabled: false
    profile_links_music_target: "Música"
    # Contacts (%USERPROFILE%\Contacts).
    #   target atual: "documents\\profile\\contacts"
    #   caminho final com esta config: "%USERPROFILE%\\OneDrive\\documents\\profile\\contacts"
    profile_links_contacts_enabled: false
    profile_links_contacts_target: "documents\\profile\\contacts"
    # Favorites (%USERPROFILE%\Favorites).
    #   target atual: "documents\\profile\\favorites"
    #   caminho final com esta config: "%USERPROFILE%\\OneDrive\\documents\\profile\\favorites"
    profile_links_favorites_enabled: false
    profile_links_favorites_target: "documents\\profile\\favorites"
    # Links (%USERPROFILE%\Links).
    #   target atual: "documents\\profile\\links"
    #   caminho final com esta config: "%USERPROFILE%\\OneDrive\\documents\\profile\\links"
    profile_links_links_enabled: false
    profile_links_links_target: "documents\\profile\\links"
  wsl:
    # Raiz do OneDrive no WSL.
    # EX: "/mnt/d/OneDrive"
    onedrive_root: "/mnt/d/OneDrive"
    # Pasta de clients no WSL: pode ser relativa (a raiz) ou absoluta.
    # EX (rel): "clients" | EX (abs): "/mnt/d/OneDrive/clients"
    onedrive_clients_dir: ""
    # Pasta de projects no WSL: pode ser relativa (a raiz) ou absoluta.
    # EX (rel): "clients/pablo/projects" | EX (abs): "/mnt/d/OneDrive/projects"
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
