# Inventario de Leituras 1Password no Runtime

- Status: `mapped-for-dot-85`
- Data-base: `2026-03-08`
- Relacionados:
  - [`../2026-03-07-onepassword-batch-resolution.md`](../2026-03-07-onepassword-batch-resolution.md)
  - [`../2026-03-07-parecer-e-plano-inicial.md`](../2026-03-07-parecer-e-plano-inicial.md)
  - [`../../../docs/secrets-and-auth.md`](../../../docs/secrets-and-auth.md)
  - [`../../../df/powershell/_functions.ps1`](../../../df/powershell/_functions.ps1)
  - [`../../../df/bash/.inc/check-env.sh`](../../../df/bash/.inc/check-env.sh)
  - [`../../../df/bash/.inc/secrets-manager.sh`](../../../df/bash/.inc/secrets-manager.sh)
  - [`../../../scripts/git_signing_lib.py`](../../../scripts/git_signing_lib.py)
  - [`../../../bootstrap/bootstrap-ubuntu-wsl.sh`](../../../bootstrap/bootstrap-ubuntu-wsl.sh)

## Objetivo

Mapear onde o runtime ainda executa `op whoami`, `op read` ou `op inject` para
reduzir chamadas repetitivas ao 1Password e preparar as proximas subtasks:

- `DOT-86`: definir o contrato de cache e invalidacao
- `DOT-87`: aplicar o cache agressivo no shell e no `checkEnv`

## Metodo

Busca usada nesta rodada:

```text
rg -n "\bop\s+(read|item get|run|inject|whoami|service-account|signin)\b" \
  df/powershell/_functions.ps1 \
  df/bash/.inc/check-env.sh \
  df/bash/.inc/secrets-manager.sh \
  scripts/git_signing_lib.py \
  bootstrap/bootstrap-ubuntu-wsl.sh -S
```

## Hotspots confirmados

| Arquivo | Linhas | Chamadas | Leitura operacional | Prioridade |
| --- | --- | --- | --- | --- |
| [`../../../df/powershell/_functions.ps1`](../../../df/powershell/_functions.ps1) | `1224`, `1385`, `1722`, `1731`, `1763`, `1857`, `2682` | `op inject`, `op read`, `op whoami` | hot path de terminal, `checkEnv`, signer e fallback de token GitHub | `P0` |
| [`../../../df/bash/.inc/check-env.sh`](../../../df/bash/.inc/check-env.sh) | `105`, `120`, `143`, `166`, `265` | `op whoami`, `op read` | valida shell interativo, session check, fallback de token e signer tecnico | `P0` |
| [`../../../df/bash/.inc/secrets-manager.sh`](../../../df/bash/.inc/secrets-manager.sh) | `31`, `200`, `224` | `op whoami`, `op read`, `op inject` | camada de resolucao de secrets acionada por comandos de runtime bash | `P1` |
| [`../../../scripts/git_signing_lib.py`](../../../scripts/git_signing_lib.py) | `117` | `op read` | signer tecnico recorre ao cofre quando a chave publica ainda nao esta materializada na worktree | `P1` |
| [`../../../bootstrap/bootstrap-ubuntu-wsl.sh`](../../../bootstrap/bootstrap-ubuntu-wsl.sh) | `391`, `558` | `op inject`, `op read` | bootstrap e fallback de token GitHub fora do hot path de abertura de shell | `P2` |

## Priorizacao operacional

### P0 - Shell interativo e health-check

- PowerShell `checkEnv`
- Bash `checkEnv`
- fallback de token GitHub em shell interativo
- leitura da chave publica tecnica quando o cache local ainda nao estiver valido

Esses caminhos sao os mais urgentes porque afetam abertura de terminal,
diagnostico recorrente e o signer tecnico usado durante a rodada.

### P1 - Runtime sob comando explicito

- [`df/bash/.inc/secrets-manager.sh`](../../../df/bash/.inc/secrets-manager.sh)
- [`scripts/git_signing_lib.py`](../../../scripts/git_signing_lib.py)

Sao caminhos menos frequentes que o shell interativo, mas ainda entram no raio
de operacao diaria e podem reacender o problema sob carga.

### P2 - Bootstrap

- [`bootstrap/bootstrap-ubuntu-wsl.sh`](../../../bootstrap/bootstrap-ubuntu-wsl.sh)

Mantem uso de `op` em pontos controlados e nao e o foco imediato da mitigacao,
porque nao roda a cada nova sessao interativa.

## Findings desta rodada

### 1. `checkEnv` continua sendo um dos maiores consumidores de `op`

Os fluxos de shell e PowerShell ainda usam `op whoami` para validar sessao e
`op read` para provar refs criticas. Isso e bom para diagnostico profundo, mas
fica caro quando cai em aberturas frequentes de terminal.

### 2. Fallback de `GH_TOKEN` e signer tecnico ainda batem no cofre na borda errada

Os caminhos de fallback do `GitHub CLI` e da chave publica tecnica ainda podem
fazer `op read` em shell interativo quando o cache nao estiver materializado.
Esse e o principal alvo das proximas subtasks.

### 2.1. `checkEnv` duplica comportamento em Bash e PowerShell

Os dois lados da stack validam sessao `op`, testam refs e resolvem fallback de
token do GitHub. Isso cria duplicacao funcional e aumenta a probabilidade de
tempestade de leituras quando o usuario alterna entre host Windows e WSL.

### 3. `op inject` no bootstrap e aceitavel

Os usos de `op inject` em bootstrap e geracao de env continuam adequados porque
rodam fora do hot path do shell interativo. Eles nao sao o principal problema
de latencia ou rate limit.

### 4. O cache da chave publica tecnica resolveu apenas uma fatia do problema

O signer tecnico ja ganhou fallback por cache da chave publica, mas o runtime
ainda nao tem uma camada equivalente para token GitHub, sessao `op` e refs
frequentes do `checkEnv`.

## Recomendacao para `DOT-86`

Definir um contrato canonico de cache local e invalidacao com:

- borda unica de resolucao por shell/session
- TTL curto para valores sensiveis
- cache persistente apenas para material publico ou de baixo risco
- `n/a` explicito para secrets que nao podem ficar fora de memoria

## Recomendacao para `DOT-87`

Aplicar primeiro nos caminhos de maior frequencia:

1. `checkEnv` de PowerShell
2. `checkEnv` de Bash
3. fallback de `GH_TOKEN` / `GITHUB_TOKEN`
4. chave publica tecnica do signer em [`../../../scripts/git_signing_lib.py`](../../../scripts/git_signing_lib.py)
5. resolver de refs do `secrets-manager`

## Evidencias

- inventario executado localmente por `rg`
- hotspots confirmados em arquivos versionados do repo
- diagnostico anterior de rate limit registrado em
  [`../2026-03-07-onepassword-batch-resolution.md`](../2026-03-07-onepassword-batch-resolution.md)
