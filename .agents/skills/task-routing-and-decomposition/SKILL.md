---
name: task-routing-and-decomposition
description: Roteamento declarativo, intake, decomposicao e delegacao de trabalho de IA para este repo de dotfiles. Use quando a tarefa pedir triagem, plano de delegacao, backlog tecnico, distribuicao de agentes ou verificacao de gates obrigatorios antes da implementacao.
---

# task-routing-and-decomposition

## Objetivo

Materializar intake, roteamento e delegacao com backend real e declarativo.

## Fluxo

1. Ler [`../../../docs/AI-WIP-TRACKER.md`](../../../docs/AI-WIP-TRACKER.md), [`../../../ROADMAP.md`](../../../ROADMAP.md) e [`docs/AI-DELEGATION-FLOW.md`](docs/AI-DELEGATION-FLOW.md).
2. Rodar preflight de pendencias antes de iniciar nova demanda.
3. Ler [`.agents/orchestration/capability-matrix.yaml`](.agents/orchestration/capability-matrix.yaml) e [`.agents/orchestration/routing-policy.yaml`](.agents/orchestration/routing-policy.yaml).
4. Gerar `TaskCard` e `DelegationPlan` a partir dos agentes, skills e gates declarativos.
5. Garantir que workflow, task e docs de catalogo continuem sincronizados.
6. Encaminhar backlog residual para o roadmap quando nao entrar na rodada atual.

## Regras

- O roteamento deve ser deterministico e rastreavel.
- Gatilhos obrigatorios de arquitetura, continuidade e integracoes criticas nao podem ser omitidos.
- Nao gerar plano de delegacao sem refletir o estado real de WIP e backlog.

## Entregas esperadas

- intake rastreavel
- roteamento deterministico
- plano de delegacao reproduzivel
- backlog tecnico ou followups quando houver gaps

## Validacao

- `task ai:chat:intake MESSAGE="exemplo" ROUTE=1 PENDING_ACTION=concluir_primeiro`
- `task ai:route INTENT="exemplo" PATHS="ROADMAP.md"`
- `task ai:delegate INTENT="exemplo" PATHS="AGENTS.md,docs/WORKFLOWS.md"`
- `task ai:eval:smoke`
- `task ci:workflow:sync:check`
- `task test:unit:python:windows`

## Referencias

- [`references/checklist.md`](references/checklist.md)
