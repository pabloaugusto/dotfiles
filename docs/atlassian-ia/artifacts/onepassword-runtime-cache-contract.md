# Contrato de Cache e Invalidacao 1Password no Runtime

- Status: `ready-for-dot-87`
- Data-base: `2026-03-08`
- Fonte canonica:
  [`../../../config/runtime-secrets-cache.yaml`](../../../config/runtime-secrets-cache.yaml)
- Relacionados:
  - [`onepassword-runtime-read-inventory.md`](onepassword-runtime-read-inventory.md)
  - [`../2026-03-07-onepassword-batch-resolution.md`](../2026-03-07-onepassword-batch-resolution.md)
  - [`../../../docs/secrets-and-auth.md`](../../../docs/secrets-and-auth.md)
  - [`../../../df/powershell/_functions.ps1`](../../../df/powershell/_functions.ps1)
  - [`../../../df/bash/.inc/check-env.sh`](../../../df/bash/.inc/check-env.sh)
  - [`../../../df/bash/.inc/secrets-manager.sh`](../../../df/bash/.inc/secrets-manager.sh)
  - [`../../../scripts/git_signing_lib.py`](../../../scripts/git_signing_lib.py)

## Objetivo

Definir a fronteira oficial entre:

- o cache nativo do `1Password CLI`
- o cache adicional do runtime local deste repo
- o que pode ou nao pode sair da memoria durante a sessao

Esse contrato fecha o refinamento do `DOT-86` e prepara a implementacao do
`DOT-87` sem voltar a espalhar `op read` no hot path de terminal.

## Base oficial consultada

- [`1Password CLI environment variables`](https://developer.1password.com/docs/cli/environment-variables/):
  `OP_CACHE` existe e vem `true` por padrao.
- [`1Password CLI reference`](https://developer.1password.com/docs/cli/reference/):
  em sistemas `UNIX-like`, o CLI usa um daemon para cachear itens, vaults e
  chaves; em `Windows`, esse cache entre comandos nao esta disponivel.
- [`op run`](https://developer.1password.com/docs/cli/reference/commands/run/):
  `op run` carrega refs para variaveis de ambiente so durante o subprocesso.
- [`Load secrets into the environment`](https://developer.1password.com/docs/cli/secrets-environment-variables/):
  segredos em variaveis de ambiente evitam plaintext em arquivo, mas devem ser
  tratados como acessiveis a processos do mesmo usuario.
- [`Use service accounts with 1Password CLI`](https://developer.1password.com/docs/service-accounts/use-with-1password-cli/):
  service accounts sao compativeis com `op read`, `op inject`, `op run` e
  `op service-account ratelimit`.
- [`Service account rate limits`](https://developer.1password.com/docs/service-accounts/rate-limits):
  limites horarios e diarios existem, e alguns comandos fazem mais de uma
  request.

## Leitura arquitetural

### 1. O repo deve aproveitar o cache do proprio CLI quando ele existir

O `1Password CLI` ja cacheia informacao de item, vault e chaves em memoria no
daemon em plataformas `UNIX-like`. Isso significa que o runtime dos dotfiles
nao deve criar uma segunda camada complexa antes de reduzir a quantidade de
comandos disparados.

Decisao:

- manter `OP_CACHE=true` como comportamento esperado
- nao desativar o cache nativo do CLI
- reduzir chamadas repetidas feitas pelo runtime

### 2. O Windows continua exigindo compensacao no lado do repo

A documentacao oficial diz que o cache entre comandos nao esta disponivel no
`Windows`. Por isso, a mitigacao precisa existir tambem no runtime local:

- evitar `op whoami` e `op read` repetidos por abertura de shell
- reaproveitar estado recente quando a verificacao ainda estiver fresca
- persistir apenas metadados e material publico

### 3. Cache persistente de segredo continua proibido

O repo ja admite fonte cifrada para runtime em
[`$HOME/.env.local.sops`](../../../docs/secrets-and-auth.md), mas isso e fonte
controlada e cifrada, nao um cache plaintext.

Decisao:

- segredos sensiveis nao podem ir para arquivo plaintext de cache
- `GH_TOKEN`, `GITHUB_TOKEN` e `OP_SERVICE_ACCOUNT_TOKEN` podem existir em
  memoria e em variaveis da sessao atual
- qualquer persistencia em disco para esses valores fica proibida

## Classes canonicas de material

| Classe | Exemplos | Pode persistir? | Onde pode viver | Regra de refresh |
| --- | --- | --- | --- | --- |
| `public_material` | chave publica tecnica de assinatura | sim | `config.worktree`, state file, memoria | mudanca da ref ou refresh explicito |
| `session_metadata` | resultado recente de `op whoami`, snapshot de rate limit, status de `gh auth` | sim, com TTL | state file, memoria, env de sessao | TTL curto ou refresh explicito |
| `session_secret` | `GH_TOKEN`, `GITHUB_TOKEN`, `OP_SERVICE_ACCOUNT_TOKEN` materializados para uma sessao | nao em disco | memoria e env da sessao | ausencia, falha de auth ou refresh explicito |

## TTL e invalidacao

### `session_metadata`

- `ttl_seconds`: `300`
- invalida quando:
  - o TTL expira
  - uma chamada autenticada falha
  - o contexto de conta muda
  - o usuario pede refresh explicito

### `public_material`

- sem TTL obrigatorio
- invalida quando:
  - a ref oficial muda
  - o valor em cache diverge do valor esperado
  - o usuario pede refresh explicito

### `session_secret`

- dura somente enquanto a sessao estiver viva
- invalida quando:
  - o shell termina
  - a autenticacao falha
  - o usuario pede refresh explicito

## Ordem canonica de resolucao

1. variavel ja presente no processo atual
2. cache da sessao atual
3. fonte cifrada de runtime
4. `1Password CLI`

Isso evita bater no cofre cedo demais e preserva o modelo de menor surpresa no
shell interativo.

## Locais canonicos

As raizes por plataforma ficaram versionadas em
[`../../../config/runtime-secrets-cache.yaml`](../../../config/runtime-secrets-cache.yaml):

- `Windows host`: `%LOCALAPPDATA%/dotfiles/state/secrets`
- `WSL / Unix`: `$XDG_STATE_HOME/dotfiles/secrets`
- fallback Unix: `$HOME/.local/state/dotfiles/secrets`

Esses locais sao para estado nao sensivel, como:

- `op-session.json`
- `op-ratelimit.json`
- fingerprints ou metadados de origem

## Regras operacionais

- `checkEnv` nao deve repetir `op whoami` e `op read` se o metadado da sessao
  ainda estiver valido
- fallback de token do `GitHub CLI` deve preferir valor ja resolvido na sessao
  atual antes de reler o cofre
- signer tecnico pode persistir a chave publica em `config.worktree`, porque
  ela e material publico
- `secret.read` e `secret.inject` seguem validos, mas nao podem virar hot path
  de terminal

## O que entra em `DOT-87`

Aplicacao priorizada:

1. [`../../../df/powershell/_functions.ps1`](../../../df/powershell/_functions.ps1)
2. [`../../../df/bash/.inc/check-env.sh`](../../../df/bash/.inc/check-env.sh)
3. fallback de `GH_TOKEN` / `GITHUB_TOKEN`
4. [`../../../scripts/git_signing_lib.py`](../../../scripts/git_signing_lib.py)
5. [`../../../df/bash/.inc/secrets-manager.sh`](../../../df/bash/.inc/secrets-manager.sh)

## Evidencias desta rodada

- hotspot inventory:
  [`onepassword-runtime-read-inventory.md`](onepassword-runtime-read-inventory.md)
- implementacao batch do control plane:
  [`../2026-03-07-onepassword-batch-resolution.md`](../2026-03-07-onepassword-batch-resolution.md)
- contrato geral de auth:
  [`../../../docs/secrets-and-auth.md`](../../../docs/secrets-and-auth.md)
