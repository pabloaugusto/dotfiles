# Roadmap do Repositorio

Atualizado em: 2026-03-07 09:08 UTC
Ciclo ativo: 2026-Q1

Planejamento incremental para qualidade, testes, bootstrap e governanca do repo.

## Guardrails

- Toda sugestao aceita deve gerar rastreabilidade no mesmo ciclo.
- Pendencias mantidas devem aparecer em `docs/AI-WIP-TRACKER.md` e no roadmap.
- Priorizacao automatica ajuda a ordenar, mas a decisao final continua humana.

## Backlog Mestre

Edite apenas a tabela entre os marcadores abaixo.

<!-- roadmap:backlog:start -->
| ID | Iniciativa | R | I | C | E | BV | TC | RR | JS | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RM-001 | Harness Linux para bootstrap e relink | 400 | 2.6 | 0.8 | 8 | 8 | 7 | 6 | 5 | in_progress |
| RM-002 | Harness Windows real em CI | 380 | 2.8 | 0.7 | 13 | 9 | 8 | 7 | 8 | in_progress |
| RM-003 | Governanca de worklog e roadmap com enforcement | 320 | 2.4 | 0.85 | 5 | 9 | 7 | 8 | 4 | done |
<!-- roadmap:backlog:end -->

## Priorizacao Automatica

Atualizada por `task ai:roadmap:refresh`.

<!-- roadmap:priority:start -->
Atualizado em: `2026-03-07 09:08 UTC`

### Ranking RICE

| Rank | ID | Status | RICE |
| --- | --- | --- | --- |
| 1 | RM-001 | in_progress | 104.00 |
| 2 | RM-002 | in_progress | 57.29 |

### Ranking WSJF

| Rank | ID | Status | WSJF |
| --- | --- | --- | --- |
| 1 | RM-001 | in_progress | 4.20 |
| 2 | RM-002 | in_progress | 3.00 |

### Referencia de IDs

- `RM-001`: Harness Linux para bootstrap e relink
- `RM-002`: Harness Windows real em CI

### Sequencia Recomendada

1. `RM-001` - Harness Linux para bootstrap e relink
2. `RM-002` - Harness Windows real em CI

### Governanca de Sugestoes

Ha sugestoes pendentes sem decisao final neste ciclo.
Pergunta obrigatoria ao usuario:
- descartar as sugestoes pendentes, ou
- manter no roadmap para aplicar depois.
IDs pendentes: `SG-20260307-090831`
<!-- roadmap:priority:end -->

## Horizonte de Entrega

### Now

<!-- roadmap:now:start -->
- Expandir datasets e cenarios de eval para bootstrap cross-platform, seguranca e risco operacional. | notas=entregue parcialmente nesta rodada com ai:eval:smoke e ampliacao inicial dos datasets; bootstrap full permanece evolucao futura
- Adicionar validadores dedicados de sincronismo entre workflows, tasks, docs, catalogos e ativos declarativos da IA. | notas=entregue nesta rodada com validate_workflow_task_sync.py e catalogos TASKS/WORKFLOWS
- Importar chat-intake, route e delegate com backend real de roteamento declarativo para a camada canonica .agents. | notas=entregue nesta rodada com backend Python, orchestrator e smoke eval
- RM-001 - expandir o harness Linux de relink para bootstrap full com stubs de auth e secrets
- RM-002 - estabilizar o harness Windows no runner hospedado e ampliar cobertura alem de relink
<!-- roadmap:now:end -->

### Next

<!-- roadmap:next:start -->
- (sem itens)
<!-- roadmap:next:end -->

### Later

<!-- roadmap:later:start -->
- (sem itens)
<!-- roadmap:later:end -->

## Sugestoes pendentes de decisao

<!-- roadmap:pending:start -->
- Consolidar ou arquivar o legado historico versionado que nao e fonte canonica, incluindo bootstrap/bootstrap-ubuntu.original.sh, scripts experimentais e backups declaradamente n... | notas=Reduzir ruido conceitual, diminuir superficie de manutencao e deixar explicita a fronteira entre referencia historica e runtime canonico.
<!-- roadmap:pending:end -->

## Riscos e bloqueios

- Bootstrap full ainda depende de 1Password, gh, sops e layout real de OneDrive; faltam stubs e fixtures para PR CI barato.
- Harness Windows cobre relink isolado em perfil temporario; bootstrap completo com auth real segue fora deste ciclo.
