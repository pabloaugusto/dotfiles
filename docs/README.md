# Docs Index

Mapa das documentacoes versionadas do projeto e ordem recomendada de leitura.

## Comece por aqui

1. [`README.md`](README.md)
2. [`CONTEXT.md`](CONTEXT.md)
3. [`bootstrap/README.md`](bootstrap/README.md)
4. [`docs/test-strategy.md`](docs/test-strategy.md)
5. [`docs/ai-operating-model.md`](docs/ai-operating-model.md)
6. [`SECURITY.md`](SECURITY.md)

## Operacao do ambiente e bootstrap

- [`docs/bootstrap-flow.md`](docs/bootstrap-flow.md): fluxograma detalhado do bootstrap Windows, WSL,
  OneDrive e gates.
- [`docs/checkenv.md`](docs/checkenv.md): contrato e checklist do `checkEnv`.
- [`docs/config-reference.md`](docs/config-reference.md): referencia comentada do YAML de bootstrap.
- [`docs/onedrive.md`](docs/onedrive.md): layout, migracao e troubleshooting do OneDrive.
- [`docs/secrets-and-auth.md`](docs/secrets-and-auth.md): modelo de segredos, auth e runtime cifrado.
- [`docs/reference/secrets-rotation-architecture.md`](reference/secrets-rotation-architecture.md): arquitetura e trilha canonica de rotacao de secrets.
- [`docs/user-home-structure.md`](docs/user-home-structure.md): layout esperado do `HOME` apos bootstrap.
- [`bootstrap/README.md`](bootstrap/README.md): guia operacional textual do bootstrap.

## Qualidade, testes e CI/CD

- [`docs/test-strategy.md`](docs/test-strategy.md): arquitetura de testes do repo.
- [`docs/TASKS.md`](docs/TASKS.md): catalogo das tasks canonicas mais importantes.
- [`docs/WORKFLOWS.md`](docs/WORKFLOWS.md): catalogo dos workflows ativos e suas tasks.
- [`pyproject.toml`](pyproject.toml): contrato Python da camada de qualidade e da automacao
  auxiliar do repo.
- [`config/tooling.releases.yaml`](config/tooling.releases.yaml): pinagem declarativa de ferramentas externas
  como `actionlint` e `gitleaks`.
- [`tests/README.md`](tests/README.md): suites, harnesses e comandos de teste.
- [`docs/repo-audit.md`](docs/repo-audit.md): snapshot atual de riscos, achados resolvidos e backlog
  tecnico de manutencao.

## Governanca e IA

- [`docs/ai-operating-model.md`](docs/ai-operating-model.md): contrato da camada de IA.
- [`config/ai/platforms.yaml`](../config/ai/platforms.yaml): configuracao dev-time das plataformas externas da camada de IA.
- [`config/ai/platforms.local.yaml.tpl`](../config/ai/platforms.local.yaml.tpl): template do overlay local ignorado no Git para refs reais de plataformas.
- [`config/ai/agents.yaml`](../config/ai/agents.yaml): optionalidade e papeis operacionais do modelo multiagente.
- [`config/ai/agent-operations.yaml`](../config/ai/agent-operations.yaml): contrato operacional por papel para `Jira` e `Confluence`, com passo a passo, handoffs e evidencia obrigatoria.
- [`config/ai/contracts.yaml`](../config/ai/contracts.yaml): contratos Jira + Confluence do fluxo-alvo.
- [`config/ai/sync-targets.yaml`](../config/ai/sync-targets.yaml): manifest declarativo da fundacao de sync, com classificacao de artefatos, outbox local duravel e destinos remotos elegiveis.
- [`config/ai/confluence-model.yaml`](../config/ai/confluence-model.yaml): arquitetura de informacao alvo do space, com governanca `repo-first -> Confluence`, ownership de `source of truth` no `ai-documentation-manager` e publication no `ai-documentation-sync`.
- [`docs/ai-sync-foundation.md`](ai-sync-foundation.md): arquitetura-base do fluxo `repo declarativo -> outbox local duravel -> fonte perene remota`.
- [`vendor/atlassian/README.md`](../vendor/atlassian/README.md): specs OpenAPI vendorizados da Atlassian para codegen e auditoria.
- [`docs/atlassian-ia/README.md`](atlassian-ia/README.md): trilha versionada de contexto,
  pareceres, planos e artefatos da migracao Jira + Confluence.
- [`AI-FALLBACK-OPERATIONS.md`](AI-FALLBACK-OPERATIONS.md): protocolo canonico dos modos
  `primary`, `degraded` e `recovery` entre `Jira` e trackers locais.
- [`AI-FALLBACK-LEDGER.md`](AI-FALLBACK-LEDGER.md): ledger canonico dos
  registros ativos e resolvidos de fallback contingencial.
- [`AI-WIP-TRACKER.md`](AI-WIP-TRACKER.md): fallback contingencial local; o `Jira` e a fonte primaria do fluxo vivo.
- [`AI-SCRUM-MASTER-LEDGER.md`](AI-SCRUM-MASTER-LEDGER.md): inconformidades e
  **cerimonias** rastreadas pelo **Scrum Master**.
- [`../ROADMAP.md`](../ROADMAP.md): backlog priorizado e sugestoes.
- [`ROADMAP-DECISIONS.md`](ROADMAP-DECISIONS.md): historico das decisoes do roadmap.
- [`docs/AI-AGENTS-CATALOG.md`](docs/AI-AGENTS-CATALOG.md): catalogo dos agentes do repo.
- [`docs/AI-SKILLS-CATALOG.md`](docs/AI-SKILLS-CATALOG.md): catalogo das skills.
- [`docs/AI-DELEGATION-FLOW.md`](docs/AI-DELEGATION-FLOW.md): fluxo de intake, roteamento e delegacao.
- [`docs/AI-GOVERNANCE-AND-REGRESSION.md`](docs/AI-GOVERNANCE-AND-REGRESSION.md): regressao e governanca da camada de IA.
- [`.agents/prompts/README.md`](../.agents/prompts/README.md): contrato estrutural dos prompt packs versionados.
- [`.agents/prompts/CATALOG.md`](../.agents/prompts/CATALOG.md): catalogo dos packs formais e legados.
- [`docs/AI-BACKLOG-LIVE-AUDIT.md`](docs/AI-BACKLOG-LIVE-AUDIT.md): matriz auditavel do backlog vivo versus `Jira`, incluindo backfill de owners oficiais.
- [`docs/AI-DONE-ISSUES-AUDIT.md`](docs/AI-DONE-ISSUES-AUDIT.md): baseline versionada da auditoria integral das issues em **Done**, com checklist por onda, veredicto formal e remediacoes de paridade terminal.
- [`docs/AI-PAUSED-ISSUES-AUDIT.md`](docs/AI-PAUSED-ISSUES-AUDIT.md): classificacao factual das issues em **Paused**, com evidencias, veredicto e acao recomendada por item.
- [`docs/AI-RETROSPECTIVE-BACKFILL-AUDIT.md`](docs/AI-RETROSPECTIVE-BACKFILL-AUDIT.md): inventario versionado das branches encerradas, com cobertura existente, backfill fiel e excecoes documentadas de retrospectiva.
- [`docs/AI-SOURCE-AUDIT.md`](docs/AI-SOURCE-AUDIT.md): auditoria estrutural das fontes cross-repo.
- [`docs/git-conventions.md`](docs/git-conventions.md): convencoes de branch, commit e PR.

## Referencias e notas

- [`docs/reference/powershell/`](docs/reference/powershell/): referencias tecnicas auxiliares.
- [`docs/notes/`](docs/notes/): notas de uso pontual que nao sao contratos principais.

## Regra de manutencao

- README raiz = catalogo funcional do projeto.
- [`docs/TASKS.md`](docs/TASKS.md) e [`docs/WORKFLOWS.md`](docs/WORKFLOWS.md) devem refletir a automacao real.
- [`bootstrap/README.md`](bootstrap/README.md) e [`tests/README.md`](tests/README.md) devem refletir os fluxos correntes,
  nao estados "iniciais".
