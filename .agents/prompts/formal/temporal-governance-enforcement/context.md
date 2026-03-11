# Contexto Do Pack

Este prompt pack existe para materializar uma trilha formal de implementacao
para governanca temporal, timezone, locale e regionalizacao sem depender do
nome do repositorio.

## Contexto especifico do projeto atual

- o projeto atual ja possui camada versionada de prompts formais em
  [`.agents/prompts/`](../../README.md)
- o projeto atual ja possui governanca versionada para startup, continuidade,
  reviews, validadores e contracts
- as correcoes de data, hora, locale e idioma ja apareceram como prioridade
  aceita no backlog vivo e nao devem ser tratadas como tema novo desconectado
- a implementacao deste pack deve reutilizar a trilha oficial ja existente em
  vez de abrir uma governanca paralela

## Fronteiras

- este pack nao autoriza operar fora dos contratos vivos do projeto
- o objetivo e reduzir drift temporal com backend real, nao criar um conjunto
  novo de regras soltas
- a politica correta deve subir para startup, restart, reviewers, validators,
  tests, docs, prompts e closeout
- quando houver superficies que precisem permanecer em `UTC`, a excecao deve
  ser explicita, rastreavel e semanticamente nomeada

## Arquivos vivos relacionados

- [`AGENTS.md`](../../../../AGENTS.md)
- [`LICOES-APRENDIDAS.md`](../../../../LICOES-APRENDIDAS.md)
- [`docs/ai-operating-model.md`](../../../../docs/ai-operating-model.md)
- [`docs/AI-STARTUP-AND-RESTART.md`](../../../../docs/AI-STARTUP-AND-RESTART.md)
- [`docs/AI-DELEGATION-FLOW.md`](../../../../docs/AI-DELEGATION-FLOW.md)
- [`docs/TASKS.md`](../../../../docs/TASKS.md)
- [`config/ai/contracts.yaml`](../../../../config/ai/contracts.yaml)
- [`config/ai/agent-operations.yaml`](../../../../config/ai/agent-operations.yaml)
- [`scripts/ai_session_startup_lib.py`](../../../../scripts/ai_session_startup_lib.py)
- [`scripts/validate-ai-assets.py`](../../../../scripts/validate-ai-assets.py)

## Resultado esperado

- a arvore [`.agents/prompts/`](../../README.md) passa a ter um pack formal,
  catalogado e reutilizavel para governanca temporal
- o pack pode ser executado sem citar o nome atual do repositorio
- a implementacao derivada dele deve descobrir o contexto real do projeto antes
  de editar, mas sem perder a aderencia aos contratos vivos da arvore atual
