# Contexto Do Pack

Este prompt pack existe para materializar no repo a camada de `Pre-Execution Alignment`
sem desconectar a execucao das regras reais do [`dotfiles`](../../../../README.md).

## Contexto especifico do repo

- [`Jira`](https://pabloaugusto.atlassian.net/jira/software/projects/DOT/boards/1)
  e a fonte primaria do fluxo vivo
- [`docs/AI-WIP-TRACKER.md`](../../../../docs/AI-WIP-TRACKER.md) e fallback contingencial
- o `Epic` canonico desta frente e [`DOT-71`](https://pabloaugusto.atlassian.net/browse/DOT-71)
- a promocao deste pack foi aberta em [`DOT-178`](https://pabloaugusto.atlassian.net/browse/DOT-178)
- startup, worklog, fallback, delegacao, review, lessons e closeout ja possuem
  backend real no repo e nao podem ser substituidos por texto livre de prompt

## Fronteiras

- este pack nao autoriza operar fora de [`AGENTS.md`](../../../../AGENTS.md),
  [`LICOES-APRENDIDAS.md`](../../../../LICOES-APRENDIDAS.md),
  [`docs/ai-operating-model.md`](../../../../docs/ai-operating-model.md) e
  [`config/ai/contracts.yaml`](../../../../config/ai/contracts.yaml)
- o PEA deve reduzir drift antes da execucao, nao competir com o enforcement
  real dos hooks, tasks, validadores e workflows
- quando houver delegacao, o resumo do PEA so e valido se viajar junto com a
  issue dona, a branch atual, o startup report e as regras aplicaveis

## Arquivos vivos relacionados

- [`AGENTS.md`](../../../../AGENTS.md)
- [`docs/AI-STARTUP-GOVERNANCE-MANIFEST.md`](../../../../docs/AI-STARTUP-GOVERNANCE-MANIFEST.md)
- [`docs/AI-STARTUP-AND-RESTART.md`](../../../../docs/AI-STARTUP-AND-RESTART.md)
- [`docs/AI-DELEGATION-FLOW.md`](../../../../docs/AI-DELEGATION-FLOW.md)
- [`docs/TASKS.md`](../../../../docs/TASKS.md)
- [`docs/ai-operating-model.md`](../../../../docs/ai-operating-model.md)
- [`config/ai/contracts.yaml`](../../../../config/ai/contracts.yaml)
- [`config/ai/agent-operations.yaml`](../../../../config/ai/agent-operations.yaml)
- [`scripts/ai_session_startup_lib.py`](../../../../scripts/ai_session_startup_lib.py)
- [`scripts/validate-ai-assets.py`](../../../../scripts/validate-ai-assets.py)

## Resultado esperado

- a arvore [`.agents/prompts/`](../../README.md) passa a ter uma trilha formal
  e catalogada para o PEA/startup
- o startup oficial passa a carregar essa camada e expor `pea_status`
- a delegacao passa a reconhecer quando deve carregar classificacao, assuncoes
  e ambiguidades do PEA junto do pacote minimo de contexto
