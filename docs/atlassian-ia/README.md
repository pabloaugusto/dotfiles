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
- [`2026-03-07-parecer-e-plano-inicial.md`](2026-03-07-parecer-e-plano-inicial.md):
  parecer arquitetural consolidado e primeira versao do plano de implementacao.
- [`artifacts/README.md`](artifacts/README.md):
  catalogo dos artefatos canonicos de schema, endpoint map e sincronizacao.
- [`artifacts/agent-operations.md`](artifacts/agent-operations.md):
  contrato artifact-first do passo a passo operacional de cada papel em `Jira`
  e `Confluence`, com evidencia obrigatoria por atuacao.
- [`artifacts/migration-bundle.md`](artifacts/migration-bundle.md):
  contrato do bundle auditavel que deve acompanhar cada lote de exportacao para
  `Jira` e `Confluence`.

## Relacionados

- [`../ai-operating-model.md`](../ai-operating-model.md)
- [`../AI-WIP-TRACKER.md`](../AI-WIP-TRACKER.md)
- [`../../ROADMAP.md`](../../ROADMAP.md)
- [`../ROADMAP-DECISIONS.md`](../ROADMAP-DECISIONS.md)
