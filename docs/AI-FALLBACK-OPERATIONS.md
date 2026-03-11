# AI Fallback Operations

## Objetivo

Definir quando os trackers locais podem atuar como fallback contingencial e
como a sessao deve voltar do modo degradado para o `Jira` primario sem
ambiguidade.

## Modos operacionais

### `primary`

- `Jira` e a fonte primaria do backlog, do `WIP`, das decisoes e dos handoffs.
- [`AI-WIP-TRACKER.md`](AI-WIP-TRACKER.md) e
  [`ROADMAP-DECISIONS.md`](ROADMAP-DECISIONS.md) continuam existindo para
  continuidade local, mas nao podem assumir o papel de ledger primario.
- O ledger de fallback deve permanecer sem registros ativos.

### `degraded`

- So entra em vigor quando houver indisponibilidade real do `Jira` ou falha
  objetiva da sincronizacao primaria.
- Antes de transformar um tracker local em contingencia real, a sessao precisa
  registrar a captura em [`AI-FALLBACK-LEDGER.md`](AI-FALLBACK-LEDGER.md).
- Enquanto durar a degradacao, a sessao pode manter continuidade local no
  tracker correspondente, sempre preservando a referencia do work item dono.

### `recovery`

- Comeca quando o `Jira` volta a responder, mas ainda existem registros ativos
  no ledger de fallback.
- A sessao so pode declarar retorno ao modo `primary` depois de classificar
  cada registro como `drained`, `reconciled` ou `obsolete`.

## Estados de resolucao

- `drained`: o contexto local foi drenado de volta para o `Jira`.
- `reconciled`: o `Jira` voltou com contexto equivalente, e o fallback local
  foi reconciliado sem copia literal integral.
- `obsolete`: o registro local deixou de representar backlog vivo e foi
  encerrado sem sincronizacao adicional.

## Tasks canonicas

### `task ai:fallback:status`

- verifica se a sessao esta em `primary`, `degraded` ou `recovery`
- informa se o `Jira` esta acessivel
- mostra quantos registros ativos ainda faltam drenar

### `task ai:fallback:capture`

- cria ou atualiza um registro ativo no ledger
- deve ser usada antes de tratar `AI-WIP-TRACKER` ou `ROADMAP-DECISIONS` como
  fallback operacional real
- por padrao bloqueia captura quando o `Jira` esta saudavel

### `task ai:fallback:resolve`

- resolve um registro ativo como `drained`, `reconciled` ou `obsolete`
- para `drained` e `reconciled`, sincroniza comentario estruturado no `Jira`
  por padrao
- fecha a pendencia do ledger e deixa o retorno ao modo `primary` auditavel

## Fluxo recomendado

1. Rodar `task ai:fallback:status`.
2. Se o modo continuar `primary`, operar normalmente com `Jira` como primario.
3. Se o `Jira` falhar de verdade, registrar a captura com
   `task ai:fallback:capture`.
4. Trabalhar localmente apenas no tracker estritamente necessario.
5. Quando o `Jira` voltar, rodar `task ai:fallback:status` de novo.
6. Resolver cada registro com `task ai:fallback:resolve`.
7. Voltar ao modo `primary` apenas quando o ledger nao tiver mais item ativo.
