# Vendor Atlassian OpenAPI

Diretorio versionado para congelar os specs OpenAPI oficiais usados pelo
control plane Atlassian.

## Regras

- nao gerar clients direto da URL em producao
- sempre vendorizar primeiro os specs
- qualquer codegen deve apontar para estes arquivos vendorizados
- atualizar `manifest.json` sempre que um spec for revendorizado

## Artefatos esperados

- `jira-openapi.json`
- `confluence-openapi.json`
- `manifest.json`
