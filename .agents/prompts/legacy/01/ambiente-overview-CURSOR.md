## Visão geral do ambiente de dotfiles

Este documento resume a arquitetura e os fluxos principais do repositório de dotfiles multiambiente (Windows host + Ubuntu WSL), com foco em bootstrap, segredos, autenticação, estrutura de pastas e automações.

### 1. Arquitetura e objetivos

- **Objetivo principal**: padronizar ambiente de trabalho entre Windows e Ubuntu WSL, com foco em segurança operacional, repetibilidade e uso intensivo de 1Password.
- **Pilares**:
  - **Bootstrap reproduzível** para Windows e WSL.
  - **Secrets/runtime seguros** usando `sops+age` e 1Password.
  - **GitHub via SSH** com 1Password SSH Agent.
  - **Commits assinados (SSH)** com `gpg.format=ssh` e `op-ssh-sign`.
  - **Health-check central** (`checkEnv`) como gate de conformidade.
  - **OneDrive** como camada de dados compartilhada entre Windows e WSL (quando habilitado).

Estrutura macro:

- `bootstrap/`: entrypoints e fluxo de provisionamento (Windows + WSL).
- `df/`: dotfiles por domínio (shells, git, ssh, secrets, etc.).
- `docs/`: documentação detalhada (bootstrap, checkEnv, OneDrive, segurança, estrutura de home, auditoria, etc.).
- `Taskfile.yml`: interface oficial de automação (`task`).

### 2. Bootstrap Windows

Entrypoint: `bootstrap/_start.ps1`  
Fluxo operacional principal:

1. **Pré-requisitos**:
   - Garante `winget`, `pwsh` e `git` instalados.
   - Carrega `bootstrap/bootstrap-config.ps1` e valida `bootstrap/user-config.yaml` (config central).
2. **Config central (YAML)**:
   - Define identidade Git, estratégia OneDrive (`enabled`, root, migração), caminhos de links (`bin`, `etc`, `clients`, `projects`), links opcionais de pastas padrão (`Documents`, `Desktop`, etc.), refs de segredos e usuário extra no WSL.
   - A partir do YAML, sincroniza artefatos derivados:
     - `df/secrets/secrets-ref.yaml`
     - `bootstrap/secrets/.env.local.tpl`
     - `df/git/.gitconfig.local` (local, não versionado).
3. **Menu de operação** (`bootstrap` function em `_start.ps1`):
   - `0` – aborta.
   - `1` – **Windows – new install** (full).
   - `2` – **Windows – refresh** (sem reinstalar tudo).
   - Outras opções exibem que apenas Windows é suportado aqui; WSL usa script dedicado.
4. **Fluxo `bootstrap-windows.ps1`**:
   - Confirma execução em PowerShell elevado e existência de `C:\Users\<user>\dotfiles`.
   - **OneDrive (quando `paths.windows.onedrive_enabled=true`)**:
     - Resolve raiz atual (registro OneDrive/env) e raiz desejada (YAML/env).
     - Quando necessário, instala OneDrive via `winget`.
     - Pode guiar migração da raiz com:
       - `robocopy` dos dados para nova root.
       - Criação de **junction** da root antiga → nova (best-effort).
       - Atualização de `UserFolder` no registro.
   - **Layout de links Windows**:
     - `Resolve-WindowsLinkLayout` define destinos de:
       - `C:\Users\<user>\bin`, `etc`, `clients`, `projects`.
       - Opcionalmente, atalhos em drive raiz (`D:\bin`, `D:\clients`, etc.).
     - `Invoke-ProfileFoldersToOneDriveLinking`:
       - Para cada pasta padrão habilitada (`Documents`, `Desktop`, `Downloads`, `Pictures`, `Videos`, etc.):
         - Cria target em OneDrive.
         - Opcionalmente **migra conteúdo** (via `robocopy`) antes de linkar.
         - Mantém backup `<Pasta>.dotfiles-prelink-YYYYMMDDHHMMSS`.
   - **Links de dotfiles**:
     - `.ssh`, `.assets`, `.gitconfig*`, `.config\git`, `.oh-my-posh`.
     - Perfis PowerShell em `Documents\PowerShell`.
     - VS Code (`%APPDATA%\Code\User`) e Windows Terminal.
   - **Software e fontes** (modo full):
     - Usa `bootstrap/software-list.ps1` + `winget` + `Install-FontWindows`.
   - **Segredos, auth e gates finais**:
     - Gera `~/.env.local.sops` a partir de `bootstrap/secrets/.env.local.tpl` via 1Password (`Set-LocalEnvFrom1Password`).
     - Remove `.env.local` plaintext legado.
     - Persiste apenas `SOPS_AGE_KEY` no ambiente do usuário.
     - Garante GitHub CLI autenticado via 1Password (`Ensure-GitHubCliAuthFrom1Password`).
     - Executa:
       - `checkEnv` (gate de conformidade).
       - `Test-OneDriveLayoutHealth` (garante consistência de links/OneDrive).
   - **Preferências Windows** (modo full):
     - Ajustes de data/hora, teclado, regionalização e Explorer.

### 3. Bootstrap Ubuntu WSL

Entrypoint: `bootstrap/bootstrap-ubuntu-wsl.sh`  
Responsabilidades:

1. **Prompt de confirmação**:
   - Padrão "MARCO/POLO" para garantir consentimento explícito.
2. **Fonts**:
   - Linka `~/dotfiles/df/assets/fonts` em `~/.local/share/fonts` e roda `fc-cache`.
3. **Software**:
   - Instala base apt (`unzip`, `build-essential`, `git`, etc.).
   - Instala stack principal via Homebrew:
     - 1Password CLI, `gh`, `oh-my-posh`, `zsh`, ferramentas DevOps (terraform, helm, kubectl, talosctl, flux, etc.), linguagens (node, gerenciadores npm/yarn/pnpm), `age`, `sops`, `atuin`, etc.
4. **Usuário extra opcional**:
   - Se `DOTFILES_ADD_USER` e `DOTFILES_ADD_USER_PASS_HASH` estiverem definidos:
     - Cria usuário adicional (ex. `deploy`) com `/home/<user>/dotfiles` copiado.
     - Executa `setProfileSymlinks` para esse usuário.
5. **Symlinks de dotfiles** (`setProfileSymlinks`):
   - `.ssh`, `.assets`, `.secrets`, `.config/git`, `.config/atuin`, `.oh-my-posh`.
   - Shells: `.bashrc`, `.profile`, `.blerc`, `.zshrc`, `.zprofile`, `.zshenv`.
   - VS Code: `~/.config/Code/User` → `df/vscode`.
   - Se OneDrive montado (`/mnt/d/OneDrive` por padrão ou override via YAML):
     - Cria `~/onedrive`, `~/clients`, `~/projects` apontando para a árvore do OneDrive.
6. **Segredos e runtime env**:
   - `setLocalEnvFile`:
     - Usa `op inject` em `bootstrap/secrets/.env.local.tpl` para gerar arquivo temporário.
     - Carrega variáveis em memória (incluindo `OP_SERVICE_ACCOUNT_TOKEN`, `GH_TOKEN`/`GITHUB_TOKEN`, `SOPS_AGE_KEY`).
     - Deriva recipient `age` a partir de `SOPS_AGE_KEY`.
     - Criptografa para `~/.env.local.sops` com `sops`.
     - Remove `.env.local` plaintext.
   - `importLocalEnvFromSops`:
     - Decripta `~/.env.local.sops` on‑demand para popular ambiente atual.
   - `persistSopsAgeEnv`:
     - Cria `~/.config/dotfiles/runtime.env` com `SOPS_AGE_KEY` e limpa exports legados em `.bashrc` / `.profile`.
7. **Autenticação GitHub + SSH signer**:
   - `ensureOpToken`: garante `OP_SERVICE_ACCOUNT_TOKEN` (prompt se necessário).
   - `ensureOpSshSignAlias`:
     - Cria wrapper `~/.local/bin/op-ssh-sign` apontando para `op-ssh-sign-wsl.exe` quando necessário.
   - `ensureGitHubAuth`:
     - Resolve token via `GH_TOKEN`/`GITHUB_TOKEN` ou refs 1Password.
     - Faz `gh auth login --git-protocol ssh` e força `git_protocol=ssh`.
8. **Gate final**:
   - Linka `~/.ssh/config.local` → `config.unix`.
   - Executa `checkEnv` (Bash) como health‑check final; falhas abortam bootstrap.

### 4. Modelo de segredos, autenticação e assinatura

Arquivos principais:

- `df/secrets/secrets-ref.yaml`: refs canônicas `op://...` para o projeto.
- `bootstrap/secrets/.env.local.tpl`: template de env descriptografado (nunca versionado em plaintext).
- `~/.env.local.sops`: runtime env cifrado (para Windows e WSL).
- `~/.config/dotfiles/runtime.env`: apenas `SOPS_AGE_KEY` e metadados relacionados.
- `df/ssh/config*` e `df/git/.gitconfig*`: política de SSH e Git signing.

Princípios:

- Nenhum `.env` plaintext versionado.
- Secrets sempre via 1Password (refs `op://...`).
- Arquivos cifrados com `sops+age`; apenas a chave `age` (SOPS_AGE_KEY) persiste em env.
- `user.signingkey` contém **chave pública SSH** (não segredo).
- SSH + assinatura Git sempre passando pelo agent/sign‑program do 1Password.

GitHub CLI:

- Reutiliza sessão existente quando possível.
- Se necessário, resolve token em ordem:
  - `GH_TOKEN`
  - `GITHUB_TOKEN`
  - `op://secrets/dotfiles/github/token`
  - `op://secrets/github/api/token`
- Força `git_protocol=ssh` tanto por host quanto globalmente.

### 5. `checkEnv` – gate de conformidade

Implementações:

- PowerShell: `df/powershell/_functions.ps1`.
- Bash: `df/bash/.inc/check-env.sh`.

O que valida (resumido):

- Presença de binários essenciais: `op`, `gh`, `git`, `ssh`, `sops`, `age`.
- Sessão 1Password válida (`op whoami`) + leitura das refs em `df/secrets/secrets-ref.yaml`.
- `gh auth status` em `github.com` + `git_protocol=ssh`.
- Política Git:
  - `gpg.format=ssh`.
  - `commit.gpgsign=true`.
  - `user.signingkey` em formato `ssh-...`.
  - `gpg.ssh.program` resolvível para um binário real (`op-ssh-sign` / wrapper).
- Política SSH:
  - `identityagent` apontando para 1Password agent (socket Unix ou pipe Windows).
  - `identityfile none` para evitar fallback em chaves locais.
  - Handshake SSH com GitHub (`ssh -T git@github.com`).
- Teste de commit assinado:
  - Cria repo temporário, faz `git commit -S` e valida assinatura (`Good SSH signature` / bloco `gpgsig`).
- Windows:
  - Em `bootstrap-windows.ps1`, após `checkEnv`, ainda executa `Test-OneDriveLayoutHealth` para validar links de perfil/OneDrive.

Saída:

- Cada check é marcado como **SUCCESS**, **FAIL** ou **INCONCLUSIVE**, com sugestões de correção ao final.

### 6. Estrutura de diretórios de usuário (Windows + WSL)

Documentada em detalhe em `docs/user-home-structure.md`. Resumo:

- **Windows (`C:\Users\<user>`)**:
  - Links principais:
    - `bin`, `etc`, `clients`, `projects` → raiz/configuração de OneDrive quando habilitado.
    - Pastas padrão (`Documents`, `Desktop`, `Downloads`, `Pictures`, `Videos`, `Music`, `Contacts`, `Favorites`, `Links`) redirecionadas para subpastas em OneDrive, com backup `.dotfiles-prelink-*` preservado.
  - Integrações:
    - `Documents\PowerShell\*.ps1` linkados para `df/powershell`.
    - `%APPDATA%\Code\User` → `df/vscode`.
    - Windows Terminal `settings.json` → `df/windows-terminal/settings.json`.
  - Dotfiles principais (`.ssh`, `.gitconfig`, `.oh-my-posh`, `.editorconfig`, etc.) sempre apontando para o repo `dotfiles`.
- **WSL (`/home/<user>`)**:
  - `~/dotfiles` (repo).
  - Symlinks padronizados em `~/.ssh`, `~/.config/git`, `~/.config/Code/User`, `~/.oh-my-posh`, `~/.aliases`, `.bash*`, `.zsh*`, etc.
  - `~/onedrive`, `~/clients`, `~/projects` apontando para `/mnt/d/OneDrive/...` quando configurado.
  - `~/.env.local.sops` + `~/.config/dotfiles/runtime.env` para runtime env cifrado.

### 7. Automação via `task` e scripts auxiliares

- **Interface oficial**: `go-task`, com definição em `Taskfile.yml`.
- Padrões:
  - Comandos sem sufixo fazem **auto-detecção de ambiente** (Windows/WSL).
  - Versões com `:windows` / `:linux` permitem forçar ambiente específico.
- Fluxos principais:
  - `task sync`:
    - Chama `sync:windows` ou `sync:linux`, que delegam para:
      - **Windows**: `Invoke-DotfilesSmartSync` (PowerShell).
      - **Linux/WSL**: `df/bash/.inc/sync-smart.sh` (`dotfiles_sync`).
    - Fluxo inteligente:
      - Detecta alterações locais.
      - Oferece commit agrupado por contexto (CI, bootstrap, bash, docs, etc.).
      - Faz fetch/pull (`repo:update`) e push condicionais.
  - `task repo:update` / `sync:update` (+ variantes `-safe`):
    - Atualizam o repo (`main`, `fetch --prune`, `pull --rebase`), com opção de auto‑stash.
  - `task repo:publish` / `sync:publish MSG="..."`:
    - Update + commit + push determinístico com mensagem fornecida.
  - `task env:check`:
    - Roda `checkEnv` na shell apropriada.
  - `task bootstrap`:
    - Despacha para `_start.ps1` (Windows) ou `bootstrap-ubuntu-wsl.sh` (Linux/WSL).
  - `task ci:*` e `task pr:*`:
    - Paridade com CI: lint, docker build, validação de PR local antes de abrir/atualizar PR.

Scripts de suporte importantes:

- `df/bash/.inc/sync-smart.sh`: implementa o fluxo "smart sync" no Linux/WSL (agrupamento por contexto, push condicional, auto‑heal de remote HTTPS → SSH).
- `df/bash/.inc/check-env.sh`: implementação Bash de `checkEnv`, com retry automático para `op` e `gh` e simulação de commit assinado.

### 8. Segurança operacional e práticas recomendadas

- Documentos centrais:
  - `SECURITY.md`
  - `docs/secrets-and-auth.md`
  - `docs/repo-audit.md`
  - `docs/checkenv.md`
- **Nunca versionar**:
  - Chaves privadas (`*.pem`, `*.key`, etc.).
  - `.env` plaintext.
  - Tokens exportados diretamente.
  - Arquivos locais como `bootstrap/user-config.yaml` e `df/git/.gitconfig.local`.
- **Antes de publish**:
  - Scan rápido de segredos via `git grep` com padrões pré‑definidos.
  - `git status --ignored` para garantir que nada sensível foi adicionado indevidamente.
  - `git diff --staged` revisado.
- **Hardening adicional sugerido**:
  - Secret scanner em pre‑commit/CI (`gitleaks`, `detect-secrets`).
  - Branch protection no GitHub com require‑checks.
  - Tokens dedicados por projeto com privilégio mínimo.
  - Uso regular de `checkEnv` após qualquer mudança na pilha de auth/SSH/Git.
