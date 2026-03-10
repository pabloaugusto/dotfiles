# Catalogo de Tasks

Referencia operacional das tasks canonicas mais importantes do repositorio.

## Como usar este catalogo

- Este documento nao tenta listar cada alias do [`Taskfile.yml`](Taskfile.yml).
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
- Observacao: aceite `SIGN_MODE=human|automation|auto` para validar
  explicitamente o signer esperado da worktree.

### `git:signing:status`

- Funcionalidade: exibe o modo de assinatura efetivo da worktree e a origem do
  signer atual.
- Uso manual: `task git:signing:status`

### `git:signing:mode:automation`

- Funcionalidade: aplica signer tecnico de automacao na worktree atual usando
  chave publica resolvida via `op`, mantendo a chave privada no 1Password SSH
  Agent.
- Uso manual: `task git:signing:mode:automation`

### `git:signing:mode:human`

- Funcionalidade: remove overrides da worktree e volta ao signer humano padrao.
- Uso manual: `task git:signing:mode:human`

### `git:signing:github:ensure`

- Funcionalidade: garante que a signing key tecnica esteja cadastrada no GitHub
  via `gh`.
- Uso manual: `task git:signing:github:ensure`

### `secrets:rotation:preflight`

- Funcionalidade: executa preflight nao-destrutivo da trilha canonica de
  rotacao de secrets.
- Uso manual: `task secrets:rotation:preflight`

### `secrets:rotation:plan`

- Funcionalidade: gera plano ordenado e auditavel da trilha canonica de
  rotacao de secrets.
- Uso manual: `task secrets:rotation:plan`

### `secrets:rotation:validate`

- Funcionalidade: executa validacao nao-destrutiva dos alvos declarados de
  rotacao de secrets.
- Uso manual: `task secrets:rotation:validate`

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
- Observacao: `PENDING_ACTION=concluir_primeiro` cobre concluir o WIP atual ou
  puxar apenas o **work item** que o destrava diretamente.
- Uso manual: `task ai:chat:intake MESSAGE="auditar gaps restantes" ROUTE=1 PENDING_ACTION=concluir_primeiro`

### `ai:route`

- Funcionalidade: gera task card e delegation plan declarativos a partir de
  `intent`, `paths` e `risk`.
- Uso manual: `task ai:route INTENT="refatorar bootstrap" PATHS="bootstrap/bootstrap-windows.ps1,Taskfile.yml"`

### `ai:delegate`

- Funcionalidade: gera plano de delegacao em Markdown com gates obrigatorios e
  validacoes recomendadas.
- Uso manual: `task ai:delegate INTENT="importar governanca" PATHS="AGENTS.md,.agents/**"`

### `ai:review:record`

- Funcionalidade: registra parecer especializado `aprovado` ou `reprovado`
  para um `worklog` na trilha viva de
  [`docs/AI-REVIEW-LEDGER.md`](AI-REVIEW-LEDGER.md).
- Uso manual: `task ai:review:record WORKLOG_ID="WIP-..." REVIEWER="python-reviewer" STATUS="aprovado" SUMMARY="Sem regressao funcional" PATHS="scripts/validate-ai-assets.py"`

### `ai:review:check`

- Funcionalidade: valida se todos os revisores especializados obrigatorios para
  o escopo aprovaram o `worklog`.
- Uso manual: `task ai:review:check WORKLOG_ID="WIP-..." PATHS="scripts/validate-ai-assets.py"`

### `ai:validate:linux`

- Funcionalidade: valida a camada declarativa de IA no Linux e no CI.
- Uso manual: `task ai:validate:linux`

### `ai:validate:windows`

- Funcionalidade: valida a camada declarativa de IA no Windows.
- Uso manual: `task ai:validate:windows`

### `ai:eval:smoke`

- Funcionalidade: executa smoke eval de roteamento e governanca declarativa.
- Uso manual: `task ai:eval:smoke`

### `ai:control-plane:show`

- Funcionalidade: exibe o resumo da control plane dev-time em [`config/ai/`](../config/ai/).
- Uso manual: `task ai:control-plane:show`

### `ai:startup:session`

- Funcionalidade: gera o relatorio operacional de **startup** e **restart** da
  sessao de IA, resolvendo os arquivos canonicos do manifest e listando os
  contratos nascidos no chat que ainda aguardam promocao definitiva.
- Uso manual: `task ai:startup:session`
- Uso com caminho customizado: `task ai:startup:session OUT=".cache/ai/startup-session.md"`
- Observacao: a task escreve por padrao o artefato local em
  `.cache/ai/startup-session.md`, usando como fontes
  [`docs/AI-STARTUP-GOVERNANCE-MANIFEST.md`](AI-STARTUP-GOVERNANCE-MANIFEST.md)
  e [`docs/AI-CHAT-CONTRACTS-REGISTER.md`](AI-CHAT-CONTRACTS-REGISTER.md).

### `ai:1password:ratelimit`

- Funcionalidade: exibe o consumo atual e o restante do rate limit da service
  account usada pelo `1Password CLI`.
- Uso manual: `task ai:1password:ratelimit`
- Uso com refresh explicito: `task ai:1password:ratelimit REFRESH=1`
- Observacao: a task falha com `exit 1` quando `account.read_write` estiver
  esgotado, para permitir preflight automatizado antes de rodadas remotas.

### `ai:atlassian:check`

- Funcionalidade: resolve refs da control plane Atlassian e valida conectividade
  com `Jira` e `Confluence` via API oficial.
- Uso manual: `task ai:atlassian:check`
- Uso com override pontual: `task ai:atlassian:check SITE_URL="https://sua-org.atlassian.net"`
- Observacao: a task usa a control plane base em [`config/ai/platforms.yaml`](../config/ai/platforms.yaml)
  e respeita o overlay local derivado de
  [`config/ai/platforms.local.yaml.tpl`](../config/ai/platforms.local.yaml.tpl)
  quando presente; `SITE_URL` segue disponivel para override pontual.

### `ai:atlassian:openapi:show`

- Funcionalidade: exibe o catalogo dos specs OpenAPI oficiais da Atlassian
  usados como base para codegen e auditoria.
- Uso manual: `task ai:atlassian:openapi:show`

### `ai:atlassian:openapi:vendor`

- Funcionalidade: baixa e vendoriza os specs oficiais da Atlassian em
  [`vendor/atlassian/`](../vendor/atlassian/README.md).
- Uso manual: `task ai:atlassian:openapi:vendor`
- Observacao: o fluxo-base do repo nao deve gerar clients direto da URL; o
  codegen deve usar os arquivos vendorizados.

### `ai:jira:model:show`

- Funcionalidade: exibe o modelo declarativo alvo do projeto `Jira` mantido em
  [`config/ai/jira-model.yaml`](../config/ai/jira-model.yaml).
- Uso manual: `task ai:jira:model:show`

### `ai:jira:model:delta`

- Funcionalidade: compara o tenant `Jira` atual com o modelo alvo e devolve o
  delta de statuses, fields, components e acesso de board.
- Uso manual: `task ai:jira:model:delta`
- Observacao: o resultado operacional consolidado tambem fica documentado em
  [`docs/atlassian-ia/2026-03-07-jira-configuration-export.md`](atlassian-ia/2026-03-07-jira-configuration-export.md).

### `ai:atlassian:backfill:plan`

- Funcionalidade: gera o plano declarativo de backfill retroativo a partir de
  [`ROADMAP.md`](../ROADMAP.md), [`docs/ROADMAP-DECISIONS.md`](ROADMAP-DECISIONS.md),
  [`docs/AI-WIP-TRACKER.md`](AI-WIP-TRACKER.md) e da trilha
  [`docs/atlassian-ia/`](atlassian-ia/README.md).
- Uso manual: `task ai:atlassian:backfill:plan`
- Observacao: a task so monta os payloads e as contagens; a aplicacao no tenant
  continua dependente de auth/permissoes e da customizacao estrutural do
  projeto `Jira`.

### `ai:atlassian:migration:bundle`

- Funcionalidade: gera um bundle auditavel com manifest, schemas, endpoint
  catalog, plano de backfill e copia dos artefatos fonte usados na migracao
  para `Jira` e `Confluence`.
- Uso manual: `task ai:atlassian:migration:bundle`
- Observacao: o `.zip` gerado deve ser anexado na issue correspondente do
  `Jira` assim que ela existir e linkado da pagina correspondente no
  `Confluence`.

### `ai:atlassian:seed:plan`

- Funcionalidade: gera o plano declarativo da semeadura retroativa em `Jira` e
  `Confluence`, incluindo precondicoes, contagem de issues e arvore de paginas
  do modelo oficial.
- Uso manual: `task ai:atlassian:seed:plan`
- Observacao: o plano atual explicita o bloqueio do board enquanto o layout do
  `DOT board` ainda estiver desalinhado com o workflow alvo, a menos que haja
  override explicito aprovado pelo usuario para uma rodada especifica.

### `ai:atlassian:seed:apply`

- Funcionalidade: executa a semeadura retroativa, cria/atualiza a issue de
  migracao, anexa o bundle auditavel e sincroniza paginas e comentarios
  estruturados.
- Uso manual: `task ai:atlassian:seed:apply`
- Observacao: esta task so deve ser rodada apos o board refletir o workflow
  oficial e o delta estrutural do projeto estar saneado.
- Override excepcional desta rodada: `uv run --locked python scripts/ai-atlassian-seed.py apply --allow-visual-board-gap`

### `ai:atlassian:docs:sync`

- Funcionalidade: resincroniza a documentacao oficial do control plane no
  `Confluence` sem depender da semeadura completa de `Jira`.
- Uso manual: `task ai:atlassian:docs:sync ISSUE_KEYS="DOT-1,DOT-65,DOT-66"`
- Observacao: esta task existe para manter o `Confluence` vivo mesmo quando o
  board do `Jira Software` ainda estiver em drift ou bloqueado.

### `ai:worklog:check`

- Funcionalidade: valida pendencias do tracker e bloqueia nova rodada quando a
  worktree estiver suja sem item ativo em `Doing`.
- Observacao: quando existir WIP ativo, `concluir_primeiro` significa concluir
  ou destravar primeiro, e nao puxar demanda nova sem relacao com esse WIP.
- Uso manual: `task ai:worklog:check`

### `ai:worklog:done`

- Funcionalidade: move a tarefa de `Doing` para `Done`, mas bloqueia o
  fechamento quando o escopo exigir revisor especializado ainda sem parecer
  `aprovado`.
- Uso manual: `task ai:worklog:done WORKLOG_ID="WIP-..." DELIVERY="..." LESSONS_DECISION="sem_nova_licao" LESSONS_SUMMARY="..." REVIEW_PATHS="scripts/validate-ai-assets.py"`

### `ai:worklog:close:gate:linux`

- Funcionalidade: falha se ainda houver item em `Doing` no tracker.
- Uso manual: `task ai:worklog:close:gate:linux`

### `ai:lessons:check:linux`

- Funcionalidade: falha se houver worklog concluido sem revisao em
  [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md).
- Uso manual: `task ai:lessons:check:linux`

### `ci:ai:check:linux`

- Funcionalidade: executa o gate canonico do workflow `ai-governance.yml`.
- Uso manual: `task ci:ai:check:linux`

## Qualidade, validacao e PR

### `install:dev`

- Funcionalidade: sincroniza a toolchain Python de desenvolvimento via `uv`.
- Uso manual: `task install:dev`

### `lint:python:windows`

- Funcionalidade: executa `ruff check` em [`scripts/`](scripts/), [`tests/python`](tests/python) e hooks
  Python no Windows.
- Uso manual: `task lint:python:windows`

### `format:python:check:windows`

- Funcionalidade: verifica a formatacao canonica Python com `ruff format
  --check` no Windows.
- Uso manual: `task format:python:check:windows`

### `type:check:windows`

- Funcionalidade: executa `ty` incremental na camada Python importada de
  qualidade no Windows.
- Uso manual: `task type:check:windows`

### `test:python:windows`

- Funcionalidade: executa `pytest` com coverage na suite Python canonica do
  repositorio no Windows.
- Uso manual: `task test:python:windows`

### `docs:lint:windows`

- Funcionalidade: aplica `pymarkdownlnt` nos documentos canonicos do repo no
  Windows.
- Uso manual: `task docs:lint:windows`

### `docs:check:windows`

- Funcionalidade: valida links locais e referencias documentais com
  `validate_docs.py` no Windows.
- Uso manual: `task docs:check:windows`

### `spell:check:windows`

- Funcionalidade: executa `cspell` com dicionario tecnico versionado no
  Windows.
- Uso manual: `task spell:check:windows`
- Observacao: a task existe, mas ainda nao faz parte do gate canonico
  `ci:quality` enquanto o dicionario PT-BR/EN e curado.

### `spell:dictionary:audit:windows`

- Funcionalidade: audita o dicionario local do `cspell` e detecta palavras
  redundantes ja cobertas pelos dicionarios importados.
- Uso manual: `task spell:dictionary:audit:windows`
- Observacao: com `FIX=1`, remove redundancias seguras de
  [`.cspell/project-words.txt`](../.cspell/project-words.txt).

### `spell:curate:windows`

- Funcionalidade: faz curadoria assistida das palavras desconhecidas para um
  escopo especifico.
- Uso manual: `task spell:curate:windows TARGETS="docs scripts" APPLY=1`

### `spell:review:windows`

- Funcionalidade: executa o review consultivo do Pascoalete por arquivo,
  atualiza [`docs/AI-ORTHOGRAPHY-LEDGER.md`](AI-ORTHOGRAPHY-LEDGER.md) e abre
  pendencia no backlog se restar falha textual nao corrigida.
- Uso manual: `task spell:review:windows WORKLOG_ID="WIP-..." PATHS="README.md,AGENTS.md"`
- Observacao: a task falha quando ainda ha achados, mas isso nao bloqueia PR,
  commit ou `done`; a falha serve para evidenciar o apontamento consultivo.

### `lint:yaml:windows`

- Funcionalidade: aplica `yamllint` nos YAMLs do repo no Windows.
- Uso manual: `task lint:yaml:windows`

### `validate:actions:windows`

- Funcionalidade: valida workflows do GitHub Actions com `actionlint` pinado no
  Windows.
- Uso manual: `task validate:actions:windows`

### `security:secrets:windows`

- Funcionalidade: escaneia o repo em busca de segredos versionados com
  `gitleaks` pinado no Windows.
- Uso manual: `task security:secrets:windows`

### `ci:lint:linux`

- Funcionalidade: executa lint sintatico de shell e hooks Bash no Linux e CI.
- Uso manual: `task ci:lint:linux`

### `ci:lint:windows`

- Funcionalidade: executa validacao sintatica dos scripts PowerShell no Windows.
- Uso manual: `task ci:lint:windows`

### `ci:workflow:sync:check`

- Funcionalidade: valida sincronismo entre workflows, Taskfile e catalogos
  [`docs/TASKS.md`](docs/TASKS.md) e [`docs/WORKFLOWS.md`](docs/WORKFLOWS.md).
- Uso manual: `task ci:workflow:sync:check`

### `ci:quality:linux`

- Funcionalidade: executa a camada canonica do workflow
  `quality-foundation.yml` no Linux e CI, incluindo `uv`, `ruff`, `ty`,
  `pytest`, lint documental, YAML, workflows e scanner de segredos.
- Uso manual: `task ci:quality:linux`

### `ci:quality:windows`

- Funcionalidade: executa a camada canonica do workflow
  `quality-foundation.yml` no Windows, incluindo `uv`, `ruff`, `ty`, `pytest`,
  lint documental, YAML, workflows, scanner de segredos, validacao de IA e
  Pester.
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

### `test:python:linux`

- Funcionalidade: executa `pytest` com coverage na suite Python canonica do
  repositorio no Linux e CI.
- Uso manual: `task test:python:linux`

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
