# =============================================================================
# bootstrap/user-config.yaml
# Configuracao local do bootstrap
# =============================================================================
#
# Este formato e compartilhado entre:
# - bootstrap/user-config.yaml.tpl
# - bootstrap/user-config.yaml
# - bootstrap/bootstrap-config.ps1
#
# O bootstrap renderiza o user-config local a partir deste mesmo layout,
# evitando drift entre script, template e arquivo final.
#
# Regra principal desta configuracao: prefira SEMPRE caminhos absolutos
# e canonicos. Use caminho relativo apenas em ultimo caso.
#
# Por que evitar relativo, alias e symlink como fonte de verdade:
# - o destino final passa a depender de outra base implicita
# - mudar a root pode redirecionar varios links sem ficar obvio no arquivo
# - symlinks e atalhos podem mascarar drift e apontar para destinos antigos
# - variaveis de ambiente exigem expansao extra e falham se houver typo
# - existe um pequeno custo extra de resolucao a cada bootstrap
#
# Como ler os nomes:
# - *_root : raiz/base principal
# - *_dir  : nome historico; aceita absoluto e deve preferir absoluto
# - *_path : caminho absoluto explicito; quando existir, normalmente e o preferido
version: @@VERSION@@

# =============================================================================
# 1. Identificacao desta maquina
# =============================================================================
profile:
  # Nome livre para identificar este setup em logs e mensagens do bootstrap.
  name: "@@PROFILE_NAME@@"

# =============================================================================
# 2. Identidade Git
# =============================================================================
git:
  # Nome usado nos commits.
  name: "@@GIT_NAME@@"

  # Email usado nos commits.
  email: "@@GIT_EMAIL@@"

  # Username/login no GitHub.
  username: "@@GIT_USERNAME@@"

  # Chave PUBLICA usada para assinatura SSH de commits.
  # A chave privada deve ficar no 1Password.
  signing_key: "@@GIT_SIGNING_KEY@@"

  # Ref opcional do 1Password para a chave PUBLICA SSH do signer tecnico
  # de automacao usado por worktrees/agentes.
  # Exemplo: "op://secrets/dotfiles/git-automation/public key"
  # Isso facilita rotacao sem espalhar configuracao manual.
  automation_signing_key_ref: "@@GIT_AUTOMATION_SIGNING_KEY_REF@@"

# =============================================================================
# 3. Caminhos e links do Windows
# =============================================================================
paths:
  windows:
    # -------------------------------------------------------------------------
    # 3.1 Base do OneDrive no Windows
    # -------------------------------------------------------------------------
    # true  = o bootstrap usa OneDrive como base para os links.
    # false = o bootstrap ignora OneDrive e trabalha so com pastas locais.
    onedrive_enabled: @@WINDOWS_ONEDRIVE_ENABLED@@

    # Raiz canonica do OneDrive no Windows.
    # Prefira sempre o caminho absoluto real da maquina.
    # Exemplo: "D:\\onedrive"
    onedrive_root: "@@WINDOWS_ONEDRIVE_ROOT@@"

    # Se a raiz configurada acima for diferente da raiz atual,
    # o bootstrap tenta migrar automaticamente.
    onedrive_auto_migrate: @@WINDOWS_ONEDRIVE_AUTO_MIGRATE@@

    # -------------------------------------------------------------------------
    # 3.2 Clients e projects dentro do OneDrive
    # -------------------------------------------------------------------------
    # Nome historico: aceita relativo, mas o recomendado e ABSOLUTO.
    # Exemplo recomendado: "D:\\onedrive\\clients"
    onedrive_clients_dir: "@@WINDOWS_ONEDRIVE_CLIENTS_DIR@@"

    # Fallback/legado para projects.
    # Se puder, deixe vazio e use `onedrive_projects_path` com valor absoluto.
    # So use relativo aqui como ultimo caso.
    onedrive_projects_dir: "@@WINDOWS_ONEDRIVE_PROJECTS_DIR@@"

    # Campo preferido para projects: caminho absoluto e canonico.
    # Exemplo recomendado: "D:\\onedrive\\clients\\seu-usuario\\projects"
    onedrive_projects_path: "@@WINDOWS_ONEDRIVE_PROJECTS_PATH@@"

    # -------------------------------------------------------------------------
    # 3.3 Links criados dentro do perfil do usuario
    # -------------------------------------------------------------------------
    # Estes campos definem ONDE o link sera criado.
    # Prefira caminho absoluto. Use %USERPROFILE% so em ultimo caso.
    links_profile_bin: "@@WINDOWS_LINKS_PROFILE_BIN@@"
    links_profile_etc: "@@WINDOWS_LINKS_PROFILE_ETC@@"
    links_profile_clients: "@@WINDOWS_LINKS_PROFILE_CLIENTS@@"
    links_profile_projects: "@@WINDOWS_LINKS_PROFILE_PROJECTS@@"

    # -------------------------------------------------------------------------
    # 3.4 Links extras na raiz do drive
    # -------------------------------------------------------------------------
    links_drive_enabled: @@WINDOWS_LINKS_DRIVE_ENABLED@@
    links_drive_bin: "@@WINDOWS_LINKS_DRIVE_BIN@@"
    links_drive_etc: "@@WINDOWS_LINKS_DRIVE_ETC@@"
    links_drive_clients: "@@WINDOWS_LINKS_DRIVE_CLIENTS@@"
    links_drive_projects: "@@WINDOWS_LINKS_DRIVE_PROJECTS@@"

    # -------------------------------------------------------------------------
    # 3.5 Pastas padrao do perfil que podem virar links para o OneDrive
    # -------------------------------------------------------------------------
    # Prefira sempre caminho absoluto completo em cada *_target.
    # Use target relativo apenas quando voce quiser depender conscientemente
    # de onedrive_root.
    # Base atual usada caso voce ainda opte por relativo:
    # @@RELATIVE_TARGET_BASE_HINT@@
    #
    # true  = tenta copiar/mover o conteudo atual antes de criar o link
    # false = nao migra automaticamente; preserva backup local e cria o link
    profile_links_migrate_content: @@WINDOWS_PROFILE_LINKS_MIGRATE_CONTENT@@

    # Documents do perfil.
    # Destino resolvido hoje: @@WINDOWS_PROFILE_LINKS_DOCUMENTS_PREVIEW@@
    profile_links_documents_enabled: @@WINDOWS_PROFILE_LINKS_DOCUMENTS_ENABLED@@
    profile_links_documents_target: "@@WINDOWS_PROFILE_LINKS_DOCUMENTS_TARGET@@"

    # Desktop do perfil.
    # Destino resolvido hoje: @@WINDOWS_PROFILE_LINKS_DESKTOP_PREVIEW@@
    profile_links_desktop_enabled: @@WINDOWS_PROFILE_LINKS_DESKTOP_ENABLED@@
    profile_links_desktop_target: "@@WINDOWS_PROFILE_LINKS_DESKTOP_TARGET@@"

    # Downloads do perfil.
    # Destino resolvido hoje: @@WINDOWS_PROFILE_LINKS_DOWNLOADS_PREVIEW@@
    profile_links_downloads_enabled: @@WINDOWS_PROFILE_LINKS_DOWNLOADS_ENABLED@@
    profile_links_downloads_target: "@@WINDOWS_PROFILE_LINKS_DOWNLOADS_TARGET@@"

    # Pictures do perfil.
    # Destino resolvido hoje: @@WINDOWS_PROFILE_LINKS_PICTURES_PREVIEW@@
    profile_links_pictures_enabled: @@WINDOWS_PROFILE_LINKS_PICTURES_ENABLED@@
    profile_links_pictures_target: "@@WINDOWS_PROFILE_LINKS_PICTURES_TARGET@@"

    # Videos do perfil.
    # Destino resolvido hoje: @@WINDOWS_PROFILE_LINKS_VIDEOS_PREVIEW@@
    profile_links_videos_enabled: @@WINDOWS_PROFILE_LINKS_VIDEOS_ENABLED@@
    profile_links_videos_target: "@@WINDOWS_PROFILE_LINKS_VIDEOS_TARGET@@"

    # Music do perfil.
    # Destino resolvido hoje: @@WINDOWS_PROFILE_LINKS_MUSIC_PREVIEW@@
    profile_links_music_enabled: @@WINDOWS_PROFILE_LINKS_MUSIC_ENABLED@@
    profile_links_music_target: "@@WINDOWS_PROFILE_LINKS_MUSIC_TARGET@@"

    # Contacts do perfil.
    # Destino resolvido hoje: @@WINDOWS_PROFILE_LINKS_CONTACTS_PREVIEW@@
    profile_links_contacts_enabled: @@WINDOWS_PROFILE_LINKS_CONTACTS_ENABLED@@
    profile_links_contacts_target: "@@WINDOWS_PROFILE_LINKS_CONTACTS_TARGET@@"

    # Favorites do perfil.
    # Destino resolvido hoje: @@WINDOWS_PROFILE_LINKS_FAVORITES_PREVIEW@@
    profile_links_favorites_enabled: @@WINDOWS_PROFILE_LINKS_FAVORITES_ENABLED@@
    profile_links_favorites_target: "@@WINDOWS_PROFILE_LINKS_FAVORITES_TARGET@@"

    # Links do perfil.
    # Destino resolvido hoje: @@WINDOWS_PROFILE_LINKS_LINKS_PREVIEW@@
    profile_links_links_enabled: @@WINDOWS_PROFILE_LINKS_LINKS_ENABLED@@
    profile_links_links_target: "@@WINDOWS_PROFILE_LINKS_LINKS_TARGET@@"

  # ===========================================================================
  # 4. Caminhos equivalentes no WSL
  # ===========================================================================
  wsl:
    # Raiz canonica do OneDrive no WSL.
    # Prefira caminho absoluto real, ex: "/mnt/d/onedrive"
    onedrive_root: "@@WSL_ONEDRIVE_ROOT@@"

    # Nome historico: aceita relativo, mas o recomendado e ABSOLUTO.
    # Exemplo recomendado: "/mnt/d/onedrive/clients"
    onedrive_clients_dir: "@@WSL_ONEDRIVE_CLIENTS_DIR@@"

    # Nome historico: aceita relativo, mas o recomendado e ABSOLUTO.
    # Exemplo recomendado: "/mnt/d/onedrive/clients/seu-usuario/projects"
    onedrive_projects_dir: "@@WSL_ONEDRIVE_PROJECTS_DIR@@"

# =============================================================================
# 5. Bootstrap extra no WSL
# =============================================================================
bootstrap:
  add_user:
    # Criar um usuario Linux extra no WSL?
    enabled: @@BOOTSTRAP_ADD_USER_ENABLED@@

    # Nome do usuario adicional.
    username: "@@BOOTSTRAP_ADD_USER_USERNAME@@"

    # Hash da senha do usuario adicional.
    # Exemplo de geracao: openssl passwd -1 "sua-senha"
    password_hash: "@@BOOTSTRAP_ADD_USER_PASSWORD_HASH@@"

# =============================================================================
# 6. Segredos e refs do 1Password
# =============================================================================
secrets:
  # Token principal de service account do 1Password para o bootstrap.
  onepassword_service_account_ref: "@@SECRETS_ONEPASSWORD_SERVICE_ACCOUNT_REF@@"

  # Token GitHub preferencial para este projeto.
  github_project_pat_ref: "@@SECRETS_GITHUB_PROJECT_PAT_REF@@"

  # Primeiro fallback quando o token dedicado do projeto nao resolver o bloqueio.
  github_full_access_ref: "@@SECRETS_GITHUB_FULL_ACCESS_REF@@"

  # Contingencia final para bloqueios que persistirem apos o fallback anterior.
  github_full_access_fallback_ref: "@@SECRETS_GITHUB_FULL_ACCESS_FALLBACK_REF@@"

  # Chave age usada pelo sops.
  age_key_ref: "@@SECRETS_AGE_KEY_REF@@"
