# AI WIP Tracker

Atualizado em: 2026-03-06 00:00 UTC

Fonte de verdade operacional para continuidade de tarefas dos agentes de IA.

## Regras operacionais

- Toda solicitacao acionavel deve passar por preflight de pendencias.
- Se houver itens em `Doing`, perguntar ao usuario:
  - concluir pendencias antes (`concluir_primeiro`), ou
  - manter pendencias e registrar no roadmap (`roadmap_pendente`).
- Durante execucao, registrar progresso incremental no ledger.
- Ultimo passo obrigatorio antes de encerrar demanda: mover item ativo de
  `Doing` para `Done` e remover do log incremental as demandas finalizadas.

## Doing

<!-- ai-worklog:doing:start -->
| ID | Tarefa | Branch | Responsavel | Inicio UTC | Ultima atualizacao UTC | Proximo passo | Bloqueios |
| --- | --- | --- | --- | --- | --- | --- | --- |
| (sem itens) | - | - | - | - | - | - | - |
<!-- ai-worklog:doing:end -->

## Done

<!-- ai-worklog:done:start -->
| ID | Tarefa | Branch | Responsavel | Inicio UTC | Concluido UTC | Resultado |
| --- | --- | --- | --- | --- | --- | --- |
| (sem itens) | - | - | - | - | - | - |
<!-- ai-worklog:done:end -->

## Log incremental - Tarefas nao finalizadas ainda

<!-- ai-worklog:log:start -->
| Data/Hora UTC | ID | Status | Resumo | Proximo passo | Bloqueios | Contexto | Notas |
| --- | --- | --- | --- | --- | --- | --- | --- |
| (sem itens) | - | - | - | - | - | - | - |
<!-- ai-worklog:log:end -->
