# AI Sync Foundation

## Objetivo

Estabelecer a arquitetura-base obrigatoria para qualquer sincronismo perene do
repo:

- repo declarativo versionado
- outbox local duravel fora do Git
- fonte perene remota elegivel

Esta fundacao existe para impedir tres drifts comuns:

- dominio criando sincronismo ad hoc fora do contrato do repo
- `.cache` sendo promovido informalmente a estado duravel
- publicacao remota sem `ack`, sem retry consistente e sem trilha recuperavel

## Contrato central

A fundacao de sync deste repo segue o modelo:

`repo declarativo -> outbox local duravel -> fonte perene remota`

O contrato versionado fica em
[`config/ai/sync-targets.yaml`](../config/ai/sync-targets.yaml).

O state local duravel fica fora do repo, por padrao em:

`~/.ai-control-plane/workspaces/<workspace_id>/`

Nenhum dominio pode:

- redefinir `workspace_id`
- redefinir `runtime_environment_id`
- criar outbox paralelo
- ignorar `ack`
- ignorar retry
- ignorar `dead-letter`
- publicar remotamente sem classificacao previa do artefato

## Identidades obrigatorias

### `workspace_id`

Identifica o workspace logico do repo dentro do state root duravel.

No contrato atual, ele e definido em
[`config/ai/sync-targets.yaml`](../config/ai/sync-targets.yaml) e nao deve ser
recalculado por dominio consumidor.

### `runtime_environment_id`

Identifica o runtime efetivo da execucao, derivado da combinacao de campos como:

- `host_name`
- `os_family`
- `runtime_kind`
- `distro`

Essas identidades existem para resolver o historico multiambiente sem misturar:

- Windows host
- WSL
- container
- CI

## Estrutura local duravel

Sob `~/.ai-control-plane/workspaces/<workspace_id>/`, a fundacao usa esta
estrutura minima:

- `outbox/`
- `status/`
- `checkpoints/`
- `dead-letter/`

### `outbox/`

Fila local duravel de eventos ainda nao `acked` remotamente.

### `status/`

Snapshots compactos de estado por artifact key, incluindo:

- quantidade pendente
- quantidade retida
- `last_synced_at`
- ultimo `event_id` com sucesso

### `checkpoints/`

Checkpoint do ultimo sync bem-sucedido por artifact key.

### `dead-letter/`

Eventos esgotados apos o numero maximo de tentativas configurado.

## Manifest declarativo

O arquivo
[`config/ai/sync-targets.yaml`](../config/ai/sync-targets.yaml) e a fonte
versionada do contrato de sync.

Ele define:

- `workspace`
- `runtime_identity`
- `artifacts`
- `artifact_inventory`

### `workspace`

Define:

- `id`
- `state_root`
- `workspace_dir`

### `runtime_identity`

Define:

- estrategia de derivacao
- campos usados para o `runtime_environment_id`
- tipos validos de runtime

### `artifacts`

Cada artifact key define:

- tipo do artefato
- origem declarativa
- elegibilidade de sync
- fonte de verdade
- destino remoto
- local do outbox
- politica de retencao

### `artifact_inventory`

Classifica o universo relevante do repo em:

- `repo_canonical`
- `runtime_ledger_candidates`
- `remote_ineligible`

## Classificacao de artefatos

### Repo canonical

Permanece canonico e versionado no Git.

Exemplos:

- [`config/ai/`](../config/ai/)
- [`docs/AI-WIP-TRACKER.md`](AI-WIP-TRACKER.md)
- [`docs/AI-REVIEW-LEDGER.md`](AI-REVIEW-LEDGER.md)
- [`docs/AI-SCRUM-MASTER-LEDGER.md`](AI-SCRUM-MASTER-LEDGER.md)

### Runtime ledger candidate

Artefato que pode nascer localmente e ganhar historico remoto perene segundo o
contrato do manifest.

Em outras palavras, e um `runtime ledger candidate`.

Exemplos atuais:

- logs de retrospectiva
- eventos de execucao de prompt

### Remote ineligible

Artefatos que nao devem ser enviados ao remoto perene.

Exemplos:

- `.cache/`
- `platforms.local.yaml`
- [`bootstrap/user-config.yaml.tpl`](../bootstrap/user-config.yaml.tpl) quando o
  arquivo materializado local for apenas derivado efemero
- storages locais do editor
- runtimes locais de ferramentas

## Protocolo operacional

### 1. Registrar evento

O dominio gera um evento local duravel no outbox correspondente.

### 2. Checar fundacao

Usar:

- `task ai:control-plane:sync:check`

Essa task valida:

- manifest
- identidades
- state root
- estrutura local esperada

### 3. Inspecionar estado

Usar:

- `task ai:control-plane:sync:status`

Essa task exibe:

- artifacts
- pendencias
- filas mortas
- inventory

### 4. Drenar

Usar:

- dry-run: `task ai:control-plane:sync:drain`
- apply: `task ai:control-plane:sync:drain APPLY=1`

O fluxo:

- consome o outbox
- publica segundo o destino oficial
- aguarda `ack` remoto
- compacta localmente apenas apos sucesso
- move para `dead-letter` quando excede tentativas

## `ack`, retry e `dead-letter`

### `ack`

Nenhum evento pode ser removido do outbox apenas por tentativa. Ele so pode
ser compactado depois de confirmacao remota bem-sucedida.

### Retry

Falhas temporarias incrementam o contador de tentativas e mantem o evento
pendente.

### `dead-letter`

Quando o numero maximo de tentativas e excedido, o evento sai da fila ativa e
vai para `dead-letter`, mantendo:

- payload
- erro
- tentativa final
- motivo da exaustao

## Destino remoto inicial

A fundacao atual usa `Confluence` como ledger remoto inicial para artefatos
runtime elegiveis, por meio da estrategia `append-page-ledger`.

Isso nao significa que todo artefato vai para `Confluence`.

A elegibilidade depende de:

- classificacao no manifest
- policy do dominio consumidor
- source of truth
- necessidade real de historico perene remoto

## Interface com dominios consumidores

Dominios especializados devem consumir esta fundacao, e nao reimplementa-la.

Exemplo direto:

- o pack
  [`documentation-layer-governance`](../.agents/prompts/formal/documentation-layer-governance/prompt.md)
  usa esta fundacao como base para o futuro `ai-documentation-sync`
- o manifest
  [`config/ai/sync-targets.yaml`](../config/ai/sync-targets.yaml) ja pode
  carregar artefatos como `documentation_links` para `documentation-link`,
  backlinks e rastreabilidade cross-surface quando a policy documental os
  classificar como elegiveis

Regra obrigatoria:

- o dominio decide *o que* deve ser sincronizado
- a fundacao define *como* o sincronismo duravel funciona

## Fronteira com a camada documental

Esta doc nao define:

- quem escreve documentacao
- quem revisa linguagem
- quem revisa qualidade documental
- quem governa source of truth documental

Essas decisoes pertencem ao pack documental, nao a esta fundacao.

Esta fundacao define apenas:

- estrutura duravel
- identidade
- manifest
- fluxo de outbox
- `ack`
- retry
- `dead-letter`
- trilha remota perene

## Guardrails

- `.cache` continua efemero
- runtime duravel continua fora do repo
- nenhum dominio cria manifest paralelo
- nenhum dominio redefine state root
- nenhum dominio publica remoto ignorando o manifest
- nenhum dominio bypassa a fundacao oficial quando o caso e elegivel ao fluxo

## Relacao com os prompts formais

Ordem segura:

1. [`startup-alignment`](../.agents/prompts/formal/startup-alignment/prompt.md)
2. [`sync-outbox-foundation`](../.agents/prompts/formal/sync-outbox-foundation/prompt.md)
3. [`documentation-layer-governance`](../.agents/prompts/formal/documentation-layer-governance/prompt.md)

O prompt foundation define a arquitetura.
O prompt documental a consome.

Eles nao devem ser fundidos.
