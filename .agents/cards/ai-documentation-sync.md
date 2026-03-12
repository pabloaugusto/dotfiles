# Sync Documental

## Objetivo

Executar a publicacao, atualizacao, backlinks, `documentation-link` e
rastreabilidade cross-surface da camada documental, sempre consumindo a
fundacao oficial de sync e sem redefinir source of truth, placement ou
lifecycle.

## Quando usar

- publicacao ou update documental em Confluence
- materializacao de backlinks Jira <-> Confluence
- `documentation-link`, anexos, bundles e evidencias documentais
- artefatos elegiveis para o outbox duravel da fundacao de sync

## Skill principal

- `$dotfiles-repo-governance`
- `$dotfiles-critical-integrations`

## Entradas

- decisao de placement e source of truth do `ai-documentation-manager`
- conteudo aprovado pelo writer e reviewers aplicaveis
- manifest [`config/ai/sync-targets.yaml`](../../config/ai/sync-targets.yaml)
- issue Jira e superficie remota alvo

## Saidas

- pagina criada ou atualizada
- comentario `documentation-link` no Jira
- evidencias de publicacao, backlinks ou bundle
- evento registrado na fundacao de sync quando aplicavel

## Fluxo

1. Confirmar se o artefato e elegivel ao fluxo oficial de sync.
2. Ler a decisao de placement/source of truth antes de publicar.
3. Executar create/update, backlinks e comentario `documentation-link`.
4. Registrar evidencias e artefatos no Jira e na superficie remota.
5. Fechar a rastreabilidade documental sem absorver ownership de conteudo.

## Guardrails

- Nao redefinir `workspace_id`, `runtime_environment_id`, outbox ou `ack`.
- Nao decidir source of truth, placement ou lifecycle.
- Nao publicar conteudo sem decisao documental explicita.
- Nao substituir writer, reviewer documental ou Curador Repo.

## Validacao recomendada

- `task ai:control-plane:sync:check`
- `task ai:control-plane:sync:status`
- `task docs:check`

## Criterios de conclusao

- rastreabilidade cross-surface materializada
- backlinks e `documentation-link` registrados
- uso aderente da fundacao oficial de sync
- nenhuma decisao de governanca documental feita por inercia
