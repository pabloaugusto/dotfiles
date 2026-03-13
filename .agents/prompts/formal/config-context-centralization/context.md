# Contexto Do Pack

Este pack existe para formalizar a concentracao de configuracoes por contexto no
repo [`dotfiles`](../../../../README.md), com foco especial em drenar a
pulverizacao atual da camada de IA.

## Contexto especifico do repo

- o problema principal atual e a configuracao espalhada, sobretudo em
  [config/ai/](../../../../config/ai/) e
  [`.agents/config.toml`](../../../config.toml)
- a realidade pos-migracao do repo agora e [app/](../../../../app/) como
  runtime do produto dotfiles
- o arquivo futuro `config.toml` dentro de
  [config/](../../../../config/) deve virar o default global do projeto para
  locale, idioma, moeda, calendario e timezone
- este pack nao implementa a arquitetura; ele formaliza a execucao futura
- a execucao futura nao deve usar
  [pyproject.toml](../../../../pyproject.toml) como hub generico
- [DOT-209](https://pabloaugusto.atlassian.net/browse/DOT-209) e referencia
  funcional previa, mas o owner deste pack e
  [DOT-217](https://pabloaugusto.atlassian.net/browse/DOT-217)

## Dependencias informacionais

- [`startup-alignment`](../startup-alignment/prompt.md)
- [`runtime-dev-boundary`](../runtime-dev-boundary/prompt.md)
- [`agents-rules-centralization`](../agents-rules-centralization/prompt.md)
- [`documentation-layer-governance`](../documentation-layer-governance/prompt.md)
- [`time-locale-governance`](../time-locale-governance/prompt.md)

## Resultado esperado deste pack

- existir um pack formal, vivo e catalogado para concentracao de configs por
  contexto
- existir um plano aprovado perene em [`approved-plan.md`](approved-plan.md)
- a execucao futura ganhar contrato claro para concentrar config em:
  - [config/](../../../../config/)
  - a futura pasta `config` sob [app/](../../../../app/)
  - a futura pasta `config` sob [`.agents/`](../../../)
