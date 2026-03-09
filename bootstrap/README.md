# Bootstrap Guide

Guia operacional dos scripts de bootstrap para Windows e Ubuntu WSL.

## Entrypoints e tasks oficiais

Scripts principais:

- [`bootstrap/_start.ps1`](./_start.ps1): menu e entrypoint do Windows host.
- [`bootstrap/bootstrap-windows.ps1`](./bootstrap-windows.ps1): fluxo Windows (`full`, `refresh`,
  `relink`).
- [`bootstrap/bootstrap-ubuntu-wsl.sh`](./bootstrap-ubuntu-wsl.sh): fluxo Ubuntu WSL (`full`, `relink`).
- [`bootstrap/bootstrap-config.ps1`](./bootstrap-config.ps1): parser, wizard e sincronismo da config.

Tasks oficiais:

- `task bootstrap`
- `task bootstrap:windows:new`
- `task bootstrap:windows:refresh`
- `task bootstrap:relink`
- `task bootstrap:windows:relink`
- `task bootstrap:linux:relink`

## Fluxograma de referencia

O diagrama decisorio completo do bootstrap fica em:

- [`../docs/bootstrap-flow.md`](../docs/bootstrap-flow.md)

Este README resume o fluxo operacional e os contratos principais.

## Config central

Arquivos:

- [`bootstrap/user-config.yaml.tpl`](./user-config.yaml.tpl): template versionado
- arquivo local ignorado documentado em [`../docs/config-reference.md`](../docs/config-reference.md#bootstrapuser-configyaml)

O YAML define:

- identidade Git
- signer humano e ref opcional do signer tecnico de automacao
- refs de segredos no 1Password
- estrategia OneDrive no Windows
- caminhos canonicos de clients, projects e links de perfil
- estrategia de links opcionais em drive raiz
- configuracao de usuario extra no WSL

## Artefatos derivados

Quando o YAML e validado ou regenerado, o bootstrap sincroniza:

- [`df/secrets/secrets-ref.yaml`](../df/secrets/secrets-ref.yaml)
- [`bootstrap/secrets/.env.local.tpl`](./secrets/.env.local.tpl)
- derivado local nao versionado documentado em [`../docs/secrets-and-auth.md`](../docs/secrets-and-auth.md#ssh-agent-e-git-signing)

Quando configurado, o bootstrap tambem propaga a ref da chave publica tecnica
para `git-signing.automation-public-key` em [`df/secrets/secrets-ref.yaml`](../df/secrets/secrets-ref.yaml),
permitindo que a worktree aplique o signer tecnico sem copiar segredo para o repo.

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
- em worktree de automacao, se o handshake cru continuar exigindo aprovacao do
  1Password, valide `task env:check SIGN_MODE=automation` e confirme o
  `core.sshCommand` tecnico da worktree.
- `~/.env.local.sops` ausente: rerode bootstrap ou a etapa de auth/secrets.
- links quebrados: rode `task bootstrap:relink`.
- layout OneDrive inconsistente: valide a config e o resultado de
  `Test-OneDriveLayoutHealth` no Windows.
