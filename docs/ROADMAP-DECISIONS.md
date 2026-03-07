# Decisoes do Roadmap

Atualizado em: 2026-03-07 09:08 UTC
Ciclo ativo: 2026-Q1

Registro das decisoes humanas por ciclo e governanca de sugestoes.

## Registro de Sugestoes

Use status: `pendente`, `aceita`, `descartada`, `aplicar_depois`.

<!-- roadmap:suggestions:start -->
| ID | Descricao | Status | RM | Captura | Atualizacao |
| --- | --- | --- | --- | --- | --- |
| SG-20260307-090831 | Consolidar ou arquivar o legado historico versionado que nao e fonte canonica, incluindo bootstrap/bootstrap-ubuntu.original.sh, scripts experimentais e backups declaradamente n... | pendente |  | 2026-03-07 | 2026-03-07 |
| SG-20260307-041349-01 | Expandir datasets e cenarios de eval para bootstrap cross-platform, seguranca e risco operacional. | aceita |  | 2026-03-07 | 2026-03-07 |
| SG-20260307-041349 | Adicionar validadores dedicados de sincronismo entre workflows, tasks, docs, catalogos e ativos declarativos da IA. | aceita |  | 2026-03-07 | 2026-03-07 |
| SG-20260307-041348 | Importar chat-intake, route e delegate com backend real de roteamento declarativo para a camada canonica .agents. | aceita |  | 2026-03-07 | 2026-03-07 |
<!-- roadmap:suggestions:end -->

## Historico de Ciclos

<!-- roadmap:cycles:start -->
### Ciclo 2026-Q1 @ 2026-03-07 09:08 UTC

- Top sequencia recomendada: `RM-001, RM-002`
- Decisao final permanece humana.
- Acao de governanca: decidir pendencias antes de novo escopo amplo.
- Sugestoes pendentes no fechamento: `SG-20260307-090831`
<!-- roadmap:cycles:end -->

## Registro automatico

<!-- roadmap:autolog:start -->
- 2026-03-07 09:08 UTC | decisao=pending | horizonte=next | item=Consolidar ou arquivar o legado historico versionado que nao e fonte canonica, incluindo bootstrap/bootstrap-ubuntu.original.sh, scripts experimentais e backups declaradamente n... | notas=Reduzir ruido conceitual, diminuir superficie de manutencao e deixar explicita a fronteira entre referencia historica e runtime canonico.
- 2026-03-07 08:10 UTC | decisao=accepted | horizonte=now | item=Expandir datasets e cenarios de eval para bootstrap cross-platform, seguranca e risco operacional. | notas=entregue parcialmente nesta rodada com ai:eval:smoke e ampliacao inicial dos datasets; bootstrap full permanece evolucao futura
- 2026-03-07 08:10 UTC | decisao=accepted | horizonte=now | item=Adicionar validadores dedicados de sincronismo entre workflows, tasks, docs, catalogos e ativos declarativos da IA. | notas=entregue nesta rodada com validate_workflow_task_sync.py e catalogos TASKS/WORKFLOWS
- 2026-03-07 08:10 UTC | decisao=accepted | horizonte=now | item=Importar chat-intake, route e delegate com backend real de roteamento declarativo para a camada canonica .agents. | notas=entregue nesta rodada com backend Python, orchestrator e smoke eval
- 2026-03-07 04:13 UTC | decisao=pending | horizonte=later | item=Expandir datasets e cenarios de eval para bootstrap cross-platform, seguranca e risco operacional. | notas=gaps remanescentes de evals e regression suite
- 2026-03-07 04:13 UTC | decisao=pending | horizonte=next | item=Adicionar validadores dedicados de sincronismo entre workflows, tasks, docs, catalogos e ativos declarativos da IA. | notas=gaps remanescentes inspirados em iageny; workflow-task-doc sync
- 2026-03-07 04:13 UTC | decisao=pending | horizonte=next | item=Importar chat-intake, route e delegate com backend real de roteamento declarativo para a camada canonica .agents. | notas=gaps remanescentes da auditoria cross-repo; arquitetura/roteamento
- (sem itens)
<!-- roadmap:autolog:end -->
