# Confluence Schema

- Status: `artifact-first`
- Data-base: `2026-03-07`
- Fonte canonica:
  [`../../../config/ai/confluence-model.yaml`](../../../config/ai/confluence-model.yaml)
- Sincronizacao alvo:
  - pagina `DOT - AI Control Plane Hub`
  - paginas filhas de schema, operacao e migration plan

## Space alvo

- requested key: `DOT`
- accepted keys: `DOT`
- o modelo canonico nao carrega mais retrocompatibilidade de nome legado para o
  space

## Home page alvo

- `DOT - AI Control Plane Hub`

## Arvore inicial de paginas

- `DOT - AI Control Plane Hub`
- `Schema e Artefatos`
- `DOT - Jira Schema`
- `DOT - Jira Board Layout`
- `DOT - Confluence Schema`
- `DOT - Endpoint Catalog`
- `DOT - Agent Operations Contract`
- `DOT - Migration Bundle Contract`
- `Delivery e Backfill`
- `DOT - Jira Backfill Ledger`
- `DOT - Migration Plan`
- `DOT - AI Product Owner Blueprint`
- `DOT - Agent Operation Playbook`
- `Operacao e Governanca`
- `DOT - Auth and Permissions`
- `DOT - Tenant Diagnostics`
- `DOT - 1Password Batch Resolution`
- `DOT - Dev-Time Foundation`
- `Estrategia e Evolucao`
- `DOT - Atlassian OpenAPI Strategy`
- `DOT - Python Modular Architecture Research`
- `DOT - Atlassian Product Discovery`
- `DOT - Market Best Practices`
- `DOT - Optional Capabilities Figma UX SEO`

## Contrato de publicacao

- cada schema nasce primeiro no repo
- cada artefato sincronizado para o `Confluence` deve manter link de volta para
  a issue correspondente no `Jira`
- cada issue do `Jira` que gerar pagina ou atualizar pagina deve receber
  comentario `documentation-link`
- artefatos do repo permanecem versionados como espelho essencial
- o passo a passo operacional por papel fica consolidado em
  [`agent-operations.md`](agent-operations.md)
- o sync de documentacao deve poder rodar de forma independente da semeadura
  completa de `Jira`, para manter o `Confluence` vivo mesmo quando o board do
  `Jira Software` ainda estiver em drift
