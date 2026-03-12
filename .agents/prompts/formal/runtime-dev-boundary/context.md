# Contexto Do Pack

Este pack existe para preparar a execucao segura da separacao arquitetural entre
runtime da app e camada de desenvolvimento do repo.

## Por que este pack foi criado

Este pack foi criado para impedir que a futura centralizacao da camada de
desenvolvimento em [`config/`](../../../../config/) aconteca em cima de uma
fronteira arquitetural ainda ambigua.

Antes de discutir consolidacao de config, o repo precisa deixar explicito o que
e runtime da app e o que e desenvolvimento/governanca do sistema.

## Estado atual relevante

- o runtime da app agora mora em [`app/bootstrap/`](../../../../app/bootstrap/)
  e [`app/df/`](../../../../app/df/)
- a pasta [`app/`](../../../../app/) ja existe como camada explicita de runtime
- [`pyproject.toml`](../../../../pyproject.toml) ja esta corretamente
  posicionado como dono da toolchain Python, dependencias, lint, testes e
  configuracao de desenvolvimento nao-runtime
- [`config/`](../../../../config/) ja abriga configuracao de suporte,
  control plane e tooling do repo, mas nao deve absorver runtime da app

## Fronteira desejada

- [`app/`](../../../../app/) deve se tornar a camada explicita de runtime da
  app e do workstation
- [`config/`](../../../../config/) deve permanecer reservado a
  desenvolvimento/suporte/governanca
- [`pyproject.toml`](../../../../pyproject.toml) deve permanecer intacto no seu
  papel atual

## O que esperamos resolver com ele

- reduzir o drift semantico entre runtime e desenvolvimento
- simplificar a leitura estrutural do repo para IA e humanos
- preparar a segunda etapa de centralizacao da camada de desenvolvimento sem
  misturar config de runtime
- deixar a topologia coerente com o racional que o repo ja descreve em
  [`CONTEXT.md`](../../../../CONTEXT.md) e [`README.md`](../../../../README.md)

## Dependencia arquitetural

- a centralizacao futura da configuracao da camada de desenvolvimento em
  [`config/`](../../../../config/) ja foi rastreada em
  [`DOT-209`](https://pabloaugusto.atlassian.net/browse/DOT-209)
- esse follow-up so deve avancar depois que a separacao runtime vs
  desenvolvimento estiver realmente concluida

## Preflight de execucao

- este pack nao autoriza piggyback em WIP ativo sem relacao
- este pack deve nascer em branch e worktree proprios
- antes da implementacao, a issue executora da separacao precisa existir e
  pertencer ao [`DOT-71`](https://pabloaugusto.atlassian.net/browse/DOT-71)
- [`DOT-210`](https://pabloaugusto.atlassian.net/browse/DOT-210) e a issue dona
  da promocao deste prompt pack, nao da migracao arquitetural em si

## Dependencias e ordem segura

- prerequisite packs: nenhum
- preflight packs:
  - [`startup-alignment`](../startup-alignment/prompt.md)
  - [`agents-rules-centralization`](../agents-rules-centralization/prompt.md)
  - [`documentation-layer-governance`](../documentation-layer-governance/prompt.md)

## Resultado esperado

- o repo passa a ter uma trilha formal para executar a separacao de camadas
- a execucao futura fica protegida contra o erro de centralizar config antes de
  corrigir a fronteira arquitetural
- a relacao entre esta etapa e
  [`DOT-209`](https://pabloaugusto.atlassian.net/browse/DOT-209) fica
  explicitamente documentada
