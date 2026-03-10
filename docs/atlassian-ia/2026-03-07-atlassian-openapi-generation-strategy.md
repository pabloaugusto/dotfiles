# Estrategia OpenAPI Atlassian

- Status: `aprovada-para-implantacao`
- Data-base: `2026-03-07`
- Contexto relacionado:
  - [`2026-03-07-atlassian-auth-scopes-and-permissions.md`](2026-03-07-atlassian-auth-scopes-and-permissions.md)
  - [`artifacts/atlassian-endpoints.md`](artifacts/atlassian-endpoints.md)
  - [`../../vendor/atlassian/README.md`](../../vendor/atlassian/README.md)

## Decisao

O control plane Atlassian deve usar specs OpenAPI oficiais vendorizadas no repo
como fonte para codegen, inspeccao e documentacao de endpoints.

## Fonte oficial por produto

- Jira Cloud:
  - humana:
    [`REST API v3`](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
  - OpenAPI:
    [`swagger-v3.v3.json`](https://dac-static.atlassian.com/cloud/jira/platform/swagger-v3.v3.json?_v=1.8409.0)
- Confluence Cloud:
  - humana:
    [`REST API v2`](https://developer.atlassian.com/cloud/confluence/rest/v2/)
  - OpenAPI:
    [`openapi-v2.v3.json`](https://dac-static.atlassian.com/cloud/confluence/openapi-v2.v3.json?_v=1.8409.0)
- Jira Product Discovery:
  - sem spec publico separado no fluxo atual
  - tratar como extensao operacional da plataforma Jira onde aplicavel

## Estrategia de geracao

- baseline de producao: `OpenAPI Generator`
- opcao idiomatica/experimental: `openapi-python-client`
- nunca gerar direto da URL em fluxo de producao
- sempre:
  - baixar o spec oficial
  - vendorizar no repo
  - opcionalmente aplicar patch controlado
  - gerar clients de forma reprodutivel por task/CI

## Implicacao para a arquitetura

- clients gerados ficam isolados da regra de negocio
- o dominio usa facades pequenas e estaveis
- codegen e substituivel sem reescrever o dominio
