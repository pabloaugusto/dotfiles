# User Home Estructure (Windows + WSL)

Guia de referencia da estrutura final esperada de home/perfil quando o bootstrap
e executado com o modo mais completo (OneDrive habilitado e opcoes relacionadas
ativadas).

## Premissas usadas neste documento

Configuracao considerada (exemplo):

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
  wsl:
    onedrive_root: "/mnt/d/OneDrive"
    onedrive_clients_dir: "clients"
    onedrive_projects_dir: "clients/pablo/projects"
bootstrap:
  add_user:
    enabled: true
```

Notas:

- Se `bootstrap.add_user.enabled=true`, o bootstrap provisiona usuario extra no
  WSL e aplica a mesma logica de links no `/home/<usuario-extra>`.
- Neste exemplo todas as pastas opcionais do perfil Windows estao com `*_enabled=true`.

## Secao 1 - Windows (`C:\\Users\\{user}`)

### 1.1 Visao geral (tree)

```text
C:\Users\pablo\
|-- bin       -> D:\OneDrive\bin
|-- etc       -> D:\OneDrive\etc
|-- clients   -> D:\OneDrive\clients
|-- projects  -> D:\OneDrive\clients\pablo\projects
|-- Documents -> D:\OneDrive\documents
|-- Desktop -> D:\OneDrive\desktop
|-- Downloads -> D:\OneDrive\downloads
|-- Pictures -> D:\OneDrive\Imagens
|-- Videos -> D:\OneDrive\Vídeos
|-- Music -> D:\OneDrive\Música
|-- Contacts -> D:\OneDrive\documents\profile\contacts
|-- Favorites -> D:\OneDrive\documents\profile\favorites
|-- Links -> D:\OneDrive\documents\profile\links
|-- .ssh      -> C:\Users\pablo\dotfiles\app\df\ssh
|-- .assets   -> C:\Users\pablo\dotfiles\app\df\assets
|-- .editorconfig -> C:\Users\pablo\dotfiles\app\df\.editorconfig
|-- .gitconfig -> C:\Users\pablo\dotfiles\app\df\git\.gitconfig
|-- .gitconfig-windows -> C:\Users\pablo\dotfiles\app\df\git\.gitconfig-windows
|-- .gitconfig.local.sample -> C:\Users\pablo\dotfiles\app\df\git\.gitconfig.local.sample
|-- .config\
|   |-- git -> C:\Users\pablo\dotfiles\app\df\git
|   `-- winfetch -> C:\Users\pablo\dotfiles\app\df\winfetch
|-- .oh-my-posh -> C:\Users\pablo\dotfiles\app\df\oh-my-posh
|-- .bashrc -> C:\Users\pablo\dotfiles\app\df\bash\.bashrc
|-- .bash_profile -> C:\Users\pablo\dotfiles\app\df\bash\.bash_profile
`-- .bashrc_profile -> C:\Users\pablo\dotfiles\app\df\bash\.bashrc_profile
```

### 1.2 Links adicionais no drive (quando `links_drive_enabled=true`)

```text
D:\
|-- bin      -> D:\OneDrive\bin
|-- etc      -> D:\OneDrive\etc
|-- clients  -> D:\OneDrive\clients
`-- projects -> D:\OneDrive\clients\pablo\projects
```

### 1.3 Links de ferramentas e apps

```text
C:\Users\pablo\Documents\PowerShell\profile.ps1 -> C:\Users\pablo\dotfiles\app\df\powershell\profile.ps1
C:\Users\pablo\Documents\PowerShell\env-vars.ps1 -> C:\Users\pablo\dotfiles\app\df\powershell\env-vars.ps1
C:\Users\pablo\Documents\PowerShell\env-check.ps1 -> C:\Users\pablo\dotfiles\app\df\powershell\env-check.ps1
C:\Users\pablo\Documents\PowerShell\plugins.ps1 -> C:\Users\pablo\dotfiles\app\df\powershell\plugins.ps1
C:\Users\pablo\Documents\PowerShell\aliases.ps1 -> C:\Users\pablo\dotfiles\app\df\powershell\aliases.ps1
C:\Users\pablo\Documents\PowerShell\hotkeys.ps1 -> C:\Users\pablo\dotfiles\app\df\powershell\hotkeys.ps1
C:\Users\pablo\Documents\PowerShell\wsl.ps1 -> C:\Users\pablo\dotfiles\app\df\powershell\wsl.ps1
C:\Users\pablo\Documents\PowerShell\_functions.ps1 -> C:\Users\pablo\dotfiles\app\df\powershell\_functions.ps1
C:\Users\pablo\Documents\PowerShell\powershell.config.json -> C:\Users\pablo\dotfiles\app\df\powershell\powershell.config.json

%APPDATA%\Code\User -> C:\Users\pablo\dotfiles\app\df\vscode
<WindowsTerminalPackage>\LocalState\settings.json -> C:\Users\pablo\dotfiles\app\df\windows-terminal\settings.json
```

## Secao 2 - Linux/WSL (`/home/{user}`)

### 2.1 Visao geral (tree)

```text
/home/pablo
|-- dotfiles/                      (repo)
|-- .ssh -> /home/pablo/dotfiles/app/df/ssh
|-- .assets -> /home/pablo/dotfiles/app/df/assets
|-- .secrets -> /home/pablo/dotfiles/app/df/secrets
|-- .config/
|   |-- git -> /home/pablo/dotfiles/app/df/git
|   |-- atuin -> /home/pablo/dotfiles/app/df/config/atuin
|   `-- Code/User -> /home/pablo/dotfiles/app/df/vscode
|-- .oh-my-posh -> /home/pablo/dotfiles/app/df/oh-my-posh
|-- .editorconfig -> /home/pablo/dotfiles/app/df/.editorconfig
|-- .gitconfig -> /home/pablo/dotfiles/app/df/git/.gitconfig
|-- .aliases -> /home/pablo/dotfiles/app/df/.aliases
|-- .bash_logout -> /home/pablo/dotfiles/app/df/bash/.bash_logout
|-- .bashrc -> /home/pablo/dotfiles/app/df/bash/.bashrc
|-- .profile -> /home/pablo/dotfiles/app/df/bash/.profile
|-- .blerc -> /home/pablo/dotfiles/app/df/bash/.blerc
|-- .zshrc -> /home/pablo/dotfiles/app/df/zsh/.zshrc
|-- .zprofile -> /home/pablo/dotfiles/app/df/zsh/.zprofile
|-- .zshenv -> /home/pablo/dotfiles/app/df/zsh/.zshenv
|-- onedrive -> /mnt/d/OneDrive
|-- clients -> /mnt/d/OneDrive/clients
|-- projects -> /mnt/d/OneDrive/clients/pablo/projects
|-- .env.local.sops               (arquivo cifrado de runtime)
|-- .local/bin/op-ssh-sign        (wrapper para op-ssh-sign-wsl.exe)
`-- .config/dotfiles/runtime.env  (export de SOPS_AGE_KEY)
```

### 2.2 Caso `bootstrap.add_user.enabled=true`

Para usuario extra (exemplo `deploy`):

- `/home/deploy/dotfiles` e copiado do usuario principal.
- `setProfileSymlinks deploy` e executado.
- Resultado: mesma estrutura de links no `/home/deploy`, adaptada ao usuario.

## Secao 3 - Intercambiavel Windows <-> WSL

Esta secao explica o que e compartilhado entre os dois ambientes.

### 3.1 OneDrive compartilhado

Com `onedrive_root = D:\\OneDrive` no Windows e `onedrive_root = /mnt/d/OneDrive`
no WSL:

- Windows grava em `D:\OneDrive\...`
- WSL enxerga o mesmo conteudo em `/mnt/d/OneDrive/...`
- Links `C:\Users\<user>\clients` e `/home/<user>/clients` apontam para o mesmo
  conjunto de dados fisicos.

### 3.2 Montagens nativas do WSL (nao sao criadas pelo bootstrap)

No WSL, por padrao:

- `/mnt/c` mapeia `C:\`
- `/mnt/d` mapeia `D:\` (quando o drive existe no Windows)

Ou seja:

- [`C:\Users\pablo\dotfiles`](../) <-> `/mnt/c/Users/pablo/dotfiles`
- `D:\OneDrive` <-> `/mnt/d/OneDrive`

### 3.3 Exemplo visual de interoperabilidade

```text
Windows: C:\Users\pablo\projects -> D:\OneDrive\clients\pablo\projects
WSL:     /home/pablo/projects    -> /mnt/d/OneDrive/clients/pablo/projects

Ambos convergem para:
D:\OneDrive\clients\pablo\projects
```

Pastas padrao (quando habilitadas) tambem convergem para OneDrive:

```text
C:\Users\pablo\Documents -> D:\OneDrive\documents
C:\Users\pablo\Pictures  -> D:\OneDrive\Imagens
C:\Users\pablo\Videos    -> D:\OneDrive\Vídeos
```

## Secao 4 - Como auditar rapidamente a estrutura apos bootstrap

### 4.1 Windows

```powershell
checkEnv
Get-Item "$Env:USERPROFILE\\bin" | Select-Object FullName, LinkType, Target
Get-Item "$Env:USERPROFILE\\clients" | Select-Object FullName, LinkType, Target
Get-Item "$Env:USERPROFILE\\projects" | Select-Object FullName, LinkType, Target
Get-Item "$Env:USERPROFILE\\.ssh" | Select-Object FullName, LinkType, Target
Get-Item "$Env:USERPROFILE\\Documents" | Select-Object FullName, LinkType, Target
Get-Item "$Env:USERPROFILE\\Desktop" | Select-Object FullName, LinkType, Target
Get-Item "$Env:USERPROFILE\\Downloads" | Select-Object FullName, LinkType, Target
Get-Item "$Env:USERPROFILE\\Pictures" | Select-Object FullName, LinkType, Target
Get-Item "$Env:USERPROFILE\\Videos" | Select-Object FullName, LinkType, Target
```

### 4.2 WSL

```bash
checkEnv
ls -ld ~/onedrive ~/clients ~/projects ~/.ssh ~/.config/git ~/.oh-my-posh
readlink -f ~/projects
readlink -f ~/clients
```

## Secao 5 - Observacoes importantes

- "100% automatizado" para troca da root oficial do OneDrive tem limite do cliente
  Microsoft. O bootstrap usa estrategia best-effort (shutdown + copia + junction).
- Para pastas padrao opcionais (`Documents`, `Desktop`, etc.), o bootstrap cria
  backup local `<Pasta>.dotfiles-prelink-YYYYMMDDHHMMSS` antes de substituir por link.
- O gate final valida links e paths para reduzir risco de bootstrap incompleto.
- Se OneDrive estiver desabilitado (`onedrive_enabled=false`), a estrutura muda:
  `bin/etc/clients/projects` no perfil ficam locais, sem link para OneDrive.
