# Workflows

Catalogo dos workflows ativos do GitHub Actions e das tasks canonicamente acionadas por cada um.

### `ai-governance.yml`

- Objetivo: validar a camada declarativa de IA, licoes, tracker e smoke eval quando arquivos de IA/governanca mudarem.
- Tasks: `ai:validate:linux`, `ai:eval:smoke:linux`, `ci:workflow:sync:check:linux`, `test:unit:python:linux`, `ai:lessons:check:linux`, `ai:worklog:close:gate:linux`

### `bootstrap-integration.yml`

- Objetivo: validar os harnesses reais de integracao do bootstrap em Linux e Windows.
- Tasks: `test:integration:linux`, `test:integration:windows`

### `pr-validate.yml`

- Objetivo: validar naming, commits, camada de IA e suite unitaria no fluxo de PR.
- Tasks: `ai:validate:linux`, `ai:eval:smoke:linux`, `ci:workflow:sync:check:linux`, `ai:worklog:close:gate:linux`, `ci:pr:title:check`, `ci:commits:check`, `ci:branch:check`, `test:unit:python:linux`

### `quality-foundation.yml`

- Objetivo: manter lint de shell, qualidade PowerShell e Pester no baseline do repo.
- Tasks: `ci:lint:linux`, `ci:lint:windows`, `ai:validate:windows`, `test:unit:powershell`
