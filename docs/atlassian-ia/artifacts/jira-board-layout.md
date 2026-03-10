# Jira Board Layout

- Status: `artifact-first`
- Data-base: `2026-03-08`
- Fonte canonica:
  [`../../../config/ai/jira-model.yaml`](../../../config/ai/jira-model.yaml)
- Escopo:
  alinhar o `DOT board` ao workflow oficial e manter a evidência do estado real
  do tenant

## Estado validado em 2026-03-08

- a UI autenticada do board foi corrigida com `Playwright`
- o layout visual agora reflete o workflow oficial
- o board settings mostra `warning_count = 0`
- o status `Paused` esta mapeado em coluna propria
- o painel `Unmapped statuses` nao apresenta mais drift residual para o fluxo
  oficial
- as evidencias desta rodada ficaram anexadas nas issues operacionais:
  - [`DOT-65`](https://pabloaugusto.atlassian.net/browse/DOT-65)
  - [`DOT-66`](https://pabloaugusto.atlassian.net/browse/DOT-66)

## Colunas canonicas confirmadas

- `Backlog`
  - status: `Backlog`
- `Refinement`
  - status: `Refinement`
- `Ready`
  - status: `Ready`
- `Doing`
  - status: `Doing`
- `Paused`
  - status: `Paused`
- `Testing`
  - status: `Testing`
- `Review`
  - status: `Review`
- `Changes Requested`
  - status: `Changes Requested`
- `Done`
  - status: `Done`

## Acoes executadas na rodada

1. atualizar o workflow publicado do tenant para incluir `Paused`
2. validar as transicoes reais do projeto `DOT` por API
3. corrigir o layout visual do board por UI autenticada com `Playwright`
4. criar a coluna `Paused` no board
5. confirmar por browser que o board settings ficou sem warnings
6. promover `project.target_board.layout_confirmed = true` no modelo local

## Bloqueio de automacao atual

- a leitura oficial da board API continua falhando em
  [`/rest/agile/1.0/board`](https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/)
  com `401 Unauthorized; scope does not match`
- a documentacao oficial do `Jira Software` exige `read:project:jira` em
  conjunto com os scopes de board para leitura do board
- a API publica oficial documentada no repo nao expone endpoint de escrita para
  mutar o layout de colunas; por isso a correcao fina do layout depende de UI
  autenticada
- o gap residual deixou de ser visual; agora e exclusivamente de automacao pela
  API `Jira Software`

## Regra de governanca

- a semeadura retroativa nao deve rodar antes de o board refletir este layout
- como o layout foi confirmado, o flag do modelo local ja pode permanecer
  habilitado
- excecao de uma rodada aprovada em `2026-03-08`:
  - o usuario liberou a semeadura atual mesmo com o gap visual do board
  - nas proximas rodadas, o bloqueio volta a valer por padrao
- toda validacao do board deve gerar evidencia:
  - screenshot
  - comentario estruturado na issue de migracao
  - link da pagina correspondente no `Confluence`
