# Dotfiles Context Map

Mapa técnico do estado atual do repositório.

## Objetivo

Padronizar ambiente de trabalho em:

- Windows host (principal)
- Ubuntu WSL (paridade operacional)

Com foco em:

- bootstrap reproduzível
- secrets/runtime seguros
- autenticação GitHub estável
- assinatura de commits via SSH/1Password

## Estrutura principal

- `bootstrap/`: entrypoints e fluxo de provisionamento.
- `df/powershell/`: perfil e utilitários Windows.
- `df/bash/`, `df/zsh/`, `df/.aliases`: shell Unix/WSL.
- `df/git/`: config Git base + overlays por ambiente.
- `df/ssh/`: política SSH global + variações por SO.
- `df/secrets/`: refs e política `sops`.
- `docs/`: documentação detalhada por domínio.

## Fluxo Windows (canônico)

1. `bootstrap/_start.ps1`
2. valida config YAML (`bootstrap/bootstrap-config.ps1`)
3. executa `bootstrap/bootstrap-windows.ps1`
4. gera runtime env cifrado (`~/.env.local.sops`)
5. autentica `gh`
6. roda `checkEnv`

## Fluxo WSL (canônico)

1. `bootstrap/bootstrap-ubuntu-wsl.sh`
2. instala base (`apt` + Homebrew)
3. cria symlinks e prepara shell
4. gera runtime env cifrado
5. autentica `gh`
6. roda `checkEnv`

## Configuração central

Fonte única local:

- `bootstrap/user-config.yaml` (ignorado)
- template versionado: `bootstrap/user-config.yaml.tpl`

Derivados automáticos:

- `df/secrets/secrets-ref.yaml`
- `bootstrap/secrets/.env.local.tpl`
- `df/git/.gitconfig.local`

## Segurança operacional

- refs `op://...` para secrets
- `.env.local.sops` em vez de `.env.local` plaintext
- `SOPS_AGE_KEY` persistido em env de usuário
- `OP_SERVICE_ACCOUNT_TOKEN` não persistido por padrão
- SSH + assinatura Git via 1Password

## Gate de conformidade

`checkEnv` (PowerShell e Bash) valida:

- dependências (`op`, `gh`, `git`, `ssh`, `sops`, `age`)
- sessão 1Password
- auth/protocolo `gh`
- política Git de assinatura
- política SSH/agent
- handshake GitHub
- commit assinado de teste

## Sincronismo Windows <-> WSL

Prática operacional esperada antes de testes cross-platform:

1. commit/push no Windows
2. `dfsync` no Windows (sincroniza e valida WSL)
3. testes no WSL
