# Atlassian IA

Trilha versionada para contexto, pareceres, planos e referencias da migracao da
camada de IA do repo para um modelo com Jira e Confluence como plataformas de
governanca.

## Objetivo

- preservar os contextos enviados pelo usuario sem depender de memoria implicita
- registrar pareceres e planos gerados ao longo da analise
- manter rastreabilidade local antes de qualquer cutover real para Atlassian

## Regras desta trilha

- cada contexto relevante deve ficar em arquivo proprio, com data no nome
- pareceres, planos e decisoes gerados pela IA tambem devem ser materializados aqui
- schemas, endpoints, rotinas, workflows e demais artefatos gerados para a
  trilha Atlassian devem nascer primeiro como artefatos versionados no repo
- esta pasta guarda rastreabilidade e estudo; ela nao substitui as fontes de
  verdade atuais do repo nem as futuras fontes oficiais em Jira/Confluence
- sempre que possivel, usar links explicitos para docs, tasks, scripts e fontes externas

## Arquivos atuais

- [`2026-03-07-blueprint-ai-product-owner-system.md`](2026-03-07-blueprint-ai-product-owner-system.md):
  blueprint base fornecido pelo usuario.
- [`2026-03-07-melhores-praticas-mercado.md`](2026-03-07-melhores-praticas-mercado.md):
  contexto adicional do usuario sobre praticas de mercado para IA + Jira +
  Confluence.
- [`2026-03-07-operacao-agentes-jira-confluence.md`](2026-03-07-operacao-agentes-jira-confluence.md):
  contexto adicional do usuario sobre operacao completa dos agentes nas
  ferramentas Atlassian.
- [`2026-03-07-modelo-operacional-completo-figma-seo.md`](2026-03-07-modelo-operacional-completo-figma-seo.md):
  extensao de escopo com Figma, UX/CRO, SEO, backlog bruto x refinado e
  politica de subtasks.
- [`2026-03-07-fundacao-dev-time-desacoplada.md`](2026-03-07-fundacao-dev-time-desacoplada.md):
  diretriz aprovada para tirar configs/secrets/contratos dev-time de
  [`df/`](../../df/) e [`bootstrap/`](../../bootstrap/), mantendo optionalidade
  por config e browser validation opcional via `Playwright`.
- [`2026-03-07-atlassian-product-discovery.md`](2026-03-07-atlassian-product-discovery.md):
  decisao de incorporar `Atlassian Product Discovery` como camada opcional de
  discovery upstream do `Jira`, preservando o `AI Product Owner` como promotor
  exclusivo das issues principais.
- [`2026-03-07-diagnostico-auth-e-acesso-atlassian.md`](2026-03-07-diagnostico-auth-e-acesso-atlassian.md):
  estado real do handshake Atlassian, incluindo gateway de service account,
  acesso operacional em `Jira core` e `Confluence v2` e gap atual na API de
  board do `Jira Software`.
- [`2026-03-07-atlassian-auth-scopes-and-permissions.md`](2026-03-07-atlassian-auth-scopes-and-permissions.md):
  inventario canonico de scopes, permissoes de principal, versoes de API por
  produto e checklist de rotacao futura.
- [`2026-03-07-jira-configuration-export.md`](2026-03-07-jira-configuration-export.md):
  export declarativo do projeto alvo no `Jira`, com delta atual, bloqueios
  administrativos confirmados por API e ordem de aplicacao.
- [`2026-03-07-atlassian-openapi-generation-strategy.md`](2026-03-07-atlassian-openapi-generation-strategy.md):
  estrategia aprovada para vendorizar specs OpenAPI oficiais da Atlassian e
  usar codegen reprodutivel no repo.
- [`2026-03-07-onepassword-batch-resolution.md`](2026-03-07-onepassword-batch-resolution.md):
  estrategia implementada para resolver refs `op://...` em lote com `op run`,
  manter cache em memoria por processo e reduzir risco de rate limit no cofre.
- [`2026-03-07-python-modular-architecture-research.md`](2026-03-07-python-modular-architecture-research.md):
  pesquisa e recomendacao para evoluir o piloto para um monolito modular com
  pacotes importaveis por dominio e extracao futura seletiva para microservicos.
- [`2026-03-08-analise-fronteira-app-runtime.md`](2026-03-08-analise-fronteira-app-runtime.md):
  diagnostico inicial sobre mover o runtime materializado para uma futura pasta
  [`/app`](../../), com recomendacao faseada de desacoplamento antes do move
  fisico.
- [`2026-03-08-playwright-atlassian-auth-bootstrap.md`](2026-03-08-playwright-atlassian-auth-bootstrap.md):
  contrato canonico do bootstrap humano inicial de autenticacao web via
  `Playwright`, com `storageState` local, reuso de sessao e evidencias visuais.
- [`2026-03-08-atlassian-agile-hub-inventory.md`](2026-03-08-atlassian-agile-hub-inventory.md):
  inventario versionado do crawl oficial do hub `Atlassian Agile`, com
  cobertura ampla do diretorio `/br/agile` e catalogo de URLs lidas.
- [`2026-03-08-manual-agilidade-control-plane.md`](2026-03-08-manual-agilidade-control-plane.md):
  manual agil consolidado do projeto, derivado do hub oficial da Atlassian e
  traduzido para o fluxo real `Jira + Confluence + repo`.
- [`2026-03-08-spike-cobertura-agentes-e-review-especializado.md`](2026-03-08-spike-cobertura-agentes-e-review-especializado.md):
  spike dedicada a cobertura de agentes, review especializado, qualidade de
  spikes e priorizacao continua do backlog pelo `PO`.
- [`2026-03-08-blocker-escalation-and-notifications.md`](2026-03-08-blocker-escalation-and-notifications.md):
  contrato vitalicio de escalacao de bloqueios, com notificacao do usuario por
  todos os canais disponiveis e trilha obrigatoria em `Jira` e `Confluence`.
- [`2026-03-08-github-for-atlassian-runbook.md`](2026-03-08-github-for-atlassian-runbook.md):
  runbook operacional da integracao oficial `GitHub for Atlassian`, com
  checklist de setup, convencoes obrigatorias, evidencias minimas e diagnostico
  rapido.
- [`2026-03-08-github-jira-confluence-traceability.md`](2026-03-08-github-jira-confluence-traceability.md):
  estrategia oficial para integrar `GitHub`, `Jira` e `Confluence` com
  rastreabilidade ponta a ponta de branches, commits, PRs, workflows,
  deployments, releases e referencias documentais.
- [`artifacts/onepassword-runtime-read-inventory.md`](artifacts/onepassword-runtime-read-inventory.md):
  inventario versionado dos hotspots de `op` no runtime, usado para fechar
  `DOT-85` e preparar `DOT-86` / `DOT-87`.
- [`artifacts/onepassword-runtime-cache-contract.md`](artifacts/onepassword-runtime-cache-contract.md):
  contrato versionado de classes de material, TTL, invalidacao e locais
  permitidos para o cache de runtime do `1Password`.
- [`2026-03-07-parecer-e-plano-inicial.md`](2026-03-07-parecer-e-plano-inicial.md):
  parecer arquitetural consolidado e primeira versao do plano de implementacao.
- [`artifacts/README.md`](artifacts/README.md):
  catalogo dos artefatos canonicos de schema, endpoint map e sincronizacao.
- [`artifacts/agent-operations.md`](artifacts/agent-operations.md):
  contrato artifact-first do passo a passo operacional de cada papel em `Jira`
  e `Confluence`, com evidencia obrigatoria por atuacao.
- [`artifacts/jira-writing-standards.md`](artifacts/jira-writing-standards.md):
  padrao canonico de escrita de epics, stories, tasks, bugs e subtasks, com
  criterios de aceite e referencias oficiais da Atlassian.
- [`artifacts/reviewer-standards-catalog.md`](artifacts/reviewer-standards-catalog.md):
  catalogo normativo dos reviewers especializados, com especificacoes oficiais,
  RFCs, convencoes secundarias e tooling de enforcement por especialidade.
- [`artifacts/reviewer-decision-model.md`](artifacts/reviewer-decision-model.md):
  modelo formal de decisao tecnica dos reviewers especializados, inspirado na
  blueprint de reviewer Python e adaptado ao workflow Jira + Confluence.
- [`artifacts/reviewer-severity-policy.md`](artifacts/reviewer-severity-policy.md):
  politica canonica de severidade para os reviewers especializados.
- [`artifacts/reviewer-jira-workflow-policy.md`](artifacts/reviewer-jira-workflow-policy.md):
  politica operacional que transforma review em comentario + evidencia + transicao coerente no Jira.
- [`artifacts/python-quality-review-agent.md`](artifacts/python-quality-review-agent.md):
  blueprint canonico do reviewer Python como sistema formal de decisao tecnica.
- [`artifacts/universal-engineering-standards-stack.md`](artifacts/universal-engineering-standards-stack.md):
  stack universal de governanca tecnica para engenharia moderna, cobrindo
  especificacoes, style guides, lint, format, seguranca, Git, CI/CD, containers
  e AI.
- [`artifacts/migration-bundle.md`](artifacts/migration-bundle.md):
  contrato do bundle auditavel que deve acompanhar cada lote de exportacao para
  `Jira` e `Confluence`.

## Relacionados

- [`../ai-operating-model.md`](../ai-operating-model.md)
- [`../AI-WIP-TRACKER.md`](../AI-WIP-TRACKER.md)
- [`../../ROADMAP.md`](../../ROADMAP.md)
- [`../ROADMAP-DECISIONS.md`](../ROADMAP-DECISIONS.md)
