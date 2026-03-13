# Prompt Packs

Fonte canonica dos prompt packs versionados deste repo.

## Estrutura canonica

- [`README.md`](README.md): contrato estrutural desta arvore
- [`CATALOG.md`](CATALOG.md): inventario humano dos packs disponiveis
- [`legacy/`](legacy/): material historico, pesquisas e prompts antigos mantidos
  apenas por rastreabilidade
- [`formal/`](formal/): prompt packs vivos e executaveis, organizados por slug curto, legivel e orientado ao tema

## Contrato dos packs formais

Cada pack formal em [`formal/`](formal/) deve expor:

- um arquivo principal de prompt, como [`prompt.md`](formal/startup-alignment/prompt.md)
- um arquivo de contexto, como [`context.md`](formal/startup-alignment/context.md)
- metadados declarativos, como [`meta.yaml`](formal/startup-alignment/meta.yaml)
- uma pasta de fragmentos reutilizaveis, como [`fragments/`](formal/startup-alignment/fragments/)
- opcionalmente, um artefato de plano aprovado, como
  [`approved-plan.md`](formal/config-context-centralization/approved-plan.md),
  quando a rodada precisar preservar o plano aprovado pelo usuario de forma
  perene e objetiva
- `task_id` estavel em [`meta.yaml`](formal/startup-alignment/meta.yaml),
  sempre no formato `prompt/<slug>`
- um bloco `dependencies` em [`meta.yaml`](formal/startup-alignment/meta.yaml)
  com `prerequisite_packs` e `preflight_packs`, mesmo quando as listas estiverem vazias
- quando houver `owner_issue`, um bloco `jira` em
  [`meta.yaml`](formal/startup-alignment/meta.yaml) com
  `summary_prefix: "PROMPT:"` e `required_labels` contendo `prompt`

## Artefato opcional `approved-plan.md`

- `approved-plan.md` e opcional
- nao e entrypoint de execucao
- existe para guardar um plano aprovado pelo usuario de forma perene e objetiva
- nao substitui [`prompt.md`](formal/startup-alignment/prompt.md),
  [`context.md`](formal/startup-alignment/context.md) nem
  [`meta.yaml`](formal/startup-alignment/meta.yaml)
- quando existir, deve refletir o plano aprovado vigente daquela trilha, sem
  virar dump solto de conversas

## Naming operacional obrigatorio

Quando a rodada tocar qualquer arquivo versionado em [`.agents/prompts/`](./):

- o pack formal deve declarar `task_id: prompt/<slug>` em
  [`meta.yaml`](formal/startup-alignment/meta.yaml)
- a branch deve usar tipo `prompt`, no formato `prompt/<jira-key>-<slug>`
- commit e `PR title` devem continuar no contrato `emoji + conventional`, mas
  com `scope` obrigatorio `prompt`
- a issue Jira dona da rodada deve usar titulo com prefixo `PROMPT:` e carregar
  a label `prompt`
- hooks locais, tasks e CI devem validar esse namespace de forma contextual
- os slugs dos packs devem ser curtos, legiveis e semanticamente claros, evitando nomes excessivamente tecnicos ou longos quando houver alternativa mais amigavel sem perda de precisao
- cada pack formal deve declarar explicitamente quais packs precisam ser
  executados antes dele e quais packs precisam ao menos ser checados antes da
  execucao segura da rodada
- quando um pack consumir infraestrutura ou contratos de outro, a dependencia
  deve ser declarada em [`meta.yaml`](formal/startup-alignment/meta.yaml),
  reforcada em [`context.md`](formal/startup-alignment/context.md) e visivel no
  catalogo

## Regras

- prompt pack formal nao substitui [`AGENTS.md`](../../AGENTS.md), [`LICOES-APRENDIDAS.md`](../../LICOES-APRENDIDAS.md), [`docs/ai-operating-model.md`](../../docs/ai-operating-model.md) nem os contratos em [`config/ai/`](../../config/ai/)
- packs formais devem refletir o fluxo real do repo: `Jira` como fonte primaria,
  trackers locais como fallback contingencial, governanca Git, worklog, lessons,
  review e closeout
- [`legacy/`](legacy/) preserva historico e contexto; o que estiver vivo e executavel deve
  ser promovido para [`formal/`](formal/)
- startup/restart deve carregar o catalogo e os packs formais aplicaveis quando
  o contrato da rodada exigir
