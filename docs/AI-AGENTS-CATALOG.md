# AI Agents Catalog

Catalogo humano dos papeis permanentes de IA deste repo.

## Gates obrigatorios

- `repo-governance-authority`: sempre
- `execution-worklog-governance-owner`: sempre
- `architecture-modernization-authority`: sempre, em paralelo
- `critical-integrations-guardian`: obrigatorio quando a mudanca tocar bootstrap, auth, secrets, CI, CLI, sync ou ambiente
- `secrets-rotation-governor`: obrigatorio quando a mudanca tocar rotacao, backup, expiracao, revogacao ou inventario de credenciais/chaves
- `lessons-governance-curator`: obrigatorio em fechamento de worklog, retroativos e mudancas de governanca de continuidade
- `pascoalete`: obrigatorio em modo consultivo quando a mudanca tocar texto, comentario, documentacao, configuracao textual ou identificadores legiveis
- `python-reviewer`, `powershell-reviewer` e `automation-reviewer`: obrigatorios quando a mudanca tocar a familia de arquivo correspondente

## Catalogo

| Papel | Cartao | Agente declarativo | Skill principal | Quando entra |
| --- | --- | --- | --- | --- |
| Bootstrap Operador | [`.agents/cards/bootstrap-operador.md`](../.agents/cards/bootstrap-operador.md) | `bootstrap-operator` | `$dotfiles-bootstrap` | bootstrap, relink, config e links |
| Curador Repo | [`.agents/cards/curador-repo.md`](../.agents/cards/curador-repo.md) | `repo-governance-authority` | `$dotfiles-repo-governance` | contratos, naming, docs, IA, governanca e higiene de linkagem interna |
| Governador Continuidade WIP | [`.agents/cards/governador-continuidade-wip.md`](../.agents/cards/governador-continuidade-wip.md) | `execution-worklog-governance-owner` | `$wip-continuity-governance` | worklog, roadmap, doing/done e fechamento |
| Engenheiro Qualidade | [`.agents/cards/engenheiro-qualidade.md`](../.agents/cards/engenheiro-qualidade.md) | suporte ao `repo-governance-authority` | `$dotfiles-test-harness` | testes, CI, harnesses e quality gates |
| Arquiteto Modernizacao | [`.agents/cards/arquiteto-modernizacao.md`](../.agents/cards/arquiteto-modernizacao.md) | `architecture-modernization-authority` | `$dotfiles-architecture-modernization` | gate paralelo de arquitetura, simplificacao, performance e monitoramento continuo de WIP/backlog |
| Guardiao Integracoes Criticas | [`.agents/cards/guardiao-integracoes-criticas.md`](../.agents/cards/guardiao-integracoes-criticas.md) | `critical-integrations-guardian` | `$dotfiles-critical-integrations` | auth, secrets, tooling critica, bootstrap, sync e CI |
| Guardiao Rotacao Secrets | [`.agents/cards/guardiao-rotacao-secrets.md`](../.agents/cards/guardiao-rotacao-secrets.md) | `secrets-rotation-governor` | `$dotfiles-secrets-rotation` | rotacao segura de tokens, chaves SSH, refs, `sops+age` e continuidade de acesso |
| Pascoalete | [`.agents/cards/pascoalete.md`](../.agents/cards/pascoalete.md) | `pascoalete` | `$dotfiles-orthography-review` | ortografia tecnica, higiene vocabular, curadoria de `cspell` e pendencia consultiva quando houver falha textual nao corrigida |
| Revisor Python | [`.agents/cards/revisor-python.md`](../.agents/cards/revisor-python.md) | `python-reviewer` | `$dotfiles-python-review` | scripts Python, hooks Python, tipagem, lint e testes |
| Revisor PowerShell | [`.agents/cards/revisor-powershell.md`](../.agents/cards/revisor-powershell.md) | `powershell-reviewer` | `$dotfiles-powershell-review` | bootstrap e scripts `.ps1` do host Windows |
| Revisor Automacao | [`.agents/cards/revisor-automacao.md`](../.agents/cards/revisor-automacao.md) | `automation-reviewer` | `$dotfiles-automation-review` | shell, workflows, Taskfile, Docker e CI/CD |
| Curador Licoes Aprendidas | [`.agents/cards/curador-licoes-aprendidas.md`](../.agents/cards/curador-licoes-aprendidas.md) | `lessons-governance-curator` | `$dotfiles-lessons-governance` | lessons, retroativos e revisoes de rodada |
| Orquestrador Delegacao | [`.agents/cards/orquestrador-delegacao.md`](../.agents/cards/orquestrador-delegacao.md) | `orchestrator` | `$task-routing-and-decomposition` | intake, roteamento, decomposicao e delegacao |
