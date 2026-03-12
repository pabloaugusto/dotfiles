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

- `app/bootstrap/`: entrypoints e fluxo de provisionamento.
- `app/df/powershell/`: perfil e utilitários Windows.
- `app/df/bash/`, `app/df/zsh/`, `app/df/.aliases`: shell Unix/WSL.
- `app/df/git/`: config Git base + overlays por ambiente.
- `app/df/ssh/`: política SSH global + variações por SO.
- `app/df/secrets/`: refs e política `sops`.
- `docs/`: documentação detalhada por domínio.

## Fluxo Windows (canônico)

1. `app/bootstrap/_start.ps1`
2. valida config YAML (`app/bootstrap/bootstrap-config.ps1`)
3. executa `app/bootstrap/bootstrap-windows.ps1`
4. gera runtime env cifrado (`~/.env.local.sops`)
5. autentica `gh`
6. roda `checkEnv`

## Fluxo WSL (canônico)

1. `app/bootstrap/bootstrap-ubuntu-wsl.sh`
2. instala base (`apt` + Homebrew)
3. cria symlinks e prepara shell
4. gera runtime env cifrado
5. autentica `gh`
6. roda `checkEnv`

## Configuração central

Fonte única local:

- `app/bootstrap/user-config.yaml` (ignorado)
- template versionado: `app/bootstrap/user-config.yaml.tpl`

Derivados automáticos:

- `app/df/secrets/secrets-ref.yaml`
- `app/bootstrap/secrets/.env.local.tpl`
- `app/df/git/.gitconfig.local`

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

1. fluxo canônico: `task sync` no ambiente atual
2. `task sync:wsl-gate` no Windows (sincroniza e valida clone WSL via Git-only)
3. testes no WSL

Aliases determinísticos (sem prompt), quando necessário:

- `task sync:update`
- `task sync:update-safe`
- `task sync:publish MSG="..."`
