# Contexto Do Pack

Este prompt pack formaliza a camada de governanca documental por agentes de IA
no repo [`dotfiles`](../../../../README.md), sem reinventar a infraestrutura de
sincronismo ja tratada pela fundacao oficial de sync.

## Dependencias e ordem segura

- prerequisite packs:
  - `sync-outbox-foundation`
- preflight packs:
  - `startup-alignment`
- ordem segura:
  1. checar `startup-alignment` quando a sessao vier sem continuidade
     comprovadamente integra
  2. executar ou validar `sync-outbox-foundation`
  3. so depois executar `documentation-layer-governance`

## Fronteiras

- este pack nao redefine `workspace_id`
- este pack nao redefine `runtime_environment_id`
- este pack NAO redefine o protocolo de outbox, `ack`, retry, `dead-letter` ou
  `retention_policy`
- este pack usa a infraestrutura-base definida pelo pack
  [`sync-outbox-foundation`](../sync-outbox-foundation/prompt.md)
- este pack governa ownership, source of truth, lifecycle, placement e sync
  documental, mas nao recria a fundacao tecnica de sincronismo

## Arquivos vivos relacionados

- [`AGENTS.md`](../../../../AGENTS.md)
- [`docs/ai-operating-model.md`](../../../../docs/ai-operating-model.md)
- [`config/ai/contracts.yaml`](../../../../config/ai/contracts.yaml)
- `sync-targets.yaml` em [`config/ai/`](../../../../config/ai/)
- [`scripts/validate-ai-assets.py`](../../../../scripts/validate-ai-assets.py)
- [`scripts/ai-prompt-governance.py`](../../../../scripts/ai-prompt-governance.py)
- [`scripts/ai_session_startup_lib.py`](../../../../scripts/ai_session_startup_lib.py)
- [`../startup-alignment/prompt.md`](../startup-alignment/prompt.md)
- [`../sync-outbox-foundation/prompt.md`](../sync-outbox-foundation/prompt.md)

## Resultado esperado

- a camada documental passa a ter ownership explicito por superficie
- a trilha documental passa a depender formalmente da fundacao de sync
- `Pascoalete` e `Escrivao` passam a operar com fronteiras endurecidas
- a sync documental deixa de ser um escopo implicito e passa a ter papel
  proprio, consumindo a fundacao oficial
