# Contexto Do Pack

Este prompt pack existe para formalizar a governanca canonica de tempo,
timezone, locale e regionalizacao do repo
[`dotfiles`](../../../../README.md), sem misturar essa camada com a fundacao de
sync nem com a camada documental.

## Contexto especifico do repo

- o repo ja possui `startup`, `restart`, `worklog`, `ledgers`, `validators`,
  `Jira`, `Confluence`, prompt packs formais e fundacao de sync
- hoje existem varios pontos com `UTC` historico, naming herdado e semantica
  temporal misturada entre exibicao humana, auditoria tecnica e token de
  maquina
- ainda nao existe uma policy declarativa unica e canonica para tempo,
  timezone, locale e regionalizacao em um arquivo global do projeto
- esta trilha foi aberta em
  [`DOT-180`](https://pabloaugusto.atlassian.net/browse/DOT-180)
- esta trilha deve propor a consolidacao em um arquivo TOML global canonico do
  projeto
- o inventario por superficie deve ser separado da policy global e viver em um
  registry YAML temporal proprio

```text
Arquivos alvo planejados:
- config/config.toml
- config/time-surfaces.yaml
```

## Fronteiras

- este pack nao substitui [`AGENTS.md`](../../../../AGENTS.md),
  [`LICOES-APRENDIDAS.md`](../../../../LICOES-APRENDIDAS.md),
  [`docs/ai-operating-model.md`](../../../../docs/ai-operating-model.md) nem os
  contratos declarativos em [`config/ai/`](../../../../config/ai/)
- este pack formaliza a governanca temporal; ele nao executa a implementacao
- a implementacao futura deve acontecer em task propria, apartada, com branch,
  worklog, review e validacao proprios
- este pack nao pode reimplementar arquitetura de sync
- este pack nao pode absorver a governanca documental nem a fundacao de sync;
  ele deve consumi-las como referencia quando tocar superficies relacionadas

## Dependencias e ordem segura

- prerequisite packs: nenhum
- preflight packs:
  - [`startup-alignment`](../startup-alignment/prompt.md)
  - [`documentation-layer-governance`](../documentation-layer-governance/prompt.md)
  - [`sync-outbox-foundation`](../sync-outbox-foundation/prompt.md)
- este pack deve ser executado em task propria no futuro, mas com checagem
  previa dos packs acima
- `startup-alignment` protege a camada de preflight e sessao
- `documentation-layer-governance` protege ownership de docs, comments,
  docstrings, prompts e strings legiveis
- `sync-outbox-foundation` protege superficies persistidas, eventos, ledgers e
  qualquer historico remoto elegivel a sincronismo

## Arquivos vivos relacionados

- [`AGENTS.md`](../../../../AGENTS.md)
- [`docs/AI-STARTUP-AND-RESTART.md`](../../../../docs/AI-STARTUP-AND-RESTART.md)
- [`docs/AI-WIP-TRACKER.md`](../../../../docs/AI-WIP-TRACKER.md)
- [`docs/AI-REVIEW-LEDGER.md`](../../../../docs/AI-REVIEW-LEDGER.md)
- [`docs/AI-ORTHOGRAPHY-LEDGER.md`](../../../../docs/AI-ORTHOGRAPHY-LEDGER.md)
- [`docs/AI-SCRUM-MASTER-LEDGER.md`](../../../../docs/AI-SCRUM-MASTER-LEDGER.md)
- [`config/ai/contracts.yaml`](../../../../config/ai/contracts.yaml)
- [`config/ai/sync-targets.yaml`](../../../../config/ai/sync-targets.yaml)
- [`scripts/ai_session_startup_lib.py`](../../../../scripts/ai_session_startup_lib.py)
- [`scripts/ai_sync_foundation_lib.py`](../../../../scripts/ai_sync_foundation_lib.py)
- [`scripts/ai-worklog.py`](../../../../scripts/ai-worklog.py)
- [`scripts/ai_atlassian_backfill_lib.py`](../../../../scripts/ai_atlassian_backfill_lib.py)
- [`scripts/ai_agent_execution_lib.py`](../../../../scripts/ai_agent_execution_lib.py)

## Resultado esperado

- existir um prompt formal, vivo e catalogado para governanca temporal
- a futura execucao ter um contrato claro para criar um arquivo TOML global
  como fonte canonica de configuracoes do projeto
- a futura execucao ter um contrato claro para criar um registry YAML temporal
  por superficie
- o repo passar a ter uma matriz clara para distinguir exibicao humana,
  auditoria tecnica e token temporal de maquina
