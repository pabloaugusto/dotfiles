# Prompt Packs

Fonte canonica dos prompt packs versionados deste repo.

## Estrutura canonica

- [`README.md`](README.md): contrato estrutural desta arvore
- [`CATALOG.md`](CATALOG.md): inventario humano dos packs disponiveis
- [`legacy/`](legacy/): material historico, pesquisas e prompts antigos mantidos
  apenas por rastreabilidade
- [`formal/`](formal/): prompt packs vivos e executaveis, organizados por slug

## Contrato dos packs formais

Cada pack formal em [`formal/`](formal/) deve expor:

- um arquivo principal de prompt, como [`prompt.md`](formal/pea-startup-governance/prompt.md)
- um arquivo de contexto, como [`context.md`](formal/pea-startup-governance/context.md)
- metadados declarativos, como [`meta.yaml`](formal/pea-startup-governance/meta.yaml)
- uma pasta de fragmentos reutilizaveis, como [`fragments/`](formal/pea-startup-governance/fragments/)

## Regras

- prompt pack formal nao substitui [`AGENTS.md`](../../AGENTS.md), [`LICOES-APRENDIDAS.md`](../../LICOES-APRENDIDAS.md), [`docs/ai-operating-model.md`](../../docs/ai-operating-model.md) nem os contratos em [`config/ai/`](../../config/ai/)
- packs formais devem refletir o fluxo real do repo: `Jira` como fonte primaria,
  trackers locais como fallback contingencial, governanca Git, worklog, lessons,
  review e closeout
- [`legacy/`](legacy/) preserva historico e contexto; o que estiver vivo e executavel deve
  ser promovido para [`formal/`](formal/)
- startup/restart deve carregar o catalogo e os packs formais aplicaveis quando
  o contrato da rodada exigir
