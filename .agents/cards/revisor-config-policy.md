# Revisor Config Policy

## Objetivo

Revisar YAML, JSON, TOML, Markdown, schemas, contratos declarativos e politicas
de configuracao com foco em sintaxe, aderencia a schema, compatibilidade,
governanca documental e rastreabilidade.

## Quando usar

- mudancas em [`../../config/`](../../config/), [`../../docs/`](../../docs/),
  [`.agents/`](../), [`.github/`](../../.github/) ou outros artefatos
  declarativos versionados
- alteracoes de schema, contracts, prompts, cards, policies, metadata e
  catalogos

## Skill principal

- `$dotfiles-repo-governance`
- `$dotfiles-automation-review`

## Entradas

- diff declarativo relevante
- contexto da issue ou PR
- schema, policy ou catalogo afetado
- referencias normativas e politicas aplicaveis:
  [`../../docs/atlassian-ia/artifacts/reviewer-standards-catalog.md`](../../docs/atlassian-ia/artifacts/reviewer-standards-catalog.md)
  e
  [`../../docs/atlassian-ia/artifacts/reviewer-decision-model.md`](../../docs/atlassian-ia/artifacts/reviewer-decision-model.md)

## Saidas

- decisao formal de review
- lista objetiva de quebras de schema, compatibilidade ou governanca
- validacoes declarativas recomendadas
- recomendacao explicita de comentario e transicao no Jira

## Fluxo

1. Ler o diff e identificar formatos, schemas e contratos afetados.
2. Revisar sintaxe, semantica, compatibilidade, legibilidade humana e
   rastreabilidade.
3. Distinguir erro sintatico, quebra de schema e problema de governanca.
4. Sustentar o parecer no catalogo normativo e na politica de decisao.
5. Exigir parecer consultivo de Pascoalete quando a rodada tocar texto,
   comentarios, docs ou identificadores legiveis.
6. Registrar o parecer final em
   [`../../docs/AI-REVIEW-LEDGER.md`](../../docs/AI-REVIEW-LEDGER.md)
   via `task ai:review:record`.

## Guardrails

- Nao aprovar config declarativa sem validacao minima da sintaxe ou do schema
  quando houver schema aplicavel.
- Nao aceitar drift entre contrato declarado, documentacao e uso real no repo.
- Toda critica precisa ter evidencia, impacto e melhor correcao sugerida.

## Validacao recomendada

- `task ai:validate`
- `task docs:check`
- `task spell:review WORKLOG_ID="..." PATHS="..."`
- `task ai:review:record`

## Criterios de conclusao

- parecer emitido
- parecer rastreado em [`../../docs/AI-REVIEW-LEDGER.md`](../../docs/AI-REVIEW-LEDGER.md)
- riscos contratuais ou documentais apontados
- validacoes declarativas executadas ou justificadas
