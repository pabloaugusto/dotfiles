# Jira Board Layout

- Status: `artifact-first`
- Data-base: `2026-03-08`
- Fonte canonica:
  [`../../../config/ai/jira-model.yaml`](../../../config/ai/jira-model.yaml)
- Escopo:
  alinhar o `DOT board` ao workflow oficial antes da semeadura retroativa

## Evidencia do drift atual

- a UI do board mostra o erro:
  - `This status isn't available in any workflows used by this board`
- os statuses legados ainda presos nas colunas sao:
  - `Selected for Development`
  - `In Progress`
- os statuses oficiais hoje aparecem como `Unmapped statuses`:
  - `Refinement`
  - `Ready`
  - `Doing`
  - `Testing`
  - `Review`
  - `Changes Requested`

## Colunas alvo

- `Backlog`
  - status: `Backlog`
- `Refinement`
  - status: `Refinement`
- `Ready`
  - status: `Ready`
- `Doing`
  - status: `Doing`
- `Testing`
  - status: `Testing`
- `Review`
  - status: `Review`
- `Changes Requested`
  - status: `Changes Requested`
- `Done`
  - status: `Done`

## Acoes de ajuste

1. remover das colunas quaisquer statuses legados nao pertencentes ao workflow
   oficial
2. criar as colunas faltantes no board para refletir o contrato de workflow
3. mover cada status oficial do painel `Unmapped statuses` para sua coluna
   correspondente
4. validar que o painel `Unmapped statuses` fique vazio
5. validar que nao existam warnings amarelos nas colunas

## Bloqueio de automacao atual

- a leitura oficial da board API continua falhando em
  [`/rest/agile/1.0/board`](https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/)
  com `401 Unauthorized; scope does not match`
- a documentacao oficial do `Jira Software` exige `read:project:jira` em
  conjunto com os scopes de board para leitura do board
- a API publica oficial documentada no repo nao expone endpoint de escrita para
  mutar o layout de colunas; por isso a correcao fina do layout depende de UI
  autenticada

## Regra de governanca

- nenhuma semeadura retroativa deve rodar antes de o board refletir este layout
- excecao de uma rodada aprovada em `2026-03-08`:
  - o usuario liberou a semeadura atual mesmo com o gap visual do board
  - nas proximas rodadas, o bloqueio volta a valer por padrao
- toda validacao do board deve gerar evidencia:
  - screenshot
  - comentario estruturado na issue de migracao
  - link da pagina correspondente no `Confluence`
