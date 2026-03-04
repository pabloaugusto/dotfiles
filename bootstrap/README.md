# Bootstrap Guide

Guia operacional dos scripts de bootstrap para Windows e Ubuntu WSL.

## Entrypoints

- `bootstrap/_start.ps1`: menu/entrypoint para execução no Windows host.
- `bootstrap/bootstrap-windows.ps1`: fluxo Windows (full ou refresh).
- `bootstrap/bootstrap-ubuntu-wsl.sh`: fluxo Ubuntu WSL.
- `bootstrap/bootstrap-config.ps1`: wizard + validação de config central.

## Fluxograma do Bootstrap

Fluxograma visual e decision-complete (macro + subfluxos Windows/WSL/OneDrive + gates):

- `../docs/bootstrap-flow.md`

Observação:

- esse README mantém a visão operacional textual;
- o diagrama central de referência está no documento dedicado acima.

## Config central (YAML)

Arquivos:

- `bootstrap/user-config.yaml.tpl` (template versionado)
- `bootstrap/user-config.yaml` (local, ignorado)

O YAML define:

- identidade Git (nome/email/username/signing key pública)
- estratégia OneDrive no Windows (`enabled`, root, auto-migrate)
- caminhos OneDrive no WSL
- caminhos customizáveis de links no perfil Windows (`bin`, `etc`, `clients`, `projects`)
- links opcionais de pastas padrão do perfil Windows para OneDrive (`Documents`, `Desktop`, etc.)
- caminhos opcionais de atalhos em drive raiz (ex.: `D:\bin`)
- refs de segredos no 1Password
- opção de usuário extra no WSL

## Artefatos derivados

Após validar/preencher o YAML, o bootstrap sincroniza:

- `df/secrets/secrets-ref.yaml`
- `bootstrap/secrets/.env.local.tpl`
- `df/git/.gitconfig.local` (local, não versionado)

## Fluxo Windows (new install)

1. valida pré-requisitos básicos (winget, paths, config YAML)
2. resolve política OneDrive (`enabled=true/false`)
3. se OneDrive ativo:
   - se OneDrive não estiver instalado, instala via `winget` e inicia setup guiado
   - detecta root atual configurada
   - pergunta se deve manter ou mover root base
   - quando necessário, tenta migração automática (best-effort): copia dados, junction e atualização de root no registro
   - cria links de perfil e links opcionais de drive
4. se OneDrive desativado:
   - cria diretórios locais no perfil (sem depender de OneDrive)
5. instala software/módulos/fontes
6. resolve runtime secrets via `op inject`
7. cifra runtime env em `~/.env.local.sops`
8. autentica `gh` com token do 1Password e força protocolo SSH
9. roda `checkEnv` (gate obrigatório)
10. roda validação dedicada de OneDrive/links no pós-bootstrap (gate obrigatório)
11. aplica preferências Windows (modo full)

## Fluxo Windows (refresh)

Semelhante ao full, porém:

- não reinstala catálogo completo de software/fontes
- não reaplica preferências pesadas do sistema
- mantém auth/signing + `checkEnv`

## Fluxo Ubuntu WSL

1. instala base (`apt`) e stack via Homebrew
2. cria symlinks de shell/git/ssh/config
3. garante token `OP_SERVICE_ACCOUNT_TOKEN`
4. gera env runtime com `op inject`, cifra em `~/.env.local.sops`
5. persiste `SOPS_AGE_KEY` em `~/.config/dotfiles/runtime.env`
6. garante auth `gh` (SSH)
7. roda `checkEnv` no final

## Modelo de autenticação

- `op`: sessão validada e reutilizada quando possível.
- `gh`: login por token resolvido do 1Password (preferencial token dedicado).
- SSH: prioridade para 1Password SSH Agent.
- Assinatura Git: `gpg.format=ssh` + `gpg.ssh.program=op-ssh-sign`.

## Estratégia de override OneDrive (Windows)

Precedência de root desejada:

1. `paths.windows.onedrive_root` (YAML)
2. `OneDrive` do ambiente
3. `%USERPROFILE%\OneDrive`

Comportamento:

- `paths.windows.onedrive_enabled=true`: bootstrap executa etapa de pré-requisito OneDrive antes de qualquer link.
  - se OneDrive não existir: instala, pergunta root desejada e aguarda conclusão de login/setup.
  - se existir: mostra root atual e pergunta se deve mover.
- `paths.windows.onedrive_enabled=false`: bootstrap ignora OneDrive e usa diretórios locais.
- `paths.windows.onedrive_auto_migrate=true`: quando você optar por mudar root, o bootstrap tenta automação sem fechamento manual:
  - encerra cliente OneDrive
  - copia dados para root nova
  - cria junction na root antiga apontando para a nova
  - tenta atualizar root no registro do OneDrive (best-effort)
  - inicia cliente novamente
- `paths.windows.profile_links_migrate_content`:
  - `true`: migra conteúdo das pastas padrão antes de criar links para OneDrive
  - `false`: não migra conteúdo, apenas cria links (mantendo backup local da origem)

Limite importante:

- Alterar a root "oficial" do OneDrive sem interação depende do cliente Microsoft e não é 100% garantido para todos os cenários/versões.
- O modo de junction reduz intervenção manual e mantém compatibilidade na maior parte dos casos.

## Opção de usuário extra no WSL

Campo: `bootstrap.add_user` no YAML.

Utilidade:

- separar usuário pessoal e automação/deploy
- reduzir superfície de execução privilegiada no usuário principal
- facilitar política de privilégio mínimo por contexto

Quando evitar:

- uso pessoal simples com um único usuário no WSL

## Troubleshooting rápido

- `checkEnv` com FAIL em `gpg.ssh.program`: validar `op-ssh-sign` no PATH.
- `gh` sem SSH protocol: `gh config set git_protocol ssh --host github.com`.
- SSH denied (publickey): confirmar chave no GitHub e agent 1Password ativo.
- `.env.local.sops` ausente: rerodar bootstrap/auth step.
- OneDrive path FAIL no pós-bootstrap: validar root atual, permissões e rerodar bootstrap com `paths.windows.onedrive_enabled=true`.
