# Prompt Packs Catalog

<!-- cspell:words agnostica duravel integracao historicos -->

## Formais

| Pack | Task ID | Objetivo | Entrypoints | Dependencias | Dono |
| --- | --- | --- | --- | --- | --- |
| [`startup-alignment`](formal/startup-alignment/prompt.md) | `prompt/startup-alignment` | Formalizar o `Pre-Execution Alignment` e sua integracao com `startup/restart`, delegacao e governanca operacional do repo | [`prompt.md`](formal/startup-alignment/prompt.md), [`context.md`](formal/startup-alignment/context.md), [`meta.yaml`](formal/startup-alignment/meta.yaml) | nenhuma | [`DOT-178`](https://pabloaugusto.atlassian.net/browse/DOT-178) |
| [`startup-governor-enforcement`](formal/startup-governor-enforcement/prompt.md) | `prompt/startup-governor-enforcement` | Endurecer o startup obrigatorio com um agente gatekeeper dedicado, `startup clearance` verificavel e bloqueio da primeira resposta operacional ate a sessao estar realmente pronta | [`prompt.md`](formal/startup-governor-enforcement/prompt.md), [`context.md`](formal/startup-governor-enforcement/context.md), [`meta.yaml`](formal/startup-governor-enforcement/meta.yaml) | checar `startup-alignment` e `agents-rules-centralization` antes da execucao segura da rodada | [`DOT-206`](https://pabloaugusto.atlassian.net/browse/DOT-206) |
| [`agents-rules-centralization`](formal/agents-rules-centralization/prompt.md) | `prompt/agents-rules-centralization` | Formalizar a unificacao da governanca normativa por tema em [`.agents/rules/`](../rules/), com migracao por ondas, fallback tematico e paridade entre `AGENTS`, docs, startup e enforcement | [`prompt.md`](formal/agents-rules-centralization/prompt.md), [`context.md`](formal/agents-rules-centralization/context.md), [`meta.yaml`](formal/agents-rules-centralization/meta.yaml) | checar `startup-alignment` e `documentation-layer-governance` antes da execucao segura da rodada | [`DOT-205`](https://pabloaugusto.atlassian.net/browse/DOT-205) |
| [`sync-outbox-foundation`](formal/sync-outbox-foundation/prompt.md) | `prompt/sync-outbox-foundation` | Formalizar a arquitetura-base de sync, outbox duravel e fonte perene remota para artefatos vivos de IA | [`prompt.md`](formal/sync-outbox-foundation/prompt.md), [`context.md`](formal/sync-outbox-foundation/context.md), [`meta.yaml`](formal/sync-outbox-foundation/meta.yaml) | checar `startup-alignment` antes da execucao segura da rodada | [`DOT-179`](https://pabloaugusto.atlassian.net/browse/DOT-179) |
| [`documentation-layer-governance`](formal/documentation-layer-governance/prompt.md) | `prompt/documentation-layer-governance` | Formalizar a camada documental por agentes de IA, com ownership por superficie, governanca documental e dependencia explicita da fundacao de sync | [`prompt.md`](formal/documentation-layer-governance/prompt.md), [`context.md`](formal/documentation-layer-governance/context.md), [`meta.yaml`](formal/documentation-layer-governance/meta.yaml) | checar `startup-alignment`; executar ou validar `sync-outbox-foundation` antes | [`DOT-181`](https://pabloaugusto.atlassian.net/browse/DOT-181) |
| [`time-locale-governance`](formal/time-locale-governance/prompt.md) | `prompt/time-locale-governance` | Formalizar a governanca temporal do repo, com policy global TOML, registry por superficie e enforcement contra drift de timezone, locale e semantica temporal | [`prompt.md`](formal/time-locale-governance/prompt.md), [`context.md`](formal/time-locale-governance/context.md), [`meta.yaml`](formal/time-locale-governance/meta.yaml) | checar `startup-alignment`, `documentation-layer-governance` e `sync-outbox-foundation` antes da execucao segura da rodada | [`DOT-180`](https://pabloaugusto.atlassian.net/browse/DOT-180) |
| [`runtime-dev-boundary`](formal/runtime-dev-boundary/prompt.md) | `prompt/runtime-dev-boundary` | Formalizar a separacao da camada runtime da app e da camada de desenvolvimento do repo, preparando a migracao para [`app/`](../../app/) antes da centralizacao futura de config dev | [`prompt.md`](formal/runtime-dev-boundary/prompt.md), [`context.md`](formal/runtime-dev-boundary/context.md), [`meta.yaml`](formal/runtime-dev-boundary/meta.yaml) | checar `startup-alignment`, `agents-rules-centralization` e `documentation-layer-governance` antes da execucao segura da rodada | [`DOT-210`](https://pabloaugusto.atlassian.net/browse/DOT-210) |
| [`config-context-centralization`](formal/config-context-centralization/prompt.md) | `prompt/config-context-centralization` | Formalizar a concentracao de configuracoes por contexto em [`config/`](../../config/), na futura pasta `config` sob [`app/`](../../app/) e na futura pasta `config` sob [`.agents/`](../), com hub global de regionalizacao, drenagem de literais/configs espalhados e hardeners anti-drift | [`prompt.md`](formal/config-context-centralization/prompt.md), [`context.md`](formal/config-context-centralization/context.md), [`meta.yaml`](formal/config-context-centralization/meta.yaml), [`approved-plan.md`](formal/config-context-centralization/approved-plan.md) | checar `startup-alignment`, `runtime-dev-boundary`, `agents-rules-centralization`, `documentation-layer-governance` e `time-locale-governance` antes da execucao segura da rodada | [`DOT-217`](https://pabloaugusto.atlassian.net/browse/DOT-217) |

## Legados

| Grupo | Objetivo | Referencia |
| --- | --- | --- |
| [`legacy/01`](legacy/01/) | materiais historicos de auditoria e sugestoes anteriores | [`legacy/01/`](legacy/01/) |
| [`legacy/01.md`](legacy/01.md) | prompt historico agregado da trilha `01` | [`legacy/01.md`](legacy/01.md) |
| [`legacy/02.md`](legacy/02.md) | prompt historico agregado da trilha `02` | [`legacy/02.md`](legacy/02.md) |

## Regra de manutencao

- todo pack formal novo precisa entrar neste catalogo na mesma rodada
- todo pack formal novo precisa expor `task_id: prompt/<slug>` em `meta.yaml`
- nomes de packs formais devem permanecer curtos, legiveis e semanticamente claros
- todo pack formal novo precisa declarar dependencias e preflight packs de forma
  explicita e visivel no catalogo
- quando a rodada tocar [`.agents/prompts/`](./), branch, commit e `PR title`
  precisam respeitar o namespace operacional `prompt`
- [`legacy/`](legacy/) nao substitui [`formal/`](formal/); quando um prompt
  voltar a ser vivo, ele deve ser promovido e catalogado
