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
- estado atual de [`../../docs/AI-WIP-TRACKER.md`](../../docs/AI-WIP-TRACKER.md)
- estado atual de [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md)
- estado atual de [`../../ROADMAP.md`](../../ROADMAP.md) quando houver pendencias adiadas
- branch atual e contexto da demanda

## Saidas

- tracker atualizado
- decisao explicita sobre pendencias
- status claro de `Doing`, `Done` e log incremental

## Fluxo

1. Ler [`../../docs/AI-WIP-TRACKER.md`](../../docs/AI-WIP-TRACKER.md).
2. Rodar `task ai:worklog:check`.
3. Se houver pendencia, resolver com `concluir_primeiro` ou `roadmap_pendente`.
   `concluir_primeiro` cobre concluir o WIP atual ou puxar apenas o work item
   minimo que o destrava diretamente.
4. Garantir que `roadmap_pendente` escreva em [`../../ROADMAP.md`](../../ROADMAP.md) e [`../../docs/ROADMAP-DECISIONS.md`](../../docs/ROADMAP-DECISIONS.md).
5. Registrar ou atualizar a tarefa atual.
6. Manter o item em `Doing` enquanto ainda houver execucao relevante em curso.
7. Antes do `done`, revisar [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md) e decidir `capturada` ou `sem_nova_licao`.
8. Encerrar com `task ai:worklog:done` apenas imediatamente antes da resposta final.
9. Se a rodada terminou e a worktree continuar dirty, exigir commit checkpoint antes de novo escopo.
10. Validar `task ai:lessons:check` e `task ai:worklog:close:gate`.

## Guardrails

- Nao encerrar trabalho com item aberto em `Doing`.
- Nao ocultar pendencia fora do tracker.
- Nao usar o roadmap como descarte silencioso; registrar sugestao e contexto.
- Nao usar `concluir_primeiro` para puxar demanda nova sem relacao direta com o
  WIP ativo.
- Nao permitir drift entre tracker, roadmap e decisions log.
- Nao permitir item em `Done` sem revisao correspondente em [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md).
- Nao fechar `Doing` cedo demais so para "limpar" o tracker.
- Nao permitir nova rodada com worktree suja quando nao houver item ativo em `Doing`.

## Validacao recomendada

- `task ai:worklog:check`
- `task ai:worklog:branch:check`
- `task ai:lessons:check`
- `task ai:worklog:close:gate`

## Criterios de conclusao

- tracker consistente
- nenhuma pendencia esquecida
- lessons revisadas
- fechamento validado pelo close gate
