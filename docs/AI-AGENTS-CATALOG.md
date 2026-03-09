# AI Agents Catalog

Catalogo humano dos papeis permanentes de IA deste repo.

## Gates obrigatorios

- `repo-governance-authority`: sempre
- `execution-worklog-governance-owner`: sempre
- `ai-scrum-master`: sempre, como gate global de **board**, **WIP**,
  comunicacao, ownership e **cerimonias**
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

## Malha operacional Jira e Confluence

| Papel | Cartao | Agente declarativo | Skill principal | Quando entra |
| --- | --- | --- | --- | --- |
| AI Product Owner | [`.agents/cards/ai-product-owner.md`](../.agents/cards/ai-product-owner.md) | `ai-product-owner` | `$task-routing-and-decomposition` | intake, backlog, prioridade, refinement, ready e timeline |
| Scrum Master | [`.agents/cards/ai-scrum-master.md`](../.agents/cards/ai-scrum-master.md) | `ai-scrum-master` | `$wip-continuity-governance` | gate global de **board**, **WIP**, ownership, comunicacao, conformidade de agentes e **cerimonias** |
| AI Engineering Architect | [`.agents/cards/ai-engineering-architect.md`](../.agents/cards/ai-engineering-architect.md) | `ai-engineering-architect` | `$dotfiles-architecture-modernization` | discovery tecnico, ADR, enriquecimento de backlog e refinement |
| AI Engineering Manager | [`.agents/cards/ai-engineering-manager.md`](../.agents/cards/ai-engineering-manager.md) | `ai-engineering-manager` | `$wip-continuity-governance` | capacidade, gargalos, pausas, riscos, bloqueios e escalacoes |
| AI Tech Lead | [`.agents/cards/ai-tech-lead.md`](../.agents/cards/ai-tech-lead.md) | `ai-tech-lead` | `$task-routing-and-decomposition` | decomposicao, handoff tecnico e coordenacao de execucao |
| AI Developer Python | [`.agents/cards/ai-developer-python.md`](../.agents/cards/ai-developer-python.md) | `ai-developer-python` | `$dotfiles-python-review` | implementacao Python e evidencias tecnicas |
| AI Developer PowerShell | [`.agents/cards/ai-developer-powershell.md`](../.agents/cards/ai-developer-powershell.md) | `ai-developer-powershell` | `$dotfiles-powershell-review` | implementacao PowerShell e automacao Windows |
| AI Developer Automation | [`.agents/cards/ai-developer-automation.md`](../.agents/cards/ai-developer-automation.md) | `ai-developer-automation` | `$dotfiles-automation-review` | shell, workflow, Docker, Taskfile e CI/CD |
| AI Developer Config Policy | [`.agents/cards/ai-developer-config-policy.md`](../.agents/cards/ai-developer-config-policy.md) | `ai-developer-config-policy` | `$dotfiles-repo-governance` | schemas, contracts, metadata e policies declarativas |
| AI QA | [`.agents/cards/ai-qa.md`](../.agents/cards/ai-qa.md) | `ai-qa` | `$dotfiles-test-harness` | testing, acceptance criteria e evidencias |
| AI Reviewer | [`.agents/cards/ai-reviewer.md`](../.agents/cards/ai-reviewer.md) | `ai-reviewer` | `$task-routing-and-decomposition` | consolidacao de review, risco transversal e paridade Jira x fluxo |
| AI Reviewer Python | [`.agents/cards/revisor-python.md`](../.agents/cards/revisor-python.md) | `ai-reviewer-python` | `$dotfiles-python-review` | review especializado de Python |
| AI Reviewer PowerShell | [`.agents/cards/revisor-powershell.md`](../.agents/cards/revisor-powershell.md) | `ai-reviewer-powershell` | `$dotfiles-powershell-review` | review especializado de PowerShell |
| AI Reviewer Automation | [`.agents/cards/revisor-automacao.md`](../.agents/cards/revisor-automacao.md) | `ai-reviewer-automation` | `$dotfiles-automation-review` | review especializado de automacao |
| AI Reviewer Config Policy | [`.agents/cards/revisor-config-policy.md`](../.agents/cards/revisor-config-policy.md) | `ai-reviewer-config-policy` | `$dotfiles-repo-governance` | review especializado de YAML, JSON, TOML, Markdown e schemas |
| AI DevOps | [`.agents/cards/ai-devops.md`](../.agents/cards/ai-devops.md) | `ai-devops` | `$dotfiles-critical-integrations` | pipelines, releases, integracoes e infraestrutura de fluxo |
| AI Documentation Agent | [`.agents/cards/ai-documentation-agent.md`](../.agents/cards/ai-documentation-agent.md) | `ai-documentation-agent` | `$dotfiles-repo-governance` | sync Jira <-> Confluence, docs vivas e bundles auditaveis |
