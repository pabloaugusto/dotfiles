# AI Fallback Ledger

Atualizado em: 2026-03-11 08:26 UTC

Registro canonico do uso excepcional dos trackers locais quando o `Jira` nao
consegue sustentar o fluxo primario.

## Regras operacionais

- O modo normal do repo e `primary`: o `Jira` segue como fonte primaria e o
  fallback local nao pode virar ledger concorrente por inercia.
- O modo `degraded` so pode ser usado quando houver indisponibilidade real do
  `Jira` ou falha objetiva da sincronizacao primaria.
- Toda degradacao real deve gerar um registro ativo neste ledger antes de
  transformar [`AI-WIP-TRACKER.md`](AI-WIP-TRACKER.md) ou
  [`ROADMAP-DECISIONS.md`](ROADMAP-DECISIONS.md) em fallback operacional.
- Quando o `Jira` voltar, a sessao entra em `recovery` ate que cada registro
  ativo seja classificado como `drained`, `reconciled` ou `obsolete`.
- `drained` significa que o contexto local foi drenado de volta para o `Jira`.
- `reconciled` significa que o `Jira` voltou com contexto equivalente, sem
  precisar copiar tudo literalmente do fallback local.
- `obsolete` significa que o registro local deixou de representar backlog vivo
  e foi encerrado sem sincronizacao adicional.

## Registros ativos

<!-- ai-fallback:active:start -->
| Capturado UTC | Atualizado UTC | Tracker | Referencia local | Estado | Jira | Resumo | Proximo passo |
| --- | --- | --- | --- | --- | --- | --- | --- |
| (sem itens) | - | - | - | - | - | - | - |
<!-- ai-fallback:active:end -->

## Registros resolvidos

<!-- ai-fallback:resolved:start -->
| Capturado UTC | Resolvido UTC | Tracker | Referencia local | Estado | Jira | Resumo | Resultado |
| --- | --- | --- | --- | --- | --- | --- | --- |
| (sem itens) | - | - | - | - | - | - | - |
<!-- ai-fallback:resolved:end -->
