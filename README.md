# Dotfiles

Repositório de dotfiles com bootstrap **multiambiente** (Windows host + Ubuntu WSL),
focado em segurança operacional e repetibilidade.

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

## Rotina operacional Windows + WSL

Antes de testar no WSL após mudanças no Windows:

1. commit/push no Windows
2. rodar `dfsync` no Windows (sincroniza e valida WSL)
3. só então executar testes no WSL

## Segurança

- Não versionar secrets plaintext.
- Não versionar chaves privadas.
- `user.signingkey` em Git config é **chave pública** (não segredo).
- Rotacionar qualquer token exposto historicamente.

Guia completo: `SECURITY.md` e `docs/secrets-and-auth.md`.

## Documentação complementar

- `bootstrap/README.md`
- `docs/bootstrap-flow.md`
- `docs/checkenv.md`
- `docs/onedrive.md`
- `docs/user-home-estructure.md`
- `docs/secrets-and-auth.md`
- `docs/config-reference.md`
- `docs/repo-audit.md`
