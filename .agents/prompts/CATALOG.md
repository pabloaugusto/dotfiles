# Prompt Packs Catalog

<!-- cspell:words agnostica duravel integracao historicos -->

## Formais

| Pack | Task ID | Objetivo | Entrypoints | Dono |
| --- | --- | --- | --- | --- |
| [`agnostic-sync-outbox-foundation`](formal/agnostic-sync-outbox-foundation/prompt.md) | `prompt/agnostic-sync-outbox-foundation` | Formalizar a arquitetura agnostica de sync, outbox duravel e fonte perene remota para artefatos vivos de IA | [`prompt.md`](formal/agnostic-sync-outbox-foundation/prompt.md), [`context.md`](formal/agnostic-sync-outbox-foundation/context.md), [`meta.yaml`](formal/agnostic-sync-outbox-foundation/meta.yaml) | [`DOT-179`](https://pabloaugusto.atlassian.net/browse/DOT-179) |
| [`pea-startup-governance`](formal/pea-startup-governance/prompt.md) | `prompt/pea-startup-governance` | Formalizar o `Pre-Execution Alignment` e sua integracao com `startup/restart`, delegacao e governanca operacional do repo | [`prompt.md`](formal/pea-startup-governance/prompt.md), [`context.md`](formal/pea-startup-governance/context.md), [`meta.yaml`](formal/pea-startup-governance/meta.yaml) | [`DOT-178`](https://pabloaugusto.atlassian.net/browse/DOT-178) |

## Legados

| Grupo | Objetivo | Referencia |
| --- | --- | --- |
| [`legacy/01`](legacy/01/) | materiais historicos de auditoria e sugestoes anteriores | [`legacy/01/`](legacy/01/) |
| [`legacy/01.md`](legacy/01.md) | prompt historico agregado da trilha `01` | [`legacy/01.md`](legacy/01.md) |
| [`legacy/02.md`](legacy/02.md) | prompt historico agregado da trilha `02` | [`legacy/02.md`](legacy/02.md) |

## Regra de manutencao

- todo pack formal novo precisa entrar neste catalogo na mesma rodada
- todo pack formal novo precisa expor `task_id: prompt/<slug>` em `meta.yaml`
- quando a rodada tocar [`.agents/prompts/`](./), branch, commit e `PR title`
  precisam respeitar o namespace operacional `prompt`
- [`legacy/`](legacy/) nao substitui [`formal/`](formal/); quando um prompt
  voltar a ser vivo, ele deve ser promovido e catalogado
