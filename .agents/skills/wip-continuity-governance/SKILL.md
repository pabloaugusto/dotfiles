---
name: wip-continuity-governance
description: Manter continuidade operacional de tarefas IA via tracker Doing/Done, com preflight obrigatorio de pendencias e registro incremental de progresso.
---

# WIP Continuity Governance

## Objetivo

Evitar perda de contexto, tarefas esquecidas e encerramento prematuro de demandas com trabalho de IA ainda aberto.

## Fluxo

1. Ler [`docs/AI-WIP-TRACKER.md`](docs/AI-WIP-TRACKER.md), [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md) e, quando houver pendencias adiadas, [`docs/ROADMAP.md`](docs/ROADMAP.md) e [`docs/ROADMAP-DECISIONS.md`](docs/ROADMAP-DECISIONS.md).
2. Rodar `task ai:worklog:check` antes de iniciar execucao relevante.
3. Se houver pendencia, exigir decisao explicita: `concluir_primeiro` ou `roadmap_pendente`.
4. Registrar tarefa em `Doing` com `task ai:worklog:start` ou atualizar com `task ai:worklog:update`.
5. Manter a tarefa em `Doing` durante toda a execucao relevante.
6. Antes do `done`, revisar explicitamente [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md) e registrar `capturada` ou `sem_nova_licao`.
7. Fechar a tarefa com `task ai:worklog:done` imediatamente antes da resposta final e validar `task ai:lessons:check` e `task ai:worklog:close:gate`.
8. Antes de iniciar nova rodada, garantir commit checkpoint se a worktree permanecer dirty sem `Doing` ativo.

## Regras

- Nenhuma demanda acionavel deve ficar sem registro quando houver risco de interrupcao.
- [`docs/AI-WIP-TRACKER.md`](docs/AI-WIP-TRACKER.md) e a fonte de verdade do estado incremental.
- [`docs/ROADMAP.md`](docs/ROADMAP.md) e [`docs/ROADMAP-DECISIONS.md`](docs/ROADMAP-DECISIONS.md) recebem itens adiados por `roadmap_pendente`.
- nenhum item em `Done` pode ficar sem revisao em [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md).
- Nao encerrar branch, PR ou entrega com item aberto em `Doing`.
- Nao mover item para `Done` antes do ultimo passo tecnico da rodada.
- Nao iniciar nova rodada com worktree suja sem checkpoint commit quando nao houver `Doing` ativo.

## Entregas esperadas

- continuidade operacional rastreavel
- pendencias resolvidas ou encaminhadas formalmente
- fechamento sem drift entre tracker, roadmap e lessons

## Validacao

- `task ai:worklog:check`
- `task ai:lessons:check`
- `task ai:worklog:branch:check`
- `task ai:worklog:close:gate`

## Referencias

- [`references/checklist.md`](references/checklist.md)
