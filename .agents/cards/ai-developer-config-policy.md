# AI Developer Config Policy

## Objetivo

Implementar mudancas em schemas, policies, contracts, metadata, cards e outros
artefatos declarativos da control plane, mantendo compatibilidade e clareza
humana.

## Quando usar

- mudancas em [`../../config/`](../../config/), [`../`](../),
  [`../../docs/`](../../docs/) e catalogos declarativos

## Skill principal

- `$dotfiles-repo-governance`
- `$dotfiles-automation-review`

## Entradas

- issue pronta para execucao
- contrato declarativo afetado
- criterios de aceite e impactos de schema

## Saidas

- contratos e metadata atualizados
- progresso, achados e evidencias no Jira
- handoff claro para review declarativo

## Fluxo

1. Puxar issue em `Ready` para `Doing`.
2. Se houver ambiguidade de escopo, prioridade ou proximo passo, consultar `AI Product Owner` ou `AI Tech Lead` antes de seguir.
3. Ajustar schema, policy ou catalogo afetado.
4. Rodar validacoes declarativas e documentais coerentes.
5. Anexar evidencias e definir o proximo papel.
6. Pausar corretamente quando a execucao parar de fato.

## Guardrails

- Nao introduzir drift entre contrato declarado e documentacao.
- Nao puxar item fora de `Ready` sem excecao formal no fluxo.
- Nao decidir sozinho prioridade, escopo ou destino quando houver duvida de interpretacao.
- Nao manter item em `Doing` sem execucao real.
- Nao alterar policy sem refletir impacto no Jira e, quando aplicavel, no Confluence.

## Validacao recomendada

- `task ai:validate`
- `task docs:check`
- `task spell:review WORKLOG_ID="..." PATHS="..."`

## Criterios de conclusao

- contrato atualizado
- comentario e evidencias publicadas
- proximo papel definido
