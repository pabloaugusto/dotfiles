# Catalogo de Tasks

Referencia operacional das tasks canonicas mais importantes do repositorio.

## Como usar este catalogo

- Este documento nao tenta listar cada alias do `Taskfile.yml`.
- O foco aqui sao as entradas que estruturam bootstrap, operacao diaria,
  qualidade, testes, PR e governanca de IA.
- Toda task usada por workflow ativo precisa aparecer aqui.

## Operacao diaria

### `sync`

- Funcionalidade: fluxo inteligente de sincronizacao do repo no ambiente atual.
- Uso manual: `task sync`

### `repo:update`

- Funcionalidade: atualiza o repo atual com `fetch --prune` e `pull --rebase`.
- Uso manual: `task repo:update`

### `repo:update-safe`

- Funcionalidade: atualiza o repo com auto-stash quando a worktree estiver suja.
- Uso manual: `task repo:update-safe`

### `repo:publish`

- Funcionalidade: publica alteracoes com commit e push no fluxo canonico do repo.
- Uso manual: `task repo:publish MSG="♻️ refactor(repo): exemplo"`

### `sync:wsl-gate`

- Funcionalidade: sincroniza e valida o clone local do WSL a partir do Windows
  via Git-only.
- Uso manual: `task sync:wsl-gate`

### `env:check`

- Funcionalidade: executa `checkEnv` no ambiente atual.
- Uso manual: `task env:check`

## Bootstrap e links canonicos

### `bootstrap`

- Funcionalidade: executa o bootstrap oficial do ambiente atual.
- Uso manual: `task bootstrap`

### `bootstrap:windows:new`

- Funcionalidade: bootstrap completo no Windows host.
- Uso manual: `task bootstrap:windows:new`

### `bootstrap:windows:refresh`

- Funcionalidade: refresh rapido do bootstrap no Windows.
- Uso manual: `task bootstrap:windows:refresh`

### `bootstrap:relink`

- Funcionalidade: recria os links canonicos do bootstrap no ambiente atual.
- Uso manual: `task bootstrap:relink`

### `bootstrap:windows:relink`

- Funcionalidade: recria symlinks e junctions canonicos do bootstrap no Windows.
- Uso manual: `task bootstrap:windows:relink`

### `bootstrap:linux:relink`

- Funcionalidade: recria symlinks canonicos do bootstrap no Linux/WSL.
- Uso manual: `task bootstrap:linux:relink`

## Governanca e automacao de IA

### `ai:chat:intake`

- Funcionalidade: registra intake com preflight de pendencias, worklog e
  roteamento opcional.
- Uso manual: `task ai:chat:intake MESSAGE="auditar gaps restantes" ROUTE=1 PENDING_ACTION=concluir_primeiro`

### `ai:route`

- Funcionalidade: gera task card e delegation plan declarativos a partir de
  `intent`, `paths` e `risk`.
- Uso manual: `task ai:route INTENT="refatorar bootstrap" PATHS="bootstrap/bootstrap-windows.ps1,Taskfile.yml"`

### `ai:delegate`

- Funcionalidade: gera plano de delegacao em Markdown com gates obrigatorios e
  validacoes recomendadas.
- Uso manual: `task ai:delegate INTENT="importar governanca" PATHS="AGENTS.md,.agents/**"`

### `ai:validate:linux`

- Funcionalidade: valida a camada declarativa de IA no Linux e no CI.
- Uso manual: `task ai:validate:linux`

### `ai:validate:windows`

- Funcionalidade: valida a camada declarativa de IA no Windows.
- Uso manual: `task ai:validate:windows`

### `ai:eval:smoke`

- Funcionalidade: executa smoke eval de roteamento e governanca declarativa.
- Uso manual: `task ai:eval:smoke`

### `ai:worklog:check`

- Funcionalidade: valida pendencias do tracker e bloqueia nova rodada quando a
  worktree estiver suja sem item ativo em `Doing`.
- Uso manual: `task ai:worklog:check`

### `ai:worklog:close:gate:linux`

- Funcionalidade: falha se ainda houver item em `Doing` no tracker.
- Uso manual: `task ai:worklog:close:gate:linux`

### `ai:lessons:check:linux`

- Funcionalidade: falha se houver worklog concluido sem revisao em
  `LICOES-APRENDIDAS.md`.
- Uso manual: `task ai:lessons:check:linux`

### `ci:ai:check:linux`

- Funcionalidade: executa o gate canonico do workflow `ai-governance.yml`.
- Uso manual: `task ci:ai:check:linux`

## Qualidade, validacao e PR

### `ci:lint:linux`

- Funcionalidade: executa lint sintatico de shell e hooks Bash no Linux e CI.
- Uso manual: `task ci:lint:linux`

### `ci:lint:windows`

- Funcionalidade: executa validacao sintatica dos scripts PowerShell no Windows.
- Uso manual: `task ci:lint:windows`

### `ci:workflow:sync:check`

- Funcionalidade: valida sincronismo entre workflows, Taskfile e catalogos
  `docs/TASKS.md` e `docs/WORKFLOWS.md`.
- Uso manual: `task ci:workflow:sync:check`

### `ci:quality:linux`

- Funcionalidade: executa a camada canonica do workflow
  `quality-foundation.yml` no Linux e CI.
- Uso manual: `task ci:quality:linux`

### `ci:quality:windows`

- Funcionalidade: executa a camada canonica do workflow
  `quality-foundation.yml` no Windows.
- Uso manual: `task ci:quality:windows`

### `ci:bootstrap:integration:linux`

- Funcionalidade: executa a camada canonica do workflow
  `bootstrap-integration.yml` no Linux e CI.
- Uso manual: `task ci:bootstrap:integration:linux`

### `ci:bootstrap:integration:windows`

- Funcionalidade: executa a camada canonica do workflow
  `bootstrap-integration.yml` no Windows.
- Uso manual: `task ci:bootstrap:integration:windows`

### `ci:pr:title:check`

- Funcionalidade: valida titulo de PR no padrao `emoji + conventional commits`.
- Uso manual: `task ci:pr:title:check PR_TITLE="✨ feat(repo): endurecer governanca"`

### `ci:commits:check`

- Funcionalidade: valida um range de commits no padrao
  `emoji + conventional commits`.
- Uso manual: `task ci:commits:check RANGE="origin/main..HEAD"`

### `ci:branch:check`

- Funcionalidade: valida o nome da branch no padrao sem emoji e semanticamente
  limpo.
- Uso manual: `task ci:branch:check BRANCH="feat/test-harness-hybrid"`

### `ci:validate`

- Funcionalidade: executa o baseline local de validacao de PR no ambiente atual.
- Uso manual: `task ci:validate`

### `pr:validate`

- Funcionalidade: executa o pipeline local recomendado antes de abrir ou
  atualizar um PR.
- Uso manual: `task pr:validate`

## Testes

### `test:unit:python:linux`

- Funcionalidade: executa a suite unitaria Python no Linux e CI.
- Uso manual: `task test:unit:python:linux`

### `test:unit:powershell`

- Funcionalidade: executa a suite Pester do repositorio.
- Uso manual: `task test:unit:powershell`

### `test:integration:linux`

- Funcionalidade: executa o harness Linux de integracao do bootstrap `relink`.
- Uso manual: `task test:integration:linux`

### `test:integration:windows`

- Funcionalidade: executa o harness Windows de integracao do bootstrap
  `relink`.
- Uso manual: `task test:integration:windows`
