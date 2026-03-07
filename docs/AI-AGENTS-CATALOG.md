# AI Agents Catalog

Catalogo humano dos papeis permanentes de IA deste repo.

## Gates obrigatorios

- `repo-governance-authority`: sempre
- `execution-worklog-governance-owner`: sempre
- `architecture-modernization-authority`: sempre, em paralelo
- `critical-integrations-guardian`: obrigatorio quando a mudanca tocar bootstrap, auth, secrets, CI, CLI, sync ou ambiente
- `lessons-governance-curator`: obrigatorio em fechamento de worklog, retroativos e mudancas de governanca de continuidade

## Catalogo

| Papel | Cartao | Agente declarativo | Skill principal | Quando entra |
| --- | --- | --- | --- | --- |
| Bootstrap Operador | [`.agents/cards/bootstrap-operador.md`](../.agents/cards/bootstrap-operador.md) | `bootstrap-operator` | `$dotfiles-bootstrap` | bootstrap, relink, config e links |
| Curador Repo | [`.agents/cards/curador-repo.md`](../.agents/cards/curador-repo.md) | `repo-governance-authority` | `$dotfiles-repo-governance` | contratos, naming, docs, IA e governanca |
| Governador Continuidade WIP | [`.agents/cards/governador-continuidade-wip.md`](../.agents/cards/governador-continuidade-wip.md) | `execution-worklog-governance-owner` | `$wip-continuity-governance` | worklog, roadmap, doing/done e fechamento |
| Engenheiro Qualidade | [`.agents/cards/engenheiro-qualidade.md`](../.agents/cards/engenheiro-qualidade.md) | suporte ao `repo-governance-authority` | `$dotfiles-test-harness` | testes, CI, harnesses e quality gates |
| Arquiteto Modernizacao | [`.agents/cards/arquiteto-modernizacao.md`](../.agents/cards/arquiteto-modernizacao.md) | `architecture-modernization-authority` | `$dotfiles-architecture-modernization` | gate paralelo de arquitetura, simplificacao, performance e monitoramento continuo de WIP/backlog |
| Guardiao Integracoes Criticas | [`.agents/cards/guardiao-integracoes-criticas.md`](../.agents/cards/guardiao-integracoes-criticas.md) | `critical-integrations-guardian` | `$dotfiles-critical-integrations` | auth, secrets, tooling critica, bootstrap, sync e CI |
| Curador Licoes Aprendidas | [`.agents/cards/curador-licoes-aprendidas.md`](../.agents/cards/curador-licoes-aprendidas.md) | `lessons-governance-curator` | `$dotfiles-lessons-governance` | lessons, retroativos e revisoes de rodada |
| Orquestrador Delegacao | [`.agents/cards/orquestrador-delegacao.md`](../.agents/cards/orquestrador-delegacao.md) | `orchestrator` | `$task-routing-and-decomposition` | intake, roteamento, decomposicao e delegacao |
