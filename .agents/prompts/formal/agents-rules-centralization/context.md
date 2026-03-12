# Contexto Do Pack

Este pack existe para unificar e centralizar a governanca normativa do repo em
[`.agents/rules/`](../../../rules/), reduzindo drift entre
[`AGENTS.md`](../../../../AGENTS.md), [`docs/`](../../../../docs/), contratos
declarativos em [`config/ai/`](../../../../config/ai/) e enforcement
executavel em [`Taskfile.yml`](../../../../Taskfile.yml),
[`.githooks/`](../../../../.githooks/) e scripts.

## Contexto especifico do repo

- [`.agents/rules/`](../../../rules/) ja existe como camada declarativa do repo,
  mas hoje ainda esta subutilizada e parcial
- [`AGENTS.md`](../../../../AGENTS.md) segue como contrato global do projeto
- [`docs/ai-operating-model.md`](../../../../docs/ai-operating-model.md)
  descreve [`.agents/rules/`](../../../rules/) como camada declarativa do
  sistema
- o `Epic` canonico desta frente continua sendo
  [`DOT-71`](https://pabloaugusto.atlassian.net/browse/DOT-71)
- a issue dona deste pack e
  [`DOT-205`](https://pabloaugusto.atlassian.net/browse/DOT-205)

## Fronteiras

- este pack nao autoriza transformar Markdown em enforcement
- [`AGENTS.md`](../../../../AGENTS.md), [`docs/`](../../../../docs/) e
  [`config/ai/`](../../../../config/ai/) nao devem competir com a nova
  camada; eles devem apontar para ela e permanecer em paridade
- `fallback` nao deve nascer como arquivo tematico principal neste primeiro
  corte; ele deve virar secao obrigatoria dentro de cada tema relevante
- a migracao deve acontecer por ondas pequenas, com validacao real e sem
  quebrar startup, Jira, worklog, docs ou hooks

## Dependencias e ordem segura

- prerequisite packs: nenhum
- preflight packs:
  - [`startup-alignment`](../startup-alignment/prompt.md)
  - [`documentation-layer-governance`](../documentation-layer-governance/prompt.md)
- este pack deve respeitar a separacao entre `startup`, `PEA`, `enforcement`
  e `documentacao derivada`

## Arquivos vivos relacionados

- [`AGENTS.md`](../../../../AGENTS.md)
- [`LICOES-APRENDIDAS.md`](../../../../LICOES-APRENDIDAS.md)
- [`docs/AI-STARTUP-GOVERNANCE-MANIFEST.md`](../../../../docs/AI-STARTUP-GOVERNANCE-MANIFEST.md)
- [`docs/AI-STARTUP-AND-RESTART.md`](../../../../docs/AI-STARTUP-AND-RESTART.md)
- [`docs/AI-DELEGATION-FLOW.md`](../../../../docs/AI-DELEGATION-FLOW.md)
- [`docs/git-conventions.md`](../../../../docs/git-conventions.md)
- [`docs/ai-operating-model.md`](../../../../docs/ai-operating-model.md)
- [`Taskfile.yml`](../../../../Taskfile.yml)
- [`config/ai/contracts.yaml`](../../../../config/ai/contracts.yaml)
- [`config/ai/agent-operations.yaml`](../../../../config/ai/agent-operations.yaml)
- [`config/ai/jira-model.yaml`](../../../../config/ai/jira-model.yaml)
- [`scripts/validate-ai-assets.py`](../../../../scripts/validate-ai-assets.py)
- [`scripts/ai_session_startup_lib.py`](../../../../scripts/ai_session_startup_lib.py)

## Resultado esperado

- [`.agents/rules/`](../../../rules/) vira a fonte canonica normativa por tema
- [`AGENTS.md`](../../../../AGENTS.md) fica mais curto e mais claro
- `docs` passam a ser consumo humano e derivacao, nao a origem primaria da
  regra
- startup, agentes e subagentes passam a carregar a nova camada centralizada
- validadores e testes passam a proteger a paridade dessa arquitetura
