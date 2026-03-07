# Bootstrap Guide

Guia operacional dos scripts de bootstrap para Windows e Ubuntu WSL.

## Entrypoints e tasks oficiais

Scripts principais:

- `bootstrap/_start.ps1`: menu e entrypoint do Windows host.
- `bootstrap/bootstrap-windows.ps1`: fluxo Windows (`full`, `refresh`,
  `relink`).
- `bootstrap/bootstrap-ubuntu-wsl.sh`: fluxo Ubuntu WSL (`full`, `relink`).
- `bootstrap/bootstrap-config.ps1`: parser, wizard e sincronismo da config.

Tasks oficiais:

- `task bootstrap`
- `task bootstrap:windows:new`
- `task bootstrap:windows:refresh`
- `task bootstrap:relink`
- `task bootstrap:windows:relink`
- `task bootstrap:linux:relink`

## Fluxograma de referencia

O diagrama decisorio completo do bootstrap fica em:

- `../docs/bootstrap-flow.md`

Este README resume o fluxo operacional e os contratos principais.

## Config central

Arquivos:

- `bootstrap/user-config.yaml.tpl`: template versionado
- `bootstrap/user-config.yaml`: arquivo local ignorado

O YAML define:

- identidade Git
- refs de segredos no 1Password
- estrategia OneDrive no Windows
- caminhos canonicos de clients, projects e links de perfil
- estrategia de links opcionais em drive raiz
- configuracao de usuario extra no WSL

## Artefatos derivados

Quando o YAML e validado ou regenerado, o bootstrap sincroniza:

- `df/secrets/secrets-ref.yaml`
- `bootstrap/secrets/.env.local.tpl`
- `df/git/.gitconfig.local` local e nao versionado

## Fluxo Windows full

1. valida pre-requisitos basicos e a config YAML
2. resolve politica OneDrive
3. prepara layout local ou OneDrive
4. cria links canonicos do perfil e do repo
5. instala software, modulos e fontes
6. resolve runtime secrets via 1Password
7. cifra runtime env em `~/.env.local.sops`
8. autentica `gh` e garante protocolo SSH
9. roda `checkEnv`
10. roda validacao dedicada do layout OneDrive
11. aplica preferencias Windows quando o modo e full

## Fluxo Windows refresh

- reaproveita config, auth, signer e validacoes
- nao reinstala o catalogo completo de software e fontes
- nao reaplica preferencias pesadas do sistema

## Fluxo relink

Use quando o objetivo for apenas reparar links quebrados.

Windows:

- `task bootstrap:windows:relink`
- `task bootstrap:relink`

Linux/WSL:

- `task bootstrap:linux:relink`
- `task bootstrap:relink`

Garantias atuais:

- reusa o layout canonico da config
- nao reinstala software
- nao reexecuta bootstrap pesado
- valida estado final dos links no fluxo correspondente

## Fluxo Ubuntu WSL

1. instala base via `apt` e Homebrew
2. cria symlinks de shell, Git, SSH e config
3. resolve `OP_SERVICE_ACCOUNT_TOKEN`
4. gera runtime env e cifra em `~/.env.local.sops`
5. persiste `SOPS_AGE_KEY` no runtime local
6. garante auth do `gh`
7. roda `checkEnv`

## Testabilidade atual

O bootstrap ja possui cobertura automatizada real para `relink`:

- Linux em container OCI com Bats
- Windows em ambiente temporario real com PowerShell

Comandos:

- `task test:integration:linux`
- `task test:integration:windows`

## Modelo de autenticacao

- `op`: fonte de refs de segredo
- `gh`: login por token vindo do 1Password
- SSH: prioridade para 1Password SSH Agent
- Git signing: `gpg.format=ssh` com `op-ssh-sign`

## Troubleshooting rapido

- `checkEnv` falha em `gpg.ssh.program`: valide `op-ssh-sign` no `PATH`.
- `gh` sem protocolo SSH: rode `gh config set git_protocol ssh --host github.com`.
- `ssh -T git@github.com` falha: confirme chave publica e agent do 1Password.
- `~/.env.local.sops` ausente: rerode bootstrap ou a etapa de auth/secrets.
- links quebrados: rode `task bootstrap:relink`.
- layout OneDrive inconsistente: valide a config e o resultado de
  `Test-OneDriveLayoutHealth` no Windows.
