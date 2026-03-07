# Catalogo de Tasks

Referencia operacional das tasks mais criticas para governanca, roteamento e CI deste repo.

## Como ler

- Cada secao descreve a finalidade da task e quando ela entra no fluxo.
- O foco aqui sao tasks usadas diretamente em workflows ou gates obrigatorios.

### `ai:chat:intake`

- Funcionalidade: registra intake com preflight de pendencias, worklog e roteamento opcional.
- Uso manual: `task ai:chat:intake MESSAGE="auditar gaps restantes" ROUTE=1 PENDING_ACTION=concluir_primeiro`

### `ai:route`

- Funcionalidade: gera task card e delegation plan declarativos a partir de `intent`, `paths` e `risk`.
- Uso manual: `task ai:route INTENT="refatorar bootstrap" PATHS="bootstrap/bootstrap-windows.ps1,Taskfile.yml"`

### `ai:delegate`

- Funcionalidade: gera plano de delegacao em Markdown com gates obrigatorios e validacoes recomendadas.
- Uso manual: `task ai:delegate INTENT="importar governanca" PATHS="AGENTS.md,.agents/**"`

### `ai:validate:linux`

- Funcionalidade: valida a camada declarativa de IA no Linux/CI.
- Uso manual: `task ai:validate:linux`

### `ai:validate:windows`

- Funcionalidade: valida a camada declarativa de IA no Windows.
- Uso manual: `task ai:validate:windows`

### `ci:ai:check:linux`

- Funcionalidade: executa o gate canonico do workflow `ai-governance.yml` no Linux/CI.
- Uso manual: `task ci:ai:check:linux`

### `ci:lint:linux`

- Funcionalidade: executa lint sintatico de shell e hooks Bash no Linux/CI.
- Uso manual: `task ci:lint:linux`

### `ci:lint:windows`

- Funcionalidade: executa validacao sintatica dos scripts PowerShell no Windows.
- Uso manual: `task ci:lint:windows`

### `ai:worklog:check`

- Funcionalidade: valida pendencias do tracker e bloqueia nova rodada quando a worktree estiver suja sem item ativo em `Doing`.
- Uso manual: `task ai:worklog:check`

### `ai:worklog:close:gate:linux`

- Funcionalidade: falha se ainda houver item em `Doing` no tracker.
- Uso manual: `task ai:worklog:close:gate:linux`

### `ai:lessons:check:linux`

- Funcionalidade: falha se houver worklog concluido sem revisao em `LICOES-APRENDIDAS.md`.
- Uso manual: `task ai:lessons:check:linux`

### `ai:eval:smoke`

- Funcionalidade: executa smoke eval de roteamento e governanca declarativa.
- Uso manual: `task ai:eval:smoke`

### `ai:eval:smoke:linux`

- Funcionalidade: executa o smoke eval no Linux/CI.
- Uso manual: `task ai:eval:smoke:linux`

### `ci:workflow:sync:check`

- Funcionalidade: valida sincronismo entre workflows, Taskfile e catalogos `docs/TASKS.md` e `docs/WORKFLOWS.md`.
- Uso manual: `task ci:workflow:sync:check`

### `ci:workflow:sync:check:linux`

- Funcionalidade: executa o gate de sincronismo no Linux/CI.
- Uso manual: `task ci:workflow:sync:check:linux`

### `ci:quality:linux`

- Funcionalidade: executa a camada canonica do workflow `quality-foundation.yml` no Linux/CI.
- Uso manual: `task ci:quality:linux`

### `ci:quality:windows`

- Funcionalidade: executa a camada canonica do workflow `quality-foundation.yml` no Windows.
- Uso manual: `task ci:quality:windows`

### `ci:bootstrap:integration:linux`

- Funcionalidade: executa a camada canonica do workflow `bootstrap-integration.yml` no Linux/CI.
- Uso manual: `task ci:bootstrap:integration:linux`

### `ci:bootstrap:integration:windows`

- Funcionalidade: executa a camada canonica do workflow `bootstrap-integration.yml` no Windows.
- Uso manual: `task ci:bootstrap:integration:windows`

### `ci:pr:title:check`

- Funcionalidade: valida titulo de PR no padrao `emoji + conventional commits`.
- Uso manual: `task ci:pr:title:check TITLE="✨ feat(repo): endurecer governanca"`

### `ci:commits:check`

- Funcionalidade: valida o range de commits no padrao `emoji + conventional commits`.
- Uso manual: `task ci:commits:check RANGE="origin/main..HEAD"`

### `ci:branch:check`

- Funcionalidade: valida o nome da branch no padrao sem emoji e semanticamente limpo.
- Uso manual: `task ci:branch:check BRANCH="feat/test-harness-hybrid"`

### `test:unit:python:linux`

- Funcionalidade: executa a suite unitaria Python no Linux/CI.
- Uso manual: `task test:unit:python:linux`

### `test:unit:powershell`

- Funcionalidade: executa a suite Pester do repo.
- Uso manual: `task test:unit:powershell`

### `test:integration:linux`

- Funcionalidade: executa o harness Linux de integracao do bootstrap/relink.
- Uso manual: `task test:integration:linux`

### `test:integration:windows`

- Funcionalidade: executa o harness Windows de integracao do bootstrap/relink.
- Uso manual: `task test:integration:windows`
