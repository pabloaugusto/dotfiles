# Workflows

Catalogo dos workflows ativos do GitHub Actions e das tasks canonicamente
acionadas por cada um.

### `ai-governance.yml`

- Objetivo: validar a camada declarativa de IA, tracker, licoes, smoke eval e
  sincronismo documental quando arquivos de governanca mudarem.
- Trigger: `pull_request` e `push` com filtro de paths para arquivos de IA,
  catalogos, validadores, testes e `Taskfile.yml`.
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

- Objetivo: manter lint de shell, qualidade PowerShell e Pester no baseline do
  repositorio.
- Trigger: `pull_request` e `push`
- Plataformas: `ubuntu-latest`, `windows-latest`
- Tasks: `ci:quality:linux`, `ci:quality:windows`

## Regra de manutencao

- Workflows nao devem repetir listas manuais de gates quando ja existir task
  canonica correspondente.
- Toda mudanca em workflow precisa manter paridade com:
  - `Taskfile.yml`
  - `docs/TASKS.md`
  - este arquivo
