# Governador Continuidade WIP

## Objetivo

Garantir que o trabalho incremental de IA tenha rastreabilidade, retomada segura e fechamento correto antes da entrega final.

## Quando usar

- retomada de tarefa interrompida
- mudanca de contexto durante uma implementacao longa
- necessidade de registrar progresso incremental
- fechamento de branch, PR ou entrega com risco de pendencia esquecida

## Skill principal

- `$wip-continuity-governance`

## Entradas

- mensagem acionavel do usuario
- estado atual de `docs/AI-WIP-TRACKER.md`
- branch atual e contexto da demanda

## Saidas

- tracker atualizado
- decisao explicita sobre pendencias
- status claro de `Doing`, `Done` e log incremental

## Fluxo

1. Ler `docs/AI-WIP-TRACKER.md`.
2. Rodar `task ai:worklog:check`.
3. Se houver pendencia, resolver com `concluir_primeiro` ou `roadmap_pendente`.
4. Registrar ou atualizar a tarefa atual.
5. Encerrar com `task ai:worklog:done`.
6. Validar `task ai:worklog:close:gate`.

## Guardrails

- Nao encerrar trabalho com item aberto em `Doing`.
- Nao ocultar pendencia fora do tracker.
- Nao usar o roadmap como descarte silencioso; registrar sugestao e contexto.

## Criterios de conclusao

- tracker consistente
- nenhuma pendencia esquecida
- fechamento validado pelo close gate
