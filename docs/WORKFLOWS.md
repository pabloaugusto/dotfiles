# Workflows

Catalogo dos workflows ativos do GitHub Actions e das tasks canonicamente
acionadas por cada um.

### `ai-governance.yml`

- Objetivo: validar a camada declarativa de IA, tracker, licoes, smoke eval e
  sincronismo documental quando arquivos de governanca mudarem.
- Trigger: `pull_request` e `push` com filtro de paths para arquivos de IA,
  catalogos, validadores, testes e [`Taskfile.yml`](Taskfile.yml).
- Plataforma: `ubuntu-latest`
- Tasks: `ci:ai:check:linux`, `test:unit:python:linux`

### `bootstrap-integration.yml`

- Objetivo: validar os harnesses reais de integracao do bootstrap `relink` em
  Linux e Windows.
- Trigger: `pull_request`, `push` e `workflow_dispatch`
- Plataformas: `ubuntu-latest`, `windows-latest`
- Tasks: `ci:bootstrap:integration:linux`, `ci:bootstrap:integration:windows`

### `pr-validate.yml`

- Objetivo: validar naming, commits, branch, camada de IA e suite unitaria no
  fluxo principal de PR.
- Trigger: `pull_request`, `push` em `main` e `workflow_dispatch`
- Plataforma: `ubuntu-latest`
- Tasks: `ci:ai:check:linux`, `ci:pr:title:check`, `ci:commits:check`, `ci:branch:check`, `test:unit:python:linux`

### `quality-foundation.yml`

- Objetivo: manter o baseline canonico de qualidade do repo, cobrindo shell,
  PowerShell, toolchain Python via `uv`, `ruff`, `ty`, `pytest`, lint
  documental, YAML, workflows e scanner de segredos.
- Trigger: `pull_request` e `push`
- Plataformas: `ubuntu-latest`, `windows-latest`
- Tasks: `ci:quality:linux`, `ci:quality:windows`

## Observacao operacional

- `spell:check` existe como task local com `cspell`, mas ainda nao entra no
  workflow canonico enquanto o dicionario tecnico PT-BR/EN nao estiver curado
  o suficiente para evitar ruido estrutural.

## Regra de manutencao

- Workflows nao devem repetir listas manuais de gates quando ja existir task
  canonica correspondente.
- Toda mudanca em workflow precisa manter paridade com:
  - [`Taskfile.yml`](Taskfile.yml)
  - [`docs/TASKS.md`](docs/TASKS.md)
  - este arquivo
