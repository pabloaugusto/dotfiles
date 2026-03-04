# OneDrive (Windows) - fluxo completo de paths e links

Guia operacional do modelo de OneDrive aplicado no bootstrap Windows.

Fluxo macro/orquestração do bootstrap (incluindo subfluxo OneDrive):

- `./bootstrap-flow.md` (seção **"5) Subfluxo OneDrive (Windows)"**)

## 1) Campos de configuracao que controlam a linkagem

Arquivo: `bootstrap/user-config.yaml` (secao `paths.windows`).

- `onedrive_enabled`: liga/desliga o modo OneDrive no bootstrap.
- `onedrive_root`: root desejada do OneDrive (absoluta). Se vazio, tenta auto-detect.
- `onedrive_auto_migrate`: tenta migracao automatica da root (best-effort).
- `onedrive_clients_dir`: destino de `clients` (relativo a root ou absoluto).
- `onedrive_projects_dir`: destino de `projects` (relativo a root ou absoluto).
- `onedrive_projects_path`: override absoluto com prioridade maxima para `projects`.
- `links_profile_bin|etc|clients|projects`: caminhos origem no perfil do usuario.
- `links_drive_enabled`: ativa/desativa atalhos extras no drive raiz.
- `links_drive_bin|etc|clients|projects`: caminhos desses atalhos no drive.
- `profile_links_migrate_content`: controla se migra conteudo antes de criar links de pastas padrao.
- `profile_links_<pasta>_enabled`: ativa/desativa link de pasta padrao do perfil.
- `profile_links_<pasta>_target`: destino dentro do OneDrive para cada pasta.

Pastas suportadas hoje:

- `documents`, `desktop`, `downloads`, `pictures`, `videos`, `music`, `contacts`, `favorites`, `links`.

## 1.1) Pre-requisito obrigatorio antes dos links

Quando `onedrive_enabled=true`, o bootstrap SEMPRE executa primeiro a etapa de root do OneDrive:

1. detecta se OneDrive esta instalado;
2. se nao estiver, instala (`winget`) e pede o path base desejado;
3. se ja estiver, mostra root atual e pergunta se deseja mover;
4. se root mudar e `onedrive_auto_migrate=true`, migra dados e aplica ajuste de root (best-effort);
5. so depois disso continua para criar links que dependem do OneDrive.

## 2) Exemplo completo (padrao recomendado)

```yaml
paths:
  windows:
    onedrive_enabled: true
    onedrive_root: "D:\\OneDrive"
    onedrive_auto_migrate: true
    onedrive_clients_dir: "clients"
    onedrive_projects_dir: "clients\\pablo\\projects"
    onedrive_projects_path: ""
    links_profile_bin: "%USERPROFILE%\\bin"
    links_profile_etc: "%USERPROFILE%\\etc"
    links_profile_clients: "%USERPROFILE%\\clients"
    links_profile_projects: "%USERPROFILE%\\projects"
    links_drive_enabled: true
    links_drive_bin: "D:\\bin"
    links_drive_etc: "D:\\etc"
    links_drive_clients: "D:\\clients"
    links_drive_projects: "D:\\projects"
    profile_links_migrate_content: true
    profile_links_documents_enabled: true
    profile_links_documents_target: "documents"
    profile_links_desktop_enabled: true
    profile_links_desktop_target: "desktop"
    profile_links_downloads_enabled: true
    profile_links_downloads_target: "downloads"
    profile_links_pictures_enabled: true
    profile_links_pictures_target: "Imagens"
    profile_links_videos_enabled: true
    profile_links_videos_target: "Vídeos"
    profile_links_music_enabled: true
    profile_links_music_target: "Música"
    profile_links_contacts_enabled: true
    profile_links_contacts_target: "documents\\profile\\contacts"
    profile_links_favorites_enabled: true
    profile_links_favorites_target: "documents\\profile\\favorites"
    profile_links_links_enabled: true
    profile_links_links_target: "documents\\profile\\links"
```

Resultado esperado (usuario `pablo`):

- `%USERPROFILE%\\bin` -> `D:\\OneDrive\\bin`
- `%USERPROFILE%\\etc` -> `D:\\OneDrive\\etc`
- `%USERPROFILE%\\clients` -> `D:\\OneDrive\\clients`
- `%USERPROFILE%\\projects` -> `D:\\OneDrive\\clients\\pablo\\projects`
- `%USERPROFILE%\\Documents` -> `D:\\OneDrive\\documents` (quando `profile_links_documents_enabled=true`)
- `%USERPROFILE%\\Desktop` -> `D:\\OneDrive\\desktop` (quando `profile_links_desktop_enabled=true`)
- `%USERPROFILE%\\Pictures` -> `D:\\OneDrive\\Imagens` (quando `profile_links_pictures_enabled=true`)
- `%USERPROFILE%\\Videos` -> `D:\\OneDrive\\Vídeos` (quando `profile_links_videos_enabled=true`)
- `D:\\bin` -> `D:\\OneDrive\\bin`
- `D:\\etc` -> `D:\\OneDrive\\etc`
- `D:\\clients` -> `D:\\OneDrive\\clients`
- `D:\\projects` -> `D:\\OneDrive\\clients\\pablo\\projects`

## 3) Esquema visual de diretorios e links (modo OneDrive ativo)

```text
D:\
|-- OneDrive\
|   |-- bin\
|   |-- etc\
|   `-- clients\
|       `-- pablo\
|           `-- projects\
|-- bin      -> D:\OneDrive\bin
|-- etc      -> D:\OneDrive\etc
|-- clients  -> D:\OneDrive\clients
`-- projects -> D:\OneDrive\clients\pablo\projects

C:\Users\pablo\
|-- bin      -> D:\OneDrive\bin
|-- etc      -> D:\OneDrive\etc
|-- clients  -> D:\OneDrive\clients
|-- projects -> D:\OneDrive\clients\pablo\projects
|-- .ssh     -> C:\Users\pablo\dotfiles\df\ssh
|-- .gitconfig -> C:\Users\pablo\dotfiles\df\git\.gitconfig
`-- ... (demais links de dotfiles)
```

## 4) Todos os links criados no bootstrap Windows

### 4.1 Links do bloco OneDrive/profile

- Perfil: `bin`, `etc`, `clients`, `projects` (sempre).
- Drive raiz: `bin`, `etc`, `clients`, `projects` (somente se `links_drive_enabled=true` e drive existir).
- Pastas padrao opcionais: `Documents`, `Desktop`, `Downloads`, `Pictures`, `Videos`, `Music`, `Contacts`, `Favorites`, `Links` (somente quando cada `profile_links_*_enabled=true`).

### 4.2 Outros links (dotfiles e ferramentas)

Origem em `C:\Users\<user>\...` para destino em `C:\Users\<user>\dotfiles\...`:

- `.ssh`, `.assets`, `.editorconfig`
- `.gitconfig`, `.config\git`, `.gitconfig-windows`, `.gitconfig.local.sample`
- `.bashrc`, `.bash_profile`, `.bashrc_profile`
- `.config\winfetch`, `.oh-my-posh`
- `.ssh\config.local` -> `df\ssh\config.windows`
- `Documents\PowerShell\profile.ps1` e arquivos de modulo PowerShell (`env-vars.ps1`, `aliases.ps1`, etc.)
- `%APPDATA%\Code\User` -> `df\vscode`
- `Windows Terminal settings.json` -> `df\windows-terminal\settings.json` (quando caminho do app e detectado)

## 5) Exemplo alternativo (sem drive D:)

```yaml
paths:
  windows:
    onedrive_enabled: true
    onedrive_root: "E:\\Cloud\\OneDrive"
    links_drive_enabled: false
```

Resultado:

- links de perfil funcionam normalmente apontando para `E:\Cloud\OneDrive\...`
- nenhum link e criado em `D:\*`

## 6) Exemplo alternativo (OneDrive desativado)

```yaml
paths:
  windows:
    onedrive_enabled: false
```

Resultado:

- bootstrap nao exige root do OneDrive
- `bin`, `etc`, `clients`, `projects` no perfil ficam como diretorios locais
- links de dotfiles continuam sendo criados normalmente

## 7) Pastas padrao do Windows (Documents/Desktop/Pictures/etc)

Agora o fluxo canônico permite redirecionamento por links para OneDrive, por pasta,
usando os campos `profile_links_*`.

Comportamento de migracao:

- `profile_links_migrate_content=true`:
  - migra conteudo atual da pasta para destino no OneDrive;
  - cria backup local da pasta antiga (`<Pasta>.dotfiles-prelink-YYYYMMDDHHMMSS`);
  - cria o link na origem.
- `profile_links_migrate_content=false`:
  - nao migra conteudo automaticamente;
  - cria backup local da pasta antiga (`<Pasta>.dotfiles-prelink-YYYYMMDDHHMMSS`);
  - cria o link na origem.

## 8) Como validar no pos-bootstrap

```powershell
checkEnv

Get-Item "$Env:USERPROFILE\\bin" | Select-Object FullName, LinkType, Target
Get-Item "$Env:USERPROFILE\\etc" | Select-Object FullName, LinkType, Target
Get-Item "$Env:USERPROFILE\\clients" | Select-Object FullName, LinkType, Target
Get-Item "$Env:USERPROFILE\\projects" | Select-Object FullName, LinkType, Target
```

## 9) Migracao automatica de root (best-effort)

Quando `onedrive_auto_migrate=true` e voce confirma troca de root:

1. para o cliente OneDrive;
2. copia dados para root nova;
3. cria junction da root antiga para a nova;
4. tenta atualizar root no registro do OneDrive;
5. sobe o cliente OneDrive de novo.

Limite: a troca da root "oficial" do cliente pode depender de estado/politica do OneDrive e exigir interacao em alguns ambientes.
