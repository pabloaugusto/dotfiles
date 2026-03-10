# Migration Bundle

- Status: `artifact-first`
- Data-base: `2026-03-07`
- Bundle alvo: `.cache/atlassian-migration/atlassian-migration-<timestamp>.zip`
- Gerador:
  [`../../../scripts/ai-atlassian-migration-bundle.py`](../../../scripts/ai-atlassian-migration-bundle.py)

## Objetivo

Preservar, em um unico artefato auditavel, tudo o que sera exportado do repo
para `Jira` e `Confluence`.

## Conteudo minimo

- manifest com hash, tamanho e categoria de cada arquivo
- snapshot das specs oficiais vendorizadas em
  [`../../../vendor/atlassian/`](../../../vendor/atlassian/) que embasam o
  lote
- schemas do `Jira` e do `Confluence`
- catalogo de endpoints usados no apply e na semeadura
- plano declarativo de backfill
- registros planejados para `Jira`
- registros planejados para `Confluence`
- copia dos artefatos fonte do repo que fundamentaram a migracao
- copia da logica que gerou o bundle e o plano

## Contrato de uso

- gerar o bundle antes de cada lote de exportacao
- anexar o `.zip` na issue correspondente do `Jira` assim que a issue de
  migracao existir
- referenciar o mesmo bundle na pagina correspondente do `Confluence`
- manter o bundle fora do Git; o que fica versionado e a logica que o produz
