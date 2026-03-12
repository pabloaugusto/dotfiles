# Runtime App Layer

Esta pasta concentra a camada runtime da app/workstation deste repositorio.

## Fronteira arquitetural

- [`bootstrap/`](bootstrap/) contem o provisionamento e os entrypoints de bootstrap.
- [`df/`](df/) contem os dotfiles e assets materializados na maquina.
- [`../config/`](../config/) permanece reservado para configuracao da camada de
  desenvolvimento, suporte e governanca do repo.
- [`../pyproject.toml`](../pyproject.toml) continua dono da toolchain Python,
  dependencias, lint, testes e configuracao de desenvolvimento nao-runtime.

## Objetivo

Explicitar no filesystem a separacao entre:

- runtime da app/workstation
- camada de desenvolvimento e governanca do repo

Essa fronteira precisa existir antes da etapa posterior de consolidacao da
configuracao de desenvolvimento rastreada em
[`DOT-209`](https://pabloaugusto.atlassian.net/browse/DOT-209).

## Leitura recomendada

- [`bootstrap/README.md`](bootstrap/README.md)
- [`../README.md`](../README.md)
- [`../CONTEXT.md`](../CONTEXT.md)
- [`../docs/bootstrap-flow.md`](../docs/bootstrap-flow.md)
