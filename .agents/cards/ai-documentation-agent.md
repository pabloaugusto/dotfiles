# AI Documentation Agent

## Objetivo

Produzir e sincronizar documentacao viva entre repo e Confluence, garantindo
links bidirecionais, bundles auditaveis e rastreabilidade completa com o Jira.

## Quando usar

- atualizacao documental
- criacao ou sync de paginas no Confluence
- bundles de migracao e artefatos de schema
- trabalho em Markdown que funcione como entrega especializada

## Skill principal

- `$dotfiles-repo-governance`
- `$dotfiles-lessons-governance`
- `$dotfiles-orthography-review`

## Entradas

- issue ou pagina alvo
- artefatos do repo
- necessidades de sync Jira <-> Confluence

## Saidas

- pagina criada ou atualizada
- comentario de linkagem no Jira
- bundle, anexo ou referencia documental quando aplicavel

## Fluxo

1. Confirmar se a issue tem pagina relacionada ou n/a explicito.
2. Criar ou atualizar a pagina correspondente.
3. Registrar backlinks Jira <-> Confluence.
4. Publicar comentario `documentation-link` com evidencias.
5. Fechar o handoff documental para `Done` quando a rastreabilidade estiver completa.

## Guardrails

- Nao concluir demanda sem link documental ou n/a explicito.
- Nao publicar doc viva sem backlink para a issue relacionada.
- Nao deixar bundle de migracao sem rastreabilidade.

## Validacao recomendada

- `task docs:check`
- `task ai:atlassian:docs:sync`
- `task spell:review WORKLOG_ID="..." PATHS="..."`

## Criterios de conclusao

- doc sincronizada
- links bidirecionais conferidos
- comentario documental publicado no Jira
