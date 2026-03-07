# Dotfiles

Repositório de dotfiles com bootstrap **multiambiente** (Windows host + Ubuntu WSL),
focado em segurança operacional e repetibilidade.

## Funcionalidades do projeto

- Bootstrap multiambiente para Windows host e Ubuntu WSL, com modos `new`, `refresh` e `relink`.
- Recriacao idempotente dos symlinks canonicos do bootstrap via `task bootstrap:relink`.
- Validacao operacional de ambiente com `checkEnv` em PowerShell e Bash.
- Sincronizacao Git entre Windows e WSL via tasks de `sync`, sem copia manual entre ambientes.
- Configuracao central de bootstrap com template versionado, normalizacao de caminhos canonicos e arquivos derivados sincronizados.
- Camada declarativa de IA versionada em `.agents/`, com skills, cartoes, registry, orchestration, rules, evals, worklog, roadmap e licoes aprendidas.
- Governanca de Git com `emoji + conventional commits`, validacao de branch/PR/commits e gates de continuidade.
- Suite de testes com Pester, Python e Bats, incluindo harnesses reais de integracao para `relink` em Linux e Windows.
- Workflows de CI para governanca de IA, validacao de PR, baseline de qualidade e integracao do bootstrap.

## Objetivos

- Git via SSH com 1Password SSH Agent como primeira opção.
- Commits assinados com SSH (`gpg.format=ssh`) usando 1Password signer.
- `op` e `gh` autenticados automaticamente durante bootstrap.
- Secrets de runtime sem plaintext versionado (modelo `.env.local.sops`).
- Health-check (`checkEnv`) como gate de conformidade.
- OneDrive Windows com override resiliente de paths e validação pós-bootstrap.

## Arquitetura rápida

- Bootstrap Windows: `bootstrap/_start.ps1` -> `bootstrap/bootstrap-windows.ps1`
- Bootstrap WSL: `bootstrap/bootstrap-ubuntu-wsl.sh`
- Config central: `bootstrap/user-config.yaml` (local) e `bootstrap/user-config.yaml.tpl` (template versionado)
- Secrets refs: `df/secrets/secrets-ref.yaml`
- Runtime env template: `bootstrap/secrets/.env.local.tpl`
- Runtime env cifrado local: `~/.env.local.sops`
- Fonte canonica da camada de IA: `.agents/`
- Ponte de compatibilidade para assistentes especificos: `.codex/README.md`

## Modelo de segredos e autenticação

### Entrada única (one-credential)

O bootstrap usa o token de service account do 1Password para acessar refs
necessários (`op://...`) sem exigir secrets prévios em disco.

### Persistência pós-bootstrap

- `SOPS_AGE_KEY` persiste no ambiente de usuário (modo env-only).
- `SOPS_AGE_KEY_FILE` permanece vazio por padrão.
- Secrets runtime ficam cifrados em `~/.env.local.sops`.
- `~/.env.local` plaintext legado é removido quando encontrado.

### Refs esperados no 1Password

Veja `df/secrets/secrets-ref.yaml`:

- `op://secrets/dotfiles/1password/service-account`
- `op://secrets/dotfiles/github/token` (preferencial, least privilege)
- `op://secrets/github/api/token` (fallback)
- `op://secrets/dotfiles/age/age.key`

## Configuração central do bootstrap

Arquivos:

- Template versionado: `bootstrap/user-config.yaml.tpl`
- Arquivo local: `bootstrap/user-config.yaml` (ignorado por Git)

Comportamento:

1. Se não existir `user-config.yaml`, ele é criado a partir do template.
2. Se estiver completo, `_start.ps1` pergunta se usa como está ou sobrescreve guiado.
3. Se estiver incompleto, pergunta se abre wizard ou aborta para edição manual.

Arquivos derivados sincronizados automaticamente:

- `df/secrets/secrets-ref.yaml`
- `bootstrap/secrets/.env.local.tpl`
- `df/git/.gitconfig.local` (local, não versionado)

### OneDrive (Windows) no YAML

Campos principais em `paths.windows`:

- `onedrive_enabled`: habilita/desabilita dependência de OneDrive no bootstrap.
- `onedrive_root`: root desejada do OneDrive (ou auto-detect quando vazio).
- `onedrive_auto_migrate`: tentativa best-effort de migração automática de root via junction.
- `onedrive_clients_dir`, `onedrive_projects_dir`, `onedrive_projects_path`: destinos de links dentro do OneDrive.
- `links_profile_*`: origens dos symlinks no perfil (`bin`, `etc`, `clients`, `projects`).
- `links_drive_enabled` + `links_drive_*`: atalhos opcionais no drive raiz (ex.: `D:\*`), sem obrigatoriedade de `D:`.
- `profile_links_migrate_content` + `profile_links_*`: redirecionamento opcional de pastas padrão do perfil (`Documents`, `Desktop`, `Downloads`, `Pictures`, etc.) para OneDrive, com opção de migração automática de conteúdo.

## Execução

### Windows (host)

```powershell
sudo $env:USERPROFILE\dotfiles\bootstrap\_start.ps1
```

Opções principais:

- `1` = new install (full)
- `2` = refresh dotfiles (rápido, sem reinstalar tudo)

### Ubuntu WSL

```bash
bash ~/dotfiles/bootstrap/bootstrap-ubuntu-wsl.sh
```

## checkEnv

`checkEnv` existe em PowerShell e Bash e valida:

- binários (`op`, `gh`, `git`, `ssh`, `sops`, `age`)
- sessão 1Password e leitura de refs
- auth do `gh` + protocolo SSH
- política Git de assinatura (`gpg.format`, `commit.gpgsign`, `user.signingkey`, `gpg.ssh.program`)
- política SSH (`identityagent`, `identityfile none`, socket no Unix/WSL)
- handshake `ssh -T git@github.com`
- commit assinado de teste
- no Windows, validação adicional de root OneDrive e links de perfil (quando `onedrive_enabled=true`)

Documentação detalhada: `docs/checkenv.md`.

## Tasks (interface oficial de automação)

Todas as operações diárias e validações de PR/CI devem ser executadas via `task`
(`Taskfile.yml`) para manter paridade entre ambientes e evitar drift.

Padrão de execução:

- comandos sem sufixo fazem **auto-detecção de ambiente** (Windows/WSL Linux)
- comandos com sufixo `:windows` e `:linux` permanecem disponíveis para execução manual/forçada

Fluxo de sync (repositórios independentes por ambiente):

1. fluxo canônico diário: rode `task sync` no ambiente em que estiver trabalhando
2. ao trocar de ambiente (Windows/WSL/outra máquina): rode `task sync` no destino
3. quando precisar comportamento estritamente previsível (sem prompt): use aliases determinísticos (`sync:update`, `sync:update-safe`, `sync:publish`)

Tasks principais:

- `task sync` (auto), `task sync:windows`, `task sync:linux` (fluxo inteligente guiado)
- `task sync:update` / `task sync:update-safe` / `task sync:publish MSG="..."` (determinísticos, sem heurística interativa)
- `task sync:update:windows` / `task sync:update:linux`
- `task sync:wsl-gate` (auto) e `task sync:wsl-gate:windows` para gate local Windows->WSL via Git-only
- `task env:check` (auto) e variantes `task env:check:windows` / `task env:check:linux`
- `task bootstrap` (auto) e variantes `task bootstrap:windows:new` / `task bootstrap:windows:refresh` / `task bootstrap:linux`
- `task bootstrap:relink` (auto) e variantes `task bootstrap:windows:relink` / `task bootstrap:linux:relink` para recriar symlinks canônicos do bootstrap
- `task ci:validate` (auto) e variantes `task ci:validate:windows` / `task ci:validate:linux`
- `task test:integration:linux` / `task test:integration:windows`
- `task ai:validate`, `task ai:eval:smoke`, `task ai:lessons:check`, `task ai:worklog:check`, `task ai:worklog:close:gate`
- `task pr:status` / `task pr:checks PR=<numero>`

Política de paridade:

- toda automação de CI/CD e validação de PR deve ter task equivalente em `Taskfile.yml`
- toda mudança em workflow de CI/CD deve ser refletida nas tasks correspondentes
- sincronização entre ambientes (Windows/WSL ou máquinas diferentes) deve ocorrer via Git, sem cópia direta de arquivos entre ambientes
- `repo:update`/`repo:update-safe`/`repo:publish` (e aliases `sync:update`/`sync:update-safe`/`sync:publish`) reutilizam o mesmo core do `sync` para reduzir drift de comportamento

## Segurança

- Não versionar secrets plaintext.
- Não versionar chaves privadas.
- `user.signingkey` em Git config é **chave pública** (não segredo).
- Rotacionar qualquer token exposto historicamente.

Guia completo: `SECURITY.md` e `docs/secrets-and-auth.md`.

## Documentação complementar

- `bootstrap/README.md`
- `docs/ai-operating-model.md`
- `docs/AI-WIP-TRACKER.md`
- `docs/ROADMAP.md`
- `docs/ROADMAP-DECISIONS.md`
- `docs/AI-AGENTS-CATALOG.md`
- `docs/AI-SKILLS-CATALOG.md`
- `docs/AI-DELEGATION-FLOW.md`
- `docs/AI-GOVERNANCE-AND-REGRESSION.md`
- `docs/TASKS.md`
- `docs/WORKFLOWS.md`
- `tests/README.md`
- `docs/bootstrap-flow.md`
- `docs/checkenv.md`
- `docs/onedrive.md`
- `docs/user-home-structure.md`
- `docs/secrets-and-auth.md`
- `docs/config-reference.md`
- `docs/repo-audit.md`
- `docs/README.md`
- `archive/README.md`
