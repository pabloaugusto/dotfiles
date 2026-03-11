# Prompt Para Codex - Formalizar Arquitetura Agnostica De Sync, Outbox E Fonte Perene

<!-- cspell:words Agnostica Missao fundacao sincronizacao duravel solucao repositorio portavel replicacao definicao portaveis padrao worktrees persistencia elegiveis idempotencia obrigatorio implementacao estavel fisico facil aplicavel minimos unica Tambem concluido resolucao validacoes canonicos catalogos existencia sincronizavel efemeros tecnicos relevancia historica redundancias publicacao transitorio migracoes obrigatorias legivel ligacao proximos Criterios concluida Instrucao codigo worktree agnostico agnostica separacao dependencia testavel validacao -->

## Missao

Implementar, de ponta a ponta, a fundacao de uma arquitetura agnostica de
sincronizacao para artefatos vivos de IA, separando com rigor:

1. artefatos declarativos versionados no repo
2. estado local duravel fora do repo
3. fonte perene remota de verdade, como `Confluence`

Esta solucao NAO pode ficar acoplada ao nome atual deste repositorio.
Ela deve nascer portavel para replicacao em outros repos.

## Decisoes ja fechadas

Estas decisoes ja foram tomadas e NAO devem ser reabertas nesta rodada:

1. `repo` guarda apenas definicao, contrato e artefatos declarativos portaveis
2. runtime duravel NAO fica em `.cache`
3. runtime duravel NAO fica em `.outbox` dentro do repo
4. o root local padrao deve ser `~/.ai-control-plane/` em Windows e WSL/Linux
5. worktrees e clones diferentes NAO podem ser a base da persistencia local
6. o historico perene oficial deve viver em fonte remota apropriada
7. `Confluence` e o destino principal para os runtime ledgers elegiveis
8. o estado local deve funcionar como outbox duravel ate confirmacao remota
9. o repo deve versionar um manifest declarativo de sincronizacao em
   [`config/ai/sync-targets.yaml`](../../../../config/ai/)

## Objetivo tecnico

Entregar a fundacao correta para o fluxo:

`repo declarativo -> outbox local duravel -> fonte perene remota`

com:

- arquitetura modular
- nomenclatura agnostica
- sem drift entre docs, contracts e codigo
- compatibilidade Windows host e Ubuntu WSL
- idempotencia
- zero ambiguidade sobre o que e contrato, runtime local e ledger perene

## Modelo obrigatorio

### Camada 1 - Repo versionado

O repo deve continuar guardando apenas:

- prompts
- metadados
- contratos
- docs
- manifest declarativo de sync
- schemas, validadores e testes dessa arquitetura

Nada de churn de runtime no Git.

### Camada 2 - State local duravel fora do repo

Toda pendencia de sincronizacao deve viver fora do repo, sob:

`~/.ai-control-plane/workspaces/<workspace-id>/`

Estrutura minima obrigatoria:

- `outbox/`
- `status/`
- `checkpoints/`
- `dead-letter/`

### Camada 3 - Fonte perene remota

O destino perene oficial dos runtime ledgers elegiveis deve ser remoto.

Destino principal desta rodada:

- `Confluence`

A implementacao deve preparar a base para suportar outros destinos no futuro,
como `Jira`, `filesystem` ou `webhook`, sem reescrever a arquitetura.

## Identidade obrigatoria

A arquitetura deve separar obrigatoriamente duas identidades diferentes:

- `workspace_id`
- `runtime_environment_id`

### `workspace_id`

`workspace_id` identifica o contexto logico do workspace ou projeto.

Ele obrigatoriamente deve ser:

- estavel
- curto
- ASCII
- `kebab-case`
- desacoplado do path local do clone
- desacoplado do nome fisico atual do repositorio

Se o projeto atual ainda nao possuir um identificador melhor, implementar um
valor inicial neutro, documentado e facil de evoluir sem quebrar a arquitetura.

### `runtime_environment_id`

`runtime_environment_id` identifica o ambiente concreto em que a execucao
aconteceu.

Ele deve permitir distinguir, no minimo:

- maquina ou host
- familia de sistema operacional
- tipo de runtime
- distro, quando aplicavel

### Tipos minimos de runtime

Implementar suporte conceitual, no minimo, para:

- `host`
- `wsl`
- `container`
- `ci`

### Regras negativas

- nao usar apenas hostname cru como identidade unica
- nao substituir `workspace_id` por `runtime_environment_id`
- nao confundir contexto logico do projeto com ambiente concreto de execucao

## Manifest obrigatorio

Implementar o contrato versionado em:

[`config/ai/sync-targets.yaml`](../../../../config/ai/)

O manifest deve declarar, no minimo, por artefato:

- `artifact_type`
- `definition_source`
- `source_of_truth`
- `remote_target`
- `local_outbox`
- `retention_policy`

Tambem deve suportar uma raiz agnostica de workspace e a separacao entre
identidade logica e identidade de runtime.

Exemplo minimo de referencia sem prender a implementacao:

```yaml
version: 1
workspace:
  id: core-governance
  state_root: ~/.ai-control-plane

runtime_identity:
  strategy: derived
  fields:
    - host_name
    - os_family
    - runtime_kind
    - distro

artifacts:
  prompt_runs:
    artifact_type: runtime_ledger
    definition_source: repo
    source_of_truth: confluence
    remote_target:
      kind: confluence
      strategy: per-prompt
    local_outbox:
      path: outbox/confluence/prompt-runs.jsonl
    retention_policy:
      on_remote_ack: compact
      keep_last_synced_days: 14
```

## Formato operacional dos eventos

O outbox deve usar `jsonl` como formato operacional.

Cada evento deve carregar, no minimo:

- `event_id`
- `workspace_id`
- `runtime_environment_id`
- `artifact_key`
- `record_key`
- `occurred_at`
- `execution_status`
- `effectiveness_status`
- `payload`
- `sync`

Tambem deve existir um bloco de runtime suficientemente rico para auditoria.

Exemplo minimo de referencia:

```json
{
  "event_id": "evt_01",
  "workspace_id": "core-governance",
  "runtime_environment_id": "workstation-wsl-ubuntu",
  "artifact_key": "prompt_runs",
  "record_key": "pea-startup-governance",
  "occurred_at": "2026-03-11T18:40:00Z",
  "execution_status": "success",
  "effectiveness_status": "effective",
  "runtime": {
    "host_name": "workstation",
    "os_family": "linux",
    "runtime_kind": "wsl",
    "distro": "Ubuntu"
  },
  "payload": {
    "summary": "PEA aplicado e validado"
  },
  "sync": {
    "status": "pending",
    "attempts": 0
  }
}
```

## Regra de sincronizacao obrigatoria

A arquitetura deve obedecer a esta ordem:

1. gravar primeiro no outbox local
2. tentar sincronizar no destino remoto
3. considerar concluido apenas apos `ack` remoto explicito
4. nunca apagar evento antes do `ack`
5. apos `ack`, compactar ou podar conforme a `retention_policy`
6. quando houver falha recorrente, permitir envio para `dead-letter`
7. o processo deve ser idempotente e seguro para retry

## Escopo obrigatorio desta rodada

Implementar, no minimo:

1. o manifest declarativo de sync
2. uma camada central de resolucao de paths, workspace state e runtime identity
3. a base para outbox local duravel fora do repo
4. a base para sync remoto perene com `Confluence`
5. validacoes automatizadas da estrutura
6. documentacao da arquitetura
7. classificacao inicial dos artefatos vivos atuais do repo

## Classificacao obrigatoria dos artefatos vivos

Voce DEVE auditar os artefatos vivos atuais e classifica-los em tres grupos:

### 1. Permanecem canonicos e versionados no repo

Usar para:

- contratos
- docs de governanca
- catalogos
- ledgers que ainda sao fonte de verdade local do projeto
- artefatos cuja existencia no Git e parte do contrato operacional

### 2. Candidatos a runtime ledger sincronizavel

Usar para artefatos operacionais cujo historico perene deve viver em fonte
remota e cujo buffer local deve existir apenas como outbox duravel.

### 3. Nao elegiveis para sync remoto

Usar para:

- artefatos efemeros
- logs tecnicos de baixa relevancia historica
- redundancias
- artefatos inadequados para publicacao remota
- artefatos cujo valor real e apenas local ou transitorio

Nao faca migracao cega.
Classifique primeiro, justifique e so depois proponha migracoes.

## Regras negativas obrigatorias

Durante esta implementacao:

- nao usar `.cache` para estado duravel
- nao usar `.outbox` dentro do repo como persistencia principal
- nao registrar `last_run` no corpo dos prompts
- nao criar `log.md` versionado por execucao dentro dos packs
- nao acoplar a arquitetura ao nome atual do repositorio
- nao depender da existencia de apenas uma worktree
- nao criar framework paralelo desconectado da governanca atual
- nao introduzir dependencia dura de rede nos testes
- nao mover todos os `.md` vivos para o remoto sem classificacao previa

## Qualidade obrigatoria

A implementacao precisa ser:

- modular
- legivel
- testavel
- idempotente
- agnostica ao repo
- coerente com Windows e WSL
- alinhada ao contrato de governanca existente
- sem drift entre docs, contracts, tests e validadores

## Descoberta obrigatoria antes de editar

Antes de implementar, mapear no projeto real:

- onde ficam os contratos vivos
- quais ledgers e logs atuais sao canonicos
- quais sao operacionais
- quais ja possuem ligacao com `Confluence`
- onde a governanca de artefatos vivos ja existe
- quais validadores e tasks precisam absorver a nova arquitetura

Nao assumir por memoria.
Descobrir no repo real e adaptar a implementacao ao backend existente.

## Entregas obrigatorias

Ao final, entregar:

1. codigo implementado
2. `config/ai/sync-targets.yaml`
3. documentacao da arquitetura
4. classificacao inicial dos artefatos vivos atuais
5. testes e validacoes da nova camada
6. resumo final objetivo com:
   - o que foi implementado
   - como a arquitetura funciona
   - quais artefatos permanecem no repo
   - quais passam a ser candidatos a sync remoto
   - riscos remanescentes e proximos passos

## Criterios de aceite

A rodada so conta como concluida se:

1. a arquitetura ficar claramente separada entre repo, state local e remoto
2. o state local ficar fora do repo e fora de `.cache`
3. o manifest declarativo existir e ficar coerente com o codigo
4. o `workspace_id` ficar agnostico ao nome do repo atual
5. o `runtime_environment_id` permitir distinguir execucao em host, WSL, container ou CI
6. o outbox local suportar retries e `ack` remoto sem perda silenciosa
7. a base para `Confluence` como fonte perene ficar pronta
8. a classificacao dos artefatos vivos ficar explicita e justificada
9. docs, tests e validadores refletirem a mesma regra

## Instrucao final

Implemente esta fundacao como infraestrutura portavel e perene.

- trate `repo = definicao`
- trate `~/.ai-control-plane = state duravel`
- trate `Confluence = historico perene`
- nao improvise solucao local de worktree
- nao reduza esta entrega a brainstorm ou plano
- entregue backend real, docs reais, validacao real e classificacao auditavel
