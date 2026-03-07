---
name: wip-continuity-governance
description: Manter continuidade operacional de tarefas IA via tracker Doing/Done, com preflight obrigatorio de pendencias e registro incremental de progresso.
---

# WIP Continuity Governance

## Objetivo

Evitar perda de contexto, tarefas esquecidas e encerramento prematuro de demandas com trabalho de IA ainda aberto.

## Fluxo

1. Ler `docs/AI-WIP-TRACKER.md`.
2. Rodar `task ai:worklog:check` antes de iniciar execucao relevante.
3. Se houver pendencia, exigir decisao explicita: `concluir_primeiro` ou `roadmap_pendente`.
4. Registrar tarefa em `Doing` com `task ai:worklog:start` ou atualizar com `task ai:worklog:update`.
5. Fechar a tarefa com `task ai:worklog:done` e validar `task ai:worklog:close:gate`.

## Regras

- Nenhuma demanda acionavel deve ficar sem registro quando houver risco de interrupcao.
- `docs/AI-WIP-TRACKER.md` e a fonte de verdade do estado incremental.
- `docs/ROADMAP-DECISIONS.md` recebe itens adiados por `roadmap_pendente`.
- Nao encerrar branch, PR ou entrega com item aberto em `Doing`.

## Validacao minima

- `task ai:worklog:check`
- `task ai:worklog:branch:check`
- `task ai:worklog:close:gate`

## Referencias

- `references/checklist.md`
